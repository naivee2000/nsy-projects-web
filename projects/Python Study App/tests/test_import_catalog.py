import json
from collections import deque
from pathlib import Path
import random
import shutil

import pytest

from fastapi.testclient import TestClient

from code_practice import catalog, database
from code_practice.app import app
from code_practice.build_import_batch import BATCH, build, verify, workbook_sample, review_isolated, cached_validation_is_current
from code_practice.import_workbook import inspect_source
from code_practice.import_decisions import eligible_original_ids, first_match_by_original, original_overlap_search_state
from code_practice.package_catalog import package
from code_practice.validation import run_source

ROOT = Path(__file__).resolve().parent.parent


def test_original_overlap_search_retires_each_original_after_its_first_match():
    from code_practice.content import PROBLEMS

    original_ids = [problem.id for problem in PROBLEMS]
    state = original_overlap_search_state(original_ids)
    first_matches = first_match_by_original()
    assert state["original_count"] == 101
    assert state["matched_count"] == len(first_matches) == 71
    assert state["unresolved_count"] == len(eligible_original_ids(original_ids)) == 30
    assert "recursive-step-combinations" in first_matches
    assert first_matches["recursive-step-combinations"] == 70
    assert "recursive-step-combinations" not in state["unresolved"]


def test_interface_exclusions_preserve_ordinary_trees_and_linked_lists():
    for name in ("TreeNode", "ListNode"):
        source = f"class Solution:\n    def solve(self, root: {name}):\n        return root\n    def helper(self, node):\n        return node\n"
        assert inspect_source("---\ntags:\n    - Recursion\n---", source)["exclusion"] is None
    design = inspect_source("---\ntags:\n    - Design\n---", "class LRUCache:\n    def get(self,k): pass\n    def put(self,k,v): pass\n")
    assert design["exclusion"]["category"] == "multi-method-design"
    immutable_query = inspect_source(
        "---\ntags:\n    - Design\n---",
        "class NumArray:\n    def __init__(self, nums): pass\n    def sumRange(self, left, right): pass\n",
    )
    assert immutable_query["exclusion"]["category"] == "multi-method-design"
    documented_only = inspect_source(
        "---\ntags:\n    - Design\n---\nImplement the <code>VideoShelf</code> class"
        "<li><code>VideoShelf()</code></li><li><code>int upload(String video)</code></li>"
        "<li><code>void remove(int id)</code></li>",
        "",
    )
    assert documented_only["exclusion"]["category"] == "multi-method-design"
    assert "VideoShelf.{VideoShelf, upload, remove}" in documented_only["exclusion"]["reason"]
    interactive = inspect_source("---\ntags:\n    - Interactive\n---", "class Solution:\n    def solve(self, master): pass\n")
    assert interactive["exclusion"]["category"] == "interactive"


def test_ledger_accounts_for_every_row_and_published_imports_are_verified():
    ledger = json.loads((ROOT / "catalog_import/ledger.json").read_text())
    assert ledger["record_count"] == len(ledger["records"]) == 3629
    assert len({r["source_id"] for r in ledger["records"]}) == 3629
    assert {r["workbook_row"] for r in ledger["records"]} == set(range(7, 3636))
    assert sum(ledger["counts"].values()) == 3629
    published = set(catalog.get_catalog())
    for r in ledger["records"]:
        if r["status"] == "imported":
            assert r["problem_id"] in published
            report = json.loads((ROOT / r["validation_report"]).read_text())
            assert report["valid"] and report["oracle_inputs"] >= 500
        elif r["status"] == "overlap":
            assert r["existing_id"] in published
        else:
            assert f"leetcode-{r['source_id']}" not in published


