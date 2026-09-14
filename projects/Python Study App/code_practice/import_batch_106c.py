"""Third reviewed group of workbook batch 106."""
from .import_batch_055 import entry

def xor_pairs_o(a):
 nums,low,high=a;return sum(low<=nums[i]^nums[j]<=high for i in range(len(nums)) for j in range(i+1,len(nums)))
def integers_o(a):
 word=a[0];values=set();current=''
 for char in word+'a':
  if char.isdigit():current+=char
  elif current:values.add(current.lstrip('0') or '0');current=''
 return len(values)
def permutation_o(a):
 n=a[0];original=list(range(n));current=original[:];steps=0
 while True:
  current=[current[i//2] if i%2==0 else current[n//2+(i-1)//2] for i in range(n)];steps+=1
  if current==original:return steps
def evaluate_o(a):
 s,knowledge=a;known=dict(knowledge);answer='';index=0
 while index<len(s):
  if s[index]!='(':answer+=s[index];index+=1;continue
  end=s.index(')',index);answer+=known.get(s[index+1:end],'?');index=end+1
 return answer
def divisors_o(a):
 total=a[0];best=[0]*(total+1);best[0]=1
 for amount in range(1,total+1):best[amount]=max(part*best[amount-part] for part in range(1,amount+1))
 return best[total]%(10**9+7)
def rxor(r):
 nums=[r.randint(1,63) for _ in range(r.randint(1,15))];low=r.randint(1,63);return [nums,low,r.randint(low,80)]
def rintegers(r):return [''.join(r.choice('abc0123456789') for _ in range(r.randint(1,50)))]
def rpermutation(r):return [2*r.randint(1,40)]
def revaluate(r):
 keys=['a','bb','cat','x'];knowledge=[[key,''.join(r.choice('pqrs') for _ in range(r.randint(1,4)))] for key in r.sample(keys,r.randint(0,4))]
 pieces=[]
 for _ in range(r.randint(1,8)):pieces.append('('+r.choice(keys+['missing'])+')' if r.random()<.5 else ''.join(r.choice('wz') for _ in range(r.randint(1,4))))
 return [''.join(pieces),knowledge]
def rdivisors(r):return [r.randint(1,60)]
XOR='''def count_xor_pairs_in_range(nums, low, high):
 class Node:
  def __init__(self):self.children=[None,None];self.count=0
 root=Node()
 def insert(value):
  node=root
  for bit in range(15,-1,-1):
   digit=value>>bit&1
   if node.children[digit] is None:node.children[digit]=Node()
   node=node.children[digit];node.count+=1
 def below(value,limit):
  node=root;answer=0
  for bit in range(15,-1,-1):
   if node is None:break
   digit=value>>bit&1
   if limit>>bit&1:
    if node.children[digit]:answer+=node.children[digit].count
    node=node.children[digit^1]
   else:node=node.children[digit]
  return answer
 answer=0
 for value in nums:answer+=below(value,high+1)-below(value,low);insert(value)
 return answer
'''
INTEGERS='''def count_distinct_integers(word):
 values=set();index=0
 while index<len(word):
  if not word[index].isdigit():index+=1;continue
  end=index
  while end<len(word) and word[end].isdigit():end+=1
  normalized=word[index:end].lstrip('0') or '0';values.add(normalized);index=end
 return len(values)
'''
PERMUTATION='''def permutation_reinitialization_steps(n):
 position=1;steps=0
 while True:
  position=position*2 if position<n//2 else (position-n//2)*2+1;steps+=1
  if position==1:return steps
'''
EVALUATE='''def evaluate_bracket_keys(s, knowledge):
 known=dict(knowledge);answer=[];index=0
 while index<len(s):
  if s[index]=='(':
   end=s.find(')',index+1);answer.append(known.get(s[index+1:end],'?'));index=end+1
  else:answer.append(s[index]);index+=1
 return ''.join(answer)
'''
DIVISORS='''def maximum_nice_divisors(prime_factors):
 mod=10**9+7
 if prime_factors<=3:return prime_factors
 quotient,remainder=divmod(prime_factors,3)
 if remainder==0:return pow(3,quotient,mod)
 if remainder==1:return 4*pow(3,quotient-1,mod)%mod
 return 2*pow(3,quotient,mod)%mod
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1803:E('count_xor_pairs_in_range',[('nums','list[int]'),('low','int'),('high','int')],'int',['arrays','bit-manipulation','tries'],['Count index pairs i<j whose XOR lies in the inclusive range [low,high].','Values and bounds are positive and at most twenty thousand.'],[([[1,4,2,7],2,6],'All six index pairs have XOR between two and six.'),([[9,8,4,2,1],5,14],'Exactly eight of the ten pairs fall within the requested range.')],[[*x] for x in [([1],1,2),([1,2],1,3),([1,1],1,1),([1,4,2,7],2,6),([9,8,4,2,1],5,14),([2,3,4],0,0),([2,3,4],1,7),([5,5,5],0,0),([1,8,16],2,10),([7,12,3,9],4,12),([10,20,30],1,15),([1,2,4,8],3,9),([15,1,6,11,4],5,10),([31,32,63],1,63)]],XOR,[XOR.replace('high+1','high'),XOR.replace('-below(value,low)','-below(value,low+1)')],['Treats the inclusive upper bound as exclusive.','Treats the inclusive lower bound as exclusive.'],xor_pairs_o,rxor,H('Count XOR values below a limit, then subtract two prefix counts.','Insert earlier values in a binary trie and query each new value bit by bit.','For a one bit in limit, count the branch that keeps XOR zero and continue through the XOR-one branch.','The trie partitions all earlier numbers by the first differing XOR bit, so below(high+1)-below(low) counts exactly each valid pair once.'),'O(n*bits)','O(n*bits)',8),
1805:E('count_distinct_integers',[('word','str')],'int',['strings','hash-maps','parsing'],['Maximal digit runs form the integers; letters separate runs.','Ignore leading zeros when comparing values, with every all-zero run representing zero.'],[(['a123bc34d8ef34'],'The runs represent 123, 34, 8, and 34, giving three distinct integers.'),(['a1b01c001'],'All three runs represent integer one after removing leading zeros.')],[[s] for s in ['0','00','a','1','a1','1a2','a123bc34d8ef34','leet1234code234','a1b01c001','000a000','9x09y0090','12abc12','1a11a111','abc0010def10']],INTEGERS,[INTEGERS.replace(".lstrip('0') or '0'",''),INTEGERS.replace('values.add(normalized)','values.add(word[index])')],['Counts strings with different leading-zero spellings separately.','Keeps only the first digit of every integer run.'],integers_o,rintegers,H('Letters split the input into maximal digit runs.','Normalize each run by stripping leading zeros, using 0 for an empty remainder.','Insert normalized runs into a set and return its size.','Decimal strings without leading zeros are unique representations, so set equality is exactly integer equality without requiring large numeric conversion.'),'O(n)','O(n)',3),
1806:E('permutation_reinitialization_steps',[('n','int')],'int',['arrays','math','simulation'],['n is even and the initial permutation is [0,1,...,n-1].','Apply the stated even/odd index rearrangement until the full permutation first returns; return the positive operation count.'],[([2],'The length-two permutation is unchanged after one operation.'),([4],'The permutation becomes [0,2,1,3] and returns after the second operation.')],[[n] for n in [2,4,6,8,10,12,14,16,18,20,30,50,100,1000]],PERMUTATION,[PERMUTATION.replace('position=1','position=2',1),PERMUTATION.replace('position<n//2','position<=n//2')],['Tracks the orbit of the wrong initial position.','Uses the wrong branch at the midpoint.'],permutation_o,rpermutation,H('Positions zero and n-1 never move; track the orbit of position one.','Derive its next position from whether it lies in the first or second half.','Count transitions until position one returns to itself.','The shuffle is a permutation, and its nontrivial positions share the cycle order governing restoration; the orbit length of one is the first full reset.'),'O(answer)','O(1)',5),
1807:E('evaluate_bracket_keys',[('s','str'),('knowledge','list[list[str]]')],'str',['strings','hash-maps','parsing'],['Bracketed keys are nonempty and brackets never nest.','Replace known keys with their values and unknown keys with a single question mark.'],[(['(name)is(age)yearsold',[['name','bob'],['age','two']]],'Known keys produce bobistwoyearsold.'),(['hi(name)',[['a','b']]],'The unknown key name becomes a question mark, producing hi?.')],[[*x] for x in [('plain',[]),('(a)',[['a','x']]),('(a)',[]),('(a)(b)',[['a','x'],['b','y']]),('x(a)y',[['a','z']]),('(missing)is(a)',[['a','ok']]),('a(b)c(d)',[['b','B']]),('(x)tail',[['x','head']]),('pre(x)',[]),('(longkey)',[['longkey','v']]),('a(b)c',[['b','']]),('(a)-(b)',[['a','one'],['b','two']]),('start(k)end',[['k','middle']]),('(a)x(a)',[['a','q']])]],EVALUATE,[EVALUATE.replace("known.get(s[index+1:end],'?')","known.get(s[index+1:end],'')"),EVALUATE.replace('index=end+1','index=end')],['Deletes unknown keys instead of replacing them with a question mark.','Reprocesses the closing bracket as literal output.'],evaluate_o,revaluate,H('A dictionary gives constant-time lookup for each bracketed key.','Scan the string; copy ordinary characters and jump from an opening bracket to its closing bracket.','Append dictionary.get(key,"?") for every pair.','Non-nesting guarantees each jump captures one complete key, and every input position is copied or replaced exactly once.'),'O(len(s)+knowledge)','O(knowledge+output)',5),
1808:E('maximum_nice_divisors',[('prime_factors','int')],'int',['math','number-theory','recursion'],['Use at most prime_factors prime factors, counted with multiplicity.','Return the maximum number of nice divisors modulo 1,000,000,007.'],[([5],'Splitting the exponent budget into three and two gives 3*2=6 nice divisors.'),([8],'The optimal split 3+3+2 gives 18.')],[[n] for n in [1,2,3,4,5,6,7,8,9,10,11,12,20,50]],DIVISORS,[DIVISORS.replace('remainder==1','remainder==2'),DIVISORS.replace('quotient-1','quotient')],['Applies the four-times correction to remainder two instead of remainder one.','Uses an extra factor of three for remainder one.'],divisors_o,rdivisors,H('The divisor count becomes a product of exponent choices whose sum uses the factor budget.','Parts of three maximize product; avoid a leftover one by replacing 3+1 with 2+2.','Use modular exponentiation for the threes and multiply by two or four for the remainder.','Any part at least five improves when split into three and the remainder, while 2+2 beats 3+1; this leaves only optimal twos and threes.'),'O(log prime_factors)','O(1)',8),
}
BATCH[1806]['wrong'][0]=PERMUTATION.replace('return steps','return steps+1')
BATCH[1806]['wrong_reasons'][0]='Adds an extra operation after the permutation has already returned.'
BATCH[1806]['wrong'][1]=PERMUTATION.replace('return steps','return max(0,steps-1)')
BATCH[1806]['wrong_reasons'][1]='Stops one operation before the permutation actually returns.'
