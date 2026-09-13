from bisect import bisect_right
from copy import deepcopy
from itertools import permutations,product
import json
from pathlib import Path
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_052 import BATCH,arrangement_permanent,subsequences
from code_practice.learning import review_focus_boost
from code_practice.reconcile_original_overlaps import adapted_function,target_payload,contiguous_oracle
from code_practice.reconcile_overlaps import check_two_uncommon
from code_practice.validation import run_source


def reference(pid):
    scope={};exec(BATCH[pid]['reference'],scope)
    return scope[BATCH[pid]['name']]


@pytest.mark.parametrize('pid',BATCH)
def test_batch_52_reference_and_two_algorithmic_failures(pid):
    p=get_catalog()[f'leetcode-{pid}']
    assert len(p.hints)==4 and p.editorial
    assert sum(t.visible for t in p.tests)==2 and sum(not t.visible for t in p.tests)>=12
    assert all(run_source(p.reference_solution,p,t)==(True,None) for t in p.tests)
    for wrong in p.known_wrong_solutions:
        results=[run_source(wrong,p,t) for t in p.tests]
        assert (False,None) in results and all(error is None for _,error in results)


@pytest.mark.parametrize('pid',BATCH)
def test_batch_52_fixture_generator_domains_and_stress(pid):
    spec=BATCH[pid];rng=random.Random(4047+pid);solve=reference(pid)
    cases=[a for a,_ in spec['examples']]+spec['boundaries']+[a for a,_ in spec['stress']]
    cases += [spec['generator'](rng) for _ in range(500)]
    for args in cases:
        if pid==520:
            assert 1<=len(args[0])<=100 and all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in args[0])
        elif pid==522:
            assert 2<=len(args[0])<=50 and all(1<=len(w)<=100 and set(w)<=set('abcdefghijklmnopqrstuvwxyz') for w in args[0])
        elif pid==524:
            s,words=args
            assert 1<=len(s)<=1000 and 1<=len(words)<=1000
            assert all(1<=len(w)<=1000 and set(w)<=set('abcdefghijklmnopqrstuvwxyz') for w in [s,*words])
        else:assert type(args[0]) is int and 1<=args[0]<=15
    for args,expected in spec['stress']:
        copy=deepcopy(args);assert solve(*copy)==expected and copy==args


def test_capital_every_case_pattern_through_length_twelve():
    solve=reference(520)
    for n in range(1,13):
        for chars in product('aA',repeat=n):
            word=''.join(chars)
            assert solve(word)==BATCH[520]['oracle']([word])


def test_uncommon_exhaustive_small_arrays_count_owners_not_selections():
    solve=reference(522)
    for n in (2,3,4):
        for words in product(('a','b','aa','ab','ba','bb'),repeat=n):
            assert solve(words)==BATCH[522]['oracle']([words])
    assert solve(['aaa','b'])==3
    assert solve(['abc','abc','ac'])==-1
    assert solve(['abc','abc','d'])==1


def next_position_match(word,text):
    # Independent index-list/binary-search certificate for long strings.
    positions={}
    for i,c in enumerate(text):positions.setdefault(c,[]).append(i)
    previous=-1
    for c in word:
        candidates=positions.get(c,[]);index=bisect_right(candidates,previous)
        if index==len(candidates):return False
        previous=candidates[index]
    return True


def test_uncommon_full_extended_domain_against_index_search():
    solve=reference(522);rng=random.Random(522)
    for _ in range(100):
        words=[''.join(rng.choice('ab') for _ in range(rng.randint(1,100))) for _ in range(50)]
        words[-5:]=words[:5]
        expected=max((len(w) for i,w in enumerate(words) if all(i==j or not next_position_match(w,t) for j,t in enumerate(words))),default=-1)
        assert solve(words)==expected


def test_dictionary_exhaustive_ordered_deletions_and_lexical_ties():
    solve=reference(524)
    words=[''.join(chars) for n in range(1,5) for chars in product('ab',repeat=n)]
    for n in range(1,8):
        for chars in product('ab',repeat=n):
            text=''.join(chars)
            for dictionary in (words,words[::-1],words[::2]):
                assert solve(text,dictionary)==BATCH[524]['oracle']([text,dictionary])
    assert solve('bab',['ba','ab','bb'])=='ab'
    assert solve('ab',['ba'])==''


def test_dictionary_large_index_search_certificate():
    solve=reference(524);rng=random.Random(524)
    for _ in range(3):
        text=''.join(rng.choice('abcd') for _ in range(1000))
        words=[''.join(rng.choice('abcde') for _ in range(rng.randint(1,1000))) for _ in range(999)]
        words.append(text[::2])
        expected=min((w for w in words if next_position_match(w,text)),key=lambda w:(-len(w),w),default='')
        assert solve(text,words)==expected


def test_arrangements_literal_permutations_and_entire_fifteen_value_domain():
    solve=reference(526)
    for n in range(1,9):
        literal=sum(all(v%i==0 or i%v==0 for i,v in enumerate(p,1)) for p in permutations(range(1,n+1)))
        assert solve(n)==literal==arrangement_permanent(n)
    problem=get_catalog()['leetcode-526']
    assert sorted(t.arguments[0] for t in problem.tests)==list(range(1,16))
    assert sum(not t.visible for t in problem.tests)==13
    for n in range(1,16):assert solve(n)==arrangement_permanent(n)
    assert solve(15)==24679 and review_focus_boost(problem)>=50


def test_binary_balance_exhaustive_and_original_id_preserved():
    payload=target_payload(525);solve=adapted_function(525,payload)
    assert payload['id']=='longest-target-sum-subarray' and payload['version']==1
    for n in range(1,12):
        for bits in product((0,1),repeat=n):assert solve(bits)==contiguous_oracle([bits])
    assert solve([0]*50000+[1]*50000)==100000
    assert solve([1]+[0]*99998+[1])==2
    assert 'leetcode-525' not in get_catalog()


def test_two_string_overlap_full_domain_and_rejects_old_ten_character_cap():
    root=Path(__file__).resolve().parent.parent
    source=next(s for s in map(json.loads,(root/'catalog_import/sources.jsonl').read_text().splitlines()) if s['source_id']==521)
    payload=get_catalog()['leetcode-522'].model_dump(mode='json')
    evidence=check_two_uncommon(payload,source)
    assert evidence['oracle_inputs']==1000 and evidence['full_domain_generated_inputs']==500
    assert 'leetcode-521' not in get_catalog()
    with pytest.raises(ValueError,match='100-character'):
        check_two_uncommon({**payload,'constraints':['word lengths are at most ten']},source)
    wrong=payload['reference_solution'].replace('best=-1','strs=[w[:10] for w in strs];best=-1')
    with pytest.raises(ValueError,match='disagrees'):
        check_two_uncommon({**payload,'reference_solution':wrong},source)
