import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_203a import BATCH as A
from code_practice.import_batch_203b import BATCH as B

ROOT=Path(__file__).resolve().parents[1]
BATCH={**A,**B};IDS=(755,768,773,780,801,805,814,815)

def test_batch_203_verified_subset():
    catalog=get_catalog()
    for source_id in IDS:
        problem=catalog[f'leetcode-{source_id}']
        report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(test.visible for test in problem.tests)>=2
        assert sum(not test.visible for test in problem.tests)>=12
        assert len(problem.hints)==4 and report['valid'] and report['oracle_inputs']==500
        assert all(item['failed_cases'] for item in report['wrong_solutions'])

def test_batch_203_inputs_are_distinct():
    for source_id in IDS:
        spec=BATCH[source_id];values=[args for args,_ in spec['examples']]+spec['boundaries']
        encoded=[json.dumps(args,sort_keys=True) for args in values]
        assert len(encoded)==len(set(encoded))
