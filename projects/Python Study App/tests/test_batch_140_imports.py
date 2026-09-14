import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_140 import BATCH
ROOT=Path(__file__).resolve().parents[1];IDS=(2374,2375,2380,2381,2391)
def test_batch_140_is_complete_and_verified():
    catalog=get_catalog()
    for source_id in IDS:
        p=catalog[f'leetcode-{source_id}'];r=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(t.visible for t in p.tests)>=2 and sum(not t.visible for t in p.tests)>=12
        assert len(p.hints)==4 and r['valid'] and r['oracle_inputs']==500
        assert r['reference_passed']==len(p.tests) and all(w['failed_cases'] for w in r['wrong_solutions'])
def test_batch_140_inputs_are_distinct():
    for source_id in IDS:
        values=[a for a,_ in BATCH[source_id]['examples']]+BATCH[source_id]['boundaries'];encoded=[json.dumps(a,sort_keys=True) for a in values]
        assert len(encoded)==len(set(encoded))
