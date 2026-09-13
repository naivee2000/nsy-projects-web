# Code Practice Lab

A private Python interview-practice app that runs locally or as an authenticated personal website. It currently includes 412 runnable problems (101 original exercises plus 311 verified workbook imports), a browser-isolated Pyodide judge, progressive wrong-answer coaching, hints, a guided daily queue, review scheduling, persistent SQLite progress, and an optional Codex-assisted variant workflow. The full workbook expansion is in progress, not complete.

The transfer-ready **412-problem handoff checkpoint** is tagged `python-study-412-checkpoint`; all earlier checkpoint tags remain unchanged. See [the current checkpoint and transfer checklist](docs/RELEASE_412_CHECKPOINT.md) for exact-version update commands. This release includes all seventeen verified batch-41/42/43 additions since the 395-problem checkpoint. Six unfinished batch-44 candidates remain separate laptop working files, not runnable imports or part of this release. Continuing development on this laptop does not change the website until you explicitly transfer another release, rebuild, and restart it. Keep the website computer's existing progress database; do not re-import the seed during a normal update. No GitHub push is performed unless the owner explicitly requests it.

## Start the app

Requirements: Python 3.11 or newer, Node.js 22.12+ (24 LTS recommended), npm, SQLite CLI for backup/seed commands, and macOS or another Unix-like system.

```bash
./run_local.sh
```

