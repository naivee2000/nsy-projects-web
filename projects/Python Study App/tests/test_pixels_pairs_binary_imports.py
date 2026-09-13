from collections import Counter
from copy import deepcopy
from itertools import combinations,product
import json
from math import ceil,log2
from pathlib import Path
import random
import re

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_054 import BATCH,clock_string,singleton_input
from code_practice.learning import review_focus_boost
from code_practice.reconcile_overlaps import check_single_pixels
from code_practice.validation import run_source


def reference(pid):
    scope={};exec(BATCH[pid]['reference'],scope)
    return scope[BATCH[pid]['name']]


@pytest.mark.parametrize('pid',BATCH)
def test_batch_54_references_and_two_logically_wrong_algorithms(pid):
    p=get_catalog()[f'leetcode-{pid}']
    assert len(p.hints)==4 and p.editorial
    assert sum(t.visible for t in p.tests)==2 and sum(not t.visible for t in p.tests)>=12
    assert all(run_source(p.reference_solution,p,t)==(True,None) for t in p.tests)
    for wrong in p.known_wrong_solutions:
        results=[run_source(wrong,p,t) for t in p.tests]
        assert (False,None) in results and all(error is None for _,error in results)


@pytest.mark.parametrize('pid',BATCH)
def test_batch_54_domains_stress_and_input_preservation(pid):
    spec=BATCH[pid];solve=reference(pid);rng=random.Random(4047+pid)
    cases=[a for a,_ in spec['examples']]+spec['boundaries']+[a for a,_ in spec['stress']]
    cases += [spec['generator'](rng) for _ in range(500)]
    for args in cases:
        if pid==532:
            nums,k=args
            assert 1<=len(nums)<=10000 and 0<=k<=10**7 and all(type(v) is int and abs(v)<=10**7 for v in nums)
        elif pid==533:
            board,target=args;rows=len(board);cols=len(board[0])
            assert 1<=rows<=500 and 1<=cols<=500 and 1<=target<=min(rows,cols)
            assert all(len(row)==cols and set(row)<=set('BW') for row in board)
        elif pid==537:
            for text in args:
                assert re.fullmatch(r'-?\d+\+-?\d+i',text)
                assert all(abs(int(v))<=100 for v in text[:-1].split('+'))
        elif pid==539:
            assert 2<=len(args[0])<=20000
            assert all(re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',t) for t in args[0])
        elif pid==540:
            nums=args[0];counts=Counter(nums)
            assert 1<=len(nums)<=100000 and len(nums)%2==1 and nums==sorted(nums)
            assert sum(c==1 for c in counts.values())==1 and all(c in (1,2) for c in counts.values())
            assert all(type(v) is int and 0<=v<=100000 for v in nums)
        else:
            s,k=args
            assert 1<=len(s)<=10000 and set(s)<=set('abcdefghijklmnopqrstuvwxyz') and 1<=k<=10000
    for args,expected in spec['stress']:
        copied=deepcopy(args);assert solve(*copied)==expected and copied==args


def test_k_pairs_exhaustive_signed_values_and_duplicate_multiplicity():
    solve=reference(532)
    for length in range(1,8):
        for values in product((-1,0,1),repeat=length):
            for k in range(4):assert solve(values,k)==BATCH[532]['oracle']([values,k])
    assert solve([1,1,1,2],0)==1 and solve([1,2],0)==0


def column_pixel_certificate(board,target):
    row_counts=[row.count('B') for row in board];answer=0
    for c in range(len(board[0])):
        owners=[r for r,row in enumerate(board) if row[c]=='B']
        if len(owners)!=target:continue
        first=board[owners[0]]
        if all(board[r]==first for r in owners):answer+=sum(row_counts[r]==target for r in owners)
    return answer


def test_pixels_exhaustive_rectangles_and_large_independent_column_certificate():
    solve=reference(533)
    for rows,cols in ((1,1),(1,4),(4,1),(2,3),(3,2),(3,3)):
        for cells in product('BW',repeat=rows*cols):
            board=[list(cells[r*cols:(r+1)*cols]) for r in range(rows)]
            for target in range(1,min(rows,cols)+1):
                assert solve(board,target)==BATCH[533]['oracle']([board,target])==column_pixel_certificate(board,target)
    for args,expected in BATCH[533]['stress']:
        assert solve(*args)==expected==column_pixel_certificate(*args)
    assert solve([list('BBW'),list('BWB'),list('WBB')],2)==0
    assert solve([list('BB'),list('BB')],2)==4


def repeated_complex_oracle(a,b,c,d):
    # Add a+bi c times, then its quarter turn -b+ai d times, including signs.
    real=imag=0
    for _ in range(abs(c)):
        sign=1 if c>=0 else -1;real+=sign*a;imag+=sign*b
    for _ in range(abs(d)):
        sign=1 if d>=0 else -1;real-=sign*b;imag+=sign*a
    return f'{real}+{imag}i'


def test_complex_signs_zeroes_cross_terms_and_extreme_components():
    solve=reference(537)
    for a,b,c,d in product((-100,-3,-1,0,1,3,100),repeat=4):
        args=[f'{a}+{b}i',f'{c}+{d}i']
        assert solve(*args)==BATCH[537]['oracle'](args)==repeated_complex_oracle(a,b,c,d)
    assert solve('1+-1i','1+-1i')=='0+-2i'
    assert solve('-100+100i','100+100i')=='-20000+0i'


def test_clock_all_possible_gaps_rotations_duplicates_and_pigeonhole():
    solve=reference(539)
    for start in (0,1,59,60,719,720,1439):
        for gap in range(1440):
            times=[clock_string(start),clock_string((start+gap)%1440)]
            assert solve(times)==min(gap,1440-gap)==BATCH[539]['oracle']([times])
    rng=random.Random(539)
    for _ in range(200):
        minutes=rng.sample(range(1440),rng.randint(2,30));shift=rng.randrange(1440)
        a=[clock_string(v) for v in minutes];b=[clock_string((v+shift)%1440) for v in minutes]
        assert solve(a)==solve(b)==BATCH[539]['oracle']([a])
        assert solve(a+[a[0]])==0
    assert solve([clock_string(i%1440) for i in range(20000)])==0


class ReadProbe:
    def __init__(self,values):self.values=values;self.reads=0;self.limit=2*ceil(log2(len(values)))+1
    def __len__(self):return len(self.values)
    def __getitem__(self,index):
        assert type(index) is int,'No slices in logarithmic search'
        self.reads+=1
        assert self.reads<=self.limit,'Exceeded logarithmic element-read bound'
        return self.values[index]
    def __iter__(self):raise AssertionError('No linear iteration in logarithmic search')


def test_sorted_singleton_exhaustive_positions_and_logarithmic_reads():
    solve=reference(540)
    for size in range(1,8):
        for values in combinations(range(0,28,4),size):
            for single in values:
                nums=singleton_input(values,single);observed=ReadProbe(nums)
                assert solve(observed)==single==BATCH[540]['oracle']([nums])
    for size in (1,2,3,8,31,257,4096,50000):
        for index in {0,size//2,size-1}:
            nums=singleton_input(list(range(size)),index);observed=ReadProbe(nums)
            assert solve(observed)==index and observed.reads<=2*ceil(log2(len(nums)))+1
    p=get_catalog()['leetcode-136'];scope={};exec(p.reference_solution,scope)
    with pytest.raises(AssertionError,match='linear iteration'):
        scope[p.signature.name](ReadProbe(singleton_input(list(range(50000)),25000)))
    assert review_focus_boost(get_catalog()['leetcode-540'])>=50


def test_alternating_reverse_every_short_binary_string_and_tail_size():
    solve=reference(541)
    for n in range(1,10):
        for chars in product('ab',repeat=n):
            text=''.join(chars)
            for k in range(1,12):assert solve(text,k)==BATCH[541]['oracle']([text,k])
    assert solve('abcdefgh',3)=='cbadefhg' and solve('abcd',2)=='bacd'


def test_single_pixel_overlap_requires_full_source_board_domain():
    root=Path(__file__).resolve().parent.parent
    source=next(s for s in map(json.loads,(root/'catalog_import/sources.jsonl').read_text().splitlines()) if s['source_id']==531)
    payload=get_catalog()['leetcode-533'].model_dump(mode='json');report=check_single_pixels(payload,source)
    assert report['oracle_inputs']==500 and report['largest_input']==[500,500]
    with pytest.raises(ValueError,match='500x500'):
        check_single_pixels({**payload,'constraints':['Only 200x200 boards']},source)
    wrong=payload['reference_solution'].replace('from collections import Counter','picture=[row[:200] for row in picture[:200]]\n    from collections import Counter')
    with pytest.raises(ValueError,match='disagrees'):
        check_single_pixels({**payload,'reference_solution':wrong},source)
    assert 'leetcode-531' not in get_catalog()
