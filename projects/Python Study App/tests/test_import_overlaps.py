from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from code_practice import package_catalog
from code_practice.catalog import get_catalog
from code_practice.catalog_artifacts import write_json_atomic
from code_practice.reconcile_overlaps import (
    DECISIONS, check_unique_rotations, check_distinct_subsequence, check_bulb_square_root, check_bit_flips,
    check_complement, check_player_matching, matching_deficiency_oracle, assignment_mask_oracle,
    reconcile, restore_import_overlaps, validate_import_overlap,
)

ROOT = Path(__file__).resolve().parent.parent


def snapshot(tmp_path):
    """Use a tiny isolated fixture, never the owner's live ledger or progress."""
    ledger = json.loads((ROOT / "catalog_import/ledger.json").read_text())
    targets = {decision['target_source_id'] for decision in DECISIONS.values()}
    selected = set(DECISIONS) | targets
    ledger["records"] = [row for row in ledger["records"] if row["source_id"] in selected]
    write_json_atomic(tmp_path / "catalog_import/ledger.json", ledger)
    artifacts = [f'catalog_import/{folder}/leetcode-{target}.json'
                 for target in targets for folder in ('candidates', 'reports')]
    artifacts += [f'catalog_import/overlap_reports/leetcode-{source}.json' for source in DECISIONS]
    for relative in artifacts:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    sources = [json.loads(line) for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines()
               if json.loads(line)["source_id"] in selected]
    (tmp_path / "catalog_import/sources.jsonl").write_text("".join(json.dumps(row) + "\n" for row in sources))
    return ledger, {row["source_id"]: row for row in ledger["records"]}, {row["source_id"]: row for row in sources}


def test_import_overlap_checks_unique_domain_and_logarithmic_read_requirement(tmp_path):
    _, records, sources = snapshot(tmp_path)
    payload = json.loads((tmp_path / "catalog_import/candidates/leetcode-154.json").read_text())
    report = check_unique_rotations(payload, sources[153])
    assert report["oracle_inputs"] == 500 and report["deterministic_inputs"] == 3
    assert report["largest_input"] == 5000 and report["largest_element_reads"] <= 53
    assert report["workbook_sample_checked"]
    linear = {**payload, "reference_solution": "def rotated_minimum(nums):\n    return min(nums)"}
    with pytest.raises(AssertionError, match="logarithmic"):
        check_unique_rotations(linear, sources[153])
    wrong = {**payload, "reference_solution": "def rotated_minimum(nums):\n    return min(nums[0], nums[-1])"}
    with pytest.raises(ValueError, match="minimum oracle"):
        check_unique_rotations(wrong, sources[153])


def test_reconciliation_is_repeatable_and_does_not_create_duplicate_problem(tmp_path, monkeypatch):
    _, records, _ = snapshot(tmp_path)
    first = reconcile(tmp_path)
    targets = {decision['target_source_id'] for decision in DECISIONS.values()}
    assert first == {"overlap": len(DECISIONS), "imported": len(targets)}
    before = (tmp_path / "catalog_import/ledger.json").read_bytes()
    assert reconcile(tmp_path) == first
    assert (tmp_path / "catalog_import/ledger.json").read_bytes() == before
    monkeypatch.setattr(package_catalog, "ROOT", tmp_path)
    packaged = package_catalog.package(tmp_path / "published")
    assert packaged["count"] == 101 + len(targets) and packaged["imported"] == len(targets)
    assert not (tmp_path / "published/problems/leetcode-153.json").exists()
    assert not (tmp_path / "published/problems/leetcode-1081.json").exists()
    assert not (tmp_path / "published/problems/leetcode-319.json").exists()
    assert not (tmp_path / "published/problems/leetcode-2220.json").exists()
    assert "leetcode-1081" not in get_catalog() and "leetcode-316" in get_catalog()
    assert "leetcode-153" not in get_catalog() and "leetcode-154" in get_catalog()
    assert "leetcode-2220" not in get_catalog() and "leetcode-461" in get_catalog()


def test_bit_flip_overlap_covers_source_boundaries_and_rejects_lost_positions(tmp_path):
    _, records, sources = snapshot(tmp_path)
    payload = json.loads((tmp_path/'catalog_import/candidates/leetcode-461.json').read_text())
    proof = check_bit_flips(payload,sources[2220])
    assert proof['oracle_inputs']==500 and proof['largest_input']==10**9
    assert proof['deterministic_inputs']==64
    assert validate_import_overlap(records[2220],records,tmp_path)['valid']
    for body in ('return abs(x-y)', 'return (x|y).bit_count()', 'return abs(x.bit_count()-y.bit_count())'):
        with pytest.raises(ValueError):
            check_bit_flips({**payload,'reference_solution':f'def hamming_distance(x,y):\n    {body}'},sources[2220])
    records[461]['status']='quarantined'
    with pytest.raises(ValueError,match='stale'):
        validate_import_overlap(records[2220],records,tmp_path)


