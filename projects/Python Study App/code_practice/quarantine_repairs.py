"""Reviewed control-only repairs kept separate from oracle/generator modules.

The validation cache hashes the module containing each oracle. Keeping a change
to one candidate's spec here leaves unrelated oracle evidence current, while
the candidate-to-spec contract check invalidates the changed candidate.
"""


def apply_quarantine_repairs(batch):
    batch[2663]['boundaries'] = [
        ['abca', 4] if arguments == ['abac', 4] else arguments
        for arguments in batch[2663]['boundaries']
    ]

    batch[1072]['wrong'][1] = batch[1072]['reference'].replace(
        'max(counts.values())', 'len(counts)')
    batch[1072]['wrong_reasons'][1] = 'Counts distinct normalized patterns instead of the largest group of compatible rows.'

    batch[1356]['sample_contract_adapter']['source_sample'] = (
        'Input arr = [0,1,2,3,4,5,6,7,8] → Output [0,1,2,4,8,3,5,6,7] '
        'Explantion: [0] is the only integer with 0 bits. [1,2,4,8] all have 1 bit. '
        '[3,5,6] have 2 bits. [7] has 3 bits. The sorted array by bits is [0,1,2,4,8,3,5,6,7].'
    )

    batch[1087]['boundaries'].append(['{b,a}'])

    batch[1275]['boundaries'].append([[
        [0, 0], [0, 1], [0, 2], [1, 1], [1, 0], [1, 2], [2, 1], [2, 0], [2, 2],
    ]])

    batch[1602]['boundaries'].append([[1, 2, 3, 4], 3])

    batch[3012]['boundaries'].append([[2, 2, 2, 3]])

    batch[3354]['boundaries'].append([[2, 0, 0]])

    batch[3464]['boundaries'].append([
        6, [[0, 6], [2, 0], [6, 5], [2, 6], [3, 6], [0, 3], [0, 2], [6, 2], [6, 3]], 4,
    ])

    batch[3740]['boundaries'].append([[1, 2, 3, 4, 5, 1, 6, 1, 1, 1]])
    batch[3740]['wrong'][1] = batch[3740]['reference'].replace(
        'range(len(group)-2)', 'range(min(1,len(group)-2))')

    batch[3951]['wrong'][1] = batch[3951]['reference'].replace(
        'merged[-1][1]<left', 'merged[-1][1]<=left')
    batch[3951]['wrong_reasons'][1] = 'Counts a shared interval endpoint twice when requirements meet at that time.'

    batch[3997]['boundaries'].append([[5, 2, 4, 6]])

    batch[4039]['wrong'][0] = batch[4039]['reference'].replace(
        'int(text[width:]),MOD)', 'int(text[width:])+1,MOD)')
    batch[4039]['wrong_reasons'][0] = 'Adds one to the decoded exponent before modular exponentiation.'

    batch[737]['wrong'][0] = '''def are_sentences_similar(sentence1,sentence2,similar_pairs):
    if len(sentence1)!=len(sentence2):return False
    neighbors={tuple(pair) for pair in similar_pairs}
    return all(a==b or (a,b) in neighbors or (b,a) in neighbors
               for a,b in zip(sentence1,sentence2))
'''
    batch[737]['wrong_reasons'][0] = 'Checks only direct similarity pairs and misses transitive chains.'
    batch[737]['wrong'][1] = batch[737]['reference'].replace(
        'a==b or find(a)==find(b)',
        'a in parent and b in parent and find(a)==find(b)')
    batch[737]['wrong_reasons'][1] = 'Rejects identical unseen words because it requires both words to occur in a similarity pair.'

    batch[758]['wrong'][0] = batch[758]['reference'].replace(
        '    marked=[False]*len(s)',
        '    words=words[:1]\n    marked=[False]*len(s)')
    batch[758]['wrong_reasons'][0] = 'Uses only the first dictionary word and misses bold regions supplied by later words.'

    batch[916]['wrong'][0] = batch[916]['reference'].replace(
        'for req in requirements:', 'for req in requirements[:1]:')
    batch[916]['wrong_reasons'][0] = 'Checks only the first required word and ignores later character requirements.'
    batch[916]['comparator'] = 'unordered'
    batch[916]['constraints'] = [
        value.replace('Return universal words in input order.', 'Return universal words in any order.')
        for value in batch[916]['constraints']
    ]

    batch[947]['wrong'][1] = '''def maximum_removable_stones(stones):
    rows={}
    for row,column in stones:rows[row]=rows.get(row,0)+1
    return sum(size-1 for size in rows.values())
'''
    batch[947]['wrong_reasons'][1] = 'Connects stones only by equal rows and ignores chains linked through columns.'

    batch[1616]['wrong'][1] = '''def can_form_palindrome_by_split(a,b):
    return a==a[::-1] or b==b[::-1]
'''
    batch[1616]['wrong_reasons'][1] = 'Checks the whole original strings but never forms a palindrome by combining a prefix and suffix.'

    batch[1620]['wrong'][1] = '''def best_network_coordinate(towers,radius):
    strongest=max(towers,key=lambda tower:tower[2])
    return strongest[:2]
'''
    batch[1620]['wrong_reasons'][1] = 'Uses the strongest individual tower rather than summing signals from all reachable towers.'

    batch[2193]['wrong'][1] = '''def minimum_adjacent_palindrome_moves(s):
    return sum(s[index]!=s[-index-1] for index in range(len(s)//2))
'''
    batch[2193]['wrong_reasons'][1] = 'Counts mismatched mirrored positions instead of the adjacent swaps needed to move characters.'

    batch[2195]['wrong'][0] = '''def minimum_missing_positive_sum(nums,k):
    forbidden=set(nums);chosen=[];value=1
    while len(chosen)<k:
        if value not in forbidden:chosen.append(value)
        value+=2
    return sum(chosen)
'''
    batch[2195]['wrong_reasons'][0] = 'Considers only odd candidate values and misses smaller available even integers.'
