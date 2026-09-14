import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_116 import BATCH
from code_practice.import_batch_116b import BATCH as BATCH_B
from code_practice.import_batch_116c import BATCH as BATCH_C

ROOT=Path(__file__).resolve().parents[1]
IDS=(2036,2038,2039,2040,2042)
IDS+=(2044,2045,2046,2047,2048)
IDS+=(2049,2050,2052,2053,2054)
SPECS={**BATCH,**BATCH_B,**BATCH_C}

def test_batch_116_first_slice_is_complete_and_verified():
 catalog=get_catalog()
 for source_id in IDS:
  problem=catalog[f'leetcode-{source_id}']
  report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
  assert sum(case.visible for case in problem.tests)>=2
  assert sum(not case.visible for case in problem.tests)>=12
  assert len(problem.hints)==4
  assert report['valid'] and report['reference_passed']==len(problem.tests)
  assert report['oracle_inputs']==500
  assert all(wrong['failed_cases'] for wrong in report['wrong_solutions'])

def test_batch_116_first_slice_inputs_are_distinct():
 for source_id in IDS:
  spec=SPECS[source_id]
  values=[a for a,_ in spec['examples']]+spec['boundaries']
  encoded=[json.dumps(a,sort_keys=True) for a in values]
  assert len(encoded)==len(set(encoded))

def test_hard_product_problem_is_retained():
 assert get_catalog()['leetcode-2040'].difficulty>=8
