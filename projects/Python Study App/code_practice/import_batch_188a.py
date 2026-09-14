"""Tournament, bounded distribution, strong-pair, common-prefix, and character-index batch."""
from .import_batch_055 import entry,EXTRA_BOUNDARIES
EXTRA_BOUNDARIES['tournament_champion']=[
    [[[0,1,0,1],[0,0,0,1],[1,1,0,1],[0,0,0,0]]],
    [[[0,1,1,0],[0,0,1,0],[0,0,0,0],[1,1,1,0]]],
    [[[0,0,0,0],[1,0,1,0],[1,0,0,0],[1,1,1,0]]],
    [[[0,1,1,1],[0,0,0,0],[0,1,0,1],[0,1,0,0]]],
]

def champion_oracle(a):
    grid=a[0]
    for team in range(len(grid)):
        if not any(grid[other][team] for other in range(len(grid))):return team
def random_champion(r):
    n=r.randint(1,12);order=list(range(n));r.shuffle(order);rank={v:i for i,v in enumerate(order)}
    return [[[int(rank[i]<rank[j]) if i!=j else 0 for j in range(n)] for i in range(n)]]
def candy_oracle(a):
    n,limit=a;return sum(x+y+z==n for x in range(limit+1) for y in range(limit+1) for z in range(limit+1))
def random_candy(r):return [r.randint(0,50),r.randint(0,50)]
def strong_oracle(a):
    nums=a[0];return max((x^y for x in nums for y in nums if abs(x-y)<=min(x,y)),default=0)
def random_strong(r):return [[r.randint(1,1000) for _ in range(r.randint(1,25))]]
def equal_oracle(a):
    answer=0
    for chars in zip(*a):
        if len(set(chars))>1:break
        answer+=1
    return -1 if answer==0 else sum(map(len,a))-3*answer
def random_equal(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,12))) for _ in range(3)]
def containing_oracle(a):return [i for i,word in enumerate(a[0]) if any(char==a[1] for char in word)]
def random_containing(r):return [[''.join(r.choice('abcde') for _ in range(r.randint(1,10))) for _ in range(r.randint(1,20))],r.choice('abcde')]

CHAMPION='''\
def tournament_champion(grid):
    n=len(grid)
    for team in range(n):
        if all(team==other or grid[other][team]==0 for other in range(n)):return team
'''
CANDY='''\
def bounded_three_child_distributions(n,limit):
    answer=0
    for first in range(limit+1):
        for second in range(limit+1):
            third=n-first-second
            if 0<=third<=limit:answer+=1
    return answer
'''
STRONG='''\
def maximum_strong_pair_xor(nums):
    answer=0
    for i,x in enumerate(nums):
        for y in nums[i:]:
            if abs(x-y)<=min(x,y):answer=max(answer,x^y)
    return answer
'''
EQUAL='''\
def minimum_end_deletions_for_equal_strings(s1,s2,s3):
    common=0
    for a,b,c in zip(s1,s2,s3):
        if a!=b or b!=c:break
        common+=1
    return -1 if common==0 else len(s1)+len(s2)+len(s3)-3*common
'''
CONTAIN='''\
def word_indices_containing_character(words,x):
    return [index for index,word in enumerate(words) if x in word]
'''

