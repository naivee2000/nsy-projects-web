"""First slice of workbook batch 127."""

from bisect import bisect_left

from .import_batch_055 import entry


def partition_oracle(args):
    nums, limit = args; ordered = sorted(nums); groups = 0; index = 0
    while index < len(ordered):
        groups += 1; start = ordered[index]; index += 1
        while index < len(ordered) and ordered[index] - start <= limit: index += 1
    return groups


def random_partition(rng):
    return [[rng.randint(0, 30) for _ in range(rng.randint(1, 25))], rng.randint(0, 15)]


def replace_oracle(args):
    nums, operations = args; result = list(nums)
    for old, new in operations:
        result[result.index(old)] = new
    return result


def random_replace(rng):
    n = rng.randint(1, 12); nums = rng.sample(range(1, 100), n); current = list(nums); operations = []
    for _ in range(rng.randint(1, 12)):
        old = rng.choice(current)
        while True:
            new = rng.randint(101, 300)
            if new not in current: break
        current[current.index(old)] = new; operations.append([old, new])
    return [nums, operations]


def jump_oracle(args):
    nums, costs = args; dp = [10**18] * len(nums); dp[0] = 0
    for right in range(1, len(nums)):
        for left in range(right):
            middle = nums[left + 1:right]
            legal = ((nums[left] <= nums[right] and all(value < nums[left] for value in middle)) or
                     (nums[left] > nums[right] and all(value >= nums[left] for value in middle)))
            if legal: dp[right] = min(dp[right], dp[left] + costs[right])
    return dp[-1]


def random_jump(rng):
    n = rng.randint(2, 16)
    return [[rng.randint(0, 20) for _ in range(n)], [rng.randint(1, 20) for _ in range(n)]]


def password_oracle(args):
    text = args[0]
    return (len(text) >= 8 and any(c.islower() for c in text) and any(c.isupper() for c in text)
            and any(c.isdigit() for c in text) and any(c in '!@#$%^&*()-+' for c in text)
            and all(a != b for a, b in zip(text, text[1:])))


def random_password(rng):
    alphabet = 'abAB09!@#_-+'
    return [''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 20)))]


def pairs_oracle(args):
    spells, potions, success = args
    return [sum(spell * potion >= success for potion in potions) for spell in spells]


def random_pairs(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 15))],
            [rng.randint(1, 30) for _ in range(rng.randint(1, 15))], rng.randint(1, 400)]


PARTITION = '''\
def minimum_bounded_difference_groups(nums,k):
    ordered=sorted(nums);answer=0;index=0
    while index<len(ordered):
        answer+=1;smallest=ordered[index];index+=1
        while index<len(ordered) and ordered[index]-smallest<=k:index+=1
    return answer
'''

REPLACE = '''\
def apply_array_replacements(nums,operations):
    result=list(nums);positions={value:index for index,value in enumerate(result)}
    for old,new in operations:
        index=positions.pop(old);result[index]=new;positions[new]=index
    return result
'''

JUMP = '''\
def minimum_monotonic_jump_cost(nums,costs):
    dp=[float('inf')]*len(nums);dp[0]=0;non_increasing=[];increasing=[]
    for index,value in enumerate(nums):
        while non_increasing and nums[non_increasing[-1]]<=value:
            previous=non_increasing.pop();dp[index]=min(dp[index],dp[previous]+costs[index])
        while increasing and nums[increasing[-1]]>value:
            previous=increasing.pop();dp[index]=min(dp[index],dp[previous]+costs[index])
        non_increasing.append(index);increasing.append(index)
    return dp[-1]
'''

PASSWORD = '''\
def is_strong_password(password):
    special='!@#$%^&*()-+'
    return (len(password)>=8 and any(char.islower() for char in password) and any(char.isupper() for char in password) and any(char.isdigit() for char in password) and any(char in special for char in password) and all(left!=right for left,right in zip(password,password[1:])))
'''

PAIRS = '''\
def successful_spell_potion_counts(spells,potions,success):
    from bisect import bisect_left
    ordered=sorted(potions);count=len(ordered);answer=[]
    for spell in spells:
        required=(success+spell-1)//spell
        answer.append(count-bisect_left(ordered,required))
    return answer
'''


