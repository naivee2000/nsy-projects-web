"""Compare the workbook, packaged exercises and browser evidence for a Database release."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from code_practice.database_catalog import CATALOG, INVENTORY, ROOT, pandas_starter

WORKBOOK = ROOT.parent / "LeetCode_Algorithm_Study_Guide_Through_4047.xlsx"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def workbook_catalog(path):
    with ZipFile(path) as archive:
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        sheet = next(
            node for node in book.findall("s:sheets/s:sheet", NS) if node.get("name") == "Database"
        )
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = next(
            node.get("Target") for node in relationships if node.get("Id") == sheet.attrib[REL]
        )
        worksheet = target.lstrip("/") if target.startswith("/") else "xl/" + target
        root = ET.fromstring(archive.read(worksheet))
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = [
                "".join(item.itertext()) for item in ET.fromstring(archive.read("xl/sharedStrings.xml"))
            ]
        records = {}
        header_seen = False
        for row in root.findall("s:sheetData/s:row", NS):
            values = {}
            for cell in row.findall("s:c", NS):
                name = re.match(r"[A-Z]+", cell.attrib["r"])[0]
                value = cell.findtext("s:v", "", NS)
                if cell.get("t") == "s":
                    value = strings[int(value)]
                elif cell.get("t") == "inlineStr":
                    value = "".join(cell.find("s:is", NS).itertext())
                values[name] = value.strip()
            if not header_seen:
                header_seen = values.get("A") == "Problem Name" and values.get("E") == "Language"
                continue
            if not values.get("A"):
                continue
            identifier, title = values["A"].split(". ", 1)
            key = int(identifier)
            assert key not in records, f"Duplicate workbook problem {key}"
            records[key] = title, values["B"], values["E"]
    assert header_seen and len(records) == 323
    return records


def verify_catalog():
    workbook = workbook_catalog(WORKBOOK)
    assert workbook.keys() == INVENTORY.keys() == CATALOG.keys()
    for key, problem in CATALOG.items():
        row = INVENTORY[key]
        assert workbook[key] == (row["title"], row["difficulty"], row["language"]), key
        assert row["summary"] and row["example"] and problem["topic"] and problem["mysql_starter"], key
        assert len(problem["cases"]) == 16, key
        inputs = set()
        for case in problem["cases"]:
            schema = case.get("schema", problem["schema"])
            assert schema.keys() == case["tables"].keys(), key
            for table, rows in case["tables"].items():
                assert all(len(row) == len(schema[table]) for row in rows), key
            expected = case["expected"]
            assert expected["columns"] and all(
                len(r) == len(expected["columns"]) for r in expected["rows"]
            ), key
            tables = {t: sorted(json.dumps(row) for row in rows) for t, rows in case["tables"].items()}
            inputs.add(json.dumps([schema, tables, case["parameters"]], sort_keys=True))
        assert len(inputs) == 16, f"Duplicate inputs for {key}"
        assert len(set([problem["sql"], *problem["wrong"]])) == 3 and len(problem["wrong"]) == 2, key
        assert (
            len(set([problem["pandas"], *problem["wrong_pandas"]])) == 3
            and len(problem["wrong_pandas"]) == 2
        ), key
        for body in [None, problem["pandas"], *problem["wrong_pandas"]]:
            compile(pandas_starter(problem, body=body), f"database-{key}", "exec")
    return Counter(row["difficulty"] for row in INVENTORY.values())


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


def judge_fingerprint(frontend, runtime):
    # Independently reproduce the digest written by the browser sweep.
    files = (
        "code_practice/database_exercise.py",
        "code_practice/database_catalog.py",
        "code_practice/database_judge.py",
        "code_practice/database_routes.py",
        "frontend/public/database-worker.js",
        "scripts/database_catalog_sweep.mjs",
        "scripts/verify_database_browser.mjs",
        "scripts/start_database_judge.sh",
        "frontend/package-lock.json",
    )
    digest = sha256()
    for name in files:
        digest.update((ROOT.parent / name).read_bytes())
    index = (frontend / "index.html").read_bytes()
    digest.update(index)
    digest.update(compact(runtime))
    assets = re.findall(r'(?:src|href)="(/assets/[^"]+)"', index.decode())
    for name in ["database-worker.js", "pyodide/pyodide-lock.json", *assets]:
        digest.update((frontend / name.lstrip("/")).read_bytes())
    return digest.hexdigest()


def problem_fingerprints(version):
    hashes = {}
    for key, exercise in sorted(CATALOG.items()):
        contract = sha256(
            json.dumps([exercise, INVENTORY[key]], ensure_ascii=False).encode()
        ).hexdigest()
        entry = {
            "id": key,
            "sql": exercise["sql"],
            "pandas": pandas_starter(exercise, reference=True),
            "wrong": exercise["wrong"],
            "wrongPandas": [pandas_starter(exercise, body=body) for body in exercise["wrong_pandas"]],
            "contract": contract,
        }
        hashes[str(key)] = sha256(version.encode() + compact(entry)).hexdigest()
    return hashes


def verify_report(report, frontend):
    pairs = {(key, lang) for key in CATALOG for lang in ("mysql", "pandas")}
    assert len(report["combinations"]) == len(pairs) == report["passed"] == 646
    assert report["total"] == len(CATALOG) and report["pending"] == 0
    assert {int(k) for k in report["problemFingerprints"]} == set(CATALOG)
    assert all(
        re.fullmatch("[0-9a-f]{64}", v)
        for v in [
            report["judgeFingerprint"],
            report["catalogFingerprint"],
            *report["problemFingerprints"].values(),
        ]
    )
    assert report["runtime"]["mysqlImage"].startswith("mysql@sha256:")
    version = judge_fingerprint(frontend, report["runtime"])
    assert version == report["judgeFingerprint"], (
        "The browser report belongs to a different judge or frontend build"
    )
    hashes = problem_fingerprints(version)
    assert hashes == report["problemFingerprints"], (
        "A problem description, fixture or reference has changed"
    )
    assert sha256(compact(hashes)).hexdigest() == report["catalogFingerprint"]
    for row in report["combinations"]:
        pairs.remove((row["id"], row["language"]))
        assert row["status"] == "passed" and row["cases"] == 16 and row["examples"] == 2
        assert row["wrongAnswersRejected"] == len(row["wrongAnswerFailedCases"]) == 2
        assert all(cases and all(1 <= n <= 16 for n in cases) for cases in row["wrongAnswerFailedCases"])
    assert not pairs
    assert sum(row["cases"] for row in report["combinations"]) == report["referenceCases"] == 10336
    assert (
        sum(row["wrongAnswersRejected"] for row in report["combinations"])
        == report["wrongAnswerSubmissionsRejected"]
        == 1292
    )


def with_batch_index(report):
    from code_practice.database_special import exercises
    from scripts.build_database_exercises import SETS

    pilots = set(exercises())
    remaining = sorted(SETS)
    groups = [
        ("Existing exercises", sorted(CATALOG.keys() - pilots - SETS.keys())),
        ("Runner coverage", sorted(pilots)),
    ]
    groups.extend(
        (f"Catalog batch {start // 32 + 1}", remaining[start : start + 32])
        for start in range(0, len(remaining), 32)
    )
    assert sorted(key for _, ids in groups for key in ids) == sorted(CATALOG)
    rows = sorted(report["combinations"], key=lambda r: (r["id"], r["language"]))
    batches = []
    for name, ids in groups:
        verified = [row for row in rows if row["id"] in ids]
        batches.append(
            {
                "name": name,
                "problemIds": ids,
                "passedCombinations": len(verified),
                "referenceCases": sum(row["cases"] for row in verified),
                "rejectedWrongSubmissions": sum(row["wrongAnswersRejected"] for row in verified),
            }
        )
    return {
        **report,
        "batches": batches,
        "combinations": [
            {"id": row["id"], "title": INVENTORY[row["id"]]["title"], **row} for row in rows
        ],
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "local_verification.json")
    parser.add_argument("--catalog-only", action="store_true")
    parser.add_argument("--frontend", type=Path, default=ROOT.parent / "frontend/dist-local")
    parser.add_argument("--output", type=Path, help="Save the verified report with its batch index")
    args = parser.parse_args()
    counts = verify_catalog()
    print("Workbook and executable catalog agree:", dict(counts))
    if not args.catalog_only:
        report = json.loads(args.report.read_text())
        verify_report(report, args.frontend)
        if args.output:
            args.output.write_text(
                json.dumps(with_batch_index(report), ensure_ascii=False, indent=2) + "\n"
            )
        print(
            "Matched all 646 verified language combinations, 10,336 cases and 1,292 rejected wrong submissions."
        )
