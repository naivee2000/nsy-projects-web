"""Final reviewed group of workbook batch 118."""
from .import_batch_055 import entry

def fruits_o(a):
 fruits,start,k=a;best=0
 for i in range(len(fruits)):
  for j in range(i,len(fruits)):
   left,right=fruits[i][0],fruits[j][0];cost=right-left+min(abs(start-left),abs(start-right))
   if cost<=k:best=max(best,sum(amount for _,amount in fruits[i:j+1]))
 return best
def candy_o(a):
 values,k=a;return max(len(set(values[:i]+values[i+k:])) for i in range(len(values)-k+1))
def palindrome_o(a):return next((word for word in a[0] if word==word[::-1]),'')
def spaces_o(a):
 s,spaces=a;chosen=set(spaces);return ''.join((' ' if i in chosen else '')+char for i,char in enumerate(s))
def descent_o(a):
 values=a[0];return sum(all(values[x]-values[x+1]==1 for x in range(i,j)) for i in range(len(values)) for j in range(i,len(values)))
def rfruits(r):
 pos=sorted(r.sample(range(0,30),r.randint(1,8)));return [[[x,r.randint(1,10)] for x in pos],r.randint(0,29),r.randint(0,20)]
def rcandy(r):
 values=[r.randint(1,6) for _ in range(r.randint(1,20))];return [values,r.randint(0,len(values))]
def rpal(r):return [[''.join(r.choice('abc') for _ in range(r.randint(1,7))) for _ in range(r.randint(1,12))]]
def rspaces(r):
 s=''.join(r.choice('abc') for _ in range(r.randint(1,20)));return [s,sorted(r.sample(range(len(s)),r.randint(0,len(s))))]
def rdescent(r):return [[r.randint(0,20) for _ in range(r.randint(1,30))]]

