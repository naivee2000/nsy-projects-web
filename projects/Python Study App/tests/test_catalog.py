from collections import Counter

from code_practice.content import PROBLEMS
from code_practice.content_oracles import RANDOM_CASES, verify_randomized
from code_practice.content_solutions import ListNode, SOLUTIONS
from code_practice.validation import run_source, validate_problem
from code_practice.validation import content_fingerprint


def test_catalog_has_required_size_topics_and_distribution():
    assert len(PROBLEMS) == 101
    assert len({problem.id for problem in PROBLEMS}) == 101
    assert len({topic for problem in PROBLEMS for topic in problem.topics}) >= 8
    distribution = Counter(
        "easy" if problem.difficulty <= 3 else "medium" if problem.difficulty <= 7 else "advanced"
        for problem in PROBLEMS
    )
    assert distribution == {"easy": 34, "medium": 56, "advanced": 11}


def test_catalog_uses_distinct_callable_questions_and_recursion_progression():
    assert len({problem.signature.name for problem in PROBLEMS}) == 101
    assert len({problem.title for problem in PROBLEMS}) == 101
    assert len({content_fingerprint(problem) for problem in PROBLEMS}) == 101
    assert not any("boundary-lab" in problem.id or "trace-lab" in problem.id or "constraint-sprint" in problem.id for problem in PROBLEMS)
    recursion_difficulties = {problem.difficulty for problem in PROBLEMS if "recursion" in problem.topics}
    assert any(score <= 3 for score in recursion_difficulties)
    assert any(4 <= score <= 7 for score in recursion_difficulties)
    assert any(score >= 8 for score in recursion_difficulties)


def test_every_problem_meets_content_contract():
    for problem in PROBLEMS:
        assert problem.status == "approved"
        visible_examples = [test for test in problem.tests if test.visible]
        hidden_tests = [test for test in problem.tests if not test.visible]
        assert len(visible_examples) >= 2
        assert len(hidden_tests) >= 12
        assert all(test.explanation and test.explanation != "Visible example" for test in visible_examples)
        assert len({repr(test.arguments) for test in visible_examples}) == len(visible_examples)
        assert len(problem.hints) == 4
        assert problem.editorial
        assert problem.reference_solution
        assert len(problem.known_wrong_solutions) >= 2
    pair_sum = next(problem for problem in PROBLEMS if problem.id == "pair-sum-indices")
    assert "sample_nums = [2, 7, 11, 15]" in pair_sum.starter_code
    assert 'print("Current result:"' in pair_sum.starter_code

    for problem in PROBLEMS:
        adapters = {parameter.adapter for parameter in problem.signature.parameters}
        adapters.add(problem.signature.return_adapter)
        if "listnode" in adapters:
            assert "class ListNode:" in problem.starter_code
        if "treenode" in adapters:
            assert "class TreeNode:" in problem.starter_code


def test_rule_specific_examples_cover_normal_and_contrasting_cases():
    by_id = {problem.id: problem for problem in PROBLEMS}

    pivots = [test for test in by_id["balanced-pivot-index"].tests if test.explanation]
    assert [test.expected for test in pivots] == [3, -1]

    word_patterns = [test for test in by_id["word-pattern-bijection"].tests if test.explanation]
    assert [test.expected for test in word_patterns] == [True, False]

    missing_grid_values = [test for test in by_id["missing-repeated-grid-values"].tests if test.explanation]
    assert [test.expected for test in missing_grid_values] == [[2, 4], [9, 5]]

    brackets = [test for test in by_id["valid-brackets"].tests if test.explanation]
    assert [test.expected for test in brackets] == [True, False]

    merged_lists = [test for test in by_id["merge-sorted-linked-lists"].tests if test.explanation]
    assert [test.expected for test in merged_lists] == [[1, 1, 2, 3, 4, 4], [0]]


def test_linked_list_merge_splices_the_original_nodes():
    first = ListNode(1, ListNode(4))
    second = ListNode(2, ListNode(3))
    original_node_ids = {id(first), id(first.next), id(second), id(second.next)}

    merged = SOLUTIONS["merge_sorted_linked_lists"](first, second)
    merged_node_ids = set()
    values = []
    while merged:
        merged_node_ids.add(id(merged))
        values.append(merged.val)
        merged = merged.next

    assert values == [1, 2, 3, 4]
    assert merged_node_ids == original_node_ids


def test_displayed_support_classes_are_used_for_adapted_inputs():
    by_id = {problem.id: problem for problem in PROBLEMS}
    linked = by_id["reverse-linked-list"]
    linked_source = linked.starter_code.replace(
        "    # Write your solution here.\n    pass\n",
        "    assert isinstance(head, ListNode)\n    return head\n",
    )
    linked_case = next(test for test in linked.tests if test.arguments == [[7]])
    assert run_source(linked_source, linked, linked_case) == (True, None)

    tree = by_id["tree-max-depth"]
    tree_source = tree.starter_code.replace(
        "    # Write your solution here.\n    pass\n",
        "    assert isinstance(root, TreeNode)\n    return 1\n",
    )
    tree_case = next(test for test in tree.tests if test.arguments == [[1]])
    assert run_source(tree_source, tree, tree_case) == (True, None)


def test_syntax_only_easy_exercises_are_replaced_by_reasoning_patterns():
    ids = {problem.id for problem in PROBLEMS}
    removed = {
        "array-range-span",
        "reverse-word-order",
        "longest-word-length",
        "count-negative-cells",
        "boundary-land-cells",
        "linked-list-length",
        "recursive-sum-to-n",
    }
    replacements = {
        "balanced-pivot-index",
        "word-pattern-bijection",
        "formable-word-total",
        "missing-repeated-grid-values",
        "flood-fill-region",
        "deduplicate-sorted-linked-list",
        "recursive-step-combinations",
    }
    assert ids.isdisjoint(removed)
    assert replacements <= ids
    upgraded = [next(problem for problem in PROBLEMS if problem.id == problem_id) for problem_id in replacements]
    assert all(problem.difficulty == 3 for problem in upgraded)
    assert all(not problem.statement.startswith(problem.summary) for problem in upgraded)
    assert all(problem.constraints != ["Inputs follow the declared Python and JSON-compatible types.", "Return a deterministic result for every valid input."] for problem in upgraded)


def test_reference_and_known_wrong_solutions():
    for problem in PROBLEMS:
        report = validate_problem(problem)
        assert report["valid"], f"{problem.id}: {report['errors']} {report['referenceFailures']}"
        assert all(report["wrongSolutionsRejected"])


def test_practical_oracles_match_on_500_randomized_inputs_each():
    for function_name in RANDOM_CASES:
        verify_randomized(function_name, SOLUTIONS[function_name], count=500)
