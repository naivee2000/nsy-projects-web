"""Final reviewed group of workbook batch 117."""
from collections import Counter
from itertools import combinations
import heapq
from .import_batch_055 import entry

def palindrome_base(value,base):
 digits=[]
 while value:digits.append(value%base);value//=base
 return digits==digits[::-1]
def mirror_o(a):
 base,count=a;found=[];value=1
 while len(found)<count:
  if str(value)==str(value)[::-1] and palindrome_base(value,base):found.append(value)
  value+=1
 return sum(found)
def same_o(a):return sum(1 for i in range(len(a[0])) for j in range(i,len(a[0])) if a[0][i]==a[0][j])
def common_o(a):
 x,y=map(Counter,a);return sum(x[word]==y[word]==1 for word in x)
def buckets_o(a):
 street=a[0];empty=[i for i,c in enumerate(street) if c=='.']
 for size in range(len(empty)+1):
  for chosen in combinations(empty,size):
   if all(c!='H' or i-1 in chosen or i+1 in chosen for i,c in enumerate(street)):return size
 return -1
def home_o(a):
 start,home,rows,cols=a;m,n=len(rows),len(cols);pq=[(0,*start)];best={tuple(start):0}
 while pq:
  cost,r,c=heapq.heappop(pq)
  if [r,c]==home:return cost
  if cost!=best[(r,c)]:continue
  for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
   if 0<=nr<m and 0<=nc<n:
    nxt=cost+(rows[nr] if nr!=r else cols[nc])
    if nxt<best.get((nr,nc),10**9):best[(nr,nc)]=nxt;heapq.heappush(pq,(nxt,nr,nc))
def rmirror(r):return [r.randint(2,9),r.randint(1,6)]
def rsame(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,30)))]
def rcommon(r):return [[r.choice(['a','b','c','d']) for _ in range(r.randint(1,10))],[r.choice(['a','b','c','d']) for _ in range(r.randint(1,10))]]
def rbuckets(r):return [''.join(r.choice('H.') for _ in range(r.randint(1,10)))]
def rhome(r):
 m,n=r.randint(1,5),r.randint(1,5);return [[r.randrange(m),r.randrange(n)],[r.randrange(m),r.randrange(n)],[r.randint(1,9) for _ in range(m)],[r.randint(1,9) for _ in range(n)]]