def test_reviewed_batches_have_current_cached_evidence_without_repeating_oracle_runs():
    """Full 500-case validation happens at import time, not for every test run."""
    sources = {s["source_id"]: s for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines() if (s := json.loads(line))}
    records = {r["source_id"]: r for r in json.loads((ROOT / "catalog_import/ledger.json").read_text())["records"]}
    for pid, spec in BATCH.items():
        record = records[pid]
        if record["status"] == "imported":
            assert cached_validation_is_current(pid, spec, record["source_hash"], record)
    # A representative validator still proves the full deterministic/oracle path.
    pid = 11
    problem = build(pid, BATCH[pid], sources[pid])
    report = verify(problem, BATCH[pid], records[pid]["source_hash"])
    assert report["valid"] and report["oracle_inputs"] == 500
    assert len({json.dumps(t.arguments) for t in problem.tests}) == len(problem.tests)


def test_cached_validation_rejects_changed_candidate_content(tmp_path):
    ledger = json.loads((ROOT / "catalog_import/ledger.json").read_text())
    record = next(row for row in ledger["records"] if row["source_id"] == 11)
    source = next(json.loads(line) for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines()
                  if json.loads(line)["source_id"] == 11)
    report_path = tmp_path / record["validation_report"]
    candidate_path = tmp_path / "catalog_import/candidates/leetcode-11.json"
    report_path.parent.mkdir(parents=True)
    candidate_path.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / record["validation_report"], report_path)
    candidate = json.loads((ROOT / "catalog_import/candidates/leetcode-11.json").read_text())
    candidate["reference_solution"] = "def max_water_area(height):\n    return -1\n"
    candidate_path.write_text(json.dumps(candidate))
    assert not cached_validation_is_current(11, BATCH[11], record["source_hash"], record, tmp_path)


def test_library_and_dashboard_never_load_full_problem_payloads(monkeypatch):
    def forbidden(self, key):
        raise AssertionError("Overview loaded a full problem")
    monkeypatch.setattr(catalog.Catalog, "_load_detail", forbidden)
    catalog.refresh_catalog()
    with TestClient(app) as client:
        first = client.get("/api/problems?page_size=10").json()
        second = client.get("/api/problems?page=2&page_size=10").json()
        assert len(first["items"]) == len(second["items"]) == 10
        assert {p["id"] for p in first["items"]}.isdisjoint(p["id"] for p in second["items"])
        assert client.get("/api/dashboard").status_code == 200
        assert client.get("/api/problems?search=Word%20Search").json()["items"][0]["id"] == "leetcode-79"
        assert client.get("/api/problems?topic=linked-lists").json()["total"] >= 7
        assert client.get("/api/problems?search=%25_literal_missing_%25").json()["total"] == 0


def test_old_passed_progress_survives_pagination_and_catalog_rebuild(tmp_path, monkeypatch):
    with database.db_session() as connection:
        row = ("pair-sum-indices", 1, "saved solution", "accepted", 1, 12, 12, 30, 0, "2025-01-01T00:00:00+00:00")
        statement = "INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,tests_passed,tests_total,elapsed_study_seconds,hint_level,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)"
        connection.execute(statement, row)
        connection.executemany(statement, [("valid-brackets", 1, "pass", "wrong_answer", 1, 0, 12, 1, 0, "2026-01-01T00:00:00+00:00")] * 501)
    database.save_draft("pair-sum-indices", "my unfinished edits")
    before = database.DB_PATH.read_bytes()
    package(tmp_path / "new-catalog")
    assert database.DB_PATH.read_bytes() == before
    monkeypatch.setattr(catalog, "CATALOG_DIR", tmp_path / "new-catalog")
    catalog.refresh_catalog()
    with TestClient(app) as client:
        passed = client.get("/api/problems?completion=passed").json()
        assert [p["id"] for p in passed["items"]] == ["pair-sum-indices"]
        dashboard = client.get("/api/dashboard").json()
        assert dashboard["attemptCount"] == 502
        assert dashboard["solvedCount"] == 1
        assert "pair-sum-indices" not in {p["id"] for p in dashboard["recommendations"]}
        assert client.get("/api/problems/pair-sum-indices").json()["savedDraft"] == "my unfinished edits"


