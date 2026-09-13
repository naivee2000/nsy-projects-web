"""Build portable catalog artifacts offline without opening the progress database."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .schemas import ProblemDefinition
from .catalog_evidence import content_digest, load_verified_import

ROOT = Path(__file__).resolve().parent.parent


def package(output: Path) -> dict:
    from .content import PROBLEMS
    problems = [(p, None) for p in PROBLEMS]
    ledger_path = ROOT / "catalog_import/ledger.json"
    if ledger_path.exists():
        ledger = json.loads(ledger_path.read_text())
        for record in ledger["records"]:
            if record["status"] != "imported":
                continue
            payload = load_verified_import(record, ROOT)
            problems.append((ProblemDefinition.model_validate(payload), record["source_id"]))
        from .reconcile_overlaps import validate_import_overlap
        from .reconcile_original_overlaps import DECISIONS as ORIGINAL_OVERLAPS, validate_original_overlap
        records = {record["source_id"]: record for record in ledger["records"]}
        published = {problem.id for problem, _ in problems}
        for record in ledger["records"]:
            if record["status"] == "overlap":
                if record["existing_id"] not in published:
                    raise ValueError("Overlap points to an unpublished problem")
                if record["existing_id"].startswith("leetcode-"):
                    validate_import_overlap(record, records, ROOT)
                elif record['source_id'] in ORIGINAL_OVERLAPS:
                    validate_original_overlap(record, ROOT)
    if len({p.id for p, _ in problems}) != len(problems):
        raise ValueError("Catalog IDs must be unique; existing progress IDs cannot be overwritten")
    entries = []
    (output / "problems").mkdir(parents=True, exist_ok=True)
    for problem, source_id in problems:
        payload = problem.model_dump(mode="json")
        path = f"problems/{problem.id}.json"
        (output / path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        entries.append(dict(id=problem.id, version=problem.version, status=problem.status,
            title=problem.title, summary=problem.summary, topics=problem.topics,
            prerequisites=problem.prerequisites, difficulty=problem.difficulty,
            estimated_minutes=problem.estimated_minutes, path=path,
            content_sha256=content_digest(payload), source_id=source_id))
    manifest = {"schema_version": 1, "count": len(entries), "entries": entries}
    temporary = output / "manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(output / "manifest.json")
    return {"count": len(entries), "imported": sum(s is not None for _, s in problems)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "catalog_data")
    args = parser.parse_args()
    print(json.dumps(package(args.output)))


if __name__ == "__main__":
    main()
