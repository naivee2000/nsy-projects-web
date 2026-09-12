from itertools import combinations_with_replacement, product
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_032 import (
    BATCH, INTERSECTION, MULTISET, UNLOCK, ENVELOPES, REFLECTION, TRANSFORMED,
    BOMB, JUG, LINKED_PLUS, RANGE, intersection_oracle, multiset_oracle,
    pattern_counts, unlock_oracle, envelopes_oracle, reflection_oracle,
    transformed_oracle, bomb_oracle, jug_oracle, range_oracle,
)
from code_practice.validation import ListNode, run_source


def function(source, name):
    namespace = {'ListNode': ListNode}
    exec(compile(source, f'<{name}>', 'exec'), namespace)
    return namespace[name]


def test_batch_32_has_published_content_and_algorithmic_rejection_evidence():
    for source_id in BATCH:
        problem = get_catalog()[f'leetcode-{source_id}']
        assert problem.status == 'approved'
        assert sum(case.visible for case in problem.tests) >= 2
        assert sum(not case.visible for case in problem.tests) >= 12
        assert all(case.explanation for case in problem.tests if case.visible)
        assert len(problem.hints) == 4 and problem.editorial
        assert all(run_source(problem.reference_solution, problem, case)[0] for case in problem.tests)
        for wrong in problem.known_wrong_solutions:
            assert any(run_source(wrong, problem, case) == (False, None) for case in problem.tests)
    linked = get_catalog()['leetcode-369']
    assert linked.signature.parameters[0].adapter == 'listnode'
    assert linked.signature.return_adapter == 'listnode'
    assert 'class ListNode:' in linked.starter_code
    assert 'linked-lists' in linked.topics
    assert 'recursion' in get_catalog()['leetcode-351'].topics
    assert get_catalog()['leetcode-354'].prerequisites == ['binary-search', 'dynamic-programming']


def test_both_intersection_contracts_match_all_short_ternary_arrays():
    unique = function(INTERSECTION, 'unique_intersection')
    multiple = function(MULTISET, 'multiset_intersection')
    arrays = [list(values) for length in range(1, 4) for values in product(range(3), repeat=length)]
    for left in arrays:
        for right in arrays:
            assert sorted(unique(left, right)) == intersection_oracle([left, right])
            assert sorted(multiple(left, right)) == sorted(multiset_oracle([left, right]))
    assert unique([2,2], [2,2]) == [2]
    assert multiple([2,2], [2,2]) == [2,2]


def test_unlock_exhaustive_permutations_and_all_81_length_ranges():
    solve = function(UNLOCK, 'count_unlock_patterns')
    assert pattern_counts() == (0, 9, 56, 320, 1624, 7152, 26016, 72912, 140704, 140704)
    assert solve(4, 9) == 389112
    for m in range(1, 10):
        for n in range(1, 10):
            assert solve(m, n) == unlock_oracle([m, n])
    problem = get_catalog()['leetcode-351']
    assert {tuple(test.arguments) for test in problem.tests} == set(product(range(1,10), repeat=2))


def test_envelope_reduction_matches_all_small_dimension_tuples():
    solve = function(ENVELOPES, 'max_nested_envelopes')
    choices = list(product(range(1,4), repeat=2))
    for length in range(1,5):
        for envelopes in product(choices, repeat=length):
            assert solve(envelopes) == envelopes_oracle([envelopes])
    assert solve([[3,2], [2,3]]) == 1  # Rotation is not allowed.
    assert solve([[1,1], [1,2], [2,2], [2,3]]) == 2


def test_reflection_checks_y_coordinates_half_integer_axes_and_set_semantics():
    solve = function(REFLECTION, 'has_vertical_reflection')
    points = list(product(range(3), range(2)))
    for length in range(1,6):
        for values in combinations_with_replacement(points, length):
            assert solve(values) == reflection_oracle([values])
    assert solve([[0,1], [1,1]])
    assert solve([[0,1], [2,1], [2,1]])
    assert not solve([[0,0], [2,1]])


