import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_202a import BATCH as A
from code_practice.import_batch_202b import BATCH as B
from code_practice.import_batch_202c import BATCH as C
from code_practice.import_batch_202d import BATCH as D
from code_practice.import_batch_202e import BATCH as E

ROOT=Path(__file__).resolve().parents[1]
# Peak Index (162) remains in the resumable ledger but is quarantined until the
# judge supports its multiple-valid-answer contract.
SPECS={source_id:spec for source_id,spec in {**A,**B,**C,**D,**E}.items() if source_id != 162}
IDS=tuple(SPECS)

def test_batch_202_verified():
    catalog=get_catalog()
    for source_id in IDS:
        problem=catalog[f'leetcode-{source_id}'];report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(t.visible for t in problem.tests)>=2 and sum(not t.visible for t in problem.tests)>=12
        assert len(problem.hints)==4 and report['valid'] and report['oracle_inputs']==500
        assert len(report['wrong_solutions'])>=2 and all(case['failed_cases'] for case in report['wrong_solutions'])

def test_batch_202_inputs_are_distinct():
    for spec in SPECS.values():
        values=[args for args,_ in spec['examples']]+spec['boundaries'];encoded=[json.dumps(args,sort_keys=True) for args in values]
        assert len(encoded)==len(set(encoded))
