"""Second slice of workbook batch 121."""

from itertools import combinations, permutations

from .import_batch_055 import entry


def microwave_oracle(args):
    start, move, push, target = args
    answer = float("inf")
    for minutes in range(100):
        seconds = target - 60 * minutes
        if not 0 <= seconds <= 99:
            continue
        digits = f"{minutes:02d}{seconds:02d}".lstrip("0") or "0"
        current = str(start)
        cost = 0
        for digit in digits:
            cost += push
            if digit != current:
                cost += move
                current = digit
        answer = min(answer, cost)
    return answer


def random_microwave(rng):
    return [rng.randrange(10), rng.randint(1, 9), rng.randint(1, 9), rng.randint(1, 6039)]


def difference_oracle(args):
    nums = args[0]
    n = len(nums) // 3
    best = float("inf")
    indexes = range(len(nums))
    for removed in combinations(indexes, n):
        omitted = set(removed)
        kept = [value for index, value in enumerate(nums) if index not in omitted]
        best = min(best, sum(kept[:n]) - sum(kept[n:]))
    return best


def random_difference(rng):
    n = rng.randint(1, 4)
    return [[rng.randint(1, 30) for _ in range(3 * n)]]


def even_odd_oracle(args):
    nums = args[0]
    even = sorted(nums[::2])
    odd = sorted(nums[1::2], reverse=True)
    answer = []
    for index in range(len(nums)):
        answer.append(even[index // 2] if index % 2 == 0 else odd[index // 2])
    return answer


def random_even_odd(rng):
    return [[rng.randint(1, 100) for _ in range(rng.randint(1, 40))]]


def number_oracle(args):
    num = args[0]
    if num == 0:
        return 0
    digits = str(abs(num))
    candidates = {int("".join(order)) for order in permutations(digits) if order[0] != "0"}
    return -max(candidates) if num < 0 else min(candidates)


def random_number(rng):
    digits = rng.randint(1, 7)
    value = rng.randint(10 ** (digits - 1), 10**digits - 1)
    return [value if rng.randrange(2) else -value]


def cars_oracle(args):
    s = args[0]
    answer = 2 * s.count("1")
    for left in range(len(s) + 1):
        for right in range(left, len(s) + 1):
            answer = min(answer, left + len(s) - right + 2 * s[left:right].count("1"))
    return answer


def random_cars(rng):
    return ["".join(rng.choice("01") for _ in range(rng.randint(1, 35)))]


MICROWAVE = '''\
def minimum_microwave_entry_cost(start_at,move_cost,push_cost,target_seconds):
    def cost(minutes,seconds):
        if not (0<=minutes<=99 and 0<=seconds<=99):return float('inf')
        digits=f'{minutes:02d}{seconds:02d}'.lstrip('0') or '0'
        current=str(start_at);total=0
        for digit in digits:
            if digit!=current:total+=move_cost;current=digit
            total+=push_cost
        return total
    minutes,seconds=divmod(target_seconds,60)
    return min(cost(minutes,seconds),cost(minutes-1,seconds+60))
'''

DIFFERENCE = '''\
def minimum_sum_difference_after_removal(nums):
    import heapq
    n=len(nums)//3
    left=[0]*len(nums);heap=[-value for value in nums[:n]];heapq.heapify(heap)
    total=sum(nums[:n]);left[n-1]=total
    for index in range(n,2*n):
        total+=nums[index];heapq.heappush(heap,-nums[index]);total+=heapq.heappop(heap)
        left[index]=total
    right=[0]*len(nums);heap=nums[2*n:];heapq.heapify(heap)
    total=sum(heap);right[2*n]=total
    for index in range(2*n-1,n-1,-1):
        total+=nums[index];heapq.heappush(heap,nums[index]);total-=heapq.heappop(heap)
        right[index]=total
    return min(left[index-1]-right[index] for index in range(n,2*n+1))
'''

EVEN_ODD = '''\
def sort_even_odd_indices(nums):
    answer=list(nums)
    answer[::2]=sorted(nums[::2])
    answer[1::2]=sorted(nums[1::2],reverse=True)
    return answer
'''

NUMBER = '''\
def smallest_rearranged_number(num):
    if num==0:return 0
    digits=list(str(abs(num)))
    if num<0:return -int(''.join(sorted(digits,reverse=True)))
    digits.sort()
    first=next(index for index,digit in enumerate(digits) if digit!='0')
    digits[0],digits[first]=digits[first],digits[0]
    return int(''.join(digits))
'''

CARS = '''\
def minimum_illegal_car_removal_time(s):
    left=0;answer=len(s)
    for index,char in enumerate(s):
        left=min(left+(2 if char=='1' else 0),index+1)
        answer=min(answer,left+len(s)-1-index)
    return answer
'''


BATCH = {
    2162: entry('minimum_microwave_entry_cost',[('start_at','int'),('move_cost','int'),('push_cost','int'),('target_seconds','int')],'int',['math','enumeration','simulation'],['A valid display has 0..99 minutes and 0..99 seconds and represents the target total seconds.','Enter at most four digits; leading zero digits are omitted.','Moving is charged only when the next digit differs from the current finger position, while every press costs push_cost.'],[([1,2,1,600],'Enter 1000: the finger starts on 1, then one move to 0 plus four pushes costs 6.'),([0,1,2,76],'Entering 76 costs two moves and two pushes, totaling 6; it is cheaper than entering 116.')],[[a,b,c,t] for a,b,c,t in [(0,1,1,1),(5,2,3,5),(9,3,1,9),(1,2,1,60),(1,2,1,600),(0,1,2,76),(7,4,2,70),(3,5,1,90),(0,9,1,99),(2,1,9,120),(5,3,4,6039),(8,2,2,3600),(1,7,3,61),(4,2,5,100),(6,6,1,3599)]],MICROWAVE,[
        MICROWAVE.replace("if digit!=current:","if True:"),
        MICROWAVE.replace('cost(minutes-1,seconds+60)','cost(minutes+1,seconds-60)').replace("float('inf')","10**30"),
    ],['Charges a movement before every press, even when the finger is already on that digit.','Checks an invalid alternative representation instead of borrowing one minute into seconds.'],microwave_oracle,random_microwave,['A target can have at most two useful minute-second representations.','Check ordinary divmod and the alternative that decreases minutes by one and adds sixty seconds.','Convert each valid display to four digits, strip leading zeros, simulate finger moves and pushes, and take the lower cost.','Any valid m:ss pair with the same total differs only by exchanging sixty seconds for one minute; the 0..99 limits leave at most these two candidates.'],'O(1)','O(1)',6),
    2163: entry('minimum_sum_difference_after_removal',[('nums','list[int]')],'int',['arrays','heaps','dynamic programming'],['len(nums)=3*n and exactly n elements must be removed without changing remaining order.','The first n kept values form the left sum and the last n kept values form the right sum.','Return the minimum possible left sum minus right sum; values may reach 100,000.'],[([[3,1,2]],'Removing 3 leaves left sum 1 and right sum 2, so the minimum difference is -1.'),([[7,9,5,8,1,3]],'Choosing a small left pair and a large right pair across a valid split gives the minimum difference of 1.')],[[x] for x in [[1,2,3],[3,1,2],[5,5,5],[1,10,1],[7,9,5,8,1,3],[1,2,3,4,5,6],[6,5,4,3,2,1],[10,1,10,1,10,1],[4,8,2,9,5,7],[1,1,9,9,1,1],[3,6,1,8,2,7,4,9,5],[9,1,8,2,7,3,6,4,5],[2,20,3,19,4,18],[100,1,50,2,40,3]]],DIFFERENCE,[DIFFERENCE.replace('total+=heapq.heappop(heap)','total-=heapq.heappop(heap)'),DIFFERENCE.replace('total-=heapq.heappop(heap)','total+=heapq.heappop(heap)',1)],['Adds the removed maximum instead of subtracting it from the maintained prefix sum.','Adds the removed minimum instead of subtracting it from the maintained suffix sum.'],difference_oracle,random_difference,['Fix a boundary between the two kept halves, then optimize each side independently.','Maintain the n smallest values in every eligible prefix and the n largest values in every eligible suffix with heaps.','Build prefix minimum sums and suffix maximum sums, then minimize prefix[index-1]-suffix[index] over all boundaries.','For each boundary, any valid removal corresponds to choosing n prefix values and n suffix values; the heaps give the independently optimal choices, and all boundaries are checked.'],'O(n log n)','O(n)',8),
    2164: entry('sort_even_odd_indices',[('nums','list[int]')],'list[int]',['arrays','sorting'],['Sort values originally at even indices in nondecreasing order.','Sort values originally at odd indices in nonincreasing order.','Place the sorted values back only into indices of the same parity.'],[([[4,1,2,3]],'Even-index values 4,2 become 2,4; odd-index values 1,3 become 3,1, producing [2,3,4,1].'),([[2,1]],'Each parity group contains one value, so the list stays [2,1].')],[[x] for x in [[1],[2,1],[1,2,3],[3,2,1],[4,1,2,3],[5,4,3,2,1],[1,1,1,1],[9,2,8,3,7,4],[2,9,1,8,3,7],[100,1,50,2,25],[3,3,2,2,1,1],[10,20,30,40,50],[7,6,5,4,3,2,1],[1,100,2,99,3,98]]],EVEN_ODD,[EVEN_ODD.replace('reverse=True','reverse=False'),EVEN_ODD.replace('answer[::2]=sorted(nums[::2])','answer[::2]=sorted(nums[::2],reverse=True)')],['Sorts odd-index values ascending instead of descending.','Sorts even-index values descending instead of ascending.'],even_odd_oracle,random_even_odd,['Even and odd positions form two independent sequences.','Extract, sort, and assign each parity slice separately.','Sort nums[::2] ascending and nums[1::2] descending, then write both into a copy.','Slice assignment preserves the index parity and the requested sort order within each independent group.'],'O(n log n)','O(n)',3),
    2165: entry('smallest_rearranged_number',[('num','int')],'int',['math','sorting','greedy'],['Use exactly the decimal digits of abs(num), preserving the original sign.','A positive result may not begin with zero; zero itself returns zero.','For a negative input, minimizing the signed value means maximizing its absolute digit arrangement.'],[([310],'The ascending digits are 0,1,3; move the first nonzero digit forward to obtain 103.'),([-7605],'Descending absolute digits form 7650, so the smallest signed result is -7650.')],[[x] for x in [0,1,-1,10,-10,100,310,-7605,10020,-10020,909090,-909090,123456,-123456,9000001]],NUMBER,[NUMBER.replace("sorted(digits,reverse=True)","sorted(digits)"),NUMBER.replace("digits[0],digits[first]=digits[first],digits[0]","pass")],['Sorts negative digits ascending, producing a value that is not as small.','Leaves zero at the front of a positive arrangement and loses required place value.'],number_oracle,random_number,['The sign changes which digit ordering is optimal.','Use descending digits for negatives; for positives sort ascending but swap the first nonzero digit into the leading position.','Handle zero, branch by sign, arrange digits, and convert back to an integer.','Descending maximizes magnitude for a negative result. For positives, the smallest nonzero leading digit followed by all remaining digits ascending is lexicographically and numerically minimal.'],'O(d log d)','O(d)',5),
    2167: entry('minimum_illegal_car_removal_time',[('s','str')],'int',['strings','dynamic programming'],['A 1 marks illegal goods and every such car must be removed.','Removing one car from either end costs one; removing an illegal car from anywhere costs two.','Return the minimum total time, while zero cars need no removal.'],[(['1100101'],'Remove a suitable prefix and suffix while paying two for any remaining internal one; the minimum total is 5.'),(['0010'],'Removing the single internal illegal car directly costs 2, which is cheaper than clearing an end to reach it.')],[[x] for x in ['0','1','00','01','10','11','0010','0100','101','111','00000','1100101','100001','011110','1010101']],CARS,[CARS.replace("2 if char=='1' else 0","2"),CARS.replace('left+len(s)-1-index','left+len(s)-index')],['Charges two for clean zero cars kept in the prefix state.','Has an off-by-one cost for removing the remaining suffix.'],cars_oracle,random_cars,['Split the strategy into a processed prefix and a suffix removed from the right.','Track the cheapest way to clear all ones in the prefix: either extend it and pay two for a one, or remove the whole prefix from the left.','At each index update left=min(left+2*is_one,index+1), then combine it with the cost of deleting the unprocessed suffix.','Every solution has a final boundary: left DP optimizes everything before it and right-end removal handles everything after it; checking all boundaries is exhaustive.'],'O(n)','O(1)',8),
}