MIRROR='''\
def sum_k_mirror_numbers(k,n):
    def base_palindrome(value):
        digits=[]
        while value:digits.append(value%k);value//=k
        return digits==digits[::-1]
    answer=0;length=1
    while n:
        low=10**((length-1)//2);high=10**((length+1)//2)
        for half in range(low,high):
            value=half;rest=half if length%2==0 else half//10
            while rest:value=value*10+rest%10;rest//=10
            if base_palindrome(value):
                answer+=value;n-=1
                if n==0:return answer
        length+=1
'''
SAME='''\
def same_end_substring_count(s):
    counts={};answer=0
    for char in s:
        counts[char]=counts.get(char,0)+1;answer+=counts[char]
    return answer
'''
COMMON='''\
def once_in_both(words1,words2):
    from collections import Counter
    first=Counter(words1);second=Counter(words2)
    return sum(count==1 and second[word]==1 for word,count in first.items())
'''
BUCKETS='''\
def minimum_hamster_buckets(street):
    street=list(street);answer=0
    for index,char in enumerate(street):
        if char!='H':continue
        if index>0 and street[index-1]=='B':continue
        if index+1<len(street) and street[index+1]=='.':street[index+1]='B';answer+=1
        elif index>0 and street[index-1]=='.':street[index-1]='B';answer+=1
        else:return -1
    return answer
'''
HOME='''\
def minimum_homecoming_cost(start_pos,home_pos,row_costs,col_costs):
    row,column=start_pos;target_row,target_column=home_pos;answer=0
    step=1 if row<target_row else -1
    while row!=target_row:row+=step;answer+=row_costs[row]
    step=1 if column<target_column else -1
    while column!=target_column:column+=step;answer+=col_costs[column]
    return answer
'''
def L(*x):return list(x)
BATCH={
2081:entry('sum_k_mirror_numbers',[('k','int'),('n','int')],'int',['math','enumeration','palindromes'],['k is from two through nine and n is positive.','A k-mirror number is positive and palindromic in both decimal and base k without leading zeros.','Return the sum of the n smallest such numbers.'],[([2,5],'The first five binary-and-decimal palindromes are 1,3,5,7,9, summing to 25.'),([3,7],'The first seven base-three mirror numbers sum to 499.')],[[k,n] for k,n in [(2,1),(2,2),(2,3),(2,4),(2,6),(3,1),(3,2),(3,5),(4,4),(5,5),(6,3),(7,4),(8,2),(9,6)]],MIRROR,[MIRROR.replace('digits==digits[::-1]','digits==sorted(digits)'),MIRROR.replace('low=10**((length-1)//2)','low=0 if length==1 else 10**((length-1)//2)')],['Tests whether base-k digits are sorted rather than palindromic.','Generates decimal values with leading-zero halves and duplicates shorter palindromes.'],mirror_o,rmirror,L('Generate decimal palindromes directly; testing every integer wastes most candidates.','For each decimal length, mirror a half-number, then test its base-k digits with two-ended equality.','Mirror all halves for increasing lengths; add qualifying values until n reaches zero.','Generation order is increasing and exhaustive for decimal palindromes, while the digit test is equivalent to base-k palindromicity.'),'O(answer candidates*log_k value)','O(log value)',8),
2083:entry('same_end_substring_count',[('s','str')],'int',['strings','counting','combinatorics'],['s is a nonempty lowercase string.','Count contiguous substrings whose first and last characters are equal.','Return the total including every one-character substring.'],[(['abcba'],'Five singletons plus abcba and bcb give seven.'),(['abacad'],'The three a occurrences create six a-ended substrings; the other letters add three.')],[[s] for s in ['a','aa','ab','aba','abc','aaaa','abab','abba','xyzzy','leetcode','mississippi','abcabc','zzzza','qwertyq']],SAME,[SAME.replace('answer+=counts[char]','answer+=counts[char]-1'),SAME.replace('counts.get(char,0)+1','counts.get(char,1)+1')],['Omits each new one-character substring.','Initializes unseen letters at one and overcounts their first occurrence.'],same_o,rsame,L('When a substring ends at the current character, its start must be an earlier or current occurrence of that character.','Track how many times each character has appeared including the current position.','Increment the character count, then add that count to the answer.','This adds every valid substring exactly at its unique right endpoint.'),'O(n)','O(1)',5),
2085:entry('once_in_both',[('words1','list[str]'),('words2','list[str]')],'int',['hash maps','strings','counting'],['Both word arrays are nonempty.','Count distinct words occurring exactly once in each array.','Repeated words in either array do not qualify.'],[([['leetcode','is','amazing','as','is'],['amazing','leetcode','is']],'leetcode and amazing each occur once in both arrays.'),([['b','bb','bbb'],['a','aa','aaa']],'The arrays share no word, so the count is zero.')],[[x,y] for x,y in [(['a'],['a']),(['a'],['b']),(['a','a'],['a']),(['a'],['a','a']),(['a','b'],['a','b']),(['a','b','b'],['a','b']),(['x','y'],['y','z']),(['same','same'],['same','same']),(['one','two','three'],['three','two','one']),(['a','b','c'],['a','a','b']),(['cat','dog'],['cat','bird']),(['z'],['z','x']),(['p','q','p'],['q']),(['red','blue'],['blue','blue'])]],COMMON,[COMMON.replace('count==1','count>=1'),COMMON.replace('second[word]==1','second[word]>=1')],['Allows words repeated in the first array.','Allows words repeated in the second array.'],common_o,rcommon,L('Exact multiplicity in both arrays requires two independent frequency maps.','Count each array, then inspect words from one map.','Add one only when first[word]==1 and second[word]==1.','Every common candidate is visited once, and the two equality checks encode the definition exactly.'),'O(total words)','O(distinct words)',3),
2086:entry('minimum_hamster_buckets',[('street','str')],'int',['strings','greedy'],['street contains only H for hamster and . for an available bucket position.','Every hamster needs a bucket in an immediately adjacent empty position; one bucket may feed two hamsters.','Return the minimum bucket count or -1 when impossible.'],[(['H..H'],'Buckets in the two middle-adjacent positions feed both endpoint hamsters, requiring two.'),(['.H.H.'],'One bucket placed between the two hamsters feeds both.')],[[s] for s in ['H','.','HH','H.','.H','H.H','H..H','..H..','HH.','.HH','H.H.H','...','H...H','.H..H.','HHHH']],BUCKETS,[BUCKETS.replace("street[index-1]=='B'","street[index-1]=='.'"),BUCKETS.replace("index+1<len(street)","index+2<len(street)")],['Mistakes any empty left position for an already placed bucket and undercounts.','Requires two positions to the right and misses a usable final empty position.'],buckets_o,rbuckets,L('Placing to the right is best because it may also feed the next hamster.','Scan left to right: if no bucket already sits left, place one right when possible, otherwise left, or fail.','Mark placed buckets in a mutable character list so later hamsters can reuse them.','The greedy right placement never harms an earlier hamster and weakly improves options for the future, establishing minimality by exchange.'),'O(n)','O(n)',5),
2087:entry('minimum_homecoming_cost',[('start_pos','list[int]'),('home_pos','list[int]'),('row_costs','list[int]'),('col_costs','list[int]')],'int',['grids','greedy'],['Positions are valid cells; entering row r vertically costs row_costs[r], and entering column c horizontally costs col_costs[c].','All costs are positive, so an optimal route never moves away from the target row or column.','Return the minimum cost from start to home.'],[([[1,0],[2,3],[5,4,3],[8,2,6,7]],'Enter row two for cost three, then columns one through three for 2+6+7, totaling eighteen.'),([[0,0],[0,0],[5],[7]],'The robot is already home, so no cell-entry cost is paid.')],[[s,h,r,c] for s,h,r,c in [([0,0],[1,1],[1,2],[3,4]),([1,1],[0,0],[5,2],[7,3]),([0,1],[2,1],[1,2,3],[4,5]),([2,1],[0,1],[1,2,3],[4,5]),([1,0],[1,2],[5,6,7],[1,2,3]),([1,2],[1,0],[5,6,7],[1,2,3]),([0,0],[2,2],[9,1,9],[8,1,8]),([2,2],[0,0],[9,1,9],[8,1,8]),([0,0],[0,1],[1],[2,3]),([0,1],[0,0],[1],[2,3]),([1,1],[2,0],[4,5,6],[7,8]),([2,0],[1,1],[4,5,6],[7,8]),([0,2],[2,0],[1,4,2],[5,3,7]),([2,0],[0,2],[1,4,2],[5,3,7])]],HOME,[HOME.replace('answer+=row_costs[row]','answer+=row_costs[row-step]'),HOME.replace('answer+=col_costs[column]','answer+=col_costs[column-step]')],['Charges the row being left instead of the row being entered.','Charges the column being left instead of the column being entered.'],home_o,rhome,L('Positive costs mean detours only add entries and cannot reduce the necessary row and column crossings.','Walk monotonically from the start row to target row, then similarly for columns, charging each entered coordinate.','Choose step as +1 or -1; update coordinate first, then add its row or column cost.','Every route must enter each intervening coordinate at least once, and this monotone route enters each exactly once.'),'O(row distance+column distance)','O(1)',5)
}

BATCH[2086]['params'][0]=('hamsters','str','raw')
