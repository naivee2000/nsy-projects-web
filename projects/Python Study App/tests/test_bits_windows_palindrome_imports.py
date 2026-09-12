from functools import reduce
from itertools import product
from operator import and_
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_020 import BATCH
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.schemas import TestCase as Case
from code_practice.validation import run_source


def reference(pid):
    namespace = {}
    exec(BATCH[pid]["reference"], namespace)
    return namespace[BATCH[pid]["name"]]


def cases(pid):
    spec = BATCH[pid]
    rng = random.Random(4047 + pid)
    return ([args for args, _ in spec["examples"]] + spec["boundaries"]
            + [args for args, _ in spec["stress"]] + [spec["generator"](rng) for _ in range(500)])


def test_batch_twenty_inputs_match_retained_source_constraints():
    for pid in BATCH:
        for args in cases(pid):
            if pid == 190:
                assert type(args[0]) is int and 0 <= args[0] <= 2**31 - 2 and args[0] % 2 == 0
            elif pid == 201:
                assert all(type(n) is int for n in args) and 0 <= args[0] <= args[1] <= 2**31 - 1
            elif pid == 202:
                assert type(args[0]) is int and 1 <= args[0] <= 2**31 - 1
            elif pid == 204:
                assert type(args[0]) is int and 0 <= args[0] <= 5000000
            elif pid == 205:
                assert 1 <= len(args[0]) == len(args[1]) <= 50000
                assert all(ord(char) < 128 for text in args for char in text)
            elif pid == 209:
                target, nums = args
                assert type(target) is int and 1 <= target <= 10**9 and 1 <= len(nums) <= 100000
                assert all(type(n) is int and 1 <= n <= 10000 for n in nums)
            elif pid == 213:
                assert 1 <= len(args[0]) <= 100
                assert all(type(n) is int and 0 <= n <= 1000 for n in args[0])
            elif pid == 214:
                assert len(args[0]) <= 50000 and set(args[0]) <= set("abcdefghijklmnopqrstuvwxyz")
            else:
                k, n = args
                assert type(k) is type(n) is int and 2 <= k <= 9 and 1 <= n <= 60


def test_reverse_bits_preserves_fixed_width_and_is_an_involution_on_the_source_domain():
    solve = reference(190)
    for position in range(1, 31):
        assert solve(1 << position) == 1 << (31 - position)
    for (n,) in cases(190):
        result = solve(n)
        assert 0 <= result <= 2**31 - 2 and result % 2 == 0
        assert solve(result) == n
        assert result.bit_count() == n.bit_count()
    assert solve(2) == 1073741824


def test_range_and_exhausts_small_intervals_and_handles_billion_wide_ranges():
    solve = reference(201)
    for left in range(128):
        for right in range(left, 128):
            assert solve(left, right) == reduce(and_, range(left, right + 1))
    assert solve(1, 2147483647) == 0
    assert solve(1073741824, 2147483647) == 1073741824
    assert solve(5, 7) == 4 != (5 & 7)


def test_happy_numbers_follow_cycles_not_digital_roots_or_one_step_rules():
    solve = reference(202)
    for n in range(1, 1001):
        assert solve(n) == BATCH[202]["oracle"]([n])
    assert solve(1) and solve(7) and solve(19)
    assert not solve(46) and 46 % 9 == 1
    assert all(not solve(n) for n in (4, 16, 37, 58, 89, 145, 42, 20))


def linear_prime_count(n):
    """Euler sieve: mark each composite once with its smallest prime factor."""
    composite = bytearray(n)
    primes = []
    for value in range(2, n):
        if not composite[value]:
            primes.append(value)
        for prime in primes:
            multiple = value * prime
            if multiple >= n:
                break
            composite[multiple] = 1
            if value % prime == 0:
                break
    return len(primes)