def test_publisher_rejects_changed_content_with_an_old_passing_report(tmp_path, monkeypatch):
    from code_practice import package_catalog
    candidate_dir = tmp_path / "catalog_import/candidates"
    report_dir = tmp_path / "catalog_import/reports"
    candidate_dir.mkdir(parents=True)
    report_dir.mkdir()
    payload = json.loads((ROOT / "catalog_import/candidates/leetcode-11.json").read_text())
    payload["reference_solution"] = "def max_water_area(height):\n    return -1\n"
    (candidate_dir / "leetcode-11.json").write_text(json.dumps(payload))
    (report_dir / "leetcode-11.json").write_text((ROOT / "catalog_import/reports/leetcode-11.json").read_text())
    record = next(r for r in json.loads((ROOT / "catalog_import/ledger.json").read_text())["records"] if r["source_id"] == 11)
    (tmp_path / "catalog_import/ledger.json").write_text(json.dumps({"records": [record]}))
    monkeypatch.setattr(package_catalog, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="stale"):
        package_catalog.package(tmp_path / "published")
    assert not (tmp_path / "published/manifest.json").exists()


def test_tree_results_preserve_sparse_shape_and_reject_cycles():
    problem = catalog.get_catalog()["leetcode-226"]
    case = next(t for t in problem.tests if t.arguments == [[1, 2, None, 3]])
    assert case.expected == [1, None, 2, None, 3]
    assert run_source(problem.reference_solution, problem, case) == (True, None)
    passed, error = run_source("def invert_tree(root):\n    root.left = root\n    return root\n", problem, case)
    assert not passed and "cycle" in error


def test_k_group_requires_original_nodes_and_unchanged_values():
    problem = catalog.get_catalog()["leetcode-25"]
    case = problem.tests[0]
    copied_solution = '''def reverse_k_group(head, k):
    values = []
    while head:
        values.append(head.val)
        head = head.next
    dummy = ListNode()
    tail = dummy
    for start in range(0, len(values), k):
        group = values[start:start+k]
        for value in reversed(group) if len(group) == k else group:
            tail.next = ListNode(value)
            tail = tail.next
    return dummy.next
'''
    rewritten_values = '''def reverse_k_group(head, k):
    nodes = []
    current = head
    while current:
        nodes.append(current)
        current = current.next
    for start in range(0, len(nodes)-k+1, k):
        values = [node.val for node in nodes[start:start+k]][::-1]
        for node, value in zip(nodes[start:start+k], values):
            node.val = value
    return head
'''
    values_only = problem.model_copy(deep=True)
    values_only.signature.node_policy = "values"
    for source in (copied_solution, rewritten_values):
        assert run_source(source, values_only, case) == (True, None)
        assert run_source(source, problem, case) == (False, None)
    assert run_source(problem.reference_solution, problem, case) == (True, None)


def test_sample_parser_preserves_json_literals_and_blocks_expressions():
    args, expected = workbook_sample("Input root = [1,null,2] → Output false.", [{"name": "root"}])
    assert args == [[1, None, 2]] and expected is False
    with pytest.raises(ValueError):
        workbook_sample("Input nums = list(range(10)) → Output 1.", [{"name": "nums"}])
    with pytest.raises(ValueError):
        workbook_sample("Input nums = [1,2] → Output 1.", [{"name": "height"}])


def test_import_timeout_and_bad_sample_are_quarantined_without_poisoning_next_problem():
    source = next(json.loads(line) for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines()
                  if json.loads(line)["source_id"] == 11)
    spec = {**BATCH[11], "reference": "def max_water_area(height):\n    while True: pass\n"}
    payload, report = review_isolated(11, spec, source, "test", timeout_seconds=1)
    assert payload is None and not report["valid"]
    assert "exceeded" in report["failures"][0]["error"]
    payload, report = review_isolated(11, BATCH[11], {**source, "sample": "Input height = [1,1] → Output 999."}, "test")
    assert payload is None and not report["valid"]
    assert "conflicts" in report["failures"][0]["error"]
    payload, report = review_isolated(11, BATCH[11], source, "test")
    assert payload["id"] == "leetcode-11" and report["valid"]


