"""First reviewed group of workbook batch 119."""
from itertools import product
from .import_batch_055 import entry

def increasing_o(a):
 arr,k=a;changes=0
 for start in range(k):
  values=arr[start::k];dp=[]
  for i,value in enumerate(values):dp.append(1+max((dp[j] for j in range(i) if values[j]<=value),default=0))
  changes+=len(values)-max(dp,default=0)
 return changes
def elements_o(a):
 nums,queries=a;n=len(nums);answer=[]
 for time,index in queries:
  phase=time%(2*n)
  current=nums[phase:] if phase<=n else nums[:phase-n]
  answer.append(current[index] if index<len(current) else -1)
 return answer
def words_o(a):return max(len(sentence.split(' ')) for sentence in a[0])
def recipes_o(a):
 recipes,ingredients,supplies=a;available=set(supplies);answer=[];changed=True
 while changed:
  changed=False
  for recipe,needed in zip(recipes,ingredients):
   if recipe not in available and all(x in available for x in needed):available.add(recipe);answer.append(recipe);changed=True
 return answer
def locked_o(a):
 s,locked=a;free=[i for i,x in enumerate(locked) if x=='0']
 for choices in product('()',repeat=len(free)):
  chars=list(s)
  for i,c in zip(free,choices):chars[i]=c
  balance=0;valid=True
  for c in chars:
   balance+=1 if c=='(' else -1
   if balance<0:valid=False;break
  if valid and balance==0:return True
 return False
def rincreasing(r):
 values=[r.randint(1,15) for _ in range(r.randint(1,20))];return [values,r.randint(1,len(values))]
def relements(r):
 nums=[r.randint(-9,9) for _ in range(r.randint(1,10))];return [nums,[[r.randint(0,50),r.randint(0,len(nums)+2)] for _ in range(r.randint(1,10))]]
def rwords(r):return [[' '.join('x' for _ in range(r.randint(1,8))) for _ in range(r.randint(1,8))]]
def rrecipes(r):
 recipes=[f'r{i}' for i in range(r.randint(1,6))];pool=['a','b','c']+recipes;ingredients=[[r.choice(pool) for _ in range(r.randint(1,3))] for _ in recipes];return [recipes,ingredients,['a','b']]
def rlocked(r):
 n=r.randint(1,10);return [''.join(r.choice('()') for _ in range(n)),''.join(r.choice('01') for _ in range(n))]

