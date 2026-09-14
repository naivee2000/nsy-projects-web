"""First slice of workbook batch 134."""

from itertools import combinations

from .import_batch_055 import entry


def string_value_oracle(args):
    answer=0
    for text in args[0]:
        answer=max(answer,int(text) if all('0'<=char<='9' for char in text) else len(text))
    return answer


def random_string_value(rng):
    alphabet='abc0123456789';return [[''.join(rng.choice(alphabet) for _ in range(rng.randint(1,8))) for _ in range(rng.randint(1,15))]]


def delete_oracle(args):
    rows=[list(row) for row in args[0]];answer=0
    while rows and rows[0]:
        removed=[]
        for row in rows:
            value=max(row);row.remove(value);removed.append(value)
        answer+=max(removed)
    return answer


def random_delete(rng):
    rows,columns=rng.randint(1,7),rng.randint(1,7)
    return [[[rng.randint(1,50) for _ in range(columns)] for _ in range(rows)]]


def similar_oracle(args):
    words=args[0]
    return sum(set(words[i])==set(words[j]) for i,j in combinations(range(len(words)),2))


def random_similar(rng):return [[''.join(rng.choice('abcde') for _ in range(rng.randint(1,8))) for _ in range(rng.randint(1,15))]]


def forts_oracle(args):
    forts=args[0];best=0
    for left in range(len(forts)):
        for right in range(left+1,len(forts)):
            if forts[left]*forts[right]==-1 and all(value==0 for value in forts[left+1:right]):best=max(best,right-left-1)
    return best


def random_forts(rng):return [[rng.choice((-1,0,0,0,1)) for _ in range(rng.randint(2,25))]]


def circular_distance_oracle(args):
    words,target,start=args;n=len(words)
    distances=[min((index-start)%n,(start-index)%n) for index,word in enumerate(words) if word==target]
    return min(distances,default=-1)


def random_circular_distance(rng):
    words=[rng.choice(['a','b','c','d']) for _ in range(rng.randint(1,15))]
    return [words,rng.choice(['a','b','c','d','x']),rng.randrange(len(words))]


STRINGVALUE='''\
def maximum_string_value(strs):
    return max(int(text) if text.isdigit() else len(text) for text in strs)
'''

DELETE='''\
def delete_greatest_row_values(grid):
    for row in grid:row.sort()
    return sum(max(values) for values in zip(*grid))
'''

SIMILAR='''\
def count_similar_string_pairs(words):
    seen={};answer=0
    for word in words:
        key=frozenset(word);answer+=seen.get(key,0);seen[key]=seen.get(key,0)+1
    return answer
'''

FORTS='''\
def maximum_captured_forts(forts):
    previous=None;best=0
    for index,value in enumerate(forts):
        if value:
            if previous is not None and forts[previous]!=value:best=max(best,index-previous-1)
            previous=index
    return best
'''

CIRCULAR='''\
def shortest_circular_target_distance(words,target,startIndex):
    n=len(words);answer=n+1
    for index,word in enumerate(words):
        if word==target:answer=min(answer,(index-startIndex)%n,(startIndex-index)%n)
    return -1 if answer==n+1 else answer
'''


