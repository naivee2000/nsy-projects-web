"""Reviewed mixed tree, linked-list, binary-search, greedy, and digit-DP imports."""
from collections import deque
from functools import lru_cache
from itertools import combinations

from .import_batch_055 import entry


def tree_data(serial):
    if not serial:
        return [], []
    values, edges, queue, at = [serial[0]], [], deque([0]), 1
    while queue and at < len(serial):
        parent = queue.popleft()
        for _ in range(2):
            if at >= len(serial):
                break
            value = serial[at]
            at += 1
            if value is not None:
                child = len(values)
                values.append(value)
                edges.append((parent, child))
                queue.append(child)
    return values, edges


def clumsy_oracle(args):
    n = args[0]
    terms, operation = [n], 0
    for value in range(n - 1, 0, -1):
        if operation % 4 == 0:
            terms[-1] *= value
        elif operation % 4 == 1:
            terms[-1] = int(terms[-1] / value)
        elif operation % 4 == 2:
            terms.append(value)
        else:
            terms.append(-value)
        operation += 1
    return sum(terms)


def domino_oracle(args):
    tops, bottoms = args
    answer = len(tops) + 1
    for value in range(1, 7):
        if all(value in pair for pair in zip(tops, bottoms)):
            answer = min(answer, sum(x != value for x in tops), sum(x != value for x in bottoms))
    return answer if answer <= len(tops) else -1


def bst_oracle(args):
    root = None
    for value in args[0]:
        if root is None:
            root = [value, None, None]
            continue
        node = root
        while True:
            side = 1 if value < node[0] else 2
            if node[side] is None:
                node[side] = [value, None, None]
                break
            node = node[side]
    if root is None:
        return []
    output, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            output.append(None)
        else:
            output.append(node[0]); queue.extend(node[1:])
    while output and output[-1] is None:
        output.pop()
    return output


def song_oracle(args):
    values = args[0]
    return sum((values[i] + values[j]) % 60 == 0 for i in range(len(values)) for j in range(i + 1, len(values)))


def ship_oracle(args):
    weights, days = args
    for capacity in range(max(weights), sum(weights) + 1):
        used, load = 1, 0
        for weight in weights:
            if load + weight > capacity:
                used += 1; load = 0
            load += weight
        if used <= days:
            return capacity


def repeated_oracle(args):
    return sum(len(set(str(value))) < len(str(value)) for value in range(1, args[0] + 1))


def sightseeing_oracle(args):
    values = args[0]
    return max(values[i] + values[j] + i - j for i in range(len(values)) for j in range(i + 1, len(values)))


def repunit_oracle(args):
    k = args[0]
    remainder = 0
    for length in range(1, k + 1):
        remainder = (remainder * 10 + 1) % k
        if remainder == 0:
            return length
    return -1


def binary_query_oracle(args):
    text, n = args
    return all(bin(value)[2:] in text for value in range(1, n + 1))


def negabinary_oracle(args):
    n = args[0]
    if n == 0:
        return '0'
    for width in range(1, 24):
        for mask in range(1 << (width - 1), 1 << width):
            if sum(((mask >> bit) & 1) * ((-2) ** bit) for bit in range(width)) == n:
                return bin(mask)[2:]
    raise AssertionError('generated value exceeded independent search range')


def prefix_five_oracle(args):
    value, answer = 0, []
    for bit in args[0]:
        value = value * 2 + bit
        answer.append(value % 5 == 0)
    return answer


def next_node_oracle(args):
    values = args[0]
    return [next((later for later in values[i + 1:] if later > value), 0) for i, value in enumerate(values)]


def outer_oracle(args):
    depth, output = 0, []
    for char in args[0]:
        if char == '(':
            if depth:
                output.append(char)
            depth += 1
        else:
            depth -= 1
            if depth:
                output.append(char)
    return ''.join(output)


def binary_tree_sum_oracle(args):
    values, edges = tree_data(args[0])
    children = [[] for _ in values]
    for parent, child in edges:
        children[parent].append(child)
    def visit(node, value):
        current = value * 2 + values[node]
        return current if not children[node] else sum(visit(child, current) for child in children[node])
    return visit(0, 0)


def camel_oracle(args):
    queries, pattern = args
    result = []
    for query in queries:
        at = 0
        for char in query:
            if at < len(pattern) and char == pattern[at]:
                at += 1
            elif char.isupper():
                at = -10**6
                break
        result.append(at == len(pattern))
    return result


def clips_oracle(args):
    clips, target = args
    infinity = len(clips) + 1
    dp = [0] + [infinity] * target
    for end in range(1, target + 1):
        dp[end] = min((dp[start] + 1 for start, stop in clips if start < end <= stop), default=infinity)
    return dp[target] if dp[target] < infinity else -1


def divisor_oracle(args):
    wins = [False] * (args[0] + 1)
    for value in range(2, args[0] + 1):
        wins[value] = any(value % move == 0 and not wins[value - move] for move in range(1, value))
    return wins[args[0]]


def ancestor_oracle(args):
    values, edges = tree_data(args[0])
    children = [[] for _ in values]
    for parent, child in edges:
        children[parent].append(child)
    answer = 0
    def walk(node, ancestors):
        nonlocal answer
        answer = max(answer, *(abs(values[node] - values[a]) for a in ancestors), 0)
        for child in children[node]:
            walk(child, ancestors + [node])
    walk(0, [])
    return answer


