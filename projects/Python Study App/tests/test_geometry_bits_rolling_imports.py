from copy import deepcopy
from itertools import combinations, groupby, permutations, product
import random
import string

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_044 import BATCH, cross, magical_prefix, maze_oracle, polygon_oracle
from code_practice.learning import review_focus_boost
from code_practice.validation import run_source


def reference(pid):
    namespace = {}
    exec(BATCH[pid]['reference'], namespace)
    return namespace[BATCH[pid]['name']]


def intersects(a, b, c, d):
    def on(a, b, p):
        return cross(a,b,p) == 0 and all(min(a[i],b[i]) <= p[i] <= max(a[i],b[i]) for i in (0,1))
    if any((on(a,b,c),on(a,b,d),on(c,d,a),on(c,d,b))):
        return True
    return cross(a,b,c)*cross(a,b,d) < 0 and cross(c,d,a)*cross(c,d,b) < 0


def simple_polygon(points):
    n = len(points)
    if len(set(map(tuple,points))) != n:
        return False
    area = sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1]))
    if not area:
        return False
    for i in range(n):
        a,b,c = points[i],points[(i+1)%n],points[(i+2)%n]
        # Adjacent collinear edges may continue straight, but cannot backtrack.
        if cross(a,b,c) == 0 and sum((b[k]-a[k])*(c[k]-b[k]) for k in (0,1)) <= 0:
            return False
        for j in range(i+1,n):
            if j == i+1 or (i == 0 and j == n-1):
                continue
            if intersects(a,b,points[j],points[(j+1)%n]):
                return False
    return True