The first run installs dependencies and builds the frontend. Later runs work without internet. Open [http://127.0.0.1:8765](http://127.0.0.1:8765). Local mode binds only to `127.0.0.1` and does not require login.

The local runner rebuilds the frontend on each start. After pulling dependency changes, first run `.venv/bin/python -m pip install -r requirements.txt` and `npm --prefix frontend ci`, then `./run_local.sh`.

## Study workflow

- **Today** assigns one workload-capped daily set: five Easy problems; normally two Medium plus one Easy (or at most three Medium when no Easy remains); or one Hard plus at most one Medium. Finished items disappear without being replaced, and a completion message remains until the next local calendar day.
- **Daily review** separately assigns up to five previously passed problems and removes each one after a successful review submission that day. Its score prioritizes difficulty and due dates, then raises problems that took longer or failed again after their first successful solve. A full set uses at most three focus slots for linked lists, recursion, binary search, and recursive matrix/grid traversal; when available, the other two slots review completed problems outside those focus tags. Hint usage does not affect this review ordering.
- **Library** searches and filters on the server by title/pattern, topic, difficulty, and completion. It fetches 30 summaries per page; full instructions and tests load only when opening a problem. Back navigation retains the page and filters.
- **Back navigation** returns a problem to the page that opened it—Today or Library—without clearing the Library filters.
- **Run examples** executes the two hand-curated teaching examples: a representative case, a contrasting or boundary case, and a short explanation of why each shown output is correct.
- **Submit** executes all hidden tests (at least twelve per problem) and records the outcome. Passed hidden tests remain summarized; each failed hidden test can be clicked to reveal only its input, expected value, and the value or error produced by the current code.
- **Local Coach** explains one likely mistake at a time after an unresolved run. Its three-step ladder moves from concrete evidence to a debugging question without revealing the full solution.
- **Ask Codex coach** is optional and runs only after an explicit click. It sends the problem, visible failure evidence, and current draft to the locally authenticated Codex CLI for deeper Socratic feedback. It requires Codex login and may require internet access.
- Hints unlock in concept, strategy, pseudocode, and editorial order.
- Draft code, attempts, mastery, and review dates are stored in `data/code_practice.db`.

## Easy-problem quality bar

The original 101-problem catalog uses original wording and implementations. LeetCode's official Easy catalog and study-plan patterns informed its difficulty benchmark: an Easy problem should still require at least one reusable invariant, data-structure choice, recurrence, or edge-case decision. Workbook imports retain source summaries and provenance, with reviewed implementations, tests, and explanations; see the source attribution below.

A catalog audit replaced seven syntax-level exercises with stronger interview patterns. A two-chain, node-splicing linked-list merge was then added as a separate exercise, bringing the catalog to 101 problems (34 easy, 56 medium, and 11 advanced):

- Range Span → **Balanced Pivot Index** for running-left and derived-right prefix sums.
- Reverse Word Order → **Word Pattern Bijection** for two-way mapping consistency.
- Longest Word Length → **Formable Word Total** for character-frequency inventory reasoning.
- Count Negative Cells → **Missing and Repeated Grid Values** for matrix flattening and frequency reconciliation.
- Boundary Land Cells → **Flood Fill Region** for recursive connectivity and the same-color guard.
- Linked List Length → **Deduplicate a Sorted Linked List** for in-place pointer rewiring.
- Recursive Sum to N → **Recursive Step Combinations** for a memoized two-state recurrence.
- **Merge Two Sorted Linked Lists** was added for dummy-head, tail-pointer, and in-place node-splicing practice.

Short introductory problems remain only when they isolate a useful interview pattern. Examples include local peaks for safe neighbor boundaries, matrix transposition for coordinate mapping, run-length encoding for run-boundary state, recursive tree sum/leaf count for structural base cases, and linked-list middle for fast/slow pointers.

Research references: [LeetCode 75](https://leetcode.com/studyplan/leetcode-75/), [Find Pivot Index](https://leetcode.com/problems/find-pivot-index/), [Word Pattern](https://leetcode.com/problems/word-pattern/), [Find Words That Can Be Formed by Characters](https://leetcode.com/problems/find-words-that-can-be-formed-by-characters/), [Find Missing and Repeated Values](https://leetcode.com/problems/find-missing-and-repeated-values/), [Flood Fill](https://leetcode.com/problems/flood-fill/), [Remove Duplicates from Sorted List](https://leetcode.com/problems/remove-duplicates-from-sorted-list/), and [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/).

The submitted Python runs in a fresh browser Web Worker. FastAPI stores results but never executes submitted code. The two explained examples are visible in the problem pane. Hidden test details remain collapsed unless that case fails, when the learner may open a simple input/expected/current-result dropdown; reference and known-wrong solutions remain server-side. Linked-list and tree exercises include the concrete `ListNode` or `TreeNode` class in the editable starter code, including when an older saved draft is reopened. The offline coach performs static syntax-tree inspection only, so normal studying does not depend on an AI service or internet connection. The optional Codex coach runs ephemerally in a read-only sandbox, receives the revealed failure evidence but no reference solution, and is filtered to reject complete solutions and code-heavy answers.

## Back up progress

```bash
./backup_data.sh
```

Backups are written under `backups/`, which is intentionally excluded from Git.
The helper uses `CODE_PRACTICE_DB` first, then `CODE_PRACTICE_DATA_DIR/code_practice.db`, then the local default. Set `CODE_PRACTICE_BACKUP_DIR` to store backups outside the checkout. Environment settings inside PM2 are not automatically present in a terminal; supply the production paths explicitly when backing up the website database.

## Workbook expansion and portable catalog

`catalog_data/manifest.json` and `catalog_data/problems/*.json` are shipped with
the app. The server loads searchable metadata and at most 32 cached problem
details, without running reference solutions. SQLite progress remains separate
under `data/` or the configured `CODE_PRACTICE_DB` path. Old accepted submissions
remain Passed even after more than 500 newer attempts.

The 3,629-row workbook inventory is stored in `catalog_import/ledger.json`.
Current status: 74 existing equivalents, 311 verified imports, 155 documented
design/interactive exclusions, and 3,089 pending records. Ordinary tree and
linked-list exercises remain in scope. See [the delivery gates](docs/CATALOG_EXPANSION.md).
The ledger is an audit of source records, not a claim that pending problems are
available in the runnable library.

Forty-three reviewed batches include Add Two Numbers, Word Search, Swap Nodes in Pairs,
Reverse Linked List II, Sum Root to Leaf Numbers, BST search/ranking, tree diameter,
binary search, string/number exercises, and ordinary Hard problems such as
Trapping Rain Water and Sliding Window Maximum. Each has two explained visible
examples, at least twelve distinct hidden tests, two rejected plausible incorrect
implementations, and 500 seeded comparisons against an independent oracle.
Recent batches add phone-keypad combinations, reusable Combination Sum,
grid route counting with/without obstacles, minimum path cost, matrix binary
search, combinations/subsets, Decode Ways, and Restore IP Addresses. Recursive
grid problems retain the owner's weak-topic review priority. Any-order comparisons
accept valid reorderings but still reject duplicated or missing results.
The Hard-focused batch adds regular-expression and wildcard matching (with their
different star rules), longest valid parentheses, first missing positive, and
both Jump Game variants. Advanced imports retain explicit prerequisite topics.
The latest batches add linked-list rotation, interval insertion, Roman numerals,
32-bit division, permutation ranking, 3Sum Closest, prefix matching, recursive
Count and Say, and digit-by-digit string multiplication. The 3Sum Closest wording
clarifies distinct **indices**, not distinct values. Spiral Matrix is an existing
equivalent, not a duplicate import: its rectangular examples and constraints are
expanded under version 2 of `matrix-spiral-order`, preserving its ID and progress.
The ninth batch adds inorder/preorder/postorder traversal, zigzag and bottom-up
levels, Path Sum II, Triangle, and Binary Tree Maximum Path Sum. Matching paths
preserve duplicate value sequences from different leaves. Explicit traversal
frames support the 5,000-node path problem and 30,000-node maximum-path problem
without raising Python's recursion limit; beginner traversals still teach recursion.
The tenth batch adds lexical path simplification, duplicate-aware rotated binary
search, Interleaving String, Distinct Subsequences, unlimited/two-transaction
stock problems, Gas Station, and Candy. Duplicate-aware binary search retains
the existing weak-topic review priority. Source guarantees such as a unique gas
station start and 32-bit final subsequence count have explicit regression checks.
The eleventh batch preserves actual in-place contracts for Remove Duplicates,
Remove Element, Next Permutation, Rotate Image, Set Matrix Zeroes, Sort Colors,
Remove Duplicates II, and Merge Sorted Array. The judge reads the original
argument after execution. Prefix-removal tasks display `{return, prefix}` and
check both the integer count and the meaningful prefix, ignoring the tail.
Remove Element permits prefix reordering but still checks duplicate counts.
Returning a copy or computing only k without the required mutation does not pass.
The instructions explain these grading modes beside the examples. Space/time
targets remain learning goals; the judge checks observable correctness and its
execution deadline, not a formal proof of asymptotic complexity.
The twelfth batch adds Remove Duplicates from Sorted List II, stable Partition
List, Word Break, and recursive Word Break II. Removing all duplicated values
is distinct from the original keep-one linked-list exercise. Segmentation permits
word reuse; the Hard version returns every complete sentence with no duplicates.
Linked-list and recursive-word exercises retain the existing weak-topic priorities.
Batch thirteen adds Longest Consecutive Sequence, minimum palindrome cuts,
Single Number II, and postfix-expression evaluation. Tests distinguish values
from positions, cuts from pieces, signed 32-bit values from unsigned bit patterns,
and division toward zero from Python floor division.
Batch fourteen adds tree reconstruction from preorder/inorder and
inorder/postorder, plus in-place Surrounded Regions. These return actual TreeNode
objects or mutate the original grid, respectively. Reconstruction includes
3,000-node skewed trees; grid traversal includes 200×200 regions and a regression
over all 512 three-by-three boards. Recursion explanations and the stronger
recursive-grid review priority remain available; explicit stacks prevent deep
inputs from overflowing Python's call stack.
Batch fifteen adds Valid Sudoku, Valid Number, Text Justification, and Maximal
Rectangle. Tests cover valid-but-unsolvable partial Sudoku boards, 4,680 short
numeric strings, exact line spacing, and all 512 binary three-by-three matrices.
Text Justification's workbook sample lost repeated spaces; the report retains
the original and an explicit correction verified against the source contract.
No mismatching sample is silently accepted or removed.
Batch sixteen adds Flatten Binary Tree to Linked List and Reorder List. Both
modify original nodes in place, with 2,000-node tree and 50,000-node list fixtures.
The judge checks the selected input's node identities and unchanged values;
these two problems additionally require the precise original-node order even
when values repeat. Flattening keeps TreeNode objects and follows right links;
it does not construct a separate ListNode list. All 108 imported references were
revalidated after this shared-judge extension.
Batch seventeen adds Reverse Words, Maximum Product Subarray, duplicate-aware
rotated minimum, at-most-two-character windows, One Edit Distance, Missing
Ranges, Compare Version Numbers, and Dungeon Game. Regressions distinguish
zero edits from one, negative products from sums, numeric from lexical revisions,
and surviving every dungeon prefix from merely ending with positive health.
Duplicate-aware binary search and recursive-grid DP retain weak-topic priority.
Batch eighteen adds both Excel-column conversions, Factorial Trailing Zeroes,
Largest Number, Repeated DNA Sequences, and the Hard Stock IV problem with an
input transaction budget. Tests cover all 10,001 factorial inputs, all 702
one-/two-letter column labels, prefix-sensitive concatenation ordering,
overlapping DNA windows, and stock budgets that allow more than two trades.
Stress fixtures include a 100,000-character DNA sequence, 1,000 daily prices,
and a 1,000-digit string result without large-number JSON conversion.
Batch nineteen adds sorted-array/list conversion to balanced BSTs, Count Complete
Tree Nodes, and Count Univalue Subtrees. Conversions return actual TreeNode
objects; the linked-list starter includes both node classes. The new balanced-BST
comparator accepts any shape whose inorder traversal preserves every input
value and whose every subtree is height-balanced. It rejects missing duplicates,
unbalanced chains, and invalid node values. Examples are labelled “One valid
output,” and failures retain both the actual output and the contract explanation.
The property checker is tested against all 626 binary-tree shapes through seven
nodes. Stress fixtures cover 20,000-node list conversions, 50,000-node complete
trees, and 1,000-node skewed trees. All 126 imports were revalidated after this
judge extension; original IDs, progress, and weak-topic review boosts are retained.
The original Tree Height exercise is now version 2 under the same `tree-max-depth`
ID. Its recursive reference previously overflowed on a valid 10,000-node chain.
An explicit depth-first stack now supports the existing 20,000-node limit;
independent breadth-first and 500 seeded path-shape checks verify the repair.
Tests preserve version-1 accepted attempts and drafts across repackaging/reopen.
This strengthens the existing LeetCode 104 equivalent, not the problem count.
Batch twenty adds Reverse Bits, Range Bitwise AND, Happy Number, Count Primes,
Isomorphic Strings, Minimum Size Subarray Sum, House Robber II, Shortest
Palindrome, and recursive Combination Sum III. Tests preserve the source's even
32-bit reversal domain, ASCII control characters, positive-only sliding-window
assumption, circular adjacency, and front-only palindrome additions. Independent
regressions verify all 480 digit-combination inputs and the five-million prime
boundary. The Hard palindrome exercise requires mastery of existing strings and
string-matching topics, rather than a new prerequisite with no preparatory exercise.
Batch twenty-one adds Word Search II, The Skyline Problem, Maximal Square, and
Rectangle Area. Recursive grid search retains the stronger review priority;
tests check cell reuse, diagonals, repeated paths, and restoring the input board.
Independent checks cover simultaneous skyline events, square area versus side
length, and degenerate/touching rectangles. Maximum-size fixtures include 30,000
dictionary words, 10,000 buildings, and 300×300 matrices. The initial missing
cell-reuse counterexample blocked Word Search II approval until repaired; no
quarantined version was published.
Batch twenty-two adds Contains Duplicate II/III, Basic Calculator I/II, Summary
Ranges, Majority Element II, Number of Digit One, Product of Array Except Self,
Search a 2D Matrix II, and Different Ways to Add Parentheses. Exhaustive and
source-scale checks cover exact window boundaries, negative value buckets,
100,000-deep grouping, integer truncation toward zero, strict one-third voting,
the 10^9 digit-count boundary, zero products, sorted matrices, and duplicate
results produced by different expression groupings.
Batch twenty-three adds Shortest Word Distance I/III, Strobogrammatic Number
I/II/III, Group Shifted Strings, Meeting Rooms, Factor Combinations, Paint House,
and Add Digits. Tests distinguish same-word occurrences, exhaust all generation
lengths through 14, count the full 15-digit strobogrammatic domain, preserve
cyclic shifts and duplicate strings, allow touching meetings, and compare factor
and painting results against direct enumeration.
Batch twenty-four adds Lowest Common Ancestor for BSTs and arbitrary binary
trees, Verify Preorder Sequence in BST, Binary Tree Paths, 3Sum Smaller, Single
Number III, Graph Valid Tree, Ugly Number I/II, and Paint House II. The LCA
problems receive the actual `p` and `q` nodes selected from the input tree and
must return an existing node without mutating the tree. Regressions cover
100,000-node chains, exhaustive short BST preorder sequences and simple graphs,
duplicate tree paths, signed singleton pairs, the 1,690th ugly number, and
independent small painting assignments. Recursive-tree and binary-search study
priorities remain intact.
Batch twenty-five adds Delete Node in a Linked List, both Palindrome Permutation
problems, both closest-BST-value problems, Integer to English Words, both H-Index
problems, Paint Fence, and Perfect Squares. Delete Node receives the actual
selected non-tail ListNode while the judge retains the original head; it accepts
the constant-space value-copy/splice operation and rejects replacement nodes or
changes to other nodes. The workbook's contextual `head` and `node` sample is
preserved through an explicit adapter without adding a head parameter to the
learner's function. Recursive palindrome and number-word exercises retain weak-
topic review coverage, and the sorted H-Index exercise keeps its logarithmic
binary-search target.
Batch twenty-six adds Wiggle Sort, Expression Add Operators, Move Zeroes,
Inorder Successor in BST, Walls and Gates, Find the Duplicate Number, Game of
Life, Word Pattern II, Nim Game, and both Flip Game contracts. The judge accepts
any valid wiggle permutation, permits a legitimate `None` result for selected-
node queries, and enforces read-only input parameters where mutation is forbidden.
Regressions exhaust short wiggle arrays, every 3×3 Game of Life board, and short
Flip Game states; source-scale fixtures cover 10,000-element arrays and trees,
a 250×250 room grid, and a 100,001-element duplicate cycle. Recursion,
backtracking, binary-search trees, and recursive game-state practice retain the
owner's weak-topic coverage.
Batch twenty-seven adds Best Meeting Point, Binary Tree Longest Consecutive
Sequence, Bulls and Cows, Remove Invalid Parentheses, Smallest Rectangle
Enclosing Black Pixels, Number of Islands II, Additive Number, Stock With
Cooldown, Minimum Height Trees, and Sparse Matrix Multiplication. It adds median,
recursive-tree, backtracking, binary-search, union-find, dynamic-programming, and
sparse-matrix practice. Exhaustive regressions cover small meeting grids,
parenthesis strings, connected black-pixel shapes, online island additions,
stock sequences, and every labeled tree through six nodes. Source-scale cases
include a 10,000-node tree, 10,000 island updates, a 20,000-node graph, and
100-by-100 sparse matrices. A stricter interface audit also classifies
constructor-plus-query classes as design exercises; ordinary `TreeNode` and
`ListNode` function problems remain eligible.
Batch twenty-eight adds Burst Balloons, Super Ugly Number, Binary Tree Vertical
Order Traversal, Count of Smaller Numbers After Self, Remove Duplicate Letters,
and Shortest Distance from All Buildings. It exercises interval DP, prime-product
stream merging, tree row/column order, suffix frequencies, greedy subsequence
selection, and obstacle-aware grid distances. Stress tests include 300 balloons,
the 100,000th super ugly number with 100 primes, 100,000 suffix-count elements,
10,000-character strings, and 50-by-50 grids. Exhaustive small-domain tests and
an independent factorization check support the reference results.
Batch twenty-nine adds Maximum Product of Word Lengths, Generalized Abbreviation,
Power of Three, Count of Range Sum, Longest Increasing Path in a Matrix, Patching
Array, Verify Preorder Serialization, Largest BST Subtree, and House Robber III.
It includes all 32,768 abbreviations of a 15-letter word, inclusive signed range
sums, a 40,000-cell increasing matrix path, and 10,000-node tree DP fixtures.
Exhaustive small-domain tests compare against independent path enumeration,
subtree checks, independent-set enumeration, and subset-sum search. Iterative
references handle deep inputs while the hints explain the recursive recurrences.
Batch thirty adds four Hard problems: Create Maximum Number, Reconstruct
Itinerary, Self Crossing, and Palindrome Pairs. It verifies complete suffix
comparison, use of duplicate ticket occurrences, inclusive segment contact,
empty words, and both directions of ordered palindrome pairs. Palindrome
prefix/suffix flags use KMP and a reversed-word trie to meet the linear input
processing target. Stress tests cover 500-digit arrays, 300 tickets, 100,000
segments, 5,000 unique 300-character words, and 5,000 emitted palindrome pairs.
Exhaustive small-domain checks use independent index selection, ticket search,
segment intersections, and direct concatenation oracles.
Batch thirty-one adds Wiggle Sort II, an at-most-K-distinct-character window,
Power of Four, Integer Break, in-place Reverse String, and Reverse Vowels.
Strict wiggle judging accepts any original-value permutation alternating `<, >`
and rejects equal neighbors, changed duplicate counts, and returned copies.
The problem pane distinguishes this from ordinary non-strict Wiggle Sort.
Schema tests also reject malformed expectations and mixed comparison modes.
Independent small-domain checks and source-scale cases cover 50,000-value wiggles,
50,000-character windows, 100,000-character mutations, and 300,000-character
vowel scans. All 225 imports were revalidated against the updated judge contract.
Batch thirty-two adds Intersection of Two Arrays I/II, Android Unlock Patterns,
Russian Doll Envelopes, Line Reflection, Sort Transformed Array, Bomb Enemy,
Water and Jug Problem, Plus One Linked List, and Range Addition. The two
intersections preserve their different duplicate-count contracts. The unlock
oracle exhausts all dot permutations and all 81 length-bound pairs are tested.
Other regressions cover all 19,683 three-by-three bomb grids, equal envelope
dimensions, coordinate-set reflection, convex/concave/linear transformations,
actual jug-state reachability, linked-node carry overflow, and inclusive range
boundaries. Stress fixtures include 100,000 envelopes, 500-by-500 bomb grids,
100-digit linked numbers, and 10,000 updates over 100,000 array positions.
The linked-list, recursion, and binary-search tags retain weak-topic priority.
All 326 handoff-catalog entries keep their content, versions, and progress IDs.
Batch thirty-three adds Max Sum of Rectangle No Larger Than K, Find Leaves of
Binary Tree, Valid Perfect Square, Sum of Two Integers, Super Pow, Guess Number
Higher or Lower II, Wiggle Subsequence, Combination Sum IV, and Kth Smallest
Element in a Sorted Matrix. Leaf removal uses actual TreeNode inputs and an
ordered-group comparator: values within a round may be rearranged, but rounds
must remain chronological and duplicate node values are preserved. The UI
explains this beside the examples and labels failure evidence as one valid
output. Combination Sum IV explicitly counts ordered sequences, unlike coin
combinations; Guess Number II is ordinary minimax computation, not an interactive
judge. Exhaustive tests cover small rectangles, tree shapes, signed sums, wiggle
subsequences, ordered sequences, and matrix ranks. Stress fixtures cover 100-by-100
rectangles, 100-node chains, 2,000-digit exponents, n=200 guessing games, and
300-by-300 sorted matrices. All 244 imports were revalidated after the new
comparison mode. All previously published 336 entries retain their IDs and content.
Batch thirty-four adds Sort List, Max Points on a Line, Binary Tree Upside Down,
Maximum Gap, Reverse Words in a String II, Rotate Array, and Remove Linked List
Elements. Independent regressions exhaust short lists, grid-point subsets, every
valid upside-down tree shape through ten nodes, small bucket-gap arrays, word
sequences, rotations, and deletions. Source-scale fixtures include 50,000-node
sorts and 100,000-element mutation/bucket exercises. The recursive tree transform
checks original-node order even when all values match. Character-array reversal
and in-place rotation are observably distinct from the existing string/list-returning
exercises: a returned copy does not satisfy their mutation contracts. No existing
problem content, IDs, saved progress, or frozen handoff tags changed.
Batch thirty-five adds Recover Binary Search Tree with the source's exact
value-swapping contract. A new tree-structure policy permits changed integer
values but preserves every original left/right link; copied nodes and swapped
node positions fail even if the displayed tree is correct. Restored temporary
Morris threads are allowed. The constant-space reference handles 1,000-node
chains, and exhaustive tests cover every swapped pair on every tree shape through
seven nodes. All imports are revalidated when this shared judge contract changes.
Batch thirty-six adds Lexicographical Numbers, Longest Absolute File Path,
Elimination Game, UTF-8 Validation, Decode String, Longest Substring with At Least
K Repeating Characters, Integer Replacement, Remove K Digits, Frog Jump, and
Valid Word Abbreviation. Nested decoding and recursive frequency splitting retain
weak-topic review coverage; the Hard frog exercise tracks both position and last
jump. The filesystem exercise processes newline/tab-encoded text only. UTF-8
grading explicitly follows the source's byte-prefix patterns rather than adding
Unicode scalar-value restrictions. Exhaustive small-domain regressions and
source-sized fixtures cover up to 100,000 decoded characters/digits and 2,000
stones. Abbreviation validity is a separate boolean query from the existing
all-abbreviations generator. The judge and all previous problem IDs are unchanged.
Batch thirty-seven adds 4Sum, word-concatenation windows, numeric Permutations II,
Scramble String, Trapping Rain Water II, Split Array Largest Sum, Arithmetic
Slices, and Third Maximum Number. Four are Hard problems. The permutation judge
allows reordering answers but preserves order inside each row and rejects
duplicate rows. Independent checks enumerate permutations, split-tree outputs,
contiguous cuts, and water layers. Exhaustive short-domain regressions and
source-scale fixtures include 40,320 permutations, 200-by-200 basins, 5,000
repeated words, and 1,000-element partition searches. Recursive permutation/
scramble and binary-search exercises retain weak-topic priorities. Existing
problem IDs, content, progress, and the 363-problem handoff tag remain unchanged.
Batch thirty-eight adds Add Strings, Partition Equal Subset Sum, Pacific Atlantic
Water Flow, Sentence Screen Fitting, Battleships in a Board, Strong Password
Checker, Maximum XOR of Two Numbers, Reconstruct Original Digits, and Longest
Repeating Character Replacement. Ocean traversal retains the stronger recursive-
matrix review priority, with an explicit DFS stack for 40,000-cell plateaus.
The password puzzle's minimum-edit formula is checked against a separate exact
edit-distance automaton search and literal small-alphabet edits, not another
copy of the same formula. Source-scale tests cover 10,000-digit addition,
20,000-by-20,000 screen counts, 200,000 XOR inputs, and 100,000-character windows.
Coordinate lists may be reordered, but swapping row/column or duplicating cells
fails. Existing content, progress IDs, and all handoff tags remain unchanged.
Batch thirty-nine adds Valid Word Square, recursive Word Squares, Minimum Genetic
Mutation, Find Right Interval, Path Sum III, Find All Anagrams in a String,
Ternary Expression Parser, K-th Smallest in Lexicographical Order, in-place
String Compression, forward-digit Add Two Numbers II, and Arithmetic Slices II.
Tests preserve ragged mirrored rows, dictionary-word reuse, same-chain tree
prefixes, right-associated conditionals, and index-distinct gapped subsequences.
String Compression grades the actual modified character prefix and integer count,
including multi-digit runs; the unused tail is ignored. It is distinct from the
original string-returning run encoder. Forward-digit linked addition is also
distinct from reverse-digit addition. Independent checks include all small gene
banks, decimal digit-DP ranks up to a billion, 1,000-node chains, 2,499 nested
conditions, every single-run length through 2,000, and 100-digit linked inputs.
Linked-list, binary-search, and recursion review priorities remain active.
No shared judge change was needed, and all 380 handoff problems retain their
content, versions, and progress IDs.
Batch forty adds Delete Node in a BST, Circular Array Loop, Can I Win, and Count
The Repetitions. The new BST-deletion comparator accepts any strict BST containing
exactly the surviving input values; predecessor/successor choices and unbalanced
shapes are valid. It rejects missing/extra/noninteger values and malformed trees.
Examples and failure feedback explain that the displayed shape is only one valid
output. The iterative reference supports 10,000-node chains. Circular-loop tests
separate same-direction multi-node cycles from mixed-direction and self cycles,
and audit linear-time path clearing. Game minimax is checked against independent
retrograde tables and small literal game trees. Repetition matching preserves
partial matches across source blocks and skips cycles without expanding up to
100 million characters; expanded-string and binary-lifting oracles cross-check it.
All 294 imports were revalidated under the shared judge extension, with refreshed
overlap proofs. Prior problem content, IDs, progress, and transfer tags are unchanged.
Batch forty-one adds Number of Boomerangs, Find All Numbers Disappeared in an
Array, Minimum Number of Arrows to Burst Balloons, both Minimum Moves to Equal
Array Elements variants, 4Sum II, Assign Cookies, 132 Pattern, Repeated Substring
Pattern, Hamming Distance, Unique Substrings in Wraparound String, and Validate
IP Address. Examples distinguish ordered Euclidean triples, inclusive endpoints,
index multiplicities, nonadjacent strict patterns, and different move operations.
IP validation intentionally rejects compressed and embedded IPv6 notation; missing
values accept reordered results but reject duplicates. Independent checks exhaust
small grids, endpoint hitting sets, literal move states, bipartite matchings,
short strings, bit pairs, and decimal/hex grammars. Source-scale fixtures include
200,000-element stacks, 100,000-element arrays/strings, 500-point geometry, and
1.6 billion counted index tuples without materializing all tuples.
Batch forty-two adds Concatenated Words, Matchsticks to Square, Ones and Zeroes,
and Heaters. Recursive segmentation must use at least two shorter words and may
reuse them; four-side partition requires backtracking, not just divisibility or
greedy placement. Binary-string selection tracks separate zero/one budgets,
counts duplicate indices separately, and forbids repeated use of one entry.
Heater coverage binary-searches both neighbors for each house and takes the
worst nearest distance. Independent checks enumerate string cuts, literal side
assignments, subset masks, and all house-heater pairs. Large tests cover 10,000
unique dictionary words/100,000 characters, 15 sticks, 600 binary strings, and
30,000 houses/heaters. A missing greedy counterexample and a slow wrong fixture
blocked initial validation until repaired; neither quarantined version was
published. Recursion/search review boosts and Hard prerequisite gates remain
active. All previously published problem IDs and content remain unchanged.
Batch forty-three adds Encode String with Shortest Length and a flexible
`shortest_encoding` comparator. Answers must decode to the complete input and
match the independently verified optimal length; `10[a]`, `a9[a]`, `9[a]a`, and
`5[aa]` all pass for ten a characters. Literal text is required when encoding
saves no space. A bounded parser rejects malformed syntax and excessive
expansion before allocating repeated strings, without evaluating submitted text.
Schema checks bind expected encodings to the actual input, and UI examples and
failure details identify the displayed answer as one valid output. An exhaustive
grammar constructor checks both native and worker decoders independently; parse-
tree enumeration checks 500 seeded inputs and exhaustive short binary strings.
The 150-character and nested-repeat boundaries are included. Every imported
problem is revalidated after this shared-judge extension; published IDs, content,
saved progress, and transfer tags remain unchanged.
Of the 74 overlaps, 69 map to original exercises and five map to approved
imports. Unique-only Permutations (46) maps to numeric Permutations II (47):
its full unique-input domain is covered, with 500 independent permutation checks,
the original sample, and all 720 outputs on six-element boundaries. This is
distinct from the original string-returning permutation exercise.
Unique-only rotated minimum (153) uses the existing duplicate-aware
entry (154), whose reference still takes logarithmic element reads for unique
values. Its separate overlap report verifies 500 seeded cases, the workbook
sample, and 5,000-element boundaries. No second progress ID is introduced.
Smallest Subsequence of Distinct Characters (1081) maps to Remove Duplicate
Letters (316): both retain each distinct letter once in the smallest possible
order-preserving subsequence. Its report checks the workbook sample, 500
independent subsequence oracles, and the source's 1,000-character boundary.
Bulb Switcher (319) maps to integer square root (69): a bulb is toggled once per
divisor and stays on exactly at perfect-square positions. Its proof checks 500
literal round-by-round simulations, 500 full-domain square enumerations, and
boundaries through n=1,000,000,000. The existing input domain covers this source.
Minimum Bit Flips to Convert Number (2220) maps to Hamming Distance (461): each
differing bit needs exactly one flip. The target includes the complete 0..10^9
source domain, verified on 500 seeded inputs and 64 sample/boundary cases.
Maximum Matching of Players With Trainers (2410) remains pending: it shares the
Assign Cookies behavior but permits 100,000 items rather than 30,000. A documented
domain expansion and source-scale proof are needed before merging that record.
After changing an overlap target or its judge contract, revalidate the target,
run `.venv/bin/python -m code_practice.reconcile_overlaps`, then repackage.
Missing or stale overlap evidence blocks packaging; studying uses only the
already packaged catalog and never runs these offline checks at startup.
Maximum-size deterministic cases also run in real Chrome/Pyodide during verification.
Node-swapping/reversal contracts also reject value rewriting in place of node
rewiring. Tree outputs preserve sparse structure and reject cycles. Reproduce:

```bash
.venv/bin/python -m code_practice.build_import_batch
.venv/bin/python -m code_practice.reconcile_overlaps
.venv/bin/python -m code_practice.package_catalog
```

For a bounded resume, pass source IDs, for example
`.venv/bin/python -m code_practice.build_import_batch --ids 24 92 129`.
Each problem validates in its own process with a 30-second default limit.
Ledger, report, and candidate files are replaced atomically after writing, so
an interrupted save leaves the previous complete file available.
Timeouts, inconsistent workbook samples, schema errors, oracle disagreements,
and undetected incorrect solutions quarantine the candidate instead of
publishing it. Reports are tied to the exact content and judge-contract hashes.
Judge changes require revalidation of existing imports before repackaging;
the current in-place, selected-TreeNode, and selected-ListNode extensions have
been checked against every reviewed batch. The current package contains 412 problems; future
partially reviewed batches are not exposed.

Only records with successful, content-hash-matched validation reports enter the
package. Quarantined and pending candidates are excluded. Packaging never opens
or replaces the progress database. The workbook and external source checkout
are needed only to repeat extraction, not to study or run the published app.

On another computer, transfer/update the project including `catalog_data/`,
install dependencies, and run `./run_local.sh`. Keep the destination's live
database in its existing persistent location. Restart the backend after a catalog
update. Do not copy this laptop's `data/` over an existing destination database.
Both Monaco and Pyodide assets are bundled during the frontend build; normal
studying does not require a CDN or internet connection after dependencies install.
Use `./backup_data.sh` before an upgrade. To restore, stop the backend and copy
the selected backup to the configured `CODE_PRACTICE_DB` path, then restart.

Development validation includes `.venv/bin/python -m pytest` and
`node scripts/verify_catalog_browser.mjs` (requires Playwright and Chrome).
The browser check uses a temporary database, exercises real Pyodide workers,
checks the editor with external HTTP requests blocked, restarts the backend,
and performs 100 real HTTP requests per benchmark route. On macOS/Linux it records
the OS-reported backend peak RSS over each complete server run, excluding the
browser and benchmark driver. Install dependencies and build the frontend first.
Its report is `catalog_import/benchmarks/current.json`; until all imports finish,
this is an interim measurement, not the final full-catalog performance gate.

Source provenance: workbook filename/hash and row numbers are retained in the
ledger. `catalog_import/sources.jsonl` records LeetCode URLs and the exact
[doocs/leetcode](https://github.com/doocs/leetcode) source revision, descriptions,
and candidate implementations used for review. That source snapshot retains its
CC BY-SA 4.0 attribution/license in `catalog_import/SOURCE_LICENSE.txt` and
`catalog_import/ATTRIBUTION.md`. Source candidates are not executed by the app.

## Private website and one-time progress transfer

The tracked `seed_data/initial_progress.db` snapshot transfers the owner's current progress to the deployment Mac once. Production copies it only when its persistent runtime database does not yet exist. New online progress is then stored on the deployment Mac and is never overwritten by the seed or later Git pulls.

The private website mode reuses the existing NSY sign-in session and keeps FastAPI bound to localhost behind Cloudflare Tunnel. Complete installation, PM2, authentication, persistence, backup, and update instructions are in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Validate the project

```bash
.venv/bin/python -m pytest
npm --prefix frontend test
npm --prefix frontend run build
```

## Generate question variants

Generation is optional and never affects normal study or judging.

```bash
.venv/bin/python -m code_practice.generate create --seed pair-sum-indices --count 3
.venv/bin/python -m code_practice.generate list
.venv/bin/python -m code_practice.generate validate --id generated-problem-id
.venv/bin/python -m code_practice.generate approve --id generated-problem-id
```

Generated problems remain drafts until validation passes and you explicitly approve them. Restart the app after approval to refresh the catalog. You can also import a JSON draft with `python -m code_practice.generate import --file draft.json`.

## Project boundaries

- One owner, using either local mode or an authenticated private website
- Python function-signature problems only
- One-time seed transfer to a persistent deployment-host SQLite database; no ongoing two-way database synchronization
- Public deployment requires the shared NSY sign-in session and a localhost-only backend
- No server-side execution of submitted answers
- Optional Codex coaching never blocks offline studying
