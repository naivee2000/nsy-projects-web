# Projects

Each project gets exactly one top-level folder here:

```text
projects/<project-slug>/
```

Put that project's app code, docs, local runner scripts, test files, and deployment templates inside its own folder. This keeps the repo easy to scan as more projects are added.

Current projects:

- `dem-claim/` - DEM claim Excel workflow for turning load/discharge documents into fixed-format claim workbooks.
- `Car Compare/` - authenticated vehicle depreciation research workspace served at `carcompare.nsyprojects.com`. Start with `Car Compare/docs/DEPLOYMENT.md` on a website host, `Car Compare/docs/CODEX_CONTEXT.md` for a new Codex task, and `Car Compare/docs/PERFORMANCE_ACCURACY_BENCHMARK.md` for the portable acceptance gate.
- `Stock Strategy Test/` - public Long-Term Stock Allocation Lab served at `strategy.nsyprojects.com`. It includes no-login demo and free automatic tests, plus a protected quota-aware history vault and deployment/licensing guidance in `Stock Strategy Test/docs/DEPLOYMENT.md`.
- `Python Study App/` - Code Practice Lab, a private Python interview-practice app with 1,259 runnable problems so far, recursion exercises from easy through hard, a Pyodide judge, visible test tracing, progressive hints, mastery tracking, saved drafts, and persistent SQLite progress. Its 3,629-row workbook expansion remains unfinished. It runs locally without login or as an authenticated personal website whose backend remains on `127.0.0.1` behind the existing tunnel. The [430-problem handoff checklist](Python%20Study%20App/docs/RELEASE_430_CHECKPOINT.md) covers the frozen `python-study-430-checkpoint` release and updating the other computer without replacing its progress. The newer verified additions remain local development; they do not change the website without another explicit update.

## Python Study App

Start the complete frontend and backend with one command:

```bash
cd "projects/Python Study App"
./run_local.sh
```

Then open `http://127.0.0.1:8765`. Local study sessions require no login or cloud service. Private website deployment reuses the NSY sign-in session while still binding the backend only to the deployment computer's loopback interface.

After an unresolved run, the built-in offline coach provides small diagnostic nudges without giving away the answer. The optional **Ask Codex coach** button can send the current draft, problem description, and visible test evidence to the locally installed, ChatGPT-authenticated Codex CLI. Codex runs in an ephemeral read-only session, receives no reference solution, and its reply is filtered to reject complete solutions or replacement functions. If Codex is unavailable, unauthenticated, times out, or returns answer-like content, the app keeps the offline coaching response instead. This optional feature may require an internet connection even though the study app itself is local-only.

Inside a problem, drag the vertical divider between the instructions and Python editor to give either panel more room. Drag the horizontal divider below the Run/Submit bar to resize the code editor against the results and coaching area. Both splits are saved in browser storage, support arrow-key adjustments when focused, and reset to their default sizes when double-clicked.

The problem workspace has a true **Back** button. A problem opened from Today returns to Today, while a problem opened from the Library returns to the Library with its filters preserved.

Passing the two explained examples is labeled **Examples passed** and states that the code is correct for those shown cases. Submit then runs all hidden cases, with at least twelve per problem. Passed hidden cases stay summarized, while a failed hidden case has a clickable dropdown containing the test input, expected output, and the current code's output or error. A successful full submission persistently marks the problem **Passed** in the workspace header and problem library, and updates dashboard progress.

All 101 problems use two hand-curated visible examples instead of shared placeholder inputs. Each pair demonstrates the problem's defining rule plus a contrasting or boundary case, and the interface explains in plain language why each output follows from its input. Catalog tests require these explanations and verify representative regression cases such as balanced prefix sums, valid versus invalid mappings, invalid bracket nesting, linked-list splicing, and missing/repeated matrix values.

The original Easy catalog is benchmarked against reusable patterns in LeetCode's official Easy problems, while retaining original wording and implementations. A quality audit removed seven syntax-only exercises—including Range Span and Longest Word Length—and replaced them with Balanced Pivot Index, Word Pattern Bijection, Formable Word Total, Missing and Repeated Grid Values, Flood Fill Region, Deduplicate a Sorted Linked List, and Recursive Step Combinations. Merge Two Sorted Linked Lists was later added for dummy-head, tail-pointer, and existing-node splicing practice. Before workbook expansion, this original catalog contained 101 problems: 34 easy, 56 medium, and 11 advanced.

