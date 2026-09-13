"""Offline batch validation. Never imported by the web application.

Run `python -m code_practice.build_import_batch` to reproduce all reviewed batches,
or use --ids to validate a specific group without repeating completed work.
"""
from __future__ import annotations

from collections import Counter
import argparse
import ast
import hashlib
import inspect
import json
import multiprocessing
from pathlib import Path
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .import_batch_001 import BATCH as BATCH_001
from .import_batch_002 import BATCH as BATCH_002
from .import_batch_003 import BATCH as BATCH_003
from .import_batch_004 import BATCH as BATCH_004
from .import_batch_005 import BATCH as BATCH_005
from .import_batch_006 import BATCH as BATCH_006
from .import_batch_007 import BATCH as BATCH_007
from .import_batch_008 import BATCH as BATCH_008
from .import_batch_009 import BATCH as BATCH_009
from .import_batch_010 import BATCH as BATCH_010
from .import_batch_011 import BATCH as BATCH_011
from .import_batch_012 import BATCH as BATCH_012
from .import_batch_013 import BATCH as BATCH_013
from .import_batch_014 import BATCH as BATCH_014
from .import_batch_015 import BATCH as BATCH_015
from .import_batch_016 import BATCH as BATCH_016
from .import_batch_017 import BATCH as BATCH_017
from .import_batch_018 import BATCH as BATCH_018
from .import_batch_019 import BATCH as BATCH_019
from .import_batch_020 import BATCH as BATCH_020
from .import_batch_021 import BATCH as BATCH_021
from .import_batch_022 import BATCH as BATCH_022
from .import_batch_023 import BATCH as BATCH_023
from .import_batch_024 import BATCH as BATCH_024
from .import_batch_025 import BATCH as BATCH_025
from .import_batch_026 import BATCH as BATCH_026
from .import_batch_027 import BATCH as BATCH_027
from .import_batch_028 import BATCH as BATCH_028
from .import_batch_029 import BATCH as BATCH_029
from .import_batch_030 import BATCH as BATCH_030
from .import_batch_031 import BATCH as BATCH_031
from .import_batch_032 import BATCH as BATCH_032
from .import_batch_033 import BATCH as BATCH_033
from .import_batch_034 import BATCH as BATCH_034
from .import_batch_035 import BATCH as BATCH_035
from .import_batch_036 import BATCH as BATCH_036
from .import_batch_037 import BATCH as BATCH_037
from .import_batch_038 import BATCH as BATCH_038
from .import_batch_039 import BATCH as BATCH_039
from .import_batch_040 import BATCH as BATCH_040
from .import_batch_041 import BATCH as BATCH_041
from .import_batch_042 import BATCH as BATCH_042
from .import_batch_043 import BATCH as BATCH_043
from .import_batch_044 import BATCH as BATCH_044
from .import_batch_045 import BATCH as BATCH_045
from .import_batch_046 import BATCH as BATCH_046
from .import_batch_047 import BATCH as BATCH_047
from .import_batch_048 import BATCH as BATCH_048
from .import_batch_049 import BATCH as BATCH_049
from .import_batch_050 import BATCH as BATCH_050
from .import_batch_051 import BATCH as BATCH_051
from .import_batch_052 import BATCH as BATCH_052
from .import_batch_053 import BATCH as BATCH_053
from .import_batch_054 import BATCH as BATCH_054
from .import_batch_055 import BATCH as BATCH_055
from .import_batch_055b import BATCH as BATCH_055B
from .import_batch_056 import BATCH as BATCH_056
from .import_batch_057 import BATCH as BATCH_057
from .import_batch_058 import BATCH as BATCH_058
from .import_batch_059 import BATCH as BATCH_059
from .import_batch_060 import BATCH as BATCH_060
from .import_batch_061 import BATCH as BATCH_061
from .import_batch_062 import BATCH as BATCH_062
from .import_batch_063 import BATCH as BATCH_063
from .import_batch_064 import BATCH as BATCH_064
from .import_batch_065 import BATCH as BATCH_065
from .import_batch_066 import BATCH as BATCH_066
from .import_batch_067 import BATCH as BATCH_067
from .import_batch_068 import BATCH as BATCH_068
from .import_batch_069 import BATCH as BATCH_069
from .import_batch_070 import BATCH as BATCH_070
from .import_batch_071 import BATCH as BATCH_071
from .import_batch_072 import BATCH as BATCH_072
from .import_batch_073 import BATCH as BATCH_073
from .import_batch_074 import BATCH as BATCH_074
from .import_batch_075 import BATCH as BATCH_075
from .import_batch_076 import BATCH as BATCH_076
from .import_batch_077 import BATCH as BATCH_077
from .import_batch_078 import BATCH as BATCH_078
from .import_batch_079 import BATCH as BATCH_079
from .import_batch_080 import BATCH as BATCH_080
from .import_batch_080b import BATCH as BATCH_080B
from .import_batch_081 import BATCH as BATCH_081
from .import_batch_081b import BATCH as BATCH_081B
from .import_batch_082 import BATCH as BATCH_082
from .import_batch_082b import BATCH as BATCH_082B
from .import_batch_083 import BATCH as BATCH_083
from .import_batch_084 import BATCH as BATCH_084
from .catalog_evidence import judge_contract_hash
from .catalog_artifacts import write_json_atomic
from .schemas import ProblemDefinition, TestCase
from .starter_code import with_support_classes
from .validation import compare_result, run_source

