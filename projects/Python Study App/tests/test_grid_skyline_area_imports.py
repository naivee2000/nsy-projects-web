from copy import deepcopy
from itertools import combinations_with_replacement, permutations, product
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_021 import BATCH, large_dictionary
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


def test_grid_skyline_area_inputs_preserve_source_domains():
    for pid in BATCH:
        for args in cases(pid):
            if pid == 212:
                board, words = args
                assert 1 <= len(board) <= 12 and 1 <= len(board[0]) <= 12
                assert all(len(row) == len(board[0]) and all(len(char) == 1 and "a" <= char <= "z" for char in row) for row in board)
                assert 1 <= len(words) <= 30000 and len(words) == len(set(words))
                assert all(1 <= len(word) <= 10 and set(word) <= set("abcdefghijklmnopqrstuvwxyz") for word in words)
            elif pid == 218:
                buildings = args[0]
                assert 1 <= len(buildings) <= 10000
                assert all(len(building) == 3 and all(type(v) is int for v in building) for building in buildings)
                assert all(0 <= left < right <= 2**31 - 1 and 1 <= height <= 2**31 - 1 for left, right, height in buildings)
                assert [b[0] for b in buildings] == sorted(b[0] for b in buildings)
            elif pid == 221:
                matrix = args[0]
                assert 1 <= len(matrix) <= 300 and 1 <= len(matrix[0]) <= 300
                assert all(len(row) == len(matrix[0]) and set(row) <= {"0", "1"} for row in matrix)
            else:
                assert len(args) == 8 and all(type(n) is int and -10000 <= n <= 10000 for n in args)
                assert args[0] <= args[2] and args[1] <= args[3] and args[4] <= args[6] and args[5] <= args[7]


def test_multiword_search_matches_direct_simple_path_enumeration_on_every_binary_two_by_two_board():
    solve = reference(212)
    words = ["".join(chars) for length in range(1, 6) for chars in product("ab", repeat=length)]
    for chars in product("ab", repeat=4):
        board = [list(chars[:2]), list(chars[2:])]
        expected = set()
        for length in range(1, 5):
            for cells in permutations(range(4), length):
                if all(abs(a // 2 - b // 2) + abs(a % 2 - b % 2) == 1 for a, b in zip(cells, cells[1:])):
                    expected.add("".join(chars[cell] for cell in cells))
        before = deepcopy(board)
        actual = solve(board, words)
        assert len(actual) == len(set(actual))
        assert set(actual) == expected == set(BATCH[212]["oracle"]([board, words]))
        assert board == before


def test_word_search_cell_reuse_witness_survives_frequency_pruning_and_duplicates_are_rejected():
    problem = get_catalog()["leetcode-212"]
    case = Case(id="unreachable-second-a", arguments=[[["a", "b", "x", "a"]], ["aba"]], expected=[], comparator="unordered")
    assert run_source(problem.reference_solution, problem, case) == (True, None)
    assert run_source(problem.known_wrong_solutions[0], problem, case) == (False, None)
    repeated = Case(id="many-paths-one-word", arguments=[[["a", "a"], ["a", "a"]], ["a", "aa"]], expected=["a", "aa"], comparator="unordered")
    assert run_source(problem.reference_solution, problem, repeated) == (True, None)
    assert run_source('def find_board_words(board, words):\n    return ["a", "aa", "a"]', problem, repeated) == (False, None)
    dictionary = large_dictionary()
    assert len(dictionary) == len(set(dictionary)) == 30000
    board = [["a"] * 12 for _ in range(12)]
    assert set(reference(212)(board, dictionary)) == {"a" * n for n in range(1, 11)}
    assert board == [["a"] * 12 for _ in range(12)]


def pixel_skyline(buildings):
    left, right = min(b[0] for b in buildings), max(b[1] for b in buildings)
    columns = [max((height for a, b, height in buildings if a <= x < b), default=0) for x in range(left, right)]
    answer = [[left, columns[0]]]
    for offset in range(1, len(columns)):
        if columns[offset] != columns[offset - 1]:
            answer.append([left + offset, columns[offset]])
    return answer + [[right, 0]]


def test_skyline_exhausts_small_building_multisets_and_coalesces_simultaneous_events():
    solve = reference(218)
    options = [(left, right, height) for left in range(3) for right in range(left + 1, 4) for height in (1, 2, 3)]
    for buildings in combinations_with_replacement(options, 3):
        ordered = sorted(buildings, key=lambda b: b[0])
        actual = solve(ordered)
        assert actual == pixel_skyline(ordered) == BATCH[218]["oracle"]([ordered])
        assert all(a[0] < b[0] and a[1] != b[1] for a, b in zip(actual, actual[1:]))
    assert solve([[0, 2, 3], [2, 5, 3]]) == [[0, 3], [5, 0]]
    assert solve([[0, 2, 5], [2, 4, 3], [2, 3, 7]]) == [[0, 5], [2, 7], [3, 3], [4, 0]]
    for args, expected in BATCH[218]["stress"]:
        assert solve(*args) == expected


def test_maximal_square_exhausts_three_by_three_binary_matrices_and_checks_area():
    solve = reference(221)
    for chars in product("01", repeat=9):
        matrix = [list(chars[i:i + 3]) for i in (0, 3, 6)]
        before = deepcopy(matrix)
        assert solve(matrix) == BATCH[221]["oracle"]([matrix])
        assert matrix == before
    assert solve([["0", "1"], ["1", "1"]]) == 1
    assert solve([["1"] * 5 for _ in range(2)]) == 4
    assert solve([["1"] * 300 for _ in range(300)]) == 90000


def test_rectangle_union_exhausts_degenerate_and_nondegenerate_small_rectangles():
    solve = reference(223)
    intervals = list(combinations_with_replacement((-1, 0, 1), 2))
    rectangles = [(a, b, c, d) for (a, c), (b, d) in product(intervals, repeat=2)]
    def pixels(rectangle):
        a, b, c, d = rectangle
        return {(x, y) for x in range(a, c) for y in range(b, d)}
    for first, second in product(rectangles, repeat=2):
        arguments = list(first + second)
        expected = len(pixels(first) | pixels(second))
        assert solve(*arguments) == expected == BATCH[223]["oracle"](arguments)
        assert solve(*(second + first)) == expected
    assert solve(0, 0, 1, 1, 2, 2, 3, 3) == 2
    assert solve(-10000, -10000, 0, 10000, 0, -10000, 10000, 10000) == 400000000


def test_grid_recursion_review_priority_and_hard_prerequisites_are_reachable():
    words = get_catalog()["leetcode-212"]
    assert words.difficulty >= 8 and review_focus_boost(words) >= 80
    assert not prerequisites_met(words, {"matrices": 100, "recursion": 69, "backtracking": 100})
    assert prerequisites_met(words, {"matrices": 70, "recursion": 70, "backtracking": 70})
    skyline = get_catalog()["leetcode-218"]
    assert skyline.difficulty >= 8
    assert not prerequisites_met(skyline, {"heaps": 69, "intervals": 100})
    assert prerequisites_met(skyline, {"heaps": 70, "intervals": 70})
    preparatory_topics = {topic for problem in get_catalog().values() if problem.difficulty < 8 for topic in problem.topics}
    assert set(words.prerequisites + skyline.prerequisites) <= preparatory_topics
