import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_170 import BATCH
ROOT=Path(__file__).resolve().parents[1]
IDS=(2659,2660,2661,2662,2670)

def test_batch_170_is_complete_and_verified():
    catalog=get_catalog()
    for source_id in IDS:
        problem=catalog[f'leetcode-{source_id}'];report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(test.visible for test in problem.tests)>=2 and sum(not test.visible for test in problem.tests)>=12
        assert len(problem.hints)==4 and report['valid'] and report['oracle_inputs']==500
        assert report['reference_passed']==len(problem.tests) and all(result['failed_cases'] for result in report['wrong_solutions'])

def test_batch_170_inputs_are_distinct():
    for source_id in IDS:
        values=[arguments for arguments,_ in BATCH[source_id]['examples']]+BATCH[source_id]['boundaries']
        encoded=[json.dumps(arguments,sort_keys=True) for arguments in values]
        assert len(encoded)==len(set(encoded))
