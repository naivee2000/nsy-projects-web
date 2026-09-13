"""BST deletion shapes, directed circular cycles, minimax and repeated subsequences."""
from .import_batch_002 import positions, flatten
from .import_batch_003 import entry
from .import_batch_019 import complete_bst_oracle
from .import_batch_039 import chain


def delete_oracle(args):
    values = sorted(value for value in positions(args[0]).values() if value != args[1])
    return complete_bst_oracle([values])


def cycle_oracle(args):
    nums = args[0]
    for start in range(len(nums)):
        seen, route, index = {}, [], start
        while index not in seen:
            seen[index] = len(route)
            route.append(index)
            index = (index+nums[index]) % len(nums)
        cycle = route[seen[index]:]
        if len(cycle)>1 and len({nums[i]>0 for i in cycle})==1:
            return True
    return False


def game_oracle(args):
    """Bottom-up retrograde table, independent of recursive short-circuit search."""
    maximum, target = args
    if target<=0:
        return True
    if maximum*(maximum+1)//2<target:
        return False
    size = 1<<maximum
    totals = [0]*size
    for mask in range(1,size):
        bit = mask & -mask
        totals[mask] = totals[mask ^ bit]+bit.bit_length()
    winning = bytearray(size)
    for mask in range(size-1,-1,-1):
        needed = target-totals[mask]
        if needed<=0:
            continue
        available = (size-1)^mask
        while available:
            bit = available & -available
            available ^= bit
            if bit.bit_length()>=needed or not winning[mask | bit]:
                winning[mask] = 1
                break
    return bool(winning[0])


