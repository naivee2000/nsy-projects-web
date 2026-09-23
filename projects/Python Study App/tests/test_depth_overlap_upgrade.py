import json
from collections import deque
from pathlib import Path
import random
import sys

from fastapi.testclient import TestClient

from code_practice import catalog, database
from code_practice.app import app
from code_practice.content import PROBLEMS
from code_practice.import_batch_002 import flatten
from code_practice.learning import review_focus_boost
from code_practice.package_catalog import package
from code_practice.schemas import TestCase as Case
from code_practice.validation import run_source


ORIGINAL_RECURSIVE_SOURCE = """def tree_max_depth(root):
    if not root:
        return 0
    return 1 + max(tree_max_depth(root.left), tree_max_depth(root.right))
"""


def _encoded_tree_depth(values):
    if not values or values[0] is None:
        return 0
    pending = deque([1])
    index = 1
    maximum = 1
    while pending and index < len(values):
        parent_depth = pending.popleft()
        for _ in range(2):
            if index < len(values) and values[index] is not None:
                maximum = max(maximum, parent_depth + 1)
                pending.append(parent_depth + 1)
            index += 1
    return maximum


def test_depth_upgrade_keeps_the_recursion_lesson_inside_python_stack_limits():
    problem = catalog.get_catalog()["tree-max-depth"]
    limit = sys.getrecursionlimit()
    deepest = max(problem.tests, key=lambda test: _encoded_tree_depth(test.arguments[0]))
    assert _encoded_tree_depth(deepest.arguments[0]) == 500
    assert run_source(ORIGINAL_RECURSIVE_SOURCE, problem, deepest) == (True, None)
    assert run_source(problem.reference_solution, problem, deepest) == (True, None)
    assert problem.version == 3 and problem.signature.name == "tree_max_depth"
    assert sys.getrecursionlimit() == limit
    assert "depth is at most 500" in " ".join(problem.constraints)
    assert "stack" not in problem.reference_solution
    assert review_focus_boost(problem) >= 50


def test_original_recursion_tree_lessons_do_not_exceed_the_safe_depth_cap():
    for problem in PROBLEMS:
        if "recursion" not in problem.topics:
            continue
        for test in problem.tests:
            for parameter, argument in zip(problem.signature.parameters, test.arguments):
                if parameter.adapter == "treenode":
                    assert _encoded_tree_depth(argument) <= 500, (problem.id, test.id)


def test_depth_reference_and_breadth_first_oracle_pass_all_boundaries_and_wrong_answers_fail():
    problem = catalog.get_catalog()["tree-max-depth"]
    assert problem.reference_solution != problem.brute_force_solution
    assert sum(test.visible for test in problem.tests) == 2
    assert sum(not test.visible for test in problem.tests) == 16
    assert len({json.dumps(test.arguments) for test in problem.tests}) == len(problem.tests)
    for test in problem.tests:
        assert run_source(problem.reference_solution, problem, test) == (True, None)
        assert run_source(problem.brute_force_solution, problem, test) == (True, None)
    assert sum(test.expected == 500 for test in problem.tests) == 2
    assert any(test.expected == 300 for test in problem.tests)
    assert any(test.arguments == [[0] * 20000] and test.expected == 15 for test in problem.tests)
    for wrong in problem.known_wrong_solutions:
        assert any(run_source(wrong, problem, test) == (False, None) for test in problem.tests)


def test_depth_overlap_matches_500_seeded_path_shapes_and_original_workbook_sample():
    problem = catalog.get_catalog()["tree-max-depth"]
    rng = random.Random(4047 + 104)
    for index in range(500):
        count = rng.randrange(301)
        paths = {(): rng.randint(-100, 100)} if count else {}
        slots = [(0,), (1,)]
        for _ in range(1, count):
            path = slots.pop(rng.randrange(len(slots)))
            paths[path] = rng.randint(-100, 100)
            slots.extend((path + (0,), path + (1,)))
        values = flatten(paths)
        expected = max((len(path) + 1 for path in paths), default=0)
        test = Case(id=f"depth-path-oracle-{index}", arguments=[values], expected=expected)
        assert run_source(problem.reference_solution, problem, test) == (True, None)
        assert run_source(problem.brute_force_solution, problem, test) == (True, None)
    root = Path(__file__).resolve().parent.parent
    record = next(item for item in json.loads((root / "catalog_import/ledger.json").read_text())["records"] if item["source_id"] == 104)
    assert record["status"] == "overlap" and record["existing_id"] == problem.id
    assert "leetcode-104" not in catalog.get_catalog()
    from code_practice.build_import_batch import workbook_sample
    source = next(item for line in (root / "catalog_import/sources.jsonl").read_text().splitlines()
                  if (item := json.loads(line))["source_id"] == 104)
    args, expected = workbook_sample(source["sample"], [p.model_dump() for p in problem.signature.parameters])
    assert any(test.visible and test.arguments == args and test.expected == expected for test in problem.tests)


def test_depth_version_one_progress_survives_repackaging_and_reopen(tmp_path, monkeypatch):
    problem = catalog.get_catalog()["tree-max-depth"]
    draft = "def tree_max_depth(root):\n    # My unfinished version-one notes\n    return 1\n"
    with database.db_session() as connection:
        connection.execute("INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,tests_passed,tests_total,elapsed_study_seconds,hint_level,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                           (problem.id, 1, ORIGINAL_RECURSIVE_SOURCE, "accepted", 1, 14, 14, 60, 0, "2026-01-01T00:00:00+00:00"))
    database.save_draft(problem.id, draft)
    before = database.DB_PATH.read_bytes()
    package(tmp_path / "upgraded-catalog")
    assert database.DB_PATH.read_bytes() == before
    monkeypatch.setattr(catalog, "CATALOG_DIR", tmp_path / "upgraded-catalog")
    catalog.refresh_catalog()
    database.initialize_database()
    with TestClient(app) as client:
        detail = client.get(f"/api/problems/{problem.id}").json()
        assert detail["version"] == 3 and detail["solved"]
        assert detail["savedDraft"].endswith(draft)
        assert database.get_draft(problem.id) == draft
        passed = client.get("/api/problems?completion=passed").json()
        assert [item["id"] for item in passed["items"]] == [problem.id]
        assert all(item["id"] != problem.id for item in client.get("/api/dashboard").json()["recommendations"])
    old = database.list_attempts()[0]
    assert old.problem_version == 1 and old.source_code == ORIGINAL_RECURSIVE_SOURCE