INCREASING='''\
def minimum_k_increasing_changes(arr,k):
    from bisect import bisect_right
    answer=0
    for start in range(k):
        tails=[];length=0
        for value in arr[start::k]:
            length+=1;index=bisect_right(tails,value)
            if index==len(tails):tails.append(value)
            else:tails[index]=value
        answer+=length-len(tails)
    return answer
'''
ELEMENTS='''\
def cyclic_array_query_values(nums,queries):
    n=len(nums);answer=[]
    for time,index in queries:
        phase=time%(2*n)
        if phase<n and index<n-phase:answer.append(nums[index+phase])
        elif phase>n and index<phase-n:answer.append(nums[index])
        else:answer.append(-1)
    return answer
'''
WORDS='''\
def maximum_sentence_words(sentences):
    return max(sentence.count(' ')+1 for sentence in sentences)
'''
RECIPES='''\
def possible_recipes(recipes,ingredients,supplies):
    from collections import defaultdict,deque
    waiting=defaultdict(list);remaining={}
    for recipe,needed in zip(recipes,ingredients):
        remaining[recipe]=len(needed)
        for item in needed:waiting[item].append(recipe)
    queue=deque(supplies);answer=[]
    while queue:
        item=queue.popleft()
        for recipe in waiting[item]:
            remaining[recipe]-=1
            if remaining[recipe]==0:answer.append(recipe);queue.append(recipe)
    return answer
'''
LOCKED='''\
def can_make_valid_parentheses(s,locked):
    if len(s)%2:return False
    possible=0
    for char,fixed in zip(s,locked):
        if char=='(' or fixed=='0':possible+=1
        elif possible:possible-=1
        else:return False
    possible=0
    for char,fixed in zip(reversed(s),reversed(locked)):
        if char==')' or fixed=='0':possible+=1
        elif possible:possible-=1
        else:return False
    return True
'''
def L(*x):return list(x)
BATCH={
2111:entry('minimum_k_increasing_changes',[('arr','list[int]'),('k','int')],'int',['arrays','binary search','longest nondecreasing subsequence'],['arr contains positive integers and k is between one and its length.','After changes, arr[i-k] must be at most arr[i] for every i at least k.','One operation changes one element to any positive value; return the minimum operations.'],[([[5,4,3,2,1],1],'Only one element can remain in a nondecreasing subsequence, so four changes are needed.'),([[4,1,5,2,6,2],2],'Each residue subsequence is already nondecreasing, requiring zero changes.')],[[a,k] for a,k in [([1],1),([1,2],1),([2,1],1),([1,1],1),([3,2,1],2),([1,3,2,4],2),([4,3,2,1],2),([1,5,2,4,3],1),([5,4,3,2,1],5),([1,2,1,2,1,2],2),([3,1,2,1,3,2],3),([2,2,1,1],2),([9,1,8,2,7,3],2),([1,4,2,5,3,6],3)]],INCREASING,[INCREASING.replace('bisect_right','bisect_left'),INCREASING.replace('arr[start::k]','arr[start+1::k]')],['Computes a strictly increasing subsequence and rejects allowed equal values.','Skips the first value of every residue-class subsequence.'],increasing_o,rincreasing,L('Indices with the same remainder modulo k form independent sequences that must become nondecreasing.','In each sequence, retain a longest nondecreasing subsequence and change every other value.','Use bisect_right patience tails for each arr[start::k]; add length-len(tails).','Retained values already meet every k-step comparison, and any solution can retain no more than an LNDS in each independent sequence.'),'O(n log(n/k))','O(n)',8),
2113:entry('cyclic_array_query_values',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['arrays','modular arithmetic','simulation'],['During minutes zero through n, remove one element from the front per minute; during the next n minutes, append removed elements in original order.','The state repeats every 2*n minutes, with an empty array at phase n.','For each [time,index], return that current element or -1 when the index is absent.'],[([[0,1,2],[[0,2],[2,0],[3,2],[5,0]]],'The queried states give two, two, absent, and zero respectively.'),([[5],[[0,0],[1,0],[2,0],[3,0]]],'The one-element cycle alternates between [5] and empty.')],[[n,q] for n,q in [([1],[[0,0]]),([1],[[1,0]]),([1],[[2,0]]),([1,2],[[0,1],[1,0],[2,0],[3,0],[4,1]]),([1,2,3],[[1,1]]),([1,2,3],[[2,1]]),([1,2,3],[[4,0]]),([1,2,3],[[5,1]]),([1,2,3],[[6,2]]),([9,8],[[100,0]]),([0,-1,2],[[3,0],[4,0]]),([4,5,6,7],[[2,1],[6,1]]),([1,2,3],[[0,5]]),([7,8,9],[[9,0]])]],ELEMENTS,[ELEMENTS.replace('phase<n','phase<=n'),ELEMENTS.replace('phase>n','phase>=n')],['Treats the empty phase as a shrinking-array phase and may index beyond the array.','Treats the empty phase as rebuilding and returns a nonexistent element.'],elements_o,relements,L('Only the time modulo the full remove-and-rebuild cycle matters.','Before phase n the array is nums[phase:]; after phase n it is nums[:phase-n].','Check whether index is within that phase length and map it to nums[index+phase] or nums[index].','The formulas directly describe the exact elements remaining or restored at every phase.'),'O(queries)','O(output)',5),
2114:entry('maximum_sentence_words',[('sentences','list[str]')],'int',['strings','counting'],['sentences is nonempty; each sentence has words separated by one space with no leading or trailing spaces.','Count every word in each sentence.','Return the greatest sentence word count.'],[([['alice and bob love leetcode','i think so too','this is great thanks very much']],'The third sentence has six words, the maximum.'),([['please wait','continue to fight','continue to win']],'The two three-word sentences tie for the maximum.')],[[s] for s in [['a'],['a b'],['a','b c'],['one two three'],['x y','a b c d'],['hello world','single'],['a b c','d e f'],['word','two words','three whole words'],['python code practice'],['red green blue yellow'],['same same same'],['up down','left right center'],['one','one two three four five'],['a b c d e f g']]],WORDS,[WORDS.replace("count(' ')+1","count(' ')") ,WORDS.replace('max(','min(',1)],['Counts spaces but forgets the final word.','Returns the minimum sentence length instead of the maximum.'],words_o,rwords,L('With exactly one separator between words, word count equals space count plus one.','Scan sentences and take the maximum of that value.','Return max(sentence.count(" ")+1 for sentence in sentences).','The separator rule makes the formula exact for every sentence, and max selects the required one.'),'O(total characters)','O(1)',3),
2115:entry('possible_recipes',[('recipes','list[str]'),('ingredients','list[list[str]]'),('supplies','list[str]')],'list[str]',['graphs','topological sorting','hash maps'],['Each recipe has a corresponding ingredient list; recipe names may themselves be ingredients.','Supplies are initially available and cycles without an available entry point cannot be made.','Return every makeable recipe in any order.'],[([['bread'],[['yeast','flour']],['yeast','flour','corn']],'Both required ingredients are supplied, so bread can be made.'),([['bread','sandwich'],[['yeast','flour'],['bread','meat']],['yeast','flour','meat']],'Bread becomes available first and then unlocks sandwich.')],[[r,i,s] for r,i,s in [(['a'],[['x']],['x']),(['a'],[['x']],['y']),(['a','b'],[['x'],['a']],['x']),(['a','b'],[['b'],['a']],[]),(['a','b'],[['x'],['a']],['a']),(['cake','frost'],[['flour','egg'],['sugar']],['flour','egg','sugar']),(['a','b','c'],[['x'],['a'],['b']],['x']),(['a','b','c'],[['b'],['c'],['a']],['x']),(['tea'],[['water','leaf']],['water','leaf','leaf']),(['a','b'],[['x','x'],['a']],['x']),(['r1','r2'],[['s'],['s']],['s']),(['soup','meal'],[['water'],['soup','plate']],['water','plate']),(['a','b'],[['x','y'],['a']],['x']),(['a','b','c'],[['x'],['a','z'],['a']],['x','z'])]],RECIPES,[RECIPES.replace('remaining[recipe]-=1','remaining[recipe]-=2'),RECIPES.replace('queue=deque(supplies)','queue=deque()')],['Consumes two requirements for each available ingredient and unlocks recipes prematurely or not at all.','Never seeds the availability queue with supplies.'],recipes_o,rrecipes,L('Availability flows from each ingredient to the recipes waiting for it.','Build reverse edges ingredient->recipes and an unmet count; process supplies with Kahn’s algorithm.','Decrement a recipe for each available ingredient; at zero, output it and enqueue it as a new supply.','A recipe reaches zero exactly when every ingredient is obtainable; cycles without an initial supply never enter the queue.'),'O(total ingredients+supplies)','O(total ingredients+recipes)',6),
2116:entry('can_make_valid_parentheses',[('s','str'),('locked','str')],'bool',['strings','greedy','parentheses'],['s and locked have equal length; locked zero positions may change to either parenthesis while locked one positions stay fixed.','A valid result has balanced totals and no prefix with more closing than opening parentheses.','Return whether some allowed replacement is valid.'],[(['))()))','010100'],'Unlocked positions can be chosen to create a balanced valid sequence.'),([('()','11')],'The already locked pair is valid.')],[[s,l] for s,l in [('(', '0'),(')', '0'),('()', '11'),(')(', '11'),(')(', '00'),('))', '00'),('((()', '1111'),('()))', '0000'),('(()())','111111'),('))))))','000000'),('((()))','101010'),('())(()','110011'),('())(','0000'),(')()(','0101')]],LOCKED,[LOCKED.replace('if len(s)%2','if len(s)%3'),LOCKED.replace("char==')' or fixed=='0'","char=='(' or fixed=='0'")],['Rejects lengths not divisible by three instead of all odd lengths.','The reverse scan treats locked openings as possible closings.'],locked_o,rlocked,L('A forward scan must be able to cover every locked close; a reverse scan must be able to cover every locked open.','Treat each unlocked character optimistically as an opening in the forward scan and as a closing in reverse.','Reject odd length or either scan whose available balance would go negative.','Both directional feasibility conditions plus even length are necessary and sufficient to assign flexible positions into a globally valid sequence.'),'O(n)','O(1)',6)
}
BATCH[2115]['comparator']='unordered'
BATCH[2116]['examples'][1]=(['()','11'],'The already locked pair is valid.')
BATCH[2116]['boundaries'][2]=['(())','1111']
BATCH[2113]['wrong'][0]=ELEMENTS.replace('2*n','n')
BATCH[2113]['wrong_reasons'][0]='Uses n rather than 2*n as the full removal-and-rebuild cycle length.'
BATCH[2113]['wrong'][1]=ELEMENTS.replace('answer.append(nums[index])','answer.append(nums[(index+phase-n)%n])')
BATCH[2113]['wrong_reasons'][1]='Reads a rotating suffix instead of the original-order prefix during rebuilding.'
