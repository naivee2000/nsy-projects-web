"""Conflicting pairs, recursive substitutions, trie-prefix removal, special paths, and circular queries."""
from collections import Counter
from itertools import combinations

from .import_batch_055 import entry


def conflicts_oracle(args):
    n,pairs=args;answer=0
    for removed in range(len(pairs)):
        remaining=[tuple(sorted(pair)) for index,pair in enumerate(pairs) if index!=removed];count=0
        for left in range(1,n+1):
            for right in range(left,n+1):count+=all(not (left<=a and b<=right) for a,b in remaining)
        answer=max(answer,count)
    return answer


def random_conflicts(rng):
    n=rng.randint(2,9);pairs=rng.sample(list(combinations(range(1,n+1),2)),rng.randint(1,min(10,n*(n-1)//2)))
    return [n,[list(pair) for pair in pairs]]


def substitutions_oracle(args):
    replacements,text=args;mapping=dict(replacements)
    while '%' in text:
        left=text.index('%');right=text.index('%',left+1);text=text[:left]+mapping[text[left+1:right]]+text[right+1:]
    return text


def random_substitutions(rng):
    keys=['A','B','C','D'][:rng.randint(1,4)];replacements=[]
    for index,key in reversed(list(enumerate(keys))):
        suffix='' if index==len(keys)-1 or rng.random()<.4 else '%'+rng.choice(keys[index+1:])+'%'
        replacements.append([key,rng.choice(('x','y','ab'))+suffix])
    text='_'.join('%'+rng.choice(keys)+'%' for _ in range(rng.randint(1,5)));return [replacements,text]


def lcp(values):
    if not values:return 0
    answer=0
    while all(answer<len(value) and value[answer]==values[0][answer] for value in values):answer+=1
    return answer


def prefixes_oracle(args):
    words,k=args;answer=[]
    for removed in range(len(words)):
        remaining=words[:removed]+words[removed+1:]
        answer.append(max((lcp(list(group)) for group in combinations(remaining,k)),default=0))
    return answer


def random_prefixes(rng):
    n=rng.randint(2,9);return [[''.join(rng.choice('abcd') for _ in range(rng.randint(1,7))) for _ in range(n)],rng.randint(1,n)]


def path_oracle(args):
    edges,values=args;n=len(values);graph=[[] for _ in range(n)]
    for left,right,weight in edges:graph[left].append((right,weight));graph[right].append((left,weight))
    parent=[-1]*n;distance=[0]*n;paths=[None]*n;paths[0]=[0];stack=[0]
    for node in stack:
        for child,weight in graph[node]:
            if child!=parent[node]:parent[child]=node;distance[child]=distance[node]+weight;paths[child]=paths[node]+[child];stack.append(child)
    best_length=0;best_nodes=1
    for end,path in enumerate(paths):
        for offset,start in enumerate(path):
            counts=Counter(values[node] for node in path[offset:])
            if max(counts.values())<=2 and sum(count==2 for count in counts.values())<=1:
                length=distance[end]-distance[start];nodes=len(path)-offset
                if length>best_length or (length==best_length and nodes<best_nodes):best_length,best_nodes=length,nodes
    return [best_length,best_nodes]


def random_path(rng):
    n=rng.randint(2,9);edges=[[rng.randrange(node),node,rng.randint(1,9)] for node in range(1,n)];rng.shuffle(edges)
    return [edges,[rng.randint(0,4) for _ in range(n)]]


def queries_oracle(args):
    nums,queries=args;n=len(nums);answer=[]
    for index in queries:
        candidates=[min(abs(index-other),n-abs(index-other)) for other,value in enumerate(nums) if other!=index and value==nums[index]]
        answer.append(min(candidates,default=-1))
    return answer


def random_queries(rng):
    n=rng.randint(1,20);nums=[rng.randint(1,6) for _ in range(n)];return [nums,[rng.randrange(n) for _ in range(rng.randint(1,15))]]


CONFLICTS='''def maximize_valid_subarrays_after_removal(n,conflicting_pairs):
    starts=[[] for _ in range(n+1)]
    for left,right in conflicting_pairs:
        if left>right:left,right=right,left
        starts[left].append(right)
    gains=[0]*(n+2);base=best_gain=0;first=second=n+1
    for left in range(n,0,-1):
        for right in starts[left]:
            if right<first:second,first=first,right
            elif right<second:second=right
        base+=first-left;gains[first]+=second-first;best_gain=max(best_gain,gains[first])
    return base+best_gain
'''

SUBSTITUTIONS='''def apply_recursive_substitutions(replacements,text):
    mapping=dict(replacements);memo={}
    def expand_key(key):
        if key not in memo:memo[key]=expand(mapping[key])
        return memo[key]
    def expand(value):
        pieces=[];position=0
        while True:
            left=value.find('%',position)
            if left<0:pieces.append(value[position:]);return ''.join(pieces)
            right=value.find('%',left+1);pieces.append(value[position:left]);pieces.append(expand_key(value[left+1:right]));position=right+1
    return expand(text)
'''

PREFIXES='''def longest_k_prefixes_after_removal(words,k):
    if len(words)-1<k:return [0]*len(words)
    children=[{}];counts=[0];depth=[0];paths=[]
    for word in words:
        node=0;path=[]
        for char in word:
            if char not in children[node]:children[node][char]=len(children);children.append({});counts.append(0);depth.append(depth[node]+1)
            node=children[node][char];counts[node]+=1;path.append(node)
        paths.append(path)
    maximum=max(depth);levels=[0]*(maximum+1)
    for node in range(1,len(children)):
        if counts[node]>=k:levels[depth[node]]+=1
    size=1
    while size<=maximum:size*=2
    tree=[0]*(2*size)
    for value in range(1,maximum+1):tree[size+value]=value if levels[value] else 0
    for node in range(size-1,0,-1):tree[node]=max(tree[node*2],tree[node*2+1])
    def update(value,delta):
        levels[value]+=delta;node=size+value;tree[node]=value if levels[value] else 0;node//=2
        while node:tree[node]=max(tree[node*2],tree[node*2+1]);node//=2
    answer=[]
    for path in paths:
        changed=[]
        for node in path:
            if counts[node]==k:update(depth[node],-1);changed.append(depth[node])
        answer.append(tree[1])
        for value in changed:update(value,1)
    return answer
'''

PATH='''def longest_one_duplicate_tree_path(edges,nums):
    import sys
    sys.setrecursionlimit(max(1000,3*len(nums)));n=len(nums);graph=[[] for _ in range(n)]
    for left,right,weight in edges:graph[left].append((right,weight));graph[right].append((left,weight))
    penult=[0]*(n+2);third=[0]*(n+2);occurrences={};distances=[];best_length=0;best_nodes=1
    def add(tree,index,delta):
        index+=1
        while index<len(tree):tree[index]+=delta;index+=index&-index
    def kth(tree,order):
        index=0;bit=1<<(len(tree).bit_length()-1)
        while bit:
            nxt=index+bit
            if nxt<len(tree) and tree[nxt]<order:order-=tree[nxt];index=nxt
            bit//=2
        return index
    def total(tree):
        index=len(tree)-1;answer=0
        while index:answer+=tree[index];index-=index&-index
        return answer
    def visit(node,parent,depth,distance):
        nonlocal best_length,best_nodes
        value=nums[node];items=occurrences.setdefault(value,[])
        if len(items)>=2:add(penult,items[-2],-1)
        if len(items)>=3:add(third,items[-3],-1)
        items.append(depth)
        if len(items)>=2:add(penult,items[-2],1)
        if len(items)>=3:add(third,items[-3],1)
        distances.append(distance);duplicate_total=total(penult);third_total=total(third);left=0
        if duplicate_total>=2:left=max(left,kth(penult,duplicate_total-1)+1)
        if third_total:left=max(left,kth(third,third_total)+1)
        length=distance-distances[left];nodes=depth-left+1
        if length>best_length or (length==best_length and nodes<best_nodes):best_length,best_nodes=length,nodes
        for child,weight in graph[node]:
            if child!=parent:visit(child,node,depth+1,distance+weight)
        if len(items)>=2:add(penult,items[-2],-1)
        if len(items)>=3:add(third,items[-3],-1)
        items.pop()
        if len(items)>=2:add(penult,items[-2],1)
        if len(items)>=3:add(third,items[-3],1)
        if not items:occurrences.pop(value);distances.pop()
        else:distances.pop()
    visit(0,-1,0,0);return [best_length,best_nodes]
'''

QUERIES='''def closest_equal_circular_queries(nums,queries):
    from bisect import bisect_left
    positions={}
    for index,value in enumerate(nums):positions.setdefault(value,[]).append(index)
    n=len(nums);answer=[]
    for query in queries:
        group=positions[nums[query]]
        if len(group)==1:answer.append(-1);continue
        place=bisect_left(group,query);previous=group[place-1];following=group[(place+1)%len(group)]
        answer.append(min((query-previous)%n,(following-query)%n))
    return answer
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


CONFLICT_CASES=[[n,pairs] for n,pairs in [(4,[[2,3],[1,4]]),(3,[[1,2]]),(2,[[1,2]]),(4,[[1,2],[2,3]]),(5,[[1,5],[2,4]]),(5,[[1,3],[1,4],[2,5]]),(6,[[1,2],[3,4],[5,6]]),(6,[[1,6],[2,5],[3,4]]),(7,[[1,4],[2,6],[3,7]]),(5,[[1,2],[1,3],[1,4],[1,5]]),(8,[[2,8],[3,7],[4,6]]),(4,[[1,4],[1,3],[2,4]]),(6,[[1,3],[2,4],[3,5],[4,6]]),(7,[[1,7],[1,6],[2,5],[3,4]])]]
SUBSTITUTION_CASES=[[replacements,text] for replacements,text in [([['A','abc'],['B','def']],'%A%_%B%'),([['A','x']],'%A%'),([['A','x']],'%A%%A%'),([['A','%B%'],['B','z']],'%A%'),([['A','x%B%y'],['B','q']],'%A%'),([['A','%B%'],['B','%C%'],['C','end']],'%A%'),([['X','one'],['Y','two']],'%Y%-%X%'),([['A','a'],['B','b%A%']],'%B%'),([['A','hello']],'%A% world'),([['A','x'],['B','y']],'%A%_%B%_%A%'),([['ROOT','%L%%R%'],['L','left'],['R','right']],'%ROOT%'),([['A','1'],['B','2'],['C','%A%%B%']],'%C%%C%'),([['K','value']],'plain %K% text'),([['A','%B%x'],['B','%C%y'],['C','z']],'%A%')]]
PREFIX_CASES=[[words,k] for words,k in [(['jump','run','run','jump','run'],2),(['a','b'],1),(['abc','abc','abd'],2),(['x','x','x'],2),(['flower','flow','flight'],2),(['aa','ab','ac','ad'],3),(['prefix','presto','prevent','x'],2),(['a','aa','aaa'],2),(['cat','dog','fish'],2),(['same','same'],1),(['ab','abc','abcd','abx'],3),(['zoo','zoom','zebra','zen'],2),(['one','only','once','on'],2),(['abc','def','ghi','abc'],2)]]
PATH_CASES=[[edges,values] for edges,values in [([[0,1,1],[1,2,3],[1,3,1],[2,4,6],[4,7,2],[3,5,2],[3,6,5],[6,8,3]],[1,1,0,3,1,2,1,1,0]),([[0,1,5]],[1,1]),([[0,1,5]],[1,2]),([[0,1,2],[1,2,3]],[1,1,1]),([[0,1,2],[1,2,3]],[1,2,1]),([[0,1,1],[1,2,1],[2,3,1]],[1,2,1,2]),([[0,1,4],[0,2,5]],[1,1,1]),([[0,1,3],[1,2,4],[1,3,5]],[1,2,2,3]),([[0,1,2],[1,2,8],[2,3,1],[3,4,7]],[1,2,3,2,4]),([[0,1,2],[1,2,2],[2,3,2],[3,4,2]],[1,1,2,2,3]),([[0,1,7],[0,2,1],[2,3,9],[2,4,2]],[5,4,5,2,1]),([[0,1,1],[1,2,10],[1,3,3],[3,4,8]],[0,1,2,1,3]),([[0,1,6],[1,2,5],[1,3,4],[3,4,3],[3,5,2]],[1,2,3,1,1,5]),([[0,1,1],[1,2,2],[2,3,3],[3,4,4],[4,5,5]],[1,2,1,3,1,4])]]
QUERY_CASES=[[nums,queries] for nums,queries in [([1,3,1,4,1,3,2],[0,3,5]),([1],[0]),([1,1],[0,1]),([1,2,1],[0,2]),([1,2,3],[0,1,2]),([1,2,3,1],[0,3]),([5,1,2,3,5],[0,4]),([1,2,1,2],[0,1,2,3]),([7,7,7],[0,1,2]),([1,2,3,2,1],[0,2,4]),([4,1,4,2,4,1],[1,3,5]),([9,8,7,9,8,7],[0,1,2]),([1,1,2,3,2,3],[0,2,4]),([6,5,6,5,6,5,4],[0,3,6])]]


BATCH={
3480:entry('maximize_valid_subarrays_after_removal',[('n','int'),('conflicting_pairs','list[list[int]]')],'int',['arrays','prefix sums','enumeration'],['nums is implicitly [1,2,...,n], and conflicting_pairs is nonempty.','Remove exactly one conflicting pair.','Count nonempty intervals [left,right] containing neither endpoint pair of every remaining conflict, and maximize that count.'],[([4,[[2,3],[1,4]]],'Removing the more restrictive pair permits nine valid subarrays.'),([3,[[1,2]]],'Removing the only conflict makes all six nonempty subarrays valid.')],CONFLICT_CASES,CONFLICTS,[CONFLICTS.replace('return base+best_gain','return base'),CONFLICTS.replace('gains[first]+=second-first','gains[first]=second-first')],['Counts valid subarrays without applying the best single-pair removal gain.','Overwrites gains shared by the same active limiting pair instead of accumulating them.'],conflicts_oracle,random_conflicts,lesson('For each left endpoint, only the smallest and second-smallest conflicting right endpoints determine validity and the benefit of removing the active pair.','Sweep left endpoints backward while maintaining those two right boundaries and accumulate removal gains by the smallest boundary.','Add first-left to the base; add second-first to the gain bucket for first; return base plus the largest bucket.','Every invalid extension begins at the current smallest conflict, and removing that pair exposes exactly the second boundary until another left endpoint changes the limits.'),'O(n+p)','O(n+p)',8),
3481:entry('apply_recursive_substitutions',[('replacements','list[list[str]]'),('text','str')],'str',['strings','graphs','recursion'],['Replacement keys are unique, every placeholder references a defined key, and dependencies are acyclic.','A placeholder has the form %KEY% and replacement values may contain further placeholders.','Recursively expand every placeholder so the final text contains none.'],[([[['A','abc'],['B','def']],'%A%_%B%'],'The two placeholders expand to abc and def, producing abc_def.'),([[['A','%B%'],['B','z']],'%A%'],'A expands through B, producing z.')],SUBSTITUTION_CASES,SUBSTITUTIONS,[SUBSTITUTIONS.replace("memo[key]=expand(mapping[key])","memo[key]=mapping[key]"),SUBSTITUTIONS.replace('pieces.append(expand_key(value[left+1:right]))','pieces.append(value[left+1:right])')],['Expands each key only one level and leaves nested placeholders unresolved.','Inserts placeholder key names rather than their mapped values.'],substitutions_oracle,random_substitutions,lesson('Replacement dependencies form an acyclic directed graph, so each key can be expanded once and memoized.','Parse placeholder pairs recursively and cache fully expanded mapping values.','Append literal spans; for each %KEY%, append expand_key(KEY); recursively expand the mapped value on first use.','Acyclicity guarantees termination, and memoization prevents repeated work for keys referenced many times.'),'O(output length+input length)','O(output length+mapping size)',6),
3485:entry('longest_k_prefixes_after_removal',[('words','list[str]'),('k','int')],'list[int]',['strings','tries','segment trees'],['words is nonempty, k is positive, and lowercase word lengths total at most 100,000.','For each index, remove that word and choose any k remaining words.','Return the maximum common-prefix length attainable by that choice, or zero if fewer than k remain.'],[([['jump','run','run','jump','run'],2],'Removing each word produces prefix lengths [3,4,4,3,4].'),([['abc','abc','abd'],2],'Removing abd leaves two identical words with prefix length three; removing either abc leaves prefix length two.')],PREFIX_CASES,PREFIXES,[PREFIXES.replace('counts[node]==k','counts[node]>=k'),PREFIXES.replace('if counts[node]==k:update(depth[node],-1);changed.append(depth[node])','if False:update(depth[node],-1);changed.append(depth[node])')],['Temporarily removes every qualifying trie node on the word path, including nodes that remain supported by more than k words.','Reuses the global best prefix without removing the queried word’s critical path nodes.'],prefixes_oracle,random_prefixes,lesson('Removing one word only invalidates trie nodes on its path whose original count is exactly k.','Count qualifying trie nodes by depth and maintain the greatest nonempty depth in a segment tree.','For each word, decrement depth counts for path nodes with count k, read the maximum active depth, then restore them.','Nodes off the path are unchanged, nodes above k remain qualifying, and every k-word common prefix corresponds to a trie node with count at least k.'),'O(total_chars log max_length)','O(total_chars+max_length)',8),
3486:entry('longest_one_duplicate_tree_path',[('edges','list[list[int]]'),('nums','list[int]')],'list[int]',['trees','recursion','fenwick trees'],['edges describes a positive-weight tree rooted at zero.','A valid downward ancestor-to-descendant path has all distinct values except that at most one value may occur twice.','Return [maximum total edge length, minimum node count among paths attaining that length].'],[([[[0,1,1],[1,2,3],[1,3,1],[2,4,6],[4,7,2],[3,5,2],[3,6,5],[6,8,3]],[1,1,0,3,1,2,1,1,0]],'The optimal special path has total length nine and uses three nodes.'),([[[0,1,5]],[1,1]],'One duplicated value is permitted, so the two-node path has length five.')],PATH_CASES,PATH,[PATH.replace('duplicate_total>=2','duplicate_total>=3').replace('duplicate_total-1','duplicate_total-2'),PATH.replace("if third_total:left=max(left,kth(third,third_total)+1)","if False:left=max(left,kth(third,third_total)+1)")],['Allows two distinct values to be duplicated by discarding only the third-largest duplicate boundary.','Ignores third occurrences and can admit one value three times.'],path_oracle,random_path,lesson('A window is valid after excluding all third occurrences and all but the largest active duplicate boundary.','During recursive DFS, maintain each value’s path occurrences plus Fenwick markers for penultimate and third-from-last depths.','Set the left boundary after the maximum third marker and after the second-largest penultimate marker; measure the prefix-distance span, then backtrack updates.','These two boundaries enforce frequency at most two and at most one duplicated value, while every ancestor window ending at each node is considered.'),'O(n log n)','O(n)',8),
3488:entry('closest_equal_circular_queries',[('nums','list[int]'),('queries','list[int]')],'list[int]',['arrays','hash maps','binary search'],['nums is a nonempty circular array and every query is a valid index.','For each query, find another index with the same value.','Return the smallest circular index distance, or -1 if the value occurs only once.'],[([[1,3,1,4,1,3,2],[0,3,5]],'Index zero is two steps from another one, index three has no other four, and index five is three circular steps from another three.'),([[1,1],[0,1]],'Each index is one step from the other equal value.')],QUERY_CASES,QUERIES,[QUERIES.replace('(query-previous)%n','query-previous'),QUERIES.replace('if len(group)==1:answer.append(-1);continue','if len(group)==1:answer.append(0);continue')],['Uses linear distance to the previous occurrence and misses wraparound.','Returns zero for values with no other matching index.'],queries_oracle,random_queries,lesson('Equal-value indices form sorted circular position lists; only the predecessor and successor can be closest.','Group indices by value and binary-search each queried position within its group.','Measure modular distance to the previous and next group members; return their minimum, or -1 for a singleton group.','Any farther equal occurrence lies beyond one of these neighbors along a circular direction and cannot improve the distance.'),'O((n+q) log n)','O(n)',6),
}
