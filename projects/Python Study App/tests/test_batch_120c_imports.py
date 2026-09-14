import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_120c import BATCH

ROOT=Path(__file__).resolve().parents[1]
IDS=(2145,2146,2147,2148,2149)

def test_batch_120_third_slice_is_complete_and_verified():
    catalog=get_catalog()
    for source_id in IDS:
        problem=catalog[f'leetcode-{source_id}']
        report=json.loads((ROOT/'catalog_import/reports'/f'leetcode-{source_id}.json').read_text())
        assert sum(case.visible for case in problem.tests)>=2
        assert sum(not case.visible for case in problem.tests)>=12
        assert len(problem.hints)==4
        assert report['valid'] and report['reference_passed']==len(problem.tests)
        assert report['oracle_inputs']==500
        assert all(item['failed_cases'] for item in report['wrong_solutions'])

def test_batch_120_third_slice_inputs_are_distinct():
    for source_id in IDS:
        spec=BATCH[source_id]
        inputs=[arguments for arguments,_ in spec['examples']]+spec['boundaries']
        encoded=[json.dumps(arguments,sort_keys=True) for arguments in inputs]
        assert len(encoded)==len(set(encoded))

def test_hard_corridor_problem_is_retained():
    assert get_catalog()['leetcode-2147'].difficulty>=8
