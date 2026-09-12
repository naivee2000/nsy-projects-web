from collections import Counter
from itertools import product
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_030 import (
    BATCH, MAXIMUM_NUMBER, ITINERARY, CROSSING, PALINDROME_PAIRS,
    maximum_number_oracle, itinerary_oracle, crossing_oracle, palindrome_pairs_oracle,
)
from code_practice.validation import run_source


def function(source, name):
    namespace = {}
    exec(compile(source, f'<{name}>', 'exec'), namespace)
    return namespace[name]


def test_batch_30_has_published_content_and_algorithmic_rejection_evidence():
    for source_id in BATCH:
        problem = get_catalog()[f'leetcode-{source_id}']
        assert problem.status == 'approved' and problem.difficulty >= 8
        assert sum(case.visible for case in problem.tests) >= 2
        assert sum(not case.visible for case in problem.tests) >= 12
        assert all(case.explanation for case in problem.tests if case.visible)
        assert len(problem.hints) == 4 and problem.editorial and problem.prerequisites
        assert all(run_source(problem.reference_solution, problem, case)[0] for case in problem.tests)
        for wrong in problem.known_wrong_solutions:
            assert any(run_source(wrong, problem, case) == (False, None) for case in problem.tests)


def test_maximum_number_matches_all_short_digit_arrays_and_every_length():
    solve = function(MAXIMUM_NUMBER, 'create_maximum_number')
    arrays = [[first,*tail] for length in range(1,4) for first in (1,2)
              for tail in product((0,1,2), repeat=length-1)]
    for left in arrays:
        for right in arrays:
            for length in range(1,len(left)+len(right)+1):
                assert solve(left,right,length) == maximum_number_oracle([left,right,length])


def test_itinerary_matches_every_short_valid_walk_over_three_airports():
    solve = function(ITINERARY, 'reconstruct_itinerary')
    checked = set()
    for length in range(1,8):
        for following in product(('JFK','AAA','BBB'), repeat=length):
            route = ('JFK',) + following
            if any(a == b for a,b in zip(route,route[1:])):
                continue
            edges = tuple(sorted(zip(route,route[1:])))
            if edges in checked:
                continue
            checked.add(edges)
            tickets = [list(edge) for edge in edges]
            answer = solve(tickets)
            assert answer == itinerary_oracle([tickets])
            assert Counter(zip(answer,answer[1:])) == Counter(edges)
    assert len(checked) > 100


def test_crossing_local_cases_match_all_short_segment_paths():
    solve = function(CROSSING, 'is_self_crossing')
    for length in range(1,8):
        for distances in product(range(1,5), repeat=length):
            assert solve(distances) == crossing_oracle([distances])
    assert solve([1,1,2,1,1])  # Collinear touch with the fourth previous edge.
    assert solve([1,1,2,2,1,1])  # Inward transition reaches the fifth previous edge.


def test_palindrome_trie_covers_every_pair_of_short_binary_words_in_both_orders():
    solve = function(PALINDROME_PAIRS, 'palindrome_pairs')
    words = [''.join(letters) for length in range(6) for letters in product('ab', repeat=length)]
    for values in (words,words[::-1]):
        result = solve(values)
        assert sorted(result) == sorted(palindrome_pairs_oracle([values]))
        assert len(result) == len({tuple(pair) for pair in result})
        assert all(i != j for i,j in result)


def test_palindrome_maximum_word_count_expected_pairs_are_exact_reversals():
    words, expected = BATCH[336]['stress'][1][0][0], BATCH[336]['stress'][1][1]
    assert len(words) == len(set(words)) == 5000
    assert len({len(word) for word in words}) == 1
    # For equal-length words, a concatenation is palindromic iff the second
    # word is the exact reverse. This proves all 5000 large-fixture pairs.
    lookup = {word:i for i,word in enumerate(words)}
    assert sorted(expected) == sorted([[i,lookup[word[::-1]]] for i,word in enumerate(words)])
    no_pairs = BATCH[336]['stress'][0][0][0]
    assert len(no_pairs) == 5000 and all(len(word) == 300 for word in no_pairs)
    assert all(word[0]=='a' and word[-1]=='b' for word in no_pairs)


def test_batch_30_inputs_stay_in_source_domains_and_itineraries_are_real():
    for source_id,spec in BATCH.items():
        rng = random.Random(4047+source_id)
        inputs = ([args for args,_ in spec['examples']] + spec['boundaries']
                  + [args for args,_ in spec['stress']]
                  + [spec['generator'](rng) for _ in range(500)])
        for args in inputs:
            if source_id == 321:
                left,right,k = args
                assert 1 <= len(left) <= 500 and 1 <= len(right) <= 500
                assert 1 <= k <= len(left)+len(right)
                for digits in (left,right):
                    assert all(type(value) is int and 0 <= value <= 9 for value in digits)
                    assert len(digits)==1 or digits[0] != 0
            elif source_id == 332:
                tickets = args[0]
                assert 1 <= len(tickets) <= 300
                assert all(len(edge)==2 and edge[0]!=edge[1] for edge in tickets)
                assert all(len(code)==3 and set(code) <= set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                           for edge in tickets for code in edge)
                if len(tickets) <= 8:
                    answer = itinerary_oracle(args)
                    assert Counter(zip(answer,answer[1:])) == Counter(map(tuple,tickets))
            elif source_id == 335:
                assert 1 <= len(args[0]) <= 100000
                assert all(type(value) is int and 1 <= value <= 100000 for value in args[0])
            elif source_id == 336:
                words = args[0]
                assert 1 <= len(words) <= 5000 and len(set(words))==len(words)
                assert all(len(word)<=300 and set(word)<=set('abcdefghijklmnopqrstuvwxyz') for word in words)
        if source_id == 332:
            for args,answer in spec['stress']:
                assert answer[0]=='JFK'
                assert Counter(zip(answer,answer[1:])) == Counter(map(tuple,args[0]))
