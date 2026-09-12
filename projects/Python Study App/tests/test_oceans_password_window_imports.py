import ast
from collections import Counter
from itertools import combinations_with_replacement, product
import random
import string

from code_practice.catalog import get_catalog
from code_practice.import_batch_038 import (
    BATCH, WORDS, add_oracle, partition_oracle, oceans_oracle, screen_oracle,
    ships_oracle, ship_components, password_oracle, xor_oracle, digits_oracle,
    replacement_oracle,
)
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.schemas import TestCase as Case
from code_practice.validation import run_source


def reference(pid):
    namespace = {}
    exec(BATCH[pid]['reference'],namespace)
    return namespace[BATCH[pid]['name']]


def fixtures(pid):
    spec = BATCH[pid]
    rng = random.Random(4047+pid)
    return ([a for a,_ in spec['examples']] + spec['boundaries']
            + [a for a,_ in spec['stress']] + [spec['generator'](rng) for _ in range(500)])


def test_batch_38_references_reject_logical_errors_and_keep_weak_topic_gates():
    catalog = get_catalog()
    for pid in BATCH:
        problem = catalog[f'leetcode-{pid}']
        assert problem.status=='approved' and len(problem.hints)==4 and problem.editorial
        assert sum(t.visible for t in problem.tests)==2 and sum(not t.visible for t in problem.tests)>=12
        assert all(run_source(problem.reference_solution,problem,t)==(True,None) for t in problem.tests)
        for wrong in problem.known_wrong_solutions:
            results = [run_source(wrong,problem,t) for t in problem.tests]
            assert (False,None) in results and all(error is None for _,error in results)
    assert review_focus_boost(catalog['leetcode-417'])>=100
    hard = catalog['leetcode-420']
    assert hard.difficulty>=8 and not prerequisites_met(hard,{'strings':69,'greedy':100})
    assert prerequisites_met(hard,{'strings':70,'greedy':70})


def test_batch_38_all_fixtures_stay_within_source_domains():
    for pid in BATCH:
        for args in fixtures(pid):
            if pid==415:
                for text in args:
                    assert 1<=len(text)<=10000 and set(text)<=set(string.digits)
                    assert text=='0' or text[0]!='0'
            elif pid==416:
                assert 1<=len(args[0])<=200 and all(1<=v<=100 for v in args[0])
            elif pid in (417,419):
                grid = args[0]
                assert 1<=len(grid)<=200 and 1<=len(grid[0])<=200
                assert all(len(row)==len(grid[0]) for row in grid)
                if pid==417:
                    assert all(0<=v<=100000 for row in grid for v in row)
                else:
                    assert all(v in 'X.' for row in grid for v in row)
                    assert all(len({r for r,c in component})==1 or len({c for r,c in component})==1
                               for component in ship_components(grid))
            elif pid==418:
                words,rows,cols = args
                assert 1<=len(words)<=100 and all(1<=len(w)<=10 and set(w)<=set(string.ascii_lowercase) for w in words)
                assert 1<=rows<=20000 and 1<=cols<=20000
            elif pid==420:
                assert 1<=len(args[0])<=50 and set(args[0])<=set(string.ascii_letters+string.digits+'.!')
            elif pid==421:
                assert 1<=len(args[0])<=200000 and all(0<=v<=2**31-1 for v in args[0])
            elif pid==423:
                text = args[0]
                assert 1<=len(text)<=100000 and set(text)<=set(''.join(WORDS))
                decoded = reference(423)(text)
                assert Counter(text)==Counter(''.join(WORDS[int(digit)] for digit in decoded))
            else:
                text,k = args
                assert 1<=len(text)<=100000 and set(text)<=set(string.ascii_uppercase) and 0<=k<=len(text)


def test_decimal_addition_exhausts_small_pairs_and_avoids_whole_number_conversion():
    solve = reference(415)
    for a in range(200):
        for b in range(200):
            assert solve(str(a),str(b))==add_oracle([str(a),str(b)])
    tree = ast.parse(BATCH[415]['reference'])
    assert not any(isinstance(node,(ast.Import,ast.ImportFrom)) for node in ast.walk(tree))
    assert not any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                   and node.func.id in ('int','float','eval','exec') for node in ast.walk(tree))
    for args,expected in BATCH[415]['stress']:
        assert solve(*args)==expected


def test_subset_partition_exhausts_positive_multisets_and_forbids_item_reuse():
    solve = reference(416)
    for length in range(1,10):
        for nums in combinations_with_replacement(range(1,5),length):
            assert solve(list(nums))==partition_oracle([nums])
    assert not solve([1,2,5]) and solve([1,1])
    for args,expected in BATCH[416]['stress']:
        assert solve(*args)==expected


def test_reverse_ocean_search_exhausts_small_maps_and_does_not_mutate():
    solve = reference(417)
    for cells in product(range(3),repeat=9):
        grid = [list(cells[i:i+3]) for i in (0,3,6)]
        before = [row[:] for row in grid]
        assert solve(grid)==oceans_oracle([grid]) and grid==before
    for args,expected in BATCH[417]['stress']:
        assert solve(*args)==expected
    # A rectangular plateau makes coordinate order observable; square symmetry cannot hide a swap.
    assert solve([[7,7,7],[7,7,7]])==[[0,0],[0,1],[0,2],[1,0],[1,1],[1,2]]


