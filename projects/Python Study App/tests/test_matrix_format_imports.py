from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import random
import re
import string

import pytest

from code_practice.build_import_batch import build, review_isolated
from code_practice.catalog import get_catalog
from code_practice.import_batch_015 import BATCH, UNSOLVABLE, number_oracle, rectangle_oracle, sudoku_oracle
from code_practice.learning import prerequisites_met
from code_practice.schemas import TestCase as Case
from code_practice.validation import run_source

ROOT = Path(__file__).resolve().parent.parent


def reviewed_cases(pid):
    spec = BATCH[pid]
    rng = random.Random(4047 + pid)
    return ([args for args, _ in spec["examples"]] + spec["boundaries"]
            + [args for args, _ in spec["stress"]] + [spec["generator"](rng) for _ in range(500)])


def test_matrix_format_inputs_obey_every_source_domain():
    for pid in BATCH:
        for args in reviewed_cases(pid):
            if pid == 36:
                board = args[0]
                assert len(board) == 9
                assert all(len(row) == 9 and set(row) <= set(".123456789") for row in board)
            elif pid == 65:
                assert 1 <= len(args[0]) <= 20
                assert set(args[0]) <= set(string.ascii_letters + string.digits + "+-.")
            elif pid == 68:
                words, width = args
                assert 1 <= len(words) <= 300 and 1 <= width <= 100
                assert all(1 <= len(word) <= min(20, width) and
                           set(word) <= set(string.ascii_letters + string.punctuation) for word in words)
            else:
                matrix = args[0]
                assert 1 <= len(matrix) <= 200 and 1 <= len(matrix[0]) <= 200
                assert all(len(row) == len(matrix[0]) and set(row) <= set("01") for row in matrix)


def grammar_number(text):
    def unsigned_digits(value):
        return bool(value) and all(char in "0123456789" for char in value)
    def signed_integer(value):
        return unsigned_digits(value[1:] if value[:1] in ("+", "-") else value)
    parts = text.lower().split("e")
    if len(parts) > 2 or (len(parts) == 2 and not signed_integer(parts[1])):
        return False
    mantissa = parts[0]
    if mantissa[:1] in ("+", "-"):
        mantissa = mantissa[1:]
    sides = mantissa.split(".")
    return len(sides) <= 2 and unsigned_digits("".join(sides))


def test_number_flags_and_regex_match_independent_grammar_for_4680_short_strings():
    problem = get_catalog()["leetcode-65"]
    namespace = {}
    exec(problem.reference_solution, namespace)
    count = 0
    for length in range(1, 5):
        for chars in product("01eE+-.x", repeat=length):
            value = "".join(chars)
            expected = grammar_number(value)
            assert number_oracle([value]) == expected
            assert namespace["valid_number"](value) == expected
            count += 1
    assert count == 4680
    for value in ("NaN", "Infinity", "inf", "nan", "++0", "1e+", "1.2.3"):
        assert namespace["valid_number"](value) is False
    assert namespace["valid_number"]("1e" + "9" * 18) is True
    assert problem.difficulty >= 8 and not prerequisites_met(problem, {"strings": 69})


def test_sudoku_validation_does_not_require_a_solvable_puzzle():
    problem = get_catalog()["leetcode-36"]
    assert sudoku_oracle([UNSOLVABLE]) is True
    forbidden = set(UNSOLVABLE[0]) | {row[8] for row in UNSOLVABLE}
    forbidden |= {UNSOLVABLE[r][c] for r in range(3) for c in range(6, 9)}
    assert set("123456789") <= forbidden and UNSOLVABLE[0][8] == "."
    assert run_source(problem.reference_solution, problem,
                      Case(id="valid-not-solvable", arguments=[UNSOLVABLE], expected=True)) == (True, None)


def test_justification_preserves_exact_width_order_greedy_breaks_and_left_gaps():
    spec = BATCH[68]
    namespace = {}
    exec(spec["reference"], namespace)
    for words, width in reviewed_cases(68):
        lines = namespace[spec["name"]](words, width)
        assert all(len(line) == width for line in lines)
        assert [word for line in lines for word in line.split(" ") if word] == words
        consumed = 0
        for index, line in enumerate(lines):
            group = line.split()
            consumed += len(group)
            if index == len(lines) - 1 or len(group) == 1:
                assert line == " ".join(group).ljust(width)
            else:
                assert not line.endswith(" ")
                gaps = [len(gap) for gap in re.findall(" +", line)]
                assert max(gaps) - min(gaps) <= 1 and gaps == sorted(gaps, reverse=True)
            if index < len(lines) - 1:
                assert sum(map(len, group)) + len(group) + len(words[consumed]) > width
    golden = ["This    is    an", "example  of text", "justification.  "]
    assert namespace[spec["name"]](*spec["examples"][0][0]) == golden
    assert spec["oracle"](spec["examples"][0][0]) == golden


def test_maximal_rectangle_all_512_small_boards_against_cell_enumeration():
    problem = get_catalog()["leetcode-85"]
    namespace = {}
    exec(problem.reference_solution, namespace)
    for cells in product("01", repeat=9):
        matrix = [list(cells[start:start+3]) for start in (0, 3, 6)]
        expected = max([0] + [(b-t) * (r-l) for t in range(3) for b in range(t+1, 4)
                              for l in range(3) for r in range(l+1, 4)
                              if all(matrix[y][x] == "1" for y in range(t, b) for x in range(l, r))])
        assert rectangle_oracle([matrix]) == expected
        assert namespace["maximal_rectangle"](matrix) == expected
    assert namespace["maximal_rectangle"]([list("111"), list("111")]) == 6
    assert not prerequisites_met(problem, {"stacks": 69, "matrices": 100})


def test_workbook_sample_corrections_are_explicit_audited_and_fail_closed():
    source = next(json.loads(line) for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines()
                  if json.loads(line)["source_id"] == 68)
    spec = BATCH[68]
    uncorrected = {key: value for key, value in spec.items() if key != "sample_correction"}
    with pytest.raises(ValueError, match="conflicts"):
        build(68, uncorrected, source)
    for field, value in (("original_expected", []), ("corrected_expected", ["wrong"]), ("reason", "")):
        broken = deepcopy(spec)
        broken["sample_correction"][field] = value
        with pytest.raises(ValueError):
            build(68, broken, source)
    with pytest.raises(ValueError, match="missing workbook sample"):
        build(68, spec, {**source, "sample": ""})
    payload, report = review_isolated(68, spec, source, "fixture")
    assert payload is not None and report["valid"]
    assert report["sample_correction"]["original_sample"] == source["sample"]
    assert report["sample_correction"]["source_reference"] == source["reference_url"]
    assert report["sample_correction"]["original_expected"] != report["sample_correction"]["corrected_expected"]
    assert report["oracle_inputs"] == 500
