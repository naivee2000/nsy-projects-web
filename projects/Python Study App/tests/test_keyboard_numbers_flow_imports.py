from collections import Counter,deque
from copy import deepcopy
from itertools import permutations,product
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_051 import BATCH,divisor_sum_certificate,parallel_successors,rank_label
from code_practice.learning import review_focus_boost
from code_practice.validation import run_source


def reference(pid):
    scope={};exec(BATCH[pid]['reference'],scope)
    return scope[BATCH[pid]['name']]


@pytest.mark.parametrize('pid',BATCH)
def test_batch_51_references_and_logically_wrong_algorithms(pid):
    problem=get_catalog()[f'leetcode-{pid}']
    assert len(problem.hints)==4 and problem.editorial
    assert sum(t.visible for t in problem.tests)==2 and sum(not t.visible for t in problem.tests)>=12
    assert all(run_source(problem.reference_solution,problem,t)==(True,None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        results=[run_source(wrong,problem,t) for t in problem.tests]
        assert (False,None) in results and all(error is None for _,error in results)


@pytest.mark.parametrize('pid',BATCH)
def test_batch_51_fixture_and_generator_domains(pid):
    spec=BATCH[pid];rng=random.Random(4047+pid)
    cases=[a for a,_ in spec['examples']]+spec['boundaries']+[a for a,_ in spec['stress']]
    cases += [spec['generator'](rng) for _ in range(500)]
    for (value,) in cases:
        if pid==500:
            assert 1<=len(value)<=20
            assert all(1<=len(w)<=100 and all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in w) for w in value)
        elif pid==504:assert type(value) is int and abs(value)<=10**7
        elif pid==506:
            assert 1<=len(value)<=10000 and len(set(value))==len(value)
            assert all(type(v) is int and 0<=v<=10**6 for v in value)
        elif pid==507:assert type(value) is int and 1<=value<=10**8
        elif pid==516:assert 1<=len(value)<=1000 and set(value)<=set('abcdefghijklmnopqrstuvwxyz')
        else:assert 1<=len(value)<=10000 and all(type(v) is int and 0<=v<=100000 for v in value)


@pytest.mark.parametrize('pid',BATCH)
def test_batch_51_maximum_results_and_no_input_mutation(pid):
    solve=reference(pid)
    for args,expected in BATCH[pid]['stress']:
        copy=deepcopy(args);actual=solve(*copy)
        assert (sorted(actual) if pid==500 else actual)==(sorted(expected) if pid==500 else expected)
        assert copy==args
        if pid==507:assert actual==(divisor_sum_certificate(args[0])==2*args[0])


def test_keyboard_exhaustive_mixed_case_words_and_multiplicity():
    solve=reference(500)
    for length in range(1,5):
        for chars in product('qQaAzZ',repeat=length):
            word=''.join(chars)
            assert solve([word])==BATCH[500]['oracle']([[word]])
    assert solve(['TYPE','type','TYPE','omk'])==['TYPE','type','TYPE']


def test_base_seven_exhaustive_small_integers_and_full_range_roundtrip():
    solve=reference(504)
    nums=list(range(-10000,10001));rng=random.Random(504)
    nums += [rng.randint(-10**7,10**7) for _ in range(1000)]
    for n in nums:
        result=solve(n)
        assert int(result,7)==n and result==BATCH[504]['oracle']([n])
        assert result=='0' or result.lstrip('-')[0]!='0'
        assert (result.startswith('-'))==(n<0)


def test_rank_order_exhaustive_and_maximum_permutation_certificate():
    solve=reference(506)
    for n in range(1,8):
        for values in permutations(range(n)):
            assert solve(list(values))==BATCH[506]['oracle']([values])
    values=[(i*7919)%10000 for i in range(10000)]
    assert len(set(values))==10000
    assert solve(values)==[rank_label(10000-v) for v in values]


def test_perfect_number_sieve_and_factorization_certificates():
    solve=reference(507);sums=[0]*20001
    for d in range(1,10001):
        for multiple in range(d*2,20001,d):sums[multiple]+=d
    for n in range(1,20001):
        assert solve(n)==(sums[n]==n)
        assert divisor_sum_certificate(n)==sums[n]+n
    assert solve(33550336) is True
    assert solve(12) is False and solve(1) is False
    rng=random.Random(507)
    for _ in range(500):
        n=rng.randint(1,10**8)
        assert solve(n)==(divisor_sum_certificate(n)==2*n)


def lcs_length(a,b):
    previous=[0]*(len(b)+1)
    for x in a:
        current=[0]
        for j,y in enumerate(b):
            current.append(previous[j]+1 if x==y else max(previous[j+1],current[-1]))
        previous=current
    return previous[-1]


def test_palindromic_subsequence_exhaustive_and_independent_large_dp():
    solve=reference(516)
    for n in range(1,10):
        for chars in product('ab',repeat=n):
            word=''.join(chars)
            assert solve(word)==BATCH[516]['oracle']([word])
    rng=random.Random(516)
    for _ in range(5):
        word=''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(1000))
        assert solve(word)==lcs_length(word,word[::-1])
    assert solve('bbbab')==4 and solve('abcab')==3
    assert review_focus_boost(get_catalog()['leetcode-516'])>=50


