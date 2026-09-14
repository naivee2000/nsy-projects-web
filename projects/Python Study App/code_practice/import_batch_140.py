"""Greedy, strings, and prefix-sum workbook batch 140."""

from itertools import permutations
from .import_batch_055 import entry

def edge_oracle(args):
    edges=args[0];scores=[0]*len(edges)
    for source,target in enumerate(edges):scores[target]+=source
    return min(range(len(edges)),key=lambda node:(-scores[node],node))

def random_edge(rng):
    n=rng.randint(2,30);return [[rng.randrange(n) for _ in range(n)]]

def pattern_oracle(args):
    pattern=args[0]
    for values in permutations('123456789',len(pattern)+1):
        if all((rule=='I' and values[i]<values[i+1]) or (rule=='D' and values[i]>values[i+1]) for i,rule in enumerate(pattern)):return ''.join(values)

def random_pattern(rng):return [''.join(rng.choice('ID') for _ in range(rng.randint(1,7)))]

def seconds_oracle(args):
    text=args[0];seconds=0
    while '01' in text:text=text.replace('01','10');seconds+=1
    return seconds

def random_seconds(rng):return [''.join(rng.choice('01') for _ in range(rng.randint(1,30)))]

def shifts_oracle(args):
    text,operations=args;values=[ord(char)-97 for char in text]
    for left,right,direction in operations:
        delta=1 if direction else -1
        for index in range(left,right+1):values[index]=(values[index]+delta)%26
    return ''.join(chr(value+97) for value in values)

def random_shifts(rng):
    n=rng.randint(1,20);text=''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(n));operations=[]
    for _ in range(rng.randint(0,25)):
        left=rng.randrange(n);operations.append([left,rng.randrange(left,n),rng.randrange(2)])
    return [text,operations]

def garbage_oracle(args):
    garbage,travel=args;total=sum(map(len,garbage))
    for kind in 'MPG':
        last=max((i for i,items in enumerate(garbage) if kind in items),default=0)
        total+=sum(travel[:last])
    return total

def random_garbage(rng):
    n=rng.randint(1,18);garbage=[]
    for _ in range(n):garbage.append(''.join(rng.choice('MPG') for _ in range(rng.randint(1,6))))
    return [garbage,[rng.randint(1,12) for _ in range(n-1)]]

EDGE='''\
def node_with_highest_edge_score(edges):
    scores=[0]*len(edges)
    for source,target in enumerate(edges):scores[target]+=source
    answer=0
    for node in range(1,len(edges)):
        if scores[node]>scores[answer]:answer=node
    return answer
'''

PATTERN='''\
def smallest_number_for_pattern(pattern):
    answer=[];stack=[]
    for index in range(len(pattern)+1):
        stack.append(str(index+1))
        if index==len(pattern) or pattern[index]=='I':
            while stack:answer.append(stack.pop())
    return ''.join(answer)
'''

SECONDS='''\
def seconds_to_rearrange_binary_string(s):
    zeros=0;seconds=0
    for character in s:
        if character=='0':zeros+=1
        elif zeros:seconds=max(seconds+1,zeros)
    return seconds
'''

SHIFTS='''\
def apply_letter_range_shifts(s,shifts):
    difference=[0]*(len(s)+1)
    for left,right,direction in shifts:
        delta=1 if direction else -1;difference[left]+=delta;difference[right+1]-=delta
    running=0;answer=[]
    for index,character in enumerate(s):
        running+=difference[index];answer.append(chr((ord(character)-97+running)%26+97))
    return ''.join(answer)
'''

GARBAGE='''\
def minimum_garbage_collection_time(garbage,travel):
    last={};collection=0
    for house,items in enumerate(garbage):
        collection+=len(items)
        for kind in items:last[kind]=house
    prefix=[0]
    for minutes in travel:prefix.append(prefix[-1]+minutes)
    return collection+sum(prefix[house] for house in last.values())
'''

