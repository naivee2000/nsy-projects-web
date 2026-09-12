from itertools import combinations, product
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_002 import positions, flatten
from code_practice.import_batch_034 import (
    BATCH, SORT, POINTS, GAP, WORDS, ROTATE, REMOVE,
    points_oracle, upside_oracle, upside_node_order, gap_oracle, words_oracle,
)
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.schemas import TestCase as Case
from code_practice.validation import ListNode, _listnode, _serialize, run_source


def function(source, name):
    namespace = {'ListNode':ListNode}
    exec(compile(source,f'<{name}>','exec'),namespace)
    return namespace[name]


def test_batch_34_references_wrong_algorithms_and_node_starters():
    for pid in BATCH:
        problem = get_catalog()[f'leetcode-{pid}']
        assert problem.status == 'approved' and len(problem.hints) == 4 and problem.editorial
        assert sum(t.visible for t in problem.tests) >= 2
        assert sum(not t.visible for t in problem.tests) >= 12
        assert all(run_source(problem.reference_solution,problem,t) == (True,None) for t in problem.tests)
        for wrong in problem.known_wrong_solutions:
            assert any(run_source(wrong,problem,t) == (False,None) for t in problem.tests)
    for pid,cls in ((148,'ListNode'),(156,'TreeNode'),(203,'ListNode')):
        problem = get_catalog()[f'leetcode-{pid}']
        assert f'class {cls}:' in problem.starter_code
        assert review_focus_boost(problem) >= 50
    hard = get_catalog()['leetcode-149']
    assert hard.difficulty >= 8
    assert not prerequisites_met(hard,{'arrays':69,'hash-maps':100})
    assert prerequisites_met(hard,{'arrays':70,'hash-maps':70})


def test_all_batch_34_inputs_respect_source_domains():
    for pid,spec in BATCH.items():
        rng = random.Random(4047+pid)
        cases = [a for a,_ in spec['examples']] + spec['boundaries']
        cases += [a for a,_ in spec['stress']] + [spec['generator'](rng) for _ in range(500)]
        for args in cases:
            if pid == 148:
                assert len(args[0]) <= 50000 and all(-100000 <= v <= 100000 for v in args[0])
            elif pid == 149:
                assert 1 <= len(args[0]) <= 300
                assert len({tuple(p) for p in args[0]}) == len(args[0])
                assert all(len(p)==2 and all(type(v) is int and -10000 <= v <= 10000 for v in p) for p in args[0])
            elif pid == 156:
                nodes = positions(args[0])
                assert flatten(nodes) == args[0] and len(nodes) <= 10
                assert all(1 <= v <= 10 for v in nodes.values())
                for path in nodes:
                    if path and path[-1] == 1:
                        assert path[:-1]+(0,) in nodes
                        assert path+(0,) not in nodes and path+(1,) not in nodes
            elif pid == 164:
                assert 1 <= len(args[0]) <= 100000 and all(0 <= v <= 10**9 for v in args[0])
            elif pid == 186:
                text = ''.join(args[0])
                assert 1 <= len(args[0]) <= 100000 and all(len(c)==1 for c in args[0])
                assert all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ' for c in text)
                assert not text.startswith(' ') and not text.endswith(' ') and '  ' not in text
            elif pid == 189:
                assert 1 <= len(args[0]) <= 100000 and all(-2**31 <= v < 2**31 for v in args[0])
                assert 0 <= args[1] <= 100000
            else:
                assert len(args[0]) <= 10000 and all(1 <= v <= 50 for v in args[0])
                assert 0 <= args[1] <= 50


def test_bottom_up_merging_exhausts_short_lists_and_retains_reference_nodes():
    solve = function(SORT,'sort_linked_list')
    for length in range(8):
        for values in product((-1,0,1),repeat=length):
            head = _listnode(list(values))
            before, current = [], head
            while current:
                before.append(current)
                current = current.next
            result = solve(head)
            assert _serialize(result,'listnode') == sorted(values)
            after, current = [], result
            while current:
                after.append(current)
                current = current.next
            assert set(map(id,before)) == set(map(id,after))
            # Stability is a reference property, not an extra source judge restriction.
            assert after == sorted(before,key=lambda node:node.val)


