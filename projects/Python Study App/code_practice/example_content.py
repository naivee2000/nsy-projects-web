from __future__ import annotations

from typing import Any


# Each visible example is deliberately chosen to demonstrate the rule named in
# the problem, followed by a contrasting or boundary case. Expected values are
# still calculated from the reference solution when the catalog is built.
EXAMPLE_CONTENT: dict[str, list[tuple[list[Any], str]]] = {
    "pair-sum-indices": [
        ([[2, 7, 11, 15], 9], "The values 2 and 7 add to 9, so return their indices 0 and 1."),
        ([[3, 2, 4], 6], "The matching values are 2 and 4 at indices 1 and 2; indices are returned, not the values."),
    ],
    "valid-brackets": [
        (["()[]{}"], "Three adjacent bracket pairs are all balanced."),
        (["([)]"], "The closing parenthesis arrives while the square bracket is still open, so the nesting is invalid."),
    ],
    "binary-search-index": [
        ([[-1, 0, 3, 5, 9, 12], 9], "The target 9 is present at zero-based index 4."),
        ([[-1, 0, 3, 5, 9, 12], 2], "The target falls between 0 and 3 but is not present, so return -1."),
    ],
    "reverse-linked-list": [
        ([[1, 2, 3, 4]], "Every next pointer is reversed, producing the values in the opposite order."),
        ([[7]], "A one-node linked list is unchanged after reversal."),
    ],
    "merge-sorted-linked-lists": [
        ([[1, 2, 4], [1, 3, 4]], "Taking the smaller current node from each chain produces [1, 1, 2, 3, 4, 4] without sorting again."),
        ([[], [0]], "When the first chain is empty, the existing second chain is already the complete merged result."),
    ],
    "max-single-trade-profit": [
        ([[7, 1, 5, 3, 6, 4]], "Buying at 1 and later selling at 6 gives the best profit of 5."),
        ([[7, 6, 4, 3, 1]], "Prices only fall, so making no trade gives a profit of 0."),
    ],
    "normalized-palindrome": [
        (["A man, a plan, a canal: Panama"], "Ignoring spaces, punctuation, and case leaves a palindrome."),
        (["race a car"], "Normalization leaves different forward and backward character orders."),
    ],
    "merge-sorted-values": [
        ([[1, 3, 5], [2, 4, 6]], "Interleave both sorted inputs to keep the result sorted."),
        ([[], [1, 2]], "If one input is empty, the other sorted input is the complete result."),
    ],
    "tree-max-depth": [
        ([[3, 9, 20, None, None, 15, 7]], "The longest root-to-leaf route contains three nodes."),
        ([[]], "An empty tree has depth 0."),
    ],
    "longest-unique-span": [
        (["abcabcbb"], "The longest substring without a repeated character is 'abc', with length 3."),
        (["bbbbb"], "With one repeated character, every unique substring has length 1."),
    ],
    "group-anagram-words": [
        ([["eat", "tea", "tan", "ate", "nat", "bat"]], "Words with the same letters share a group; 'bat' remains by itself."),
        ([[""]], "The empty string is a valid word and forms one group."),
    ],
    "three-sum-zero": [
        ([[-1, 0, 1, 2, -1, -4]], "Two distinct value triplets sum to zero; duplicate triplets are omitted."),
        ([[0, 1, 1]], "No three values sum to zero, so the result is empty."),
    ],
    "days-until-warmer": [
        ([[73, 74, 75, 71, 69, 72, 76, 73]], "Each position reports how many days ahead its next warmer temperature occurs."),
        ([[30, 40, 50, 60]], "In a rising sequence, each day waits one day except the final day."),
    ],
    "rotated-array-search": [
        ([[4, 5, 6, 7, 0, 1, 2], 0], "The target is found at index 4 across the rotation boundary."),
        ([[4, 5, 6, 7, 0, 1, 2], 3], "The target is absent from both sorted portions, so return -1."),
    ],
    "merge-intervals": [
        ([[[1, 3], [2, 6], [8, 10], [15, 18]]], "The first two intervals overlap and merge; the other two stay separate."),
        ([[[1, 4], [4, 5]]], "Intervals that touch at an endpoint are merged into one interval."),
    ],
    "tree-level-order": [
        ([[3, 9, 20, None, None, 15, 7]], "Group the root, its children, and its grandchildren into separate levels."),
        ([[1]], "A one-node tree produces one level containing the root."),
    ],
    "valid-binary-search-tree": [
        ([[2, 1, 3]], "Every left value is smaller and every right value is larger than its ancestors."),
        ([[5, 1, 4, None, None, 3, 6]], "The value 3 sits in the root's right subtree but is smaller than 5, violating the global rule."),
    ],
    "count-islands": [
        ([[["1", "1", "0"], ["1", "0", "0"], ["0", "0", "1"]]], "Four-directional connections form two separate islands."),
        ([[["0", "0"], ["0", "0"]]], "A grid containing only water has zero islands."),
    ],
    "shortest-clear-path": [
        ([[[0, 1], [1, 0]]], "A diagonal move connects the clear start and finish in two visited cells."),
        ([[[0, 0, 0], [1, 1, 0], [1, 1, 0]]], "The shortest clear route follows the open top and right edges in four visited cells."),
    ],
    "top-k-frequent": [
        ([[1, 1, 1, 2, 2, 3], 2], "The two highest frequencies belong to 1 and 2."),
        ([[1], 1], "With one distinct value and k=1, that value is the result."),
    ],
    "combination-sum-once": [
        ([[10, 1, 2, 7, 6, 1, 5], 8], "All unique combinations summing to 8 are returned, and each input occurrence is used at most once."),
        ([[2, 5, 2, 1, 2], 5], "Repeated input values may be used when separate occurrences exist, but duplicate combinations are omitted."),
    ],
    "minimum-window": [
        (["ADOBECODEBANC", "ABC"], "'BANC' is the shortest substring containing A, B, and C."),
        (["a", "aa"], "The source lacks two copies of 'a', so no valid window exists."),
    ],
    "word-ladder-steps": [
        (["hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]], "A shortest sequence is hit → hot → dot → dog → cog, containing five words."),
        (["hit", "cog", ["hot", "dot", "dog", "lot", "log"]], "Because 'cog' is unavailable, no valid transformation can finish."),
    ],
    "weighted-job-schedule": [
        ([[1, 2, 3, 3], [3, 4, 5, 6], [50, 10, 40, 70]], "Choosing the jobs worth 50 and 70 gives the best compatible profit of 120."),
        ([[1, 2, 3, 4, 6], [3, 5, 10, 6, 9], [20, 20, 100, 70, 60]], "The optimal schedule may skip several earlier jobs to earn a larger total of 150."),
    ],
    "median-sorted-arrays": [
        ([[1, 3], [2]], "The merged order is [1, 2, 3], whose middle value is 2."),
        ([[1, 2], [3, 4]], "An even total length uses the average of the two middle values, 2 and 3."),
    ],

    "balanced-pivot-index": [
        ([[1, 7, 3, 6, 5, 6]], "At index 3, the values to the left and right both sum to 11."),
        ([[1, 2, 3]], "No index balances the sums on its two sides, so return -1."),
    ],
    "longest-increasing-run": [
        ([[1, 2, 4, 1, 2, 3, 4]], "The final contiguous run [1, 2, 3, 4] is the longest, with length 4."),
        ([[5, 4, 3]], "A decreasing list has no increasing pair, so the longest run contains one value."),
    ],
    "count-local-peaks": [
        ([[1, 4, 2, 5, 3]], "The interior values 4 and 5 are each greater than both immediate neighbors."),
        ([[1, 2, 3, 4]], "A strictly increasing list has no interior value greater than both neighbors."),
    ],
    "stable-zero-move": [
        ([[0, 1, 0, 3, 12]], "Move both zeros to the end while keeping 1, 3, and 12 in their original order."),
        ([[1, 2, 3]], "A list without zeros is returned unchanged."),
    ],
    "first-unique-character": [
        (["leetcode"], "The first character 'l' occurs once, so its index is 0."),
        (["aabbcc"], "Every character repeats, so there is no unique character and the result is -1."),
    ],
    "run-length-encode": [
        (["aaabbccccd"], "The four consecutive runs have lengths 3, 2, 4, and 1."),
        (["abcd"], "Each character forms its own run of length 1."),
    ],
    "word-pattern-bijection": [
        (["abba", "red blue blue red"], "The consistent two-way mapping is a → red and b → blue."),
        (["abba", "red blue blue green"], "The final word would force a to map to both red and green, so the pattern fails."),
    ],
    "formable-word-total": [
        ([["cat", "hat", "tree"], "atach"], "The inventory can form 'cat' and 'hat' separately, so their lengths contribute 3 + 3 = 6."),
        ([["hello", "world", "leetcode"], "welldonehoneyr"], "The letters can form 'hello' and 'world' but not 'leetcode', giving a total length of 10."),
    ],
    "anagram-check": [
        (["listen", "silent"], "Both strings contain the same letters with the same frequencies."),
        (["hello", "world"], "The character counts differ, so the strings are not anagrams."),
    ],
    "subsequence-check": [
        (["algorithm", "aim"], "The letters a, i, and m appear in order, even though other letters occur between them."),
        (["python", "pony"], "The required letters cannot be read in candidate order from the source."),
    ],
    "edit-distance": [
        (["kitten", "sitting"], "One replacement, another replacement, and one insertion transform the first word in three edits."),
        (["code", "code"], "Identical strings need zero edits."),
    ],
    "longest-common-subsequence": [
        (["abcde", "ace"], "The ordered characters a, c, and e form a common subsequence of length 3."),
        (["abc", "xyz"], "The strings share no character, so the longest common subsequence has length 0."),
    ],
    "lower-bound-index": [
        ([[1, 3, 3, 5, 8], 3], "The first value at least 3 is the first 3, at index 1."),
        ([[1, 3, 3, 5, 8], 4], "Because 4 is absent, index 3 is where it could be inserted before 5."),
    ],
    "upper-bound-index": [
        ([[1, 3, 3, 5, 8], 3], "The first value strictly greater than 3 is 5 at index 3."),
        ([[1, 3, 3, 5, 8], 8], "No value is greater than 8, so return the list length, 5."),
    ],
    "target-position-range": [
        ([[1, 2, 2, 2, 4], 2], "The target occupies every position from index 1 through index 3."),
        ([[1, 3, 5, 7], 4], "An absent target has the required range [-1, -1]."),
    ],
    "sorted-target-count": [
        ([[1, 2, 2, 2, 4], 2], "The target's sorted block contains three values."),
        ([[1, 3, 5, 7], 4], "An absent target occurs zero times."),
    ],
    "kth-largest-value": [
        ([[3, 2, 1, 5, 6, 4], 2], "In descending order, 5 occupies the second position."),
        ([[2, 2, 1], 2], "Duplicate positions count separately, so the second-largest value is also 2."),
    ],
    "maximum-fixed-window-sum": [
        ([[2, 1, 5, 1, 3, 2], 3], "The size-three window [5, 1, 3] has the largest sum, 9."),
        ([[-4, -2, -5], 2], "For negative values, the best size-two window is [-4, -2] with sum -6."),
    ],
    "distinct-count-per-window": [
        ([[1, 2, 1, 3, 4, 2, 3], 4], "Count unique values separately inside each sliding window of four positions."),
        ([[1, 1, 1], 2], "Repeated equal values give one distinct value in each window."),
    ],
    "rotate-values-right": [
        ([[1, 2, 3, 4, 5], 2], "The final two values wrap around to the front."),
        ([[1, 2, 3], 3], "Rotating by the list length returns the original order."),
    ],
    "minimum-meeting-rooms": [
        ([[[0, 30], [5, 10], [15, 20]]], "The long meeting overlaps each shorter meeting, so two rooms are necessary."),
        ([[[1, 2], [2, 3]]], "Half-open intervals that only touch at time 2 can reuse one room."),
    ],
    "erase-overlapping-intervals": [
        ([[[1, 2], [2, 3], [3, 4], [1, 3]]], "Removing [1, 3] leaves three non-overlapping intervals, so one removal is enough."),
        ([[[1, 2], [3, 4], [5, 6]]], "Already separated intervals require no removals."),
    ],
    "total-covered-length": [
        ([[[1, 4], [2, 6], [8, 10]]], "The first two intervals merge to length 5 and the last adds 2, for a total of 7."),
        ([[[1, 2], [2, 5]]], "Touching half-open intervals cover continuously from 1 to 5, a length of 4."),
    ],
    "maximum-interval-overlap": [
        ([[[1, 5], [2, 6], [4, 8]]], "All three intervals are active between times 4 and 5."),
        ([[[1, 2], [2, 3], [3, 4]]], "Touching half-open intervals do not overlap, so the maximum is 1."),
    ],
    "matrix-spiral-order": [
        ([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "Read the outside clockwise, then finish with the center value 5."),
        ([[[1, 2, 3], [4, 5, 6]]], "This matrix has two rows and three columns. Read 1,2,3 across the top, 6 down the right, then 5,4 back along the bottom."),
    ],
    "transpose-square-matrix": [
        ([[[1, 2], [3, 4]]], "Rows become columns across the main diagonal."),
        ([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "Each position (row, column) moves to (column, row)."),
    ],
    "matrix-diagonal-sum": [
        ([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "Both diagonals sum to 30, but the shared center 5 is counted only once, giving 25."),
        ([[[5]]], "The one cell lies on both diagonals but contributes only once."),
    ],
    "missing-repeated-grid-values": [
        ([[[1, 3], [2, 2]]], "For the expected range 1 through 4, value 2 repeats and value 4 is missing."),
        ([[[9, 1, 7], [8, 9, 2], [3, 4, 6]]], "For the expected range 1 through 9, value 9 repeats and value 5 is missing."),
    ],
    "largest-land-region": [
        ([[[1, 1, 0], [1, 0, 1], [0, 1, 1]]], "The two separate land regions each contain three four-directionally connected cells, so the largest area is 3."),
        ([[[0, 0], [0, 0]]], "A water-only grid has no land region, so the area is 0."),
    ],
    "land-perimeter": [
        ([[[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [1, 1, 0, 0]]], "Shared land edges are internal; only the 16 exposed edges contribute."),
        ([[[1]]], "One isolated land cell exposes all four edges."),
    ],
    "enclaved-land-count": [
        ([[[0, 0, 0, 0], [1, 0, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]]], "The three connected center land cells cannot reach the boundary."),
        ([[[1, 1], [1, 1]]], "Every land cell touches the boundary, so none is enclaved."),
    ],
    "flood-fill-region": [
        ([[[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2], "Only the 1-cells connected to the center through shared sides are recolored to 2; the isolated corner stays 1."),
        ([[[0, 0, 0], [0, 0, 0]], 0, 0, 0], "When the requested color already matches the starting region, the image remains unchanged."),
    ],
    "lexicographic-topological-order": [
        ([4, [[0, 1], [0, 2], [1, 3], [2, 3]]], "When both 1 and 2 are available, choosing 1 first produces the lexicographically smallest valid order."),
        ([3, [[0, 1], [1, 2], [2, 0]]], "A directed cycle prevents any topological ordering, so return an empty list."),
    ],
    "directed-cycle-check": [
        ([4, [[0, 1], [1, 2], [0, 3]]], "All directed paths end without returning to an active node, so no cycle exists."),
        ([3, [[0, 1], [1, 2], [2, 0]]], "The edges 0 → 1 → 2 → 0 form a directed cycle."),
    ],
    "reachable-from-zero": [
        ([5, [[0, 1], [1, 2], [3, 4]]], "Only nodes 0, 1, and 2 are reachable from node 0; the other component is separate."),
        ([4, []], "With no edges, only the starting node 0 is reachable."),
    ],
    "shortest-directed-hops": [
        ([5, [[0, 1], [1, 4], [0, 2], [2, 3], [3, 4]]], "The route 0 → 1 → 4 reaches the final node in two directed edges."),
        ([4, [[0, 1], [2, 3]]], "The final node is in a separate directed component, so return -1."),
    ],
    "undirected-component-count": [
        ([5, [[0, 1], [1, 2], [3, 4]]], "The graph separates into components {0,1,2} and {3,4}."),
        ([3, []], "Without edges, each of the three nodes is its own component."),
    ],
    "bipartite-graph-check": [
        ([4, [[0, 1], [1, 2], [2, 3], [3, 0]]], "An even cycle can alternate two colors around all four nodes."),
        ([3, [[0, 1], [1, 2], [2, 0]]], "A three-node odd cycle cannot be colored with only two colors."),
    ],
    "undirected-terminal-path": [
        ([5, [[0, 1], [1, 2], [3, 4]]], "Node 0 and the last node 4 are in different components."),
        ([4, [[0, 1], [1, 2], [2, 3]]], "The path 0 — 1 — 2 — 3 connects node 0 to the last node."),
    ],
    "tree-component-count": [
        ([6, [[0, 1], [1, 2], [3, 4], [4, 5], [5, 3]]], "The first component is a tree; the second contains a cycle, so only one component counts."),
        ([3, []], "Each isolated node is an acyclic connected component, so all three count as trees."),
    ],
    "recursive-tree-sum": [
        ([[5, 3, 8, 1, None, -2]], "Add every node value, including -2, to get a total of 15."),
        ([[]], "The recursive base case for an empty tree returns 0."),
    ],
    "recursive-leaf-count": [
        ([[3, 9, 20, None, None, 15, 7]], "The leaf nodes are 9, 15, and 7, so the count is 3."),
        ([[]], "An empty tree contains no leaves."),
    ],
    "recursive-minimum-tree-depth": [
        ([[1, 2, 3, 4, None, None, None]], "The right child 3 is a leaf, so the shortest root-to-leaf depth is 2."),
        ([[]], "An empty tree has minimum depth 0."),
    ],
    "tree-right-side-view": [
        ([[1, 2, 3, None, 5, None, 4]], "From the right, the visible values by depth are 1, 3, and 4."),
        ([[1, 2, None, 3]], "With no right children, the left chain remains visible at every depth."),
    ],
    "deduplicate-sorted-linked-list": [
        ([[1, 1, 2, 3, 3]], "Adjacent repeats are bypassed, leaving one node for each sorted value: [1, 2, 3]."),
        ([[1, 1, 1]], "A run of three equal nodes collapses to one node."),
    ],
    "linked-middle-value": [
        ([[1, 2, 3, 4]], "For even length, return the second middle value, 3."),
        ([[1, 2, 3, 4, 5]], "For odd length, the single middle value is 3."),
    ],
    "linked-palindrome-check": [
        ([[1, 2, 3, 2, 1]], "The linked-list values read identically in both directions."),
        ([[1, 2, 3, 4]], "The forward and backward value orders differ."),
    ],
    "linked-odd-even-order": [
        ([[1, 2, 3, 4, 5]], "Positions 1, 3, and 5 come before positions 2 and 4, preserving order within each group."),
        ([[1, 2]], "With two nodes, the odd-positioned first node already precedes the even-positioned second node."),
    ],
    "next-greater-values": [
        ([[2, 1, 2, 4, 3]], "For each position, scan conceptually to its first strictly greater value on the right."),
        ([[5, 4, 3]], "A decreasing list has no greater value to the right of any position."),
    ],
    "previous-smaller-values": [
        ([[2, 5, 3, 7, 1]], "Each result is the nearest earlier value that is strictly smaller, not simply the smallest seen."),
        ([[1, 2, 3]], "In an increasing list, each value after the first uses its immediate predecessor."),
    ],
    "largest-histogram-rectangle": [
        ([[2, 1, 5, 6, 2, 3]], "The adjacent bars of heights 5 and 6 form the maximum area of 10."),
        ([[2, 4]], "Using both bars at height 2 gives area 4, tied with the single height-4 bar."),
    ],
    "sum-subarray-minimums": [
        ([[3, 1, 2, 4]], "Adding the minimum value from each of the ten contiguous subarrays gives 17."),
        ([[11]], "A one-value list has one subarray whose minimum is 11."),
    ],
    "maximum-contiguous-sum": [
        ([[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "The contiguous segment [4, -1, 2, 1] has the largest sum, 6."),
        ([[-3, -2, -5]], "For an all-negative nonempty list, choose the least negative single value, -2."),
    ],
    "nonadjacent-maximum-sum": [
        ([[2, 7, 9, 3, 1]], "Choosing 2, 9, and 1 avoids adjacent positions and totals 12."),
        ([[2, 1, 4, 9]], "Choosing 2 and 9 gives the best nonadjacent total of 11."),
    ],
    "increasing-subsequence-length": [
        ([[10, 9, 2, 5, 3, 7, 101, 18]], "A longest increasing subsequence such as [2, 3, 7, 18] has length 4."),
        ([[5, 4, 3, 2, 1]], "A decreasing list has a longest increasing subsequence of one value."),
    ],
    "minimum-stair-cost": [
        ([[10, 15, 20]], "Start at the step costing 15 and jump beyond the end for a minimum total of 15."),
        ([[1, 100, 1, 1, 1, 100, 1, 1, 100, 1]], "Choosing inexpensive steps and one- or two-step jumps gives the minimum total of 6."),
    ],
    "minimum-unbounded-coins": [
        ([[1, 2, 5], 11], "Two 5-value coins and one 1-value coin form 11 using three reusable coins."),
        ([[2], 3], "Repeated 2-value coins can never form the odd amount 3, so return -1."),
    ],
    "unbounded-coin-combinations": [
        ([[1, 2, 5], 5], "There are four order-independent combinations: five 1s, 2+1+1+1, 2+2+1, and 5."),
        ([[2], 3], "No number of reusable 2-value coins forms 3, so there are zero combinations."),
    ],
    "exact-coin-reachability": [
        ([[4, 7], 11], "One 4-value coin plus one 7-value coin reaches 11 exactly."),
        ([[2, 4], 7], "Any sum of reusable 2s and 4s is even, so 7 is unreachable."),
    ],
    "minimum-single-use-coins": [
        ([[1, 2, 5, 6], 7], "Using the listed 1 and 6 (or 2 and 5) forms 7 with two coin occurrences."),
        ([[1, 2, 5], 11], "The listed coins total only 8 and cannot be reused, so return -1."),
    ],
    "unique-text-permutations": [
        (["abc"], "Three distinct letters produce all 3! = 6 arrangements."),
        (["aab"], "Duplicate 'a' choices are deduplicated, leaving three distinct permutations."),
    ],
    "unique-text-subsequences": [
        (["ab"], "Each letter may be excluded or included, producing '', 'a', 'b', and 'ab'."),
        (["aa"], "Duplicate paths producing 'a' collapse into one distinct subsequence."),
    ],
    "palindrome-partitions": [
        (["aab"], "The prefix can be split as 'a'+'a' or kept as the palindrome 'aa'; both end with 'b'."),
        (["abc"], "With no multi-character palindrome, the only partition uses three single characters."),
    ],
    "letter-case-variations": [
        (["a1b2"], "Each of the two letters independently branches to lower or upper case; digits stay fixed."),
        (["3z4"], "Only 'z' changes case, producing two results."),
    ],
    "increasing-triplet-exists": [
        ([[2, 1, 5, 0, 4, 6]], "The values 0, 4, and 6 occur in increasing index and value order."),
        ([[5, 4, 3, 2, 1]], "No later value exceeds an earlier pair, so no increasing triplet exists."),
    ],
    "maximum-circular-subarray": [
        ([[5, -3, 5]], "Wrapping across the ends joins both 5s for a maximum circular sum of 10."),
        ([[-3, -2, -5]], "For all-negative input, the best nonempty choice is the single value -2."),
    ],
    "minimum-increments-unique": [
        ([[3, 2, 1, 2, 1, 7]], "Increment duplicate values into open positions using a minimum total of six +1 operations."),
        ([[1, 2, 3]], "Already distinct values need zero increments."),
    ],
    "three-equal-sum-parts": [
        ([[0, 2, 1, -6, 6, -7, 9, 1, 2, 0, 1]], "The list can be cut into three nonempty contiguous parts that each sum to 3."),
        ([[1, 2, 3, 4]], "The total is not divisible into three equal integer sums, so no valid split exists."),
    ],
    "target-subarray-count": [
        ([[1, 1, 1], 2], "Two overlapping contiguous subarrays, positions 0–1 and 1–2, sum to 2."),
        ([[1, -1, 0], 0], "Negative and zero values create three zero-sum contiguous subarrays."),
    ],
    "target-pair-count": [
        ([[1, 5, 7, -1, 5], 6], "Two 1+5 index pairs and one 7+(-1) pair make three pairs."),
        ([[1, 1, 1], 2], "Three equal values create three distinct index pairs, even though the value pair is the same."),
    ],
    "longest-target-sum-subarray": [
        ([[1, -1, 5, -2, 3], 3], "The first four values form the longest target-sum subarray, with length 4."),
        ([[-2, -1, 2, 1], 1], "The contiguous values [-1, 2] sum to 1, giving length 2."),
    ],
    "nearest-value-to-target": [
        ([[2, 5, 9], 7], "Values 5 and 9 are equally distant from 7, so the smaller tie value 5 wins."),
        ([[], 3], "An empty list has no nearest value, so return None."),
    ],
    "recursive-step-combinations": [
        ([5], "Every sequence of one- and two-step moves is counted; five steps have eight ordered combinations."),
        ([4], "The recurrence ways(4) = ways(3) + ways(2) produces five combinations."),
    ],
    "recursive-digit-sum": [
        ([482], "Recursively peel off 2, then 8, then 4; their sum is 14."),
        ([7], "A single digit is already the base case, so return 7."),
    ],
    "recursive-power-of-two": [
        ([5], "Divide-and-conquer recursion computes 2⁵ = 32."),
        ([0], "The zero-exponent base case returns 1."),
    ],
    "recursive-catalan-number": [
        ([3], "Summing the recursive left/right structure splits gives the third Catalan number, 5."),
        ([0], "There is one empty structure, so the zeroth Catalan number is 1."),
    ],
}


def examples_for(problem_id: str) -> list[tuple[list[Any], str]]:
    try:
        examples = EXAMPLE_CONTENT[problem_id]
    except KeyError as error:
        raise ValueError(f"missing curated examples for {problem_id}") from error
    if len(examples) != 2:
        raise ValueError(f"{problem_id} needs exactly two curated examples")
    return examples