def test_ocean_answer_order_is_flexible_but_coordinates_and_duplicates_are_not():
    problem = get_catalog()['leetcode-417']
    args = [[[1,2,3],[4,5,6]]]
    expected = oceans_oracle(args)
    case = Case(id='rectangular-coordinates',arguments=args,expected=expected,comparator='unordered')
    source = lambda value: f'def pacific_atlantic_cells(heights):\n    return {value!r}\n'
    assert run_source(source(expected[::-1]),problem,case)==(True,None)
    for wrong in ([cell[::-1] for cell in expected],expected+[expected[0]],expected[:-1]):
        assert run_source(source(wrong),problem,case)==(False,None)


def test_screen_transitions_exhaust_word_widths_and_large_cycle_counts():
    solve = reference(418)
    for length in range(1,5):
        for sizes in product(range(1,5),repeat=length):
            words = ['a'*size for size in sizes]
            for rows in range(1,6):
                for cols in range(1,13):
                    assert solve(words,rows,cols)==screen_oracle([words,rows,cols])
    for args,expected in BATCH[418]['stress']:
        assert solve(*args)==expected


def test_battleships_exhaust_every_valid_three_by_three_board():
    solve = reference(419)
    valid = 0
    for cells in product('X.',repeat=9):
        grid = [list(cells[i:i+3]) for i in (0,3,6)]
        components = ship_components(grid)
        if any(len({r for r,c in comp})>1 and len({c for r,c in comp})>1 for comp in components):
            continue
        valid += 1
        before = [row[:] for row in grid]
        assert solve(grid)==len(components)==ships_oracle([grid]) and grid==before
    assert valid>100
    for args,expected in BATCH[419]['stress']:
        before = [row[:] for row in args[0]]
        assert solve(*args)==expected and args[0]==before


def strong(text):
    return (6<=len(text)<=20 and any(c.islower() for c in text) and any(c.isupper() for c in text)
            and any(c.isdigit() for c in text) and all(not (a==b==c) for a,b,c in zip(text,text[1:],text[2:])))


def explicit_edit_distance(text):
    """Literal BFS on a tiny alphabet, independent of the run formula and DFA state search."""
    level,seen = {text},{text}
    for distance in range(4):
        if any(strong(candidate) for candidate in level):
            return distance
        following = set()
        for candidate in level:
            following.update(candidate[:i]+candidate[i+1:] for i in range(len(candidate)))
            following.update(candidate[:i]+char+candidate[i+1:] for i in range(len(candidate)) for char in 'aA0')
            following.update(candidate[:i]+char+candidate[i:] for i in range(len(candidate)+1) for char in 'aA0')
        level = following-seen
        seen.update(level)
    raise AssertionError('Tiny BFS fixture unexpectedly needs more edits')


def test_password_formula_matches_literal_edits_and_exact_automaton_search():
    solve = reference(420)
    for chars in product('aA0',repeat=6):
        text = ''.join(chars)
        assert solve(text)==password_oracle([text])==explicit_edit_distance(text)
    # Nonrepresentative input letters and punctuation must remain eligible for zero-cost keeps.
    for text in ('zzzzzz','ZZZZZZ','999999','!!!!!!','...zzz','zzzZZZ999','xyxyxyxyxyxyxyxyxyxyzZ9',
                 'ab'*11,'aaaAAAAaaaaaAAAAAA1','a'*50,'.'*50):
        assert solve(text)==password_oracle([text])
    rng = random.Random(420)
    for _ in range(100):
        text = ''.join(rng.choice('xyzXYZ789.!') for _ in range(rng.randint(18,50)))
        assert solve(text)==password_oracle([text])
    for args,expected in BATCH[420]['stress']:
        assert solve(*args)==password_oracle(args)==expected


def test_xor_prefix_greed_exhausts_small_multisets_and_full_31_bit_domain():
    solve = reference(421)
    for length in range(1,6):
        for nums in combinations_with_replacement(range(8),length):
            assert solve(nums)==xor_oracle([nums])
    for bit in range(31):
        assert solve([0,1<<bit])==1<<bit
        assert solve([1<<bit,(1<<bit)-1])==(1<<(bit+1))-1
    for args,expected in BATCH[421]['stress']:
        assert solve(*args)==expected


def test_digit_inventory_matches_every_small_multiset_and_reconstructs_letters():
    solve = reference(423)
    for length in range(1,5):
        for digits in combinations_with_replacement(range(10),length):
            text = ''.join(WORDS[digit] for digit in digits)
            expected = ''.join(map(str,digits))
            assert solve(text[::-1])==digits_oracle([text])==expected
    for args,expected in BATCH[423]['stress']:
        assert solve(*args)==expected
        assert Counter(args[0])==Counter(''.join(WORDS[int(digit)] for digit in expected))


def test_historical_window_frequency_exhausts_ternary_strings_and_budgets():
    solve = reference(424)
    for length in range(1,8):
        for chars in product('ABC',repeat=length):
            text = ''.join(chars)
            for k in range(length+1):
                assert solve(text,k)==replacement_oracle([text,k])
    for args,expected in BATCH[424]['stress']:
        assert solve(*args)==expected
