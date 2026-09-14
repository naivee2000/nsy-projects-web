"""Hard-focused workbook batch 136."""

from functools import lru_cache
from math import gcd

from .import_batch_055 import entry


MOD=1_000_000_007


def company_oracle(args):
    ideas=args[0];existing=set(ideas);answer=0
    for i in range(len(ideas)):
        for j in range(len(ideas)):
            if i==j:continue
            first,second=ideas[i],ideas[j]
            if second[0]+first[1:] not in existing and first[0]+second[1:] not in existing:answer+=1
    return answer


def random_company(rng):
    suffixes=[''.join(rng.choice('abcd') for _ in range(rng.randint(1,4))) for _ in range(rng.randint(2,12))]
    ideas=[]
    for suffix in suffixes:
        word=rng.choice('abcd')+suffix
        if word not in ideas:ideas.append(word)
    return [ideas or ['aa','bb']]


def contradiction_oracle(args):
    equations,values=args;graph={}
    for (left,right),value in zip(equations,values):
        stack=[(left,1.0)];seen=set();found=None
        while stack:
            node,ratio=stack.pop()
            if node==right:found=ratio;break
            if node in seen:continue
            seen.add(node)
            for neighbor,weight in graph.get(node,[]):stack.append((neighbor,ratio*weight))
        if found is not None and abs(found-value)>1e-5*max(1,abs(found),abs(value)):return True
        graph.setdefault(left,[]).append((right,value));graph.setdefault(right,[]).append((left,1/value))
    return False


def random_contradiction(rng):
    count=rng.randint(2,7);names=[chr(97+i) for i in range(count)];hidden={name:rng.randint(1,8) for name in names};pairs=[]
    for i in range(count-1):pairs.append([names[i],names[i+1]])
    for _ in range(rng.randint(0,5)):
        a,b=rng.sample(names,2)
        if [a,b] not in pairs:pairs.append([a,b])
    values=[hidden[a]/hidden[b] for a,b in pairs]
    if rng.random()<.5:
        index=rng.randrange(len(values));values[index]*=1.1
    return [pairs,values]


def wood_oracle(args):
    m,n,prices=args;base={(h,w):price for h,w,price in prices}
    @lru_cache(None)
    def solve(h,w):
        best=base.get((h,w),0)
        for cut in range(1,h):best=max(best,solve(cut,w)+solve(h-cut,w))
        for cut in range(1,w):best=max(best,solve(h,cut)+solve(h,w-cut))
        return best
    return solve(m,n)


def random_wood(rng):
    m,n=rng.randint(1,6),rng.randint(1,6);prices=[]
    for h in range(1,m+1):
        for w in range(1,n+1):
            if rng.random()<.45:prices.append([h,w,rng.randint(1,30)])
    return [m,n,prices]


def rolls_oracle(args):
    n=args[0]
    @lru_cache(None)
    def extend(length,last,previous):
        if length==n:return 1
        return sum(extend(length+1,value,last) for value in range(1,7)
                   if value!=last and value!=previous and (not last or gcd(value,last)==1))%MOD
    return extend(0,0,0)


def random_rolls(rng):return [rng.randint(1,30)]


def secret_oracle(args):
    n,delay,forget=args;learned=[0]*(n+1);learned[1]=1
    for day in range(2,n+1):
        learned[day]=sum(learned[earlier] for earlier in range(1,day) if earlier+delay<=day<earlier+forget)%MOD
    return sum(learned[day] for day in range(1,n+1) if day+forget>n)%MOD


def random_secret(rng):
    n=rng.randint(2,40);forget=rng.randint(2,n);delay=rng.randint(1,forget-1);return [n,delay,forget]


COMPANY='''\
def distinct_company_names(ideas):
    groups=[set() for _ in range(26)]
    for word in ideas:groups[ord(word[0])-97].add(word[1:])
    answer=0
    for left in range(26):
        for right in range(left+1,26):
            shared=len(groups[left]&groups[right]);answer+=2*(len(groups[left])-shared)*(len(groups[right])-shared)
    return answer
'''

