import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_220a import BATCH
ROOT=Path(__file__).resolve().parents[1]

def test_batch_220_verified():
    catalog=get_catalog()
    for source_id in BATCH:
        problem=catalog[f'leetcode-{source_id}'];report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(t.visible for t in problem.tests)>=2 and sum(not t.visible for t in problem.tests)>=12
        assert len(problem.hints)==4 and report['valid'] and report['oracle_inputs']==500
        assert len(report['wrong_solutions'])>=2 and all(x['failed_cases'] for x in report['wrong_solutions'])

def test_batch_220_inputs_are_distinct():
    for spec in BATCH.values():
        values=[a for a,_ in spec['examples']]+spec['boundaries'];encoded=[json.dumps(a,sort_keys=True) for a in values]
        assert len(encoded)==len(set(encoded))
