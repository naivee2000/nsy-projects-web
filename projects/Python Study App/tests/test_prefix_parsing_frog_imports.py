from functools import lru_cache
from itertools import combinations, product
import random
import re

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_036 import (
    BATCH, LEXICAL, FILE, ELIMINATION, UTF, DECODE, REPEATING, REPLACEMENT, DIGITS,
    FROG, ABBREVIATION, lexical_oracle, file_oracle, elimination_oracle,
    elimination_reflection, utf_oracle, decode_oracle, repeating_oracle,
    replacement_oracle, digits_oracle, frog_oracle, abbreviation_oracle,
)
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.validation import run_source


def function(source,name):
    namespace = {}
    exec(compile(source,f'<{name}>','exec'),namespace)
    return namespace[name]


def test_batch_36_references_wrong_algorithms_and_review_contracts():
    for pid in BATCH:
        problem = get_catalog()[f'leetcode-{pid}']
        assert problem.status == 'approved' and len(problem.hints)==4 and problem.editorial
        assert sum(t.visible for t in problem.tests)==2 and sum(not t.visible for t in problem.tests)>=12
        assert all(run_source(problem.reference_solution,problem,t)==(True,None) for t in problem.tests)
        for wrong in problem.known_wrong_solutions:
            results = [run_source(wrong,problem,t) for t in problem.tests]
            assert (False,None) in results
            assert all(error is None for _,error in results)
    for pid in (394,395,403):
        assert review_focus_boost(get_catalog()[f'leetcode-{pid}']) >= 50
    hard = get_catalog()['leetcode-403']
    assert hard.difficulty >= 8
    assert not prerequisites_met(hard,{'recursion':69,'dynamic-programming':100})
    assert prerequisites_met(hard,{'recursion':70,'dynamic-programming':70})
    assert get_catalog()['leetcode-320'].signature.returns == 'list[str]'
    assert get_catalog()['leetcode-408'].signature.returns == 'bool'


def check_filesystem(text):
    parents, names = [], set()
    for line in text.split('\n'):
        name = line.lstrip('\t')
        depth = len(line)-len(name)
        assert name and depth<=len(parents)
        parents = parents[:depth]
        path = (*parents,name)
        assert path not in names
        names.add(path)
        if '.' in name:
            pieces = name.split('.')
            assert len(pieces)==2 and all(pieces)
        else:
            parents.append(name)
        assert all(c.isascii() and (c.isalnum() or c in ' .') for c in name)


def test_batch_36_deterministic_stress_and_seeded_inputs_stay_in_source_domains():
    for pid,spec in BATCH.items():
        rng = random.Random(4047+pid)
        cases = [a for a,_ in spec['examples']] + spec['boundaries']
        cases += [a for a,_ in spec['stress']] + [spec['generator'](rng) for _ in range(500)]
        for args in cases:
            if pid in (386,390,397):
                assert 1 <= args[0] <= {386:50000,390:10**9,397:2**31-1}[pid]
            elif pid == 388:
                assert 1 <= len(args[0]) <= 10000
                check_filesystem(args[0])
            elif pid == 393:
                assert 1 <= len(args[0]) <= 20000 and all(type(v) is int and 0<=v<=255 for v in args[0])
            elif pid == 394:
                text = args[0]
                assert 1 <= len(text) <= 30 and set(text)<=set('abcdefghijklmnopqrstuvwxyz0123456789[]')
                assert all(1<=int(count)<=300 for count in re.findall(r'\d+',text))
                output = decode_oracle(args)
                assert len(output)<=100000 and set(output)<=set('abcdefghijklmnopqrstuvwxyz')
            elif pid == 395:
                assert 1<=len(args[0])<=10000 and set(args[0])<=set('abcdefghijklmnopqrstuvwxyz')
                assert 1<=args[1]<=100000
            elif pid == 402:
                assert 1<=args[1]<=len(args[0])<=100000
                assert args[0].isascii() and args[0].isdigit()
                assert args[0]=='0' or not args[0].startswith('0')
            elif pid == 403:
                values = args[0]
                assert 2<=len(values)<=2000 and values==sorted(set(values)) and values[0]==0
                assert all(0<=v<=2**31-1 for v in values)
            else:
                word,abbr = args
                assert 1<=len(word)<=20 and set(word)<=set('abcdefghijklmnopqrstuvwxyz')
                assert 1<=len(abbr)<=10 and set(abbr)<=set('abcdefghijklmnopqrstuvwxyz0123456789')
                assert all(int(token)<=2**31-1 for token in re.findall(r'\d+',abbr))


def test_lexical_successors_match_full_sorting_through_three_digit_boundaries():
    solve = function(LEXICAL,'lexicographical_numbers')
    for n in range(1,1501):
        assert solve(n) == lexical_oracle([n])
    assert solve(50000) == lexical_oracle([50000])
    assert 'sorted(' not in LEXICAL and '.sort(' not in LEXICAL


