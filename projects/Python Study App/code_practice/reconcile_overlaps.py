"""Offline, evidence-backed overlaps against newly imported problem contracts.

Run python -m code_practice.reconcile_overlaps after target import validation.
This never opens progress, changes existing problem IDs, or approves candidates.
"""
from collections import Counter
import hashlib
import json
from math import ceil, log2
from pathlib import Path
import random

from .catalog_artifacts import write_json_atomic
from .catalog_evidence import content_digest, judge_contract_hash, load_verified_import

ROOT = Path(__file__).resolve().parent.parent
DECISIONS = {
    153: {
        "target_source_id": 154,
        "source_hash": "303783978ed5c7971d71a670f071a9b27942bd786348537483f278c58073874a",
        "reason": "Same rotated-array minimum value and input signature. The approved duplicate-aware contract also accepts every unique rotated array; its reference uses logarithmic element reads when values are unique. No duplicate exercise or progress ID is created.",
    },
}


def implementation_hash():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


class CountedSequence(list):
    """Instrument indexing and iteration; reject slices and excess element reads."""
    def __init__(self, values):
        super().__init__(values)
        self.reads = 0
        self.limit = 4 * ceil(log2(len(values))) + 1

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise AssertionError("Unique rotated minimum must not copy a linear slice")
        self.reads += 1
        if self.reads > self.limit:
            raise AssertionError("Exceeded the logarithmic element-read bound")
        return super().__getitem__(index)

    def __iter__(self):
        for index in range(len(self)):
            yield self[index]


def check_unique_rotations(payload, source):
    from .build_import_batch import workbook_sample
    namespace = {}
    exec(compile(payload["reference_solution"], "<reviewed-rotated-minimum>", "exec"), namespace)
    function = namespace[payload["signature"]["name"]]
    sample = workbook_sample(source["sample"], payload["signature"]["parameters"])
    if sample is None:
        raise ValueError("The reviewed overlap needs its original workbook sample")
    rng = random.Random(4047 + 153)
    inputs = []
    for _ in range(500):
        ordered = sorted(rng.sample(range(-5000, 5001), rng.randint(1, 5000)))
        pivot = rng.randrange(len(ordered))
        inputs.append((ordered[pivot:] + ordered[:pivot], ordered[0]))
    inputs.insert(0, (sample[0][0], sample[1]))
    ordered = list(range(-2500, 2500))
    inputs.extend([(ordered, -2500), (ordered[-1:] + ordered[:-1], -2500)])
    largest_reads = 0
    for values, expected in inputs:
        if not (1 <= len(values) <= 5000 and len(set(values)) == len(values)
                and all(type(value) is int and -5000 <= value <= 5000 for value in values)
                and sum(values[i] > values[(i + 1) % len(values)] for i in range(len(values))) <= 1):
            raise ValueError("Invalid unique-rotation verification input")
        observed = CountedSequence(values)
        if function(observed) != expected:
            raise ValueError("Overlap reference disagrees with the minimum oracle")
        largest_reads = max(largest_reads, observed.reads)
    return {"oracle_inputs": 500, "oracle_seed": 4200, "workbook_sample_checked": True, "deterministic_inputs": 3,
            "largest_input": max(len(values) for values, _ in inputs), "largest_element_reads": largest_reads,
            "read_bound": "4*ceil(log2(n))+1 indexed/iterated element reads; no slices",
            "complexity_scope": "Read bound is executable evidence; inspected reference halves the interval on every unique-value iteration."}


def validate_import_overlap(record, records, root=ROOT):
    """Fail closed when either source, target, judge, decision, or proof changes."""
    try:
        decision = DECISIONS[record["source_id"]]
        target = records[decision["target_source_id"]]
        payload = load_verified_import(target, root)
        report = json.loads((root / record["overlap_report"]).read_text())
        if (record["status"] != "overlap" or record["source_hash"] != decision["source_hash"]
                or record["existing_id"] != target["problem_id"] or not report["valid"]
                or report["source_id"] != record["source_id"] or report["source_hash"] != record["source_hash"]
                or report["target_problem_id"] != target["problem_id"]
                or report["target_source_hash"] != target["source_hash"]
                or report["target_content_sha256"] != content_digest(payload)
                or report["judge_contract_sha256"] != judge_contract_hash()
                or report["implementation_sha256"] != implementation_hash()
                or report["decision"] != decision or report["oracle_inputs"] < 500
                or not report["workbook_sample_checked"]):
            raise ValueError("Overlap evidence does not match")
        return report
    except (OSError, KeyError, ValueError, TypeError) as error:
        raise ValueError(f"{record.get('source_id')}: missing, stale, or failing overlap evidence") from error


def restore_import_overlaps(records, previous, root=ROOT):
    """Preserve proved mappings on unchanged re-extraction, never stale ones."""
    by_id = {record["source_id"]: record for record in records}
    for record in records:
        old = previous.get(record["source_id"], {})
        if old.get("status") != "overlap" or not old.get("overlap_report"):
            continue
        if old.get("source_hash") != record["source_hash"]:
            continue
        try:
            validate_import_overlap(old, by_id, root)
        except ValueError:
            record.update(status="pending", existing_id=None, reason="Imported overlap target or evidence changed; reconcile again.")
        else:
            record.update(old)


def reconcile(root=ROOT):
    ledger_path = root / "catalog_import/ledger.json"
    ledger = json.loads(ledger_path.read_text())
    records = {record["source_id"]: record for record in ledger["records"]}
    sources = {source["source_id"]: source for line in (root / "catalog_import/sources.jsonl").read_text().splitlines()
               if (source := json.loads(line))}
    for source_id, decision in DECISIONS.items():
        record = records[source_id]
        if record["status"] in {"imported", "excluded"}:
            raise ValueError("Cannot replace an existing import/progress ID or approved exclusion with an overlap")
        report_path = Path("catalog_import/overlap_reports") / f"leetcode-{source_id}.json"
        try:
            if record["source_hash"] != decision["source_hash"] or content_digest(sources[source_id]) != record["source_hash"]:
                raise ValueError("Source changed since the behavioral review")
            target = records[decision["target_source_id"]]
            payload = load_verified_import(target, root)
            evidence = check_unique_rotations(payload, sources[source_id])
            report = {"valid": True, "source_id": source_id, "source_hash": record["source_hash"],
                      "target_problem_id": target["problem_id"], "target_source_hash": target["source_hash"],
                      "target_content_sha256": content_digest(payload), "judge_contract_sha256": judge_contract_hash(),
                      "implementation_sha256": implementation_hash(), "decision": decision, **evidence}
        except (ValueError, AssertionError, KeyError) as error:
            report = {"valid": False, "source_id": source_id, "failures": [str(error)]}
            record.update(status="quarantined", existing_id=None, reason="Overlap validation failed; not counted as completed.")
        else:
            record.update(status="overlap", existing_id=target["problem_id"], reason=decision["reason"])
        write_json_atomic(root / report_path, report)
        record["overlap_report"] = str(report_path)
    ledger["counts"] = dict(Counter(record["status"] for record in ledger["records"]))
    write_json_atomic(ledger_path, ledger)
    return ledger["counts"]


if __name__ == "__main__":
    print(json.dumps(reconcile()))
