from itertools import product
import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_027 import (
    BATCH,
    COOLDOWN,
    ISLANDS,
    MEETING,
    MIN_HEIGHT,
    RECTANGLE,
    REMOVE_INVALID,
    cooldown_oracle,
    height_tree_oracle,
    invalid_parentheses_oracle,
    islands_oracle,
    meeting_oracle,
    rectangle_oracle,
)
from code_practice.validation import run_source


IDS = (296, 298, 299, 301, 302, 305, 306, 309, 310, 311)
ROOT = Path(__file__).resolve().parents[1]


def function(source, name):
    namespace = {}
    exec(compile(source, f"<{name}>", "exec"), namespace)
    return namespace[name]


def test_batch_27_is_published_with_complete_executable_evidence():
    catalog = get_catalog()
    for problem_id in IDS:
        problem = catalog[f"leetcode-{problem_id}"]
        assert problem.status == "approved"
        assert len([case for case in problem.tests if case.visible]) >= 2
        assert len([case for case in problem.tests if not case.visible]) >= 12
        assert len(problem.hints) == 4
        assert problem.editorial and problem.reference_solution
        assert len(problem.known_wrong_solutions) >= 2
        assert all(run_source(problem.reference_solution, problem, case)[0]
                   for case in problem.tests)
        for wrong in problem.known_wrong_solutions:
            assert any(run_source(wrong, problem, case) == (False, None)
                       for case in problem.tests)


def test_new_constructor_query_designs_are_documented_exclusions():
    ledger = json.loads((ROOT / "catalog_import/ledger.json").read_text())
    records = {record["source_id"]: record for record in ledger["records"]}
    for source_id in (244, 303, 304, 346, 359, 703, 729, 900, 901, 933):
        assert records[source_id]["status"] == "excluded"
        assert records[source_id]["exclusion_category"] == "multi-method-design"
        assert "__init__" in records[source_id]["reason"]
    # A later import batch may grow the catalog; verify the ledger accounts for
    # its actual records rather than freezing an earlier checkpoint's totals.
    from collections import Counter
    assert ledger["counts"] == dict(Counter(record['status'] for record in records.values()))
    assert sum(ledger["counts"].values()) == 3629


def test_meeting_medians_match_every_nonempty_two_by_three_home_grid():
    solve = function(MEETING, "min_total_distance")
    for cells in product((0, 1), repeat=6):
        if not any(cells):
            continue
        grid = [list(cells[:3]), list(cells[3:])]
        assert solve(grid) == meeting_oracle([grid])


def test_minimum_parenthesis_results_match_exhaustive_short_strings():
    solve = function(REMOVE_INVALID, "remove_invalid_parentheses")
    for length in range(1, 7):
        for text in map("".join, product("()ab", repeat=length)):
            assert sorted(solve(text)) == invalid_parentheses_oracle([text])


def connected_black(image):
    black = {(row, column) for row in range(len(image)) for column in range(len(image[0]))
             if image[row][column] == "1"}
    reached = {next(iter(black))}
    while True:
        expanded = reached | {
            neighbor
            for row, column in reached
            for neighbor in ((row - 1, column), (row + 1, column),
                             (row, column - 1), (row, column + 1))
            if neighbor in black
        }
        if expanded == reached:
            return reached == black
        reached = expanded


def test_rectangle_binary_search_matches_all_connected_three_by_three_shapes():
    solve = function(RECTANGLE, "smallest_black_rectangle")
    for mask in range(1, 1 << 9):
        image = [["1" if mask & (1 << (row * 3 + column)) else "0"
                  for column in range(3)] for row in range(3)]
        if not connected_black(image):
            continue
        selected = next((row, column) for row in range(3) for column in range(3)
                        if image[row][column] == "1")
        assert solve(image, *selected) == rectangle_oracle([image, *selected])


def test_union_find_matches_direct_component_counts_for_all_short_grid_sequences():
    solve = function(ISLANDS, "count_islands_after_additions")
    cells = ((0, 0), (0, 1), (1, 0), (1, 1))
    for length in range(1, 5):
        for sequence in product(cells, repeat=length):
            positions = [list(cell) for cell in sequence]
            assert solve(2, 2, positions) == islands_oracle([2, 2, positions])


def test_cooldown_state_machine_matches_exhaustive_short_prices():
    solve = function(COOLDOWN, "max_profit_with_cooldown")
    for length in range(1, 7):
        for prices in map(list, product(range(4), repeat=length)):
            assert solve(prices) == cooldown_oracle([prices])


def tree_from_prufer(code):
    node_count = len(code) + 2
    degree = [1] * node_count
    for node in code:
        degree[node] += 1
    edges = []
    for node in code:
        leaf = next(index for index, value in enumerate(degree) if value == 1)
        edges.append([leaf, node])
        degree[leaf] -= 1
        degree[node] -= 1
    remaining = [node for node, value in enumerate(degree) if value == 1]
    edges.append(remaining)
    return edges


def test_leaf_trimming_matches_all_labeled_trees_through_six_nodes():
    solve = function(MIN_HEIGHT, "minimum_height_tree_roots")
    assert solve(1, []) == [0]
    for node_count in range(2, 7):
        for code in product(range(node_count), repeat=node_count - 2):
            edges = tree_from_prufer(code)
            assert sorted(solve(node_count, edges)) == height_tree_oracle([node_count, edges])


def test_batch_27_generators_remain_inside_reviewed_shapes():
    import random

    for problem_id, spec in BATCH.items():
        rng = random.Random(4047 + problem_id)
        for _ in range(500):
            args = spec["generator"](rng)
            assert len(args) == len(spec["params"])
            if problem_id == 302:
                image, row, column = args
                assert image[row][column] == "1"
                assert connected_black(image)
            elif problem_id == 305:
                rows, columns, positions = args
                assert all(0 <= row < rows and 0 <= column < columns for row, column in positions)
