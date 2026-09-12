"""Shared hashes binding published import reports to the judge contract."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def content_digest(payload):
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def load_verified_import(record, root=ROOT):
    """Read approved content only when its complete validation evidence matches."""
    try:
        if record["status"] != "imported":
            raise ValueError("target is not an imported problem")
        payload = json.loads((root / "catalog_import/candidates" / f"{record['problem_id']}.json").read_text())
        report = json.loads((root / record["validation_report"]).read_text())
        if (not report["valid"] or payload["status"] != "approved"
                or report["problem_id"] != record["problem_id"] or payload["id"] != record["problem_id"]
                or report["content_sha256"] != content_digest(payload)
                or report.get("judge_contract_sha256") != judge_contract_hash()
                or report["source_hash"] != record["source_hash"]
                or report["visible_tests"] < 2 or report["hidden_tests"] < 12
                or report["reference_passed"] != len(payload["tests"])
                or len(report["wrong_solutions"]) < 2
                or not all(w["failed_cases"] for w in report["wrong_solutions"])
                or (report["oracle_inputs"] < 500 and not report.get("oracle_exception"))):
            raise ValueError("validation evidence does not match")
        return payload
    except (OSError, KeyError, ValueError, TypeError) as error:
        raise ValueError(f"{record.get('problem_id')}: missing, stale, or failing validation evidence") from error


def judge_contract_hash():
    digest = hashlib.sha256()
    for name in ("code_practice/schemas.py", "code_practice/validation.py", "frontend/public/judge-worker.js"):
        digest.update(name.encode())
        digest.update((ROOT / name).read_bytes())
    return digest.hexdigest()
