"""Subsequence removals, scored stages, perfect subtrees, battle DP, and keyboard states."""
from itertools import combinations,product
from .import_batch_055 import entry

def is_subsequence(pattern,text):
    it=iter(text);return all(any(char==wanted for char in it) for wanted in pattern)
def removals_oracle(args):
    source,pattern,indices=args;best=0
    for amount in range(len(indices)+1):
        for removed in combinations(indices,amount):
            blocked=set(removed)
            if is_subsequence(pattern,''.join(c for i,c in enumerate(source) if i not in blocked)):best=max(best,amount)
    return best
def random_removals(rng):
    source=''.join(rng.choice('abc') for _ in range(rng.randint(1,11)));picked=sorted(rng.sample(range(len(source)),rng.randint(1,len(source))))
    chosen=sorted(rng.sample(range(len(source)),rng.randint(1,len(source))));pattern=''.join(source[i] for i in chosen)
    return [source,pattern,picked]

def event_oracle(args):
    n,x,y=args;answer=0
    for assignment in product(range(x),repeat=n):answer+=y**len(set(assignment))
    return answer%(10**9+7)
def random_event(rng):return [rng.randint(1,6),rng.randint(1,5),rng.randint(1,5)]

def perfect_oracle(args):
    values,k=args;sizes=[]
    def visit(index):
        if index>=len(values) or values[index] is None:return 0
        left=visit(2*index+1);right=visit(2*index+2)
        if left<0 or left!=right:return -1
        size=left+right+1;sizes.append(size);return size
    visit(0);sizes.sort(reverse=True);return sizes[k-1] if k<=len(sizes) else -1
def random_perfect(rng):
    size=rng.randint(1,31);values=[rng.randint(1,50) for _ in range(size)];return [values,rng.randint(1,min(20,size+3))]

def winning_oracle(args):
    alice=args[0];moves='FWE';answer=0
    for bob in product(moves,repeat=len(alice)):
        if any(a==b for a,b in zip(bob,bob[1:])):continue
        score=sum(1 if (moves.index(b)-moves.index(a))%3==1 else -1 if a!=b else 0 for a,b in zip(alice,bob))
        answer+=score>0
    return answer
def random_winning(rng):return [''.join(rng.choice('FWE') for _ in range(rng.randint(1,9)))]

def keyboard_oracle(args):
    target=args[0];current='';answer=[]
    for wanted in target:
        current+='a';answer.append(current)
        while current[-1]!=wanted:current=current[:-1]+chr(ord(current[-1])+1);answer.append(current)
    return answer
def random_keyboard(rng):return [''.join(rng.choice('abcdef') for _ in range(rng.randint(1,12)))]

REMOVALS='''def maximum_removable_source_indices(source,pattern,target_indices):
    removable=set(target_indices);negative=-10**9;dp=[0]+[negative]*len(pattern)
    for index,char in enumerate(source):
        next_dp=[value+(index in removable) for value in dp]
        for matched in range(len(pattern)):
            if char==pattern[matched]:next_dp[matched+1]=max(next_dp[matched+1],dp[matched])
        dp=next_dp
    return dp[-1]
'''
EVENT='''def count_scored_stage_events(n,x,y):
    modulo=10**9+7;dp=[0]*(x+1);dp[0]=1
    for _ in range(n):
        next_dp=[0]*(x+1)
        for used in range(x+1):
            next_dp[used]=(next_dp[used]+dp[used]*used)%modulo
            if used<x:next_dp[used+1]=(next_dp[used+1]+dp[used]*(x-used))%modulo
        dp=next_dp
    answer=0;score_choices=1
    for used in range(1,x+1):
        score_choices=score_choices*y%modulo;answer=(answer+dp[used]*score_choices)%modulo
    return answer
'''
PERFECT='''def kth_largest_perfect_subtree(root,k):
    sizes=[];computed={};stack=[(root,False)]
    while stack:
        node,visited=stack.pop()
        if node is None:continue
        if not visited:stack.extend(((node,True),(node.right,False),(node.left,False)));continue
        left=computed.get(id(node.left),0);right=computed.get(id(node.right),0)
        if left<0 or left!=right:computed[id(node)]=-1
        else:
            computed[id(node)]=left+right+1;sizes.append(computed[id(node)])
    sizes.sort(reverse=True)
    return sizes[k-1] if k<=len(sizes) else -1
'''
WINNING='''def count_winning_battle_sequences(s):
    modulo=10**9+7;moves='FWE';states={(None,0):1}
    for alice in s:
        next_states={}
        for (last,score),count in states.items():
            for bob in moves:
                if bob==last:continue
                change=0 if bob==alice else 1 if (moves.index(bob)-moves.index(alice))%3==1 else -1
                key=(bob,score+change);next_states[key]=(next_states.get(key,0)+count)%modulo
        states=next_states
    return sum(count for (_,score),count in states.items() if score>0)%modulo
'''
KEYBOARD='''def minimum_keyboard_screen_sequence(target):
    screen='';answer=[]
    for wanted in target:
        screen+='a';answer.append(screen)
        while screen[-1]!=wanted:
            screen=screen[:-1]+chr(ord(screen[-1])+1);answer.append(screen)
    return answer
'''
def lesson(a,b,c,d):return [a,b,c,d]

