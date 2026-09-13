from functools import lru_cache
from itertools import combinations, product
import random
import re
import string

from code_practice.catalog import get_catalog
from code_practice.import_batch_002 import positions
from code_practice.import_batch_039 import (
    BATCH, square_oracle, squares_oracle, gene_oracle, interval_oracle,
    paths_oracle, anagrams_oracle, ternary_oracle, compression_oracle,
    linked_sum_oracle, arithmetic_oracle, binary_squares, progression_count,
)
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.schemas import TestCase as Case
from code_practice.validation import ListNode, _listnode, _treenode, _serialize, run_source


def reference(pid):
    namespace = {'ListNode': ListNode}
    exec(BATCH[pid]['reference'], namespace)
    return namespace[BATCH[pid]['name']]


def fixtures(pid):
    spec = BATCH[pid]
    rng = random.Random(4047+pid)
    return ([a for a,_ in spec['examples']] + spec['boundaries']
            + [a for a,_ in spec['stress']] + [spec['generator'](rng) for _ in range(500)])


def collapse_ternary(expression):
    """Reduce innermost syntax with literal replacements, not a reverse token stack."""
    while len(expression)>1:
        following = re.sub(r'([TF])\?([0-9TF]):([0-9TF])(?!\?)',
                           lambda m: m[2] if m[1]=='T' else m[3], expression)
        assert following != expression, 'Invalid ternary grammar'
        expression = following
    assert expression in '0123456789TF'
    return expression


def lexical_rank(n, value):
    """Digit-DP count of bounded decimal strings <= value in text order.

    Independent of the reference's prefix subtree skip/descend procedure.
    """
    target, limit = str(value), str(n)
    total = 0
    for length in range(1,len(limit)+1):
        bound = limit if length==len(limit) else '9'*length
        @lru_cache(None)
        def count(index, tight, relation):
            if index==length:
                return int(relation<0 or relation==0 and length<=len(target))
            result = 0
            maximum = int(bound[index]) if tight else 9
            for digit in range(1 if index==0 else 0,maximum+1):
                comparison = relation
                if comparison==0:
                    comparison = 1 if index>=len(target) else (str(digit)>target[index])-(str(digit)<target[index])
                result += count(index+1,tight and digit==maximum,comparison)
            return result
        total += count(0,True,0)
    return total


def test_batch_39_references_wrong_algorithms_and_review_gates():
    catalog = get_catalog()
    for pid in BATCH:
        problem = catalog[f'leetcode-{pid}']
        assert problem.status=='approved' and len(problem.hints)==4 and problem.editorial
        assert sum(t.visible for t in problem.tests)==2 and sum(not t.visible for t in problem.tests)>=12
        assert all(run_source(problem.reference_solution,problem,t)==(True,None) for t in problem.tests)
        for wrong in problem.known_wrong_solutions:
            results = [run_source(wrong,problem,t) for t in problem.tests]
            assert (False,None) in results and all(error is None for _,error in results)
        if problem.difficulty>=8:
            assert problem.prerequisites
            assert prerequisites_met(problem,{topic:70 for topic in problem.prerequisites})
            assert not prerequisites_met(problem,{topic:69 for topic in problem.prerequisites})
    for pid,minimum in [(436,60),(437,50),(439,50),(445,60)]:
        assert review_focus_boost(catalog[f'leetcode-{pid}'])>=minimum


