from itertools import product
import json
from pathlib import Path
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_031 import (
    BATCH, STRICT_WIGGLE, DISTINCT_WINDOW, POWER_FOUR, INTEGER_BREAK,
    REVERSE_CHARACTERS, REVERSE_VOWELS, strict_arrangement, distinct_window_oracle,
    power_four_oracle, integer_break_oracle, reverse_vowels_oracle,
)
from code_practice.schemas import ProblemDefinition
from code_practice.validation import compare, run_source


def function(source,name):
    namespace = {}
    exec(compile(source,f'<{name}>','exec'),namespace)
    return namespace[name]


def test_strict_and_nonstrict_wiggles_have_different_contracts():
    expected = [2,3,1,2]
    assert compare([1,2,2,3],expected,'wiggle')
    assert not compare([1,2,2,3],expected,'strict_wiggle')
    assert compare([2,3,1,2],expected,'strict_wiggle')
    assert compare([1,2,1,3,2,3],[2,3,1,3,1,2],'strict_wiggle')
    for wrong in ([1,3,1,3,1,3], [True,2,1,3,2,3], [1.0,2,1,3,2,3], [[1],2,1,3,2,3], None):
        assert not compare(wrong,[2,3,1,3,1,2],'strict_wiggle')


@pytest.mark.parametrize('change',['order','multiset','boolean','input_type','mixed','result_mode'])
def test_schema_blocks_invalid_strict_wiggle_fixtures(change):
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root/'catalog_import/candidates/leetcode-324.json').read_text())
    case = payload['tests'][0]
    if change == 'order':
        case['expected'] = sorted(case['expected'])
    elif change == 'multiset':
        case['expected'] = [1,6,1,5,1,5]
    elif change == 'boolean':
        case['expected'][0] = True
    elif change == 'input_type':
        case['arguments'][0][0] = [1]
    elif change == 'mixed':
        case['comparator'] = 'wiggle'
    else:
        payload['signature']['result_mode'] = 'return'
        payload['signature']['mutated_parameter'] = None
    with pytest.raises(ValueError):
        ProblemDefinition.model_validate(payload)


def test_strict_wiggle_reference_matches_all_short_feasible_multisets():
    solve = function(STRICT_WIGGLE,'wiggle_sort_strict')
    for length in range(1,8):
        for values in product(range(3),repeat=length):
            expected = strict_arrangement(values)
            if expected is None:
                continue
            original = list(values)
            assert solve(original) is None
            assert compare(original,expected,'strict_wiggle')


def test_window_matches_all_short_strings_including_zero_and_oversized_limits():
    solve = function(DISTINCT_WINDOW,'longest_k_distinct_substring')
    for length in range(1,7):
        for text in map(''.join,product('abc',repeat=length)):
            for k in range(5):
                assert solve(text,k) == distinct_window_oracle([text,k])


def test_power_four_and_integer_break_cover_their_complete_critical_domains():
    power = function(POWER_FOUR,'is_power_of_four')
    for exponent in range(31):
        for n in (2**exponent-1,2**exponent,2**exponent+1,-2**exponent):
            assert power(n) == power_four_oracle([n])
    split = function(INTEGER_BREAK,'max_integer_break_product')
    for n in range(2,59):
        assert split(n) == integer_break_oracle([n])


def test_character_and_vowel_reversals_preserve_the_correct_positions():
    reverse = function(REVERSE_CHARACTERS,'reverse_characters')
    vowels = function(REVERSE_VOWELS,'reverse_vowels')
    for length in range(1,7):
        for values in product('aEb!',repeat=length):
            actual = list(values)
            assert reverse(actual) is None
            assert actual == list(values[::-1])
            text = ''.join(values)
            result = vowels(text)
            assert result == reverse_vowels_oracle([text])
            assert all(result[i] == letter for i,letter in enumerate(text) if letter not in 'aeiouAEIOU')


def test_batch_31_published_references_and_incorrect_solutions():
    for source_id in BATCH:
        problem = get_catalog()[f'leetcode-{source_id}']
        assert problem.status == 'approved'
        assert len(problem.hints)==4 and problem.editorial
        assert sum(t.visible for t in problem.tests)>=2 and sum(not t.visible for t in problem.tests)>=12
        assert all(run_source(problem.reference_solution,problem,t)[0] for t in problem.tests)
        for wrong in problem.known_wrong_solutions:
            assert any(run_source(wrong,problem,t)==(False,None) for t in problem.tests)


def test_batch_31_inputs_meet_source_constraints():
    for source_id,spec in BATCH.items():
        rng = random.Random(4047+source_id)
        inputs = ([args for args,_ in spec['examples']] + spec['boundaries']
                  + [args for args,_ in spec['stress']]
                  + [spec['generator'](rng) for _ in range(500)])
        for args in inputs:
            if source_id == 324:
                assert 1 <= len(args[0]) <= 50000 and all(type(v) is int and 0 <= v <= 5000 for v in args[0])
                if len(args[0])<=8:
                    assert strict_arrangement(args[0]) is not None
            elif source_id == 340:
                assert 1 <= len(args[0]) <= 50000 and 0 <= args[1] <= 50
            elif source_id == 342:
                assert -(2**31) <= args[0] < 2**31
            elif source_id == 343:
                assert 2 <= args[0] <= 58
            elif source_id == 344:
                assert 1 <= len(args[0]) <= 100000
                assert all(len(c)==1 and 32 <= ord(c) <= 126 for c in args[0])
            elif source_id == 345:
                assert 1 <= len(args[0]) <= 300000 and all(32 <= ord(c) <= 126 for c in args[0])
