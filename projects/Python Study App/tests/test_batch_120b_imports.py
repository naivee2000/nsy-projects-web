import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_120b import BATCH

ROOT=Path(__file__).resolve().parents[1]
IDS=(2139,2140,2141,2143,2144)

def test_batch_120_second_slice_is_complete_and_verified():
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

def test_batch_120_second_slice_inputs_are_distinct():
    for source_id in IDS:
        spec=BATCH[source_id]
        inputs=[arguments for arguments,_ in spec['examples']]+spec['boundaries']
        encoded=[json.dumps(arguments,sort_keys=True) for arguments in inputs]
        assert len(encoded)==len(set(encoded))

def test_hard_runtime_and_balanced_range_problems_are_retained():
    catalog=get_catalog()
    assert catalog['leetcode-2141'].difficulty>=8
    assert catalog['leetcode-2143'].difficulty>=8