def test_quadratic_endpoint_merge_covers_convex_concave_linear_and_constant():
    solve = function(TRANSFORMED, 'sort_transformed_array')
    for length in range(1,5):
        for values in combinations_with_replacement(range(-2,3), length):
            for a, b, c in product(range(-2,3), repeat=3):
                assert solve(values,a,b,c) == transformed_oracle([values,a,b,c])


def test_bomb_segment_counts_match_all_19683_three_by_three_grids():
    solve = function(BOMB, 'max_bomb_enemies')
    for cells in product('0EW', repeat=9):
        grid = [list(cells[i:i+3]) for i in (0,3,6)]
        assert solve(grid) == bomb_oracle([grid])
    assert solve([list('0EE')]) == 2  # Enemies do not stop a ray.
    assert solve([list('0EWE')]) == 1  # Walls do stop it.
    assert solve([list('EEE')]) == 0  # No legal placement.


def test_gcd_characterization_matches_all_small_jug_state_graphs():
    solve = function(JUG, 'can_measure_water')
    for x in range(1,13):
        for y in range(1,13):
            for target in range(1,31):
                assert solve(x,y,target) == jug_oracle([x,y,target])


def test_linked_carry_matches_every_integer_through_999_and_100_digit_overflow():
    solve = function(LINKED_PLUS, 'plus_one_linked_list')
    for digits in [*map(str, range(1000)), '9'*100]:
        head = None
        for digit in reversed(digits):
            head = ListNode(int(digit), head)
        result, actual = solve(head), []
        while result:
            actual.append(str(result.val))
            result = result.next
        assert ''.join(actual) == str(int(digits)+1)


def test_difference_array_matches_all_pairs_of_small_inclusive_updates():
    solve = function(RANGE, 'apply_range_additions')
    for length in range(1,5):
        choices = [[start,end,inc] for start in range(length)
                   for end in range(start,length) for inc in (-1,0,1)]
        assert solve(length, []) == [0]*length
        for first, second in product(choices, repeat=2):
            assert solve(length,[first,second]) == range_oracle([length,[first,second]])


def test_batch_32_generated_and_stress_inputs_follow_source_domains():
    for source_id, spec in BATCH.items():
        rng = random.Random(4047+source_id)
        inputs = ([args for args,_ in spec['examples']] + spec['boundaries']
                  + [args for args,_ in spec['stress']]
                  + [spec['generator'](rng) for _ in range(500)])
        for args in inputs:
            if source_id in (349,350):
                assert all(1 <= len(values) <= 1000 and all(0 <= x <= 1000 for x in values) for values in args)
            elif source_id == 351:
                assert all(1 <= value <= 9 for value in args)
            elif source_id == 354:
                assert 1 <= len(args[0]) <= 100000
                assert all(len(pair)==2 and all(1 <= x <= 100000 for x in pair) for pair in args[0])
            elif source_id == 356:
                assert 1 <= len(args[0]) <= 10000
                assert all(len(pair)==2 and all(-100000000 <= x <= 100000000 for x in pair) for pair in args[0])
            elif source_id == 360:
                nums, a, b, c = args
                assert 1 <= len(nums) <= 200 and nums == sorted(nums)
                assert all(-100 <= x <= 100 for x in [*nums,a,b,c])
            elif source_id == 361:
                grid = args[0]
                assert 1 <= len(grid) <= 500 and 1 <= len(grid[0]) <= 500
                assert all(len(row)==len(grid[0]) and set(row) <= set('0EW') for row in grid)
            elif source_id == 365:
                assert all(1 <= x <= 1000 for x in args)
            elif source_id == 369:
                digits = args[0]
                assert 1 <= len(digits) <= 100 and all(0 <= x <= 9 for x in digits)
                assert len(digits)==1 or digits[0] != 0
            elif source_id == 370:
                length, updates = args
                assert 1 <= length <= 100000 and len(updates) <= 10000
                assert all(0 <= start <= end < length and -1000 <= inc <= 1000 for start,end,inc in updates)