FRUITS='''\
def maximum_harvested_fruits(fruits,start_pos,k):
    left=0;total=0;answer=0
    for right,(position,amount) in enumerate(fruits):
        total+=amount
        while left<=right:
            left_position=fruits[left][0]
            travel=position-left_position+min(abs(start_pos-left_position),abs(start_pos-position))
            if travel<=k:break
            total-=fruits[left][1];left+=1
        answer=max(answer,total)
    return answer
'''
CANDY='''\
def maximum_flavors_after_sharing(candies,k):
    from collections import Counter
    kept=Counter(candies[k:]);answer=len(kept)
    for right in range(k,len(candies)):
        kept[candies[right-k]]+=1;kept[candies[right]]-=1
        if kept[candies[right]]==0:del kept[candies[right]]
        answer=max(answer,len(kept))
    return answer
'''
PAL='''\
def first_palindromic_word(words):
    for word in words:
        if word==word[::-1]:return word
    return ''
'''
SPACES='''\
def insert_spaces_at_indices(s,spaces):
    answer=[];next_space=0
    for index,char in enumerate(s):
        if next_space<len(spaces) and spaces[next_space]==index:answer.append(' ');next_space+=1
        answer.append(char)
    return ''.join(answer)
'''
DESCENT='''\
def smooth_descent_periods(prices):
    answer=run=0
    for index,price in enumerate(prices):
        run=run+1 if index and prices[index-1]-price==1 else 1
        answer+=run
    return answer
'''
def L(*x):return list(x)
BATCH={
2106:entry('maximum_harvested_fruits',[('fruits','list[list[int]]'),('start_pos','int'),('k','int')],'int',['arrays','sliding windows','greedy'],['fruits is sorted by unique axis positions and each amount is positive.','Starting at start_pos, walk at most k unit steps and harvest every fruit at each visited position.','Return the maximum harvest; changing direction at most once is sufficient.'],[([[[2,8],[6,3],[8,6]],5,4],'Walking right from five through eight costs three steps and harvests three plus six fruits.'),([[[0,9],[4,1],[5,7],[6,2],[7,4],[10,9]],5,4],'Visiting positions four through seven costs five? The best feasible route harvests fourteen fruits.')],[[f,s,k] for f,s,k in [([[0,5]],0,0),([[0,5]],1,0),([[0,5]],1,1),([[1,2],[3,4]],2,1),([[1,2],[3,4]],2,2),([[0,1],[10,9]],5,5),([[0,1],[5,5],[10,1]],5,5),([[1,5],[2,6],[3,7]],0,2),([[1,5],[2,6],[3,7]],4,2),([[0,4],[2,5],[4,6]],2,4),([[0,10],[4,1],[8,10]],4,8),([[2,3],[6,4],[9,5]],7,3),([[1,1],[2,2],[8,8]],5,6),([[0,2],[3,3],[7,7],[9,1]],6,5)]],FRUITS,[FRUITS.replace('min(abs(start_pos-left_position),abs(start_pos-position))','max(abs(start_pos-left_position),abs(start_pos-position))'),FRUITS.replace('travel<=k','travel<k')],['Charges the farther approach in addition to the full interval and rejects feasible turn-once routes.','Requires strictly fewer than k steps and rejects routes using the full budget.'],fruits_o,rfruits,L('Any harvested set can be replaced by the full position interval between its extremes without extra travel.','Slide a sorted interval whose minimum visit cost is width plus the shorter distance from start to an endpoint.','Add each right amount; while width+min(abs(start-left),abs(start-right))>k, remove left; track the largest sum.','All amounts are positive, so each feasible interval should include every contained position, and window feasibility is monotone as left advances.'),'O(n)','O(1)',8),
2107:entry('maximum_flavors_after_sharing',[('candies','list[int]'),('k','int')],'int',['arrays','sliding windows','hash maps'],['Give away exactly one contiguous segment of k candies; k may be zero or the entire array length.','Count distinct flavors remaining outside that segment.','Return the maximum possible remaining distinct count.'],[([[1,2,2,3,4,3],3],'Giving away [2,3,4] leaves flavors one, two, and three.'),([[2,2,2,2,3,3],2],'Giving away two copies of either flavor still leaves both flavors.')],[[c,k] for c,k in [([1],0),([1],1),([1,2],1),([1,1],1),([1,2,3],0),([1,2,3],3),([1,2,1],1),([1,2,1],2),([1,1,2,2],2),([1,2,3,1],2),([4,4,4,5],3),([1,2,2,3,4,3],1),([1,2,2,3,4,3],5),([1,2,3,4,5],2)]],CANDY,[CANDY.replace('candies[k:]','candies[:k]'),CANDY.replace('answer=max(answer,len(kept))','answer=min(answer,len(kept))')],['Counts the shared window instead of the retained candies.','Tracks the minimum remaining variety instead of the maximum.'],candy_o,rcandy,L('Track the complement of the moving shared window rather than rebuilding its set.','Initialize frequencies after the first k candies; when the window moves, restore its old left candy and remove its new right candy.','Delete zero counts and maximize len(counter) after each move.','The counter always represents exactly the candies outside the current length-k segment, so its key count is the retained variety.'),'O(n)','O(distinct flavors)',5),
2108:entry('first_palindromic_word',[('words','list[str]')],'str',['strings','two pointers'],['words is nonempty and each word is nonempty.','A palindrome reads identically from left to right and right to left.','Return the earliest palindromic word, or an empty string when none exists.'],[([['abc','car','ada','racecar','cool']],'ada is the first palindrome even though racecar also qualifies later.'),([['notapalindrome','racecar']],'The second word is the first qualifying palindrome.')],[[w] for w in [['a'],['ab'],['aa'],['ab','ba'],['abc','aba'],['level','noon'],['x','y'],['python','code'],['abba','aba'],['abc','civic','radar'],['zz','zz'],['abca','a'],['12321','wow'],['rotor','test','refer']]],PAL,[PAL.replace('for word in words','for word in reversed(words)'),PAL.replace("return ''","return words[0]")],['Returns the last qualifying palindrome instead of the first.','Returns the first nonpalindromic word when no palindrome exists.'],palindrome_o,rpal,L('Order matters, so scan without sorting or collecting all matches.','Compare each word with its reversal and stop at the first equality.','Return word on word==word[::-1]; after the loop return empty string.','The first successful scan position is exactly the earliest palindrome, and exhausting the list proves none exists.'),'O(total characters)','O(max word length)',3),
2109:entry('insert_spaces_at_indices',[('s','str'),('spaces','list[int]')],'str',['strings','two pointers'],['spaces is strictly increasing and every index identifies a character before which a space is inserted.','The original characters retain their order.','Return the new string containing all requested spaces.'],[(['LeetcodeHelpsMeLearn',[8,13,15]],'Inserting before H, M, and L yields Leetcode Helps Me Learn.'),(['EnjoyYourCoffee',[5,9]],'The indices split the text into Enjoy, Your, and Coffee.')],[[s,p] for s,p in [('a',[]),('a',[0]),('ab',[1]),('abc',[0,1,2]),('hello',[2]),('abcdef',[1,5]),('python',[]),('onetwothree',[3,6]),('x y',[1]),('aaaa',[1,2,3]),('codepractice',[4]),('012345',[0,5]),('hi',[0,1]),('algorithm',[2,4,7])]],SPACES,[SPACES.replace('spaces[next_space]==index','spaces[next_space]==index+1'),SPACES.replace("answer.append(' ')","answer.append('  ')")],['Inserts each space one character late.','Inserts two spaces at every requested index.'],spaces_o,rspaces,L('Both the string positions and requested indices are already ordered.','Walk the string while advancing one pointer through spaces whenever it matches the current index.','Before appending s[i], append one space if spaces[j]==i, then increment j.','Every requested index is encountered once in order, so every insertion occurs at its exact boundary.'),'O(length+spaces)','O(length+spaces)',4),
2110:entry('smooth_descent_periods',[('prices','list[int]')],'int',['arrays','dynamic programming','sliding windows'],['prices is nonempty.','A period is smooth when each price after the first is exactly one less than its predecessor.','Count all nonempty contiguous smooth periods.'],[([[3,2,1,4]],'The four singleton periods plus [3,2], [2,1], and [3,2,1] total seven.'),([[8,6,7,7]],'No adjacent pair descends by exactly one, so only four singleton periods count.')],[[p] for p in [[1],[2,1],[1,2],[3,2,1],[3,1],[5,4,3,2,1],[1,1,1],[4,3,5,4],[10,9,8,8,7],[0,-1,-2],[2,1,0,2,1],[7,6,5,4,10],[5,3,2,1],[9,8,10,9,8]]],DESCENT,[DESCENT.replace('prices[index-1]-price==1','prices[index-1]-price>=1'),DESCENT.replace('answer+=run','answer+=run-1')],['Accepts drops larger than one as smooth.','Omits every singleton period by subtracting one per day.'],descent_o,rdescent,L('Each day ends one singleton plus every smooth period ending yesterday that can extend.','Maintain the length of the current exactly-one descent run.','If previous-price==1 set run+=1, otherwise run=1; add run to the total.','The run length equals the number of valid starting positions for a period ending today, counting each period at its unique endpoint.'),'O(n)','O(1)',5)
}
BATCH[2109]['difficulty']=5