def test_new_tree_list_inputs_respect_source_domains_including_stress_cases():
    from code_practice.import_batch_004 import BATCH as node_batch
    sources = {s["source_id"]: s for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines() if (s := json.loads(line))}
    bounds = {129: (1, 1000, 0, 9), 230: (1, 10000, 0, 10000),
              404: (1, 1000, -1000, 1000), 543: (1, 10000, -100, 100),
              563: (0, 10000, -1000, 1000), 700: (1, 5000, 1, 10**7)}
    for pid, spec in node_batch.items():
        problem = build(pid, spec, sources[pid])
        rng = random.Random(4047 + pid)
        inputs = [t.arguments for t in problem.tests] + [spec["generator"](rng) for _ in range(500)]
        for args in inputs:
            values = args[0]
            if pid in {19, 24, 92}:
                minimum, maximum, lo, hi = {19: (1, 30, 0, 100), 24: (0, 100, 0, 100), 92: (1, 500, -500, 500)}[pid]
                assert minimum <= len(values) <= maximum
                assert all(type(value) is int and lo <= value <= hi for value in values)
                if pid == 19:
                    assert 1 <= args[1] <= len(values)
                if pid == 92:
                    assert 1 <= args[1] <= args[2] <= len(values)
                continue
            minimum, maximum, lo, hi = bounds[pid]
            count = sum(v is not None for v in values)
            assert minimum <= count <= maximum
            assert all(v is None or (type(v) is int and lo <= v <= hi) for v in values)
            if not values:
                continue
            assert values[0] is not None
            # Verify compact breadth-first encoding and BST order without an
            # O(depth²) path map for the 10,000-node chain stress fixtures.
            queue, index = deque([(values[0], 1, float('-inf'), float('inf'))]), 1
            while queue:
                value, depth, lower, upper = queue.popleft()
                if pid in {230, 700}:
                    assert lower < value < upper
                if pid == 129:
                    assert depth <= 10
                for side in (0, 1):
                    if index == len(values):
                        break
                    child = values[index]
                    index += 1
                    if child is not None:
                        queue.append((child, depth + 1, lower if side == 0 else value, value if side == 0 else upper))
            assert index == len(values), 'orphan nodes in serialized input'
            if pid == 129:
                assert 0 <= spec["oracle"](args) <= 2**31 - 1
            if pid == 230:
                assert 1 <= args[1] <= count
            if pid == 700:
                assert 1 <= args[1] <= 10**7


def test_new_node_exercises_remain_ordinary_imports_and_keep_link_identity():
    from code_practice.import_batch_004 import BATCH as node_batch
    ledger = json.loads((ROOT / "catalog_import/ledger.json").read_text())
    rows = {r["source_id"]: r for r in ledger["records"]}
    for pid in node_batch:
        assert rows[pid]["status"] == "imported"
        assert catalog.get_catalog()[f"leetcode-{pid}"].signature.parameters[0].adapter in {"listnode", "treenode"}
    for pid in (24, 92):
        assert catalog.get_catalog()[f"leetcode-{pid}"].signature.node_policy == "reuse_input_nodes"


def test_interrupted_ledger_replacement_preserves_previous_json(tmp_path, monkeypatch):
    from code_practice.catalog_artifacts import write_json_atomic
    path = tmp_path / "offline-artifacts" / "ledger.json"
    original = {"records": [{"source_id": 24, "status": "imported"}]}
    write_json_atomic(path, original)
    previous_bytes = path.read_bytes()
    with monkeypatch.context() as context:
        def interrupt(*_):
            raise OSError("simulated interruption before rename")
        context.setattr(Path, "replace", interrupt)
        with pytest.raises(OSError, match="simulated interruption"):
            write_json_atomic(path, {"records": []})
    assert path.read_bytes() == previous_bytes
    assert json.loads(path.read_text()) == original
    assert list(path.parent.iterdir()) == [path]
    updated = {"records": original["records"] + [{"source_id": 92, "status": "imported"}]}
    write_json_atomic(path, updated)
    assert json.loads(path.read_text()) == updated


