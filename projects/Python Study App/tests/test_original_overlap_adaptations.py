from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from code_practice import package_catalog
from code_practice.catalog_artifacts import write_json_atomic
from code_practice import reconcile_original_overlaps as originals
from code_practice.reconcile_overlaps import restore_import_overlaps

ROOT=Path(__file__).resolve().parent.parent


def snapshot(tmp_path):
    ledger=json.loads((ROOT/'catalog_import/ledger.json').read_text())
    ledger['records']=[r for r in ledger['records'] if r['source_id'] in originals.DECISIONS]
    write_json_atomic(tmp_path/'catalog_import/ledger.json',ledger)
    for record in ledger['records']:
        destination=tmp_path/record['overlap_report']
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/record['overlap_report'],destination)
    return ledger['records']


@pytest.mark.parametrize('source_id',originals.DECISIONS)
def test_original_adaptations_preserve_sample_oracle_and_full_domain(source_id):
    sources={s['source_id']:s for s in map(json.loads,(ROOT/'catalog_import/sources.jsonl').read_text().splitlines())}
    payload=originals.target_payload(source_id)
    evidence=originals.check_original(source_id,payload,sources[source_id])
    assert evidence['oracle_inputs']==500 and evidence['workbook_sample_checked']
    assert evidence['deterministic_inputs']>=12
    records={r['source_id']:r for r in json.loads((ROOT/'catalog_import/ledger.json').read_text())['records']}
    assert originals.validate_original_overlap(records[source_id])['valid']
    wrongs=(
        ['def total_covered_length(intervals):\n    return sum(b-a for a,b in intervals)',
         'def total_covered_length(intervals):\n    return sum(max(0,b-a-1) for a,b in intervals)']
        if source_id==495 else
        ['def recursive_step_combinations(n):\n    return 1',
         'def recursive_step_combinations(n):\n    return n'] if source_id==509 else
        ['def longest_target_sum_subarray(nums,target):\n    return len(nums) if sum(nums)==target else 0',
         'def longest_target_sum_subarray(nums,target):\n    return 2*min(nums.count(-1),nums.count(1))'] if source_id==525 else
        ['def next_greater_values(nums):\n    return [-1]*len(nums)',
         'def next_greater_values(nums):\n    return [min((v for v in nums[i+1:] if v>x),default=-1) for i,x in enumerate(nums)]']
    )
    for wrong in wrongs:
        with pytest.raises(ValueError,match='disagrees'):
            originals.check_original(source_id,{**payload,'reference_solution':wrong},sources[source_id])


@pytest.mark.parametrize('field',['target_content_sha256','source_hash','judge_contract_sha256','implementation_sha256','oracle_inputs','valid'])
def test_original_overlap_stale_proofs_block_packaging(tmp_path,monkeypatch,field):
    records=snapshot(tmp_path)
    record=records[0]
    report=json.loads((tmp_path/record['overlap_report']).read_text())
    report[field]=0 if field=='oracle_inputs' else False if field=='valid' else 'changed'
    write_json_atomic(tmp_path/record['overlap_report'],report)
    with pytest.raises(ValueError,match='original overlap evidence'):
        originals.validate_original_overlap(record,tmp_path)
    monkeypatch.setattr(package_catalog,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='original overlap evidence'):
        package_catalog.package(tmp_path/'published')
    assert not (tmp_path/'published/manifest.json').exists()


def test_original_target_change_invalidates_proof(tmp_path,monkeypatch):
    record=snapshot(tmp_path)[0]
    payload=deepcopy(originals.target_payload(record['source_id']))
    payload['reference_solution']+='\n# changed contract implementation\n'
    monkeypatch.setattr(originals,'target_payload',lambda _:payload)
    with pytest.raises(ValueError,match='original overlap evidence'):
        originals.validate_original_overlap(record,tmp_path)


def test_reextraction_restores_only_current_original_proofs(tmp_path):
    records=snapshot(tmp_path)
    previous={r['source_id']:deepcopy(r) for r in records}
    fresh=[dict(r,status='pending',existing_id=None,overlap_report=None) for r in records]
    # Follow the actual extraction sequence, including imported-target restoration.
    restore_import_overlaps(fresh,previous,tmp_path)
    originals.restore_original_overlaps(fresh,previous,tmp_path)
    assert fresh==records
    report=json.loads((tmp_path/records[0]['overlap_report']).read_text())
    report['valid']=False
    write_json_atomic(tmp_path/records[0]['overlap_report'],report)
    originals.restore_original_overlaps(fresh,previous,tmp_path)
    assert fresh[0]['status']=='pending' and fresh[0]['existing_id'] is None


def test_packaged_original_mappings_do_not_duplicate_library_ids(tmp_path,monkeypatch):
    snapshot(tmp_path)
    monkeypatch.setattr(package_catalog,'ROOT',tmp_path)
    result=package_catalog.package(tmp_path/'published')
    assert result=={'count':101,'imported':0}
    manifest=json.loads((tmp_path/'published/manifest.json').read_text())
    ids={p['id'] for p in manifest['entries']}
    assert {'total-covered-length','next-greater-values'}<=ids
    assert not {'leetcode-495','leetcode-496','leetcode-509','leetcode-525'}&ids


def test_fibonacci_adaptation_exhausts_domain_without_changing_original():
    payload=originals.target_payload(509)
    solve=originals.adapted_function(509,payload)
    a,b=0,1
    for n in range(31):
        assert solve(n)==a==originals.fibonacci_oracle([n])
        a,b=b,a+b
    assert payload['id']=='recursive-step-combinations' and payload['version']==1
    assert solve(0)==0 and solve(30)==832040
    sources={s['source_id']:s for s in map(json.loads,(ROOT/'catalog_import/sources.jsonl').read_text().splitlines())}
    report=originals.check_original(509,payload,sources[509])
    assert report['deterministic_inputs']==report['exhaustive_domain_inputs']==31


def test_fibonacci_incomplete_domain_proof_is_rejected(tmp_path):
    record=next(r for r in snapshot(tmp_path) if r['source_id']==509)
    path=tmp_path/record['overlap_report']
    report=json.loads(path.read_text());report['exhaustive_domain_inputs']=30
    write_json_atomic(path,report)
    with pytest.raises(ValueError,match='original overlap evidence'):
        originals.validate_original_overlap(record,tmp_path)