The library fetches 30 summaries at a time, with server-side search and filters for topic, difficulty, and passed/unsolved status. Problem details load on demand. Daily recommendations and the optional weekly challenge exclude problems already marked Passed, including accepted solutions older than the latest 500 attempts.

The workbook expansion currently accounts for 3,629 rows: 83 existing equivalents,
658 verified new problems, 155 documented design/interactive exclusions, 6 quarantined records,
and 2,727 pending records. Ordinary trees and linked lists remain included.
`Python Study App/catalog_import/ledger.json` is the resumable record; pending
content is not exposed as runnable. Every imported problem has two explained
examples, at least twelve distinct hidden tests, two rejected plausible incorrect
solutions, and 500 independent seeded oracle checks.

Imports span recursive grids, linked-node rewiring, tree traversal and paths,
binary search, backtracking, strings, greedy algorithms, and dynamic programming,
including ordinary Hard problems. Weak-topic priorities remain intact. The tenth
batch adds path simplification, duplicate-aware rotated search, Interleaving
String, Distinct Subsequences, unlimited/two-transaction stock problems, Gas
Station, and Candy. Deep-tree tests cover 5,000-node path enumeration and a
30,000-node maximum-path problem. The original Spiral Matrix ID retains progress
while version 2 explicitly covers rectangles. Batch details and interim benchmark
results are in `Python Study App/docs/CATALOG_EXPANSION.md`.

