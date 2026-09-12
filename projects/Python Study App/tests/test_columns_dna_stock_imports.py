from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import product
import random
import string

from code_practice.catalog import get_catalog
from code_practice.import_batch_018 import BATCH
from code_practice.learning import prerequisites_met
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


def test_columns_dna_stock_domains_cover_boundaries_without_out_of_range_inputs():
    for pid in BATCH:
        for args in cases(pid):
            if pid == 168:
                assert type(args[0]) is int and 1 <= args[0] <= 2**31 - 1
            elif pid == 171:
                title = args[0]
                assert 1 <= len(title) <= 7 and set(title) <= set(string.ascii_uppercase)
                assert 1 <= BATCH[171]["oracle"]([title]) <= 2**31 - 1
            elif pid == 172:
                assert type(args[0]) is int and 0 <= args[0] <= 10000
            elif pid == 179:
                assert 1 <= len(args[0]) <= 100
                assert all(type(n) is int and 0 <= n <= 10**9 for n in args[0])
            elif pid == 187:
                assert 1 <= len(args[0]) <= 100000 and set(args[0]) <= set("ACGT")
            else:
                k, prices = args
                assert type(k) is int and 1 <= k <= 100 and 1 <= len(prices) <= 1000
                assert all(type(n) is int and 0 <= n <= 1000 for n in prices)


def test_column_conversions_match_enumerated_labels_and_large_round_trips():
    encode, decode = reference(168), reference(171)
    labels = ["".join(letters) for width in (1, 2) for letters in product(string.ascii_uppercase, repeat=width)]
    for number, label in enumerate(labels, 1):
        assert encode(number) == BATCH[168]["oracle"]([number]) == label
        assert decode(label) == BATCH[171]["oracle"]([label]) == number
    for number, in cases(168):
        assert decode(encode(number)) == number
    assert encode(2147483647) == "FXSHRXW"
    assert decode("FXSHRXW") == 2147483647


def test_factorial_zeroes_full_domain_matches_accumulated_prime_factors():
    solve = reference(172)
    fives = 0
    for n in range(10001):
        value = n
        while value and value % 5 == 0:
            fives += 1
            value //= 5
        assert solve(n) == fives
        if n <= 500:
            assert BATCH[172]["oracle"]([n]) == fives
    assert solve(10000) == 2499


def test_largest_number_matches_all_small_permutations_and_comparator_order():
    solve = reference(179)
    pool = (0, 1, 10, 12, 121, 9)
    for values in product(pool, repeat=3):
        assert solve(values) == BATCH[179]["oracle"]([values])
    # Cross-check the editorial's transitive ordering argument using exact
    # rational values, not floating point or the sorting reference itself.
    for a, b in product(pool + (1000000000, 8308, 830), repeat=2):
        first, second = str(a), str(b)
        x = Fraction(a, 10**len(first) - 1)
        y = Fraction(b, 10**len(second) - 1)
        assert ((first + second > second + first) - (first + second < second + first)) == ((x > y) - (x < y))
    assert solve([0] * 100) == "0"
    assert solve([10**9] * 100) == "1000000000" * 100


def test_dna_counts_overlapping_windows_once_and_has_no_short_window_false_positives():
    solve = reference(187)
    inputs = [args[0] for args in cases(187)]
    inputs += ["".join(chars) for chars in product("AC", repeat=11)]
    for text in inputs:
        counts = Counter(text[i:i + 10] for i in range(len(text) - 9))
        expected = sorted(word for word, count in counts.items() if count >= 2)
        actual = solve(text)
        assert len(actual) == len(set(actual))
        assert sorted(actual) == expected
    assert solve("A" * 9) == []
    assert solve("A" * 10) == []
    assert solve("A" * 11) == ["A" * 10]
    problem = get_catalog()["leetcode-187"]
    example = problem.tests[0]
    case = Case(id="order-and-multiplicity", arguments=example.arguments,
                expected=example.expected, comparator="unordered")
    good = f"def repeated_dna(s):\n    return {example.expected[::-1]!r}\n"
    bad = f"def repeated_dna(s):\n    return {example.expected + example.expected!r}\n"
    assert run_source(good, problem, case) == (True, None)
    assert run_source(bad, problem, case) == (False, None)


def test_variable_stock_budget_exhausts_small_prices_and_keeps_hard_prerequisites():
    solve = reference(188)
    for length in range(1, 7):
        for prices in product((0, 1, 2), repeat=length):
            for k in (1, 2, 3):
                assert solve(k, prices) == BATCH[188]["oracle"]([k, prices])
    prices = [0, 3, 0, 3, 0, 3]
    assert [solve(k, prices) for k in (1, 2, 3)] == [3, 6, 9]
    assert solve(100, [0, 1000] * 500) == 100000
    problem = get_catalog()["leetcode-188"]
    assert problem.difficulty >= 8
    assert not prerequisites_met(problem, {"dynamic-programming": 69})
    assert prerequisites_met(problem, {"dynamic-programming": 70})


def test_new_return_contracts_do_not_mutate_input_arguments():
    for pid in BATCH:
        solve = reference(pid)
        for original in BATCH[pid]["boundaries"]:
            arguments = deepcopy(original)
            solve(*arguments)
            assert arguments == original