def test_enumeration_comparators_allow_ordering_but_not_missing_or_duplicate_results():
    for pid in (39, 77, 78, 90):
        problem = catalog.get_catalog()[f"leetcode-{pid}"]
        name = problem.signature.name
        reordered = problem.reference_solution + f"\noriginal = {name}\ndef {name}(*args):\n    return [row[::-1] for row in original(*args)][::-1]\n"
        assert run_source(reordered, problem, problem.tests[0]) == (True, None)
        for suffix in (" * 2", "[1:]"):
            broken = problem.reference_solution + f"\noriginal = {name}\ndef {name}(*args):\n    return original(*args){suffix}\n"
            assert run_source(broken, problem, problem.tests[0]) == (False, None)
    phone = catalog.get_catalog()["leetcode-17"]
    reversed_letters = phone.reference_solution + "\noriginal = phone_combinations\ndef phone_combinations(digits):\n    return [word[::-1] for word in original(digits)]\n"
    assert run_source(reversed_letters, phone, phone.tests[0]) == (False, None)


def test_new_grid_problems_receive_existing_weak_topic_priority():
    from code_practice.learning import is_grid_recursion_problem, review_focus_boost
    for pid in (63, 64):
        problem = catalog.get_catalog()[f"leetcode-{pid}"]
        assert is_grid_recursion_problem(problem)
        assert review_focus_boost(problem) > review_focus_boost(catalog.get_catalog()["leetcode-62"])
    assert "binary-search" in catalog.get_catalog()["leetcode-74"].topics


def test_regex_and_wildcard_star_semantics_are_not_conflated():
    from code_practice.schemas import TestCase
    regex = catalog.get_catalog()["leetcode-10"]
    wildcard = catalog.get_catalog()["leetcode-44"]
    for args, regex_expected, wildcard_expected in ((["ab", "a*"], False, True), (["b", "a*b"], True, False)):
        for problem, expected in ((regex, regex_expected), (wildcard, wildcard_expected)):
            assert run_source(problem.reference_solution, problem, TestCase(id="star-contract", arguments=args, expected=expected)) == (True, None)
    for pid in (10, 32, 41, 44):
        problem = catalog.get_catalog()[f"leetcode-{pid}"]
        assert problem.difficulty >= 8 and problem.prerequisites


def test_matching_and_jump_generators_stay_inside_reviewed_input_domains():
    from code_practice.import_batch_006 import BATCH as hard_batch, reachable_oracle
    for pid, spec in hard_batch.items():
        rng = random.Random(4047 + pid)
        for _ in range(500):
            args = spec["generator"](rng)
            if pid == 10:
                text, pattern = args
                assert 1 <= len(text) <= 20 and 1 <= len(pattern) <= 20
                assert set(text) <= set("abcdefghijklmnopqrstuvwxyz")
                assert set(pattern) <= set("abcdefghijklmnopqrstuvwxyz.*")
                assert all(i > 0 and pattern[i - 1] != "*" for i, char in enumerate(pattern) if char == "*")
            elif pid == 44:
                text, pattern = args
                assert len(text) <= 2000 and len(pattern) <= 2000
                assert set(text) <= set("abcdefghijklmnopqrstuvwxyz")
                assert set(pattern) <= set("abcdefghijklmnopqrstuvwxyz?*")
            elif pid == 32:
                assert len(args[0]) <= 30000 and set(args[0]) <= set("()")
            elif pid == 41:
                assert 1 <= len(args[0]) <= 100000
                assert all(-(2**31) <= value < 2**31 for value in args[0])
            else:
                assert 1 <= len(args[0]) <= 10000
                assert all(0 <= value <= (1000 if pid == 45 else 100000) for value in args[0])
                if pid == 45:
                    assert reachable_oracle(args), "Minimum-jump inputs must guarantee a reachable destination"