BATCH={
2496:entry('maximum_string_value',[('strs','list[str]')],'int',['strings','simulation'],['A string containing only decimal digits has its integer value.','Any string containing a letter has value equal to its length.','Return the greatest value among all strings.'],[([['alic3','bob','3','4','00000']],'The mixed string alic3 has length five, exceeding all numeric values.'),([['1','01','001','0001']],'Every string is numeric with integer value one, so the maximum is one.')],[[s] for s in [['0'],['10'],['abc'],['9','10'],['99','word'],['000','a'],['a1','20'],['123','abcd'],['0010','9'],['x','999'],['12a','100'],['00000','4'],['hello','42'],['7','eight','90']]],STRINGVALUE,[STRINGVALUE.replace('text.isdigit()','text.isalpha()'),STRINGVALUE.replace('else len(text)','else 0')],['Treats alphabetic strings as integers and numeric strings as lengths.','Assigns zero to every nonnumeric string instead of its length.'],string_value_oracle,random_string_value,['Decide each string’s rule independently.','Use a digit-only check before parsing as an integer.','Otherwise use the string length; take the maximum across results.','The two cases partition all allowed strings and directly implement their defined values.'],'O(total characters)','O(1)',3),
2500:entry('delete_greatest_row_values',[('grid','list[list[int]]')],'int',['matrices','sorting'],['In each round remove the greatest remaining value from every row.','Add the greatest value removed in that round to the score.','Continue until the rectangular grid is empty.'],[([[[1,2,4],[3,3,1]]],'Round maxima contribute four, three, and one, totaling eight.'),([[[10]]],'The only removed value is ten, so the score is ten.')],[[g] for g in [[[1],[2]],[[1,2]],[[1,2],[3,4]],[[4,1],[2,3]],[[1,1],[1,1]],[[1,5,3],[2,4,6]],[[9,8,7],[1,2,3]],[[1,2,3],[4,5,6],[7,8,9]],[[5,5,1],[4,2,2]],[[10,1],[9,8],[7,6]],[[3,1,4,1],[5,9,2,6]],[[2,2,2],[3,3,3]],[[100,1,50],[60,70,80]],[[1,4,2],[3,1,5]]]],DELETE,[DELETE.replace('row.sort()','row.sort(reverse=True)'),DELETE.replace('max(values)','min(values)')],['Sorts descending, causing zip columns to represent removal rounds in reverse order.','Adds the smallest removed value from each round instead of the greatest.'],delete_oracle,random_delete,['Sort each row in increasing order.','The original repeated-max removals correspond to reading sorted rows from right to left.','For each aligned sorted column, add its maximum; column order does not affect the sum.','Sorting fixes every row’s removal sequence, and each zipped column contains exactly one round’s removed values.'],'O(rows*columns log columns)','O(1) besides sorting',3),
2506:entry('count_similar_string_pairs',[('words','list[str]')],'int',['strings','hash maps'],['Two strings are similar when they contain exactly the same set of distinct letters.','Letter multiplicities and order do not matter.','Count index pairs i<j of similar strings.'],[([['aba','aabb','abcd','bac','aabc']],'aba pairs with aabb, while bac pairs with aabc; those are the two similar pairs.'),([['aabb','ab','ba']],'All three strings share letter set {a,b}, so all three index pairs qualify.')],[[w] for w in [['a'],['a','a'],['a','b'],['ab','ba'],['abc','cba','bac'],['aa','a'],['ab','abb'],['abc','abd'],['x','xx','xxx'],['ab','bc','ca'],['abcd','dcba','abc'],['hello','hole'],['aaab','bbaa','ab'],['z','y','z']]],SIMILAR,[SIMILAR.replace('frozenset(word)','tuple(word)'),SIMILAR.replace('answer+=seen.get(key,0)','answer+=1 if key in seen else 0')],['Uses the exact character sequence, so order and multiplicity incorrectly matter.','Counts only one pair for a new match instead of all prior strings with the same signature.'],similar_oracle,random_similar,['Canonicalize each word as its set of distinct letters.','Use that immutable set as a hash-map key.','For each word, add the number of earlier identical keys before incrementing its frequency.','Every similar pair is counted once when its later endpoint is processed.'],'O(total characters)','O(words*alphabet)',3),
2511:entry('maximum_captured_forts',[('forts','list[int]')],'int',['arrays','greedy'],['Values are 1 for your fort, -1 for an enemy fort, and 0 for empty positions.','You may capture empty positions strictly between two nearest nonzero forts of opposite signs.','Return the maximum number of captured empty positions, or zero if no such interval exists.'],[([[1,0,0,-1,0,0,0,0,1]],'The four zeros between the enemy fort and the final friendly fort form the largest capturable interval.'),([[0,0,1,-1]],'Opposite forts are adjacent, so zero empty positions are captured.')],[[a] for a in [[1,-1],[-1,1],[1,0,-1],[1,0,0,1],[-1,0,0,-1],[0,1,0,-1,0],[1,0,0,0,-1],[0,0,0],[1,0,-1,0,1],[-1,0,1,0,0,-1],[1,0,0,-1,0,1],[0,-1,0,0,1,0],[1,1,-1],[-1,0,0,0,1]]],FORTS,[FORTS.replace('forts[previous]!=value','forts[previous]==value'),FORTS.replace('index-previous-1','index-previous')],['Measures gaps between forts of the same side instead of opposite sides.','Counts a boundary fort as captured in addition to the empty positions.'],forts_oracle,random_forts,['Only consecutive nonzero forts can bound a valid all-zero interval.','Remember the index of the previous nonzero fort while scanning.','When the current sign is opposite, maximize current_index-previous_index-1.','Any interval with another fort inside is invalid, so checking consecutive nonzero endpoints covers every possible capture.'],'O(n)','O(1)',3),
2515:entry('shortest_circular_target_distance',[('words','list[str]'),('target','str'),('startIndex','int')],'int',['arrays','circular arrays'],['Moving one step left or right costs one and indexes wrap around.','Return the fewest steps from startIndex to any occurrence of target.','Return -1 when target does not occur.'],[([['hello','i','am','leetcode','hello'],'hello',1],'The occurrence at index zero is one left step from start index one.'),([['a','b','c'],'d',0],'The target is absent, so the result is minus one.')],[[w,t,s] for w,t,s in [(['a'],'a',0),(['a'],'b',0),(['a','b'],'b',0),(['a','b'],'a',1),(['a','b','c'],'c',0),(['a','b','c'],'b',2),(['x','a','x','a'],'a',0),(['x','a','x','a'],'a',3),(['one','two','three'],'one',2),(['one','two','three'],'three',0),(['a','b','a','c','a'],'a',1),(['a','b','c','d'],'d',1),(['z','y','x','z'],'z',2),(['same','same'],'same',1)]],CIRCULAR,[CIRCULAR.replace('(index-startIndex)%n,(startIndex-index)%n','abs(index-startIndex)'),CIRCULAR.replace('return -1 if answer==n+1 else answer','return answer')],['Uses only direct linear distance and ignores the shorter wraparound route.','Returns an out-of-range sentinel instead of -1 when the target is absent.'],circular_distance_oracle,random_circular_distance,['For an occurrence at index i, clockwise distance is (i-start)%n and counterclockwise distance is (start-i)%n.','Take the smaller directional distance for each occurrence.','Minimize across all matching indexes; return -1 if none match.','The two directions are the only simple routes on a cycle, so their minimum is the shortest path to each occurrence.'],'O(n)','O(1)',3),
}

BATCH[2500]['wrong'][0]='''\
def delete_greatest_row_values(grid):
    return sum(max(row) for row in grid)
'''
BATCH[2500]['wrong_reasons'][0]='Adds each row maximum once and ignores all later deletion rounds.'
BATCH[2496]['wrong'][0]='''\
def maximum_string_value(strs):
    return max(len(text) for text in strs)
'''
BATCH[2496]['wrong_reasons'][0]='Uses character count for numeric strings instead of parsing their integer value.'
