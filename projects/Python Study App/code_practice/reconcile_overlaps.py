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
    2220: {
        "target_source_id": 461,
        "source_hash": "29c828993d44681ce0a71f2c38517254af50bbc61c083e7c7ac4d799f9c224f7",
        "reason": "Every differing bit must be flipped at least once, and flipping each differing bit once suffices. Thus minimum flips is exactly Hamming distance for the same two integers. The target's nonnegative 31-bit domain includes every source start/goal in 0..10^9. Independent per-position comparisons verify 500 full-domain inputs, the workbook sample, and bit-boundary/carry cases. Keep one existing Hamming Distance progress ID.",
    },
    46: {
        "target_source_id": 47,
        "source_hash": "c63f4d5d058004744b30b60d058486cf74a7db6a9f753906b344cfb4dc1a8b7f",
        "reason": "Both return every distinct ordered permutation of an integer list in any outer order. The duplicate-aware numeric contract covers every unique input from source 46 (length 1–6, values -10..10) and also repeated values up to length 8. The count-based reference produces n! rows on unique inputs; independent position permutations verify 500 inputs, the workbook sample, and the six-element boundary. Keep one numeric-permutation progress ID, distinct from the original text-returning string exercise.",
    },
    153: {
        "target_source_id": 154,
        "source_hash": "303783978ed5c7971d71a670f071a9b27942bd786348537483f278c58073874a",
        "reason": "Same rotated-array minimum value and input signature. The approved duplicate-aware contract also accepts every unique rotated array; its reference uses logarithmic element reads when values are unique. No duplicate exercise or progress ID is created.",
    },
    1081: {
        "target_source_id": 316,
        "source_hash": "21833734d4fc27642ee4a1466650a165e1dfcb72dcf09167572f4298a6901938",
        "reason": "Both contracts return the lexicographically smallest subsequence containing every distinct lowercase letter exactly once. The approved Remove Duplicate Letters entry accepts the entire 1–1000-character source domain (and up to 10000 characters). Source descriptions explicitly identify the equivalence; exhaustive-subsequence oracle comparisons verify behavior. One existing progress ID is retained.",
    },
    319: {
        "target_source_id": 69,
        "source_hash": "96e38bc1896eb94f07fc21941e35874391887f54bc744c3b81d10566bf794b9e",
        "reason": "Bulb i is toggled once per positive divisor, so it remains on exactly when i is a perfect square (only squares have an unpaired divisor). Thus the number lit among 1..n is floor(sqrt(n)), exactly the existing integer-square-root result. The target's 0..2^31-1 input domain covers all source n in 0..10^9, and its binary-search implementation satisfies the source's performance needs. Keep the existing progress ID.",
    },
}