BATCH={
2374:entry('node_with_highest_edge_score',[('edges','list[int]')],'int',['graphs','arrays'],['Node i contributes its label i to the score of edges[i].','A node’s edge score is the sum of all source labels pointing to it.','Return the smallest node label among those with the maximum score.'],[([[1,0,0,0,0,7,7,5]],'Node 7 receives sources 5 and 6 for score eleven, which is the largest.'),([[2,0,0,2]],'Nodes 0 and 2 both score three, so the smaller label 0 wins the tie.')],[[x] for x in [[0],[1,0],[0,0],[1,1,1],[2,2,0],[1,2,0],[3,3,3,0],[4,4,4,4,0],[2,0,1],[3,0,0,0],[1,0,3,2],[5,5,5,5,5,0],[2,2,3,3],[6,0,0,0,0,0,0]]],EDGE,[EDGE.replace('>scores[answer]','>=scores[answer]'),EDGE.replace('scores[target]+=source','scores[target]+=1')],['Lets a larger node replace the smaller winner when scores tie.','Counts incoming edges instead of summing their source labels.'],edge_oracle,random_edge,['Accumulate each source label into the score of its destination.','Initialize the answer to node zero.','Scan nodes in increasing order and replace the answer only for a strictly larger score.','Every contribution is added exactly once, and strict replacement preserves the first—and therefore smallest—maximum-score index.'],'O(n)','O(n)',5),
2375:entry('smallest_number_for_pattern',[('pattern','str')],'str',['strings','stacks','greedy'],['Pattern contains only I and D and has length at most eight.','Use distinct digits from 1 through 9 to form a number one digit longer than pattern.','I requires an increase and D a decrease; return the lexicographically smallest valid number.'],[(['IIIDIDDD'],'Flush increasing runs and reverse decreasing runs to obtain 123549876.'),(['DDD'],'The four smallest digits must appear in decreasing order, producing 4321.')],[[p] for p in ['I','D','II','ID','DI','DD','III','DII','IDD','DID','IIDDD','DDIII','IDIDID','IIIIIIII']],PATTERN,[PATTERN.replace("stack.append(str(index+1))","stack.append(str(index+2))"),PATTERN.replace("pattern[index]=='I'","pattern[index]=='D'")],['Starts with digit 2 and cannot produce the lexicographically smallest number.','Flushes runs at decreases rather than increases, reversing the wrong segments.'],pattern_oracle,random_pattern,['The smallest solution uses digits 1 through n+1.','Push digits in increasing order while scanning the pattern.','At every I boundary, and after the final digit, pop the stack to reverse the preceding D run.','Each D run must descend, so reversing its smallest available consecutive digits is minimal; flushing at I fixes each prefix as early and small as possible.'],'O(n)','O(n)',5),
2380:entry('seconds_to_rearrange_binary_string',[('s','str')],'int',['strings','dynamic programming'],['Every second, replace all non-overlapping occurrences of 01 with 10 simultaneously.','Repeat until no 01 remains.','Return the number of simultaneous rounds.'],[(['0110101'],'The strings progress through four simultaneous rounds before all ones precede all zeroes.'),(['11100'],'There is no 01 pair initially, so zero seconds are needed.')],[[s] for s in ['0','1','01','10','001','011','010','101','000111','111000','010101','001011','10001','01111000']],SECONDS,[SECONDS.replace('seconds+1','seconds'),SECONDS.replace('max(seconds+1,zeros)','seconds+1')],['Fails to account for a one waiting behind previously moving ones.','Ignores the number of zeroes that a one must cross.'],seconds_oracle,random_seconds,['Count zeroes encountered while scanning left to right.','A one with zeroes before it must move; it needs at least zeros seconds to cross them.','It also cannot finish earlier than one second after the preceding moving one, giving max(seconds+1, zeros).','This recurrence captures both independent lower bounds, and the simultaneous swaps achieve their maximum exactly.'],'O(n)','O(1)',5),
2381:entry('apply_letter_range_shifts',[('s','str'),('shifts','list[list[int]]')],'str',['strings','prefix sums'],['Each operation [left,right,direction] includes both endpoints.','Direction 1 shifts letters forward; direction 0 shifts backward.','Alphabet shifts wrap between a and z; return the string after all operations.'],[(['abc',[[0,1,0],[1,2,1],[0,2,1]]],'The net shifts are zero, one, and two positions, producing ace.'),(['z',[[0,0,1]]],'A forward shift wraps z to a.')],[[s,q] for s,q in [('a',[]),('a',[[0,0,0]]),('abc',[[0,2,1]]),('abc',[[0,2,0]]),('zzz',[[0,1,1],[1,2,1]]),('aaa',[[0,0,0],[2,2,0]]),('xyz',[[0,2,1]]),('hello',[[1,3,0]]),('abcde',[[0,4,1],[0,4,0]]),('az',[[0,0,0],[1,1,1]]),('code',[[0,1,1],[2,3,0]]),('b',[[0,0,0],[0,0,0]]),('mnop',[[1,2,1],[0,3,0]]),('test',[[0,3,1],[1,1,1]])]],SHIFTS,[SHIFTS.replace('1 if direction else -1','-1 if direction else 1'),SHIFTS.replace('difference[right+1]-=delta','difference[right]-=delta')],['Reverses forward and backward operations.','Ends each range one index too early.'],shifts_oracle,random_shifts,['Record +delta at each range start and -delta just after its inclusive end.','Take a prefix sum to obtain the net shift at each character.','Add that net value modulo 26 to produce the final letter.','Difference updates include every operation in constant time, and prefix accumulation applies exactly the operations covering each position.'],'O(n+q)','O(n)',5),
2391:entry('minimum_garbage_collection_time',[('garbage','list[str]'),('travel','list[int]')],'int',['arrays','prefix sums','simulation'],['Each character M, P, or G is one piece collected in one minute.','A dedicated truck for each type starts at house 0 and stops after the last house containing its type.','travel[i] is the time from house i to i+1; return total collection and necessary travel time.'],[([['G','P','GP','GG'],[2,4,3]],'Six pieces take six minutes; the paper truck travels six minutes and the glass truck nine, totaling 21.'),([['MMM','PGM','GP'],[3,10]],'Eight pieces take eight minutes, and all three trucks travel to the last house for 39 travel minutes, totaling 47.')],[[g,t] for g,t in [(['G'],[]),(['M','P'],[5]),(['G','M'],[3]),(['MPG','M'],[4]),(['P','M'],[2]),(['M','P','G'],[1,1]),(['GG','P','M'],[2,3]),(['M','P','M'],[5,7]),(['P','G','P'],[4,6]),(['MP','G','M'],[3,8]),(['G','M','P','G'],[1,2,3]),(['MMM','PPP'],[10]),(['MPG','MPG'],[2]),(['M','G','M','P'],[1,2,3])]],GARBAGE,[GARBAGE.replace('sum(prefix[house] for house in last.values())','3*prefix[-1]'),GARBAGE.replace('return collection+sum','return sum')],['Makes all three trucks travel to the final house even when they can stop earlier.','Omits the one-minute cost of collecting each piece.'],garbage_oracle,random_garbage,['Count every garbage character for the collection-time total.','Record the last house containing each of M, P, and G.','Build prefix travel times from house 0 and add the prefix at each type’s last house.','Each piece must be collected once, and each truck must traverse exactly the route to its last required house, so these independent mandatory costs are sufficient.'],'O(n)','O(n)',5),
}