CONTRADICTION='''\
def equations_have_contradiction(equations,values):
    parent={};weight={}
    def find(node):
        if parent[node]!=node:
            old=parent[node];parent[node]=find(old);weight[node]*=weight[old]
        return parent[node]
    for (left,right),value in zip(equations,values):
        for node in (left,right):
            if node not in parent:parent[node]=node;weight[node]=1.0
        root_left,root_right=find(left),find(right)
        if root_left==root_right:
            if abs(weight[left]/weight[right]-value)>1e-5*max(1,abs(value)):return True
        else:
            parent[root_left]=root_right;weight[root_left]=value*weight[right]/weight[left]
    return False
'''

WOOD='''\
def maximum_wood_sale_value(m,n,prices):
    dp=[[0]*(n+1) for _ in range(m+1)]
    for height,width,price in prices:dp[height][width]=max(dp[height][width],price)
    for height in range(1,m+1):
        for width in range(1,n+1):
            for cut in range(1,height):dp[height][width]=max(dp[height][width],dp[cut][width]+dp[height-cut][width])
            for cut in range(1,width):dp[height][width]=max(dp[height][width],dp[height][cut]+dp[height][width-cut])
    return dp[m][n]
'''

ROLLS='''\
def distinct_dice_roll_sequences(n):
    states={(value,0):1 for value in range(1,7)}
    for _ in range(1,n):
        updated={}
        for (last,previous),count in states.items():
            for value in range(1,7):
                if value!=last and value!=previous and __import__('math').gcd(value,last)==1:updated[(value,last)]=(updated.get((value,last),0)+count)%1000000007
        states=updated
    return sum(states.values())%1000000007
'''

SECRET='''\
def people_aware_of_secret(n,delay,forget):
    learned=[0]*(n+1);learned[1]=1;sharing=0
    for day in range(2,n+1):
        if day-delay>=1:sharing+=learned[day-delay]
        if day-forget>=1:sharing-=learned[day-forget]
        learned[day]=sharing%1000000007
    return sum(learned[max(1,n-forget+1):])%1000000007
'''


