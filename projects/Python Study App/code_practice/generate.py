from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .catalog import get_catalog
from .database import initialize_database, list_variants, save_variant, update_variant_status
from .schemas import ProblemDefinition
from .validation import content_fingerprint, validate_problem


PROMPT_VERSION = "variant-v1"


def _json_from_text(text: str) -> Any:
    start = min((index for index in (text.find("["), text.find("{")) if index >= 0), default=-1)
    if start < 0:
        raise ValueError("Codex did not return JSON")
    closing = "]" if text[start] == "[" else "}"
    end = text.rfind(closing)
    if end < start:
        raise ValueError("Codex returned incomplete JSON")
    return json.loads(text[start:end + 1])


def generate_with_codex(seed: ProblemDefinition, count: int) -> list[dict[str, Any]]:
    schema = ProblemDefinition.model_json_schema()
    seed_payload = seed.model_dump(mode="json")
    prompt = f"""
Create {count} original interview-practice variants from the seed problem below.
Return only a JSON array. Every item must satisfy the supplied JSON schema.
Each variant must change at least two of: data_model, operation, output_shape,
constraints, algorithm_combination. Keep the learning objective recognizable,
but do not merely rename the story or change numbers. Include exactly four hints,
at least two visible tests, at least twelve hidden tests, a reference solution,
a brute-force solution, two known-wrong solutions, and expected outputs.
Set status to draft, seed_problem_id to {seed.id!r}, prompt_version to {PROMPT_VERSION!r},
and list the selected dimensions in variation_dimensions.

JSON schema:
{json.dumps(schema)}

Seed:
{json.dumps(seed_payload)}
""".strip()
    try:
        completed = subprocess.run(
            ["codex", "exec", prompt],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Codex CLI is not installed; the study app still works without generation") from exc
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Codex generation failed")
    payload = _json_from_text(completed.stdout)
    return payload if isinstance(payload, list) else [payload]


def import_drafts(items: list[dict[str, Any]], seed_id: str | None = None) -> int:
    imported = 0
    for item in items:
        item["status"] = "draft"
        item["prompt_version"] = item.get("prompt_version") or PROMPT_VERSION
        item["seed_problem_id"] = item.get("seed_problem_id") or seed_id
        try:
            problem = ProblemDefinition.model_validate(item)
        except ValidationError as exc:
            print(f"Rejected invalid draft {item.get('id', '<unknown>')}: {exc}", file=sys.stderr)
            continue
        save_variant(problem.model_dump(mode="json"), problem.seed_problem_id or seed_id or "unknown")
        imported += 1
    return imported


def validate_variant(problem_id: str) -> dict[str, Any]:
    catalog = get_catalog()
    fingerprints = {content_fingerprint(problem) for problem in catalog.values()}
    row = next((item for item in list_variants() if item["problem_id"] == problem_id), None)
    if not row:
        raise ValueError(f"Unknown variant: {problem_id}")
    problem = ProblemDefinition.model_validate(row["problem"])
    report = validate_problem(problem, fingerprints)
    update_variant_status(problem_id, "validating" if report["valid"] else "rejected", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and approve Code Practice Lab variants")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create", help="Generate drafts from an approved seed")
    create.add_argument("--seed", required=True)
    create.add_argument("--count", type=int, default=3, choices=range(1, 6))
    imported = commands.add_parser("import", help="Import draft JSON produced elsewhere")
    imported.add_argument("--file", required=True)
    imported.add_argument("--seed")
    validate = commands.add_parser("validate", help="Validate one stored draft")
    validate.add_argument("--id", required=True)
    approve = commands.add_parser("approve", help="Approve a successfully validated draft")
    approve.add_argument("--id", required=True)
    reject = commands.add_parser("reject", help="Reject a stored draft")
    reject.add_argument("--id", required=True)
    commands.add_parser("list", help="List generated variants")
    args = parser.parse_args()
    initialize_database()

    if args.command == "create":
        seed = get_catalog().get(args.seed)
        if not seed:
            parser.error(f"Unknown seed problem: {args.seed}")
        count = import_drafts(generate_with_codex(seed, args.count), seed.id)
        print(f"Imported {count} draft(s)")
    elif args.command == "import":
        payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
        count = import_drafts(payload if isinstance(payload, list) else [payload], args.seed)
        print(f"Imported {count} draft(s)")
    elif args.command == "validate":
        report = validate_variant(args.id)
        print(json.dumps(report, indent=2))
        return 0 if report["valid"] else 1
    elif args.command == "approve":
        row = next((item for item in list_variants() if item["problem_id"] == args.id), None)
        if not row or row["status"] != "validating" or not row["validation"].get("valid"):
            parser.error("Variant must pass validation before approval")
        update_variant_status(args.id, "approved", row["validation"])
        print(f"Approved {args.id}; restart the local app to refresh the catalog")
    elif args.command == "reject":
        if not update_variant_status(args.id, "rejected"):
            parser.error(f"Unknown variant: {args.id}")
        print(f"Rejected {args.id}")
    else:
        for row in list_variants():
            print(f"{row['problem_id']}\t{row['status']}\tseed={row['seed_problem_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
