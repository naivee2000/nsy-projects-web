from collections import Counter
from itertools import combinations, product
from math import prod
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_023 import BATCH, STROBO_15_COUNT
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


def test_batch_twenty_three_inputs_match_retained_source_contracts():
    for pid in BATCH:
        for args in cases(pid):
            if pid in (243, 245):
                words, first, second = args
                limit = 30000 if pid == 243 else 100000
                assert 1 <= len(words) <= limit
                assert all(1 <= len(word) <= 10 and word.islower() for word in words)
                assert first in words and second in words
                if pid == 243:
                    assert len(words) >= 2 and first != second
                elif first == second:
                    assert words.count(first) >= 2
            elif pid == 246:
                value = args[0]
                assert 1 <= len(value) <= 50 and value.isdigit()
                assert value == "0" or value[0] != "0"
            elif pid == 247:
                assert type(args[0]) is int and 1 <= args[0] <= 14
            elif pid == 248:
                low, high = args
                assert 1 <= len(low) <= 15 and 1 <= len(high) <= 15
                assert (low == "0" or low[0] != "0") and (high == "0" or high[0] != "0")
                assert len(low) < len(high) or len(low) == len(high) and low <= high
            elif pid == 249:
                assert 1 <= len(args[0]) <= 200
                assert all(1 <= len(text) <= 50 and text.islower() for text in args[0])
            elif pid == 252:
                assert len(args[0]) <= 10000
                assert all(len(interval) == 2 and 0 <= interval[0] < interval[1] <= 10**6
                           for interval in args[0])
            elif pid == 254:
                assert type(args[0]) is int and 1 <= args[0] <= 10**7
            elif pid == 256:
                assert 1 <= len(args[0]) <= 100
                assert all(len(row) == 3 and all(type(cost) is int and 1 <= cost <= 20 for cost in row)
                           for row in args[0])
            else:
                assert type(args[0]) is int and 0 <= args[0] <= 2**31 - 1


def test_distinct_word_distance_exhausts_small_occurrence_layouts():
    solve = reference(243)
    for length in range(2, 8):
        for words in product("abc", repeat=length):
            for first, second in (("a", "b"), ("a", "c"), ("b", "c")):
                if first in words and second in words:
                    expected = min(abs(i - j) for i, word in enumerate(words) if word == first
                                   for j, other in enumerate(words) if other == second)
                    assert solve(list(words), first, second) == expected
    assert solve(["a", "x", "a", "b"], "a", "b") == 1


def test_same_word_distance_uses_two_individual_occurrences():
    solve = reference(245)
    for length in range(2, 8):
        for words in product("abc", repeat=length):
            for first, second in product("abc", repeat=2):
                if first not in words or second not in words:
                    continue
                if first == second and words.count(first) < 2:
                    continue
                assert solve(list(words), first, second) == BATCH[245]["oracle"]([list(words), first, second])
    assert solve(["a", "x", "a"], "a", "a") == 2
    assert solve(["a", "a"], "a", "a") == 1


def test_strobogrammatic_predicate_exhausts_short_canonical_digit_strings():
    solve = reference(246)
    rotated = {"0": "0", "1": "1", "6": "9", "8": "8", "9": "6"}
    for length in range(1, 5):
        for digits in product("0123456789", repeat=length):
            if length > 1 and digits[0] == "0":
                continue
            value = "".join(digits)
            expected = all(char in rotated for char in value) and "".join(
                rotated[char] for char in reversed(value)) == value
            assert solve(value) == expected


