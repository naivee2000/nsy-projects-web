import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_204a import BATCH as A
from code_practice.import_batch_204b import BATCH as B
from code_practice.import_batch_204c import BATCH as C
from code_practice.import_batch_204d import BATCH as D

ROOT=Path(__file__).resolve().parents[1];BATCH={**A,**B,**C,**D};IDS=tuple(BATCH)

def test_batch_204_verified():
    catalog=get_catalog()
    for source_id in IDS:
        problem=catalog[f'leetcode-{source_id}'];report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(test.visible for test in problem.tests)>=2 and sum(not test.visible for test in problem.tests)>=12
        assert len(problem.hints)==4 and report['valid'] and report['oracle_inputs']==500
        assert len(report['wrong_solutions'])>=2 and all(item['failed_cases'] for item in report['wrong_solutions'])

def test_batch_204_inputs_are_distinct():
    for spec in BATCH.values():
        values=[args for args,_ in spec['examples']]+spec['boundaries'];encoded=[json.dumps(args,sort_keys=True) for args in values]
        assert len(encoded)==len(set(encoded))
