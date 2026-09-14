"""Final five problems of batch 101."""
from itertools import combinations,permutations
from .import_batch_055 import entry
def energy_o(a):
 tasks=a[0];best=10**9
 for order in permutations(tasks):
  spent=required=0
  for actual,minimum in order:required=max(required,spent+minimum);spent+=actual
  best=min(best,required)
 return best
def repeat_o(a):
 sequence,word=a;k=0
 while word*(k+1) in sequence:k+=1
 return k
def wealth_o(a):return max(map(sum,a[0]))
def competitive_o(a):return list(min(combinations(a[0],a[1])))
def parser_o(a):return a[0].replace('()','o').replace('(al)','al')
def renergy(r):
 tasks=[]
 for _ in range(r.randint(1,7)):
  actual=r.randint(1,10);tasks.append([actual,r.randint(actual,actual+15)])
 return [tasks]
def rrepeat(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,25))),''.join(r.choice('abc') for _ in range(r.randint(1,5)))]
def rwealth(r):return [[[r.randint(0,50) for _ in range(r.randint(1,8))] for _ in range(r.randint(1,8))]]
def rcompetitive(r):
 nums=[r.randint(-20,20) for _ in range(r.randint(1,12))];return [nums,r.randint(1,len(nums))]
def rparser(r):return [''.join(r.choice(('G','()','(al)')) for _ in range(r.randint(1,20)))]
ENERGY='''def minimum_initial_task_energy(tasks):
 spent=required=0
 for actual,minimum in sorted(tasks,key=lambda task:task[1]-task[0],reverse=True):
  required=max(required,spent+minimum);spent+=actual
 return required
'''
REPEAT='''def maximum_repeating_word(sequence, word):
 repeated=word;answer=0
 while repeated in sequence:answer+=1;repeated+=word
 return answer
'''
WEALTH='''def richest_customer_wealth(accounts):
 return max(sum(customer) for customer in accounts)
'''
COMPETE='''def most_competitive_subsequence(nums, k):
 stack=[]
 for index,value in enumerate(nums):
  while stack and stack[-1]>value and len(stack)-1+len(nums)-index>=k:stack.pop()
  if len(stack)<k:stack.append(value)
 return stack
'''
PARSER='''def interpret_goal_command(command):
 return command.replace('()','o').replace('(al)','al')
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1665:E('minimum_initial_task_energy',[('tasks','list[list[int]]')],'int',['greedy','sorting'],['1–100,000 tasks; each [actual,minimum] has 1 <= actual <= minimum.','Choose any order and return the least starting energy that permits every task.'],[([[[1,2],[2,4],[4,8]]],'Starting with eight permits the high-slack task first and all remaining work.'),([[[1,3],[2,4],[10,11],[10,12],[8,9]]],'Ordering by required energy margin minimizes the start at thirty-two.')],[[t] for t in [[[1,2],[2,4],[4,8]],[[1,3],[2,4],[10,11],[10,12],[8,9]],[[1,1]],[[1,2],[1,2]],[[5,5],[1,10]],[[2,3],[3,3]],[[4,8],[2,2]],[[1,100],[99,100]],[[3,5],[2,9],[1,2]],[[10,20],[5,5],[2,8]],[[2,4],[4,6],[6,8]],[[7,7],[3,20]],[[1,5],[2,5],[3,5]],[[9,10],[1,100],[50,50]]]],ENERGY,[ENERGY.replace('reverse=True','reverse=False'),ENERGY.replace('spent+minimum','minimum')],['Runs low-margin tasks first, which can require more initial energy.','Ignores energy already spent when checking later task requirements.'],energy_o,renergy,L('A task’s minimum-minus-cost margin measures how costly it is to postpone.','Process larger margins first and track total energy already spent.','Sort by minimum-actual descending; required is max(required,spent+minimum), then add actual to spent.','Swapping an inverted adjacent pair never increases the required start, establishing the sorted order by exchange argument.'),'O(n log n)','O(n)',8),
1668:E('maximum_repeating_word',[('sequence','str'),('word','str')],'int',['strings','simulation'],['Both inputs are nonempty lowercase strings.','Return the largest k for which k consecutive copies of word occur as a substring of sequence.'],[(['ababc','ab'],'The substring abab contains two consecutive copies of ab.'),(['ababc','ba'],'Ba occurs once, but baba does not occur.')],[[*x] for x in [('ababc','ab'),('ababc','ba'),('a','a'),('a','b'),('aaaaa','a'),('aaaaa','aa'),('abcabcabc','abc'),('abcabcab','abc'),('xyz','xy'),('abababa','aba'),('zzzz','zz'),('mississippi','issi'),('abc','abcd'),('aaaaabaaaa','aa')]],REPEAT,[REPEAT.replace('repeated+=word','repeated+=word+word'),REPEAT.replace('answer+=1','answer+=2')],['Skips every second candidate repetition length.','Counts each found repetition twice.'],repeat_o,rrepeat,L('Test increasingly long consecutive repetitions, since every valid k implies every smaller k.','Grow one candidate by appending word until it no longer occurs.','Start with word, increment the answer while candidate is a substring, and append one more word each round.','The first absent repetition ends a monotone sequence of valid k values, so the prior count is maximal.'),'O(k*|sequence|)','O(k*|word|)',3),
1672:E('richest_customer_wealth',[('accounts','list[list[int]]')],'int',['matrices','arrays'],['At least one customer and one account; balances are nonnegative.','Customer wealth is their row sum. Return the maximum row sum.'],[([[[1,2,3],[3,2,1]]],'Both customers total six, so the greatest wealth is six.'),([[[1,5],[7,3],[3,5]]],'The second customer totals ten, the maximum.')],[[a] for a in [[[1,2,3],[3,2,1]],[[1,5],[7,3],[3,5]],[[5]],[[0]],[[1],[2]],[[0,0],[0,0]],[[10,20,30]],[[1,1],[2,2],[3,3]],[[9,0],[4,4]],[[1,2,3],[10,0,0]],[[5,5,5],[4,4,7]],[[100,1],[50,60]],[[2,8],[3,7]],[[1,0,0],[0,1,0],[0,0,1]]]],WEALTH,[WEALTH.replace('max(sum(customer)','min(sum(customer)'),WEALTH.replace('sum(customer)','max(customer)')],['Returns the poorest customer’s wealth.','Uses only the largest single account in each row.'],wealth_o,rwealth,L('Each customer is independent, so first aggregate rows and then compare totals.','Compute every row sum and retain the largest.','Map sum across accounts and return max.','The definition of wealth is exactly a row sum, and max selects the richest among all customers.'),'O(rows*columns)','O(1)',3),
1673:E('most_competitive_subsequence',[('nums','list[int]'),('k','int')],'list[int]',['stacks','greedy'],['1 <= k <= len(nums) <= 100,000.','Return the lexicographically smallest length-k subsequence while preserving original order.'],[([[3,5,2,6],2],'Discarding three and five when two arrives leaves the smallest possible prefix 2,6.'),([[2,4,3,3,5,4,9,6],4],'The monotonic stack produces 2,3,3,4 as the smallest feasible sequence.')],[[*x] for x in [([3,5,2,6],2),([2,4,3,3,5,4,9,6],4),([1],1),([2,1],1),([1,2],2),([3,2,1],2),([1,1,1],2),([5,1,4,2,3],3),([9,8,7,6],2),([1,3,2,4],3),([4,2,3,1],2),([2,2,1,2],3),([-1,3,-2,4],2),([6,5,4,3,2,1],5)]],COMPETE,[COMPETE.replace('stack[-1]>value','stack[-1]>=value'),COMPETE.replace('>=k','>k')],['Pops equal values and may keep a later occurrence needed for feasibility.','Requires one extra future slot before popping, leaving an avoidably large prefix.'],competitive_o,rcompetitive,L('Remove a larger suffix value when the remaining input can still fill k positions.','Maintain the lexicographically smallest feasible monotonic stack prefix.','While top>current and popped length plus remaining count can reach k, pop; append while size<k.','The first differing position improves whenever a larger top is safely replaced, and the feasibility test prevents undersizing.'),'O(n)','O(k)',5),
1678:E('interpret_goal_command',[('command','str')],'str',['strings','parsing'],['Command is a valid concatenation of G, (), and (al).','Translate these tokens respectively to G, o, and al without changing order.'],[(['G()(al)'],'Tokens G, (), and (al) translate to Goal.'),(['G()()()()(al)'],'Four empty-parenthesis tokens become four o characters before al.')],[[s] for s in ['G()(al)','G()()()()(al)','G','()','(al)','GG','G()','()(al)','(al)G','()()','(al)(al)','G(al)G','()G()','G(al)()']],PARSER,[PARSER.replace("replace('()','o')","replace('()','')"),PARSER.replace("replace('(al)','al')","replace('(al)','la')")],['Deletes the o token instead of translating it.','Reverses al into la.'],parser_o,rparser,L('The grammar has three fixed tokens with fixed translations.','Replace the two parenthesized tokens; G already represents itself.','Convert () to o, then (al) to al.','Valid input contains no other parentheses, so the two replacements consume every encoded token and preserve order.'),'O(n)','O(n)',3),
}