def test_exact_lines_match_every_subset_of_a_three_by_three_grid():
    solve = function(POINTS,'max_points_on_line')
    grid = [[x,y] for x in range(-1,2) for y in range(-1,2)]
    for size in range(1,10):
        for selected in combinations(grid,size):
            expected = points_oracle([selected])
            assert solve(selected) == expected == solve(selected[::-1])
    assert solve([[0,0],[10000,9999],[9999,9998]]) == 2
    assert solve([[0,0],[0,1],[0,-1],[0,3]]) == 4
    # Independent geometric bounds for large fixtures: one line, then a 30x10 grid.
    # A nonvertical line intersects each of 30 columns at most once; vertical <=10.
    for args,expected in BATCH[149]['stress']:
        assert solve(*args) == expected


def test_recursive_upside_down_checks_every_valid_shape_and_original_node_order():
    problem = get_catalog()['leetcode-156']
    for depth in range(10):
        for mask in range(1 << depth):
            if depth+1+mask.bit_count() > 10:
                continue
            paths = [(0,)*i for i in range(depth+1)]
            paths += [(0,)*i+(1,) for i in range(depth) if mask & (1 << i)]
            for repeated in (False,True):
                tree = flatten({path:1 if repeated else i+1 for i,path in enumerate(paths)})
                args = [tree]
                case = Case(id='valid-shape',arguments=args,expected=upside_oracle(args),
                            expected_node_order=upside_node_order(args))
                assert run_source(problem.reference_solution,problem,case) == (True,None)
    # Same values and correct output shape do not justify exchanging original nodes.
    case = Case(id='equal-values',arguments=[[1,1,1]],expected=[1,1,1],expected_node_order=[1,2,0])
    assert run_source('def upside_down_tree(root):\n    return root',problem,case) == (False,None)
    assert run_source('def upside_down_tree(root):\n    return TreeNode(1,TreeNode(1),TreeNode(1))',problem,case) == (False,None)


def test_bucket_gap_matches_sorted_neighbors_on_all_small_arrays_and_large_cases():
    solve = function(GAP,'maximum_gap')
    for length in range(1,6):
        for values in product(range(6),repeat=length):
            assert solve(values) == gap_oracle([values])
    for args,expected in BATCH[164]['stress']:
        assert solve(*args) == expected == gap_oracle(args)
    assert 'sorted(' not in GAP and '.sort(' not in GAP


def test_word_and_array_mutation_are_not_existing_return_a_copy_contracts():
    words = function(WORDS,'reverse_words_in_place')
    for length in range(1,6):
        for tokens in product(('a','BC','2d'),repeat=length):
            chars = list(' '.join(tokens))
            expected = words_oracle([chars])
            assert words(chars) is None and chars == expected
    rotate = function(ROTATE,'rotate_array')
    for length in range(1,8):
        for k in range(15):
            values = list(range(length))
            expected = values[:]
            for _ in range(k):
                expected.insert(0,expected.pop())
            assert rotate(values,k) is None and values == expected
    old = get_catalog()['rotate-values-right']
    new = get_catalog()['leetcode-189']
    assert old.signature.result_mode == 'return' and old.version == 1
    assert new.signature.result_mode == 'mutated_argument'
    assert get_catalog()['leetcode-151'].signature.parameters[0].annotation == 'str'
    assert get_catalog()['leetcode-186'].signature.parameters[0].annotation == 'list[str]'
    for pid in (186,189):
        problem = get_catalog()[f'leetcode-{pid}']
        assert run_source(problem.known_wrong_solutions[1],problem,problem.tests[0]) == (False,None)


def test_deletion_exhausts_short_lists_including_adjacent_head_and_tail_matches():
    solve = function(REMOVE,'remove_list_elements')
    for length in range(8):
        for values in product((1,2,3),repeat=length):
            for target in (0,1,2,3,4):
                actual = _serialize(solve(_listnode(list(values)),target),'listnode')
                assert actual == [v for v in values if v != target]