ROOT = Path(__file__).resolve().parent.parent
VALIDATION_PROTOCOL_VERSION = 2
BATCH = {**BATCH_001, **BATCH_002, **BATCH_003, **BATCH_004, **BATCH_005, **BATCH_006, **BATCH_007, **BATCH_008, **BATCH_009, **BATCH_010, **BATCH_011, **BATCH_012, **BATCH_013, **BATCH_014, **BATCH_015, **BATCH_016, **BATCH_017, **BATCH_018, **BATCH_019, **BATCH_020, **BATCH_021, **BATCH_022, **BATCH_023, **BATCH_024, **BATCH_025, **BATCH_026, **BATCH_027, **BATCH_028, **BATCH_029, **BATCH_030, **BATCH_031, **BATCH_032, **BATCH_033, **BATCH_034, **BATCH_035, **BATCH_036}


BATCH.update(BATCH_037)
BATCH.update(BATCH_038)
BATCH.update(BATCH_039)
BATCH.update(BATCH_040)
BATCH.update(BATCH_041)
BATCH.update(BATCH_042)
BATCH.update(BATCH_043)
BATCH.update(BATCH_044)
BATCH.update(BATCH_045)
BATCH.update(BATCH_046)
BATCH.update(BATCH_047)
BATCH.update(BATCH_048)
BATCH.update(BATCH_049)
BATCH.update(BATCH_050)
BATCH.update(BATCH_051)
BATCH.update(BATCH_052)
BATCH.update(BATCH_053)
BATCH.update(BATCH_054)
BATCH.update(BATCH_055)
BATCH.update(BATCH_055B)
BATCH.update(BATCH_056)
BATCH.update(BATCH_057)
BATCH.update(BATCH_058)
BATCH.update(BATCH_059)
BATCH.update(BATCH_060)
BATCH.update(BATCH_061)
BATCH.update(BATCH_062)
BATCH.update(BATCH_063)
BATCH.update(BATCH_064)
BATCH.update(BATCH_065)
BATCH.update(BATCH_066)
BATCH.update(BATCH_067)
BATCH.update(BATCH_068)
BATCH.update(BATCH_069)
BATCH.update(BATCH_070)
BATCH.update(BATCH_071)
BATCH.update(BATCH_072)
BATCH.update(BATCH_073)
BATCH.update(BATCH_074)
BATCH.update(BATCH_075)
BATCH.update(BATCH_076)
BATCH.update(BATCH_077)
BATCH.update(BATCH_078)
BATCH.update(BATCH_079)
BATCH.update(BATCH_080)
BATCH.update(BATCH_080B)
BATCH.update(BATCH_081)
BATCH.update(BATCH_081B)
BATCH.update(BATCH_082)
BATCH.update(BATCH_082B)
BATCH.update(BATCH_083)
BATCH.update(BATCH_084)


def digest(payload):
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def batch_implementation_hash(spec):
    """Hash the source that supplies this problem's oracle and generator."""
    return hashlib.sha256(Path(inspect.getsourcefile(spec["oracle"])).read_bytes()).hexdigest()