The judge also supports genuine in-place problems: modified arrays/matrices are
checked directly, and removal exercises check both the returned count and the
updated prefix. Unused tail values are ignored only when the problem permits it.
Eight new imports cover these contracts, including Rotate Image, Next Permutation,
and Merge Sorted Array. Existing return-value, tree, and linked-list problems
retain their interfaces; all imported references are revalidated after judge changes.
Batch twelve adds delete-all-duplicate linked nodes, stable linked-list
partitioning, Word Break, and recursive Word Break II. The latter returns all
complete dictionary sentences while allowing repeated use of the same word.
Batch thirteen covers consecutive values, minimum palindrome cuts, signed
singletons among triples, and postfix arithmetic with division toward zero.
Batch fourteen reconstructs trees from traversal arrays and captures surrounded
grid regions in place. TreeNode interfaces and recursive-grid review priorities
are retained, with 3,000-node chains, 200×200 grids, and exhaustive testing of
all 512 three-by-three X/O boards.
Batch fifteen adds Sudoku validation, numeric syntax, exact text justification,
and largest all-one matrix rectangles. The spreadsheet's collapsed-space output
for Text Justification is explicitly corrected, with original/corrected values
and source evidence preserved in its validation report. Tests reject unreviewed,
stale, or incorrect sample corrections.
Batch sixteen adds in-place tree flattening and linked-list reordering, retaining
the original TreeNode/ListNode objects and values. Identity-sensitive order
checks distinguish even equal-valued nodes. Stress cases contain 2,000 tree
nodes and 50,000 list nodes; every imported reference was revalidated after the
judge extension. Normal progress IDs and saved solutions remain unchanged.
Batch seventeen adds word reversal, maximum products, duplicate-aware rotated
minimum, two-character windows, exactly-one-edit checks, missing ranges, version
comparison, and Dungeon Game. Independent oracles and source-domain regressions
cover all eight, including 100,000-character windows, billion-wide intervals,
and 200×200 dungeons. Binary-search and recursive-grid review priorities remain.
Batch eighteen adds two Excel-column conversions, factorial zeroes, largest-number
ordering, overlapping repeated DNA sequences, and Hard Stock IV with a variable
transaction budget. Independent oracles include exact factorials, permutation
enumeration, sorted DNA windows, and exhaustive legal buy/sell-day choices.
Regressions check all 10,001 factorial inputs and the column-label boundaries;
large tests cover 100,000 DNA characters and 1,000 stock prices.
Batch nineteen adds balanced BST construction from sorted arrays and linked
lists, complete-tree counting, and uniform-value subtree counting. The judge
accepts every balanced output shape that preserves the exact inorder values,
including duplicates; sample shapes are not mandatory. An exhaustive 626-shape
regression checks this rule. TreeNode/ListNode starters, recursive review boosts,
and all original progress IDs remain intact. All 126 imports were revalidated
after the new comparison mode, including 20,000-node conversion fixtures.
The original Tree Height problem keeps its ID and progress but advances to
version 2: an explicit stack replaces recursion that overflowed on long valid
chains. A breadth-first oracle, 500 seeded shapes, 20,000-node stress cases, and
version-1 progress/draft preservation tests cover the repair. This remains the
existing equivalent of LeetCode 104 rather than adding a duplicate problem.
Batch twenty adds fixed-width bit reversal, range AND, happy-number cycles,
prime counting, character isomorphism, minimum positive-sum windows, circular
house selection, shortest front-added palindromes, and recursive digit
combinations. It includes the five-million prime boundary and exhaustive checks
of all 480 digit-combination inputs. The Hard palindrome problem's prerequisites
can be mastered through the existing string-matching exercises.
Batch twenty-one adds recursive Word Search II, Skyline, Maximal Square, and
Rectangle Area. It checks 30,000 dictionary words, 10,000 buildings, and 300×300
matrices. Independent small-domain tests exhaust simple grid paths, building
multisets, binary squares, and rectangle unions, including degenerate rectangles.
The grid problem retains the stronger recursive-matrix review priority. Approval
remained blocked until a cell-reuse mistake was demonstrably rejected.
Batch twenty-two adds both nearby-duplicate window problems, both Basic
Calculators, Summary Ranges, Majority Element II, Number of Digit One, Product of
Array Except Self, Search a 2D Matrix II, and Different Ways to Add Parentheses.
It verifies inclusive index/value boundaries, negative buckets, 100,000-deep
parentheses, truncation toward zero, zero products, Catalan multiplicity, and
300×300 row-and-column-sorted matrices.
Batch twenty-three adds both one-pass word-distance contracts, all three
strobogrammatic-number problems, shifted-string grouping, Meeting Rooms, Factor
Combinations, Paint House, and Add Digits. It preserves the distinct-occurrence
rule, wraparound shifts, order-independent outputs, recursive generation through
length 14, inclusive 15-digit ranges, touching meetings, and O(1) digital roots.
Batch twenty-four adds both lowest-common-ancestor contracts, BST preorder
validation, binary-tree paths, 3Sum Smaller, Single Number III, Graph Valid Tree,
both Ugly Number problems, and Paint House II. The judge now passes actual selected
TreeNode references for `p` and `q`, requires an existing returned node, and rejects
tree mutation. Source-scale fixtures include 100,000-node trees, the 1,690th ugly
number, and large arrays, graphs, and painting grids. Recursive-tree and binary-
search review priorities remain active.
Batch twenty-five adds selected-node linked-list deletion, both palindrome-
permutation contracts, closest BST values for one and k results, number-to-English
conversion, both H-Index variants, Paint Fence, and Perfect Squares. Delete Node
keeps its one-parameter callable: the judge supplies the actual selected non-tail
ListNode, observes the original head, and rejects replacement nodes or changes to
unrelated nodes. Recursive palindrome/number wording and logarithmic sorted
H-Index practice preserve the owner's study priorities.
Batch twenty-six adds Wiggle Sort, Expression Add Operators, Move Zeroes,
Inorder Successor in BST, Walls and Gates, Find the Duplicate Number, Game of
Life, Word Pattern II, Nim Game, and both Flip Game problems. Flexible wiggle
outputs, optional successor results, and read-only array contracts are now
enforced consistently in Python and the browser worker. Exhaustive short-domain
checks cover wiggle arrangements, 3×3 life boards, and recursive game states;
large fixtures cover arrays, trees, grids, and duplicate cycles.
Batch twenty-seven adds Best Meeting Point, Binary Tree Longest Consecutive
Sequence, Bulls and Cows, Remove Invalid Parentheses, Smallest Rectangle
Enclosing Black Pixels, Number of Islands II, Additive Number, Stock With
Cooldown, Minimum Height Trees, and Sparse Matrix Multiplication. Exhaustive
small-domain and source-scale tests cover recursive trees, backtracking, binary
search, union-find, dynamic programming, graph trimming, and sparse matrices.
The interface audit now also records constructor-plus-query classes as deferred
design exercises without excluding ordinary tree or linked-list functions.
Batch twenty-eight adds Burst Balloons, Super Ugly Number, Binary Tree Vertical
Order Traversal, Count of Smaller Numbers After Self, Remove Duplicate Letters,
and Shortest Distance from All Buildings. Tests preserve changing balloon
neighbors, duplicate product suppression, tree-position ties, strict suffix
counts, subsequence order, and impassable building cells. Source-scale fixtures
include 300 balloons, 100,000 values, 100 primes, and 50-by-50 grids.
Batch twenty-nine adds Maximum Product of Word Lengths, Generalized Abbreviation,
Power of Three, Count of Range Sum, Longest Increasing Path in a Matrix, Patching
Array, Verify Preorder Serialization, Largest BST Subtree, and House Robber III.
It covers recursive generation, signed prefix sums, greedy subset coverage, and
tree/grid dynamic programming, including a 40,000-cell path and 10,000-node
trees. Each has independent oracle checks and source-scale fixtures.
Batch thirty adds Create Maximum Number, Reconstruct Itinerary, Self Crossing,
and Palindrome Pairs. The tests cover suffix tie-breaking, repeated tickets,
segment touches and overlaps, empty-string pairs, and both index orders.
The palindrome reference combines linear prefix/suffix preprocessing with a
reversed-word trie. Maximum-size fixtures include 500-digit arrays, 300 tickets,
100,000 segments, and 5,000 unique 300-character words.
Batch thirty-one adds Wiggle Sort II, Longest Substring with At Most K Distinct
Characters, Power of Four, Integer Break, Reverse String, and Reverse Vowels.
The judge and instructions distinguish strict alternating inequalities from
ordinary Wiggle Sort, accepting alternative valid arrangements while rejecting
equal neighbors, changed values, and returned copies. The 225 imports at that
checkpoint were revalidated against the updated judge contract.
Batch thirty-two adds both array-intersection contracts, Android Unlock Patterns,
Russian Doll Envelopes, Line Reflection, Sort Transformed Array, Bomb Enemy,
Water and Jug Problem, Plus One Linked List, and Range Addition. It preserves
the distinction between unique and repeated intersections, all 81 unlock-length
ranges, exact vertical reflection of coordinate sets, combined jug volumes,
actual linked-node results, and inclusive range updates. Regressions include
all 19,683 three-by-three bomb grids and source-scale envelopes, grids, lists,
and updates. The frozen 326-problem tag and every previous problem ID are unchanged.
Batch thirty-three adds bounded rectangle sums, chronological tree-leaf rounds,
perfect-square detection, signed bitwise addition, large modular powers, minimax
guessing budgets, wiggle subsequences, ordered reusable sums, and sorted-matrix
rank selection. A new ordered-group comparator accepts leaf permutations within
each removal round while rejecting changed round order or duplicate counts.
All 244 imported references were revalidated against the updated judge; existing
problem content, progress IDs, and the 326-problem handoff tag remain unchanged.
Batch thirty-four adds bottom-up linked-list sorting, exact collinearity counts,
recursive upside-down tree rewiring, linear-time bucket gaps, in-place word and
array rearrangement, and linked-list element removal. Exhaustive regressions
cover short inputs and every valid upside-down tree shape through ten nodes;
large cases reach 50,000 list nodes and 100,000 array elements. Repeated values
do not relax original-node identity checks. The two mutation exercises remain
distinct from existing return-a-string/list contracts. All 345 checkpoint problems
retain their content and progress IDs, and neither handoff tag is moved.
Batch thirty-five adds Recover Binary Search Tree and a value-only tree mutation
contract. It rejects replacement nodes and changed child links even when the
displayed values look correct, while allowing temporary Morris traversal links
that are fully restored. The reference meets the O(1)-space follow-up and handles
1,000-node chains. Exhaustive tests cover every swapped pair across all binary
tree shapes through seven nodes. Shared-judge changes trigger full import
revalidation before packaging. No push to GitHub occurs without an explicit request.
Batch thirty-six adds decimal-prefix traversal, abstract filesystem path lengths,
alternating elimination, structural byte validation, nested decoding, recursive
substring-frequency splitting, integer replacement, greedy digit removal, Hard
Frog Jump, and abbreviation validity. Tests distinguish actual newline/tab
encoding from literal letters, the exercise's byte-prefix rules from stricter
Unicode decoding, contiguous windows from global counts, and frog position/jump
states from greedy choices. Source-sized fixtures reach 100,000 output characters
or digits and 2,000 stones; all 353 earlier problems retain identical IDs and content.
Batch thirty-seven adds 4Sum, word-concatenation windows, numeric Permutations II,
recursive Scramble String, 2D trapped water, partition-capacity binary search,
Arithmetic Slices, and Third Maximum Number. Four are Hard problems. Tests keep
permutation row order and duplicate counts, exhaust small word/map/partition
domains, and cover 40,320 permutations and 200-by-200 terrain maps. All 363
checkpoint problems remain unchanged. Unique-only numeric Permutations (46)
maps to Permutations II (47) after 500 independent checks and six-element output
boundaries, without introducing a duplicate study/progress entry.
Batch thirty-eight adds decimal string addition, equal subset partitioning,
Pacific/Atlantic reverse-flow traversal, cyclic screen fitting, battleship starts,
minimum password edits, maximum XOR, digit reconstruction, and replacement
windows. Matrix recursion review priority remains intact. Independent edit search
validates the Hard password formula; exhaustive small-domain checks and large
fixtures cover 40,000-cell grids, 200,000 XOR values, and 100,000-character text.
No judge change was needed, and all 371 earlier problems keep their content and IDs.
An earlier overlap audit covered 69 original exercises plus four approved imports that
also cover other workbook contracts. Rotated minimum 153 maps to 154 after
500 seeded correctness/logarithmic-read checks, without a duplicate progress ID.
Smallest Subsequence of Distinct Characters (1081) maps to Remove Duplicate
Letters (316), supported by 500 independent subsequence oracle comparisons,
the source sample, and 1,000-character boundaries.
Bulb Switcher (319) maps to integer square root (69): exactly the perfect-square
bulb positions remain on. Evidence includes 500 literal toggle simulations,
500 full-domain square counts, and n=1,000,000,000 boundaries.
Run `.venv/bin/python -m code_practice.reconcile_overlaps` and
`.venv/bin/python -m code_practice.reconcile_original_overlaps` from the app folder
after revalidating changed overlap targets and before repackaging. Stale source,
target, judge, or proof data blocks publication rather than silently retaining
an unproved equivalence. Normal studying does not execute these offline checks.

