"""Reviewed control-only repairs kept separate from oracle/generator modules.

The validation cache hashes the module containing each oracle. Keeping a change
to one candidate's known-wrong control here leaves unrelated oracle evidence
current, while the changed candidate's specification still gets a new cache key.
"""


def apply_quarantine_repairs(batch):
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