BATCH={
3316:entry('maximum_removable_source_indices',[('source','str'),('pattern','str'),('target_indices','list[int]')],'int',['dynamic programming','subsequences','strings'],['source length is at most 3,000; pattern is a guaranteed subsequence.','Only original positions in sorted target_indices may be removed, and original indices never shift.','Return the maximum removals that still leave pattern as a subsequence.'],[(['abbaa','aba',[0,1,2]],'Either index one or two can be removed, but not both, so the maximum is one.'),(['bcda','d',[0,3]],'Both indexed characters lie outside the required d and can be removed.')],[[s,p,i] for s,p,i in [('a','a',[0]),('ab','a',[1]),('ab','b',[0]),('abc','ac',[0,1,2]),('aaaa','aa',[0,1,2,3]),('dda','dda',[0,1,2]),('abcabc','abc',[0,1,2]),('abcabc','abc',[3,4,5]),('banana','ana',[0,2,4]),('yeyeykyded','yeyyd',[0,2,3,4]),('abcdef','ace',[1,3,5]),('aabbcc','abc',[0,2,4]),('mississippi','mip',[1,2,3,4]),('ababab','aaa',[1,3,5])]],REMOVALS,[REMOVALS.replace('dp[matched]','next_dp[matched]'),REMOVALS.replace('value+(index in removable)','value+1')],['Reuses the current source character through an in-place match transition.','Counts removal of positions not listed in target_indices.'],removals_oracle,random_removals,lesson('Track how many pattern characters have been matched and the most removable eligible positions so far.','For each source character, either skip/remove it or use it to match the next pattern character.','Skipping gains one only at a target index; matching copies the previous state without that gain.','These are the only choices for every character, so DP maximization covers every feasible retained subsequence.'),'O(nm)','O(m)',7),
3317:entry('count_scored_stage_events',[('n','int'),('x','int'),('y','int')],'int',['dynamic programming','combinatorics'],['n, x, and y are positive and at most 1,000.','Assign each labeled performer to one of x labeled stages; every nonempty stage receives one of y scores.','Count distinct assignments and band scores modulo 1,000,000,007.'],[([1,2,3],'Two stage choices and three score choices give six events.'),([5,2,1],'With one score, all 2^5 performer stage assignments are distinct.')],[[n,x,y] for n,x,y in [(1,1,1),(1,1,5),(2,1,3),(2,2,1),(2,2,2),(3,2,2),(3,3,1),(3,3,4),(4,2,3),(4,4,2),(5,1,7),(5,3,2),(6,2,1),(6,4,3)]],EVENT,[EVENT.replace('dp[used]*used','dp[used]'),EVENT.replace('score_choices=score_choices*y','score_choices=score_choices+y')],['Forgets which occupied stage an arriving performer joins.','Adds score choices instead of multiplying one independent choice per band.'],event_oracle,random_event,lesson('Process labeled performers while tracking how many labeled stages are occupied.','A performer joins one of used stages or opens one of x-used empty stages.','After assignments, multiply the count with j occupied stages by y^j score choices.','The transitions distinguish every stage assignment, and independent band scores multiply exactly once afterward.'),'O(nx)','O(x)',8),
3319:entry('kth_largest_perfect_subtree',[('root','TreeNode | None'),('k','int')],'int',['trees','postorder traversal','sorting'],['The binary tree has 1–2,000 nodes and k is positive.','A perfect subtree has two perfect child subtrees of equal size; an empty child has size zero.','Return the kth-largest perfect-subtree size counting each root, or -1 if fewer than k exist.'],[([[5,3,6,5,2,5,7,1,8,None,None,6,8],2],'The perfect sizes begin 3,3, followed by leaves, so the second largest is three.'),([[1,2,3,4,5,6,7],1],'The entire seven-node tree is perfect and is the largest subtree.')],[[t,k] for t,k in [([1],1),([1],2),([1,2],1),([1,2],2),([1,2,3],1),([1,2,3],2),([1,2,3,4,5,6,7],2),([1,2,3,None,4],3),([1,2,None,3],1),([1,None,2],2),([1,2,3,4,None,None,5],1),([1,2,3,4,5],3),([1,2,3,4,5,6],2),([1,2,3,4,5,6,7,8],4)]],PERFECT,[PERFECT.replace('left!=right','left==right'),PERFECT.replace('left+right+1','max(left,right)+1')],['Rejects equal child sizes and accepts unequal ones.','Stores subtree height-like values rather than node counts.'],perfect_oracle,random_perfect,lesson('A node roots a perfect subtree exactly when both child subtrees are perfect with equal sizes.','Use iterative postorder so child results exist before the parent and deep trees cannot overflow recursion.','Store -1 for nonperfect roots; otherwise store left+right+1 and collect that size.','The recurrence is the perfect-tree definition, and sorting all qualifying roots answers the requested rank.'),'O(n log n)','O(n)',6),
3320:entry('count_winning_battle_sequences',[('s','str')],'int',['dynamic programming','game theory','counting'],['s contains 1–1,000 moves from F, W, E.','Bob chooses F/W/E without repeating his previous move; W beats F, E beats W, and F beats E.','Count Bob sequences with a strictly positive final score difference modulo 1,000,000,007.'],[(['FFF'],'Exactly WFW, FWF, and WEW beat Alice while avoiding repeated moves.'),(['FWEFW'],'There are eighteen legal Bob sequences with a positive final score.')],[[s] for s in ['F','W','E','FF','FW','FE','FFF','FWE','WWW','EEE','FWEFW','FEFE','WEEF','EFWFE']],WINNING,[WINNING.replace('if bob==last:continue','if False:continue'),WINNING.replace('score>0','score>=0')],['Allows Bob to repeat the same creature in consecutive rounds.','Counts tied battles as wins.'],winning_oracle,random_winning,lesson('Only the previous Bob move and current score difference affect future choices.','Map each round to score change -1,0,+1 and aggregate counts by (last move,difference).','Try the two allowed next moves from every state, then sum positive-difference states.','The state retains every constraint-relevant fact and merges only equivalent prefixes, so all legal sequences are counted once.'),'O(n²)','O(n)',8),
3324:entry('minimum_keyboard_screen_sequence',[('target','str')],'list[str]',['strings','simulation'],['target contains 1–400 lowercase English letters.','Key one appends a; key two increments only the last character cyclically.','Return every nonempty screen state on a minimum-keypress route to target.'],[(['abc'],'The states are a, aa, ab, aba, abb, abc.'),(['he'],'Increment the first a through h, append a, then increment it through e.')],[[s] for s in ['a','b','z','aa','az','za','abc','cab','hello','zzz','badge','feed','abcdef','leetcode']],KEYBOARD,[KEYBOARD.replace("current+='a'","current+='b'"),KEYBOARD.replace('answer.append(current)','pass',1)],['Appends b instead of the only appendable character a.','Omits the screen state produced by each append keypress.'],keyboard_oracle,random_keyboard,lesson('Each target position must first be created with append-a, then incremented until it reaches the desired letter.','Finish characters left to right because only the final character can change.','Record immediately after the append and after every required increment.','Every recorded press is forced: one append per character and exactly its alphabet distance from a, proving minimality and unique states.'),'O(total output characters)','O(total output characters)',3),
}
BATCH[3319]['params'][0]=('root','TreeNode | None','treenode')
BATCH[3324]['wrong'][0]=KEYBOARD.replace("screen+='a'","screen+=wanted")
BATCH[3324]['wrong'][1]=KEYBOARD.replace('answer.append(screen)','pass',1)
BATCH[3324]['wrong_reasons'][0]='Appends the desired character directly instead of using the required append-a operation.'