Published content is portable under `Python Study App/catalog_data/`; startup does not execute reference solutions. Transfer this folder with the app, retain the destination computer's existing progress database, and restart after updates. Rebuild packaged content with `.venv/bin/python -m code_practice.package_catalog` from the app folder; that command never opens or replaces progress. Backup and restoration instructions and the interim browser benchmark command are in the app README. Full import and full-catalog performance acceptance remain unfinished.

The 430-problem checkpoint freezes verified content for handoff; it does not declare the workbook goal complete. It includes the eleven validated batch-46/47/48 additions since the earlier 419-problem release. Batch 39 covers word-square checks/search, gene-bank paths, interval binary search, tree path sums, anagram windows, nested conditionals, decimal rank search, character-prefix mutation, forward-digit linked addition, and arithmetic subsequences. Batch 40 adds BST deletion, circular-array loops, finite-pool minimax, and repeated-subsequence cycle skipping. The new deletion judge accepts any strict BST containing exactly the surviving values, including unbalanced shapes; all 294 then-published imports were revalidated. Batch 41 adds twelve problems covering ordered geometry, missing values, interval arrows, two array-move operations, 4Sum II, resource matching, strict 132 patterns, string repetition, bit distance, cyclic substrings, and strict IP grammar. Minimum Bit Flips is a verified Hamming Distance equivalent rather than a duplicate; the five then-current imported-target overlap proofs were refreshed. Players/Trainers now maps to version 2 of Assign Cookies, with a documented 100,000-item bound and independent equivalence proof. Existing progress IDs remain intact; two domain upgrades raise problem versions without erasing old attempts. Backups respect `CODE_PRACTICE_DB` and `CODE_PRACTICE_DATA_DIR`, with an optional external `CODE_PRACTICE_BACKUP_DIR`. Continuing catalog development on this laptop cannot affect the website until another explicit code update. Runtime progress and the existing seed snapshot were not changed. All seven earlier handoff tags remain unchanged; the eleven verified batch-46/47/48 additions are included in the new frozen release.

