"""Shortest repetition encoding with noncanonical optimal outputs."""
from functools import lru_cache

from .import_batch_003 import entry


@lru_cache(None)
def encoding_candidates(text):
    """Exhaust small parse trees, retaining every non-lengthening encoding.

    Unlike the reference table, this oracle does not keep just one optimal child.
    Longer-than-literal children cannot occur in an optimal complete encoding.
    """
    candidates = {text}
    for split in range(1, len(text)):
        for left in encoding_candidates(text[:split]):
            for right in encoding_candidates(text[split:]):
                if len(left)+len(right) <= len(text):
                    candidates.add(left+right)
    for copies in range(2, len(text)+1):
        if len(text) % copies:
            continue
        part = text[:len(text)//copies]
        if part*copies == text:
            for child in encoding_candidates(part):
                candidate = f'{copies}[{child}]'
                if len(candidate) <= len(text):
                    candidates.add(candidate)
    return frozenset(candidates)


def encoding_oracle(args):
    text = args[0]
    best = min(encoding_candidates(text), key=lambda value:(len(value),value))
    return best if len(best) < len(text) else text


def random_encoding(rng):
    if rng.random() < .6:
        part = ''.join(rng.choice('ab') for _ in range(rng.randint(1,3)))
        return [part*rng.randint(2,3)]
    return [''.join(rng.choice('abc') for _ in range(rng.randint(1,10)))]


ENCODE = '''\
def shortest_encoding(s):
    n = len(s)
    best = [['']*(n+1) for _ in range(n)]
    for size in range(1,n+1):
        for start in range(n-size+1):
            end = start+size
            raw = s[start:end]
            answer = raw
            for split in range(start+1,end):
                candidate = best[start][split]+best[split][end]
                if len(candidate) < len(answer):
                    answer = candidate
            for width in range(1,size//2+1):
                if size % width == 0 and raw[:width]*(size//width) == raw:
                    candidate = str(size//width)+'['+best[start][start+width]+']'
                    if len(candidate) < len(answer):
                        answer = candidate
            best[start][end] = answer
    return best[0][n]
'''

BATCH = {
471: entry('shortest_encoding', [('s','str')], 'str', ['strings','dynamic-programming','recursion'],
    ['1 <= s.length <= 150; lowercase English letters only.',
     'An encoding contains lowercase literals and k[encoded_string], with positive integer k and a nonempty body. Nesting and concatenation are allowed.',
     'Return any shortest encoding that expands to exactly s. If no encoding is shorter, return the literal input unchanged.',
     'Several optimal strings may be accepted; this is not run-length encoding or merely finding the shortest repeated prefix.'],
    [(['aaa'], 'The literal aaa has length 3, shorter than 3[a] of length 4. Do not encode it.'),
     (['aaaaaaaaaa'], '10[a], a9[a], and 9[a]a all expand to ten a characters and have the optimal length 5. Any of these answers passes.')],
    [[s] for s in ('a','b','aa','aaaa','aaaaa','abab','ababab','abcabcabc',
                  'aaaaab','abababab','aabcaabcd','abbbabbbcabbbabbbc','abcabca','abcdef')],
    ENCODE, ['def shortest_encoding(s):\n    return s\n',
      "def shortest_encoding(s):\n    from itertools import groupby\n    out=[]\n    for char,group in groupby(s):\n        count=len(list(group))\n        encoded=str(count)+'['+char+']'\n        out.append(encoded if len(encoded)<count else char*count)\n    return ''.join(out)\n"],
    ['Never compresses profitable repetitions.', 'Compresses only identical-character runs, missing multi-character and nested repetitions.'],
    encoding_oracle, random_encoding,
    ['An optimal expression is either literal text, two adjacent expressions, or a repeated expression.',
     'Solve every substring from shorter lengths to longer lengths, trying all splits and exact repeat periods.',
     'Initialize the substring answer to its literal text; improve it with left+right encodings and k[encoded_period].',
     'Only replace an answer when shorter. The judge checks decoded text and optimal length, not which tied answer you choose.'],
    'The outermost grammar operation gives a complete case split: literal, concatenation, or repetition. '
    'Its children encode shorter substrings already solved by interval DP. Trying all splits and all exact '
    'periods therefore finds a minimum-length expression. Python substring construction gives an O(n^4) '
    'upper bound and stored encoded strings an O(n^3) space bound. The independent small-input oracle '
    'enumerates all non-lengthening parse-tree encodings, including ties. Bounded grammar decoding '
    'accepts equally short alternatives and rejects malformed or excessive expansion without eval.',
    'O(n^4) upper bound with Python string construction', 'O(n^3) stored string characters', difficulty=8,
    stress=[(['a'*150], '150[a]'), (['ab'*75], '75[ab]'),
            (['abcdefghijklmnopqrstuvwxyz'*5], '5[abcdefghijklmnopqrstuvwxyz]'),
            ([('a'*20+'b')*7], '7[20[a]b]')]),
}
BATCH[471]['comparator'] = 'shortest_encoding'
BATCH[471]['prerequisites'] = ['strings','dynamic-programming']
