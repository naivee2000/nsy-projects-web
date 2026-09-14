import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_156 import BATCH

ROOT = Path(__file__).resolve().parents[1]
IDS = (2555, 2556, 2557, 2559, 2560)


def test_batch_156_is_complete_and_verified():
    catalog = get_catalog()
    for source_id in IDS:
        problem = catalog[f"leetcode-{source_id}"]
        report = json.loads(
            (ROOT / "catalog_import/reports" / f"leetcode-{source_id}.json").read_text()
        )
        assert (
            sum(t.visible for t in problem.tests) >= 2
            and sum(not t.visible for t in problem.tests) >= 12
        )
        assert (
            len(problem.hints) == 4
            and report["valid"]
            and report["oracle_inputs"] == 500
        )
        assert report["reference_passed"] == len(problem.tests) and all(
            x["failed_cases"] for x in report["wrong_solutions"]
        )


def test_batch_156_inputs_are_distinct():
    for source_id in IDS:
        values = [a for a, _ in BATCH[source_id]["examples"]] + BATCH[source_id][
            "boundaries"
        ]
        encoded = [json.dumps(a, sort_keys=True) for a in values]
        assert len(encoded) == len(set(encoded))