BATCH = {
    2294: entry('minimum_bounded_difference_groups',[('nums','list[int]'),('k','int')],'int',['arrays','greedy','sorting'],['Partition all elements into subsequences; because order within each chosen group is inherited, only its minimum and maximum values affect validity.','Every group must satisfy maximum-minimum<=k.','Return the minimum number of groups.'],[([[3,6,1,2,5],2],'Sorted values 1,2,3 form one group and 5,6 another, so two groups suffice.'),([[1,2,3],0],'With zero tolerance, every distinct value needs its own group, giving three.')],[[n,k] for n,k in [([1],0),([3,6,1,2,5],2),([1,2,3],0),([1,1,1],0),([1,2,3],2),([1,5,9],3),([4,3,2,1],1),([10,20,30,40],15),([2,2,5,5],0),([1,4,7,10],6),([0,100],99),([5,6,7,20,21],2),([3,1,4,1,5],1),([8,2,6,4],3)]],PARTITION,[PARTITION.replace('<=k','<k'),PARTITION.replace('ordered=sorted(nums)','ordered=nums')],['Requires maximum-minimum to be strictly less than k and splits equality cases.','Groups in original order instead of sorting values to minimize ranges.'],partition_oracle,random_partition,['Sort values so each optimal group can be represented as one consecutive sorted block.','Start a group at the smallest unassigned value and include everything no more than k above it.','Repeat from the next uncovered sorted value and count groups.','Any group containing the smallest remaining value cannot extend beyond smallest+k; taking every eligible value cannot hurt and leaves the fewest possible elements.'],'O(n log n)','O(n)',5),
    2295: entry('apply_array_replacements',[('nums','list[int]'),('operations','list[list[int]]')],'list[int]',['arrays','hash maps','simulation'],['Initial values are distinct.','Each operation [old,new] replaces the currently present old value, and new is not currently present.','Return the final array in its original positional order.'],[([[1,2,4,6],[[1,3],[4,7],[6,1]]],'The replacements update positions to produce [3,2,7,1].'),([[1,2],[[1,3],[3,4]]],'Both operations affect the same position in sequence, producing [4,2].')],[[n,o] for n,o in [([1],[[1,2]]),([1,2,4,6],[[1,3],[4,7],[6,1]]),([1,2],[[1,3],[3,4]]),([5,6],[[6,7]]),([1,2,3],[[2,4]]),([1,2,3],[[1,4],[2,5],[3,6]]),([10,20,30],[[20,40],[40,50]]),([7,8,9],[[7,10],[9,7]]),([1,3,5,7],[[3,4],[7,8]]),([100],[[100,1],[1,2],[2,3]]),([2,4,6],[[4,5],[2,4]]),([9,1,8],[[1,2],[8,1]]),([5,10,15],[[10,20]]),([3,2,1],[[3,4],[1,3]])]],REPLACE,[REPLACE.replace('positions[new]=index',''),REPLACE.replace('result[index]=new','result.append(new)')],['Does not index the new value, so a later operation cannot replace it.','Appends replacement values instead of preserving the original position.'],replace_oracle,random_replace,['A value-to-index map locates every currently present value in constant expected time.','For each operation, remove old from the map, write new at that index, and map new to the same index.','Maintain both the result list and positions dictionary through all operations.','The invariant maps every current array value to its unique position, making each sequential replacement exact.'],'O(n+operations)','O(n)',5),
    2297: entry('minimum_monotonic_jump_cost',[('nums','list[int]'),('costs','list[int]')],'int',['arrays','monotonic stacks','dynamic programming'],['From i to later j, jump when nums[i]<=nums[j] and every intermediate value is below nums[i], or when nums[i]>nums[j] and every intermediate value is at least nums[i].','Starting at index zero costs nothing; landing at j adds costs[j].','Return the minimum cost to reach the last index.'],[([[3,2,4,4,1],[3,7,6,4,2]],'The best legal jump sequence reaches the last index with total landing cost eight.'),([[0,1,2],[1,1,1]],'A direct jump from zero to two is legal and costs one.')],[[n,c] for n,c in [([1,2],[0,5]),([3,2,4,4,1],[3,7,6,4,2]),([0,1,2],[1,1,1]),([3,2,1],[0,2,3]),([1,1,1],[0,5,2]),([1,3,2],[0,1,10]),([5,1,4,2],[0,3,2,1]),([2,5,1,6],[0,4,3,2]),([4,3,5,2,6],[0,2,8,1,4]),([1,2,1,2],[0,5,1,5]),([9,7,8,6],[0,3,2,4]),([0,10,0],[0,1,9]),([6,2,5,1,4],[0,7,3,2,6]),([2,2,3,1],[0,4,2,5])]],JUMP,[JUMP.replace('<=value','<value'),JUMP.replace('>value','>=value')],['Uses a strict comparison in the upward monotonic stack and mishandles equal values.','Pops equal values in the downward stack and violates the second jump rule.'],jump_oracle,random_jump,['The only useful predecessors are exposed by two monotonic stacks for the two jump inequalities.','When a new value arrives, popped stack nodes and the remaining top each have a legal direct jump to it.','Relax dp[index] from every exposed predecessor on both stacks, then push the index.','Any predecessor hidden deeper is blocked by a nearer value unless it becomes exposed through popping, so all and only potentially optimal jump edges are relaxed.'],'O(n)','O(n)',7),
    2299: entry('is_strong_password',[('password','str')],'bool',['strings'],['A strong password has length at least eight and contains lowercase, uppercase, digit, and one of !@#$%^&*()-+.','No two adjacent characters may be identical.','Return true only when every condition holds.'],[(['IloveLe3tcode!'],'The password is long enough, covers all four character classes, and has no repeated neighbors.'),(['Me+You--IsMyDream'],'The adjacent two hyphens violate the no-identical-neighbors rule.')],[[x] for x in ['IloveLe3tcode!','Me+You--IsMyDream','Aa1!aaaa','Aa1!aaaaa','abcdefghi','ABCDEFGHI','12345678!','Aa123456','Aa!bcdef','Aa1@bcde','Aa11!bcde','Z9-zebra!','GoodPass1#','short1A!']],PASSWORD,[PASSWORD.replace('len(password)>=8','len(password)>8'),PASSWORD.replace('all(left!=right','all(left==right')],['Requires more than eight characters and rejects valid length-eight passwords.','Requires adjacent characters to be identical instead of different.'],password_oracle,random_password,['Evaluate each independent strength requirement directly.','Use any checks for the four character classes and pairwise comparison for adjacent duplicates.','Return the conjunction of length, lowercase, uppercase, digit, special, and adjacency predicates.','The conjunction is true exactly when none of the required conditions fails.'],'O(n)','O(1)',3),
    2300: entry('successful_spell_potion_counts',[('spells','list[int]'),('potions','list[int]'),('success','int')],'list[int]',['arrays','binary search','sorting'],['A spell-potion pair succeeds when their positive strength product is at least success.','Return one count for each spell in original order.','Potions may be reordered for searching but duplicate potion values count separately.'],[([[5,1,3],[1,2,3,4,5],7],'The spells form four, zero, and three successful pairs respectively.'),([[3,1,2],[8,5,8],16],'The counts are three, zero, and two while both potions of strength eight count separately.')],[[s,p,x] for s,p,x in [([1],[1],1),([1],[1],2),([5,1,3],[1,2,3,4,5],7),([3,1,2],[8,5,8],16),([10],[1,2,3],20),([1,2],[100],50),([2,4],[1,1,1],2),([7,3],[2,5,9],15),([1,1,1],[1,2,3],2),([100,50],[1,2],100),([4],[4],16),([4],[4],17),([9,2,6],[3,7,1,5],30),([5,10],[10,5,1],50)]],PAIRS,[PAIRS.replace('(success+spell-1)//spell','success//spell'),PAIRS.replace('bisect_left','bisect_left',1).replace('ordered,required','ordered,required+1')],['Uses floor rather than ceiling division and accepts potions whose product is below success.','Uses a strict product threshold by searching above the first sufficient potion.'],pairs_oracle,random_pairs,['Sort potions once, then binary-search the threshold required by each spell.','The smallest sufficient potion is ceil(success/spell).','Use (success+spell-1)//spell and count the sorted suffix from bisect_left.','All potions in that suffix meet the product threshold and every earlier potion fails it, including correct handling of duplicates.'],'O(p log p+s log p)','O(p)',6),
}

