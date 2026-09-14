"""Second slice of batch 102: optimal games, formatting, and unique windows."""
from functools import lru_cache
from .import_batch_055 import entry
def game_six_o(a):
 alice,bob=a;n=len(alice)
 @lru_cache(None)
 def play(mask,turn):
  if mask==(1<<n)-1:return 0
  values=[]
  for i in range(n):
   if not mask>>i&1:values.append((alice[i] if turn==0 else -bob[i])+play(mask|1<<i,1-turn))
  return (max if turn==0 else min)(values)
 difference=play(0,0);return (difference>0)-(difference<0)
def deci_o(a):return max(map(int,a[0]))
def game_seven_o(a):
 stones=a[0];prefix=[0]
 for x in stones:prefix.append(prefix[-1]+x)
 @lru_cache(None)
 def solve(left,right):
  if left==right:return 0
  remove_left=prefix[right+1]-prefix[left+1]-solve(left+1,right)
  remove_right=prefix[right]-prefix[left]-solve(left,right-1)
  return max(remove_left,remove_right)
 return solve(0,len(stones)-1)
def phone_o(a):
 digits=''.join(c for c in a[0] if c.isdigit());groups=[]
 while len(digits)>4:groups.append(digits[:3]);digits=digits[3:]
 if len(digits)==4:groups.extend((digits[:2],digits[2:]))
 else:groups.append(digits)
 return '-'.join(groups)
def erasure_o(a):
 nums=a[0];best=0
 for left in range(len(nums)):
  seen=set();total=0
  for value in nums[left:]:
   if value in seen:break
   seen.add(value);total+=value;best=max(best,total)
 return best
def rgame6(r):
 n=r.randint(1,8);return [[r.randint(1,20) for _ in range(n)],[r.randint(1,20) for _ in range(n)]]
def rdeci(r):return [''.join(r.choice('0123456789') for _ in range(r.randint(1,30))).lstrip('0') or '1']
def rgame7(r):return [[r.randint(1,20) for _ in range(r.randint(2,10))]]
def rphone(r):
 digits=''.join(r.choice('0123456789') for _ in range(r.randint(2,30)));result=''
 for char in digits:result+=char+r.choice(('','',' ','-'))
 return [result.rstrip(' -')]
