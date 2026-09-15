"""Offline-query binary-trie import completing batch 207."""
from .import_batch_055 import entry


def xor_oracle(args):
    nums, queries = args
    return [max((value ^ number for number in nums if number <= limit), default=-1)
            for value, limit in queries]


def random_xor(rng):
    nums = [rng.randint(0, 63) for _ in range(rng.randint(1, 12))]
    queries = [[rng.randint(0, 63), rng.randint(0, 63)] for _ in range(rng.randint(1, 10))]
    return [nums, queries]


XOR = '''def maximum_xor_with_limit(nums,queries):
    ordered=sorted(nums);indexed=sorted((limit,value,index) for index,(value,limit) in enumerate(queries))
    trie={};answer=[-1]*len(queries);position=0
    for limit,value,index in indexed:
        while position<len(ordered) and ordered[position]<=limit:
            node=trie
            for bit in range(30,-1,-1):node=node.setdefault((ordered[position]>>bit)&1,{})
            position+=1
        if not trie:continue
        node=trie;result=0
        for bit in range(30,-1,-1):
            current=(value>>bit)&1;preferred=1-current
            if preferred in node:result|=1<<bit;node=node[preferred]
            else:node=node[current]
        answer[index]=result
    return answer
'''

IGNORE_LIMIT = '''def maximum_xor_with_limit(nums,queries):
    return [max(value^number for number in nums) for value,limit in queries]
'''

MINIMUM_XOR = '''def maximum_xor_with_limit(nums,queries):
    return [min((value^number for number in nums if number<=limit),default=-1) for value,limit in queries]
'''


BATCH = {
1707: entry('maximum_xor_with_limit',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['bit manipulation','tries','offline queries'],['nums and queries each contain up to 100000 entries; all values and limits are between zero and 10^9.','For query [x,m], choose a nums value no greater than m that maximizes x XOR value.','Return -1 for a query with no eligible value, preserving query order.'],[([[0,1,2,3,4],[[3,1],[1,3],[5,6]]],'Eligible maxima are three, three, and seven for the three queries respectively.'),([[5,2,4,6,6,3],[[12,4],[8,1],[6,3]]],'The first query can use up to four and reaches fifteen; the second has no eligible value; the third reaches five.')],[[n,q] for n,q in [([0],[[0,0]]),([1],[[0,0]]),([1],[[0,1]]),([0,1],[[2,0]]),([2,3],[[1,2]]),([2,3],[[1,3]]),([5,10],[[7,4],[7,5],[7,10]]),([0,1,2,3],[[4,0],[4,1],[4,2],[4,3]]),([8,1,2],[[7,2]]),([7,7,7],[[0,7]]),([1,4,8,16],[[15,8],[15,3]]),([100,200],[[50,99],[50,100],[50,1000]]),([3,10,5,25,2,8],[[5,28],[5,2]]),([0,1073741823],[[1073741823,0],[0,1073741823]])]],XOR,[IGNORE_LIMIT,MINIMUM_XOR],['Ignores each query limit and may choose an ineligible large number.','Minimizes XOR among eligible values instead of maximizing it.'],xor_oracle,random_xor,['Sort queries by limit so eligible numbers can be inserted once in increasing order.','Store inserted numbers in a binary trie from the highest relevant bit downward.','For each x bit, prefer the opposite trie branch to set that result bit; fall back to the matching branch.','At a query’s turn the trie contains exactly nums values no greater than its limit, and greedy highest-bit choices lexicographically maximize the XOR value.'],'Sort nums and process queries offline by m. Incrementally insert newly eligible values into a binary trie. A query greedily takes the opposite bit whenever possible from bit 30 down, which maximizes the most significant differing bit before lower bits matter. Restore answers to original query order. The oracle independently enumerates every eligible number.','O((nums+queries) log V)','O(nums log V)',8),
}
