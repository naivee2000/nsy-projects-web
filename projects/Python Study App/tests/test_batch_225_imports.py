import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_225a import BATCH

ROOT=Path(__file__).resolve().parents[1]


def test_batch_225_verified():
    catalog=get_catalog()
    for source_id,spec in BATCH.items():
        problem=catalog.get(f'leetcode-{source_id}')
        report=json.loads((ROOT/'catalog_import'/'reports'/f'leetcode-{source_id}.json').read_text())
        assert problem.signature.name==spec['name']
        assert sum(test.visible for test in problem.tests)>=2
        assert sum(not test.visible for test in problem.tests)>=12
        assert len(problem.hints)==4 and report['valid']
        assert report['reference_passed']==len(problem.tests)
        assert report['oracle_inputs']>=500
        assert len(report['wrong_solutions'])>=2
        assert all(item['failed_cases'] for item in report['wrong_solutions'])


def test_batch_225_inputs_are_distinct():
    for spec in BATCH.values():
        values=[args for args,_ in spec['examples']]+spec['boundaries']
        encoded=[json.dumps(value,sort_keys=True) for value in values]
        assert len(encoded)==len(set(encoded))