Monaco editor and Pyodide runtime assets are included in the local frontend build, so studying needs no CDN after installation. Import validation runs in bounded per-problem processes and quarantines failures. The Chrome check uses a temporary progress database, blocks external requests, tests restart persistence, measures 100 requests per API route, and records OS-reported backend peak memory. No deployment or push is part of this expansion work.

The Today page assigns one fixed workload-capped set per local calendar day: five Easy problems; normally two Medium plus one Easy (or at most three Medium when no Easy remains); or one Hard plus at most one Medium. Completed items disappear from that fixed set without being replaced. After the final assigned problem passes, the app shows a finished message and waits until the next day to create another set. A separate fixed daily review checklist selects up to five previously passed problems. Review priority combines spaced-review due dates with difficulty, failures after the first successful solve, time spent relative to the estimate, and whether the latest attempt failed. A full five-problem review uses at most three focus slots for linked lists, recursion, binary search, and recursive matrix/grid traversal, reserving two slots for other completed topics whenever available; hint usage does not influence review selection. A review disappears after another successful full submission that day, is not replaced, and the section shows a finished message after every assigned review is checked.

Batch 42 adds Concatenated Words, Matchsticks to Square, Ones and Zeroes, and
Heaters. Regressions distinguish multi-piece word reuse, four equal sides,
separate zero/one budgets with duplicate indices, and worst-house coverage.
All four pass 500 independent oracle comparisons plus source-scale tests;
recursion and binary-search review priorities and Hard prerequisite gates remain.
The 407 preceding catalog entries retain identical content and progress IDs.