def test_prime_count_full_boundary_has_an_independent_linear_sieve_check():
    solve = reference(204)
    for n in range(101):
        assert solve(n) == linear_prime_count(n) == BATCH[204]["oracle"]([n])
    assert solve(2) == 0 and solve(3) == 1 and solve(11) == 4
    assert linear_prime_count(5000000) == 348513
    assert solve(5000000) == 348513


def test_isomorphism_exhausts_small_position_patterns_and_keeps_ascii_characters():
    solve = reference(205)
    for length in range(1, 5):
        texts = ["".join(chars) for chars in product("abc", repeat=length)]
        for first, second in product(texts, repeat=2):
            expected = all((first[i] == first[j]) == (second[i] == second[j])
                           for i in range(length) for j in range(length))
            assert solve(first, second) == expected
    assert not solve("ab", "aa") and not solve("aa", "ab")
    assert solve("\x00A\x00", "\x7fz\x7f")
    assert solve(" \t ", "a0a")


def test_minimum_window_uses_at_least_and_repeated_shrinking():
    solve = reference(209)
    for length in range(1, 6):
        for values in product((1, 2, 3), repeat=length):
            for target in range(1, 17):
                assert solve(target, values) == BATCH[209]["oracle"]([target, values])
    assert solve(5, [10]) == 1
    assert solve(10, [1, 1, 1, 10]) == 1
    assert solve(1000000000, [10000] * 100000) == 100000


def test_circular_house_profit_enforces_wraparound_but_not_a_singleton_self_edge():
    solve = reference(213)
    for length in range(1, 7):
        for values in product((0, 1, 2), repeat=length):
            assert solve(values) == BATCH[213]["oracle"]([values])
    assert solve([5]) == 5
    assert solve([10, 0, 0, 10]) == 10
    assert solve([1000] * 100) == 50000


def prepend_oracle(text):
    # Directly enumerate added strings by increasing length, without using
    # the longest-palindromic-prefix characterization of the result.
    for added in range(len(text) + 1):
        for chars in product("ab", repeat=added):
            candidate = "".join(chars) + text
            if candidate == candidate[::-1]:
                return candidate


def test_shortest_palindrome_matches_direct_prepend_search_and_has_reachable_prerequisites():
    solve = reference(214)
    for length in range(8):
        for chars in product("ab", repeat=length):
            text = "".join(chars)
            expected = prepend_oracle(text)
            assert solve(text) == BATCH[214]["oracle"]([text]) == expected
    for (text,), expected in BATCH[214]["stress"]:
        actual = solve(text)
        assert actual == expected and actual.endswith(text) and actual == actual[::-1]
    problem = get_catalog()["leetcode-214"]
    assert problem.difficulty >= 8
    assert not prerequisites_met(problem, {"strings": 100, "string-matching": 69})
    assert prerequisites_met(problem, {"strings": 70, "string-matching": 70})
    prior = get_catalog()["leetcode-28"]
    assert set(problem.prerequisites) <= set(prior.topics) and prior.difficulty < 8


def test_digit_combinations_exhaust_all_480_inputs_without_duplicates_or_order_restrictions():
    solve = reference(216)
    for k in range(2, 10):
        for target in range(1, 61):
            actual = solve(k, target)
            assert sorted(actual) == sorted(BATCH[216]["oracle"]([k, target]))
            assert len(actual) == len({tuple(sorted(row)) for row in actual})
            assert all(len(row) == len(set(row)) == k and sum(row) == target for row in actual)
    problem = get_catalog()["leetcode-216"]
    assert review_focus_boost(problem) >= 50
    case = Case(id="unordered-combinations", arguments=[3, 9], expected=[[1, 2, 6], [1, 3, 5], [2, 3, 4]], comparator="unordered_nested")
    assert run_source('def fixed_digit_combinations(k, n):\n    return [[4,3,2],[5,3,1],[6,2,1]]', problem, case) == (True, None)
    assert run_source('def fixed_digit_combinations(k, n):\n    return [[1,2,6],[1,3,5],[1,2,6]]', problem, case) == (False, None)
