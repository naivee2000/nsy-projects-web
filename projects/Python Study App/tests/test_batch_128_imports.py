import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_128 import BATCH

ROOT = Path(__file__).resolve().parents[1]
IDS = (2317, 2319, 2320, 2321, 2325)


def test_batch_128_first_slice_is_complete_and_verified():
    catalog = get_catalog()
    for source_id in IDS:
        problem = catalog[f'leetcode-{source_id}']
        report = json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(t.visible for t in problem.tests) >= 2
        assert sum(not t.visible for t in problem.tests) >= 12
        assert len(problem.hints) == 4
        assert report['valid'] and report['oracle_inputs'] == 500
        assert report['reference_passed'] == len(problem.tests)
        assert all(w['failed_cases'] for w in report['wrong_solutions'])


def test_batch_128_first_slice_inputs_are_distinct():
    for source_id in IDS:
        inputs = [a for a,_ in BATCH[source_id]['examples']] + BATCH[source_id]['boundaries']
        encoded = [json.dumps(a,sort_keys=True) for a in inputs]
        assert len(encoded) == len(set(encoded))