@pytest.mark.parametrize('pid', BATCH)
def test_batch_44_reference_and_logical_wrong_solutions(pid):
    problem = get_catalog()[f'leetcode-{pid}']
    assert problem.status == 'approved' and len(problem.hints) == 4 and problem.editorial
    assert sum(t.visible for t in problem.tests) == 2
    assert sum(not t.visible for t in problem.tests) >= 12
    assert all(run_source(problem.reference_solution,problem,t) == (True,None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        outcomes = [run_source(wrong,problem,t) for t in problem.tests]
        assert (False,None) in outcomes and all(error is None for _,error in outcomes)


@pytest.mark.parametrize('pid', BATCH)
def test_batch_44_source_domains(pid):
    spec = BATCH[pid]
    rng = random.Random(4047+pid)
    inputs = ([a for a,_ in spec['examples']] + spec['boundaries']
              + [a for a,_ in spec['stress']] + [spec['generator'](rng) for _ in range(500)])
    for args in inputs:
        if pid == 469:
            points = args[0]
            assert 3 <= len(points) <= 10000 and len(set(map(tuple,points))) == len(points)
            assert all(len(p) == 2 and all(type(x) is int and -10000 <= x <= 10000 for x in p) for p in points)
            if len(points) < 100:
                assert simple_polygon(points)
            else:
                # The large fixtures are a rectangular perimeter and a one-unit
                # notch in its upper chain: both chains are x-monotone and disjoint.
                assert points[:2500] == [[i,0] for i in range(2500)]
                assert points[2500:5000] == [[2500,i] for i in range(2500)]
                assert points[7500:] == [[0,2500-i] for i in range(2500)]
                assert all(p[0] == 2500-i and p[1] == (2499 if i == 1250 and points[6250][1] == 2499 else 2500)
                           for i,p in enumerate(points[5000:7500]))
        elif pid == 476:
            # Version 2 additionally supports source 1009's zero input.
            assert type(args[0]) is int and 0 <= args[0] < 2**31
        elif pid == 477:
            assert 1 <= len(args[0]) <= 10000 and all(type(x) is int and 0 <= x <= 10**9 for x in args[0])
            assert 0 <= reference(pid)(*args) < 2**31
        elif pid == 481:
            assert type(args[0]) is int and 1 <= args[0] <= 100000
        elif pid == 482:
            s,k = args
            assert 1 <= len(s) <= 100000 and set(s) <= set(string.ascii_letters+string.digits+'-')
            assert type(k) is int and 1 <= k <= 10000
        else:
            maze,start,destination = args
            assert 1 <= len(maze) <= 100 and 1 <= len(maze[0]) <= 100
            assert all(len(row) == len(maze[0]) and all(type(x) is int and x in (0,1) for x in row) for row in maze)
            assert start != destination
            for p in (start,destination):
                assert len(p) == 2 and 0 <= p[0] < len(maze) and 0 <= p[1] < len(maze[0]) and maze[p[0]][p[1]] == 0


@pytest.mark.parametrize('pid', BATCH)
def test_batch_44_maximum_cases_and_input_preservation(pid):
    solve = reference(pid)
    for args,expected in BATCH[pid]['stress']:
        copied = deepcopy(args)
        assert solve(*copied) == expected
        assert copied == args


def test_polygon_exhaust_simple_boundaries_and_orientation_invariance():
    solve = reference(469)
    grid = list(product(range(3),repeat=2))
    checked = 0
    results = set()
    for n in range(3,7):
        for subset in combinations(grid,n):
            for tail in permutations(subset[1:]):
                points = [subset[0],*tail]
                if not simple_polygon(points):
                    continue
                expected = polygon_oracle([points])
                results.add(expected)
                assert solve(points) == expected
                assert solve(points[::-1]) == expected
                assert solve(points[1:]+points[:1]) == expected
                assert solve([[x*5000-5000,y*5000-5000] for x,y in points]) == expected
                checked += 1
    assert checked > 100 and results == {True,False}
    assert not simple_polygon([[0,0],[2,2],[0,2],[2,0]])
    assert not simple_polygon([[0,0],[2,0],[1,0],[1,2],[0,2]])


def test_significant_bit_complement_exhaust_small_and_31_bit_boundaries():
    solve = reference(476)
    for n in range(1,65536):
        assert solve(n) == BATCH[476]['oracle']([n])
        assert solve(n) >= 0 and solve(n) & n == 0
    for bit in range(31):
        assert solve(1<<bit) == (1<<bit)-1
        assert solve((1<<(bit+1))-1) == 0


def test_hamming_total_counts_index_pairs_and_all_input_bits():
    solve = reference(477)
    for n in range(1,6):
        for nums in product(range(4),repeat=n):
            assert solve(nums) == BATCH[477]['oracle']([nums])
    for bit in range(30):
        nums = [0,0,1<<bit,1<<bit,1<<bit]
        assert solve(nums) == 6
    assert solve([10**9,10**9,0]) == BATCH[477]['oracle']([[10**9,10**9,0]])


def test_magical_oracle_self_description_and_exact_prefix_counts():
    text = magical_prefix(100002)
    assert text.startswith('1221121221221121122')
    runs = [len(list(group)) for _,group in groupby(text)]
    assert set(runs) <= {1,2}
    assert ''.join(map(str,runs[:-1])) == text[:len(runs)-1]
    assert runs[-1] <= int(text[len(runs)-1])
    solve = reference(481)
    for n in [*range(1,1001),*range(10000,100001,5000)]:
        assert solve(n) == text[:n].count('1')
    assert solve(4) == 2  # final run truncated, not three ones in 12211


def test_license_exhaust_short_strings_and_group_shape():
    solve = reference(482)
    for n in range(1,7):
        for chars in product('aB1-',repeat=n):
            s = ''.join(chars)
            for k in range(1,8):
                actual = solve(s,k)
                assert actual == BATCH[482]['oracle']([s,k])
                assert actual.replace('-','') == s.replace('-','').upper()
                if actual:
                    groups = actual.split('-')
                    assert 1 <= len(groups[0]) <= k and all(len(g) == k for g in groups[1:])


def test_rolling_maze_exhaust_all_3_by_3_masks_and_open_endpoint_pairs():
    solve = reference(490)
    checked = 0
    for bits in product((0,1),repeat=9):
        maze = [list(bits[i:i+3]) for i in (0,3,6)]
        opened = [list(divmod(i,3)) for i,b in enumerate(bits) if b == 0]
        for start,destination in permutations(opened,2):
            args = [maze,start,destination]
            assert solve(*args) == maze_oracle(args)
            checked += 1
    assert checked == 9216
    assert solve([[0,0,0,0]],[0,0],[0,2]) is False
    assert solve([[0,0,0,0]],[0,0],[0,3]) is True
    assert review_focus_boost(get_catalog()['leetcode-490']) >= 130


def test_maze_example_route_really_stops_at_the_destination():
    maze,start,destination = BATCH[490]['examples'][0][0]
    r,c = start
    for dr,dc in ((0,-1),(1,0),(0,-1),(1,0),(0,1),(1,0),(0,1)):
        before = r,c
        while 0 <= r+dr < len(maze) and 0 <= c+dc < len(maze[0]) and maze[r+dr][c+dc] == 0:
            r,c = r+dr,c+dc
        assert (r,c) != before
    assert [r,c] == destination