@pytest.mark.parametrize("change", ["source", "target_source", "target_content", "proof", "target_status"])
def test_changed_overlap_dependencies_block_publication(tmp_path, monkeypatch, change):
    ledger, records, _ = snapshot(tmp_path)
    if change == "source":
        records[153]["source_hash"] = "changed"
    elif change == "target_source":
        records[154]["source_hash"] = "changed"
    elif change == "target_content":
        path = tmp_path / "catalog_import/candidates/leetcode-154.json"
        candidate = json.loads(path.read_text())
        candidate["reference_solution"] = "def rotated_minimum(nums):\n    return -1"
        write_json_atomic(path, candidate)
    elif change == "proof":
        path = tmp_path / "catalog_import/overlap_reports/leetcode-153.json"
        proof = json.loads(path.read_text())
        proof["oracle_inputs"] = 0
        write_json_atomic(path, proof)
    else:
        records[154]["status"] = "quarantined"
    write_json_atomic(tmp_path / "catalog_import/ledger.json", ledger)
    with pytest.raises(ValueError):
        validate_import_overlap(records[153], records, tmp_path)
    monkeypatch.setattr(package_catalog, "ROOT", tmp_path)
    with pytest.raises(ValueError):
        package_catalog.package(tmp_path / "published")
    assert not (tmp_path / "published/manifest.json").exists()


def test_reextraction_preserves_only_unchanged_proven_overlap(tmp_path):
    _, records, _ = snapshot(tmp_path)
    old = deepcopy(records)
    records[153] = {**records[153], "status": "pending", "existing_id": None}
    records[153].pop("overlap_report")
    restore_import_overlaps(list(records.values()), old, tmp_path)
    assert records[153] == old[153]
    records[154]["status"] = "quarantined"
    restore_import_overlaps(list(records.values()), old, tmp_path)
    assert records[153]["status"] == "pending" and records[153]["existing_id"] is None
    records[154] = deepcopy(old[154])
    records[153]["source_hash"] = "updated-source"
    restore_import_overlaps(list(records.values()), old, tmp_path)
    assert records[153]["status"] == "pending"


def test_invalid_overlap_is_quarantined_and_existing_import_ids_are_never_replaced(tmp_path):
    ledger, records, _ = snapshot(tmp_path)
    records[154]["status"] = "quarantined"
    write_json_atomic(tmp_path / "catalog_import/ledger.json", ledger)
    targets = {decision['target_source_id'] for decision in DECISIONS.values()}
    assert reconcile(tmp_path) == {"quarantined": 2, "imported": len(targets)-1, "overlap": len(DECISIONS)-1}
    changed = json.loads((tmp_path / "catalog_import/ledger.json").read_text())
    assert next(row for row in changed["records"] if row["source_id"] == 153)["existing_id"] is None
    records[153]["status"] = "imported"
    write_json_atomic(tmp_path / "catalog_import/ledger.json", ledger)
    before = (tmp_path / "catalog_import/ledger.json").read_bytes()
    with pytest.raises(ValueError, match="progress ID"):
        reconcile(tmp_path)
    assert (tmp_path / "catalog_import/ledger.json").read_bytes() == before


def test_distinct_subsequence_overlap_verifies_order_and_every_required_letter(tmp_path):
    _, records, sources = snapshot(tmp_path)
    payload = json.loads((tmp_path / "catalog_import/candidates/leetcode-316.json").read_text())
    report = check_distinct_subsequence(payload, sources[1081])
    assert report["oracle_inputs"] == 500 and report["largest_input"] == 1000
    assert validate_import_overlap(records[1081], records, tmp_path)["valid"]
    for wrong in ("return ''.join(sorted(set(s)))", "return ''.join(dict.fromkeys(s))", "return min(s)"):
        with pytest.raises(ValueError):
            check_distinct_subsequence({**payload, "reference_solution": f"def remove_duplicate_letters(s):\n    {wrong}"}, sources[1081])
    records[316]["status"] = "quarantined"
    with pytest.raises(ValueError, match="stale"):
        validate_import_overlap(records[1081], records, tmp_path)


