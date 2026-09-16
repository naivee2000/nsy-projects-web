import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_122c import BATCH


ROOT = Path(__file__).resolve().parents[1]
VALID_IDS = (2191, 2192, 2194)
QUARANTINED_IDS = (2193, 2195)


def test_batch_122_third_slice_verified_entries_are_complete():
    catalog = get_catalog()
    for source_id in VALID_IDS:
        problem = catalog[f"leetcode-{source_id}"]
        report = json.loads(
            (ROOT / "catalog_import/reports" / f"leetcode-{source_id}.json").read_text()
        )
        assert sum(case.visible for case in problem.tests) >= 2
        assert sum(not case.visible for case in problem.tests) >= 12
        assert len(problem.hints) == 4
        assert report["valid"]
        assert report["reference_passed"] == len(problem.tests)
        assert report["oracle_inputs"] == 500
        assert all(item["failed_cases"] for item in report["wrong_solutions"])


def test_batch_122_third_slice_inputs_are_distinct():
    for source_id in (*VALID_IDS, *QUARANTINED_IDS):
        spec = BATCH[source_id]
        inputs = [arguments for arguments, _ in spec["examples"]] + spec["boundaries"]
        encoded = [json.dumps(arguments, sort_keys=True) for arguments in inputs]
        assert len(encoded) == len(set(encoded))


def test_repaired_candidates_are_verified_and_visible():
    catalog = get_catalog()
    ledger = json.loads((ROOT / "catalog_import/ledger.json").read_text())
    records = {record["source_id"]: record for record in ledger["records"]}
    for source_id in QUARANTINED_IDS:
        assert records[source_id]["status"] == "imported"
        assert f"leetcode-{source_id}" in catalog
        report = json.loads((ROOT / "catalog_import/reports" / f"leetcode-{source_id}.json").read_text())
        assert report["valid"] and report["oracle_inputs"] == 500
        assert all(control["failed_cases"] for control in report["wrong_solutions"])
