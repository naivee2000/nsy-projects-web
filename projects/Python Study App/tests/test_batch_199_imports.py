import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_199a import BATCH as A
from code_practice.import_batch_199b import BATCH as B
from code_practice.import_batch_199c import BATCH as C
from code_practice.import_batch_199d import BATCH as D
from code_practice.import_batch_199e import BATCH as E

ROOT=Path(__file__).resolve().parents[1];ALL={**A,**B,**C,**D,**E};QUARANTINED={1227};SPECS={k:v for k,v in ALL.items() if k not in QUARANTINED};IDS=tuple(SPECS)

def test_batch_199_verified():
    catalog=get_catalog()
    for source_id in IDS:
        problem=catalog[f'leetcode-{source_id}'];report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(t.visible for t in problem.tests)>=2 and sum(not t.visible for t in problem.tests)>=12
        assert len(problem.hints)==4 and report['valid'] and report['oracle_inputs']==500
        assert len(report['wrong_solutions'])>=2 and all(c['failed_cases'] for c in report['wrong_solutions'])

def test_batch_199_inputs_are_distinct():
    for spec in SPECS.values():
        values=[a for a,_ in spec['examples']]+spec['boundaries'];encoded=[json.dumps(a,sort_keys=True) for a in values]
        assert len(encoded)==len(set(encoded))

def test_repaired_candidate_is_verified():
    records={r['source_id']:r for r in json.loads((ROOT/'catalog_import/ledger.json').read_text())['records']}
    assert records[1227]['status']=='imported'
    report=json.loads((ROOT/'catalog_import/reports/leetcode-1227.json').read_text())
    assert report['valid'] and report['oracle_inputs']==500
    assert all(control['failed_cases'] for control in report['wrong_solutions'])
