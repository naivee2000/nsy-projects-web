from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from code_practice import package_catalog
from code_practice.catalog import get_catalog
from code_practice.catalog_artifacts import write_json_atomic
from code_practice.reconcile_overlaps import (
    check_unique_rotations, reconcile, restore_import_overlaps, validate_import_overlap,
)

ROOT = Path(__file__).resolve().parent.parent


def snapshot(tmp_path):
    """Use a tiny isolated fixture, never the owner's live ledger or progress."""
    ledger = json.loads((ROOT / "catalog_import/ledger.json").read_text())
    ledger["records"] = [row for row in ledger["records"] if row["source_id"] in (153, 154)]
    write_json_atomic(tmp_path / "catalog_import/ledger.json", ledger)
    for relative in ("catalog_import/candidates/leetcode-154.json", "catalog_import/reports/leetcode-154.json",
                     "catalog_import/overlap_reports/leetcode-153.json"):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    sources = [json.loads(line) for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines()
               if json.loads(line)["source_id"] in (153, 154)]
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
    assert first == {"overlap": 1, "imported": 1}
    before = (tmp_path / "catalog_import/ledger.json").read_bytes()
    assert reconcile(tmp_path) == first
    assert (tmp_path / "catalog_import/ledger.json").read_bytes() == before
    monkeypatch.setattr(package_catalog, "ROOT", tmp_path)
    packaged = package_catalog.package(tmp_path / "published")
    assert packaged["count"] == 102 and packaged["imported"] == 1
    assert not (tmp_path / "published/problems/leetcode-153.json").exists()
    assert "leetcode-153" not in get_catalog() and "leetcode-154" in get_catalog()


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
    assert reconcile(tmp_path) == {"quarantined": 2}
    changed = json.loads((tmp_path / "catalog_import/ledger.json").read_text())
    assert next(row for row in changed["records"] if row["source_id"] == 153)["existing_id"] is None
    records[153]["status"] = "imported"
    write_json_atomic(tmp_path / "catalog_import/ledger.json", ledger)
    before = (tmp_path / "catalog_import/ledger.json").read_bytes()
    with pytest.raises(ValueError, match="progress ID"):
        reconcile(tmp_path)
    assert (tmp_path / "catalog_import/ledger.json").read_bytes() == before