def compositions(total,n):
    if n==1:
        yield (total,);return
    for first in range(total+1):
        for rest in compositions(total-first,n-1):yield (first,*rest)


def test_washing_exhaustive_small_parallel_games():
    solve=reference(517);checked=0
    for n in range(1,5):
        for total in range(9):
            for state in compositions(total,n):
                assert solve(list(state))==BATCH[517]['oracle']([state])
                checked+=1
    assert checked==714


def can_balance_in(loads,rounds):
    """Independent time-expanded integer max-flow: each sender has capacity one."""
    n=len(loads);total=sum(loads)
    if total%n:return False
    count=n*(rounds+1)+n*rounds+2;source=count-2;sink=count-1
    graph=[[] for _ in range(count)]
    def edge(a,b,capacity):
        graph[a].append([b,capacity,len(graph[b])]);graph[b].append([a,0,len(graph[a])-1])
    for i,load in enumerate(loads):edge(source,i,load)
    for t in range(rounds):
        for i in range(n):
            node=t*n+i;gate=n*(rounds+1)+t*n+i
            edge(node,(t+1)*n+i,total)
            edge(node,gate,1)
            for j in (i-1,i+1):
                if 0<=j<n:edge(gate,(t+1)*n+j,1)
    for i in range(n):edge(rounds*n+i,sink,total//n)
    flow=0
    while flow<total:
        levels=[-1]*count;levels[source]=0;queue=deque([source])
        while queue:
            a=queue.popleft()
            for b,capacity,_ in graph[a]:
                if capacity and levels[b]<0:levels[b]=levels[a]+1;queue.append(b)
        if levels[sink]<0:return False
        index=[0]*count
        def augment(a,amount):
            if a==sink:return amount
            while index[a]<len(graph[a]):
                item=graph[a][index[a]];b,capacity,reverse=item
                if capacity and levels[b]==levels[a]+1:
                    sent=augment(b,min(amount,capacity))
                    if sent:
                        item[1]-=sent;graph[b][reverse][1]+=sent;return sent
                index[a]+=1
            return 0
        while sent:=augment(source,total-flow):flow+=sent
    return True


def test_washing_time_expanded_flow_certifies_optimum():
    solve=reference(517);rng=random.Random(517)
    cases=[[0,3,0],[3,0,3],[1,0,5],[0,0,0,4]]
    for _ in range(100):
        loads=[rng.randrange(9) for _ in range(rng.randint(2,8))]
        loads[-1]+=(-sum(loads))%len(loads);cases.append(loads)
    for loads in cases:
        answer=solve(loads)
        assert can_balance_in(loads,answer)
        if answer:assert not can_balance_in(loads,answer-1)


def test_simultaneous_send_receive_and_flow_bottlenecks():
    assert (2,2,2) in set(parallel_successors((3,0,3)))
    assert (1,1,1) not in set(parallel_successors((0,3,0)))
    assert (0,0,1) not in set(parallel_successors((1,0,0)))
    assert (2,1,3) in set(parallel_successors((1,1,4)))
    problem=get_catalog()['leetcode-517'];catalog=get_catalog()
    assert problem.difficulty>=8
    assert reference(517)([100000]*5000+[0]*5000)==250000000
    for topic in problem.prerequisites:assert any(p.difficulty<8 and topic in p.topics for p in catalog.values())
