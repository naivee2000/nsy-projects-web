import ast
from itertools import combinations, product
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_022 import BATCH
from code_practice.learning import prerequisites_met, review_focus_boost


def reference(pid):
    namespace = {}
    exec(BATCH[pid]["reference"], namespace)
    return namespace[BATCH[pid]["name"]]


def cases(pid):
    spec = BATCH[pid]
    rng = random.Random(4047 + pid)
    return ([args for args, _ in spec["examples"]] + spec["boundaries"]
            + [args for args, _ in spec["stress"]]
            + [spec["generator"](rng) for _ in range(500)])


def test_batch_twenty_two_inputs_match_retained_source_contracts():
    for pid in BATCH:
        for args in cases(pid):
            if pid == 219:
                nums, limit = args
                assert 1 <= len(nums) <= 100000 and 0 <= limit <= 100000
                assert all(type(value) is int and -10**9 <= value <= 10**9 for value in nums)
            elif pid == 220:
                nums, index_limit, value_limit = args
                assert 2 <= len(nums) <= 100000 and 1 <= index_limit <= len(nums)
                assert 0 <= value_limit <= 10**9
                assert all(type(value) is int and -10**9 <= value <= 10**9 for value in nums)
            elif pid == 224:
                assert 1 <= len(args[0]) <= 300000 and set(args[0]) <= set("0123456789+-() ")
            elif pid == 227:
                assert 1 <= len(args[0]) <= 300000 and set(args[0]) <= set("0123456789+-*/ ")
            elif pid == 228:
                nums = args[0]
                assert len(nums) <= 20 and nums == sorted(set(nums))
                assert all(-2**31 <= value <= 2**31 - 1 for value in nums)
            elif pid == 229:
                assert 1 <= len(args[0]) <= 50000
                assert all(-10**9 <= value <= 10**9 for value in args[0])
            elif pid == 233:
                assert type(args[0]) is int and 0 <= args[0] <= 10**9
            elif pid == 238:
                assert 2 <= len(args[0]) <= 100000
                assert all(type(value) is int and -30 <= value <= 30 for value in args[0])
            elif pid == 240:
                matrix, target = args
                assert 1 <= len(matrix) <= 300 and 1 <= len(matrix[0]) <= 300
                assert all(len(row) == len(matrix[0]) for row in matrix)
                assert all(row == sorted(row) for row in matrix)
                assert all(matrix[row][column] <= matrix[row + 1][column]
                           for row in range(len(matrix) - 1) for column in range(len(matrix[0])))
                assert -10**9 <= target <= 10**9
            else:
                expression = args[0]
                assert 1 <= len(expression) <= 20 and set(expression) <= set("0123456789+-*")


def test_nearby_duplicate_exhausts_index_boundaries():
    solve = reference(219)
    for length in range(1, 7):
        for nums in product(range(3), repeat=length):
            for limit in range(length + 1):
                expected = any(nums[i] == nums[j] and j - i <= limit
                               for i in range(length) for j in range(i + 1, length))
                assert solve(list(nums), limit) == expected
    assert not solve([1, 1], 0)
    assert solve([1, 2, 3, 1], 3)
    assert not solve([1, 2, 3, 1], 2)


def test_nearby_almost_duplicate_exhausts_negative_buckets_and_both_limits():
    solve = reference(220)
    for length in range(2, 6):
        for nums in product(range(-2, 3), repeat=length):
            for index_limit in range(1, length + 1):
                for value_limit in range(4):
                    expected = any(j - i <= index_limit and abs(nums[i] - nums[j]) <= value_limit
                                   for i in range(length) for j in range(i + 1, length))
                    assert solve(list(nums), index_limit, value_limit) == expected
    assert solve([-3, -2], 1, 1)
    assert solve([1, 2], 1, 1)
    assert not solve([0, 10, 0], 1, 0)


def test_basic_calculator_handles_unary_minus_grouping_and_source_scale_depth():
    solve = reference(224)
    for left, middle, right in product(range(5), repeat=3):
        expressions = {
            f"{left}-({middle}-{right})": left - (middle - right),
            f"-({left}+({middle}-{right}))": -(left + (middle - right)),
            f"({left}-{middle})+({right}-{left})": (left - middle) + (right - left),
        }
        for expression, expected in expressions.items():
            assert solve(expression) == expected == BATCH[224]["oracle"]([expression])
    assert solve("1-(-2)") == 3
    assert solve("(" * 100000 + "1" + ")" * 100000) == 1
    assert solve("1+" * 149999 + "1") == 150000