BATCH={
2306:entry('distinct_company_names',[('ideas','list[str]')],'int',['strings','hash sets','combinatorics'],['Choose two distinct original ideas in order and swap their first letters.','A company name is valid only when both newly formed words are absent from the original idea set.','Count ordered company names, so reversing the two resulting words is a different name.'],[([['coffee','donuts','time','toffee']],'Valid swaps between the c/d suffix groups and t/d groups produce six ordered names.'),([['lack','back']],'Swapping initials recreates the two original ideas, so no valid name exists.')],[[x] for x in [['aa','bb'],['ab','ac'],['ab','cb'],['ax','by','cz'],['coffee','toffee'],['a','b'],['aaa','baa','cbb'],['dog','cat','fish'],['ab','bc','ca'],['apple','banana','cherry'],['ax','ay','bx','bz'],['moon','soon','star'],['aa','ba','ca','db'],['red','bed','blue','green']]],COMPANY,[COMPANY.replace('len(groups[left])-shared','len(groups[left])',1),COMPANY.replace('2*','')],['Does not remove suffixes shared by both initial groups, allowing a generated word already in ideas.','Counts only one ordering for each valid pair of swapped ideas.'],company_oracle,random_company,['Group suffixes by their original first letter.','For two initial groups, suffixes present in both cannot participate because one swapped word would already exist.','Multiply the exclusive suffix counts and multiply by two for the two ordered company names.','Every valid swap chooses one exclusive suffix from each group, and every such choice creates two absent words, establishing a bijection.'],'O(total characters+alphabet^2*ideas)','O(total characters)',8),
2307:entry('equations_have_contradiction',[('equations','list[list[str]]'),('values','list[float]')],'bool',['graphs','union find','weighted union find'],['equations[i]=[a,b] asserts a/b=values[i].','Return true when any equation conflicts with ratios implied by earlier equations.','Compare floating ratios with relative tolerance 1e-5.'],[([[['a','b'],['b','c'],['a','c']],[3.0,0.5,1.5]],'The first two equations imply a/c=1.5, matching the third, so there is no contradiction.'),([[['a','b'],['b','c'],['a','c']],[2.0,3.0,5.0]],'The first two equations imply a/c=6, contradicting the asserted value five.')],[[e,v] for e,v in [([['a','b']],[2.0]),([['a','b'],['b','a']],[2.0,0.5]),([['a','b'],['b','a']],[2.0,2.0]),([['a','b'],['c','d']],[2.0,3.0]),([['a','b'],['b','c'],['a','c']],[2.0,3.0,6.0]),([['a','b'],['b','c'],['a','c']],[2.0,3.0,6.1]),([['x','x']],[1.0]),([['x','x']],[2.0]),([['a','b'],['a','c'],['b','c']],[4.0,2.0,0.5]),([['a','b'],['c','d'],['b','c'],['a','d']],[2.0,3.0,4.0,24.0]),([['a','b'],['b','c'],['c','a']],[2.0,5.0,0.1]),([['p','q'],['q','r'],['p','r']],[0.5,0.25,0.125]),([['a','b'],['b','c'],['c','d'],['a','d']],[2.0,2.0,2.0,8.0]),([['u','v'],['u','v']],[3.0,3.0001])]],CONTRADICTION,[CONTRADICTION.replace('value*weight[right]/weight[left]','weight[right]/(value*weight[left])'),CONTRADICTION.replace('>1e-5*max(1,abs(value))','>1e-3*max(1,abs(value))')],['Attaches weighted roots with the ratio inverted, corrupting later implied equations.','Uses a tolerance one hundred times too loose and misses genuine contradictions.'],contradiction_oracle,random_contradiction,['Store for each node its parent and multiplicative ratio to that parent.','Path compression must multiply weights so each node’s stored weight becomes its ratio to the root.','For different roots, attach one root with the ratio that makes the new equation true; for equal roots, compare the implied ratio with the assertion.','Weighted union invariants preserve every equation along a component, so an inconsistent same-root ratio is exactly a contradiction.'],'O(e alpha(v))','O(v)',8),
2312:entry('maximum_wood_sale_value',[('m','int'),('n','int'),('prices','list[list[int]]')],'int',['matrices','dynamic programming'],['Start with one m by n rectangle and make any number of full horizontal or vertical cuts.','A listed [height,width,price] piece may be sold without rotation; unlisted pieces have direct price zero.','Return the maximum total sale value.'],[([3,5,[[1,4,2],[2,2,7],[2,1,3]]],'Combining profitable listed pieces through cuts yields maximum value nineteen.'),([2,2,[[1,1,2],[2,2,7]]],'Cutting into four unit pieces worth two each yields eight, which beats selling the whole piece for seven.')],[[m,n,p] for m,n,p in [(1,1,[]),(1,1,[[1,1,5]]),(1,2,[[1,1,3]]),(2,1,[[1,1,3]]),(2,2,[[2,2,5],[1,1,2]]),(2,3,[[1,3,4],[2,1,3]]),(3,3,[[1,1,1],[3,3,8]]),(3,2,[[2,1,4],[1,2,3]]),(4,4,[[2,2,5],[4,4,19]]),(1,5,[[1,2,3],[1,1,1]]),(5,1,[[2,1,3],[1,1,1]]),(3,4,[[3,2,10],[1,4,5]]),(4,3,[[2,3,9],[2,1,2]]),(2,4,[[1,2,4],[2,2,7]])]],WOOD,[WOOD.replace('range(1,height)','range(1,height//2)'),WOOD.replace('dp[height][width]=max(dp[height][width],price)','dp[height][width]=price')],['Omits central/asymmetric horizontal cuts because its range stops too early.','Overwrites duplicate direct prices instead of keeping the best listed price.'],wood_oracle,random_wood,['Let dp[h][w] be the best value obtainable from that exact rectangle.','Initialize states with their best listed direct prices.','For every horizontal and vertical cut, combine the two resulting dp states and maximize.','The final operation of any optimal cutting plan is either no cut or one full cut into two independently optimal subrectangles, proving the recurrence.'],'O(m*n*(m+n))','O(m*n)',8),
2318:entry('distinct_dice_roll_sequences',[('n','int')],'int',['dynamic programming','number theory'],['Each roll is an integer one through six.','Adjacent rolls must be different and coprime.','A roll must also differ from the roll two positions earlier; return the sequence count modulo 1,000,000,007.'],[([4],'There are 184 length-four sequences satisfying both distance-one and distance-two restrictions.'),([1],'Any of the six faces forms a valid one-roll sequence.')],[[n] for n in [2,3,5,6,7,8,9,10,12,15,20,25,30,50]],ROLLS,[ROLLS.replace('value!=previous and ',''),ROLLS.replace("gcd(value,last)==1",'gcd(value,last)>1')],['Ignores the required inequality with the roll two positions earlier.','Requires adjacent values to share a factor instead of being coprime.'],rolls_oracle,random_rolls,['The next choice depends only on the previous two roll values.','Store counts by state (last,second_last), using zero as the missing predecessor initially.','Transition to faces different from both stored values and coprime with last; shift the state and reduce modulo M.','Those state fields contain every condition involving a new roll, so the transitions generate every valid sequence exactly once.'],'O(36*n)','O(36)',8),
2327:entry('people_aware_of_secret',[('n','int'),('delay','int'),('forget','int')],'int',['dynamic programming','sliding windows'],['One person learns the secret on day one.','A person starts sharing delay days after learning and shares once per day until strictly before the day they forget.','Return how many people still remember at the end of day n, modulo 1,000,000,007.'],[([6,2,4],'Tracking daily learners and the active sharing window leaves five people aware on day six.'),([4,1,3],'Each learner shares starting the next day and forgets after three days, leaving six aware people on day four.')],[[n,d,f] for n,d,f in [(2,1,2),(3,1,2),(3,1,3),(5,2,3),(5,2,4),(7,1,4),(10,2,5),(10,3,6),(20,2,7),(15,4,8),(30,5,10),(8,3,4),(12,1,2),(25,7,14)]],SECRET,[SECRET.replace('day-forget>=1','day-forget>1'),SECRET.replace('max(1,n-forget+1)','max(1,n-forget)')],['Removes sharers one day late, allowing people to share on their forgetting day.','Includes people who forgot exactly on day n in the final aware count.'],secret_oracle,random_secret,['Record how many people first learn the secret on each day.','Maintain the number currently sharing as a sliding sum: add learners from day-delay and remove learners from day-forget.','Today’s learner count equals that sharing count; at the end sum learners from the last forget-1 days.','The window boundaries encode exactly each cohort’s sharing and remembering interval, so every person is counted on precisely the valid days.'],'O(n)','O(n)',5),
}

BATCH[2312]['wrong'][1]='''\
def maximum_wood_sale_value(m,n,prices):
    dp=[[0]*(n+1) for _ in range(m+1)]
    for height,width,price in prices:dp[height][width]=max(dp[height][width],price)
    for height in range(1,m+1):
        for width in range(1,n+1):
            for cut in range(1,height):dp[height][width]=max(dp[height][width],dp[cut][width]+dp[height-cut][width])
    return dp[m][n]
'''
BATCH[2312]['wrong_reasons'][1]='Considers horizontal cuts only and misses profitable vertical splits.'