def test_bulb_overlap_is_verified_by_actual_toggles_and_full_domain_boundaries(tmp_path):
    _, records, sources = snapshot(tmp_path)
    payload = json.loads((tmp_path / 'catalog_import/candidates/leetcode-69.json').read_text())
    proof = check_bulb_square_root(payload, sources[319])
    assert proof['literal_simulation_inputs'] == 500
    assert proof['full_domain_square_enumeration_inputs'] == 500
    assert proof['largest_input'] == 10**9
    assert validate_import_overlap(records[319], records, tmp_path)['valid']
    for wrong in ('return n%2', 'return n//2', 'return int(n**0.5)+1'):
        with pytest.raises(ValueError):
            check_bulb_square_root({**payload, 'reference_solution': f'def integer_sqrt(n):\n    {wrong}'}, sources[319])
    records[69]['status'] = 'quarantined'
    with pytest.raises(ValueError, match='stale'):
        validate_import_overlap(records[319], records, tmp_path)


def test_complement_overlap_requires_zero_and_source_boundaries(tmp_path):
    _,records,sources = snapshot(tmp_path)
    payload = json.loads((tmp_path/'catalog_import/candidates/leetcode-476.json').read_text())
    proof = check_complement(payload,sources[1009])
    assert proof['oracle_inputs'] == 500 and proof['zero_checked']
    assert proof['largest_input'] == 10**9-1 and proof['deterministic_inputs'] >= 80
    assert validate_import_overlap(records[1009],records,tmp_path)['valid']
    with pytest.raises(ValueError,match='zero-domain'):
        check_complement({**payload,'version':1},sources[1009])
    # The previously correct positive-only implementation must fail the extension.
    wrong = 'def number_complement(num):\n    return ((1<<num.bit_length())-1)^num'
    with pytest.raises(ValueError,match='binary oracle'):
        check_complement({**payload,'reference_solution':wrong},sources[1009])


def test_player_matching_overlap_checks_new_scale_and_exact_threshold(tmp_path):
    _,records,sources = snapshot(tmp_path)
    payload = json.loads((tmp_path/'catalog_import/candidates/leetcode-455.json').read_text())
    proof = check_player_matching(payload,sources[2410])
    assert proof['oracle_inputs'] == 500 and proof['largest_input'] == 100000
    assert proof['deterministic_inputs'] == 8
    assert validate_import_overlap(records[2410],records,tmp_path)['valid']
    with pytest.raises(ValueError,match='100,000-item'):
        check_player_matching({**payload,'version':1},sources[2410])
    for wrong in (payload['reference_solution'].replace('return child','return min(child,30000)'),
                  payload['reference_solution'].replace('size>=needs[child]','size>needs[child]')):
        assert wrong != payload['reference_solution']
        with pytest.raises(ValueError):
            check_player_matching({**payload,'reference_solution':wrong},sources[2410])


def test_nested_neighborhood_deficiency_matches_exhaustive_assignments():
    from itertools import combinations_with_replacement
    lists = [list(a) for n in range(1,5) for a in combinations_with_replacement((1,2,3),n)]
    for players in lists:
        for trainers in lists:
            assert matching_deficiency_oracle(players,trainers) == assignment_mask_oracle(players,trainers)


@pytest.mark.parametrize('pid', [455,476])
def test_domain_upgrade_preserves_version_one_passed_status_and_draft(tmp_path,monkeypatch,pid):
    from fastapi.testclient import TestClient
    from code_practice import catalog,database
    from code_practice.app import app
    problem_id = f'leetcode-{pid}'
    with database.db_session() as connection:
        connection.execute('INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,tests_passed,tests_total,elapsed_study_seconds,hint_level,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',
            (problem_id,1,'old accepted source','accepted',1,12,12,30,0,'2026-01-01T00:00:00+00:00'))
    database.save_draft(problem_id,'my saved edits')
    before = database.DB_PATH.read_bytes()
    package_catalog.package(tmp_path/'upgraded-catalog')
    assert database.DB_PATH.read_bytes() == before
    monkeypatch.setattr(catalog,'CATALOG_DIR',tmp_path/'upgraded-catalog')
    catalog.refresh_catalog()
    for _ in range(2):
        with TestClient(app) as client:
            detail = client.get(f'/api/problems/{problem_id}').json()
            assert detail['version'] == 2 and detail['savedDraft'] == 'my saved edits'
            assert problem_id in {p['id'] for p in client.get('/api/problems?completion=passed').json()['items']}
            assert problem_id not in {p['id'] for p in client.get('/api/dashboard').json()['recommendations']}
            assert client.get('/api/problems/leetcode-1009').status_code == 404
            assert client.get('/api/problems/leetcode-2410').status_code == 404
        catalog.refresh_catalog()
