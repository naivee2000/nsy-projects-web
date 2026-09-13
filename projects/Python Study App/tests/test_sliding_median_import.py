import ast
from copy import deepcopy
from itertools import product
import json
import math
from pathlib import Path
import random

import pytest

from code_practice.import_batch_045 import BATCH, median_oracle
from code_practice.schemas import ProblemDefinition
from code_practice.validation import compare, run_source

ROOT = Path(__file__).resolve().parent.parent


def problem():
    return ProblemDefinition.model_validate(json.loads((ROOT/'catalog_import/candidates/leetcode-480.json').read_text()))


def reference():
    namespace = {}
    exec(BATCH[480]['reference'],namespace)
    return namespace[BATCH[480]['name']]


def worker_compare():
    source = (ROOT/'frontend/public/judge-worker.js').read_text().split('runPythonAsync(`',1)[1].split('`);',1)[0]
    functions = [n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in {'finite_number','matches'}]
    namespace = {'math':math}
    exec(compile(ast.Module(body=functions,type_ignores=[]),'<decimal-worker>','exec'),namespace)
    return namespace['matches']


@pytest.mark.parametrize('actual,expected,accepted',[
    ([1,-0.5,3.0],[1.0,-0.5,3],True),([],[],True),
    ([1e-5],[0],True),([math.nextafter(1e-5,0)],[0],True),
    ([math.nextafter(1e-5,math.inf)],[0],False),([-1e-5],[0],True),
    ([1e9+1e-6],[1e9],True),([1e9+1e-4],[1e9],False),
    ([-0.500009],[-0.5],True),([-0.50002],[-0.5],False),
    ([True],[1],False),([False],[0],False),(['1'],[1],False),
    ([None],[0],False),([float('nan')],[0],False),([float('inf')],[0],False),
    ([float('-inf')],[0],False),([10**400],[1],False),
    ([1],[1,float('nan')],False),([1],[float('inf')],False),
    ([2,1],[1,2],False),([1],[1,2],False),([1,2,2],[1,2],False),
    ([[1]],[1],False),((1,),[1],False),(None,[1],False),
])
def test_decimal_list_native_worker_parity_and_absolute_boundaries(actual,expected,accepted):
    assert compare(actual,expected,'float_list') is accepted
    assert worker_compare()(actual,expected,'float_list') is accepted


@pytest.mark.parametrize('bad',[[True],['1'],[None],[float('nan')],[float('inf')],[10**400],[[1]],1])
def test_decimal_schema_rejects_invalid_expectations(bad):
    payload = problem().model_dump()
    payload['tests'][0]['expected'] = bad
    with pytest.raises(ValueError,match='finite numbers'):
        ProblemDefinition.model_validate(payload)


@pytest.mark.parametrize('change',['return_type','comparator','mode'])
def test_decimal_schema_requires_a_consistent_return_contract(change):
    payload = problem().model_dump()
    if change == 'return_type': payload['signature']['returns']='list[int]'
    elif change == 'comparator': payload['tests'][0]['comparator']='exact'
    else:
        payload['signature']['result_mode']='mutated_argument'
        payload['signature']['mutated_parameter']=0
    with pytest.raises(ValueError): ProblemDefinition.model_validate(payload)


def test_sliding_median_reference_and_both_logically_wrong_algorithms():
    p = problem()
    assert p.difficulty == 8 and len(p.hints)==4 and p.editorial
    assert sum(t.visible for t in p.tests)==2 and sum(not t.visible for t in p.tests)>=12
    assert all(run_source(p.reference_solution,p,t)==(True,None) for t in p.tests)
    for wrong in p.known_wrong_solutions:
        results=[run_source(wrong,p,t) for t in p.tests]
        assert (False,None) in results and all(e is None for _,e in results)


def test_medians_exhaust_short_arrays_all_window_widths():
    solve = reference()
    for size in range(1,7):
        for nums in product((-2,-1,0,1,2),repeat=size):
            values=list(nums)
            for k in range(1,size+1):
                assert solve(values,k)==median_oracle([values,k])


def test_median_inputs_outputs_and_maximum_boundaries_preserve_source_domain():
    solve = reference(); spec=BATCH[480];rng=random.Random(4527)
    args=[a for a,_ in spec['examples']]+spec['boundaries']+[a for a,_ in spec['stress']]+[spec['generator'](rng) for _ in range(500)]
    for nums,k in args:
        assert 1<=k<=len(nums)<=100000
        assert all(type(v) is int and -2**31<=v<=2**31-1 for v in nums)
    for args,expected in spec['stress']:
        before=deepcopy(args);actual=solve(*args)
        assert actual==expected and args==before
        assert len(actual)==len(args[0])-args[1]+1
    assert solve([-2**31,2**31-1],2)==[-0.5]


def test_median_prerequisites_have_existing_preparatory_topics_and_source_correction():
    entries=json.loads((ROOT/'catalog_data/manifest.json').read_text())['entries']
    topics={t for e in entries if e['id']!='leetcode-480' for t in e['topics']}
    assert set(BATCH[480]['prerequisites'])<=topics
    assert '0.00001' in BATCH[480]['statement']
    assert '10^-4' in BATCH[480]['editorial'] and '10^-5' in BATCH[480]['editorial']


def test_helper_class_is_allowed_behind_the_function_entry_point():
    source = '''
class MedianHelper:
    def solve(self, nums, k):
        result = []
        for i in range(len(nums)-k+1):
            window = sorted(nums[i:i+k])
            result.append((window[(k-1)//2]+window[k//2])/2)
        return result
def sliding_window_medians(nums, k):
    return MedianHelper().solve(nums, k)
'''
    p=problem()
    assert all(run_source(source,p,t)==(True,None) for t in p.tests if t.visible)
