import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_191a import BATCH as A
from code_practice.import_batch_191b import BATCH as B

ROOT=Path(__file__).resolve().parents[1]
SPECS={**A,**B}
IDS=tuple(SPECS)

def test_batch_191_verified():
    catalog=get_catalog()
    for source_id in IDS:
        problem=catalog[f'leetcode-{source_id}']
        report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(test.visible for test in problem.tests)>=2
        assert sum(not test.visible for test in problem.tests)>=12
        assert len(problem.hints)==4
        assert report['valid'] and report['oracle_inputs']==500
        assert all(control['failed_cases'] for control in report['wrong_solutions'])

def test_batch_191_inputs_are_distinct():
    for spec in SPECS.values():
        cases=[args for args,_ in spec['examples']]+spec['boundaries']
        encoded=[json.dumps(args,sort_keys=True) for args in cases]
        assert len(encoded)==len(set(encoded))