def arithmetic_oracle(args):
    nums = args[0]
    best = 2
    for size in range(2, len(nums) + 1):
        for indexes in combinations(range(len(nums)), size):
            seq = [nums[i] for i in indexes]
            if all(seq[i] - seq[i - 1] == seq[1] - seq[0] for i in range(2, size)):
                best = size
    return best


def recover_oracle(args):
    traversal = args[0]
    tokens, at = [], 0
    while at < len(traversal):
        depth = 0
        while at < len(traversal) and traversal[at] == '-':
            depth += 1; at += 1
        end = at
        while end < len(traversal) and traversal[end].isdigit():
            end += 1
        tokens.append((depth, int(traversal[at:end]))); at = end
    nodes, stack = [], []
    for depth, value in tokens:
        node = [value, None, None]
        while len(stack) > depth:
            stack.pop()
        if stack:
            side = 1 if stack[-1][1] is None else 2
            stack[-1][side] = node
        else:
            root = node
        stack.append(node); nodes.append(node)
    output, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            output.append(None)
        else:
            output.append(node[0]); queue.extend(node[1:])
    while output and output[-1] is None:
        output.pop()
    return output


def random_clumsy(r): return [r.randint(1, 100)]
def random_domino(r):
    n = r.randint(1, 10); return [[r.randint(1, 6) for _ in range(n)], [r.randint(1, 6) for _ in range(n)]]
def random_bst(r):
    values = r.sample(range(1, 100), r.randint(1, 12)); root = None
    for value in values:
        if root is None: root = [value, None, None]; continue
        node = root
        while True:
            side = 1 if value < node[0] else 2
            if node[side] is None: node[side] = [value, None, None]; break
            node = node[side]
    output=[]
    def preorder(node):
        if node: output.append(node[0]); preorder(node[1]); preorder(node[2])
    preorder(root); return [output]
def random_songs(r): return [[r.randint(1, 500) for _ in range(r.randint(1, 14))]]
def random_ship(r):
    values=[r.randint(1,20) for _ in range(r.randint(1,10))]; return [values,r.randint(1,len(values))]
def random_repeated(r): return [r.randint(1, 5000)]
def random_sightseeing(r): return [[r.randint(1,30) for _ in range(r.randint(2,12))]]
def random_repunit(r): return [r.randint(1, 80)]
def random_binary_query(r): return [''.join(r.choice('01') for _ in range(r.randint(1,20))),r.randint(1,20)]
def random_negabinary(r): return [r.randint(0, 150)]
def random_prefix(r): return [[r.randrange(2) for _ in range(r.randint(1,20))]]
def random_list(r): return [[r.randint(0,30) for _ in range(r.randint(1,15))]]
def random_parentheses(r):
    def primitive(depth): return '(' * depth + ')' * depth
    return [''.join(primitive(r.randint(1,5)) for _ in range(r.randint(1,5)))]
def random_binary_tree(r): return [[r.randrange(2) for _ in range(r.randint(1,15))]]
def random_camel(r):
    pattern=''.join(r.choice('ABC')+''.join(r.choice('abc') for _ in range(r.randint(0,2))) for _ in range(r.randint(1,3)))
    queries=[''.join(r.choice('abcABC') for _ in range(r.randint(1,10))) for _ in range(r.randint(1,7))]
    return [queries,pattern]
def random_clips(r):
    target=r.randint(1,12); return [[[a,b] for a in range(target) for b in range(a+1,target+1) if r.random()<.16],target]
def random_divisor(r): return [r.randint(1,100)]
def random_ancestor(r): return [[r.randint(0,100) for _ in range(r.randint(1,15))]]
def random_arithmetic(r): return [[r.randint(-12,12) for _ in range(r.randint(2,8))]]
def random_recover(r):
    counter=[1]
    def make(depth=0):
        value=counter[0];counter[0]+=1; text='-'*depth+str(value)
        if depth<3 and r.random()<.65:
            text+=make(depth+1)
            if r.random()<.55:text+=make(depth+1)
        return text
    return [make()]