def test_batch_39_generated_and_deterministic_inputs_obey_source_domains():
    for pid in BATCH:
        for args in fixtures(pid):
            if pid in (422,425):
                words = args[0]
                assert 1<=len(words)<=(500 if pid==422 else 1000)
                assert all(1<=len(w)<=(500 if pid==422 else 4) and set(w)<=set(string.ascii_lowercase) for w in words)
                if pid==425:
                    assert len(set(words))==len(words) and len(set(map(len,words)))==1
            elif pid==433:
                start,end,bank = args
                assert len(bank)<=10 and all(len(w)==8 and set(w)<=set('ACGT') for w in [start,end,*bank])
            elif pid==436:
                intervals = args[0]
                assert 1<=len(intervals)<=20000 and len({a for a,b in intervals})==len(intervals)
                assert all(-10**6<=a<=b<=10**6 for a,b in intervals)
            elif pid==437:
                nodes = positions(args[0])
                assert len(nodes)<=1000 and all(abs(v)<=10**9 for v in nodes.values()) and abs(args[1])<=1000
            elif pid==438:
                assert all(1<=len(w)<=30000 and set(w)<=set(string.ascii_lowercase) for w in args)
            elif pid==439:
                assert 5<=len(args[0])<=10000
                collapse_ternary(args[0])
            elif pid==440:
                assert 1<=args[1]<=args[0]<=10**9
            elif pid==443:
                assert 1<=len(args[0])<=2000
                assert all(len(c)==1 and c in string.ascii_letters+string.digits+string.punctuation for c in args[0])
            elif pid==445:
                assert all(1<=len(v)<=100 and all(type(d) is int and 0<=d<=9 for d in v)
                           and (len(v)==1 or v[0]!=0) for v in args)
            else:
                nums = args[0]
                assert 1<=len(nums)<=1000 and all(-2**31<=v<2**31 for v in nums)
                # Check large fixtures independently without exponential enumeration.
                answer = (progression_count(len(nums)) if nums==list(range(1000)) else
                          2**31-1-31-465 if nums==[0]*31 else arithmetic_oracle(args))
                assert 0<=answer<2**31


def test_ragged_word_square_exhausts_short_rows_and_missing_mirrors():
    solve = reference(422)
    words = [''.join(chars) for n in range(1,4) for chars in product('ab',repeat=n)]
    for count in range(1,5):
        for rows in product(words,repeat=count):
            assert solve(rows)==square_oracle([list(rows)])
    assert not solve(['abc','bad','c'])
    for args,expected in BATCH[422]['stress']:
        assert solve(*args)==expected


def test_word_squares_exhaust_small_dictionaries_and_preserve_reused_words():
    solve = reference(425)
    for size in range(1,4):
        words = [''.join(chars) for chars in product('ab',repeat=size)]
        for count in range(1,len(words)+1):
            for subset in combinations(words,count):
                assert sorted(solve(subset))==sorted(squares_oracle([subset]))
    for args,expected in BATCH[425]['stress']:
        result = solve(*args)
        assert sorted(result)==sorted(expected)
        assert len({tuple(rows) for rows in result})==len(result)
    assert len(binary_squares(4))==1024
    assert all(square[0]==square[2]=='baba' for square in solve(['abat','baba','atan','atal']))


def test_word_square_comparison_keeps_row_order_and_multiplicity():
    problem = get_catalog()['leetcode-425']
    case = problem.tests[0]
    expected = case.expected
    code = lambda value: f'def word_squares(words):\n    return {value!r}\n'
    assert run_source(code(expected[::-1]),problem,case)==(True,None)
    for wrong in ([row[::-1] for row in expected],expected[:-1],expected+[expected[0]]):
        assert run_source(code(wrong),problem,case)==(False,None)


def test_gene_bfs_matches_all_small_banks_and_endpoint_pairs():
    solve = reference(433)
    genes = [''.join(chars)+'AAAAA' for chars in product('AC',repeat=3)]
    for mask in range(1<<len(genes)):
        bank = [w for i,w in enumerate(genes) if mask>>i&1]
        for start,end in product(genes,repeat=2):
            assert solve(start,end,bank)==gene_oracle([start,end,bank])
    for args in fixtures(433):
        assert solve(*args)==gene_oracle(args)


def test_right_intervals_exhaust_equal_endpoints_and_original_indices():
    solve = reference(436)
    for count in range(1,5):
        for starts in combinations(range(-2,3),count):
            for widths in product(range(3),repeat=count):
                intervals = [[a,a+w] for a,w in zip(starts,widths)][::-1]
                assert solve(intervals)==interval_oracle([intervals])
    for args,expected in BATCH[436]['stress']:
        assert solve(*args)==expected


def test_tree_path_prefixes_match_ancestor_enumeration_and_deep_chain_counts():
    solve = reference(437)
    # Complete three-node trees expose sibling contamination and repeated prefixes.
    for values in product(range(-2,3),repeat=3):
        for target in range(-6,7):
            assert solve(_treenode(values),target)==paths_oracle([values,target])
    for args in fixtures(437):
        if len(args[0])<100:
            assert solve(_treenode(args[0]),args[1])==paths_oracle(args)
    for (tree,target),expected in BATCH[437]['stress']:
        assert solve(_treenode(tree),target)==expected