def repetition_oracle(args):
    s1,n1,s2,n2 = args
    source = s1*n1
    answer = 0
    for count in range(1,len(source)//(len(s2)*n2)+1):
        cursor = 0
        for char in s2*(n2*count):
            found = source.find(char,cursor)
            if found<0:
                break
            cursor = found+1
        else:
            answer = count
            continue
        break
    return answer


def random_delete(rng):
    values = rng.sample(range(-30,31),rng.randint(0,20))
    mapping = {}
    for value in values:
        path = ()
        while path in mapping:
            path += (int(value>mapping[path]),)
        mapping[path] = value
    key = rng.choice(values) if values and rng.random()<.7 else rng.randint(-35,35)
    return [flatten(mapping),key]


def random_cycle(rng):
    return [[rng.choice([*range(-12,0),*range(1,13)]) for _ in range(rng.randint(1,12))]]


def random_game(rng):
    return [rng.randint(1,9),rng.randint(0,55)]


def random_repetition(rng):
    return [''.join(rng.choice('abc') for _ in range(rng.randint(1,6))),rng.randint(1,8),
            ''.join(rng.choice('abc') for _ in range(rng.randint(1,6))),rng.randint(1,8)]


DELETE = '''\
def delete_bst_node(root, key):
    parent,node = None,root
    while node is not None and node.val!=key:
        parent = node
        node = node.left if key<node.val else node.right
    if node is None:
        return root
    if node.left is not None and node.right is not None:
        successor_parent,successor = node,node.right
        while successor.left is not None:
            successor_parent,successor = successor,successor.left
        node.val = successor.val
        parent,node = successor_parent,successor
    replacement = node.left if node.left is not None else node.right
    if parent is None:
        return replacement
    if parent.left is node:
        parent.left = replacement
    else:
        parent.right = replacement
    return root
'''

CYCLE = '''\
def has_circular_array_loop(nums):
    size = len(nums)
    def advance(index,forward):
        if index<0 or nums[index]==0 or (nums[index]>0)!=forward:
            return -1
        following = (index+nums[index])%size
        return -1 if following==index else following
    for start in range(size):
        if nums[start]==0:
            continue
        forward = nums[start]>0
        slow = advance(start,forward)
        fast = advance(advance(start,forward),forward)
        while slow>=0 and fast>=0:
            if slow==fast:
                return True
            slow = advance(slow,forward)
            fast = advance(advance(fast,forward),forward)
        current = start
        while nums[current]!=0 and (nums[current]>0)==forward:
            following = (current+nums[current])%size
            nums[current] = 0
            current = following
    return False
'''

GAME = '''\
def can_force_win(max_choosable_integer, desired_total):
    from functools import cache
    maximum = max_choosable_integer
    total = maximum*(maximum+1)//2
    if desired_total<=0:
        return True
    if total<desired_total:
        return False
    if total==desired_total:
        return maximum%2==1
    @cache
    def win(mask,needed):
        for value in range(maximum,0,-1):
            bit = 1<<(value-1)
            if mask & bit:
                continue
            if value>=needed or not win(mask | bit,needed-value):
                return True
        return False
    return win(0,desired_total)
'''

REPETITION = '''\
def count_repeated_subsequences(s1, n1, s2, n2):
    if not set(s2)<=set(s1):
        return 0
    offset = completed = blocks = 0
    seen = {0:(0,0)}
    while blocks<n1:
        for char in s1:
            if char==s2[offset]:
                offset += 1
                if offset==len(s2):
                    offset = 0
                    completed += 1
        blocks += 1
        if offset in seen:
            earlier,matched = seen[offset]
            period = blocks-earlier
            jumps = (n1-blocks)//period
            blocks += jumps*period
            completed += jumps*(completed-matched)
        else:
            seen[offset] = (blocks,completed)
    return completed//n2
'''


BATCH = {
450: entry('delete_bst_node',[('root','TreeNode | None'),('key','int')],'TreeNode | None',
    ['trees','binary-search','recursion'],
    ['0 <= node count <= 10,000; all values are unique integers between -100,000 and 100,000.',
     'The input is a valid BST and -100,000 <= key <= 100,000. Remove key if it exists; otherwise keep all values.',
     'Return a TreeNode root or None. Any valid BST containing exactly the remaining values is accepted; balancing is not required.'],
    [([[5,3,6,2,4,None,7],3],'Remove 3 and retain exactly 2,4,5,6,7 in inorder. The shown tree is one valid arrangement; predecessor- or successor-based deletion shapes are also accepted.'),
     ([[2,1,3],2],'Deleting the root changes the root reference. Both 3 with left child 1 and 1 with right child 3 are valid.')],
    [[tree,key] for tree,key in [([],0),([],1),([1],1),([1],2),([1,None,2],1),([2,1],2),
      ([2,1,3],1),([2,1,3],3),([2,1,3],0),([4,2,6,1,3,5,7],4),
      ([5,3,9,2,4,7,10,None,None,None,None,6,8,None,11],5),
      ([-100000,None,100000],-100000)]],
    DELETE,[DELETE.replace('successor_parent,successor = node,node.right','return root\n        successor_parent,successor = node,node.right'),
            DELETE.replace('replacement = node.left if node.left is not None else node.right','replacement = node.left')],
    ['Handles simple cases but leaves a two-child target undeleted.', 'Drops a surviving right subtree when unlinking a node.'],
    delete_oracle,random_delete,
    ['Deleting a BST node has zero-child, one-child, and two-child cases.',
     'For two children, use the inorder successor or predecessor, then unlink its old position.',
     'Search while retaining the parent. For two children copy the successor value, then remove that successor using its right child.',
     'Reconnect the parent to the surviving child, or return that child as the new root. Iteration handles a 10,000-node chain without recursion overflow.'],
    'The smallest value in the right subtree can replace a two-child target without breaking BST '
    'ordering. That successor has no left child, so unlinking it is a one-child operation. Retaining '
    'the parent permits root and non-root removal with constant auxiliary space. A predecessor-based '
    'solution is equally correct. The judge checks strict BST ordering and exactly the surviving '
    'integer values, not one reference shape or a balance requirement. The oracle independently '
    'filters the value set and labels a complete tree in inorder.',
    'O(height)','O(1)',difficulty=6,
    stress=[([chain(list(range(10000))),0],complete_bst_oracle([list(range(1,10000))])),
            ([chain(list(range(9999,-1,-1)),False),5000],complete_bst_oracle([[n for n in range(10000) if n!=5000]]))]),
457: entry('has_circular_array_loop',[('nums','list[int]')],'bool',['arrays','two-pointers','graphs'],
    ['1 <= nums.length <= 5,000; -1,000 <= nums[i] <= 1,000 and every original entry is nonzero.',
     'Move from i to (i+nums[i]) modulo n. A valid cycle uses at least two distinct indices and only one direction.',
     'A same-index jump is invalid even if its magnitude exceeds n. Input mutation is allowed for the O(1)-extra-space follow-up.'],
    [([[2,-1,1,2,2]],'Indices 0→2→3→0 form a length-three cycle whose jumps are all positive.'),
     ([[1,-1]],'The two positions repeat, but one jump is positive and one negative. This mixed-direction cycle is invalid.')],
    [[nums] for nums in ([1],[-1],[1000],[-1000],[2,2],[1,1],[-1,-1],[-2,1,-1,-2,-2],
                        [-1,-2,-3,-4,-5,6],[1,-1,5,1,4],[3,1,2],[1,1,-1])],
    CYCLE,[CYCLE.replace('return -1 if following==index else following','return following'),
           CYCLE.replace(' or (nums[index]>0)!=forward','')],
    ['Accepts a self-loop as a multi-index cycle.', 'Finds cycles without enforcing a consistent jump direction.'],
    cycle_oracle,random_cycle,
    ['This is a directed graph with exactly one outgoing jump per index, plus direction and cycle-length rules.',
     'Use slow/fast pointers on same-direction edges; reject self edges and stop at invalid or previously cleared entries.',
     'After a failed search, walk its same-direction path again and mark those entries zero. Preserve the next index before clearing.',
     'Cleared paths cannot contain a valid cycle. They are visited only a constant number of times, giving linear time and constant extra space.'],
    'Floyd pointers detect a repeated position without storing a visited set, but the next-step '
    'function must reject direction changes and self-jumps. After failure, clear the explored '
    'same-direction path using zero, which cannot occur in original inputs. Later searches stop at '
    'cleared nodes. The independent oracle follows every start, extracts the eventual cycle, and '
    'then checks its length and signs. Negative modulo results still designate valid circular indices.',
    'O(n)','O(1)',difficulty=6,
    stress=[([[1]*5000],True),([[-1]*5000],True),([[1]*4999+[-1]],False)]),
464: entry('can_force_win',[('max_choosable_integer','int'),('desired_total','int')],'bool',
    ['dynamic-programming','recursion','game-theory'],
    ['1 <= max_choosable_integer <= 20; 0 <= desired_total <= 300.',
     'Two optimal players alternate choosing an unused integer from 1 through the maximum. Choices are shared and cannot be reused.',
     'The player reaching or exceeding the target wins. Target zero is already a first-player win; an unreachable target returns False.'],
    [([10,11],'Whatever the first pick x, the second player can choose 11-x and reach 11. The first player cannot force a win.'),
     ([4,6],'Pick 1 first. Any opponent pick leaves an unused number that lets the first player reach 6 on the next turn.')],
    [[n,t] for n,t in ((1,0),(1,1),(1,2),(2,3),(3,6),(4,10),(5,15),(5,16),(4,4),(4,7),(6,10),(8,18))],
    GAME,["def can_force_win(max_choosable_integer,desired_total):\n    if desired_total<=0: return True\n    first=True\n    for value in range(max_choosable_integer,0,-1):\n        desired_total-=value\n        if desired_total<=0: return first\n        first=not first\n    return False\n",
          "def can_force_win(max_choosable_integer,desired_total):\n    return desired_total==0 or desired_total%(max_choosable_integer+1)!=0\n"],
    ['Assumes both players should always choose the largest remaining number.', 'Uses the reusable-number game formula even though choices cannot be reused.'],
    game_oracle,random_game,
    ['Winning means there exists a move that wins immediately or leaves the opponent unable to force a win.',
     'The set of already-used numbers completely identifies the remaining choices and running total.',
     'Memoize win(used_mask,needed). For each unused value, succeed if it reaches needed or the next state is losing.',
     'Reject targets larger than the total sum before searching. The recursion depth is at most 20 because every move consumes a number.'],
    'Minimax examines every legal response, not just a greedy line of play. A used-number mask '
    'determines both the available pool and remaining target, so there are at most 2^m states. '
    'Each tries at most m moves. An unreachable total is not a win merely because the other player '
    'has no move. If the target equals the sum of all numbers, exactly m turns are required and '
    'parity determines the winner. The oracle fills a separate retrograde table bottom-up.',
    'O(m*2^m)','O(2^m)',difficulty=7,
    stress=[([20,210],False),([19,190],True),([20,300],False),([20,21],False),([20,20],True),
            ([20,100],True),([20,150],False)]),
466: entry('count_repeated_subsequences',[('s1','str'),('n1','int'),('s2','str'),('n2','int')],'int',
    ['strings','dynamic-programming','cycle-detection'],
    ['1 <= len(s1), len(s2) <= 100; lowercase English letters only; 1 <= n1,n2 <= 1,000,000.',
     'Find the largest m such that s2 repeated n2*m times is a subsequence of s1 repeated n1 times.',
     'Matching characters need not be contiguous and may cross source-block boundaries. Return a count, not the expanded strings.'],
    [(['acb',4,'ab',2],'Each acb supplies one subsequence ab. Four ab matches form two groups of (ab repeated twice), so return 2.'),
     (['ab',3,'ba',1],'In ababab, baba is a subsequence crossing block boundaries. Two ba copies fit, but a third lacks a final a.')],
    [[a,b,c,d] for a,b,c,d in [('a',1,'a',1),('a',1,'b',1),('a',2,'a',3),('ab',1,'ba',1),
      ('ab',2,'ba',1),('aaa',2,'aa',1),('aaa',2,'aa',2),('abc',2,'ac',1),
      ('abc',3,'cab',1),('acb',1,'acb',1),('baba',3,'ab',2),('ab',4,'aab',1)]],
    REPETITION,["def count_repeated_subsequences(s1,n1,s2,n2):\n    offset=count=0\n    for char in s1:\n        if char==s2[offset]:\n            offset+=1\n            if offset==len(s2):\n                offset=0\n                count+=1\n    return count*n1//n2\n",
                REPETITION.replace('return completed//n2','return completed')],
    ['Discards a partial target match at every source-block boundary.', 'Counts copies of s2 instead of complete groups containing n2 copies.'],
    repetition_oracle,random_repetition,
    ['After a source block, future matching depends only on the next character needed in s2.',
     'Record the target offset and completed target copies at each source-block boundary.',
     'When an offset repeats, compute the block period and match gain, skip whole periods, then scan the short remainder.',
     'Greedy subsequence matching maximizes completed target copies; divide that number by n2 only after all source blocks.'],
    'Matching the earliest available character never harms a later subsequence completion. There '
    'are only len(s2) boundary offsets. A repeated offset means subsequent source blocks repeat '
    'the same transition cycle and target-copy gain, so whole cycles can be skipped arithmetically. '
    'The unmatched prefix must survive source-block boundaries. At most O(len(s2)) blocks need '
    'literal scanning before cycle skipping and the final remainder; no million-fold string '
    'expansion is needed. The oracle independently searches expanded small targets in small sources.',
    'O(len(s1)*len(s2))','O(len(s2))',difficulty=8,
    stress=[(['a'*100,10**6,'a',1],10**8),(['ab',10**6,'ba',3],333333),
            (['ab',10**6,'b'*99+'a',1],10101),(['ab'*50,10**6,'ab'*50,10**6],1)]),
}
BATCH[450]['params'] = [('root','TreeNode | None','treenode'),('key','int','raw')]
BATCH[450]['adapter'] = 'treenode'
BATCH[450]['comparator'] = 'bst_delete'
BATCH[466]['prerequisites'] = ['strings','dynamic-programming']
