from itertools import combinations_with_replacement, product
import random
import re
import string

from code_practice.catalog import get_catalog
from code_practice.import_batch_017 import BATCH
from code_practice.learning import prerequisites_met, review_focus_boost


def reference(pid):
    namespace = {}
    exec(BATCH[pid]["reference"], namespace)
    return namespace[BATCH[pid]["name"]]


def cases(pid):
    spec = BATCH[pid]
    rng = random.Random(4047 + pid)
    return ([args for args, _ in spec["examples"]] + spec["boundaries"]
            + [args for args, _ in spec["stress"]] + [spec["generator"](rng) for _ in range(500)])


def test_text_array_dungeon_source_domains_include_numeric_guarantees():
    for pid in BATCH:
        for args in cases(pid):
            if pid == 151:
                assert 1 <= len(args[0]) <= 10000 and args[0].strip()
                assert set(args[0]) <= set(string.ascii_letters + string.digits + " ")
            elif pid == 152:
                nums = args[0]
                assert 1 <= len(nums) <= 20000 and all(type(value) is int and -10 <= value <= 10 for value in nums)
                if len(nums) <= 100:
                    for start in range(len(nums)):
                        accumulated = 1
                        for value in nums[start:]:
                            accumulated *= value
                            assert -(2**31) <= accumulated < 2**31
                else:
                    # In this stress fixture all nonzero segment absolute products
                    # fit signed-positive range; every contained product does too.
                    magnitude = 1
                    for value in nums:
                        magnitude = magnitude * abs(value) if value else 1
                        assert magnitude < 2**31
            elif pid == 154:
                nums = args[0]
                assert 1 <= len(nums) <= 5000 and all(-5000 <= value <= 5000 for value in nums)
                assert sum(nums[index] > nums[(index + 1) % len(nums)] for index in range(len(nums))) <= 1
            elif pid == 159:
                assert 1 <= len(args[0]) <= 100000 and set(args[0]) <= set(string.ascii_letters)
            elif pid == 161:
                assert all(len(text) <= 10000 and set(text) <= set(string.ascii_letters + string.digits) for text in args)
            elif pid == 163:
                nums, lower, upper = args
                assert -(10**9) <= lower <= upper <= 10**9 and len(nums) <= 100
                assert nums == sorted(set(nums)) and all(lower <= value <= upper for value in nums)
            elif pid == 165:
                for version in args:
                    assert 1 <= len(version) <= 500 and re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version)
                    assert all(0 <= int(revision) < 2**31 for revision in version.split("."))
            else:
                dungeon = args[0]
                assert 1 <= len(dungeon) <= 200 and 1 <= len(dungeon[0]) <= 200
                assert all(len(row) == len(dungeon[0]) and all(-1000 <= value <= 1000 for value in row) for row in dungeon)


def test_duplicate_rotated_minimum_exhausts_small_sorted_multisets_and_rotations():
    solve = reference(154)
    for length in range(1, 7):
        for ordered in combinations_with_replacement((-1, 0, 1), length):
            for pivot in range(length):
                values = list(ordered[pivot:] + ordered[:pivot])
                assert solve(values) == min(values)
    problem = get_catalog()["leetcode-154"]
    assert review_focus_boost(problem) >= 60
    assert not prerequisites_met(problem, {"binary-search": 69})


def test_product_tracks_negative_extremes_and_does_not_cross_zero():
    solve = reference(152)
    for values, expected in [([-2, 3, -4], 24), ([-2, 0, -1], 0), ([-5], -5),
                             ([2, 0, 3], 3), ([-1, -1, -1], 1)]:
        assert solve(values) == expected
    for length in range(1, 6):
        for values in product((-1, 0, 1), repeat=length):
            assert solve(values) == BATCH[152]["oracle"]([values])


def test_exactly_one_edit_matches_explicit_single_operation_neighbors():
    solve = reference(161)
    texts = ["".join(chars) for length in range(4) for chars in product("ab", repeat=length)]
    for first in texts:
        neighbors = {first[:index] + char + first[index:] for index in range(len(first) + 1) for char in "ab"}
        neighbors |= {first[:index] + first[index + 1:] for index in range(len(first))}
        neighbors |= {first[:index] + char + first[index + 1:] for index in range(len(first)) for char in "ab" if char != first[index]}
        assert first not in neighbors
        for second in texts:
            expected = second in neighbors
            assert solve(first, second) == expected
            assert BATCH[161]["oracle"]([first, second]) == expected


def test_missing_ranges_cover_exact_complement_without_splitting_adjacent_gaps():
    solve = reference(163)
    for nums, lower, upper in cases(163):
        result = solve(nums, lower, upper)
        assert all(lower <= start <= end <= upper for start, end in result)
        assert all(result[index][1] + 1 < result[index + 1][0] for index in range(len(result) - 1))
        assert not any(start <= value <= end for start, end in result for value in nums)
        assert sum(end - start + 1 for start, end in result) + len(nums) == upper - lower + 1
        if upper - lower <= 100:
            assert result == BATCH[163]["oracle"]([nums, lower, upper])


def test_words_windows_and_versions_keep_their_distinct_contracts():
    reverse = reference(151)
    assert reverse("  A1   b2 c3  ") == "c3 b2 A1"
    window = reference(159)
    assert window("ece") == 3 and window("aaaa") == 4 and window("aAb") == 2
    compare = reference(165)
    for first, second, expected in [("1", "1.0.00", 0), ("1.2", "1.10", -1),
                                     ("2.0", "1.999", 1), ("0000", "0.0", 0)]:
        assert compare(first, second) == expected
        assert compare(second, first) == -expected


def can_survive(dungeon, initial):
    """Forward feasibility for one initial health, not backward requirements."""
    health = [[None] * len(dungeon[0]) for _ in dungeon]
    for row in range(len(dungeon)):
        for column in range(len(dungeon[0])):
            previous = [initial] if row == column == 0 else []
            if row and health[row - 1][column] is not None:
                previous.append(health[row - 1][column])
            if column and health[row][column - 1] is not None:
                previous.append(health[row][column - 1])
            if previous:
                value = max(previous) + dungeon[row][column]
                if value >= 1:
                    health[row][column] = value
    return health[-1][-1] is not None


def test_dungeon_all_729_two_by_three_grids_match_forward_health_search():
    solve = reference(174)
    for values in product((-1, 0, 1), repeat=6):
        dungeon = [list(values[:3]), list(values[3:])]
        expected = next(initial for initial in range(1, 8) if can_survive(dungeon, initial))
        assert solve(dungeon) == expected
        assert BATCH[174]["oracle"]([dungeon]) == expected
    assert solve([[-5, 100]]) == 6  # Positive final gain does not erase the first room's danger.
    problem = get_catalog()["leetcode-174"]
    assert review_focus_boost(problem) >= 130
    assert not prerequisites_met(problem, {"matrices": 100, "dynamic-programming": 69})
