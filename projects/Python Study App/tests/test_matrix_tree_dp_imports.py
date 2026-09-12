from functools import lru_cache
from itertools import combinations_with_replacement, product
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_002 import flatten, positions
from code_practice.import_batch_029 import (
    BATCH, WORD_PRODUCT, ABBREVIATIONS, POWER_THREE, RANGE_SUM, MATRIX_PATH,
    PATCHES, SERIALIZATION, LARGEST_BST, TREE_ROBBER,
    word_product_oracle, abbreviation_oracle, power_three_oracle,
    range_sum_oracle, increasing_path_oracle, patch_oracle,
    serialization_oracle, largest_bst_oracle, tree_robber_oracle,
)
from code_practice.validation import _treenode, run_source


def function(source, name):
    namespace = {}
    exec(compile(source, f'<{name}>', 'exec'), namespace)
    return namespace[name]


def test_batch_29_is_published_with_complete_content_and_wrong_answer_evidence():
    for source_id in BATCH:
        problem = get_catalog()[f'leetcode-{source_id}']
        assert problem.status == 'approved'
        assert sum(case.visible for case in problem.tests) >= 2
        assert sum(not case.visible for case in problem.tests) >= 12
        assert len(problem.hints) == 4 and problem.editorial
        assert all(case.explanation for case in problem.tests if case.visible)
        assert all(run_source(problem.reference_solution, problem, case)[0] for case in problem.tests)
        for wrong in problem.known_wrong_solutions:
            assert any(run_source(wrong, problem, case) == (False, None) for case in problem.tests)


def test_word_masks_preserve_full_lengths_across_duplicate_masks():
    solve = function(WORD_PRODUCT, 'max_word_length_product')
    for words in combinations_with_replacement(('a','aa','b','bb','ab','bc','ccc'), 4):
        assert solve(words) == word_product_oracle([words])


def test_abbreviations_cover_every_keep_skip_choice_with_unique_outputs():
    solve = function(ABBREVIATIONS, 'generalized_abbreviations')
    for length in range(1, 7):
        for word in map(''.join, product('ab', repeat=length)):
            result = solve(word)
            assert len(result) == len(set(result)) == 2**length
            assert sorted(result) == abbreviation_oracle([word])
    assert '15' in solve('abcdefghijklmno')


def test_power_of_three_at_every_representable_power_and_neighbor():
    solve = function(POWER_THREE, 'is_power_of_three')
    for exponent in range(20):
        for number in (3**exponent-1, 3**exponent, 3**exponent+1, -(3**exponent)):
            assert solve(number) == power_three_oracle([number])


def test_range_count_matches_all_short_signed_arrays_at_inclusive_bounds():
    solve = function(RANGE_SUM, 'count_range_sum')
    for length in range(1, 7):
        for nums in map(list, product((-1,0,1), repeat=length)):
            for lower, upper in ((-2,-1),(-1,-1),(-1,1),(0,0),(0,2),(1,1)):
                assert solve(nums, lower, upper) == range_sum_oracle([nums,lower,upper])


def test_matrix_path_matches_every_small_grid_including_equal_values():
    solve = function(MATRIX_PATH, 'longest_increasing_matrix_path')
    for cells in product(range(3), repeat=6):
        grid = [list(cells[:3]),list(cells[3:])]
        assert solve(grid) == increasing_path_oracle([grid])


def test_patching_matches_shortest_search_over_all_possible_added_values():
    solve = function(PATCHES, 'min_patches')
    for length in range(1, 5):
        for nums in combinations_with_replacement(range(1,6), length):
            for n in range(1,11):
                assert solve(nums,n) == patch_oracle([nums,n])


def test_serialization_slots_match_full_subtree_reduction_on_all_short_token_sequences():
    solve = function(SERIALIZATION, 'valid_preorder_serialization')
    for length in range(1, 10):
        for tokens in product(('#','1'), repeat=length):
            text = ','.join(tokens)
            assert solve(text) == serialization_oracle([text])


@lru_cache(None)
def shapes(size):
    if size == 0:
        return (None,)
    return tuple((left,right) for left_size in range(size)
                 for left in shapes(left_size) for right in shapes(size-left_size-1))


def filled_shape(shape, values):
    mapping, iterator = {}, iter(values)
    def visit(part, path):
        if part is not None:
            mapping[path] = next(iterator)
            visit(part[0], path+(0,))
            visit(part[1], path+(1,))
    visit(shape, ())
    return flatten(mapping)


def test_tree_dynamic_programs_match_all_small_shapes_and_value_assignments():
    bst = function(LARGEST_BST, 'largest_bst_subtree')
    robber = function(TREE_ROBBER, 'rob_tree')
    assert bst(None) == 0
    for size in range(1, 6):
        for shape in shapes(size):
            for values in product(range(3), repeat=size):
                tree = filled_shape(shape, values)
                root = _treenode(tree)
                assert bst(root) == largest_bst_oracle([tree])
                assert robber(root) == tree_robber_oracle([tree])


def test_batch_29_inputs_obey_source_domains_and_large_result_bounds():
    for source_id, spec in BATCH.items():
        rng = random.Random(4047 + source_id)
        inputs = ([args for args,_ in spec['examples']] + spec['boundaries']
                  + [args for args,_ in spec['stress']]
                  + [spec['generator'](rng) for _ in range(500)])
        for args in inputs:
            if source_id == 318:
                assert 2 <= len(args[0]) <= 1000
                assert all(1 <= len(word) <= 1000 and set(word) <= set('abcdefghijklmnopqrstuvwxyz') for word in args[0])
            elif source_id == 320:
                assert 1 <= len(args[0]) <= 15 and set(args[0]) <= set('abcdefghijklmnopqrstuvwxyz')
            elif source_id == 326:
                assert -(2**31) <= args[0] < 2**31
            elif source_id == 327:
                nums,lo,hi = args
                assert 1 <= len(nums) <= 100000 and -100000 <= lo <= hi <= 100000
                assert all(-(2**31) <= value < 2**31 for value in nums)
                if len(nums) <= 30:
                    assert range_sum_oracle(args) < 2**31
            elif source_id == 329:
                grid = args[0]
                assert 1 <= len(grid) <= 200 and 1 <= len(grid[0]) <= 200
                assert all(len(row)==len(grid[0]) and all(0 <= v < 2**31 for v in row) for row in grid)
            elif source_id == 330:
                nums,n = args
                assert 1 <= len(nums) <= 1000 and 1 <= n < 2**31
                assert nums == sorted(nums) and all(1 <= v <= 10000 for v in nums)
            elif source_id == 331:
                assert 1 <= len(args[0]) <= 10000
                assert all(token=='#' or (token.isdigit() and 0 <= int(token) <= 100) for token in args[0].split(','))
            elif source_id in (333,337):
                values = [value for value in args[0] if value is not None]
                assert (0 if source_id==333 else 1) <= len(values) <= 10000
                assert all((-10000 if source_id==333 else 0) <= value <= 10000 for value in values)
        if source_id == 327:
            assert all(0 <= expected < 2**31 for _,expected in spec['stress'])
