from collections import Counter

from code_practice.content import PROBLEMS
from code_practice.content_oracles import RANDOM_CASES, verify_randomized
from code_practice.content_solutions import SOLUTIONS
from code_practice.validation import validate_problem
from code_practice.validation import content_fingerprint


def test_catalog_has_required_size_topics_and_distribution():
    assert len(PROBLEMS) == 100
    assert len({problem.id for problem in PROBLEMS}) == 100
    assert len({topic for problem in PROBLEMS for topic in problem.topics}) >= 8
    distribution = Counter(
        "easy" if problem.difficulty <= 3 else "medium" if problem.difficulty <= 7 else "advanced"
        for problem in PROBLEMS
    )
    assert distribution == {"easy": 33, "medium": 56, "advanced": 11}


def test_catalog_uses_distinct_callable_questions_and_recursion_progression():
    assert len({problem.signature.name for problem in PROBLEMS}) == 100
    assert len({problem.title for problem in PROBLEMS}) == 100
    assert len({content_fingerprint(problem) for problem in PROBLEMS}) == 100
    assert not any("boundary-lab" in problem.id or "trace-lab" in problem.id or "constraint-sprint" in problem.id for problem in PROBLEMS)
    recursion_difficulties = {problem.difficulty for problem in PROBLEMS if "recursion" in problem.topics}
    assert any(score <= 3 for score in recursion_difficulties)
    assert any(4 <= score <= 7 for score in recursion_difficulties)
    assert any(score >= 8 for score in recursion_difficulties)


def test_every_problem_meets_content_contract():
    for problem in PROBLEMS:
        assert problem.status == "approved"
        assert len([test for test in problem.tests if test.visible]) >= 2
        assert len([test for test in problem.tests if not test.visible]) >= 12
        assert len(problem.hints) == 4
        assert problem.editorial
        assert problem.reference_solution
        assert len(problem.known_wrong_solutions) >= 2
    pair_sum = next(problem for problem in PROBLEMS if problem.id == "pair-sum-indices")
    assert "sample_nums = [2, 7, 11, 15]" in pair_sum.starter_code
    assert 'print("Current result:"' in pair_sum.starter_code


def test_reference_and_known_wrong_solutions():
    for problem in PROBLEMS:
        report = validate_problem(problem)
        assert report["valid"], f"{problem.id}: {report['errors']} {report['referenceFailures']}"
        assert all(report["wrongSolutionsRejected"])


def test_practical_oracles_match_on_500_randomized_inputs_each():
    for function_name in RANDOM_CASES:
        verify_randomized(function_name, SOLUTIONS[function_name], count=500)
