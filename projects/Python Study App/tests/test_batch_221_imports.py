import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_221a import BATCH as BATCH_A
from code_practice.import_batch_221b import BATCH as BATCH_B
from code_practice.import_batch_221c import BATCH as BATCH_C
from code_practice.import_batch_221d import BATCH as BATCH_D
BATCH={**BATCH_A,**BATCH_B,**BATCH_C,**BATCH_D}

ROOT=Path(__file__).resolve().parents[1]


def test_batch_221_verified():
    catalog=get_catalog()
    for source_id,spec in BATCH.items():
        problem_id=f'leetcode-{source_id}'
        problem=catalog.get(problem_id)
        report=json.loads((ROOT/'catalog_import'/'reports'/f'{problem_id}.json').read_text())
        assert problem.id==problem_id
        assert report['valid'] is True
        assert report['reference_passed']==len(problem.tests)
        assert report['visible_tests']>=2
        assert report['hidden_tests']>=12
        assert report['oracle_inputs']>=500
        assert len(report['wrong_solutions'])>=2
        assert all(item['failed_cases'] for item in report['wrong_solutions'])
        assert problem.signature.name==spec['name']


def test_batch_221_workbook_samples_are_visible():
    catalog=get_catalog()
    for source_id in BATCH:
        problem=catalog.get(f'leetcode-{source_id}')
        assert sum(test.visible for test in problem.tests)>=2