BATCH[2295]['wrong'][0] = '''\
def apply_array_replacements(nums,operations):
    result=list(nums);positions={value:index for index,value in enumerate(result)}
    for old,new in operations:
        index=positions.pop(old);result[index]=new;positions[new]=(index+1)%len(result)
    return result
'''
BATCH[2295]['wrong_reasons'][0] = 'Records each replacement at the following position, so a chained replacement updates the wrong element.'
BATCH[2297]['examples'][1] = ([[0,1,2],[1,1,1]], 'The valid route is zero to one to two, with total landing cost two; the intermediate one blocks a direct jump.')
BATCH[2297]['hints'][1] = 'When a new value arrives, each node popped from the non-increasing or increasing stack has a legal direct jump to it.'
BATCH[2297]['hints'][2] = 'Relax dp[index] from every popped predecessor on both stacks, then push the index.'
BATCH[2297]['editorial'] = 'Adjacent nodes are exposed by one stack, while any longer legal predecessor is popped at its first qualifying endpoint, so the two stack scans relax all jump choices needed by an optimum.'
BATCH[2297]['wrong'][0] = JUMP.replace('dp[previous]+costs[index]', 'dp[previous]+costs[previous]')
BATCH[2297]['wrong_reasons'][0] = 'Charges the cost of the departed index instead of the index where the jump lands.'
BATCH[2297]['wrong'][1] = JUMP.replace('dp[0]=0', 'dp[0]=costs[0]')
BATCH[2297]['wrong_reasons'][1] = 'Charges the starting index even though cost is paid only when landing after a jump.'
