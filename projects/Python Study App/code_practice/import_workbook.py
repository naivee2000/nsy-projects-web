"""Read-only workbook extraction and resumable source inventory; never approves content.

Run with explicit --workbook, --source-metadata and --source-repository paths.
Only packaged relative paths and provenance identifiers are retained in outputs.
No source code from the workbook or source repository is executed by this command.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
from html import unescape
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from .import_decisions import OVERLAPS
from .catalog_artifacts import write_json_atomic, write_text_atomic

APP_ROOT = Path(__file__).resolve().parent.parent
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def workbook_rows(path: Path) -> list[dict]:
    """Extract labeled cells from Problems without Excel or third-party readers."""
    with ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            for item in ET.fromstring(archive.read("xl/sharedStrings.xml")):
                shared.append("".join(item.itertext()))
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheet = next(s for s in workbook.find("x:sheets", NS) if s.attrib["name"] == "Problems")
        rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = next(r.attrib["Target"] for r in relationships if r.attrib["Id"] == rel_id)
        target = target.lstrip("/") if target.startswith("/") else "xl/" + target
        root = ET.fromstring(archive.read(target))
        data = []
        header_seen = False
        for row in root.findall("x:sheetData/x:row", NS):
            values = {}
            for cell in row:
                column = re.match(r"[A-Z]+", cell.attrib["r"])[0]
                kind = cell.get("t")
                raw = cell.findtext("x:v", default="", namespaces=NS)
                values[column] = (shared[int(raw)] if kind == "s" else
                                    "".join(cell.find("x:is", NS).itertext()) if kind == "inlineStr" else raw)
            if not header_seen:
                if values.get("A") == "Problem Name":
                    if [values.get(c) for c in "ABCD"] != ["Problem Name", "Difficulty", "Detailed Original Summary", "Concise Example"]:
                        raise ValueError("Unexpected workbook columns")
                    header_seen = True
                continue
            if not any(values.values()):
                continue
            data.append(dict(workbook_row=int(row.attrib["r"]), title=values.get("A", ""),
                             difficulty=values.get("B", ""), statement=values.get("C", ""),
                             sample=values.get("D", "")))
    if not header_seen or not data or len({r["title"] for r in data}) != len(data):
        raise ValueError("Missing header/records or duplicate workbook names")
    if any(not r["title"] or not r["statement"] or r["difficulty"] not in {"Easy", "Medium", "Hard"} for r in data):
        raise ValueError("Missing required workbook content")
    return data


def fingerprint(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def plain_html(fragment: str) -> str:
    fragment = re.sub(r"<sup>(.*?)</sup>", r"^\1", fragment, flags=re.S)
    fragment = re.sub(r"</(?:p|li|pre)>|<br\s*/?>", "\n", fragment)
    return unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def inspect_source(readme: str, source: str) -> dict:
    """Conservative static interface inventory; helper methods are not exclusions."""
    front = readme.split("---", 2)[1] if readme.startswith("---") else ""
    tags = re.findall(r"^\s+- (.+)$", front, flags=re.M)
    info = {"tags": tags, "interfaces": [], "exclusion": None, "review_notes": []}
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        info["review_notes"].append(f"Reference source requires syntax review: {exc.msg}")
        return info
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
            info["interfaces"].append({"class": node.name, "methods": [m.name for m in methods],
                "signatures": [ast.unparse(m.args) for m in methods]})
    if "Interactive" in tags:
        info["exclusion"] = {"category": "interactive", "reason": "Source explicitly tags an interactive judge protocol."}
    elif "Design" in tags and info["interfaces"]:
        # A Solution class used for one named function is never excluded just for being a class.
        designed = [i for i in info["interfaces"] if i["class"] not in {"Solution", "TreeNode", "ListNode", "Node"}
                    and len(i["methods"]) >= 2
                    and any(not method.startswith("_") for method in i["methods"])]
        if designed:
            info["exclusion"] = {"category": "multi-method-design", "reason": "Design exercise requires persistent operations: " +
                "; ".join(i["class"] + ".{" + ", ".join(i["methods"]) + "}" for i in designed)}
    elif "Design" in tags:
        # Some upstream design entries have complete HTML documentation but no
        # Python solution file. Preserve the same scope decision when the prose
        # explicitly documents several persistent public operations.
        methods = list(dict.fromkeys(re.findall(r"<li><code>(?:[\w\[\]]+\s+)?(\w+)\(", readme)))
        if len(methods) >= 2:
            class_match = re.search(r"Implement the <code>(\w+)</code> class", readme)
            class_name = class_match.group(1) if class_match else "documented design class"
            info["exclusion"] = {"category": "multi-method-design",
                                 "reason": f"Design exercise requires persistent operations: {class_name}.{{{', '.join(methods)}}}"}
    if not source.strip():
        info["review_notes"].append("Missing Python reference candidate; implementation required.")
    return info


def inventory(workbook: Path, metadata_path: Path, source_repository: Path, output: Path) -> dict:
    rows = workbook_rows(workbook)
    metadata = json.loads(metadata_path.read_text())["data"]
    by_title = {item["title"]: item for item in metadata}
    readmes = {int(p.parent.name.split(".", 1)[0]): p for p in (source_repository / "solution").glob("*/*/README_EN.md")
               if p.parent.name.split(".", 1)[0].isdigit()}
    revision = subprocess.check_output(["git", "-C", str(source_repository), "rev-parse", "HEAD"], text=True).strip()
    from .content import PROBLEMS
    existing = {p.id for p in PROBLEMS}
    if any(problem_id not in existing for problem_id, _ in OVERLAPS.values()):
        raise ValueError("Overlap mapping references an unknown existing problem")
    output.mkdir(parents=True, exist_ok=True)
    ledger_path = output / "ledger.json"
    old = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    old_rows = {r["source_id"]: r for r in old.get("records", [])}
    sources, records = [], []
    for row in rows:
        item = by_title.get(row["title"])
        if item is None:
            raise ValueError(f"Cannot resolve workbook title to source ID: {row['title']}")
        pid = int(item["questionFrontendId"])
        readme_path = readmes.get(pid)
        readme = readme_path.read_text() if readme_path else ""
        code_path = readme_path.parent / "Solution.py" if readme_path else None
        code = code_path.read_text() if code_path and code_path.exists() else ""
        inspected = inspect_source(readme, code)
        relative = str(readme_path.relative_to(source_repository)) if readme_path else None
        source = {**row, "source_id": pid, "slug": item["titleSlug"],
            "source_url": f"https://leetcode.com/problems/{item['titleSlug']}/",
            "reference_url": f"https://github.com/doocs/leetcode/blob/{revision}/{quote(relative)}" if relative else None,
            "source_revision": revision, "reference_candidate": code,
            "description_html": (re.search(r"<!-- description:start -->(.*?)<!-- description:end -->", readme, re.S).group(1)
                                 if "<!-- description:start -->" in readme and "<!-- description:end -->" in readme else ""),
            **inspected}
        source_hash = fingerprint(source)
        record = {"source_id": pid, "workbook_row": row["workbook_row"], "title": row["title"],
            "difficulty": row["difficulty"], "source_hash": source_hash,
            "status": "pending", "existing_id": None, "reason": "Requires contract review, independent tests, and validation.",
            "validation_report": None}
        if pid in OVERLAPS:
            record.update(status="overlap", existing_id=OVERLAPS[pid][0], reason=OVERLAPS[pid][1])
        elif inspected["exclusion"]:
            record.update(status="excluded", reason=inspected["exclusion"]["reason"], exclusion_category=inspected["exclusion"]["category"])
        previous = old_rows.get(pid)
        if previous and previous["source_hash"] == source_hash and previous["status"] in {"imported", "quarantined"}:
            record = previous
        elif previous and previous["status"] == "imported" and previous["source_hash"] != source_hash:
            record.update(status="quarantined", reason="Source changed since validation; revalidation required.")
        sources.append(source)
        records.append(record)
    from .reconcile_overlaps import restore_import_overlaps
    restore_import_overlaps(records, old_rows, output.parent)
    from .reconcile_original_overlaps import restore_original_overlaps
    restore_original_overlaps(records, old_rows, output.parent)
    counts = dict(Counter(r["status"] for r in records))
    ledger = {"schema_version": 1, "workbook": workbook.name,
        "workbook_sha256": hashlib.sha256(workbook.read_bytes()).hexdigest(),
        "source_revision": revision, "counts": counts, "record_count": len(records),
        "missing_workbook_samples": sum(not r["sample"] for r in rows), "records": records}
    # Deterministic generated data; replace only this tool's owned output artifacts.
    write_text_atomic(output / "sources.jsonl", "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in sources))
    write_json_atomic(ledger_path, ledger)
    write_text_atomic(output / "SOURCE_LICENSE.txt", (source_repository / "LICENSE").read_text())
    return {k: v for k, v in ledger.items() if k != "records"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--source-metadata", type=Path, required=True)
    parser.add_argument("--source-repository", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=APP_ROOT / "catalog_import")
    args = parser.parse_args()
    print(json.dumps(inventory(args.workbook, args.source_metadata, args.source_repository, args.output), indent=2))


if __name__ == "__main__":
    main()