def validation_cache_key(spec, source_hash):
    """Stable evidence identity; bump the protocol only for semantic validator changes."""
    payload = {
        "protocol": VALIDATION_PROTOCOL_VERSION,
        "source_hash": source_hash,
        "batch_implementation_sha256": batch_implementation_hash(spec),
        "judge_contract_sha256": judge_contract_hash(),
    }
    return digest(payload)


def cached_validation_is_current(pid, spec, source_hash, record, root=ROOT):
    """Return true only for a complete, unchanged approved validation bundle."""
    if record.get("status") != "imported" or record.get("source_hash") != source_hash:
        return False
    try:
        report = json.loads((root / record["validation_report"]).read_text())
        candidate = json.loads((root / "catalog_import/candidates" / f"leetcode-{pid}.json").read_text())
        if not (report.get("valid") and report.get("problem_id") == f"leetcode-{pid}"
                and report.get("content_sha256") == digest(candidate)
                and report.get("source_hash") == source_hash
                and report.get("judge_contract_sha256") == judge_contract_hash()
                and report.get("batch_implementation_sha256") == batch_implementation_hash(spec)
                and report.get("reference_passed") == len(candidate["tests"])
                and report.get("visible_tests", 0) >= 2 and report.get("hidden_tests", 0) >= 12
                and report.get("oracle_inputs", 0) >= 500
                and len(report.get("wrong_solutions", [])) >= 2
                and all(w.get("failed_cases") for w in report["wrong_solutions"])):
            return False
        # Reports written before protocol v2 have equivalent evidence fields. They
        # remain reusable until their problem, source, oracle batch, or judge changes.
        return report.get("validation_cache_key") in {None, validation_cache_key(spec, source_hash)}
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False