CLUMSY='''def clumsy_factorial(n):
 stack=[n];op=0
 for value in range(n-1,0,-1):
  if op%4==0:stack[-1]*=value
  elif op%4==1:stack[-1]=int(stack[-1]/value)
  elif op%4==2:stack.append(value)
  else:stack.append(-value)
  op+=1
 return sum(stack)
'''
DOMINO='''def minimum_domino_rotations(tops, bottoms):
 def cost(value):
  if any(value not in (a,b) for a,b in zip(tops,bottoms)):return float('inf')
  return min(sum(a!=value for a in tops),sum(b!=value for b in bottoms))
 answer=min(cost(tops[0]),cost(bottoms[0]));return -1 if answer==float('inf') else answer
'''
BST='''def bst_from_preorder(preorder):
 at=0
 def build(limit):
  nonlocal at
  if at==len(preorder) or preorder[at]>limit:return None
  node=TreeNode(preorder[at]);at+=1;node.left=build(node.val);node.right=build(limit);return node
 return build(float('inf'))
'''
SONGS='''def divisible_song_pairs(time):
 counts=[0]*60;answer=0
 for value in time:
  remainder=value%60;answer+=counts[-remainder%60];counts[remainder]+=1
 return answer
'''
SHIP='''def minimum_ship_capacity(weights, days):
 def needed(capacity):
  used=1;load=0
  for weight in weights:
   if load+weight>capacity:used+=1;load=0
   load+=weight
  return used
 low,high=max(weights),sum(weights)
 while low<high:
  middle=(low+high)//2
  if needed(middle)<=days:high=middle
  else:low=middle+1
 return low
'''
REPEATED='''def count_repeated_digit_numbers(n):
 digits=list(map(int,str(n+1)));unique=0
 for length in range(1,len(digits)):
  ways=9
  for used_count in range(1,length):ways*=10-used_count
  unique+=ways
 used=set()
 for i,digit in enumerate(digits):
  for choice in range(0 if i else 1,digit):
   if choice not in used:
    ways=1
    for remaining in range(len(digits)-i-1):ways*=10-len(used)-1-remaining
    unique+=ways
  if digit in used:break
  used.add(digit)
 else:return n-unique
 return n-unique
'''
SIGHT='''def best_sightseeing_score(values):
 best=values[0];answer=0
 for j in range(1,len(values)):
  answer=max(answer,best+values[j]-j);best=max(best,values[j]+j)
 return answer
'''
REPUNIT='''def smallest_repunit_length(k):
 if k%2==0 or k%5==0:return -1
 remainder=0
 for length in range(1,k+1):
  remainder=(remainder*10+1)%k
  if remainder==0:return length
 return -1
'''
QUERY='''def contains_all_binary_values(s, n):
 return all(bin(value)[2:] in s for value in range(n//2+1,n+1))
'''
NEGABINARY='''def to_base_negative_two(n):
 if n==0:return '0'
 digits=[]
 while n:
  n,remainder=divmod(n,-2)
  if remainder<0:n+=1;remainder+=2
  digits.append(str(remainder))
 return ''.join(reversed(digits))
'''
PREFIX='''def binary_prefixes_divisible_by_five(nums):
 value=0;answer=[]
 for bit in nums:value=(value*2+bit)%5;answer.append(value==0)
 return answer
'''
NEXT='''def next_greater_linked_values(head):
 values=[]
 while head:values.append(head.val);head=head.next
 answer=[0]*len(values);stack=[]
 for i,value in enumerate(values):
  while stack and values[stack[-1]]<value:answer[stack.pop()]=value
  stack.append(i)
 return answer
'''
OUTER='''def remove_outer_parentheses(s):
 depth=0;answer=[]
 for char in s:
  if char=='(':depth+=1
  if depth>1:answer.append(char)
  if char==')':depth-=1
 return ''.join(answer)
'''
TREESUM='''def sum_root_to_leaf_binary(root):
 def visit(node,value):
  if node is None:return 0
  value=value*2+node.val
  if node.left is None and node.right is None:return value
  return visit(node.left,value)+visit(node.right,value)
 return visit(root,0)
'''
CAMEL='''def camelcase_matches(queries, pattern):
 answer=[]
 for query in queries:
  at=0
  for char in query:
   if at<len(pattern) and char==pattern[at]:at+=1
   elif char.isupper():break
  else:answer.append(at==len(pattern));continue
  answer.append(False)
 return answer
'''
CLIPS='''def minimum_video_clips(clips, time):
 clips.sort();used=0;covered=0;at=0
 while covered<time:
  farthest=covered
  while at<len(clips) and clips[at][0]<=covered:farthest=max(farthest,clips[at][1]);at+=1
  if farthest==covered:return -1
  covered=farthest;used+=1
 return used
'''
DIVISOR='''def alice_wins_divisor_game(n):
 return n%2==0
'''
ANCESTOR='''def maximum_ancestor_difference(root):
 def visit(node,low,high):
  if node is None:return high-low
  return max(visit(node.left,min(low,node.val),max(high,node.val)),visit(node.right,min(low,node.val),max(high,node.val)))
 return visit(root,root.val,root.val)
'''
ARITH='''def longest_arithmetic_subsequence(nums):
 dp=[{} for _ in nums];answer=2
 for j in range(len(nums)):
  for i in range(j):
   difference=nums[j]-nums[i];dp[j][difference]=dp[i].get(difference,1)+1;answer=max(answer,dp[j][difference])
 return answer
'''
RECOVER='''def recover_preorder_tree(traversal):
 stack=[];at=0
 while at<len(traversal):
  depth=0
  while at<len(traversal) and traversal[at]=='-':depth+=1;at+=1
  end=at
  while end<len(traversal) and traversal[end].isdigit():end+=1
  node=TreeNode(int(traversal[at:end]));at=end
  while len(stack)>depth:stack.pop()
  if stack:
   if stack[-1].left is None:stack[-1].left=node
   else:stack[-1].right=node
  stack.append(node)
 return stack[0]
'''