def implementation_hash():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def check_bit_flips(payload, source):
    from .build_import_batch import workbook_sample
    namespace = {}
    exec(compile(payload['reference_solution'], '<reviewed-bit-flips>', 'exec'), namespace)
    function = namespace[payload['signature']['name']]
    sample = workbook_sample(source['sample'], [{'name':'start'},{'name':'goal'}])
    if sample is None or function(*sample[0]) != sample[1]:
        raise ValueError('Bit-flip workbook sample disagrees')
    rng = random.Random(4047+2220)
    cases = [[rng.randint(0,10**9),rng.randint(0,10**9)] for _ in range(500)]
    boundaries = [[0,0],[0,10**9],[10**9,0],[10**9,10**9]]
    boundaries += [[0,1<<bit] for bit in range(30)]
    boundaries += [[(1<<bit)-1,1<<bit] for bit in range(1,30)]
    for start,goal in cases+boundaries:
        if not all(type(value) is int and 0<=value<=10**9 for value in (start,goal)):
            raise ValueError('Invalid bit-flip source input')
        expected = sum((start//(2**bit))%2 != (goal//(2**bit))%2 for bit in range(30))
        actual = function(start,goal)
        if type(actual) is not int or actual != expected:
            raise ValueError('Overlap reference disagrees with per-position bit-flip oracle')
    return {'oracle_inputs':500,'oracle_seed':6267,'workbook_sample_checked':True,
            'deterministic_inputs':len(boundaries)+1,'largest_input':10**9,
            'domain':'Two integers in 0..10^9; each differing binary position needs exactly one flip'}


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


def check_unique_permutations(payload, source):
    from itertools import permutations
    from .build_import_batch import workbook_sample
    namespace = {}
    exec(compile(payload['reference_solution'], '<reviewed-unique-permutations>', 'exec'), namespace)
    function = namespace[payload['signature']['name']]
    sample = workbook_sample(source['sample'], payload['signature']['parameters'])
    if sample is None or sorted(function(*sample[0])) != sorted(sample[1]):
        raise ValueError('Permutation workbook sample disagrees')
    rng = random.Random(4047+46)
    cases = [rng.sample(range(-10,11),rng.randint(1,6)) for _ in range(500)]
    boundaries = [[-10],[10],[-10,0,10],[5,4,3,2,1,0],[-10,-9,-1,0,9,10]]
    for values in cases+boundaries:
        if not (1 <= len(values) <= 6 and len(set(values)) == len(values)
                and all(type(value) is int and -10 <= value <= 10 for value in values)):
            raise ValueError('Invalid unique-permutation source input')
        expected = sorted([list(row) for row in permutations(values)])
        actual = function(values)
        if not isinstance(actual,list) or sorted(actual) != expected:
            raise ValueError('Overlap reference disagrees with ordered permutation oracle')
    return {'oracle_inputs':500,'oracle_seed':4093,'workbook_sample_checked':True,
            'deterministic_inputs':len(boundaries)+1,'largest_input':6,'largest_output':720,
            'domain':'1–6 distinct signed integers in -10..10; preserve order inside rows and reject duplicate/missing rows'}


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


def check_distinct_subsequence(payload, source):
    from itertools import combinations
    from .build_import_batch import workbook_sample
    namespace = {}
    exec(compile(payload["reference_solution"], "<reviewed-distinct-subsequence>", "exec"), namespace)
    function = namespace[payload["signature"]["name"]]
    sample = workbook_sample(source["sample"], payload["signature"]["parameters"])
    if sample is None or function(*sample[0]) != sample[1]:
        raise ValueError("Distinct-subsequence workbook sample disagrees")
    rng = random.Random(4047 + 1081)
    for _ in range(500):
        text = "".join(rng.choice("abcde") for _ in range(rng.randint(1, 11)))
        alphabet = set(text)
        expected = min(candidate for indices in combinations(range(len(text)), len(alphabet))
                       if set(candidate := "".join(text[i] for i in indices)) == alphabet)
        if function(text) != expected:
            raise ValueError("Overlap reference disagrees with the distinct-subsequence oracle")
    boundaries = [("z" * 974 + "abcdefghijklmnopqrstuvwxyz", "abcdefghijklmnopqrstuvwxyz"),
                  ("zyxwvutsrqponmlkjihgfedcba", "zyxwvutsrqponmlkjihgfedcba"),
                  ("a" * 1000, "a"), ("cbacdcbc", "acdb")]
    for text, expected in boundaries:
        if function(text) != expected:
            raise ValueError("Distinct-subsequence source boundary disagrees")
    return {"oracle_inputs": 500, "oracle_seed": 5128,
            "workbook_sample_checked": True, "deterministic_inputs": 5,
            "largest_input": 1000,
            "domain": "1–1000 lowercase letters; order-preserving subsequence with each distinct letter exactly once"}


def check_bulb_square_root(payload, source):
    from .build_import_batch import workbook_sample
    namespace = {}
    exec(compile(payload["reference_solution"], "<reviewed-bulb-square-root>", "exec"), namespace)
    function = namespace[payload["signature"]["name"]]
    # Parameter spelling differs (source n, target x), but both take one integer.
    sample = workbook_sample(source['sample'], [{'name': 'n'}])
    if sample is None or function(*sample[0]) != sample[1]:
        raise ValueError('Bulb workbook sample disagrees')
    rng = random.Random(4047 + 319)
    for _ in range(500):
        n = rng.randint(0, 2000)
        bulbs = [False] * (n+1)
        for step in range(1, n+1):
            for position in range(step, n+1, step):
                bulbs[position] = not bulbs[position]
        if function(n) != sum(bulbs):
            raise ValueError('Overlap reference disagrees with literal bulb simulation')
    squares = [value*value for value in range(1, 31623)]
    for _ in range(500):
        n = rng.randint(0, 10**9)
        if function(n) != sum(square <= n for square in squares):
            raise ValueError('Overlap reference disagrees with perfect-square enumeration')
    boundaries = {0, 1, 10**9}
    for root in (2, 3, 31, 100, 1000, 31622):
        boundaries.update((root*root-1, root*root, root*root+1))
    for n in sorted(boundaries):
        if function(n) != sum(square <= n for square in squares):
            raise ValueError('Bulb square boundary disagrees')
    return {'oracle_inputs': 1000, 'oracle_seed': 4366,
            'literal_simulation_inputs': 500, 'full_domain_square_enumeration_inputs': 500,
            'workbook_sample_checked': True, 'deterministic_inputs': len(boundaries)+1,
            'largest_input': 10**9,
            'domain': 'n=0..10^9; odd divisor counts occur exactly at perfect-square bulb positions'}


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
            checker = {2220: check_bit_flips, 46: check_unique_permutations, 153: check_unique_rotations, 1081: check_distinct_subsequence,
                       319: check_bulb_square_root}[source_id]
            evidence = checker(payload, sources[source_id])
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
