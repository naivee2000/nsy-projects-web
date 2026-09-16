import json
from copy import deepcopy
from pathlib import Path

from code_practice.build_import_batch import BATCH, cached_validation_is_current
from code_practice.catalog import get_catalog


ROOT = Path(__file__).resolve().parents[1]
RECOVERED = (
    737, 758, 916, 947, 1072, 1087, 1275, 1356, 1602, 1616, 1620,
    2193, 2195, 2663, 3012, 3354, 3464, 3505, 3740, 3951, 3997, 4039,
)


def test_recovered_controls_are_verified_and_packaged():
    catalog = get_catalog()
    records = {row["source_id"]: row for row in json.loads(
        (ROOT / "catalog_import" / "ledger.json").read_text())["records"]}
    for source_id in RECOVERED:
        record = records[source_id]
        report = json.loads((ROOT / "catalog_import" / "reports" / f"leetcode-{source_id}.json").read_text())
        problem = catalog[f"leetcode-{source_id}"]
        assert record["status"] == "imported"
        assert cached_validation_is_current(source_id, BATCH[source_id], record["source_hash"], record)
        assert report["valid"] and report["reference_passed"] == len(problem.tests)
        assert report["oracle_inputs"] >= 500
        assert len(report["wrong_solutions"]) >= 2
        assert all(control["failed_cases"] for control in report["wrong_solutions"])
        assert sum(test.visible for test in problem.tests) >= 2
        assert sum(not test.visible for test in problem.tests) >= 12


def test_control_overrides_leave_unrelated_oracle_evidence_current():
    records = {row["source_id"]: row for row in json.loads(
        (ROOT / "catalog_import" / "ledger.json").read_text())["records"]}
    for source_id in (755, 898, 1619, 2191):
        record = records[source_id]
        assert cached_validation_is_current(source_id, BATCH[source_id], record["source_hash"], record)


def test_cache_invalidates_when_order_contract_changes():
    record = next(row for row in json.loads((ROOT / "catalog_import/ledger.json").read_text())["records"]
                  if row["source_id"] == 916)
    assert cached_validation_is_current(916, BATCH[916], record["source_hash"], record)
    altered = deepcopy(BATCH[916])
    altered["comparator"] = "exact"
    assert not cached_validation_is_current(916, altered, record["source_hash"], record)
    altered = deepcopy(BATCH[916])
    altered["constraints"][1] = "Return universal words in input order."
    assert not cached_validation_is_current(916, altered, record["source_hash"], record)