Batch 43 adds shortest string encoding with a bounded, noncanonical-output judge.
Different optimal strings pass if they decode to the exact input and share the
minimum length. No-space-saving cases must remain literal. Tests cover nested
repeats, alternate optima, malformed grammar, expansion limits, independent
grammar construction, and 500 parse-tree oracle inputs. UI examples and failure
evidence say “One valid output.” All 311 imports are revalidated under the new
judge contract; prior catalog content and progress IDs remain unchanged.

Batch 44 adds Convex Polygon, Number Complement, Total Hamming Distance,
Magical String, License Key Formatting, and The Maze. Independent checks cover
simple boundary geometry, significant-bit width, repeated index pairs, partial
runs, right-aligned groups, and all 9,216 valid endpoint pairs over every 3-by-3
maze wall pattern. Stress fixtures reach 10,000 polygon vertices/array entries,
100,000 characters, and 100-by-100 rolling mazes. The ball must stop at the target,
not merely pass through it; recursive-grid review priority is retained.
Source 1009 now maps to Number Complement version 2, with an explicit zero input
that returns one. Source 2410 maps to Assign Cookies version 2, extending its
array bound to 100,000. Both mappings pass 500 independent oracle checks and
source-boundary tests. Those upgrades kept the catalog at 418 distinct problems; no duplicate
progress IDs are created. Version-1 Passed status and drafts survive the upgrades.

Batch 45 adds Sliding Window Median, with ordered decimal-list judging at an
absolute tolerance of 0.00001. It follows the complete source rather than the
workbook summary's looser rounding. Tests reject stale windows, lower-middle-only
answers, wrong order/length, booleans, strings, and non-finite values. Fenwick
frequency ranks support 100,000-value inputs; independent sorted-window checks
cover 500 seeded inputs and exhaustive short arrays. Helper classes are allowed
behind the function entry point. All 318 imports and seven overlap proofs are
revalidated under the new judge; existing problem content and progress IDs remain.