def test_spiral_equivalent_covers_rectangles_and_preserves_old_progress():
    from code_practice.schemas import TestCase
    problem = catalog.get_catalog()["matrix-spiral-order"]
    assert problem.version == 2 and "rectangular" in problem.statement
    def walk(matrix):
        if not matrix or not matrix[0]:
            return []
        rows, cols = len(matrix), len(matrix[0])
        seen, answer, row, col, direction = set(), [], 0, 0, 0
        steps = ((0, 1), (1, 0), (0, -1), (-1, 0))
        for _ in range(rows * cols):
            seen.add((row, col))
            answer.append(matrix[row][col])
            dr, dc = steps[direction]
            nr, nc = row + dr, col + dc
            if not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) in seen:
                direction = (direction + 1) % 4
                dr, dc = steps[direction]
            row, col = row + dr, col + dc
        return answer
    rng = random.Random(4054)
    cases = list(problem.tests)
    for i in range(500):
        rows, cols = rng.randint(1, 10), rng.randint(1, 10)
        matrix = [[rng.randint(-100, 100) for _ in range(cols)] for _ in range(rows)]
        cases.append(TestCase(id=f"rectangle-oracle-{i}", arguments=[matrix], expected=walk(matrix)))
    for case in cases:
        assert case.expected == walk(case.arguments[0])
        assert run_source(problem.reference_solution, problem, case) == (True, None)
    wrong = [problem.reference_solution.replace("len(matrix[0])-1", "len(matrix)-1"),
             "def matrix_spiral_order(matrix):\n    return [value for row in matrix for value in row]\n"]
    for source in wrong:
        assert any(run_source(source, problem, case) == (False, None) for case in problem.tests)
    with database.db_session() as connection:
        connection.execute("INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,tests_passed,tests_total,elapsed_study_seconds,hint_level,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                           (problem.id, 1, "old accepted solution", "accepted", 1, 14, 14, 60, 0, "2026-01-01T00:00:00+00:00"))
    database.save_draft(problem.id, "saved personal draft")
    catalog.refresh_catalog()
    with TestClient(app) as client:
        detail = client.get(f"/api/problems/{problem.id}").json()
        assert detail["version"] == 2 and detail["solved"]
        assert detail["savedDraft"] == "saved personal draft"
        assert client.get("/api/problems?completion=passed").json()["items"][0]["id"] == problem.id
    old = database.list_attempts()[0]
    assert old.problem_version == 1 and old.source_code == "old accepted solution"


def test_conversion_references_obey_arithmetic_contracts():
    import ast
    from code_practice.import_batch_007 import DIVISION, NUMERAL, ROMAN, roman_oracle
    from code_practice.import_batch_008 import PRODUCT
    # The arithmetic restrictions apply to references as well as to learners.
    assert not any(isinstance(node, (ast.Mult, ast.Div, ast.FloorDiv, ast.Mod))
                   for node in ast.walk(ast.parse(DIVISION)))
    assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "int"
                   for node in ast.walk(ast.parse(PRODUCT)))
    namespace = {}
    exec(ROMAN + NUMERAL, namespace)
    for number in range(1, 4000):
        numeral = namespace["integer_to_roman"](number)
        assert numeral == roman_oracle([number])
        assert namespace["roman_to_integer"](numeral) == number


def test_nearest_sum_and_string_generators_respect_source_domains():
    from code_practice.import_batch_008 import BATCH as string_batch, closest_oracle
    for pid, spec in string_batch.items():
        rng = random.Random(4047 + pid)
        arguments = [args for args, _ in spec["examples"]] + spec["boundaries"]
        arguments += [args for args, _ in spec.get("stress", [])]
        arguments += [spec["generator"](rng) for _ in range(500)]
        for args in arguments:
            if pid == 16:
                nums, target = args
                assert 3 <= len(nums) <= 500
                assert all(-1000 <= number <= 1000 for number in nums)
                assert -10000 <= target <= 10000
                # The 500-element all-equal stress case has one possible sum;
                # avoid needlessly enumerating 20 million identical triples.
                if len(set(nums)) == 1:
                    assert len(nums) >= 3
                else:
                    closest_oracle(args)  # Raises if two different sums tie.
            elif pid == 28:
                assert all(1 <= len(value) <= 10000 and set(value) <= set("abcdefghijklmnopqrstuvwxyz") for value in args)
            elif pid == 38:
                assert 1 <= args[0] <= 30
            else:
                assert all(1 <= len(value) <= 200 and set(value) <= set("0123456789")
                           and (value == "0" or not value.startswith("0")) for value in args)
    problem = catalog.get_catalog()["leetcode-16"]
    assert "distinct indices" in problem.summary
    assert "distinct integers" not in problem.statement
    repeated = next(case for case in problem.tests if case.arguments == [[0, 0, 0], 1])
    assert run_source(problem.reference_solution, problem, repeated) == (True, None)
    assert "recursion" in catalog.get_catalog()["leetcode-38"].topics


