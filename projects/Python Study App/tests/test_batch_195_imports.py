import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_195a import BATCH as A
from code_practice.import_batch_195b import BATCH as B
from code_practice.import_batch_195c import BATCH as C
from code_practice.import_batch_195d import BATCH as D
ROOT=Path(__file__).resolve().parents[1];SPECS={**A,**B,**C,**D};IDS=tuple(i for i in SPECS if i!=3740)
def test_batch_195_verified():
    catalog=get_catalog()
    for source_id in IDS:
        problem=catalog[f'leetcode-{source_id}'];report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(t.visible for t in problem.tests)>=2 and sum(not t.visible for t in problem.tests)>=12
        assert len(problem.hints)==4 and report['valid'] and report['oracle_inputs']==500
        assert all(c['failed_cases'] for c in report['wrong_solutions'])
def test_batch_195_inputs_are_distinct():
    for spec in SPECS.values():
        values=[a for a,_ in spec['examples']]+spec['boundaries'];encoded=[json.dumps(a,sort_keys=True) for a in values]
        assert len(encoded)==len(set(encoded))
def test_repaired_candidate_is_verified():
    assert 'leetcode-3740' in get_catalog()
    report=json.loads((ROOT/'catalog_import/reports/leetcode-3740.json').read_text())
    assert report['valid'] and report['oracle_inputs']==500
    assert all(control['failed_cases'] for control in report['wrong_solutions'])