def test_anagram_windows_exhaust_small_texts_and_patterns():
    solve = reference(438)
    texts = [''.join(chars) for n in range(1,7) for chars in product('ab',repeat=n)]
    patterns = [''.join(chars) for n in range(1,5) for chars in product('ab',repeat=n)]
    for text,pattern in product(texts,patterns):
        assert solve(text,pattern)==anagrams_oracle([text,pattern])
    for args,expected in BATCH[438]['stress']:
        assert solve(*args)==expected


def test_ternary_parsing_checks_both_nested_branches_and_maximum_depth():
    solve = reference(439)
    leaves = '01TF'
    branches = list(leaves)+[c+'?'+a+':'+b for c,a,b in product('TF',leaves,leaves)]
    for condition,a,b in product('TF',branches,branches):
        expression = condition+'?'+a+':'+b
        assert solve(expression)==ternary_oracle([expression])==collapse_ternary(expression)
    for args,expected in BATCH[439]['stress']:
        assert len(args[0])==9997 and solve(*args)==collapse_ternary(*args)==expected


def test_lexical_rank_exhausts_small_ranges_and_full_domain_digit_dp():
    solve = reference(440)
    for n in range(1,201):
        for rank,value in enumerate(sorted(range(1,n+1),key=str),1):
            assert solve(n,rank)==value
            if n<30:
                assert lexical_rank(n,value)==rank
    rng = random.Random(440)
    queries = [[rng.randint(1,10**9),None] for _ in range(500)]
    for query in queries:
        query[1] = rng.randint(1,query[0])
    for n,k in queries+[args for args,_ in BATCH[440]['stress']]:
        result = solve(n,k)
        assert 1<=result<=n and lexical_rank(n,result)==k


def test_compression_exhausts_short_runs_and_every_single_run_length():
    solve = reference(443)
    for size in range(1,8):
        for chars in product('a1!',repeat=size):
            original = list(chars)
            expected = compression_oracle([original])
            count = solve(original)
            assert {'return':count,'prefix':original[:count]}==expected
    for length in range(1,2001):
        chars = ['a']*length
        expected = ['a']+(list(str(length)) if length>1 else [])
        count = solve(chars)
        assert count==len(expected) and chars[:count]==expected


def test_character_prefix_judge_checks_mutation_and_strict_count_ignoring_tail():
    problem = get_catalog()['leetcode-443']
    case = Case(id='char-prefix',arguments=[list('aabbccc')],expected={'return':6,'prefix':list('a2b2c3')})
    code = lambda body: f'def compress_characters(chars):\n    {body}\n'
    assert run_source(code("chars[:] = list('a2b2c3Z'); return 6"),problem,case)==(True,None)
    for body in ("return 6", "return 'a2b2c3'", "chars=list('a2b2c3'); return 6",
                 "chars[:6]=list('a2b2c4'); return 6", "chars[:6]=list('a2b2c3'); return True"):
        assert not run_source(code(body),problem,case)[0]


def test_forward_linked_addition_exhausts_small_numbers_and_preserves_input_links():
    solve = reference(445)
    def check(a,b):
        heads = [_listnode(a),_listnode(b)]
        links = []
        for head in heads:
            node = head
            while node is not None:
                links.append((node,node.val,node.next))
                node = node.next
        actual = _serialize(solve(*heads),'listnode')
        assert actual==linked_sum_oracle([a,b])
        assert all(node.val==value and node.next is following for node,value,following in links)
    for a,b in product(range(100),repeat=2):
        check(list(map(int,str(a))),list(map(int,str(b))))
    for args in fixtures(445):
        check(*args)


def test_arithmetic_subsequences_exhaust_short_inputs_and_bounded_large_answers():
    solve = reference(446)
    for length in range(1,8):
        for nums in product(range(-1,2),repeat=length):
            assert solve(nums)==arithmetic_oracle([nums])
    for n in range(1,13):
        assert progression_count(n)==arithmetic_oracle([list(range(n))])
    for args,expected in BATCH[446]['stress']:
        assert solve(*args)==expected<2**31
    assert solve([-2**31,0,-2**31])==0
    assert solve([-2**31,-1,2**31-2])==1
