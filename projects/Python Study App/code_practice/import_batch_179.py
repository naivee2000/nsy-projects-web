"""Block strings, idle servers, digit pairs, integer reduction, and good splits batch 179."""
from functools import lru_cache
from math import gcd
from .import_batch_055 import entry

def blocks_oracle(a):
 @lru_cache(None)
 def f(x,y,z,suffix):
  best=0
  for word,count,state in [('AA',x,0),('BB',y,1),('AB',z,2)]:
   if count and 'AAA' not in suffix+word and 'BBB' not in suffix+word:
    values=[x,y,z];values[state]-=1;best=max(best,2+f(*values,(suffix+word)[-2:]))
  return best
 return f(*a,'')
def random_blocks(r):return [r.randint(0,6),r.randint(0,6),r.randint(0,6)]
def servers_oracle(a):
 n,logs,x,queries=a;return [sum(not any(server==i and q-x<=time<=q for server,time in logs) for i in range(1,n+1)) for q in queries]
def random_servers(r):
 n=r.randint(1,8);return [n,[[r.randint(1,n),r.randint(1,30)] for _ in range(r.randint(0,25))],r.randint(0,10),[r.randint(1,35) for _ in range(r.randint(1,10))]]
def beautiful_oracle(a):
 nums=a[0];return sum(gcd(int(str(nums[i])[0]),nums[j]%10)==1 for i in range(len(nums)) for j in range(i+1,len(nums)))
def random_beautiful(r):return [[r.randint(1,9999) for _ in range(r.randint(2,30))]]
def zero_oracle(a):
 num1,num2=a;reachable={0}
 for operations in range(1,13):
  reachable={value+(1<<power) for value in reachable for power in range(8)}
  if num1-operations*num2 in reachable:return operations
 return -1
def random_zero(r):return [r.randint(1,50),r.randint(0,5)]
def split_oracle(a):
 nums=a[0];n=len(nums);return sum(all(sum(nums[start:end])==1 for start,end in zip([0]+[i+1 for i in range(n-1) if mask>>i&1],[i+1 for i in range(n-1) if mask>>i&1]+[n])) for mask in range(1<<(n-1)))%1_000_000_007
def random_split(r):return [[r.randrange(2) for _ in range(r.randint(1,12))]]

BLOCKS='''\
def longest_valid_block_string(x,y,z):
    return 2*(2*min(x,y)+(1 if x!=y else 0)+z)
'''
SERVERS='''\
def count_idle_servers(n,logs,x,queries):
    ordered=sorted(logs,key=lambda item:item[1]);active={};answer=[];left=right=0
    for query,index in sorted((q,i) for i,q in enumerate(queries)):
        while right<len(ordered) and ordered[right][1]<=query:
            server=ordered[right][0];active[server]=active.get(server,0)+1;right+=1
        while left<right and ordered[left][1]<query-x:
            server=ordered[left][0];active[server]-=1
            if active[server]==0:del active[server]
            left+=1
        answer.append((index,n-len(active)))
    return [value for _,value in sorted(answer)]
'''
BEAUTIFUL='''\
def count_beautiful_digit_pairs(nums):
    from math import gcd
    first_counts=[0]*10;answer=0
    for value in nums:
        last=value%10;answer+=sum(first_counts[digit] for digit in range(1,10) if gcd(digit,last)==1)
        first_counts[int(str(value)[0])]+=1
    return answer
'''
ZERO='''\
def minimum_integer_zero_operations(num1,num2):
    for operations in range(1,61):
        remaining=num1-operations*num2
        if remaining<operations:continue
        if remaining.bit_count()<=operations:return operations
    return -1
'''
SPLIT='''\
def count_good_binary_splits(nums):
    MOD=1_000_000_007;ones=[i for i,value in enumerate(nums) if value==1]
    if not ones:return 0
    answer=1
    for left,right in zip(ones,ones[1:]):answer=answer*(right-left)%MOD
    return answer
'''