BATCH={
2923:entry('tournament_champion',[('grid','list[list[int]]')],'int',['matrices','graphs','indegree'],['grid[i][j]=1 means team i is stronger than team j; diagonal entries are zero.','Exactly one team is not weaker than any other team.','Return that champion team’s zero-based index.'],[([[[0,1],[0,0]]],'Team zero defeats team one and has no incoming defeat.'),([[[0,0,1],[1,0,1],[0,0,0]]],'Team one defeats both other teams, so its index is one.')],[[g] for g in [[[0]],[[0,1],[0,0]],[[0,0],[1,0]],[[0,1,1],[0,0,1],[0,0,0]],[[0,0,0],[1,0,0],[1,1,0]],[[0,0,1],[1,0,1],[0,0,0]],[[0,1,0],[0,0,0],[1,1,0]],[[0,1,1,1],[0,0,1,1],[0,0,0,1],[0,0,0,0]],[[0,0,0,0],[1,0,0,0],[1,1,0,0],[1,1,1,0]],[[0,1,0,1],[0,0,0,0],[1,1,0,1],[0,1,0,0]],[[0,0,1],[1,0,1],[0,0,0]],[[0,1,1],[0,0,0],[0,1,0]],[[0,0,0],[1,0,0],[1,1,0]],[[0,1,0],[0,0,0],[1,1,0]]]],CHAMPION,[CHAMPION.replace('grid[other][team]==0','grid[team][other]==0'),CHAMPION.replace('range(n))','range(n-1))')],['Checks that the team defeats nobody rather than that nobody defeats it.','Ignores the final possible opponent.'],champion_oracle,random_champion,['A loss appears as a one in the champion candidate’s column.','Inspect each column for incoming defeats.','Return the only team whose column contains no one outside its diagonal.','The stated champion condition is exactly zero indegree in the directed win graph.'],'O(n^2)','O(1)',3),
2928:entry('bounded_three_child_distributions',[('n','int'),('limit','int')],'int',['enumeration','combinatorics'],['Distribute exactly n identical candies among three labeled children.','Each child must receive between zero and limit candies inclusive.','Return the number of ordered distributions.'],[([5,2],'Only the three permutations of (1,2,2) meet the limit.'),([3,3],'There are ten nonnegative ordered triples summing to three.')],[[n,l] for n,l in [(0,0),(0,5),(1,0),(1,1),(2,1),(3,1),(4,1),(5,2),(6,2),(7,2),(3,3),(10,10),(10,2),(50,50)]],CANDY,[CANDY.replace('range(limit+1)','range(limit)',1),CANDY.replace('0<=third<=limit','0<third<=limit')],['Excludes the permitted value limit for the first child.','Incorrectly requires the third child to receive at least one candy.'],candy_oracle,random_candy,['Choose amounts for the first two labeled children.','Their choices force the third amount to n-first-second.','Count the pair exactly when the forced amount lies from zero through limit.','Every valid ordered triple has one unique first/second pair, so the enumeration counts it once.'],'O(limit^2)','O(1)',3),
2932:entry('maximum_strong_pair_xor',[('nums','list[int]')],'int',['arrays','bit manipulation','enumeration'],['A pair x,y is strong when abs(x-y) is no greater than min(x,y).','The same element may be paired with itself.','Return the maximum bitwise XOR among all strong pairs.'],[([[1,2,3,4,5]],'The strong pair three and four has XOR seven, which is maximal.'),([[10,100]],'Only self-pairs qualify, each producing XOR zero.')],[[x] for x in [[1],[1,2],[1,3],[2,3],[5,5],[10,100],[1,2,3,4,5],[4,5,6],[7,8,15],[10,15,20],[1,1,2,2],[100,150,200],[3,6,12],[8,9,10,11]]],STRONG,[STRONG.replace('<=min(x,y)','<min(x,y)'),STRONG.replace('x^y','x|y')],['Rejects boundary pairs whose difference equals the smaller value.','Uses bitwise OR instead of XOR.'],strong_oracle,random_strong,['The small source-I constraints permit examining every pair directly.','Check the strong inequality before evaluating a pair.','Keep the largest XOR among qualifying pairs, including each value with itself.','Every permitted pair occurs in the nested scan, so taking their maximum is exact.'],'O(n^2)','O(1)',3),
2937:entry('minimum_end_deletions_for_equal_strings',[('s1','str'),('s2','str'),('s3','str')],'int',['strings','prefixes'],['Only deletions from the ends of the three strings are allowed.','Make all three resulting strings equal and nonempty using the fewest total deletions.','Return -1 when no nonempty common result is possible.'],[(['abc','abb','ab'],'Their longest common prefix is ab; deleting c and b costs two.'),(['dac','bac','cac'],'The first characters already differ, so no nonempty common string is possible.')],[[a,b,c] for a,b,c in [('a','a','a'),('a','a','b'),('ab','a','abc'),('abc','abc','abc'),('abc','abd','abe'),('xabc','x','xyz'),('aaa','aa','a'),('hello','help','he'),('code','cod','co'),('z','zz','zzz'),('same','sam','sample'),('foo','far','faz'),('abcd','abce','abcf'),('pqr','pq','p')]],EQUAL,[EQUAL.replace('common==0','common<0'),EQUAL.replace('-3*common','-common')],['Returns a deletion count instead of -1 when the common prefix is empty.','Subtracts the kept prefix only once rather than once from each string.'],equal_oracle,random_equal,['Any equal result obtainable by end deletion must be a common prefix.','Find the longest prefix shared by all three strings.','If it is empty return -1; otherwise delete every character after it in each string.','Keeping the longest common prefix minimizes deletions, since every shorter feasible prefix removes three additional characters per shortened position.'],'O(min lengths)','O(1)',3),
2942:entry('word_indices_containing_character',[('words','list[str]'),('x','str')],'list[int]',['arrays','strings'],['Inspect each word for the given single lowercase character x.','Return the zero-based indices of every word containing x at least once.','Indices must be returned in increasing order.'],[([['leet','code'],'e'],'Both words contain e, so return indices zero and one.'),([['abc','bcd','aaaa','cbc'],'a'],'Only abc and aaaa contain a, at indices zero and two.')],[[w,x] for w,x in [(['a'],'a'),(['a'],'b'),(['ab','cd'],'a'),(['ab','cd'],'d'),(['xx','x'],'x'),(['one','two','three'],'e'),(['abc','bcd','cde'],'c'),(['zzz','aaa'],'z'),(['hello','world'],'o'),(['same','same'],'m'),(['q','qq','r'],'q'),(['abc','def','ghi'],'z'),(['apple','banana','cherry'],'a'),(['test','case','code'],'c')]],CONTAIN,[CONTAIN.replace('if x in word','if word.startswith(x)'),CONTAIN.replace('enumerate(words)','enumerate(words[1:])')],['Checks only the first character instead of any position.','Skips the first word and returns shifted indices.'],containing_oracle,random_containing,['Each word can be decided independently.','Enumerate words in their original order.','Append the current index whenever membership testing finds x in the word.','Enumeration preserves increasing indices and includes exactly all qualifying words.'],'O(total characters)','O(output)',3),
}