def test_calculator_two_applies_precedence_and_truncates_negative_terms_toward_zero():
    solve = reference(227)
    for numbers in product(range(1, 5), repeat=3):
        for operators in product("+-*/", repeat=2):
            expression = str(numbers[0]) + operators[0] + str(numbers[1]) + operators[1] + str(numbers[2])
            assert solve(expression) == BATCH[227]["oracle"]([expression])
    assert solve("1-7/2") == -2
    assert solve("0-7/2") == -3
    assert solve("2+3*4") == 14
    assert solve("1+" * 149999 + "1") == 150000


def test_summary_ranges_exhausts_small_sorted_subsets_and_formats_singletons():
    solve = reference(228)
    values = list(range(-3, 4))
    for size in range(len(values) + 1):
        for chosen in combinations(values, size):
            assert solve(list(chosen)) == BATCH[228]["oracle"]([list(chosen)])
    assert solve([]) == []
    assert solve([7]) == ["7"]
    assert solve([-2, -1, 1, 2]) == ["-2->-1", "1->2"]


def test_majority_over_third_exhausts_small_arrays_and_preserves_two_answers():
    solve = reference(229)
    for length in range(1, 8):
        for nums in product(range(3), repeat=length):
            expected = BATCH[229]["oracle"]([list(nums)])
            assert sorted(solve(list(nums))) == sorted(expected)
    assert sorted(solve([1, 2])) == [1, 2]
    assert sorted(solve([1, 1, 2, 2, 3])) == [1, 2]
    assert solve([1, 2, 3]) == []


def test_digit_one_matches_direct_enumeration_and_full_boundary_derivation():
    solve = reference(233)
    running = 0
    for value in range(10001):
        running += str(value).count("1")
        assert solve(value) == running
    # Across 000000000..999999999, each of nine positions is 1 exactly 10^8
    # times. The endpoint 1000000000 contributes one additional occurrence.
    assert solve(10**9) == 9 * 10**8 + 1


def test_product_except_self_exhausts_zeros_and_uses_no_division_operator():
    solve = reference(238)
    for length in range(2, 7):
        for nums in product(range(-2, 3), repeat=length):
            assert solve(list(nums)) == BATCH[238]["oracle"]([list(nums)])
    operators = [node for node in ast.walk(ast.parse(BATCH[238]["reference"]))
                 if isinstance(node, (ast.Div, ast.FloorDiv))]
    assert not operators
    assert solve([0, 2, 3]) == [6, 0, 0]
    assert solve([0, 0, 3]) == [0, 0, 0]


def test_matrix_search_exhausts_monotone_constructions_and_thin_shapes():
    solve = reference(240)
    bases = list(product(range(3), repeat=3))
    ordered = [values for values in bases if values[0] <= values[1] <= values[2]]
    for rows in ordered:
        for columns in ordered:
            matrix = [[row + column for column in columns] for row in rows]
            for target in range(-1, 6):
                assert solve(matrix, target) == any(target in row for row in matrix)
    assert solve([[1, 4, 7]], 7)
    assert solve([[1], [2], [3]], 2)
    assert not solve([[1, 4], [2, 5]], 3)


def test_parenthesized_results_preserve_catalan_multiplicity_and_recur():
    solve = reference(241)
    for numbers in product(range(3), repeat=4):
        for operators in product("+-*", repeat=3):
            expression = "".join(str(numbers[i]) + operators[i] for i in range(3)) + str(numbers[3])
            assert sorted(solve(expression)) == sorted(BATCH[241]["oracle"]([expression]))
            assert len(solve(expression)) == 5
    repeated = solve("1*1*1*1*1*1*1*1*1*1")
    assert repeated == [1] * 4862
    problem = get_catalog()["leetcode-241"]
    assert review_focus_boost(problem) >= 50


def test_hard_prerequisites_are_reachable_and_weak_topics_are_prioritized():
    catalog = get_catalog()
    for pid in (220, 224, 233):
        problem = catalog[f"leetcode-{pid}"]
        assert problem.difficulty >= 8
        low = {topic: 69 for topic in problem.prerequisites}
        ready = {topic: 70 for topic in problem.prerequisites}
        assert not prerequisites_met(problem, low)
        assert prerequisites_met(problem, ready)
        assert all(any(candidate.difficulty < 8 and topic in candidate.topics
                       for candidate in catalog.values()) for topic in problem.prerequisites)
    assert review_focus_boost(catalog["leetcode-224"]) >= 50
    assert review_focus_boost(catalog["leetcode-240"]) >= 60