BATCH={
2745:entry('longest_valid_block_string',[('x','int'),('y','int'),('z','int')],'int',['strings','greedy'],['You have x copies of AA, y copies of BB, and z copies of AB.','Concatenate any chosen blocks without creating AAA or BBB.','Return the maximum resulting length.'],[([2,5,1],'Use both AA blocks, three BB blocks, and the AB block for six blocks or length twelve.'),([3,3,0],'Alternate all six AA and BB blocks for length twelve.')],[[x,y,z] for x,y,z in [(0,0,1),(1,0,0),(0,1,0),(1,1,0),(2,5,1),(3,3,0),(0,0,5),(4,1,2),(1,4,2),(2,2,3),(6,0,1),(0,6,1),(5,4,0),(3,1,5)]],BLOCKS,[BLOCKS.replace('min(x,y)','max(x,y)'),BLOCKS.replace('+z)',')')],['Uses all excess AA or BB blocks even though triples would form.','Ignores every available AB block.'],blocks_oracle,random_blocks,['AA and BB blocks must alternate, so their used counts differ by at most one.','Use all pairs of AA and BB, one extra of the more numerous type, and every AB block.','Count blocks as 2*min(x,y)+(x!=y)+z, then multiply by two characters.','Alternation realizes the balanced blocks, and AB can be inserted without increasing either forbidden run.'],'O(1)','O(1)',5),
2747:entry('count_idle_servers',[('n','int'),('logs','list[list[int]]'),('x','int'),('queries','list[int]')],'list[int]',['arrays','sorting','sliding window'],['Servers are numbered 1 through n; log [server,time] records a request.','For each query q, its active window is the inclusive interval [q-x,q].','Return how many servers have no request in each query window, preserving query order.'],[([3,[[1,3],[2,6],[1,5]],5,[10,11]],'At time ten only server one is active; at eleven only server two is active, giving one and two idle servers.'),([2,[[1,1]],0,[1,2]],'With a zero-width window server one is active only for query one.')],[[n,l,x,q] for n,l,x,q in [(1,[],5,[10]),(1,[[1,5]],0,[5]),(2,[[1,1]],0,[1,2]),(3,[[1,3],[2,6],[1,5]],5,[10,11]),(3,[[1,1],[2,2],[3,3]],2,[3]),(4,[[1,5],[1,6]],3,[4,6,9]),(2,[[1,10],[2,1]],5,[6,10]),(5,[],0,[1,2]),(3,[[1,2],[1,2],[2,2]],0,[2]),(3,[[3,7]],10,[5,7]),(4,[[1,1],[2,10]],20,[10]),(2,[[1,5],[2,5]],1,[4,5]),(3,[[1,8],[2,9]],1,[9,8]),(6,[[6,20]],5,[20,26])]],SERVERS,[SERVERS.replace('<query-x','<=query-x'),SERVERS.replace('n-len(active)','len(active)')],['Treats the inclusive left endpoint as expired.','Returns active-server counts rather than idle-server counts.'],servers_oracle,random_servers,['Sort logs and queries by time.','Maintain counts per server for logs in the current inclusive window.','Advance the right pointer through time q and remove logs strictly before q-x; answer n minus active keys.','The two pointers maintain exactly the query interval, while per-server counts handle multiple logs without double counting.'],'O((logs+queries) log(logs+queries))','O(logs+n)',8),
2748:entry('count_beautiful_digit_pairs',[('nums','list[int]')],'int',['arrays','math','counting'],['For every index pair i<j, take the first decimal digit of nums[i] and last digit of nums[j].','The pair is beautiful when those digits have greatest common divisor one.','Return the number of beautiful pairs.'],[([[2,5,1,4]],'All six index pairs except the pair with digits two and four are coprime, giving five.'),([[11,21,12]],'The three digit pairs are (1,1), (1,2), and (2,2); two are coprime.')],[[x] for x in [[1,1],[2,4],[2,5,1,4],[11,21,12],[10,20],[99,11],[12,34,56],[7,14,28],[123,456,789],[5,10,15,20],[8,3,6,9],[100,101,102],[17,22,35,48],[91,82,73,64,55]]],BEAUTIFUL,[BEAUTIFUL.replace('last=value%10',"last=int(str(value)[0])"),BEAUTIFUL.replace('==1','>1')],['Uses the second number’s first digit instead of its last digit.','Counts non-coprime pairs rather than coprime pairs.'],beautiful_oracle,random_beautiful,['Only nine possible first digits need counts.','Scan left to right; before storing the current first digit, compare its last digit with earlier first-digit counts.','Add counts for digits whose gcd with the current last digit is one.','At index j the table represents exactly all eligible earlier i values, so every ordered index pair is tested once.'],'O(9n)','O(1)',3),
2749:entry('minimum_integer_zero_operations',[('num1','int'),('num2','int')],'int',['math','bit manipulation','enumeration'],['One operation chooses any nonnegative i and subtracts 2^i+num2 from num1.','Return the minimum operations needed to make num1 zero, or -1 when impossible.','The chosen exponent may differ between operations.'],[([3,-2],'Three operations choosing powers that sum to nine subtract 9-6=3 in total.'),([5,7],'Every operation subtracts more than the remaining positive target, so reaching zero is impossible.')],[[a,b] for a,b in [(1,0),(2,0),(3,-2),(5,7),(10,1),(10,2),(7,0),(8,0),(9,0),(20,3),(30,4),(15,1),(6,5),(50,2)]],ZERO,[ZERO.replace('remaining<operations','remaining<=operations'),ZERO.replace('.bit_count()<=operations','.bit_count()==operations')],['Rejects a valid representation whose remaining sum equals the number of one-valued powers.','Requires exactly one set bit per operation and ignores splitting a power into smaller powers.'],zero_oracle,random_zero,['After k operations, the selected powers must sum to num1-k*num2.','A positive integer can be written as k powers of two exactly when bit_count(value)<=k<=value.','Test k from one through sixty and return the first satisfying both bounds.','Set bits give the minimum terms; repeatedly splitting a power doubles one term into two and reaches every count up to the all-ones maximum.'],'O(60)','O(1)',8),
2750:entry('count_good_binary_splits',[('nums','list[int]')],'int',['arrays','combinatorics'],['Split the binary array into contiguous nonempty subarrays.','A split is good when every part contains exactly one value equal to one.','Return the number of good splits modulo 1,000,000,007.'],[([[0,1,0,0,1]],'The cut between the two ones has three possible positions, giving three splits.'),([[0,0]],'No part can contain exactly one one, so the answer is zero.')],[[x] for x in [[0],[1],[0,0],[1,1],[0,1,0,0,1],[1,0,1],[1,0,0,1],[0,1,0],[1,0,0],[0,0,1],[1,1,1],[0,1,0,1,0,1,0],[1,0,1,0,0,1],[0,0,1,0,0,0,1]]],SPLIT,[SPLIT.replace('right-left','right-left-1'),SPLIT.replace('if not ones:return 0','if not ones:return 1')],['Counts only zeros between consecutive ones instead of all valid cut positions.','Treats an all-zero array as one valid split.'],split_oracle,random_split,['Every part must correspond to exactly one occurrence of one.','Between consecutive ones, choose any one cut position.','Multiply their index distances; return zero when no one exists.','Choices between different consecutive ones are independent, and the distance equals the number of legal cut locations.'],'O(n)','O(n)',5),
}