def expected_strobogrammatic_count(length):
    if length == 1:
        return 3
    return 4 * 5 ** ((length - 2) // 2) * (3 if length % 2 else 1)


def test_strobogrammatic_generation_covers_every_source_length_without_leading_zeroes():
    solve = reference(247)
    predicate = reference(246)
    for length in range(1, 15):
        actual = solve(length)
        assert len(actual) == expected_strobogrammatic_count(length)
        assert len(actual) == len(set(actual))
        assert all(len(value) == length and (length == 1 or value[0] != "0") and predicate(value)
                   for value in actual)
        assert sorted(actual) == sorted(BATCH[247]["oracle"]([length]))


def test_strobogrammatic_range_matches_direct_counts_and_full_fifteen_digit_domain():
    solve = reference(248)
    predicate = reference(246)
    prefix = [0]
    for value in range(10001):
        prefix.append(prefix[-1] + predicate(str(value)))
    for low in range(0, 10001, 37):
        for high in (low, min(10000, low + 1), min(10000, low + 137)):
            expected = prefix[high + 1] - prefix[low]
            assert solve(str(low), str(high)) == expected
    assert STROBO_15_COUNT == sum(expected_strobogrammatic_count(length) for length in range(1, 16))
    assert solve("0", "999999999999999") == STROBO_15_COUNT == 312499


def shifted_equivalent(first, second):
    return len(first) == len(second) and len({(ord(b) - ord(a)) % 26 for a, b in zip(first, second)}) == 1


def test_shifted_groups_preserve_wraparound_and_duplicate_occurrences():
    solve = reference(249)
    universe = ["a", "z", "ab", "bc", "az", "ba", "aa", "bb", "ace"]
    for length in range(1, 5):
        for strings in product(universe[:6], repeat=length):
            actual = solve(list(strings))
            flattened = [value for group in actual for value in group]
            assert Counter(flattened) == Counter(strings)
            assert all(all(shifted_equivalent(group[0], value) for value in group) for group in actual)
            assert all(not shifted_equivalent(left[0], right[0])
                       for index, left in enumerate(actual) for right in actual[index + 1:])
    assert sorted(map(sorted, solve(["az", "ba", "a", "z", "a"]))) == [["a", "a", "z"], ["az", "ba"]]


def test_meeting_rooms_exhausts_half_open_interval_subsets_and_input_orders():
    solve = reference(252)
    intervals = [[start, end] for start in range(4) for end in range(start + 1, 5)]
    for size in range(5):
        for chosen in combinations(intervals, size):
            expected = all(max(a[0], b[0]) >= min(a[1], b[1])
                           for index, a in enumerate(chosen) for b in chosen[index + 1:])
            assert solve(list(reversed(chosen))) == expected
    assert solve([[0, 1], [1, 2]])
    assert not solve([[2, 3], [0, 10]])


def test_factor_combinations_match_brute_non_decreasing_products():
    solve = reference(254)
    for number in range(1, 201):
        actual = solve(number)
        expected = BATCH[254]["oracle"]([number])
        assert sorted(map(tuple, actual)) == sorted(map(tuple, expected))
        assert len(actual) == len({tuple(row) for row in actual})
        assert all(row == sorted(row) and len(row) >= 2 and prod(row) == number for row in actual)
    assert solve(999983) == []


def test_paint_house_matches_assignment_enumeration_and_uses_previous_stage():
    solve = reference(256)
    row_options = list(product(range(1, 4), repeat=3))
    for length in range(1, 4):
        for costs in product(row_options, repeat=length):
            expected = min(sum(costs[index][color] for index, color in enumerate(colors))
                           for colors in product(range(3), repeat=length)
                           if all(colors[index] != colors[index - 1] for index in range(1, length)))
            assert solve([list(row) for row in costs]) == expected
    assert solve([[1, 20, 20]] * 100) == 1050


def test_add_digits_matches_literal_iteration_across_large_domain_sample():
    solve = reference(258)
    for number in range(100001):
        value = number
        while value >= 10:
            value = sum(map(int, str(value)))
        assert solve(number) == value
    assert solve(0) == 0 and solve(9) == 9 and solve(18) == 9
    assert solve(2**31 - 1) == 1


def test_recursive_range_problem_has_reachable_prerequisites_and_review_boost():
    catalog = get_catalog()
    hard = catalog["leetcode-248"]
    assert hard.difficulty >= 8
    assert not prerequisites_met(hard, {topic: 69 for topic in hard.prerequisites})
    assert prerequisites_met(hard, {topic: 70 for topic in hard.prerequisites})
    assert all(any(problem.difficulty < 8 and topic in problem.topics for problem in catalog.values())
               for topic in hard.prerequisites)
    assert review_focus_boost(catalog["leetcode-247"]) >= 50
    assert review_focus_boost(hard) >= 50
