"""Capital rules, uncommon/deleted subsequences, and recursive arrangements."""
from collections import Counter
from functools import cache
import re

from .import_batch_003 import entry


def capital_oracle(args):
    return re.fullmatch(r'(?:[A-Z]+|[a-z]+|[A-Z][a-z]+)',args[0]) is not None


def subsequences(word):
    values={''}
    for char in word:values|={prefix+char for prefix in values}
    return values


def uncommon_oracle(args):
    # Count containing INPUT POSITIONS, not index selections within a word.
    owners=Counter()
    for word in args[0]:owners.update(subsequences(word))
    return max((len(s) for s,count in owners.items() if count==1),default=-1)


def dictionary_oracle(args):
    text,words=args;possible=subsequences(text)
    return min((w for w in words if w in possible),key=lambda w:(-len(w),w),default='')


@cache
def arrangement_permanent(n):
    """Inclusion-exclusion counts bijective assignments, without recursive search.

    Product counts all row choices within a selected set of columns. Alternating
    signs cancel choices omitting a column. n choices using all n columns are
    bijections, so exactly the valid permutations survive.
    """
    rows=[sum(1<<(v-1) for v in range(1,n+1) if v%i==0 or i%v==0) for i in range(1,n+1)]
    total=0
    for mask in range(1,1<<n):
        choices=1
        for row in rows:
            choices*=(row&mask).bit_count()
            if not choices:break
        total+=choices if (n-mask.bit_count())%2==0 else -choices
    return total


def arrangement_oracle(args):return arrangement_permanent(args[0])


def random_capital(rng):
    word=''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1,100)))
    mode=rng.randrange(4)
    return [word.upper() if mode==0 else word if mode==1 else word.capitalize() if mode==2
            else ''.join(c.upper() if rng.randrange(2) else c for c in word)]


def random_uncommon(rng):
    words=[''.join(rng.choice('abc') for _ in range(rng.randint(1,10))) for _ in range(rng.randint(2,8))]
    if rng.random()<.5:words[-1]=words[0]
    return [words]


def random_dictionary(rng):
    text=''.join(rng.choice('abcd') for _ in range(rng.randint(1,12)))
    words=[''.join(rng.choice('abcde') for _ in range(rng.randint(1,12))) for _ in range(rng.randint(1,15))]
    if rng.random()<.5:words.append(text[::2])
    return [text,words]


def random_arrangement(rng):return [rng.randint(1,15)]


CAPITAL='''\
def valid_capital_usage(word):
    capitals=sum('A'<=char<='Z' for char in word)
    return capitals==0 or capitals==len(word) or (capitals==1 and 'A'<=word[0]<='Z')
'''
UNCOMMON='''\
def longest_uncommon_subsequence(strs):
    def contained(word,text):
        index=0
        for char in text:
            if index<len(word) and word[index]==char:index+=1
        return index==len(word)
    best=-1
    for i,word in enumerate(strs):
        if all(i==j or not contained(word,other) for j,other in enumerate(strs)):
            best=max(best,len(word))
    return best
'''
DICTIONARY='''\
def longest_dictionary_word(s,dictionary):
    best=''
    for word in dictionary:
        index=0
        for char in s:
            if index<len(word) and word[index]==char:index+=1
        if index==len(word) and (len(word)>len(best) or (len(word)==len(best) and word<best)):
            best=word
    return best
'''
ARRANGEMENT='''\
def count_beautiful_arrangements(n):
    from functools import cache
    allowed=[sum(1<<(value-1) for value in range(1,n+1) if value%position==0 or position%value==0)
             for position in range(1,n+1)]
    @cache
    def visit(used):
        position=used.bit_count()
        if position==n:return 1
        choices=allowed[position]&~used;total=0
        while choices:
            bit=choices&-choices;choices-=bit
            total+=visit(used|bit)
        return total
    return visit(0)
'''

