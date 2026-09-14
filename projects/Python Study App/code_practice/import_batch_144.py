"""String matching, aggregation, and sliding-window workbook batch 144."""

from collections import Counter
from .import_batch_055 import entry


def edits_oracle(args):
    queries, dictionary = args
    return [
        word
        for word in queries
        if any(sum(a != b for a, b in zip(word, target)) <= 2 for target in dictionary)
    ]


def random_edits(rng):
    width = rng.randint(1, 7)
    words = lambda count: [
        "".join(rng.choice("abcdef") for _ in range(width)) for _ in range(count)
    ]
    return [words(rng.randint(1, 12)), words(rng.randint(1, 8))]


def targets_oracle(args):
    nums, space = args
    best_count = -1
    best = None
    for seed in nums:
        count = sum(value >= seed and (value - seed) % space == 0 for value in nums)
        if count > best_count or count == best_count and seed < best:
            best_count = count
            best = seed
    return best


def random_targets(rng):
    return [
        [rng.randint(1, 100) for _ in range(rng.randint(1, 30))],
        rng.randint(1, 15),
    ]


def creators_oracle(args):
    creators, ids, views = args
    totals = {}
    best = {}
    order = []
    for creator, video, view in zip(creators, ids, views):
        if creator not in totals:
            totals[creator] = 0
            order.append(creator)
        totals[creator] += view
        if (
            creator not in best
            or view > best[creator][0]
            or view == best[creator][0]
            and video < best[creator][1]
        ):
            best[creator] = (view, video)
    maximum = max(totals.values())
    return [
        [creator, best[creator][1]] for creator in order if totals[creator] == maximum
    ]


def random_creators(rng):
    n = rng.randint(1, 20)
    creators = [rng.choice(["amy", "bob", "cy", "dan"]) for _ in range(n)]
    ids = [f"v{rng.randint(0,30):02d}" for _ in range(n)]
    return [creators, ids, [rng.randint(0, 30) for _ in range(n)]]


def beautiful_oracle(args):
    n, target = args
    addition = 0
    while sum(map(int, str(n + addition))) > target:
        addition += 1
    return addition


def random_beautiful(rng):
    return [rng.randint(1, 500), rng.randint(5, 25)]


def window_oracle(args):
    nums, k = args
    best = 0
    for start in range(len(nums) - k + 1):
        values = nums[start : start + k]
        if len(set(values)) == k:
            best = max(best, sum(values))
    return best


def random_window(rng):
    n = rng.randint(1, 30)
    return [[rng.randint(1, 30) for _ in range(n)], rng.randint(1, n)]


EDITS = """\
def words_within_two_edits(queries,dictionary):
    answer=[]
    for query in queries:
        for target in dictionary:
            if sum(left!=right for left,right in zip(query,target))<=2:
                answer.append(query);break
    return answer
"""
TARGETS = """\
def smallest_best_destroy_target(nums,space):
    counts={}
    for value in nums:counts[value%space]=counts.get(value%space,0)+1
    best=max(counts.values())
    return min(value for value in nums if counts[value%space]==best)
"""
CREATORS = """\
def most_popular_creators(creators,ids,views):
    totals={};best={};order=[]
    for creator,video,view in zip(creators,ids,views):
        if creator not in totals:totals[creator]=0;order.append(creator)
        totals[creator]+=view
        if creator not in best or view>best[creator][0] or (view==best[creator][0] and video<best[creator][1]):best[creator]=(view,video)
    maximum=max(totals.values())
    return [[creator,best[creator][1]] for creator in order if totals[creator]==maximum]
"""
BEAUTIFUL = """\
def minimum_beautiful_addition(n,target):
    original=n;place=1
    while sum(map(int,str(n)))>target:
        digit=(n//place)%10
        if digit:n+=(10-digit)*place
        place*=10
    return n-original
"""
WINDOW = """\
def maximum_distinct_window_sum(nums,k):
    counts={};total=0;answer=0
    for index,value in enumerate(nums):
        counts[value]=counts.get(value,0)+1;total+=value
        if index>=k:
            old=nums[index-k];total-=old;counts[old]-=1
            if counts[old]==0:del counts[old]
        if index>=k-1 and len(counts)==k:answer=max(answer,total)
    return answer
"""