Batch 46 adds Smallest Good Base, Find Permutation, Predict the Winner,
Max Consecutive Ones II, Non-decreasing Subsequences, and Construct the Rectangle.
Tests distinguish optimal answers from merely valid answers and preserve ties,
equal subsequence values, original index order, and duplicate-free output rows.
Game and subsequence recursion retain the weak-topic review priority. Streaming
one-flip checks need no stored prefix. Independent exhaustive regressions and
source-scale fixtures cover exact 10^18 bases, 100,000-entry inputs, and 32,752
subsequences. All 419 checkpoint definitions and progress IDs remain unchanged.

Batch 47 adds Max Consecutive Ones, Reverse Pairs, Target Sum, and Diagonal Traverse.
Tests preserve strict doubled comparisons for negative values, distinct plus/minus
zero expressions, and rectangular diagonal direction. Recursive pair/sign problems
retain weak-topic review priority. Teemo Attacking and Next Greater Element I map
to the existing Total Covered Length and Next Greater Values exercises, using
interval conversion and query projection. Each mapping has 500 independent checks,
the source sample, and full-size fixtures; stale proofs block packaging. Regenerate
these with `.venv/bin/python -m code_practice.reconcile_original_overlaps` from the
app folder. All 425 preceding problem definitions and progress IDs remain unchanged.

Batch 48 adds Zuma Game, including preparatory insertions that remove nothing
immediately and complete multi-group chain reactions. Exact search retains hand
inventory and uses an independently checked interval lower bound for difficult
five-color cases. Tests cover 500 seeded inputs, 1,566 exhaustive small games,
and six full-size fixtures; a separate relaxed deletion search checks the bound.
Recursion review priority is retained, and all 429 previous definitions and
progress IDs remain unchanged.

Batch 49 adds The Maze II and III, IPO, Next Greater Element II, and Freedom
Trail. Weighted rolling paths distinguish stopping at walls from entering holes;
other tasks cover affordable one-time projects, circular strict successors,
and recursive ring-position choices. Every problem has two explained examples,
at least twelve hidden tests, two rejected wrong algorithms, 500 oracle checks,
and source-scale fixtures. Exhaustive small-domain regressions cover mazes,
project schedules, signed circular arrays, and ring/key combinations. All 430
prior definitions and progress IDs are unchanged. The five additions remain
outside the frozen 430-problem transfer tag; nothing was pushed or deployed.

Batch 50 adds four tree problems: BST modes, frequent subtree sums, bottom-left
value, and row maxima. Explicit traversal frames support 10,000 nodes, preserve
input nodes, and retain recursion study/review coverage. Every import has two
explained examples, at least twelve hidden tests, two rejected wrong algorithms,
and 500 oracle comparisons. Fibonacci 509 maps to the existing recursive step
count by an index/base-case adaptation, verified over all 31 valid inputs and
500 seeded cases; no duplicate progress ID is created. The three original-target
proofs are reproducible with `python -m code_practice.reconcile_original_overlaps`.
These four additions remain outside the frozen 430-problem transfer tag.

Batch 51 adds Keyboard Row, Base 7, Relative Ranks, Perfect Number, Longest
Palindromic Subsequence, and Super Washing Machines. Each has two explained
examples, at least twelve hidden tests, two rejected wrong algorithms, and
500 oracle comparisons. Additional checks cover exhaustive small inputs,
factorization and divisor-sieve certificates, and independent time-expanded
network flow for simultaneous washing moves. The largest fixtures retain the
source limits, including a 250,000,000-round balancing answer computed directly.
All 439 previous definitions and progress IDs are unchanged. The six additions
remain outside the frozen 430-problem transfer tag; nothing was pushed or deployed.

