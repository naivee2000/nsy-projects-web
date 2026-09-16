import ast
import json
import re
from pathlib import Path

from code_practice.build_import_batch import BATCH
from code_practice.catalog import get_catalog
from code_practice.content import PROBLEMS
from code_practice.order_insensitive_outputs import ORDER_INSENSITIVE_COMPARATORS
from code_practice.validation import compare


ROOT = Path(__file__).resolve().parents[1]


def worker_compare():
    source = (ROOT / "frontend" / "public" / "judge-worker.js").read_text()
    python_source = source.split("runPythonAsync(`", 1)[1].split("`);", 1)[0]
    functions = [
        node for node in ast.parse(python_source).body
        if isinstance(node, ast.FunctionDef) and node.name == "matches"
    ]
    namespace = {}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "<unordered-worker>", "exec"), namespace)
    return namespace["matches"]


def test_original_combination_outputs_accept_reordered_results():
    problems = {problem.id: problem for problem in PROBLEMS}
    for problem_id in ("letter-case-variations", "palindrome-partitions"):
        problem = problems[problem_id]
        assert {test.comparator for test in problem.tests} == {"unordered"}
        expected = problem.tests[0].expected
        assert compare(list(reversed(expected)), expected, "unordered")


def test_letter_case_variations_accept_any_outer_order_in_native_and_browser_judges():
    problem = next(problem for problem in PROBLEMS if problem.id == "letter-case-variations")
    expected = problem.tests[0].expected
    reordered = [expected[2], expected[0], expected[3], expected[1]]

    assert compare(reordered, expected, "unordered")
    assert worker_compare()(reordered, expected, "unordered")
    assert not worker_compare()(reordered[:-1], expected, "unordered")
    assert not worker_compare()(reordered + reordered[:1], expected, "unordered")


def test_word_subsets_accept_any_outer_order_without_accepting_missing_words():
    problem = get_catalog()["leetcode-916"]
    assert {test.comparator for test in problem.tests} == {"unordered"}
    expected = problem.tests[0].expected
    assert len(expected) > 1
    assert compare(expected[::-1], expected, "unordered")
    assert worker_compare()(expected[::-1], expected, "unordered")
    assert not compare(expected[:-1], expected, "unordered")


def test_doubled_array_accepts_original_values_in_any_order():
    problem = get_catalog()["leetcode-2007"]
    assert {test.comparator for test in problem.tests} == {"unordered"}
    expected = problem.tests[0].expected
    assert len(expected) > 1
    assert compare(expected[::-1], expected, "unordered")
    assert worker_compare()(expected[::-1], expected, "unordered")
    assert not worker_compare()(expected[:-1], expected, "unordered")


def test_every_reviewed_any_order_import_uses_flexible_comparison():
    for source_id, comparator in ORDER_INSENSITIVE_COMPARATORS.items():
        assert BATCH[source_id]["comparator"] == comparator


def test_unordered_comparison_preserves_content_multiplicity_and_inner_order():
    expected = [[0, 1, 3], [0, 2, 3]]
    assert compare(list(reversed(expected)), expected, "unordered")
    assert not compare([[3, 1, 0], [0, 2, 3]], expected, "unordered")
    assert not compare([[0, 1, 3], [0, 1, 3]], expected, "unordered")


def test_mst_categories_stay_fixed_while_indices_can_reorder():
    expected = [[0, 1], [2, 3, 4, 5]]
    assert compare([[1, 0], [5, 4, 3, 2]], expected, "unordered_rows")
    assert not compare([[2, 3, 4, 5], [0, 1]], expected, "unordered_rows")


def test_only_sequence_semantic_any_order_problem_keeps_exact_comparison():
    assert BATCH[950].get("comparator", "exact") == "exact"
    assert "reveal sequence" in " ".join(BATCH[950]["constraints"]).lower()


def test_packaged_explicit_any_order_contracts_are_not_exact_sequences():
    packaged = {
        path.stem: json.loads(path.read_text())
        for path in (ROOT / "catalog_data" / "problems").glob("*.json")
    }
    exact_exceptions = []
    phrase = re.compile(r"\b(?:in any order|any order|order does not matter|order doesn't matter)\b")
    for line in (ROOT / "catalog_import" / "sources.jsonl").read_text().splitlines():
        source = json.loads(line)
        problem = packaged.get(f"leetcode-{source['source_id']}")
        if not problem or not problem["signature"]["returns"].startswith("list"):
            continue
        source_text = f"{source.get('description_html', '')} {source.get('statement', '')}".lower()
        comparators = {test["comparator"] for test in problem["tests"]}
        if phrase.search(source_text) and comparators == {"exact"}:
            exact_exceptions.append(problem["id"])
    assert exact_exceptions == ["leetcode-950"]


def test_packaged_output_order_promises_use_a_flexible_comparator():
    output_order_phrase = re.compile(
        r"\b(?:return|output|answer|result)\b[^.]{0,100}"
        r"\b(?:in any order|order does not matter|order doesn't matter|arbitrary order)\b",
        re.IGNORECASE,
    )
    missed = []
    for path in (ROOT / "catalog_data" / "problems").glob("*.json"):
        problem = json.loads(path.read_text())
        if not problem["signature"]["returns"].startswith("list"):
            continue
        contract = " ".join([
            problem.get("summary", ""),
            problem.get("statement", ""),
            *problem.get("constraints", []),
        ])
        comparators = {test["comparator"] for test in problem["tests"]}
        if output_order_phrase.search(contract) and comparators == {"exact"}:
            missed.append(problem["id"])

    assert missed == []