def workbook_sample(sample, parameters, result_mode="return", mutated_parameter=None):
    """Parse only JSON/Python literals in the workbook's input/output notation.

    Calls, attribute access, comprehensions, and arbitrary expressions are never
    evaluated. Unrecognized samples must be reviewed explicitly, not skipped.
    """
    if not sample:
        return None
    if not sample.startswith("Input ") or " → Output " not in sample:
        raise ValueError("Workbook sample needs manual parsing/reconciliation")
    arguments, output = sample[6:].split(" → Output ", 1)
    class JsonNames(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id in {"null", "true", "false"}:
                return ast.Constant({"null": None, "true": True, "false": False}[node.id])
            return node
    call = ast.parse(f"sample({arguments})", mode="eval").body
    if call.args:
        if call.keywords:
            raise ValueError("Mixed named/positional workbook inputs require review")
        args = [ast.literal_eval(JsonNames().visit(value)) for value in call.args]
    else:
        normalized = lambda name: name.replace("_", "").casefold()
        values = {normalized(k.arg): ast.literal_eval(JsonNames().visit(k.value)) for k in call.keywords if k.arg}
        if set(values) != {normalized(p["name"]) for p in parameters}:
            raise ValueError("Workbook parameter names do not match the reviewed signature")
        args = [values[normalized(p["name"])] for p in parameters]
    if len(args) != len(parameters):
        raise ValueError("Workbook argument count differs from the reviewed signature")
    value = output[:-1] if output.endswith(".") else output
    if result_mode == "returned_prefix":
        output_call = ast.parse(f"sample({value})", mode="eval").body
        if len(output_call.args) != 1 or len(output_call.keywords) != 1 or mutated_parameter is None:
            raise ValueError("Prefix sample requires one count and one updated list")
        count = ast.literal_eval(output_call.args[0])
        keyword = output_call.keywords[0]
        if keyword.arg != parameters[mutated_parameter]["name"] or not isinstance(keyword.value, ast.List):
            raise ValueError("Prefix sample must name the mutated list parameter")
        if type(count) is not int or not 0 <= count <= len(keyword.value.elts):
            raise ValueError("Invalid returned prefix length in workbook sample")
        values = []
        for index, element in enumerate(keyword.value.elts):
            if isinstance(element, ast.Name) and element.id == "_":
                if index < count:
                    raise ValueError("Unspecified values are only allowed after the checked prefix")
                values.append(None)
            else:
                values.append(ast.literal_eval(JsonNames().visit(element)))
        expected = {"return": count, "prefix": values[:count]}
    else:
        expected = ast.literal_eval(JsonNames().visit(ast.parse(value, mode="eval").body))
    return args, expected


def build(pid, spec, source):
    examples = spec["examples"]
    hidden = spec["boundaries"]
    comparator = spec.get("comparator", "exact")
    args_seen = {json.dumps(args, sort_keys=True) for args, _ in examples}
    hidden_keys = [json.dumps(args, sort_keys=True) for args in hidden]
    if len(hidden_keys) != len(set(hidden_keys)) or args_seen.intersection(hidden_keys):
        raise ValueError(f"{pid}: repeated test inputs")
    parameter_sources = spec.get("parameter_sources", {})
    parameters = [dict(name=n, annotation=a, adapter=d,
                       source_parameter=parameter_sources.get(index))
                  for index, (n, a, d) in enumerate(spec["params"])]
    mode = spec.get("result_mode", "return")
    sample_adapter = spec.get("sample_contract_adapter")
    if sample_adapter:
        if (set(sample_adapter) != {"source_sample", "arguments", "expected", "reason"}
                or sample_adapter["source_sample"] != source["sample"]
                or not isinstance(sample_adapter["reason"], str)
                or not sample_adapter["reason"].strip()):
            raise ValueError(f"{pid}: invalid or stale workbook sample contract adapter")
        sample = (sample_adapter["arguments"], sample_adapter["expected"])
    else:
        sample = workbook_sample(source["sample"], parameters, mode, spec.get("mutated_parameter"))
    correction = spec.get("sample_correction")
    if correction and sample is None:
        raise ValueError(f"{pid}: cannot correct a missing workbook sample")
    if sample is not None:
        args, expected = sample
        if correction:
            if (set(correction) != {"original_expected", "corrected_expected", "reason"}
                    or expected != correction["original_expected"]
                    or not isinstance(correction["reason"], str) or not correction["reason"].strip()
                    or compare_result(spec["oracle"](args), expected, comparator, mode)):
                raise ValueError(f"{pid}: invalid or stale workbook sample correction")
            expected = correction["corrected_expected"]
        if not compare_result(spec["oracle"](args), expected, comparator, mode):
            raise ValueError(f"{pid}: workbook sample conflicts with the independent oracle")
        if not any(example_args == args for example_args, _ in examples):
            raise ValueError(f"{pid}: the correct workbook sample must remain a visible example")
    test_inputs = [(a, True, explanation) for a, explanation in examples] + [(a, False, None) for a in hidden]
    tests = [dict(id=f"lc-{pid}-{i+1}", arguments=args, expected=spec["oracle"](args),
                  comparator=comparator, visible=visible, explanation=explanation)
             for i, (args, visible, explanation) in enumerate(test_inputs)]
    for i, (args, expected) in enumerate(spec.get("stress", [])):
        key = json.dumps(args, sort_keys=True)
        if key in args_seen or key in hidden_keys:
            raise ValueError(f"{pid}: stress input duplicates an example or hidden case")
        hidden_keys.append(key)
        tests.append(dict(id=f"lc-{pid}-stress-{i+1}", arguments=args, expected=expected,
                          comparator=comparator, visible=False))
    if spec.get("node_order"):
        for test in tests:
            test["expected_node_order"] = spec["node_order"](test["arguments"])
    rubric = {3: (1, 1, 1, 0, 0), 5: (2, 1, 1, 1, 0), 6: (2, 1, 1, 1, 1),
              7: (2, 2, 1, 1, 1), 8: (3, 2, 1, 1, 1)}[spec["difficulty"]]
    starter = f"def {spec['name']}({', '.join(n + ': ' + a for n, a, _ in spec['params'])}) -> {spec['returns']}:\n    # Write your solution here.\n    pass\n"
    statement = spec.get("statement", source["statement"])
    summary = statement.split(". ", 1)[0]
    payload = dict(id=f"leetcode-{pid}", version=spec.get("version", 1), status="approved", title=source["title"],
        summary=summary + ("." if not summary.endswith(".") else ""),
        statement=statement, constraints=spec["constraints"], topics=spec["topics"],
        prerequisites=spec.get("prerequisites", spec["topics"][:1] if spec["difficulty"] >= 8 else []),
        signature=dict(name=spec["name"], parameters=parameters, returns=spec["returns"], return_adapter=spec["adapter"],
                       node_policy=spec.get("node_policy", "values"), result_mode=mode,
                       mutated_parameter=spec.get("mutated_parameter"),
                       immutable_parameters=spec.get("immutable_parameters", [])),
        starter_code=with_support_classes(starter, [p["adapter"] for p in parameters] + [spec["adapter"]]),
        reference_solution=spec["reference"], brute_force_solution=None, known_wrong_solutions=spec["wrong"],
        target_time_complexity=spec["time"], target_space_complexity=spec["space"],
        estimated_minutes=20 if spec["difficulty"] <= 3 else 50 if spec["difficulty"] >= 8 else 35,
        rubric=dict(zip(("algorithmic_insight", "prerequisites", "implementation", "performance_pressure", "edge_cases"), rubric)),
        hints=spec["hints"], editorial=spec["editorial"], tests=tests)
    return ProblemDefinition.model_validate(payload)


def verify(problem, spec, source_hash):
    started = time.perf_counter()
    failures, rejected = [], []
    for case in problem.tests:
        ok, error = run_source(problem.reference_solution, problem, case)
        if not ok:
            failures.append({"phase": "deterministic", "case": case.id, "error": error})
    for index, wrong in enumerate(problem.known_wrong_solutions):
        evidence = []
        for case in problem.tests:
            ok, error = run_source(wrong, problem, case)
            # Require an algorithmic wrong answer, not syntax errors or an exception.
            if not ok and error is None:
                evidence.append(case.id)
        rejected.append({"reason": spec["wrong_reasons"][index], "failed_cases": evidence})
        if not evidence:
            failures.append({"phase": "known_wrong", "index": index})
    seed, checked = 4047 + int(problem.id.split("-")[-1]), 0
    rng = random.Random(seed)
    for i in range(500):
        args = spec["generator"](rng)
        case = TestCase(id=f"oracle-{i}", arguments=args, expected=spec["oracle"](args), comparator=spec.get("comparator", "exact"),
                        expected_node_order=spec["node_order"](args) if spec.get("node_order") else None)
        ok, error = run_source(problem.reference_solution, problem, case)
        if not ok:
            failures.append({"phase": "oracle", "case": i, "arguments": args, "error": error})
        checked += 1
    batch_path = Path(inspect.getsourcefile(spec["oracle"]))
    return {"valid": not failures, "problem_id": problem.id, "content_sha256": digest(problem.model_dump(mode="json")),
        "source_hash": source_hash, "visible_tests": sum(t.visible for t in problem.tests),
        "hidden_tests": sum(not t.visible for t in problem.tests),
        "reference_passed": len(problem.tests) - sum(f["phase"] == "deterministic" for f in failures),
        "wrong_solutions": rejected, "oracle_inputs": checked, "oracle_seed": seed,
        "oracle_implementation": f"code_practice/{batch_path.name}:{spec['oracle'].__name__}",
        "validator_implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "batch_implementation_sha256": batch_implementation_hash(spec),
        "judge_contract_sha256": judge_contract_hash(),
        "validation_protocol_version": VALIDATION_PROTOCOL_VERSION,
        "validation_cache_key": validation_cache_key(spec, source_hash),
        "elapsed_seconds": round(time.perf_counter() - started, 3), "failures": failures}


def _review_child(pid, spec, source, source_hash, connection):
    try:
        problem = build(pid, spec, source)
        report = verify(problem, spec, source_hash)
        report["workbook_sample"] = "preserved and independently verified" if source["sample"] else "missing in workbook; reviewed examples authored"
        if spec.get("sample_contract_adapter"):
            report["workbook_sample"] = "source sample preserved through an explicit callable-context adapter"
            report["sample_contract_adapter"] = {
                **spec["sample_contract_adapter"],
                "source_reference": source["reference_url"],
            }
        if spec.get("sample_correction"):
            report["workbook_sample"] = "original input preserved; erroneous workbook output explicitly corrected"
            report["sample_correction"] = {**spec["sample_correction"], "original_sample": source["sample"],
                                           "source_reference": source["reference_url"]}
        connection.send((problem.model_dump(mode="json"), report))
    except Exception as error:
        connection.send((None, {"valid": False, "problem_id": f"leetcode-{pid}", "source_hash": source_hash,
                                "failures": [{"phase": "build", "error": f"{type(error).__name__}: {error}"}]}))
    finally:
        connection.close()


def review_isolated(pid, spec, source, source_hash, timeout_seconds=30):
    """One bounded child process per problem; a failure cannot poison the next."""
    context = multiprocessing.get_context("spawn")
    incoming, outgoing = context.Pipe(duplex=False)
    process = context.Process(target=_review_child, args=(pid, spec, source, source_hash, outgoing))
    process.start()
    outgoing.close()
    try:
        if incoming.poll(timeout_seconds):
            try:
                return incoming.recv()
            except EOFError:
                message = "Validator exited before returning evidence"
        else:
            message = f"Validation exceeded {timeout_seconds} seconds"
        return None, {"valid": False, "problem_id": f"leetcode-{pid}", "source_hash": source_hash,
                      "failures": [{"phase": "isolated_validation", "error": message}]}
    finally:
        incoming.close()
        process.join(.2)
        if process.is_alive():
            process.terminate()
            process.join(2)
        if process.is_alive():
            process.kill()
            process.join(2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="+", type=int)
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--jobs", type=int, default=4, help="Concurrent isolated validators (1-4).")
    parser.add_argument("--force", action="store_true", help="Revalidate selected imports even when evidence is current.")
    args = parser.parse_args()
    if args.ids and any(pid not in BATCH for pid in args.ids):
        parser.error("Each requested ID must have a reviewed batch specification")
    if args.timeout_seconds <= 0:
        parser.error("Timeout must be positive")
    if not 1 <= args.jobs <= 4:
        parser.error("--jobs must be between 1 and 4")
    ledger_path = ROOT / "catalog_import/ledger.json"
    ledger = json.loads(ledger_path.read_text())
    sources = {s["source_id"]: s for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines() if (s := json.loads(line))}
    reports = ROOT / "catalog_import/reports"
    candidates = ROOT / "catalog_import/candidates"
    reports.mkdir(exist_ok=True)
    candidates.mkdir(exist_ok=True)
    records = {r["source_id"]: r for r in ledger["records"]}
    selected = [pid for pid in BATCH if not args.ids or pid in args.ids]
    work = []
    skipped = []
    for pid in selected:
        spec = BATCH[pid]
        record = records[pid]
        if record["status"] in {"overlap", "excluded"}:
            if args.ids:
                raise ValueError(f"{pid}: cannot import an overlap or excluded interface")
            skipped.append(pid)
            continue
        if not args.force and cached_validation_is_current(pid, spec, record["source_hash"], record):
            skipped.append(pid)
            continue
        work.append((pid, spec, sources[pid], record["source_hash"]))

    results = {}
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=min(args.jobs, max(1, len(work)))) as executor:
        futures = {executor.submit(review_isolated, pid, spec, source, source_hash, args.timeout_seconds): pid
                   for pid, spec, source, source_hash in work}
        for future in as_completed(futures):
            pid = futures[future]
            results[pid] = future.result()

    # A single parent is the only writer for candidates, reports, and the ledger.
    for pid, spec, source, source_hash in work:
        payload, report = results[pid]
        record = records[pid]
        problem_id = f"leetcode-{pid}"
        report_path = reports / f"{problem_id}.json"
        write_json_atomic(report_path, report)
        if payload is not None:
            write_json_atomic(candidates / f"{problem_id}.json", payload, compact=True)
        record.update(status="imported" if report["valid"] else "quarantined",
                      problem_id=problem_id, validation_report=str(report_path.relative_to(ROOT)),
                      reason="Reviewed contract and independent oracle; see validation report." if report["valid"] else "Failed validation; excluded from runnable catalog.")
        print(problem_id, "PASS" if report["valid"] else report["failures"], flush=True)
    ledger["counts"] = dict(Counter(r["status"] for r in ledger["records"]))
    if work:
        write_json_atomic(ledger_path, ledger)
    print(json.dumps({"validated": len(work), "reused": len(skipped), "elapsed_seconds": round(time.perf_counter() - started, 3),
                      "counts": ledger["counts"]}), flush=True)


if __name__ == "__main__":
    main()