def test_tree_batch_inputs_match_limits_and_path_comparison_keeps_multiplicity():
    from code_practice.import_batch_009 import BATCH as tree_batch
    from code_practice.validation import compare
    from code_practice.learning import prerequisites_met, review_focus_boost
    limits = {94: (0, 100, 100), 144: (0, 100, 100), 145: (0, 100, 100),
              103: (0, 2000, 100), 107: (0, 2000, 1000),
              113: (0, 5000, 1000), 124: (1, 30000, 1000)}
    for pid, spec in tree_batch.items():
        rng = random.Random(4047 + pid)
        cases = [args for args, _ in spec["examples"]] + spec["boundaries"]
        cases += [args for args, _ in spec["stress"]]
        cases += [spec["generator"](rng) for _ in range(500)]
        for args in cases:
            if pid == 120:
                triangle = args[0]
                assert 1 <= len(triangle) <= 200
                for index, row in enumerate(triangle):
                    assert len(row) == index + 1 and all(-10000 <= value <= 10000 for value in row)
                continue
            lower, upper, magnitude = limits[pid]
            tree = args[0]
            assert lower <= sum(value is not None for value in tree) <= upper
            assert all(value is None or -magnitude <= value <= magnitude for value in tree)
            # A compact BFS input must not contain orphan values after all
            # possible parent slots have been exhausted.
            pending = 1
            for value in tree:
                assert pending > 0
                pending += 1 if value is not None else -1
            if pid == 113:
                assert -1000 <= args[1] <= 1000
    problem = catalog.get_catalog()["leetcode-113"]
    duplicate = next(case for case in problem.tests if case.arguments == [[0, 0, 0], 0])
    assert duplicate.expected == [[0, 0], [0, 0]]
    assert not compare([[0, 0]], duplicate.expected, duplicate.comparator)
    example = next(case for case in problem.tests if case.visible)
    assert compare(example.expected[::-1], example.expected, example.comparator)
    assert not compare([path[::-1] for path in example.expected], example.expected, example.comparator)
    assert review_focus_boost(problem) >= 50
    hard = catalog.get_catalog()["leetcode-124"]
    assert hard.difficulty >= 8 and not prerequisites_met(hard, {"trees": 100, "recursion": 69})
    assert prerequisites_met(hard, {"trees": 70, "recursion": 70})


def test_three_traversal_orders_and_two_level_orders_remain_distinct():
    from code_practice.schemas import TestCase
    examples = {94: [1, 3, 2], 144: [1, 2, 3], 145: [3, 2, 1]}
    for pid, expected in examples.items():
        problem = catalog.get_catalog()[f"leetcode-{pid}"]
        case = TestCase(id="ordered-tree", arguments=[[1, None, 2, 3]], expected=expected)
        assert run_source(problem.reference_solution, problem, case) == (True, None)
    for pid, expected in ((103, [[3], [20, 9], [15, 7]]), (107, [[15, 7], [9, 20], [3]])):
        problem = catalog.get_catalog()[f"leetcode-{pid}"]
        case = TestCase(id="level-order", arguments=[[3, 9, 20, None, None, 15, 7]], expected=expected)
        assert run_source(problem.reference_solution, problem, case) == (True, None)