def test_paths_include_slashes_and_spaces_but_not_directory_only_branches():
    solve = function(FILE,'longest_absolute_path')
    for args,expected in BATCH[388]['stress']:
        assert solve(*args) == expected == file_oracle(args)
    assert solve('huge empty directory\n\tempty\na.x') == 3
    assert solve('a\n\tb\n\t\tf.x\n\tg.y') == 7
    assert solve('a b\n\tc d.e f') == len('a b/c d.e f')
    assert solve('directory\n\tempty') == 0


def test_elimination_round_tracking_matches_literal_deletions_and_reflection():
    solve = function(ELIMINATION,'last_remaining')
    for n in range(1,5001):
        assert solve(n) == elimination_oracle([n]) == elimination_reflection(n)
    for args,expected in BATCH[390]['stress']:
        assert solve(*args) == expected == elimination_reflection(args[0])


def test_structural_utf_patterns_exhaust_one_and_two_bytes_without_unicode_extra_rules():
    solve = function(UTF,'valid_utf8')
    for length in (1,2):
        for data in product(range(256),repeat=length):
            assert solve(data) == utf_oracle([data])
    for data in ([192,128],[237,160,128],[244,144,128,128]):
        assert solve(data) and utf_oracle([data])
        with pytest.raises(UnicodeDecodeError):
            bytes(data).decode('utf-8')
    assert not solve([197,197]) and not solve([240,128,128])
    problem = get_catalog()['leetcode-393']
    assert 'structural patterns only' in problem.statement


def test_recursive_decoder_matches_innermost_expansion_for_nested_and_multidigit_groups():
    solve = function(DECODE,'decode_string')
    # These lexical forms need not be emitted by the source generator, but the
    # independent oracle must not misread a full digit token or an empty group.
    for text,expected in [('03[a]','aaa'),('2[]x','x'),('1[2[]]','')]:
        assert solve(text) == decode_oracle([text]) == expected
    for malformed in ('0[a]','301[a]','3a','2[4]'):
        with pytest.raises(ValueError):
            decode_oracle([malformed])
    for a,b,c in product(range(1,6),repeat=3):
        for text in (f'{a}[a{b}[bc]]{c}[d]',f'a{a}[{b}[c]]{c}[e]f'):
            assert solve(text) == decode_oracle([text])
    for args,expected in BATCH[394]['stress']:
        assert solve(*args) == expected == decode_oracle(args)


def test_recursive_frequency_splitting_exhausts_short_ternary_strings():
    solve = function(REPEATING,'longest_repeating_substring')
    for size in range(1,8):
        for chars in product('abc',repeat=size):
            text = ''.join(chars)
            for k in range(1,5):
                assert solve(text,k) == repeating_oracle([text,k])
    assert solve('aaabbbxbbaaa',3) == 6
    for args,expected in BATCH[395]['stress']:
        assert solve(*args) == expected


def test_bit_greedy_matches_bfs_and_exact_odd_branch_recurrence():
    solve = function(REPLACEMENT,'integer_replacement')
    @lru_cache(None)
    def exact(n):
        if n == 1:
            return 0
        return 1+exact(n//2) if n%2==0 else 2+min(exact((n-1)//2),exact((n+1)//2))
    for n in range(1,10001):
        assert solve(n) == exact(n) == replacement_oracle([n])
    assert solve(3)==2 and solve(15)==5 and solve(2**31-1)==32
    for args,expected in BATCH[397]['stress']:
        assert solve(*args) == expected == exact(args[0])


def test_monotone_digit_removal_matches_all_short_subsequence_choices():
    solve = function(DIGITS,'remove_k_digits')
    for size in range(1,7):
        for tail in product('012',repeat=size-1):
            for first in '12':
                text = first+''.join(tail)
                for k in range(1,size+1):
                    assert solve(text,k) == digits_oracle([text,k])
    assert solve('112',1)=='11' and solve('123',1)=='12'
    for args,expected in BATCH[402]['stress']:
        assert solve(*args) == expected
    assert 'int(' not in DIGITS


def test_frog_states_match_every_small_stone_subset_and_source_sized_cases():
    solve = function(FROG,'can_cross')
    for size in range(1,13):
        for chosen in combinations(range(1,13),size):
            stones = [0,*chosen]
            assert solve(stones) == frog_oracle([stones])
    assert solve([0,1,2]) and not solve([0,2])
    for args,expected in BATCH[403]['stress']:
        assert solve(*args) == expected


def all_abbreviations(word):
    result = set()
    for mask in range(1 << len(word)):
        chunks, count = [], 0
        for index,char in enumerate(word):
            if mask & (1 << index):
                count += 1
            else:
                if count:
                    chunks.append(str(count))
                    count = 0
                chunks.append(char)
        if count:
            chunks.append(str(count))
        result.add(''.join(chunks))
    return result


def test_abbreviation_parser_matches_enumerated_replacement_masks():
    solve = function(ABBREVIATION,'valid_word_abbreviation')
    for size in range(1,5):
        for letters in product('ab',repeat=size):
            word = ''.join(letters)
            valid = all_abbreviations(word)
            for length in range(1,5):
                for tokens in product('ab01234',repeat=length):
                    abbr = ''.join(tokens)
                    assert solve(word,abbr) == (abbr in valid) == abbreviation_oracle([word,abbr])
    assert not solve('a','01') and not solve('apple','4')
