import ast
from itertools import product
import json
from pathlib import Path
import random

import pytest

from code_practice.import_batch_043 import BATCH, encoding_oracle
from code_practice.schemas import ProblemDefinition, TestCase as Case, decode_short_encoding
from code_practice.validation import compare, run_source

ROOT = Path(__file__).resolve().parent.parent


def problem():
    return ProblemDefinition.model_validate(json.loads((ROOT/'catalog_import/candidates/leetcode-471.json').read_text()))


def worker_functions():
    source = (ROOT/'frontend/public/judge-worker.js').read_text().split('runPythonAsync(`',1)[1].split('`);',1)[0]
    parsed = ast.parse(source)
    functions = [n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in {'decode_short_encoding','matches'}]
    namespace = {}
    exec(compile(ast.Module(body=functions,type_ignores=[]),'<worker-functions>','exec'),namespace)
    return namespace


def grammar_encodings(bound=8, decoded_bound=10):
    """Construct grammar trees with known meanings; never call either decoder."""
    by_length = [{} for _ in range(bound+1)]
    by_length[1] = {'a':'a','b':'b'}
    for size in range(2,bound+1):
        options = by_length[size]
        for split in range(1,size):
            for left,a in by_length[split].items():
                for right,b in by_length[size-split].items():
                    if len(a)+len(b) <= decoded_bound:
                        options[left+right] = a+b
        for count in range(1,decoded_bound+1):
            body_size = size-len(str(count))-2
            if body_size > 0:
                for body,meaning in by_length[body_size].items():
                    if count*len(meaning) <= decoded_bound:
                        options[f'{count}[{body}]'] = meaning*count
    return {encoded:meaning for group in by_length for encoded,meaning in group.items()}


def test_decoders_and_optimum_oracle_against_constructed_grammar():
    worker = worker_functions()
    encodings = grammar_encodings()
    minima = {}
    for encoded,meaning in encodings.items():
        assert decode_short_encoding(encoded) == meaning
        assert worker['decode_short_encoding'](encoded) == meaning
        minima[meaning] = min(minima.get(meaning,len(meaning)),len(encoded))
    assert len(encodings) > 1000
    for meaning,best_length in minima.items():
        expected = encoding_oracle([meaning])
        # A better encoding cannot escape this enumeration: it would be shorter than 8.
        if best_length <= 8:
            assert len(expected) == best_length
            assert decode_short_encoding(expected) == meaning
    for size in range(1,8):
        for chars in product('a2[]',repeat=size):
            text = ''.join(chars)
            assert worker['decode_short_encoding'](text) == decode_short_encoding(text)


@pytest.mark.parametrize('bad',[None,True,3,[],{},'', '0[a]', '2[]','[a]','2[a','a]',
    '2a','a2','-2[a]','2[a]3','2[A]','2[é]','2[a b]','2[a][b]','999999999999[a]',
    '150[150[a]]','9[9[9[a]]]','a'*151,'__import__("os")'])
def test_malformed_and_excessive_encodings_are_bounded(bad):
    assert decode_short_encoding(bad) is None
    worker = worker_functions()
    assert worker['decode_short_encoding'](bad) is None
    assert not compare(bad,'10[a]','shortest_encoding')
    assert not worker['matches'](bad,'10[a]','shortest_encoding')


def test_ties_no_savings_and_exact_decoded_meaning():
    worker = worker_functions()
    for candidate in ('10[a]','a9[a]','9[a]a'):
        assert compare(candidate,'10[a]','shortest_encoding')
        assert worker['matches'](candidate,'10[a]','shortest_encoding')
    for candidate in ('aaaaaaaaaa','5[aa]','10[b]','2[5[a]]','9[a]','0[aa]'):
        # 5[aa] is actually another equally short answer (length 5), not an error.
        expected = candidate == '5[aa]'
        assert compare(candidate,'10[a]','shortest_encoding') == expected
        assert worker['matches'](candidate,'10[a]','shortest_encoding') == expected
    assert compare('aaaa','aaaa','shortest_encoding')
    assert not compare('4[a]','aaaa','shortest_encoding')
    assert decode_short_encoding('150[a]') == 'a'*150
    assert decode_short_encoding('1[1[a]]') == 'a'
    assert decode_short_encoding('2[a]',1) is None


@pytest.mark.parametrize('change',['wrong-text','malformed','expanded','no-savings','empty-input','bad-input',
    'huge-input','mixed','return-type','input-type','input-adapter','result-mode','arg-count'])
def test_schema_binds_encoding_expectations_to_source_text(change):
    payload = problem().model_dump(mode='json')
    case = payload['tests'][0]
    if change=='wrong-text': case['expected']='bbb'
    elif change=='malformed': case['expected']='2[a'
    elif change=='expanded': case['expected']='150[150[a]]'
    elif change=='no-savings': case.update(arguments=['aaaa'],expected='4[a]')
    elif change=='empty-input': case['arguments']=['']
    elif change=='bad-input': case['arguments']=['1[a]']
    elif change=='huge-input': case['arguments']=['a'*151]
    elif change=='mixed': case['comparator']='exact'
    elif change=='return-type': payload['signature']['returns']='list[str]'
    elif change=='input-type': payload['signature']['parameters'][0]['annotation']='int'
    elif change=='input-adapter': payload['signature']['parameters'][0]['adapter']='listnode'
    elif change=='result-mode':
        payload['signature'].update(result_mode='mutated_argument',mutated_parameter=0)
    else: case['arguments']=['aaa','aaa']
    with pytest.raises(ValueError,match='Shortest-encoding'):
        ProblemDefinition.model_validate(payload)


def test_import_reference_exhaustive_small_inputs_and_maximum_cases():
    p = problem(); namespace={}
    exec(p.reference_solution,namespace)
    solve = namespace[p.signature.name]
    for size in range(1,11):
        for chars in product('ab',repeat=size):
            text = ''.join(chars)
            assert compare(solve(text),encoding_oracle([text]),'shortest_encoding')
    assert all(run_source(p.reference_solution,p,t)==(True,None) for t in p.tests)
    for wrong in p.known_wrong_solutions:
        outcomes = [run_source(wrong,p,t) for t in p.tests]
        assert (False,None) in outcomes and all(error is None for _,error in outcomes)
    spec=BATCH[471];rng=random.Random(4518)
    args = [a for a,_ in spec['examples']]+spec['boundaries']+[a for a,_ in spec['stress']]
    args += [spec['generator'](rng) for _ in range(500)]
    assert all(len(a)==1 and 1<=len(a[0])<=150 and all('a'<=c<='z' for c in a[0]) for a in args)
    assert sum(t.visible for t in p.tests)==2 and sum(not t.visible for t in p.tests)>=12
    tied=Case(id='tied',arguments=['a'*10],expected='10[a]',comparator='shortest_encoding')
    assert run_source("def shortest_encoding(s):\n    return 'a9[a]'",p,tied)==(True,None)