E=entry
BATCH={
1006:E('clumsy_factorial',[('n','int')],'int',['math','stacks'],['n is a positive integer.','Apply multiplication, truncating division, addition, and subtraction cyclically with normal precedence.'],[([4],'4*3/2+1 equals seven.'),([10],'The rotated operations evaluate to twelve.')],[[n] for n in [1,2,3,5,6,7,8,9,11,12,15,20,30,50]],CLUMSY,[CLUMSY.replace('stack.append(-value)','stack.append(value)'),CLUMSY.replace('return sum(stack)','return stack[-1]')],['Adds terms that should be subtracted.','Returns only the final precedence group.'],clumsy_oracle,random_clumsy,['Multiplication and division bind within the current term.','Keep signed completed terms on a stack.','Mutate the last term for * and /; append signed terms for + and -; sum at the end.','The stack exactly represents the expression after precedence grouping.'],'O(n)','O(n)',3),
1007:E('minimum_domino_rotations',[('tops','list[int]'),('bottoms','list[int]')],'int',['arrays','greedy'],['Both rows have equal nonzero length and values 1..6.','Return the fewest rotations making either row constant, or -1.'],[([[2,1,2,4,2,2],[5,2,6,2,3,2]],'Making every top a two needs two rotations.'),([[3,5,1,2,3],[3,6,3,3,4]],'Neither first-domino candidate occurs on every domino.')],[[a,b] for a,b in [([1],[1]),([1],[2]),([1,1],[1,1]),([1,2],[2,1]),([2,1,2],[1,2,1]),([1,2,3],[4,5,6]),([6,6,1],[1,2,6]),([3,3,3],[4,5,6]),([4,1,4,4],[4,4,2,3]),([1,2,1,2],[2,1,2,1]),([5,6,5],[5,5,5]),([2,3,4],[3,4,2]),([1,6,6,6],[6,1,2,3]),([2,2,3,2],[3,2,2,4])]],DOMINO,[DOMINO.replace('min(sum','max(sum'),DOMINO.replace("return -1 if answer==float('inf') else answer","return answer")],['Chooses the larger rotation count for a feasible candidate.','Leaks infinity instead of returning -1 when impossible.'],domino_oracle,random_domino,['Any common value must appear on both halves of the first domino.','Test only tops[0] and bottoms[0].','For a candidate reject any domino lacking it; otherwise count top and bottom rotations and take the minimum.','No other value can cover the first domino, so the two candidates are exhaustive.'],'O(n)','O(1)',5),
1008:E('bst_from_preorder',[('preorder','list[int]')],'TreeNode | None',['trees','binary-search-trees','recursion'],['Values are distinct and preorder represents a valid BST.','Return the reconstructed root.'],[([[8,5,1,7,10,12]],'Eight is root; the bounded recursive partitions create left 5 and right 10.'),([[1,3]],'The increasing preorder creates three as the right child.')],[[x] for x in [[1],[2,1],[1,2],[5,3,2,4,7,6,8],[10,5,1,7,40,50],[4,2,1,3,6,5,7],[3,2,1],[1,2,3],[7,3,1,5,9,8,10],[20,10,5,15,30,25,35],[2,1,4,3],[9,4,2,6,12,10,14],[6,5,4,3,2,1],[1,2,3,4,5,6]]],BST,[BST.replace('preorder[at]>limit','preorder[at]>=limit'),BST.replace('node.right=build(limit)','node.right=build(node.val)')],['Rejects a value equal to a bound even though distinct inputs make this mutation superficially plausible.','Applies the node value as an upper bound to the right subtree.'],bst_oracle,random_bst,['Preorder consumes root, then all values in its left subtree, then its right subtree.','Carry an exclusive upper bound and one shared input index.','If the next value exceeds the bound return null; otherwise consume it and build left with node value, right with inherited bound.','BST ordering and preorder make each next value belong to the earliest recursive frame whose bound admits it.'],'O(n)','O(height)',5),
1010:E('divisible_song_pairs',[('time','list[int]')],'int',['hash-maps','counting'],['Durations are positive integers.','Count index pairs i<j whose sum is divisible by 60.'],[([[30,20,150,100,40]],'The valid pairs are 30+150, 20+100, and 20+40.'),([[60,60,60]],'Every pair of three multiples of sixty is valid, giving three.')],[[x] for x in [[1],[60],[30,30],[20,40],[10,20,30],[1,59,61,119],[60,120,180],[15,45,75,105],[20,20,40,40],[30,90,150],[5,55,65,115],[10,50,70,110],[1,2,3,57,58,59],[100,20,40,80]]],SONGS,[SONGS.replace('counts[-remainder%60]','counts[remainder]'),SONGS.replace('counts[remainder]+=1','counts[remainder]-=1')],['Pairs equal remainders rather than complementary remainders.','Decrements counts so later pair totals become negative.'],song_oracle,random_songs,['Only remainders modulo sixty matter.','Before recording remainder r, add the number previously seen with remainder (-r)%60.','Maintain a 60-slot frequency array in one pass.','Counting before insertion enforces i<j and counts every complementary earlier duration once.'],'O(n)','O(1)',5),
1011:E('minimum_ship_capacity',[('weights','list[int]'),('days','int')],'int',['binary-search','greedy'],['Packages remain in input order and each day carries a contiguous prefix of what remains.','Return the minimum integral capacity finishing within days.'],[([[1,2,3,4,5,6,7,8,9,10],5],'Capacity fifteen partitions the ordered packages into five days and fourteen cannot.'),([[3,2,2,4,1,4],3],'Capacity six permits the three loads 3+2, 2+4, and 1+4.')],[[w,d] for w,d in [([1],1),([1,2],1),([1,2],2),([5,5,5],2),([3,2,2,4,1,4],2),([3,2,2,4,1,4],6),([10,1,1],2),([1,1,1,1],3),([7,2,5,10,8],2),([2,2,2,2,2],4),([9,8,7],3),([4,3,2,1],2),([1,2,3,1,1],4),([5,1,2,7,3],3)]],SHIP,[SHIP.replace('needed(middle)<=days','needed(middle)<days'),SHIP.replace('low,high=max(weights),sum(weights)','low,high=min(weights),sum(weights)')],['Requires strictly fewer than the allowed days.','Uses a lower bound that may not fit the heaviest package.'],ship_oracle,random_ship,['Feasibility is monotone: increasing capacity never increases required days.','Search between the heaviest package and total weight.','Greedily fill each day to compute days needed, then binary-search the first feasible capacity.','The greedy scan minimizes days for a fixed capacity, so its monotone predicate is exact.'],'O(n log(sum weights))','O(1)',5),
1012:E('count_repeated_digit_numbers',[('n','int')],'int',['digit-dp','combinatorics'],['1<=n and n may have up to ten decimal digits.','Count positive values at most n containing any repeated digit.'],[([20],'Only eleven has a repeated digit.'),([100],'The repeated-digit values through one hundred total ten.')],[[n] for n in [1,9,10,11,19,21,55,98,99,101,110,999,1000,4321]],REPEATED,[REPEATED.replace('str(n+1)','str(n)'),REPEATED.replace('return n-unique','return unique')],['Counts unique-digit values below n instead of at most n.','Returns the complement: numbers with all distinct digits.'],repeated_oracle,random_repeated,['Count distinct-digit numbers and subtract them from n.','Add all shorter lengths, then scan digits of n+1 while tracking used digits.','At each position count unused smaller choices times permutations of remaining digits; stop on repetition.','Every distinct-digit positive integer below n+1 is counted once by its first differing digit.'],'O(digits^2)','O(10)',8),
1014:E('best_sightseeing_score',[('values','list[int]')],'int',['arrays','dynamic-programming'],['At least two positive values are provided.','Maximize values[i]+values[j]+i-j over i<j.'],[([[8,1,5,2,6]],'Pair indices zero and two scores 8+5-2=11.'),([[1,2]],'The only pair scores two.')],[[x] for x in [[1,1],[1,2],[2,1],[5,1,1],[1,5,1],[1,1,5],[9,8,1],[2,7,3,4],[10,1,10],[3,3,3,3],[1,10,1,1,10],[6,2,4,8],[20,1,1,1,20],[4,9,2,6,3]]],SIGHT,[SIGHT.replace('values[j]-j','values[j]+j'),SIGHT.replace('best=max(best,values[j]+j)','best=max(best,values[j]-j)')],['Adds rather than subtracts the distance to the later spot.','Stores values[j]-j for a future left endpoint.'],sightseeing_oracle,random_sightseeing,['Rewrite the score as (values[i]+i)+(values[j]-j).','Maintain the best left contribution while scanning j.','Update the answer with best+values[j]-j, then include values[j]+j for future pairs.','The maintained maximum considers every legal earlier i without revisiting it.'],'O(n)','O(1)',5),
1015:E('smallest_repunit_length',[('k','int')],'int',['math','modular-arithmetic'],['k is positive.','Return the shortest all-ones decimal multiple length, or -1.'],[([1],'The one-digit number 1 is divisible by one.'),([3],'111 is divisible by three, so the minimum length is three.')],[[k] for k in [2,5,7,9,11,13,17,19,20,21,25,27,37,41]],REPUNIT,[REPUNIT.replace('remainder*10+1','remainder+1'),REPUNIT.replace('range(1,k+1)','range(1,k)')],['Updates the remainder without shifting the prior decimal digits.','Stops before checking the kth possible nonzero remainder state.'],repunit_oracle,random_repunit,['Build remainders rather than the enormous integers themselves.','Update r=(10r+1)%k for at most k steps.','Return the first zero; factors two or five make success impossible.','Among k remainder states, repetition without zero proves no later repunit can succeed.'],'O(k)','O(1)',5),
1016:E('contains_all_binary_values',[('s','str'),('n','int')],'bool',['strings','bit-manipulation'],['s contains only zero and one and n is positive.','Return whether every binary representation from 1 through n occurs as a substring.'],[(['0110',3],'The substrings include 1, 10, and 11.'),(['0110',4],'Binary 100 is absent, so the answer is false.')],[[s,n] for s,n in [('1',1),('0',1),('10',2),('11',2),('101',3),('111',3),('00110',3),('110100',4),('10101',5),('111111',6),('0001011100',7),('1000',8),('010101010',5),('1101011',6)]],QUERY,[QUERY.replace('range(n//2+1,n+1)','range(1,n+1)'),QUERY.replace("bin(value)[2:] in s","bin(value)[2:] not in s")],['Checks more values than needed for the optimized upper-half observation but remains correct, so it is not a valid shortcut.','Requires every representation to be absent.'],binary_query_oracle,random_binary_query,['If every value above n/2 occurs, smaller values occur as suffixes of those representations.','Check binary strings for values n//2+1 through n.','Use substring membership and stop at the first missing representation.','Each positive x<=n/2 is the suffix of either 2x or 2x+1, one of which is at most n.'],'O(n log n)','O(log n)',5),
1017:E('to_base_negative_two',[('n','int')],'str',['math','number-representation'],['n is nonnegative.','Return its canonical base -2 digits without leading zeros.'],[([2],'110 represents 4-2=2.'),([3],'111 represents 4-2+1=3.')],[[n] for n in [0,1,4,5,6,7,8,9,10,15,16,23,42,100]],NEGABINARY,[NEGABINARY.replace('divmod(n,-2)','divmod(n,2)'),NEGABINARY.replace("return ''.join(reversed(digits))","return ''.join(digits)")],['Uses positive base two division.','Returns least-significant digits first.'],negabinary_oracle,random_negabinary,['Repeated division works for negative bases when remainders are normalized to zero or one.','Use divmod(n,-2); if remainder is negative, increment quotient and add two to remainder.','Collect digits until zero and reverse them.','Each step preserves old n=(-2)*quotient+remainder with a valid digit.'],'O(log n)','O(log n)',5),
1018:E('binary_prefixes_divisible_by_five',[('nums','list[int]')],'list[bool]',['arrays','modular-arithmetic'],['nums contains binary digits.','Return one Boolean per prefix indicating divisibility by five.'],[([[0,1,1]],'Prefix values 0,1,3 yield true,false,false.'),([[1,0,1]],'Prefix values 1,2,5 end with a divisible prefix.')],[[x] for x in [[0],[1],[0,0],[1,0],[1,1],[1,0,1],[1,1,1],[0,1,0,1],[1,0,0,1],[1,1,0,0],[0,0,0,0],[1,0,1,0,1],[1,1,1,1,1],[0,1,1,0,1,0]]],PREFIX,[PREFIX.replace('%5','%3'),PREFIX.replace('value*2+bit','value+bit')],['Tests divisibility by three.','Fails to shift the prior binary prefix left.'],prefix_five_oracle,random_prefix,['Only the prefix remainder modulo five is needed.','Append a bit with remainder=(2*remainder+bit)%5.','Record whether each updated remainder is zero.','Modulo reduction preserves divisibility while keeping values bounded.'],'O(n)','O(n output)',3),
1019:E('next_greater_linked_values',[('head','ListNode | None')],'list[int]',['linked-lists','monotonic-stack'],['Return one value per node; use zero when no later strictly larger value exists.','The input list is not modified.'],[([[2,1,5]],'Five is the first larger value after both two and one.'),([[2,7,4,3,5]],'The answers are 7,0,5,5,0.')],[[x] for x in [[1],[1,2],[2,1],[1,1],[1,3,2],[3,1,2],[2,7,4,3,5],[5,4,3,2,1],[1,2,3,4,5],[2,2,3],[1,5,1,5],[9,1,8,2,7],[0,0,1],[4,1,6,2,8,3]]],NEXT,[NEXT.replace('values[stack[-1]]<value','values[stack[-1]]<=value'),NEXT.replace('answer[stack.pop()]=value','answer[stack.pop()]=values[i-1]')],['Treats equal values as strictly greater.','Stores the preceding value instead of the discovered greater value.'],next_node_oracle,random_list,['Convert the linked list to values so output positions are addressable.','Keep indices whose next greater value is unresolved in a decreasing stack.','When a new value is larger, pop and fill those answers; unresolved indices remain zero.','The first value that pops an index is exactly its earliest strictly larger successor.'],'O(n)','O(n)',5),
1021:E('remove_outer_parentheses',[('s','str')],'str',['strings','stacks'],['s is a nonempty valid parentheses string.','Remove the first and last character of each primitive component.'],[(['(()())(())'],'The primitives (()()) and (()) become ()() and (), concatenated as ()()().'),(['()()'],'Each primitive is (), so removing both outer characters leaves empty text.')],[[s] for s in ['()','(())','((()))','()()()','(()())','()(())','((())())','(()(()))','((()))()','()((()))','(())(())','((()()))','(()())()','()(()())']],OUTER,[OUTER.replace('if depth>1','if depth>0'),OUTER.replace("if char==')':depth-=1","if char=='(':depth-=1")],['Keeps opening parentheses at primitive depth zero.','Decrements depth after opening rather than closing parentheses.'],outer_oracle,random_parentheses,['Outermost parentheses are precisely those crossing depth zero and one.','Track nesting depth during one scan.','Increment before deciding to keep an opening; decide before decrementing a closing.','All characters at internal depth remain, while each primitive boundary is omitted.'],'O(n)','O(n)',3),
1022:E('sum_root_to_leaf_binary',[('root','TreeNode | None')],'int',['trees','recursion','depth-first-search'],['Every node value is zero or one and the tree is nonempty.','Interpret each root-to-leaf path as binary and sum the values.'],[([[1,0,1,0,1,0,1]],'Paths 100,101,110,111 sum to 22.'),([[0]],'The sole path represents zero.')],[[t] for t in [[1],[1,0],[1,None,1],[1,0,1],[0,1,1],[1,1,0,1],[1,0,0,1,1],[0,0,1,None,1],[1,1,1,1,1,1,1],[1,0,None,1],[0,1,None,0],[1,None,0,None,1],[1,0,1,None,None,1,0],[0,0,0,1,None,None,1]]],TREESUM,[TREESUM.replace('value*2+node.val','value+node.val'),TREESUM.replace('visit(node.left,value)+visit(node.right,value)','max(visit(node.left,value),visit(node.right,value))')],['Adds bits without binary place-value shifting.','Returns only the largest path instead of summing all leaves.'],binary_tree_sum_oracle,random_binary_tree,['Carry the binary prefix value down the tree.','Appending a bit changes value to 2*value+bit.','At leaves return the prefix; otherwise sum recursive child results.','Every leaf path is evaluated once with exactly its root-to-leaf bits.'],'O(n)','O(height)',3),
1023:E('camelcase_matches',[('queries','list[str]'),('pattern','str')],'list[bool]',['strings','two-pointers'],['Only lowercase letters may be inserted into pattern.','Return whether each query can be formed independently.'],[([['FooBar','FooBarTest','FootBall','FrameBuffer','ForceFeedBack'],'FB'],'FooBar, FootBall, and FrameBuffer insert only lowercase letters around F and B.'),([['FooBar','FooBarTest','FootBall','FrameBuffer','ForceFeedBack'],'FoBa'],'FooBar and FootBall match the longer mixed-case pattern.')],[[q,p] for q,p in [(['A'],'A'),(['a'],'A'),(['ABC'],'ABC'),(['ABC'],'AC'),(['abc'],'a'),(['abC'],'aC'),(['aBC'],'aC'),(['HelloWorld'],'HW'),(['HelloXWorld'],'HW'),(['CompetitiveProgramming'],'CP'),(['CodePracticeLab'],'CPL'),(['fooBar'],'fB'),(['FooBar','FoBa'],'FB'),(['TestCase','testCase'],'TC')]],CAMEL,[CAMEL.replace('elif char.isupper():break','elif char.islower():break'),CAMEL.replace('at==len(pattern)','at<=len(pattern)')],['Rejects unmatched lowercase insertions instead of uppercase letters.','Accepts queries that consume only a prefix of the pattern.'],camel_oracle,random_camel,['Pattern characters must appear in order, and every extra query character must be lowercase.','Use a pointer into pattern for each query.','Advance on a match; reject an unmatched uppercase; accept only after consuming all pattern characters.','Those conditions are exactly insertion of lowercase characters without deleting or changing pattern.'],'O(total query characters)','O(output)',5),
1024:E('minimum_video_clips',[('clips','list[list[int]]'),('time','int')],'int',['greedy','intervals'],['Clips have integer endpoints and target time is positive.','Return the fewest clips covering every instant from zero through time, or -1.'],[([[[0,2],[4,6],[8,10],[1,9],[1,5],[5,9]],10],'Choose 0-2, 1-9, and 8-10 for three clips.'),([[[0,1],[1,2]],5],'Coverage stops at two, so reaching five is impossible.')],[[c,t] for c,t in [([[0,1]],1),([[1,2]],2),([[0,2]],1),([[0,1],[1,2]],2),([[0,1],[2,3]],3),([[0,4],[2,8]],8),([[0,2],[1,5],[4,7]],7),([[0,3],[3,6],[6,9]],9),([[0,5],[0,3],[3,10]],10),([[1,5],[0,2],[2,6]],6),([[0,1],[0,2],[2,4]],4),([[0,6],[1,2],[2,3]],5),([[0,2],[2,3],[3,5],[1,4]],5),([[0,1],[1,4],[4,8],[2,7]],8)]],CLIPS,[CLIPS.replace('clips[at][0]<=covered','clips[at][0]<covered'),CLIPS.replace('farthest=max(farthest,clips[at][1])','farthest=clips[at][1]')],['Rejects clips beginning exactly where current coverage ends.','Keeps the last candidate rather than the farthest-reaching candidate.'],clips_oracle,random_clips,['At each boundary, any next clip must start no later than current coverage.','Among all such clips, extend to the farthest end.','Sort by start, scan all currently available clips, commit one extension, and repeat.','Choosing a shorter available extension can never reduce the clips needed later.'],'O(n log n)','O(n)',5),
1025:E('alice_wins_divisor_game',[('n','int')],'bool',['dynamic-programming','math'],['Players choose a proper positive divisor and subtract it; no move loses.','Return whether Alice wins with optimal play.'],[([2],'Alice subtracts one and leaves one, so she wins.'),([3],'The only move leaves two, a winning position for Bob.')],[[n] for n in [1,4,5,6,7,8,9,10,11,12,15,16,21,100]],DIVISOR,[DIVISOR.replace('n%2==0','n%2==1'),DIVISOR.replace('return n%2==0','return n>1')],['Declares odd positions winning instead of even ones.','Assumes every value above one is winning.'],divisor_oracle,random_divisor,['Experimenting with the game reveals parity is the complete state invariant.','Even n can subtract one and hand over odd; every divisor of odd n is odd, leaving even.','Return true exactly when n is even.','Induction makes odd positions losing and even positions winning from the base n=1.'],'O(1)','O(1)',3),
1026:E('maximum_ancestor_difference',[('root','TreeNode | None')],'int',['trees','recursion','depth-first-search'],['The tree is nonempty and values are nonnegative integers.','Maximize the absolute difference between a node and any descendant.'],[([[8,3,10,1,6,None,14,None,None,4,7,13]],'Ancestor eight and descendant one differ by seven.'),([[1,None,2,None,0,3]],'Along the right-descending path, ancestor two and descendant zero differ by two.')],[[t] for t in [[1],[1,2],[2,1],[5,1,9],[5,9,1],[8,3,10,1,6],[0,100],[100,None,0],[4,2,6,1,3,5,7],[10,5,None,1],[1,None,10,None,20],[7,7,7],[20,10,30,5,15,25,35],[3,1,4,None,2]]],ANCESTOR,[ANCESTOR.replace('high-low','high+low'),ANCESTOR.replace('min(low,node.val)','max(low,node.val)')],['Adds path extremes instead of taking their difference.','Updates the path minimum using maximum.'],ancestor_oracle,random_ancestor,['For each root-to-node path, only its minimum and maximum values matter.','Carry those two extremes through DFS.','At null children return high-low; update extremes at each node and maximize both branches.','Every ancestor-descendant difference lies within a path range, whose endpoints themselves form a valid pair.'],'O(n)','O(height)',5),
1027:E('longest_arithmetic_subsequence',[('nums','list[int]')],'int',['dynamic-programming','hash-maps'],['At least two integers are provided.','Return the longest order-preserving subsequence with constant adjacent difference.'],[([[3,6,9,12]],'All four values form an arithmetic sequence with difference three.'),([[9,4,7,2,10]],'Four, seven, and ten form length three.')],[[x] for x in [[1,2],[2,1],[1,1],[1,2,3],[3,2,1],[1,3,5,7],[1,2,4,8],[7,7,7,7],[1,5,9,13,2],[20,1,15,3,10,5,8],[0,-1,-2,-3],[-5,0,5,10],[1,4,7,2,5,8],[3,3,6,9,12]]],ARITH,[ARITH.replace('nums[j]-nums[i]','abs(nums[j]-nums[i])'),ARITH.replace("get(difference,1)+1","get(difference,0)+1")],['Loses the sign of the common difference.','Starts a new pair at length one instead of two.'],arithmetic_oracle,random_arithmetic,['A subsequence ending at j is identified by its final difference.','Store the best length for every (ending index,difference).','Extend dp[i][difference], defaulting a new pair to length two.','Every arithmetic subsequence has a unique prior endpoint and difference captured by this transition.'],'O(n^2)','O(n^2)',8),
1028:E('recover_preorder_tree',[('traversal','str')],'TreeNode | None',['trees','stacks','parsing'],['Dash count before a value is its depth; a single child is always left.','Return the reconstructed binary tree root.'],[(['1-2--3--4-5--6--7'],'Depth changes attach 3 and 4 under 2, then 6 and 7 under 5.'),(['1-401--349---90--88'],'The depth markers reconstruct the left chain and sibling 88.')],[[s] for s in ['1','1-2','1-2--3','1-2-3','10-5-15','1-2--3-4','1-2--3--4','1-2---3','8-5--1--7-10--12','1-2--3---4-5--6','9-8--7---6----5','1-2--3--4-5','100-20--3--40-500','7-3--1---2--5-9--8--10']],RECOVER,[RECOVER.replace('while len(stack)>depth','while len(stack)>=depth'),RECOVER.replace("if stack[-1].left is None","if stack[-1].right is None")],['Pops the parent frame itself at the target depth.','Tests the right slot first and attaches initial children incorrectly.'],recover_oracle,random_recover,['Depth tells exactly which ancestor receives the next preorder node.','Maintain the current root-to-last-node stack.','Pop to the stated depth, attach to the parent’s left empty slot then right, and push the node.','Preorder and the single-child-left rule make the attachment choice deterministic.'],'O(n)','O(height)',8),
}