Batch 52 adds Detect Capital, Longest Uncommon Subsequence II, Longest Word in
Dictionary through Deleting, and Beautiful Arrangement. The recursive arrangement
problem tests all 15 legal inputs, including thirteen distinct hidden cases;
independent inclusion-exclusion and literal permutations verify its count.
All four imports pass 500 oracle checks and reject two wrong algorithms each.
Uncommon Subsequence II explicitly supports length-100 words to cover source 521;
500 full-range LCS checks and 500 enumerated-subsequence checks prove the overlap.
Contiguous Array (525) maps to the existing target-sum exercise after changing
binary zeros to -1; full 100,000-entry fixtures and 500 independent oracle cases
pass. All 445 preceding definitions and progress IDs remain unchanged. The four
new problems remain outside the frozen 430 transfer tag.

Batch 53 adds Continuous Subarray Sum, Word Abbreviation, Minesweeper, and
Minimum Absolute Difference in BST. Every import passes 500 oracle comparisons
and rejects two wrong algorithms. Exhaustive short-array/word-set checks, all
three-by-three mine layouts with every click, repeated reveals, and BST multiset
shapes supplement full-size fixtures: 100,000 integers, 400 words of length 400,
50-by-50 boards, and 10,000-node trees. The mine oracle uses connected components;
the abbreviation oracle simulates collisions; the BST oracle compares every pair.
Source 783 maps to the same BST problem with a full-domain proof. All 449 previous
definitions and progress IDs are unchanged, and these four imports remain
outside the frozen 430 transfer tag.

Batch fifty-four adds K-diff Pairs in an Array, Lonely Pixel II, Complex Number
Multiplication, Minimum Time Difference, Single Element in a Sorted Array, and
Reverse String II. Each has two explained examples, at least twelve distinct
hidden tests, two rejected wrong algorithms, and 500 independent oracle checks.
Additional regressions exhaust small signed arrays, binary pixel rectangles,
complex sign combinations, every circular clock gap, singleton positions, and
short string-block boundaries. Source-scale fixtures cover 500-by-500 boards,
20,000 clock entries, 99,999 sorted integers, and 10,000-character strings.
Lonely Pixel I (531) maps to the generalized pixel problem at target=1, with an
explicit 500-by-500 domain extension and independently proved full-source limits.
The sorted singleton remains distinct from unsorted Single Number: its required
logarithmic-time algorithm is verified by a strict element-read budget, which
rejects the linear XOR reference. This validates the reference's complexity;
the learner's ordinary judge still checks output and its execution deadline,
not an automatic proof of arbitrary submission complexity.
The 1,158-import checkpoint preserves all preceding definitions and progress IDs.
All 1,158 import reports and current overlap evidence match the 1,259-problem package.
The post-430 additions remain local development; the workbook ledger records 83
overlaps, 1,158 verified imports, 155 justified exclusions, 16 quarantined records,
and 2,217 pending records. At this checkpoint, 792 backend tests and 19 frontend
tests pass; Chrome/Pyodide validates 1,164 workbook-derived reference suites across
1,550 isolated judge runs, including wrong-answer rejection, timeout recovery,
restart persistence, and offline assets. Measured backend startup is 337 ms, peak
RSS is 269.688 MiB, and warm p95 API latency ranges from 1.346 ms to 2.039 ms over
100 requests per route. This is an interim checkpoint;
the full 3,629-record workbook goal remains unfinished.

Linked-list and tree problems show the full `ListNode` or `TreeNode` class definition above the function in the editable code pane. The app also prepends the required class when reopening an older saved draft that predates this feature.

The read-only tree judge now checks original node identities, exact child links,
and value types as well as serialized values. Identical-looking replacement
children and equal-valued node swaps are rejected; correctly restored Morris
threads and falsey original nodes remain accepted. All 352 import reports and
thirteen detailed overlap proofs have been refreshed for this shared change.

The private repository also carries a one-time SQLite seed containing an earlier owner progress snapshot, not live-synced progress. On the first website start, it is copied to a persistent directory outside the checkout. Later online progress lives only in that deployment-host database and survives restarts and Git pulls without being overwritten by the seed.

Detailed setup, testing, backups, architecture, and coaching safeguards are documented in `Python Study App/README.md`; deployment and progress-transfer instructions are in `Python Study App/docs/DEPLOYMENT.md`.
