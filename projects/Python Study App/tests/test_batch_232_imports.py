import json
from pathlib import Path
from code_practice.catalog import get_catalog
from code_practice.import_batch_232a import BATCH as BATCH_A
from code_practice.import_batch_232b import BATCH as BATCH_B

BATCH={**BATCH_A,**BATCH_B}

ROOT=Path(__file__).resolve().parents[1]

def test_batch_232_verified():
    catalog=get_catalog();records={r['source_id']:r for r in json.loads((ROOT/'catalog_import'/'ledger.json').read_text())['records']}
    for source_id,spec in BATCH.items():
        if records[source_id]['status']!='imported':continue
        problem=catalog[f'leetcode-{source_id}'];report=json.loads((ROOT/'catalog_import'/'reports'/f'leetcode-{source_id}.json').read_text())
        assert problem.signature.name==spec['name']
        assert sum(test.visible for test in problem.tests)>=2 and sum(not test.visible for test in problem.tests)>=12
        assert len(problem.hints)==4 and report['valid'] and report['reference_passed']==len(problem.tests)
        assert report['oracle_inputs']>=500 and len(report['wrong_solutions'])>=2
        assert all(item['failed_cases'] for item in report['wrong_solutions'])

def test_batch_232_inputs_are_distinct():
    for spec in BATCH.values():
        encoded=[json.dumps(value,sort_keys=True) for value in [args for args,_ in spec['examples']]+spec['boundaries']]
        assert len(encoded)==len(set(encoded))