BATCH={
520:entry('valid_capital_usage',[('word','str')],'bool',['strings'],
    ['1 <= len(word) <= 100; only uppercase and lowercase English letters.',
     'Accept exactly three patterns: every letter uppercase, every letter lowercase, or only the first letter uppercase.'],
    [(['USA'],'All three letters are uppercase, so return true; capitals are not limited to the first position.'),
     (['FlaG'],'Return false: uppercase F followed by lowercase letters and another uppercase G matches none of the three allowed patterns.')],
    [[w] for w in ('a','A','aa','AA','Aa','aA','Google','leetcode','gOogle','USa','uSA','AbC','ABCd','zZ','Zz')],
    CAPITAL,[CAPITAL.replace("(capitals==1 and 'A'<=word[0]<='Z')","capitals==1"),
             CAPITAL.replace(' or capitals==len(word)','')],
    ['Accepts a single capital anywhere instead of only at the beginning.', 'Forgets that an all-uppercase multi-letter word is valid.'],
    capital_oracle,random_capital,
    ['These are three patterns of case, not three special words.',
     'Count uppercase letters, then consider where a sole uppercase letter occurs.',
     'Accept count=0, count=length, or count=1 with an uppercase first character.',
     'A one-letter word satisfies an all-one-case rule. A lowercase first letter followed by a capital is never title case.'],
    'The number of capitals identifies all-lowercase and all-uppercase words. '
    'The only remaining accepted count is one, and that capital must be first. '
    'This classification is exhaustive and uses constant extra space. The independent '
    'oracle matches the three literal case-pattern languages with a regular expression.',
    'O(n)','O(1)',stress=[(['A'*100],True),(['a'*100],True),(['A'+'a'*99],True),(['a'*99+'A'],False),(['A'*99+'a'],False)]),
522:entry('longest_uncommon_subsequence',[('strs','list[str]')],'int',['strings','two-pointers'],
    ['2 <= len(strs) <= 50; lowercase English letters only.',
     'Source 522 uses 1..10 characters per word. This app explicitly supports 1 <= len(word) <= 100 to include the two-string source 521 domain in the same exercise.',
     'An uncommon subsequence belongs to exactly ONE input position and to none of the other input strings. Duplicate strings at different positions count separately.',
     'You may delete characters but cannot reorder them. Return the maximum length, or -1 if none exists.'],
    [([['aba','cdc','eae']],'Return 3: aba is a subsequence of the first string and neither of the other two. The entire input string is allowed as a subsequence.'),
     ([['aaa','aaa','aa']],'Return -1: both copies of aaa contain every subsequence of aa. A string occurring once in the array is not necessarily an uncommon subsequence.')],
    [[words] for words in (['a','a'],['a','b'],['aa','a'],['abc','abc'],['ab','ba'],['a','aa','aa'],
        ['abc','abc','ac'],['abc','abc','d'],['a','b','a'],['ab','ab','ba'],['abc','acb','bac'],
        ['aba','aba','ab'],['aaa','aa','a'],['abcd','abc','ab','a'],['aab','aba','baa'])],
    UNCOMMON,[UNCOMMON.replace('not contained(word,other)','word!=other'),
              UNCOMMON.replace('i==j or','word==other or')],
    ['Checks only duplicate equality, missing shorter words contained in longer strings.', 'Skips all equal strings instead of only the same input position.'],
    uncommon_oracle,random_uncommon,
    ['If a subsequence is unique to one input string, what happens when you extend it to that whole string?',
     'Only whole input strings need to be candidates. Reject a candidate if any other input position contains it as a subsequence.',
     'For each candidate i, scan every j!=i with a subsequence pointer; maximize the lengths of candidates that all other strings reject.',
     'Do not discard equal strings before checking: two equal occurrences disqualify one another. Subsequence matching skips characters but never reorders them.'],
    'Suppose a subsequence is unique to string s. If s itself occurred as a subsequence '
    'of another input, that other input would also contain the shorter candidate, a '
    'contradiction. Thus some longest answer is an entire input string. Compare every '
    'candidate against every other position using an order-preserving pointer. '
    'With m strings and maximum length L this costs O(m^2*L) time and O(1) extra '
    'space. A separate oracle enumerates all subsequences and counts containing '
    'input positions; it does not rely on the whole-string-candidate theorem.',
    'O(m^2*L)','O(1)',difficulty=5,
    stress=[([['a'*10]*50],-1),([['a'*10]*49+['b'*10]],10),
            ([['a'*100]*50],-1),([['a'*100]*49+['b'*100]],100),
            ([['a'*100,'a'*99]],100),([['a'*99+'b','b'+'a'*99]],100)]),
524:entry('longest_dictionary_word',[('s','str'),('dictionary','list[str]')],'str',['strings','two-pointers'],
    ['1 <= len(s) <= 1000; 1 <= len(dictionary) <= 1000; 1 <= len(word) <= 1000.',
     'All characters are lowercase English letters. Select a dictionary word by deleting zero or more characters from s without reordering.',
     'Choose maximum length first, then lexicographically smallest among ties. Return the empty string if no word is possible.'],
    [(['abpcplea',['ale','apple','monkey','plea']],'Deleting b, c, and the final a gives apple. Its length 5 beats ale and plea; monkey cannot be formed.'),
     (['bab',['ba','ab','bb']],'All three length-2 words are subsequences. Return ab: ties use alphabetical order, not dictionary order or earliest match position.')],
    [args for args in (['a',['a']],['a',['b']],['ab',['ba']],['aaa',['aaaa','aa']],['abc',['c','b','a']],
        ['abc',['abc','ab']],['abc',['ac','ab']],['abc',['bc','ac']],['bca',['bc','a']],
        ['abc',['ax','ab','ac']],['aaaa',['aaa','aaa','aa']],['abc',['abcd']],
        ['zxy',['zy','xy']],['abcabc',['cab','abc','bca']],['aabb',['abab','aab']])],
    DICTIONARY,[DICTIONARY.replace('index==len(word) and (','word in s and ('),
                 DICTIONARY.replace('word<best','word>best')],
    ['Requires a contiguous substring instead of allowing deletion gaps.', 'Chooses the lexicographically largest word when lengths tie.'],
    dictionary_oracle,random_dictionary,
    ['A dictionary word is possible exactly when it is a subsequence of s.',
     'Use a pointer into each word while scanning s. Compare candidates by length before alphabetical order.',
     'Advance the candidate pointer only on equal characters; after a full match replace best for a longer word or a lexicographically smaller equal-length word.',
     'A match need not be contiguous. Do not return the first possible word, and do not sort by alphabetical order before prioritizing length.'],
    'The earliest possible match for each next character leaves at least as much '
    'remaining text as any later choice, so the pointer test finds every feasible '
    'subsequence. Scanning every dictionary entry and maintaining the best length/'
    'lexicographic pair produces the required winner. For d words, text length n, '
    'and maximum word length L, time is O(d*(n+L)) including tie comparisons; '
    'auxiliary space is O(1). The small oracle enumerates all deletions of s and '
    'selects among literal resulting strings independently.',
    'O(d*(n+L))','O(1)',difficulty=5,
    stress=[(['a'*1000,['b'*1000]*1000],''),(['a'*1000,['a'*1000]*1000],'a'*1000),
            (['ab'*500,['b'*500,'a'*500]*500],'a'*500),
            (['a'*999+'b',['a'*999+'c']*999+['a'*999+'b']],'a'*999+'b')]),
526:entry('count_beautiful_arrangements',[('n','int')],'int',['recursion','backtracking','dynamic-programming','bitmask'],
    ['1 <= n <= 15. Use every integer from 1 through n exactly once.',
     'Positions are 1-indexed. At every position i, value % i == 0 OR i % value == 0 must hold.',
     'Return the number of valid permutations, not the permutations themselves.'],
    [([2],'Both [1,2] and [2,1] work. In the second arrangement, position 2 is divisible by its value 1; either direction of divisibility suffices.'),
     ([1],'Only [1] exists, and 1 divides 1. Count this arrangement once, even though both divisibility checks hold.')],
    [[n] for n in range(3,16)],
    ARRANGEMENT,[ARRANGEMENT.replace('value%position==0 or position%value==0','value%position==0 and position%value==0'),
        'def count_beautiful_arrangements(n):\n    from math import prod\n    return prod(sum(v%i==0 or i%v==0 for v in range(1,n+1)) for i in range(1,n+1))\n'],
    ['Requires both divisibility directions instead of either direction.', 'Multiplies independent choices while allowing the same value to be reused.'],
    arrangement_oracle,random_arrangement,
    ['Place one unused number at the next position, then recursively complete the remaining positions.',
     'The set of used values determines the next position. Cache the number of completions for that set.',
     'visit(mask): if every value is used return 1; otherwise sum visit(mask|bit) for each unused value satisfying either divisibility rule at popcount(mask)+1.',
     'Use 1-based positions for divisibility even if the allowed-mask array is 0-based. Each choice consumes one distinct value; a completed permutation contributes exactly one.'],
    'Recursive search partitions valid permutations by their next value, without '
    'overlap because every value is used once. The next position follows from the '
    'number of set bits, so the used-value mask completely identifies a subproblem. '
    'Memoization gives O(n*2^n) time and O(2^n) storage, including a recursion depth '
    'of at most 15. All 15 legal n values are tested: two visible and thirteen hidden. '
    'An independent inclusion-exclusion permanent counts bijective allowed '
    'position/value assignments, and literal permutation enumeration checks small n.',
    'O(n*2^n)','O(2^n)',difficulty=6),
}