def rerasure(r):return [[r.randint(1,20) for _ in range(r.randint(1,30))]]
GAME6='''def stone_game_six_result(alice_values, bob_values):
 order=sorted(range(len(alice_values)),key=lambda i:alice_values[i]+bob_values[i],reverse=True);alice=bob=0
 for turn,index in enumerate(order):
  if turn%2==0:alice+=alice_values[index]
  else:bob+=bob_values[index]
 return (alice>bob)-(alice<bob)
'''
DECI='''def minimum_decibinary_parts(n):
 return max(int(digit) for digit in n)
'''
GAME7='''def stone_game_seven_difference(stones):
 n=len(stones);prefix=[0]
 for value in stones:prefix.append(prefix[-1]+value)
 dp=[[0]*n for _ in range(n)]
 for width in range(2,n+1):
  for left in range(n-width+1):
   right=left+width-1
   dp[left][right]=max(prefix[right+1]-prefix[left+1]-dp[left+1][right],prefix[right]-prefix[left]-dp[left][right-1])
 return dp[0][-1]
'''
PHONE='''def reformat_phone_number(number):
 digits=''.join(char for char in number if char.isdigit());groups=[]
 while len(digits)>4:groups.append(digits[:3]);digits=digits[3:]
 if len(digits)==4:groups.extend((digits[:2],digits[2:]))
 else:groups.append(digits)
 return '-'.join(groups)
'''
ERASURE='''def maximum_unique_subarray_sum(nums):
 seen=set();left=total=answer=0
 for value in nums:
  while value in seen:seen.remove(nums[left]);total-=nums[left];left+=1
  seen.add(value);total+=value;answer=max(answer,total)
 return answer
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1686:E('stone_game_six_result',[('alice_values','list[int]'),('bob_values','list[int]')],'int',['greedy','game-theory'],['Equal-length positive value arrays.','Players alternate choosing an unused stone and add only their own value; both play optimally. Return 1, 0, or -1 for Alice, tie, or Bob.'],[([[1,3],[2,1]],'Choosing the stone with total value four first lets Alice win.'),([[1,2],[3,1]],'Optimal play produces a draw.')],[[*x] for x in [([1,3],[2,1]),([1,2],[3,1]),([2,4,3],[1,6,7]),([1],[1]),([2],[1]),([1],[2]),([5,5],[5,5]),([10,1],[1,10]),([1,2,3],[3,2,1]),([7,4,2],[3,8,5]),([1,10,2,9],[8,1,7,2]),([3,3,3],[1,2,3]),([9,1,1],[1,9,9]),([2,8,4,6],[7,1,5,3])]],GAME6,[GAME6.replace('reverse=True','reverse=False'),GAME6.replace('alice_values[i]+bob_values[i]','alice_values[i]')],['Chooses stones with smallest combined strategic value first.','Ranks only Alice’s value and ignores how much a choice denies Bob.'],game_six_o,rgame6,L('Taking a stone gains your value and denies the opponent theirs, so its combined value determines urgency.','Sort stones by Alice value plus Bob value descending and alternate selections.','Accumulate each player’s own value on their turns, then compare scores.','If two adjacent choices are inverted by combined value, swapping them cannot hurt the player choosing first, giving the greedy order.'),'O(n log n)','O(n)',5),
1689:E('minimum_decibinary_parts',[('n','str')],'int',['greedy','strings'],['n is a positive decimal string.','A deci-binary summand uses only digits zero and one; return the fewest positive summands whose decimal sum is n.'],[(['32'],'At least three summands are needed for digit three, and three suffice.'),(['82734'],'The digit eight forces eight summands.')],[[s] for s in ['1','9','10','32','82734','27346209830709182346','1000','1111','909','55555','12034','700000','123456789','20002']],DECI,[DECI.replace('max(int(digit)','min(int(digit)'),DECI.replace('for digit in n','for digit in n if digit!="9"')],['Uses the smallest digit rather than the largest required column count.','Ignores digit nine, undercounting inputs whose maximum is nine.'],deci_o,rdeci,L('Each summand contributes at most one in any digit column.','The largest decimal digit is both a lower bound and achievable count.','Return max digit. Constructively, place a one in the first d summands for a column containing d.','The construction represents every column without carries using exactly the maximum digit number of summands.'),'O(digits)','O(1)',5),
1690:E('stone_game_seven_difference',[('stones','list[int]')],'int',['dynamic-programming','game-theory'],['At least two positive stones.','Removing an endpoint scores the sum left behind; both players optimize final score difference.'],[([[5,3,1,4,2]],'Optimal endpoint choices give Alice a final advantage of six.'),([[7,90,5,1,100,10,10,2]],'Optimal play gives a difference of one hundred twenty-two.')],[[s] for s in [[5,3,1,4,2],[7,90,5,1,100,10,10,2],[1,2],[1,1],[1,2,3],[3,2,1],[5,5,5],[1,10,1],[2,4,6,8],[8,6,4,2],[1,2,10,2,1],[9,1,8,2],[3,7,2,9,4],[20,1,1,20]]],GAME7,[GAME7.replace('max(prefix','min(prefix',1),GAME7.replace('-dp[left+1][right]','+dp[left+1][right]')],['Minimizes the current player’s advantage instead of maximizing it.','Adds the opponent’s future advantage rather than subtracting it.'],game_seven_o,rgame7,L('A state is the best score difference the current player can force on one interval.','Try removing either endpoint: gain the remaining sum, then subtract the opponent’s optimal difference.','Fill interval DP from width two upward and take the maximum of the two endpoint transitions.','The recurrence enumerates both legal moves and zero-sum turn exchange changes the next state’s advantage sign.'),'O(n²)','O(n²)',5),
1694:E('reformat_phone_number',[('number','str')],'str',['strings','simulation'],['Input contains digits, spaces, and dashes and has at least two digits.','Remove separators; emit groups of three, except a final four digits become two groups of two.'],[(['1-23-45 6'],'Digits 123456 split into two groups of three: 123-456.'),(['123 4-567'],'The final four digits split into 12 and 34 after the first group, producing 123-45-67.')],[[s] for s in ['1-23-45 6','123 4-567','123 4-5678','12','123','1234','12345','123456','1234567','1 2 3 4 5 6 7 8','12-34','123-45','9-87 65-43','10 20 30']],PHONE,[PHONE.replace('len(digits)>4','len(digits)>=4'),PHONE.replace("groups.extend((digits[:2],digits[2:]))","groups.append(digits)")],['Takes a three-digit block when exactly four remain, leaving a forbidden one-digit block.','Leaves the final four digits in one oversized block.'],phone_o,rphone,L('Only the count of cleaned remaining digits determines the next block size.','Take groups of three while more than four remain; split exactly four as two plus two.','Strip non-digits, consume leading triples, handle the final two, three, or four digits, and join with dashes.','The stopping rule prevents a one-digit final block and all produced groups satisfy the required sizes.'),'O(n)','O(n)',3),
1695:E('maximum_unique_subarray_sum',[('nums','list[int]')],'int',['sliding-windows','hash-maps'],['Nonempty positive integer array.','Choose one contiguous subarray with all distinct values and maximize its sum.'],[([[4,2,4,5,6]],'After discarding the first four at the repeat, window 2,4,5,6 has sum seventeen.'),([[5,2,1,2,5,2,1,2,5]],'The best distinct window has sum eight.')],[[x] for x in [[4,2,4,5,6],[5,2,1,2,5,2,1,2,5],[1],[1,2],[1,1],[1,2,3],[3,2,1],[1,2,1,3],[10,1,2,10,20],[5,5,5],[1,2,3,4,1],[9,1,9,2,8],[2,4,6,2,8],[100,1,2,3,100]]],ERASURE,[ERASURE.replace('while value in seen','if value in seen'),ERASURE.replace('total-=nums[left]','total=0')],['Removes only one left value when a duplicate may remain deeper in the window.','Resets the entire sum while retaining later unique values in the set.'],erasure_o,rerasure,L('Positive values mean the best window ending at each index starts immediately after the previous duplicate.','Maintain a unique-value window, its sum, and a left pointer.','While the new value is present, remove left values and their sum; then add it and maximize.','The loop restores uniqueness with the earliest possible left boundary, which maximizes the positive sum for that right endpoint.'),'O(n)','O(n)',5),
}
