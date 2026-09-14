import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_182 import BATCH
ROOT=Path(__file__).resolve().parents[1];IDS=(2763,2769,2770,2771,2772)
def test_batch_182_verified():
 c=get_catalog()
 for i in IDS:
  p=c[f'leetcode-{i}'];r=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{i}.json').read_text());assert sum(t.visible for t in p.tests)>=2 and sum(not t.visible for t in p.tests)>=12 and len(p.hints)==4 and r['valid'] and r['oracle_inputs']==500 and all(x['failed_cases'] for x in r['wrong_solutions'])
def test_batch_182_distinct():
 for i in IDS:
  v=[a for a,_ in BATCH[i]['examples']]+BATCH[i]['boundaries'];e=[json.dumps(a,sort_keys=True) for a in v];assert len(e)==len(set(e))