BATCH = {
    2452: entry(
        "words_within_two_edits",
        [("queries", "list[str]"), ("dictionary", "list[str]")],
        "list[str]",
        ["strings", "arrays"],
        [
            "All query and dictionary words have the same length.",
            "A query qualifies when changing at most two positions can make it equal to at least one dictionary word.",
            "Return qualifying query words in their original order.",
        ],
        [
            (
                [["word", "note", "ants", "wood"], ["wood", "joke", "moat"]],
                "word differs from wood once, note differs from joke once, and wood matches exactly; ants has more than two differences.",
            ),
            (
                [["yes", "noo"], ["yet"]],
                "yes differs from yet once, while noo differs in all three positions, so only yes is returned.",
            ),
        ],
        [
            [q, d]
            for q, d in [
                (["a"], ["b"]),
                (["abc"], ["abc"]),
                (["abc"], ["abd"]),
                (["abc"], ["ade"]),
                (["abc"], ["def"]),
                (["aaa", "bbb"], ["abb"]),
                (["test"], ["best", "tent"]),
                (["abcd"], ["abef"]),
                (["abcd"], ["aefd"]),
                (["same", "same"], ["same"]),
                (["cat", "dog"], ["fog"]),
                (["zzzz"], ["zzaz"]),
                (["code", "cope", "cake"], ["cane"]),
                (["aaaa", "bbbb"], ["aabb", "bbba"]),
            ]
        ],
        EDITS,
        [
            EDITS.replace("<=2", "<=1"),
            EDITS.replace("answer.append(query);break", "answer.append(query)"),
        ],
        [
            "Allows only one edit instead of two.",
            "Adds a qualifying query repeatedly when it matches multiple dictionary words.",
        ],
        edits_oracle,
        random_edits,
        [
            "Compare every query with each dictionary word position by position.",
            "Count mismatches and accept as soon as one dictionary word differs in at most two positions.",
            "Append once, then stop checking that query.",
            "Changing characters independently costs exactly one per mismatched position, so the mismatch count is the required edit count.",
        ],
        "O(q*d*w)",
        "O(1)",
        3,
    ),
    2453: entry(
        "smallest_best_destroy_target",
        [("nums", "list[int]"), ("space", "int")],
        "int",
        ["arrays", "hash maps"],
        [
            "Choosing seed x destroys every target equal to x+c*space for a non-negative integer c.",
            "The optimal seed must be one of the array values.",
            "Maximize destroyed occurrences, then return the smallest seed attaining that maximum.",
        ],
        [
            (
                [[3, 7, 8, 1, 1, 5], 2],
                "All odd values share one remainder class, so choosing the smallest odd seed 1 destroys five targets.",
            ),
            (
                [[6, 2, 5], 100],
                "Each value is alone in its remainder class, so the smallest value 2 wins the tie.",
            ),
        ],
        [
            [a, s]
            for a, s in [
                ([1], 1),
                ([1, 2, 3], 1),
                ([1, 2, 3], 2),
                ([2, 4, 6], 2),
                ([2, 2, 3], 2),
                ([5, 1, 9], 4),
                ([10, 3, 7, 14], 4),
                ([8, 12, 16, 1], 4),
                ([9, 6, 3], 3),
                ([100, 1], 99),
                ([4, 10, 7, 13], 3),
                ([2, 8, 14, 5], 6),
                ([1, 1, 1], 5),
                ([20, 15, 10, 5], 5),
            ]
        ],
        TARGETS,
        [
            TARGETS.replace("value%space", "value//space"),
            TARGETS.replace("min(value", "max(value"),
        ],
        [
            "Groups targets by quotient instead of their modulo class.",
            "Returns the largest seed when several optimal seeds tie.",
        ],
        targets_oracle,
        random_targets,
        [
            "Targets reachable from one seed all have the same remainder modulo space.",
            "Count occurrences in each remainder class.",
            "Find the largest class size and choose the smallest array value belonging to such a class.",
            "A smaller same-remainder seed reaches every larger class member, so class size is the exact achievable count and the final minimum applies the tie break.",
        ],
        "O(n)",
        "O(min(n,space))",
        5,
    ),
    2456: entry(
        "most_popular_creators",
        [("creators", "list[str]"), ("ids", "list[str]"), ("views", "list[int]")],
        "list[list[str]]",
        ["arrays", "hash maps"],
        [
            "Sum views across all videos for each creator.",
            "Return every creator tied for the greatest total, paired with that creator’s highest-view video id.",
            "Break a creator’s video-view tie using the lexicographically smallest id; results follow creator first-appearance order.",
        ],
        [
            (
                [
                    ["alice", "bob", "alice", "chris"],
                    ["one", "two", "three", "four"],
                    [5, 10, 5, 4],
                ],
                "Alice and Bob each total ten views; Alice’s tied videos choose id one, while Bob chooses two.",
            ),
            (
                [["a", "a"], ["z", "b"], [7, 7]],
                "Creator a is the only creator, and tied view counts choose the lexicographically smaller video id b.",
            ),
        ],
        [
            [c, i, v]
            for c, i, v in [
                (["a"], ["x"], [0]),
                (["a", "b"], ["x", "y"], [1, 2]),
                (["a", "b"], ["x", "y"], [2, 2]),
                (["a", "a"], ["b", "a"], [1, 1]),
                (["a", "a"], ["a", "b"], [1, 2]),
                (["a", "b", "a"], ["x", "y", "z"], [3, 5, 2]),
                (["c", "b", "c", "b"], ["d", "c", "b", "a"], [1, 2, 3, 2]),
                (["x", "y", "z"], ["a", "a", "a"], [0, 0, 0]),
                (["amy", "bob", "amy"], ["v2", "v1", "v1"], [5, 9, 5]),
                (["p", "q", "p", "q"], ["a", "b", "c", "d"], [4, 3, 1, 2]),
                (["a", "b", "c"], ["z", "y", "x"], [10, 5, 10]),
                (["u", "u", "v"], ["b", "a", "c"], [7, 7, 13]),
                (["m", "n", "m"], ["1", "2", "3"], [1, 3, 2]),
                (["a", "b", "b"], ["x", "y", "z"], [6, 3, 3]),
            ]
        ],
        CREATORS,
        [
            CREATORS.replace("totals[creator]+=view", "totals[creator]=view"),
            CREATORS.replace("video<best[creator][1]", "video>best[creator][1]"),
        ],
        [
            "Keeps only the creator’s latest video views instead of summing them.",
            "Chooses the lexicographically largest id when a creator’s videos tie.",
        ],
        creators_oracle,
        random_creators,
        [
            "Accumulate each creator’s total views.",
            "For each creator, track the video with greatest individual views and smallest id on a tie.",
            "Find the maximum creator total and emit all creators at that total in first-seen order.",
            "The two maps independently capture the creator-level and video-level comparisons required by the result.",
        ],
        "O(n)",
        "O(c)",
        5,
    ),
    2457: entry(
        "minimum_beautiful_addition",
        [("n", "int"), ("target", "int")],
        "int",
        ["math", "greedy"],
        [
            "A number is beautiful when its decimal digit sum is at most target.",
            "Return the smallest non-negative x such that n+x is beautiful.",
            "A solution is guaranteed.",
        ],
        [
            (
                [16, 6],
                "Adding four reaches 20, whose digit sum is two; additions zero through three keep digit sum above six.",
            ),
            (
                [467, 6],
                "Adding 33 reaches 500 with digit sum five, while no smaller addition meets the target.",
            ),
        ],
        [
            [n, t]
            for n, t in [
                (1, 1),
                (10, 1),
                (19, 1),
                (99, 1),
                (100, 1),
                (123, 6),
                (123, 5),
                (999, 1),
                (999, 27),
                (500, 5),
                (555, 10),
                (909, 9),
                (1099, 2),
                (9876, 15),
            ]
        ],
        BEAUTIFUL,
        [
            BEAUTIFUL.replace(">target", ">target+1"),
            BEAUTIFUL.replace("return n-original", "return n"),
        ],
        [
            "Accepts a digit sum one larger than the requested target.",
            "Returns the final beautiful integer instead of the required addition.",
        ],
        beautiful_oracle,
        random_beautiful,
        [
            "While the digit sum is too large, inspect decimal places from right to left.",
            "Round the current nonzero digit up to zero by adding (10-digit)*place, carrying into higher positions.",
            "Continue until the digit sum meets target, then subtract the original n.",
            "Any smaller addition than the first required rounding leaves the current suffix nonzero and cannot reduce the digit sum enough; successive forced roundings therefore give the minimum.",
        ],
        "O(d^2)",
        "O(d)",
        5,
    ),
    2461: entry(
        "maximum_distinct_window_sum",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "sliding windows"],
        [
            "Consider every contiguous subarray of exactly length k.",
            "A window qualifies only when all k values are distinct.",
            "Return the largest qualifying sum, or zero when no window qualifies.",
        ],
        [
            (
                [[1, 5, 4, 2, 9, 9, 9], 3],
                "Distinct windows [1,5,4], [5,4,2], and [4,2,9] sum to 10, 11, and 15, so the answer is 15.",
            ),
            (
                [[4, 4, 4], 2],
                "Every length-two window repeats 4, so none qualifies and the answer is zero.",
            ),
        ],
        [
            [a, k]
            for a, k in [
                ([1], 1),
                ([1, 2], 1),
                ([1, 2], 2),
                ([1, 1], 2),
                ([1, 2, 1], 2),
                ([1, 2, 3], 3),
                ([3, 2, 1], 2),
                ([5, 1, 5, 2], 3),
                ([9, 8, 7, 9], 3),
                ([1, 1, 2, 3], 3),
                ([10, 1, 2, 3, 10], 4),
                ([2, 2, 3, 4, 5], 4),
                ([7, 7, 7, 8], 1),
                ([4, 3, 2, 1, 5], 2),
            ]
        ],
        WINDOW,
        [
            WINDOW.replace("index>=k", "index>k"),
            WINDOW.replace("len(counts)==k", "len(counts)<=k"),
        ],
        [
            "Removes the outgoing value one step late, creating oversized windows.",
            "Accepts windows containing duplicates because their distinct count is merely at most k.",
        ],
        window_oracle,
        random_window,
        [
            "Maintain a length-k sliding window with a running sum and frequency map.",
            "Add the new value and remove the value that falls k positions behind.",
            "A size-k window has all distinct values exactly when the map contains k keys.",
            "Every length-k window is visited once, and the maximum updates only for precisely qualifying windows.",
        ],
        "O(n)",
        "O(k)",
        5,
    ),
}