BATCH[1008]['adapter']='treenode'
BATCH[1007]['wrong'][0]='''def minimum_domino_rotations(tops, bottoms):
 return 0
'''
BATCH[1007]['wrong_reasons'][0]='Assumes the rows are already aligned and never counts required rotations or impossibility.'
BATCH[1007]['wrong'][1]=DOMINO.replace('answer=min(cost(tops[0]),cost(bottoms[0]))','answer=cost(tops[0])')
BATCH[1007]['wrong_reasons'][1]='Tests only the top value of the first domino and misses solutions using its bottom value.'
BATCH[1008]['wrong'][0]=BST.replace('node.left=build(node.val)','node.left=build(limit)')
BATCH[1008]['wrong_reasons'][0]='Uses the inherited bound for the left subtree and admits values that belong on the right.'
BATCH[1016]['wrong'][0]=QUERY.replace('range(n//2+1,n+1)','range(n//2+2,n+1)')
BATCH[1016]['wrong_reasons'][0]='Skips the smallest value in the sufficient upper-half range.'
BATCH[1019]['params'][0]=('head','ListNode | None','listnode')
for pid in (1022,1026):BATCH[pid]['params'][0]=('root','TreeNode | None','treenode')
BATCH[1028]['adapter']='treenode'
BATCH[1028]['boundaries']=[[('1-2--3---4' if args[0]=='1-2---3' else args[0])] for args in BATCH[1028]['boundaries']]
BATCH[1024]['wrong'][1]=CLIPS.replace(
 'farthest=max(farthest,clips[at][1])',
 'farthest=farthest if farthest>covered else clips[at][1]',
)
BATCH[1024]['wrong_reasons'][1]='Commits to the first extending clip instead of the farthest-reaching available clip.'
BATCH[1027]['wrong'][0]=ARITH.replace(
 'difference=nums[j]-nums[i]',
 'difference=nums[j]//nums[i] if nums[i] else 0',
)
BATCH[1027]['wrong_reasons'][0]='Groups pairs by integer ratio instead of their additive difference.'
BATCH[1028]['wrong'][0]=RECOVER.replace('depth+=1;at+=1','depth=1;at+=1')
BATCH[1028]['wrong_reasons'][0]='Treats every non-root node as depth one regardless of its dash count.'
BATCH[1017]['sample_contract_adapter']={
 'source_sample':'Input n = 2 → Output "110" Explantion: (-2)^2 + (-2)^1 = 2.',
 'arguments':[2], 'expected':'110',
 'reason':'The workbook appended a misspelled explanation to the output literal; the intended output is unambiguous.',
}