def test_string_and_greedy_batch_respects_domains_and_unique_circuit_guarantee():
    from itertools import accumulate
    from code_practice.import_batch_010 import BATCH as batch, feasible_starts, subsequences_oracle
    for pid, spec in batch.items():
        rng = random.Random(4047 + pid)
        cases = [args for args, _ in spec["examples"]] + spec["boundaries"]
        cases += [args for args, _ in spec["stress"]]
        cases += [spec["generator"](rng) for _ in range(500)]
        for args in cases:
            if pid == 71:
                path = args[0]
                assert 1 <= len(path) <= 3000 and path.startswith("/")
                assert all(char.isascii() and (char.isalnum() or char in "./_") for char in path)
            elif pid == 81:
                values, target = args
                assert 1 <= len(values) <= 5000 and -10000 <= target <= 10000
                assert all(-10000 <= value <= 10000 for value in values)
                assert sum(value > values[(i + 1) % len(values)] for i, value in enumerate(values)) <= 1
            elif pid == 97:
                assert len(args[0]) <= 100 and len(args[1]) <= 100 and len(args[2]) <= 200
                assert all(set(value) <= set("abcdefghijklmnopqrstuvwxyz") for value in args)
            elif pid == 115:
                assert all(1 <= len(value) <= 1000 and value.isascii() and value.isalpha() for value in args)
                if len(args[0]) <= 12:
                    assert 0 <= subsequences_oracle(args) < 2**31
                else:
                    assert args in [arguments for arguments, _ in spec["stress"]]
                    assert all(0 <= expected < 2**31 for _, expected in spec["stress"])
            elif pid in (122, 123, 135):
                size, maximum = {122: (30000, 10000), 123: (100000, 100000), 135: (50000, 50000)}[pid]
                assert 1 <= len(args[0]) <= size and all(0 <= value <= maximum for value in args[0])
            else:
                gas, cost = args
                assert 1 <= len(gas) == len(cost) <= 100000
                assert all(0 <= value <= 10000 for values in args for value in values)
                if len(gas) <= 10:
                    assert len(feasible_starts(gas, cost)) <= 1
                else:
                    # This maximum-size fixture has zero total balance. For
                    # a zero-total circular route, feasible starts are exactly
                    # the indexes attaining the minimum prefix balance.
                    assert sum(gas) == sum(cost)
                    prefixes = list(accumulate((fuel - expense for fuel, expense in zip(gas, cost)), initial=0))[:-1]
                    assert prefixes.count(min(prefixes)) == 1
                    assert prefixes.index(min(prefixes)) == 99999


def test_transaction_caps_and_duplicate_search_are_distinct_from_baseline():
    from code_practice.schemas import TestCase
    from code_practice.learning import review_focus_boost
    for problem_id, expected in (("max-single-trade-profit", 2), ("leetcode-122", 6), ("leetcode-123", 4)):
        problem = catalog.get_catalog()[problem_id]
        case = TestCase(id="transaction-cap", arguments=[[1, 3, 1, 3, 1, 3]], expected=expected)
        assert run_source(problem.reference_solution, problem, case) == (True, None)
    search = catalog.get_catalog()["leetcode-81"]
    assert review_focus_boost(search) >= 60
    case = TestCase(id="ambiguous-boundaries", arguments=[[1, 0, 1, 1, 1], 0], expected=True)
    assert run_source(search.reference_solution, search, case) == (True, None)
    assert "O(n) worst case" in search.target_time_complexity


def test_candy_relaxation_oracle_matches_exhaustive_minimum_assignments():
    from itertools import product
    from code_practice.import_batch_010 import candy_oracle
    for count in range(1, 5):
        for ratings in product(range(3), repeat=count):
            feasible = []
            for candies in product(range(1, count + 1), repeat=count):
                if all((ratings[i] <= ratings[i + 1] or candies[i] > candies[i + 1])
                       and (ratings[i] >= ratings[i + 1] or candies[i] < candies[i + 1])
                       for i in range(count - 1)):
                    feasible.append(sum(candies))
            assert candy_oracle([ratings]) == min(feasible)
