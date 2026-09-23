# Workbook catalog expansion

Status: in progress. Pending and quarantined records are not runnable imports.
The owner requested a stable handoff before resuming expansion. The frozen
430-problem checkpoint is documented in [RELEASE_430_CHECKPOINT.md](RELEASE_430_CHECKPOINT.md).
The counts below describe the current 459-problem development package, including
twenty-nine verified batch-49/50/51/52/53/54 additions since that release.
All earlier handoff tags and historical checklists remain unchanged. The owner can
transfer the frozen version while expansion continues from the current ledger.
New development does not change the other computer or authorize a push/deployment.

The source workbook has 3,629 unique problem names in rows 7–3635. The
scope includes ordinary functions, binary trees, linked lists, and Hard problems.
Multi-operation design exercises and interactive judge protocols are initially
excluded, with per-record evidence. A `Solution` wrapper alone is not a design
exercise. Unrecognized contracts remain pending rather than becoming exclusions.

## Delivery gates

1. Preserve every workbook row and its provenance in a resumable ledger. Review
   behavioral overlaps against the original 101 problems; retain their IDs.
2. Validate representative ordinary, linked-list, tree, and recursive-grid imports.
   Each needs two explained visible examples, twelve distinct hidden inputs,
   correct references, two plausible rejected algorithms, and 500 seeded oracle
   comparisons where practical. Record specific exceptions.
3. Publish only verified content into a portable catalog. Keep drafts, source
   candidates, validation reports, and the live progress database separate.
4. Paginate/search/filter on the server and load problem details on demand. Do not
   execute reference solutions during server startup or catalog listing.
5. Complete every eligible import, preserve progress through restart/upgrade,
   verify judge recovery and UI workflows, and benchmark the entire final catalog
   with at least 100 requests per endpoint (library p95 ≤300 ms; detail/dashboard
   p95 ≤500 ms). Report cold startup and peak memory.
6. Document portable installation, catalog upgrades, backup, and restoration in
   both READMEs. Do not deploy or push.

## Authoritative progress

`catalog_import/ledger.json` accounts for workbook rows. `pending` means work
remains; `excluded` is limited to the approved interface exclusions; `overlap`
records an existing equivalent and the behavioral decision; `imported` requires
a passing report tied to the exact content hash. Re-running extraction must not
erase completed validation work for unchanged source rows.

Source solutions are candidates, not independent oracles and not proof of
correctness. Generated tests must meet each problem's actual constraints.

## Current checkpoint

- All 3,629 workbook rows have portable source snapshots and ledger records.
- Current behavioral mapping: 83 existing equivalents (73 original exercises and
  ten approved imports). Static evidence identifies 155 approved-scope
  design/interactive exclusions; 3,033 rows remain pending.
- 358 new imports in fifty-four reviewed batches pass deterministic tests and
  500 independent oracle inputs each. The published catalog contains 459 problems.
- Batch fifty-four adds K-diff Pairs in an Array, Lonely Pixel II, Complex Number
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
  All 453 prior definitions and progress IDs remain unchanged. All 358 import
  reports and fourteen detailed overlap proofs match the current package.
  These six additions and the preceding twenty-three post-430 additions remain
  local development; the remaining 3,033 workbook records are still pending.
- Batch fifty-three imports 523, 527, 529, and 530: prefix-remainder length
  checks, minimal collision-free abbreviations, recursive mine-region reveals,
  and minimum BST value gaps. Each has two explained examples, at least twelve
  distinct hidden tests, two rejected wrong algorithms, and 500 oracle inputs.
  The abbreviation reference uses grouped counted tries; a separate oracle
  repeatedly expands colliding prefixes, and a pairwise longest-common-prefix
  certificate verifies 400-word, 400-character boundaries. The mine reference
  uses an explicit stack for the recursive reveal rule; an independent
  union-find component oracle determines blank regions and their numbered
  boundary. Tests exhaust all 512 three-by-three mine layouts and all nine clicks,
  preserve prior revealed cells over repeated moves, and accept a correctly
  updated copy as well as in-place output. BST input values/links remain read-only;
  all-pairs JSON-value enumeration checks the inorder reference, including
  non-parent/child closest pairs and equal-valued distinct nodes. Small BST
  multisets are checked in balanced and both chain shapes. Residue regressions
  exhaust short nonnegative arrays, preserve earliest remainder positions, and
  include zero sums, single-element rejections, and full 32-bit sums.
  Source-scale tests retain 100,000 array entries, 400 words of length 400,
  50-by-50 mine boards, and 10,000-node trees without recursion-limit changes.
  Source 783 explicitly names 530 as equivalent; 500 seeded source-domain BSTs
  and boundaries prove the mapping through the read-only TreeNode judge.
  All nine imported-target proofs were refreshed; all thirteen imported/original
  target proofs remain valid. All 449 preceding definitions and progress IDs
  remain unchanged. These four imports are outside the frozen 430 transfer tag.
  A post-suite adversarial probe showed that read-only serialization alone accepted
  an equal-looking replacement child. Native and browser judges now retain original
  nodes and verify exact child links plus value types before accepting a read-only
  TreeNode argument. Regressions reject replacements, equal-valued swaps, inserted
  nodes, and bool-for-int substitutions; falsey original nodes and restored Morris
  threads remain valid. All 352 imports passed full revalidation and all thirteen
  detailed overlap proofs were refreshed for this shared-judge change. The
  preceding 449 definitions remain byte-equivalent at their content hashes.
- Batch fifty-two imports 520, 522, 524, and 526: three capital patterns,
  unique input-position subsequence membership, dictionary deletion with lexical
  tie-breaking, and recursive arrangement counting. Every problem passes 500
  independent oracle checks, two wrong algorithms, two explained visible examples,
  and at least twelve distinct hidden tests. Beautiful Arrangement exhausts its
  whole n=1..15 domain with thirteen hidden inputs. A non-search inclusion-exclusion
  permanent independently counts bijective allowed assignments; literal permutation
  enumeration checks n=1..8. Additional regressions exhaust all case patterns
  through length twelve, small arrays of strings, and short binary deletion
  strings. Separate indexed-character searches verify full-size word domains.
  Source 522's original ten-character limit is explicitly extended to 100, allowing
  source 521 to map two strings into the same exercise without losing any source
  inputs. Its overlap proof includes 500 full-range LCS certificates and 500
  literal subsequence-enumeration cases. Source 525 maps binary zeros to -1 and
  uses the unchanged original longest-target-sum function with target zero:
  independent subarray enumeration verifies 500 seeded cases, exhaustive binary
  arrays through length eleven, and 100,000-entry boundary fixtures.
  All twelve imported/original target proofs were refreshed and remain bound to
  sources, targets, decisions, implementations, and the judge. No duplicate 521
  or 525 library ID is introduced. All 445 prior definitions and progress IDs
  remain unchanged; these four imports remain outside the 430 transfer tag.
- Batch fifty-one imports LeetCode 500, 504, 506–507, and 516–517: keyboard-row
  selection, signed base-seven notation, labels in original athlete order,
  proper-divisor equality, longest palindromic subsequence, and simultaneous
  washing-machine balancing. Word selection preserves original spelling and
  duplicate occurrences; this app ignores result ordering. The palindrome task
  forbids reordering but permits skipping characters, unlike its two wrong
  substring/multiset algorithms. The washing reference measures edge-flow and
  local outgoing bottlenecks, not absolute local deficits or simulated rounds.
  Every import has two explained examples, at least twelve distinct hidden
  tests, two logically rejected wrong algorithms, and 500 seeded oracle checks.
  Additional regressions exhaust mixed-case short words, signed base-seven
  conversions, all score permutations through seven athletes, and 714 small
  washing states. A divisor sieve checks all 1..20,000 values, independent
  factorization checks 500 full-range numbers, and the palindrome reference
  matches exhaustive binary strings through length nine plus a separate LCS
  DP on five length-1000 strings. A time-
  expanded integer max-flow oracle independently certifies optimum washing
  schedules for 104 cases by testing both the candidate horizon and one fewer
  round. Source-scale fixtures include 10,000 athletes/machines, 1000-character
  strings, the full signed base range, 100,000,000 divisor inputs, and a required
  250,000,000 washing rounds returned without simulation. All 439 preceding
  definitions and progress IDs are unchanged; recursion priorities and Hard
  prerequisites remain intact. No shared judge change was needed.
  Keyboard case rules and simultaneous-send semantics were cross-checked with
  the official [Keyboard Row](https://leetcode.com/problems/keyboard-row/description/)
  and [Super Washing Machines](https://leetcode.com/problems/super-washing-machines/description/)
  descriptions; normal studying does not fetch those pages.
- Batch fifty imports LeetCode 501, 508, 513, and 515: all BST modes, most
  frequent subtree sums, the deepest leftmost value, and maxima by tree depth.
  Explicit inorder/postorder/preorder frames handle 10,000-node chains without
  changing Python's recursion limit or mutating the supplied nodes. Tests cover
  duplicate keys on either BST side, tied outputs, negative sums and maxima,
  position versus numeric ordering, empty input only where permitted, and
  complete versus skewed trees. Each import has two explained examples, at
  least twelve distinct hidden cases, two logically rejected wrong algorithms,
  and 500 independent oracle comparisons. Additional regressions exhaust small
  BST multisets in three shapes, signed complete trees, and 722 signed trees
  over every shape through three levels. Existing recursion review priorities
  remain; all 435 preceding definitions and progress IDs are unchanged.
  Fibonacci (509) is an original-exercise equivalent, not another import:
  F(0)=0 and F(n)=step_count(n-1) for n>=1. A separate binomial-placement
  oracle checks all 31 source-domain inputs plus 500 seeded inputs. The
  original step-count problem stays at version 1 with its existing ID.
  All three original-target overlap proofs were regenerated after updating
  their shared checker; incomplete exhaustive-domain evidence blocks approval,
  and stale proofs still block packaging/re-extraction. No judge change was needed.
- Batch forty-nine imports LeetCode 499, 502–503, 505, and 514: lexicographic
  shortest hole instructions, affordable-project selection, circular strict
  successors, minimum rolling-stop distance, and recursive ring spelling.
  These retain their actual contracts rather than becoming ordinary grid BFS,
  linear successor queries, or locally greedy ring choices. Dijkstra references
  match independently constructed rays and synchronous Bellman-Ford; project
  choice matches exhaustive feasible schedules, circular answers match literal
  scans, and ring spelling matches unit-action rotation/press BFS. Additional
  regressions cover all 9,216 distinct empty endpoint pairs across every 3×3 maze,
  9,531 small project/capital/budget combinations, 97,655 signed arrays through
  length seven, and 3,468 binary ring/key combinations. Source-scale fixtures
  include 100×100 dense and 5,048-cell-travel snake mazes, 100,000 projects,
  10,000 circular values, and 100-character rings and keys. Each problem has
  two explained examples, at least twelve distinct hidden tests, two rejected
  plausible wrong algorithms, and 500 seeded oracle comparisons. Advanced
  prerequisites and the recursive ring's review priority are retained; all
  430 prior definitions and progress IDs are unchanged. The browser test's
  original partial-title selector now uses the exact Maze title to distinguish
  the newly added Maze II and Maze III cards. No shared judge change was needed.
- Batch forty-eight imports LeetCode 488, Zuma Game, as an ordinary named function.
  Memoized search retains board plus remaining hand, every non-equivalent gap,
  and preparatory moves. Local seam collapse resolves all chain reactions.
  An optimistic interval DP ignores hand inventory and forced reactions, giving
  a safe move lower bound; unlike run compression, it permits splitting original
  equal-color runs. The unoptimized search was too slow on two full-size boards
  with five different hand colors. The new bound resolves those cases without
  narrowing the input domain, removing legal moves, or extending the deadline.
  The final 500 seeded cases include 283 solvable and 217 impossible inputs
  (404 distinct inputs); 1,566 exhaustive stable binary-board/hand states through
  board length eight match an unpruned BFS oracle. Local versus global collapse
  and mirror/color/hand-order symmetries are checked separately. All 510 binary
  strings through length eight have matching interval-DP and independent paid
  partial-run-deletion bounds. Four full-size fixtures match literal BFS, and
  two adversarial impossible fixtures have independent shortest-path certificates
  proving even the relaxed game needs more than five moves. The 24 deterministic
  tests include two explained examples and 22 hidden cases. Both plausible wrong
  algorithms are rejected; advanced prerequisites and recursion priority remain.
  All 429 preceding problem definitions retain identical content and IDs.
- Batch forty-seven imports LeetCode 485, 493–494, and 498: no-flip consecutive
  runs, strict doubled-value reverse pairs, recursive sign-assignment counts,
  and rectangular diagonal traversal. Sources 495/496 are proved adaptations
  of original Total Covered Length / Next Greater Values, not duplicate imports.
  Independent regressions exhaust binary runs through length ten,
  signed five-value arrays through length six, ternary sign arrays through
  length six and every possible target, repeated small attack times/durations,
  all unique-value permutations through length seven, and 400 matrix shapes.
  Maximum-size fixtures include 50,000 signed values (including equal negatives),
  20 zero signs yielding 1,048,576 expressions, 10,000 repeated/overlapping
  attacks, 1,000 stack queries, and 10,000-cell rectangular matrices. Separate
  frequency counts, expression distributions, and event sweeps verify large
  expected outputs. Recursion keeps its review boost. No judge change was needed;
  all 425 preceding definitions retain identical content, versions, and IDs.
  An unsupported draft difficulty value initially quarantined source 485; the
  repaired Easy rubric and all four matching import reports passed before
  publishing the complete batch. The two original-equivalence reports bind source,
  original content, judge, decision, and checker hashes; each has 500 oracle checks,
  source samples, and full-size cases. Re-extraction preserves only current proofs,
  and packaging refuses stale ones. The two unreleased duplicate artifacts were
  withdrawn after confirming no local attempts or drafts used their IDs; their
  offline source fixtures remain reproducible. No owner progress was changed.
  Zuma (488) was left pending, not excluded, for the dedicated search-contract
  review now completed in batch forty-eight.
- Batch forty-six covers LeetCode 483–484, 486–487, and 491–492: exact good-base
  search, lexicographically minimal comparison permutations, optimal recursive
  end-picking, one-flip streaming runs, recursive non-decreasing subsequences,
  and minimum-gap rectangle factors. Independent exhaustive regressions cover
  2,998 small base inputs, all I/D patterns through length six, ternary game and
  subsequence arrays through length seven, binary streams through length ten,
  and all 5,000 small areas. Exact power-root certificates check 500 full-range
  base inputs plus constructed geometric sums through 10^18. Source-scale tests
  include 100,000-entry strings/arrays, 20-turn games, and 32,752 distinct output
  subsequences. Any-order comparison preserves inner sequence order and row
  multiplicities. Recursion exercises keep the existing weak-topic review boost.
  All 419 preceding definitions remain identical; no judge change was needed.
- Batch forty-five adds LeetCode 480 as an ordinary function, not an excluded
  multi-method design exercise. Ordered `float_list` grading requires finite
  numeric values, the correct length, and at most 10^-5 absolute error per element.
  The complete source's tolerance corrects the workbook summary's 10^-4 wording.
  Tests cover exact tolerance boundaries, relative-error traps near 10^9, missing/
  reordered outputs, booleans, strings, non-finite numbers, and helper classes.
  Compressed frequencies plus Fenwick rank selection support 100,000 inputs in
  O(n log n). An independent sort-each-window oracle checks 500 seeded cases and
  all widths on short arrays. Five large fixtures cover odd/even windows, duplicate
  counts, signed 32-bit extremes, k=1, and k=n. All 318 imports and seven overlap
  proofs are revalidated after the judge change. All preceding 418 problem
  definitions retain identical content, versions, and progress IDs.
- Batch forty-four covers LeetCode 469, 476–477, 481–482, and 490: simple-polygon
  convexity, significant-bit complement, aggregate Hamming distance, self-
  describing runs, right-aligned license formatting, and rolling-maze DFS.
  Independent regressions cover simple polygon boundaries in both orientations,
  65,535 positive complements, all input bit positions and duplicate index pairs,
  literal run-length self-description, exhaustive short license strings, and all
  9,216 open endpoint pairs over the 512 three-by-three maze wall patterns.
  Fixtures respect source domains, including simple rather than self-crossing
  polygons and distinct open maze endpoints. Source-scale tests include 10,000
  polygon vertices/array values, 100,000 characters, and 100-by-100 rolling grids.
  The grid exercise preserves the owner's recursion/matrix review priority.
  At batch-44 publication all 412 preceding entries retained identical content,
  versions, and progress IDs; subsequent domain upgrades are documented below.
- Two version-2 domain extensions resolve sources 1009 and 2410 without duplicate
  exercises. Number Complement (476) now includes zero, represented by one digit
  and mapped to one. Assign Cookies (455) now supports 100,000 items on each side,
  covering Players/Trainers while retaining every original input and its fixed
  difficulty. Each equivalence proof checks the source sample and 500 independent
  oracle inputs. Complement covers zero and bit-width boundaries; matching checks
  large capacity-deficit certificates against small assignment-mask enumeration.
  The 100,000-item stress cases run in Chrome. Old version-1 Passed status and
  drafts survive repackaging and reopen under the same IDs. All other 416 problem
  definitions remain unchanged. All seven overlap proofs have refreshed hashes;
  stale target versions, incomplete domains, and incorrect algorithms block proof.
- Batch forty-three covers LeetCode 471 with a `shortest_encoding` comparator:
  bounded grammar decoding plus equality with the verified optimum length,
  not equality with one reference string. Schema validation binds expectations
  to the actual lowercase input (length 1–150); literal text must be retained if
  encoding saves no space. Decoder checks reject malformed groups, nonpositive
  counts, unexpected characters, and excessive expansion before multiplication.
  Independent construction of 3,992 grammar expressions with 850 distinct
  decoded strings verifies native/worker parser behavior;
  exhaustive parse-tree candidates check 500 seeded inputs and all 2,046 binary
  strings of lengths 1–10. Stress cases cover 150-character and nested-repeat inputs. Examples
  and failure evidence label reference output as one valid answer. All 311
  imports and five overlap proofs are revalidated after the shared-judge change;
  all 411 preceding catalog entries preserve content, versions, and progress IDs.
- Batch forty-two covers LeetCode 472–475: recursive concatenated-word detection,
  four-way matchstick partition, 0/1 two-budget knapsack, and binary-searched
  heater coverage. Independent oracles enumerate string cut sets, complete-side
  subset states, item subsets, and all house-heater distances. Regressions also
  exhaust small vocabularies, literal four-bucket assignments, duplicate binary
  strings, and coverage minimality. Stress fixtures respect all source bounds,
  including 10,000 words/100,000 characters, 15 sticks, 600 strings, and 30,000
  houses/heaters. The initial greedy matchstick mutant escaped the test set and
  a slow heater mutant hit the validation limit; both blocked publication until
  repaired. All four now pass both plausible wrong algorithms and 500 oracle
  inputs each. Recursion/search boosts remain, with strings and DP prerequisites
  for the Hard word exercise. All 407 earlier entries retain identical content,
  versions, and progress IDs; the shared judge and five handoff tags are unchanged.
- Batch forty-one covers LeetCode 447–448, 452–456, 459, 461–462, and 467–468:
  ordered Euclidean triples, missing-value marking, closed-interval arrows,
  distinct array-move operations, four-array index counts, cookie matching,
  nonadjacent strict 132 patterns, whole-string periods, bit disagreements,
  distinct cyclic substrings, and full-form IP grammar. Independent exhaustive
  regressions check nine-point grids, duplicate arrays, endpoint coverage sets,
  literal n-1-increment states, Cartesian index choices, bipartite matchings,
  short strings, byte pairs, and decimal/hex group boundaries. Source-scale
  cases include 100,000-element arrays/strings, 200,000-element monotone stacks,
  500-point geometry, and a 1.6-billion tuple count. Move fixtures preserve the
  source's signed-32-bit answer guarantee even at large input boundaries.
  Minimum Bit Flips (2220) is proven equivalent to Hamming Distance with 500
  seeded full-domain inputs and 64 sample/boundary cases, so no duplicate ID is
  published. All five then-existing overlap proofs were refreshed. Players/Trainers
  (2410) was held pending at that point; the version-2 upgrade above now covers
  its 100,000-item bound with independent equivalence evidence.
  All 395 checkpoint entries retain identical content, versions, and progress IDs.
- Batch forty covers LeetCode 450, 457, 464, and 466: noncanonical BST deletion,
  same-direction circular cycles, finite-pool minimax, and repeated-subsequence
  cycle skipping. A dedicated `bst_delete` comparator binds the expected values
  to the actual input tree minus the key, checks strict inorder ordering, and
  permits unbalanced output. Schema gates reject mixed comparators, wrong
  adapters, invalid original trees/keys, and expectations with incorrect survivors.
  Native and browser serialization reject noninteger nodes, cycles/shared children,
  and Python arrays masquerading as returned trees. Examples and failed-test
  feedback label expected shapes as one valid answer. All 294 imports and four
  overlap proofs were revalidated for the shared judge change before packaging.
  Exhaustive checks cover all 626 tree shapes through seven nodes and deletion
  of every present or nearby absent key, short signed circular arrays, small game
  pools, and repeated binary strings. Larger checks cover 10,000-node chains,
  5,000-position failed routes with a linear-access bound, the full 20-number
  game domain at selected targets, and million-block strings. Game oracles use
  bottom-up retrograde tables plus literal small game trees; repetition oracles
  use expanded subsequence feasibility plus 500 full-domain binary-lifting checks.
  The level-7 game initially failed the import builder's incomplete rubric mapping
  and was quarantined until that mapping was extended; it was not published in
  a failing state. Existing problem IDs/content, progress, and handoff tags remain
  unchanged. Binary-search and recursion review priorities remain active.
- Batch thirty-nine covers LeetCode 422, 425, 433, 436–440, and 443/445/446:
  ragged word-square validity, recursive square generation, shortest gene-bank
  paths, lower-bound intervals, same-chain tree sums, anagram windows, nested
  ternaries, decimal prefix ranking, in-place character compression, forward
  linked digits, and arithmetic subsequences. Oracles independently transpose
  rows, enumerate row products, use all-pairs graph distances, scan interval
  starts, enumerate ancestor paths and windows, parse recursive grammar, sort
  integers by text, group character runs, add exact small integers, and enumerate
  index subsets. Every problem has 500 seeded comparisons and two logically
  rejected wrong algorithms, without relying on their crashing.
  Additional checks exhaust short ragged rows, binary word dictionaries and gene
  banks, small interval/window/ternary domains, all two-digit linked additions,
  and short arithmetic subsequences. An independent digit-DP inverse-rank check
  verifies 500 queries through n=10^9. Source-scale fixtures include 500-by-500
  ragged/full squares, 1,024 generated squares, 20,000 intervals, 1,000-node
  chains, 30,000-character windows, 2,499 nested conditionals, and 100-digit lists.
  Every single-run compression length through 2,000 is checked. The workbook's
  count-only compression sample has an explicit source-bound adapter preserving
  its required mutated prefix; returning a string/copy or only a count fails.
  Arithmetic tests preserve the signed-32-bit answer guarantee, rather than
  generating an invalid thousand-equal-value case. Existing IDs/content,
  weak-topic priorities, judge contracts, progress, and handoff tags are unchanged.
- Batch thirty-eight covers LeetCode 415–421 and 423–424: digitwise addition,
  one-use subset-sum DP, reverse ocean traversal, cyclic row transitions,
  straight-ship starts, minimum password edits, XOR prefixes, digit inventories,
  and replacement-budget windows. Oracles use small exact integers, subset masks,
  independent downhill floods from every cell, literal word placement, connected
  components, edit distance to a valid-password automaton, all XOR pairs,
  digit-count vector search, and every substring.
  Password search enumerates keep/delete/insert/replace transitions; three new
  character representatives per class suffice to avoid both neighboring output
  characters without excluding a valid edit. Original characters remain available
  as free keep transitions. An independent literal edit BFS checks every six-
  character word over a three-character alphabet, and longer mixed/punctuation
  inputs test deletion/replacement interactions through length 50.
  Regressions exhaust 19,683 ternary 3-by-3 ocean maps, all valid small ship boards,
  positive subset multisets, word widths, XOR multisets, digit inventories, and
  short uppercase windows at every budget. Source-scale cases include 200-by-200
  grids, 200,000 XOR values, 10,000-digit inputs, and 100,000-character strings.
  Ocean results preserve row/column order inside each pair; grid/recursion review
  priority remains active. The judge and all 371 previous problem payloads/IDs
  are unchanged, and the 363-problem transfer tag remains frozen.
- Batch thirty-seven covers LeetCode 18, 30, 47, 87, 407, 410, and 413–414:
  unique value quadruplets, word-multiset windows, numeric permutations,
  recursive scrambling, boundary-heap water retention, capacity binary search,
  contiguous arithmetic slices, and third distinct maxima. Four are Hard.
  Independent oracles enumerate four-index choices, fixed-width token bags,
  position permutations, complete split-tree languages, exterior floods at each
  integer water layer, every contiguous cut set, slices, and sorted distinct values.
  Regressions exhaust short multisets, binary word windows, scramble strings,
  all 19,683 ternary 3-by-3 maps, nonnegative partition arrays, and signed ranks.
  Source-scale cases include 40,320 distinct permutations, 200-by-200 basins,
  5,000 words, 1,000 partition items, and 5,000-value arithmetic runs.
  Outer-order permutation comparison keeps every row's internal order and all
  multiplicities. The simpler numeric permutation contract 46 maps to 47 after
  500 independent unique-input checks and six-element/720-output boundaries;
  the text-returning original exercise remains distinct. All 363 checkpoint
  problems retain identical content/versions/IDs. No shared judge change was needed.
- Small finite domains are still pending, not excluded or padded with invalid
  inputs: Generate Parentheses has only eight allowed integer inputs and each
  N-Queens contract only nine. Two visible plus twelve distinct hidden cases is
  impossible within those domains. Owner confirmation of an exhaustive-domain
  exception is requested; until then the existing approval gate is unchanged.
- Batch thirty-six covers LeetCode 386, 388, 390, 393–395, 397, 402–403, and 408:
  constant-extra-space decimal preorder, text-only filesystem paths, alternating
  survivor tracking, byte-prefix validation, nested decoding, recursive frequency
  splitting, binary integer reduction, monotone digit removal, frog state DP,
  and abbreviation validity. Independent oracles sort decimal text, reconstruct
  complete paths, literally delete alternating items, match bit grammars, expand
  innermost groups, enumerate substrings/subsequences/jump paths, search integer
  states breadth-first, and match tokenized abbreviation patterns.
  Exhaustive checks cover every one-/two-byte array, short ternary strings, stone
  subsets, digit subsequences, and abbreviation replacement masks. Larger checks
  cover 50,000 lexical integers, 10,000-character paths/windows, 20,000 bytes,
  100,000 decoded characters/digits, n=10^9 elimination, signed-32-bit integer
  boundaries, and 2,000-stone DP without deep Python recursion.
  UTF-8 wording preserves the source's structural byte rules (including shapes
  rejected by a strict Unicode decoder); filesystem wording restores the actual
  newline/tab semantics lost in its workbook summary. Abbreviation validation
  takes an extra abbreviation and returns a bool, unlike source 320's enumeration.
  No shared judge change was needed, and all 353 previous problems keep identical
  content, versions, and progress IDs. Handoff tags and the seed remain unchanged.
- Batch thirty-five covers LeetCode 99, Recover Binary Search Tree. It adds
  `preserve_tree_structure` for value-only mutation of a selected TreeNode
  argument. Schema restrictions reject incompatible return/prefix/list modes;
  native and browser checks preserve original nodes and every left/right link,
  reject noninteger values, and permit temporary threads only if restored.
  The Morris reference uses constant auxiliary space and supports 1,000-node
  left/right chains. A path-order/sorted-value oracle is independently audited
  with conventional inorder traversal. Regressions cover every swapped pair
  on all tree shapes through seven nodes and ensure all fixtures have exactly
  two misplaced values. Both wrong algorithms fail: first-inversion-only repair
  and local parent-child repair. Existing problem IDs, content, progress, and
  handoff tags remain unchanged; every import is revalidated for this judge change.
  An additional adversarial fixture exposed a falsey replacement child whose
  null value disappeared from compact tree output. Identity snapshots now use
  explicit None checks, not truthiness; inserted children cannot masquerade as
  missing links. This also strengthens returned-input-node immutability. Tests
  accept genuine falsey nodes when their original links are preserved.
- Batch thirty-four covers LeetCode 148–149, 156, 164, 186, 189, and 203:
  bottom-up linked-list merge sort, exact normalized line directions, recursive
  upside-down trees, linear-time maximum gaps, character-array word reversal,
  in-place array rotation, and linked-list filtering. Oracles independently sort
  values, count cross-product collinearity, remap binary paths, index rotations,
  and filter values. Exhaustive tests cover short lists/arrays, every subset of
  a 3-by-3 coordinate grid, every allowed tree shape through ten nodes, and short
  word/rotation/deletion cases. Stress tests include 50,000-node lists, 300 points,
  ten-node recursive chains, and 100,000-character/value arrays. The source
  mutation contracts distinguish 186 from string-returning 151 and 189 from the
  original return-a-list rotation; returned copies are rejected. Original tree
  identity/order remains enforced with equal values. No shared judge extension
  was needed, all 345 previous problems retain identical content/versions/IDs,
  and the handoff tags and progress seed remain unchanged.
- Batch thirty-three covers LeetCode 363, 366–367, 371–372, and 375–378:
  bounded rectangular sums, simultaneous leaf-removal groups, exact square
  predicates, signed carry propagation, decimal modular powers, minimax guessing,
  wiggle subsequences, ordered sequence sums, and matrix order statistics.
  A new `unordered_rows` comparator preserves chronological group order while
  permitting integer permutations inside each group. Schema and worker tests
  reject mixed modes, malformed rows, bool/float values, reordered rounds, and
  lost or extra duplicate occurrences. All 244 imports were revalidated under
  this judge contract, and overlap proofs were refreshed before packaging.
  Exhaustive checks cover 2-by-3 ternary rectangles in both orientations, binary
  tree shapes through five nodes, square boundaries through 46340^2, signed
  pairs, small decision trees, wiggle subsequences, ordered sums, and matrix ranks.
  Stress inputs include 100-by-100 rectangles, a 100-node chain, 2000-digit
  exponents, n=200 minimax, and 300-by-300 sorted matrices. An exponential
  deliberately incorrect Combination Sum IV validator fixture timed out and
  was quarantined; replacing it with an efficient incorrect 0/1 DP allowed
  complete algorithmic rejection checks. No failing candidate was published.
- Batch thirty-two covers LeetCode 349–351, 354, 356, 360–361, 365, and 369–370:
  distinct versus repeated intersections, recursive unlock patterns, strict
  envelope nesting, vertical set reflection, quadratic endpoint merging,
  wall-delimited bomb segments, jug reachability, linked-list carry, and range
  addition. Every unlock-length pair is deterministic-tested against exhaustive
  geometric permutation counts; all 19,683 three-by-three bomb grids are checked
  against direct ray casting. Exhaustive short arrays, envelopes, coordinates,
  quadratics, jug states, numbers, and interval updates add independent evidence.
  Stress fixtures include 100,000 envelopes, 10,000 points, 500-by-500 grids,
  100-digit lists, and 10,000 full-length updates on a 100,000-position array.
  No judge change was needed, and all 326 checkpoint entries retain identical
  content, versions, and IDs. The checkpoint tag still points to `c79079d`.
- Batch thirty-one covers LeetCode 324, 340, and 342–345: strict wiggle mutation,
  variable-budget distinct-character windows, powers of four, integer-product
  splitting, in-place character reversal, and vowel-only reversal. The schema
  and both judges distinguish strict from non-strict wiggles, preserve integer
  multiplicities, and reject invalid expectations, mixed modes, equal neighbors,
  booleans/floats, and returned copies. Independent exhaustive short-domain
  checks support the references. Source-scale cases include 50,000-value arrays,
  50,000-character windows, 100,000-character lists, and 300,000-character strings.
  All previous 320 packaged entries retain identical content, versions, and IDs.
- Batch thirty covers LeetCode 321, 332, 335, and 336: maximal digit merging,
  lexicographically smallest Euler itineraries, constant-space self-crossing
  detection, and palindrome pairs using KMP boundary flags and a reversed trie.
  All four are ordinary Hard problems. Independent exhaustive checks cover
  short digit arrays at every output length, all short valid three-airport walks,
  short four-direction segment sequences, and every pair of short binary words.
  Source-scale tests include 500-digit arrays with long equal suffixes, 300
  tickets with duplicates, 100000 segments, 5000 unique 300-character words,
  and a separate 5000-pair output case. Repeated tickets, empty strings, ordered
  pair direction, and nonadjacent endpoint touches retain their exact semantics.
- Batch twenty-nine covers LeetCode 318, 320, 326–327, 329–331, 333, and 337:
  letter-mask products, recursive abbreviations, powers of three, inclusive
  range-sum counting, increasing matrix paths, minimal array patches, preorder
  serialization, largest BST subtrees, and tree house selection. Exhaustive
  tests cover short strings/arrays/grids, all binary tree shapes through five
  nodes with ternary values, and subset-sum search for optimal patch counts.
  Stress fixtures include 1000 words of 1000 letters, all 32768 abbreviations
  at length 15, 100000-element range sums, a 200-by-200 snake of length 40000,
  and 10000-node trees. Source 319 maps to 69 using the perfect-square/divisor
  proof, 500 literal simulations, 500 full-domain square enumerations, and
  square-adjacent boundaries through 10^9. The original progress ID is retained.
- Batch twenty-eight covers LeetCode 312–317: interval balloon DP, generalized
  prime-product streams, binary-tree vertical traversal, strictly smaller suffix
  frequencies, minimal distinct-letter subsequences, and shortest travel sums
  to buildings through empty grid cells. Exhaustive tests check small balloon
  arrays, signed suffix arrays, three-letter strings, and all two-by-three grids
  with a building. A separate factorization scan proves the 100,000th number
  using the first 100 primes is 284445. Stress inputs cover 300 balloons,
  100-node trees, 100,000-element arrays, 10,000 letters, and 50-by-50 grids.
  Workbook 1081 is a proved overlap of 316, with 500 independent subsequence
  comparisons, its original sample, and the 1,000-character boundary. Stale
  overlap evidence or a quarantined target blocks publication.
- Batch twenty-seven covers LeetCode 296, 298–299, 301–302, 305–306, and 309–311:
  geometric medians, recursive consecutive tree paths, Bulls and Cows,
  minimum-removal parenthesis backtracking, binary-search image bounds, online
  island union-find, additive-number parsing, cooldown stock DP, leaf-trimmed
  tree centers, and sparse matrix multiplication. Regressions exhaust small
  meeting grids, short parenthesis strings, connected three-by-three black-pixel
  shapes, short island-update sequences, stock sequences, and all labeled trees
  through six nodes. Stress fixtures include 10,000-node trees and island-update
  streams, a 20,000-node path, and 100-by-100 sparse matrices. The exclusion
  classifier now recognizes persistent constructor-plus-query classes while
  preserving ordinary `TreeNode` and `ListNode` callable problems.
- Batch twenty-six covers LeetCode 280, 282–283, 285–287, 289, and 291–294:
  flexible in-place wiggle ordering, expression backtracking, stable zero
  movement, selected-node BST successor, multi-source room distances, duplicate
  cycle detection, simultaneous Game of Life updates, bijective substring
  patterns, Nim, and both Flip Game contracts. The shared judge now accepts any
  valid wiggle permutation, supports `None` for a valid absent selected-node
  result, and snapshots declared read-only inputs. Regressions exhaust all short
  ternary wiggle arrays, all 512 three-by-three life boards, and short recursive
  flip states. Stress inputs include 10,000-element arrays and trees, a 250×250
  grid, and a 100,001-element duplicate cycle.
- Batch twenty-five covers LeetCode 237, 266–267, 270, 272–276, and 279:
  selected-node list deletion, palindrome feasibility/generation, one/k closest
  BST values, integer-to-English conversion, unsorted/sorted H-Index, fence
  painting, and minimum perfect squares. Source 237 retains its one-parameter
  callable. A structured test payload builds the full list and selects the actual
  non-tail node; the judge observes the original head and requires the selected
  node to remain while its original successor is unlinked. The workbook's head
  and node context is preserved explicitly in its validation report. Regressions
  exhaust small palindrome strings, citation arrays, fence paintings, and square
  totals. Stress fixtures include 100,000 list nodes, 10,000-node BST chains,
  100,000 sorted citations, the complete 32-bit number-word range, and n=10,000
  square DP. Recursive and binary-search review priorities remain active.
- Batch twenty-four covers LeetCode 235–236, 255, 257, 259–261, and 263–265:
  lowest common ancestors in BSTs and arbitrary binary trees, BST preorder
  validation, root-to-leaf path formatting, smaller 3Sum counting, two signed
  singletons, undirected-tree validation, ugly-number recognition/generation,
  and many-color house painting. LCA arguments are actual nodes selected from
  the input tree; answers must reuse an existing node and leave the tree unchanged.
  Regressions exhaust short BST preorders, simple graphs through five nodes,
  short signed arrays, ugly-number prefixes, and small painting assignments.
  Stress fixtures include 100,000-node tree chains, 30,000-element arrays,
  10,000 preorder values, 2,000 graph nodes, the 1,690th ugly number, and a
  100-by-20 painting grid. Recursive-tree and binary-search review weighting
  remains active.
- Batch twenty-three covers LeetCode 243, 245–249, 252, 254, 256, and 258:
  distinct and same-word distances, strobogrammatic recognition/generation/range
  counting, cyclic string groups, nonoverlapping meetings, multiplicative
  partitions, three-color house painting, and digital roots. Regressions exhaust
  short word layouts and digit strings, every generation length through 14,
  direct range counts, cyclic shift groups, small interval subsets, factors
  through 200, and small color assignments. Large fixtures cover 100,000 words,
  62,500 length-14 outputs, all strobogrammatic values through 15 digits, 10,000
  meetings, and 100 houses. Recursive review weighting remains active.
- Batch twenty-two covers LeetCode 219, 220, 224, 227, 228, 229, 233, 238, 240,
  and 241: bounded duplicate pairs, two expression evaluators, consecutive range
  formatting, over-one-third voting, positional digit counting, prefix/suffix
  products, monotone-matrix search, and recursive expression grouping. Regression
  checks exhaust small arrays, arithmetic forms, value buckets, sorted subsets,
  majority patterns, products with zeroes, monotone matrices, and four-number
  grouping trees. Source-scale fixtures include 100,000-item arrays, 100,000-deep
  parentheses, 300,000-character expressions, 300×300 matrices, n=10^9, and all
  4,862 grouping trees of a ten-number product. Recursive and binary-search review
  priorities and reachable Hard prerequisites remain covered.
- Batch twenty-one covers LeetCode 212, 218, 221, 223: multiword grid recursion,
  skyline sweep, maximal square, and two-rectangle union. Independent oracles
  enumerate per-word used-cell states, endpoint heights, square cells, and planar
  coordinate cells. Additional regressions exhaust every two-by-two binary-letter
  board's simple paths, 1,140 three-building multisets, all 512 three-by-three
  binary matrices, and 1,296 small rectangle pairs including degenerate cases.
  Stress cases include 30,000 unique dictionary words, 10,000 nested/overlapping
  buildings, and 300×300 binary grids. Word Search II was initially quarantined
  because its cell-reuse mutant survived the deterministic fixtures. A reachable-
  frequency but disconnected-letter witness now rejects that bug by wrong output;
  it passed all gates before publication. Recursive-grid priorities and reachable
  Hard prerequisites are regression-tested.
- Batch twenty covers LeetCode 190, 201, 202, 204, 205, 209, 213, 214, 216:
  fixed-width reversal, range AND, digit-square cycles, primes, isomorphism,
  minimum positive-sum windows, circular nonadjacent selection, shortest
  front-added palindromes, and exactly-k digit combinations. Oracles use binary
  strings, direct interval AND, visited states, trial division, first-occurrence
  positions, subarray enumeration, subset masks, palindromic-prefix scans, and
  all digit subsets. Additional tests exhaust small bit ranges, ASCII equality
  patterns, positive windows, circular subsets, and direct palindrome prepends.
  An independent Euler sieve checks the 5,000,000 prime boundary (348,513 primes);
  all 480 valid digit-combination inputs are tested. Source 190 explicitly limits
  input to even n in [0,2^31-2]. Stress tests include 100,000-element windows and
  50,000-character palindromes. The Hard prerequisite uses the existing
  string-matching topic, so it is reachable before solving the new challenge.
- Batch nineteen covers LeetCode 108, 109, 222, 250: sorted array/list to balanced
  BST, complete-tree node count, and uniform-value subtree count. Independent
  oracles use complete heap-indexed shapes filled in inorder, input-node counts,
  and explicit descendant-path scans. References use midpoint recursion,
  linear-time linked cursor construction, perfect-subtree height comparisons,
  and iterative postorder state, respectively. Stress fixtures include 10,000
  distinct array values, 20,000 list nodes (including duplicates), 50,000 complete
  tree nodes, and 1,000-node uniform/nonuniform chains.
- `balanced_bst` is an explicit property comparator, not canonical-shape equality.
  Its bounded iterative parser verifies every subtree's balance and full inorder
  value preservation. Schema validation requires sorted integer input, a returned
  TreeNode interface, a valid expected tree, and consistent comparison modes.
  The checker is verified against all 626 shapes through seven nodes, plus wrong
  inorder, duplicate loss, interior imbalance, malformed encodings, noninteger
  nodes, and deep chains. UI examples say “One valid output”; failure evidence
  shows both the actual tree and the contract error. Existing comparators retain
  their behavior. All 126 imports and overlap proofs were revalidated under the
  new judge hash. Complete-tree references additionally obey a logarithmic-squared
  link-read bound over sizes 0–1024 and large boundaries, without claiming formal
  complexity grading for arbitrary learner submissions.
- Tree Height version 3 restores the exercise's intended recursive solution and
  caps path depth at 500, while still allowing broad trees with 20,000 total nodes.
  A separate breadth-first oracle and 500 seeded binary-path shapes verify depth
  independently; deterministic cases include 300-/500-node skewed paths and a
  wide 20,000-node tree. Plausible edge-counting and left-only mistakes
  fail by wrong output. Regression checks retain version-1 accepted source, drafts,
  Passed filtering, and recommendation exclusion through repackaging and reopen.
  Other original overlap contracts still require continued boundary auditing.
- Batch eighteen covers LeetCode 168, 171, 172, 179, 187, 188: both Excel-column
  directions, factorial zeroes, maximum concatenation ordering, overlapping DNA
  repeats, and variable-budget stock trading. Oracles use length-block unranking,
  explicit positional weights, exact factorials, permutations, sorted window
  groups, and enumeration of legal buy/sell days. Additional regressions exhaust
  all 10,001 factorial inputs, all 702 one-/two-letter labels, 216 small ordering
  triples, 2,048 two-letter-alphabet DNA strings of length 11, and 1,092 short
  price sequences under three budgets. Maximum-size cases include 100,000 DNA
  characters, 1,000 stock days, and a 1,000-digit string output.
- Batch seventeen covers LeetCode 151, 152, 154, 159, 161, 163, 165, 174:
  word reversal, subarray products, duplicate-aware rotated minimum, two-character
  windows, one edit, missing ranges, version comparison, and Dungeon Game.
  Oracles use regex tokenization, subarray enumeration, direct minimum scans,
  substring sets, full edit-distance DP, explicit interval complements, split
  revision comparison, and exhaustive dungeon routes. Regression checks also
  enumerate small rotated multisets and edit operations, and compare all 729
  two-by-three dungeons against forward initial-health feasibility search.
  The unique-only rotated-minimum workbook row 153 maps to the approved 154
  contract, which accepts unique arrays and retains logarithmic reads on them.
  A separate report checks 500 seeded inputs plus the workbook sample and two
  5,000-element boundaries; the maximum observed element-read count is 53.
  The canonical published rating remains that of the broader Hard problem.
- Imported-target overlaps now require matching source, target-content,
  target-source, judge-contract, decision, and proof hashes. Packaging refuses
  stale evidence or unpublished targets. Re-extraction preserves an unchanged
  proved mapping but returns it to pending when dependencies change. The
  explicit offline reconciliation command quarantines failing proofs and refuses
  to replace an existing imported problem/progress ID. No duplicate is published.
- Batch sixteen covers LeetCode 114 and 143: in-place tree flattening and list
  reordering. Identity tracking now supports both trees and lists, including the
  selected mutated argument. Optional `expected_node_order` indexes original
  nodes in list/preorder traversal order; it detects incorrect ordering among
  equal-valued nodes without changing older contracts that permit such ties.
  Unique nonnegative integer indices, selected-argument scope, copied nodes,
  value rewrites, cycles, empty trees, and deep/long inputs have regression tests.
  All 108 imported references were revalidated under the changed judge contract.
- Batch fifteen covers LeetCode 36, 65, 68, 85: partial Sudoku validation, number
  syntax, exact text justification, and maximal matrix rectangles. Independent
  pairwise unit checks, a regular-expression grammar, exhaustive line-break
  patterns with round-robin spaces, and rectangle enumeration supply oracles.
  Regressions independently decompose 4,680 numeric strings, check every 3×3
  binary matrix, verify exact formatting, and include valid-but-unsolvable Sudoku.
- Text Justification's workbook output has collapsed spaces and violates width
  16. An explicit reviewed correction preserves the original input/output and
  source URL in the report. The builder rejects absent, stale, empty-rationale,
  or oracle-inconsistent corrections; no general sample bypass is enabled.
- Batch fourteen covers LeetCode 105, 106, 130: construction from preorder/inorder
  or inorder/postorder, and in-place Surrounded Regions. Cartesian-tree rank
  minima and disjoint-set connectivity provide independent oracles. Tree
  reconstruction also round-trips 500 original generated shapes. Grid connectivity
  is checked against per-cell reachability for all 512 three-by-three boards.
  Deep 3,000-node left/right chains and 200×200 grids avoid recursion overflow
  through explicit-stack references while the pedagogy explains recursion.
- Batch thirteen covers LeetCode 128, 132, 137, 150: consecutive-value runs,
  minimum palindrome cuts, a signed singleton among triples, and postfix
  evaluation. Independent sorted scans, exhaustive cut masks, occurrence counts,
  and recursive expression parsing with exact rational truncation serve as oracles.
  Domain regressions cover signed endpoints, valid expression stacks and all
  intermediate results, odd/even palindromes, duplicate values, and source limits.
- The twelfth batch covers LeetCode 82, 86, 139, 140: delete-all-duplicate linked
  nodes, stable linked partitioning, segmentation existence, and all word-break
  sentences. Count-based filtering, stable Boolean-key sorting, and exhaustive
  cut-mask enumeration provide independent oracles. Regression tests verify
  reference node order even among equal values, complete sentence enumeration,
  dictionary reuse, duplicate rejection, source domains, and weak-topic priorities.
- The eleventh batch covers LeetCode 26, 27, 31, 48, 73, 75, 80, 88 using genuine
  in-place signatures. `result_mode` defaults to the existing return-value
  behavior. `mutated_argument` selects a post-call argument; `returned_prefix`
  checks a strict integer count and prefix, with the tail ignored. Prefix
  comparison permits reordering only for Remove Element and retains multiplicity.
  Returned copies and count-only answers are rejected when the input is wrong.
  All then-existing 91 references were revalidated after extending the shared judge contract.
- Prefix workbook examples are parsed as literals with one count and one named
  updated list. Underscores are legal only beyond the checked prefix. Calls and
  expressions are never evaluated; malformed outputs block import. Mutation
  schema indexes, strict counts, argument position selection, tree serialization,
  original-input evidence, and returned-copy rejection have regression coverage.
- The tenth batch covers LeetCode 71, 81, 97, 115, 122, 123, 134, 135:
  lexical path simplification, duplicate-aware rotated search, string DP,
  unlimited/two-transaction stocks, a unique circular gas route, and Candy.
  Source-domain checks include the gas route's unique-start guarantee. A faulty
  large gas fixture was quarantined and corrected before publication; the new
  zero-total fixture independently checks its unique minimum prefix balance.
  Candy's relaxation oracle additionally matches exhaustive assignments for
  all 120 rating arrays over {0,1,2} with lengths 1–4.
- The ninth batch covers LeetCode 94, 103, 107, 113, 120, 124, 144, 145:
  three depth-first traversal orders, zigzag/bottom-up levels, root-to-leaf
  paths, triangular DP, and maximum tree path sum. Path outputs preserve
  multiplicity and within-path order. Deep-tree fixtures exercise 5,000 and
  30,000 nodes without increasing Python's recursion limit. Source-domain
  checks cover every deterministic input and 500 generated inputs per problem.
- The eighth batch covers LeetCode 16, 28, 38, 43: nearest three-element sum,
  KMP prefix matching, recursive run-length encoding, and column multiplication.
  Tests enforce source-domain validity, including unique closest sums. The
  imported wording corrects “distinct integers” to “distinct indices.”
- The seventh batch covers LeetCode 6, 8, 12, 13, 29, 57, 59, 60, 61: zigzag
  conversion, integer parsing, Roman conversions, division, interval insertion,
  spiral generation, permutation ranking, and node-preserving list rotation.
- Existing `matrix-spiral-order` is now version 2 with rectangular instructions
  and examples; it remains the same progress ID and accounts for workbook 54.
  Its independent 500-input regression verifies rectangles, rejects two wrong
  traversals, and preserves version-1 attempts and the owner's saved draft.
- The sixth batch covers LeetCode 10, 32, 41, 44, 45, 55. Four are ordinary
  Hard exercises, retained with prerequisites. Regex and wildcard stars have
  different tested semantics. A 100,000-element in-place placement case and
  2,000-character wildcard cases pass in the browser (wildcard suite: 1.51 s).
- The fifth batch covers LeetCode 17, 39, 62, 63, 64, 74, 77, 78, 90, 91, 93.
  It adds recursive obstacle grids, grid optimization, matrix binary search,
  backtracking sets/combinations, decoding, and IP reconstruction. Any-order
  comparisons preserve multiplicity and reject missing/duplicate answers.
- The fourth batch covers LeetCode 19, 24, 92, 129, 230, 404, 543, 563, 700.
  It includes recursion and preserves ordinary TreeNode/ListNode interfaces.
  The tests cover node identity, sparse tree outputs, and 10,000-node chains.
- Import validation is isolated per problem with a timeout. The workbook's
  sample must agree with the oracle and remain visible. Failing content is
  quarantined; publication checks content, source, and judge-contract hashes.
- Offline packaging publishes only validated imports; the server reads a small
  metadata index and loads full problem payloads on demand with a 32-item cache.
- Library search/filtering/pagination is on the server; the UI fetches 30 at a time.
- Completion/scoring no longer lose history after 500 attempts. Catalog rebuilds
  are tested to leave the live progress database unchanged.
- Monaco assets now ship locally along with Pyodide. Browser checks block
  external requests and verify editor loading, reference execution, timeout
  recovery, and progress persistence across a real backend restart.
- The shared judge now has validated contracts for flexible and strict wiggle outputs,
  declared read-only parameters, and optional existing-node results. It also has
  a validated contract for selecting real TreeNode
  arguments from an input tree and requiring the returned node to retain its
  identity. Both batch-twenty-four LCA exercises use the contract, and copied
  nodes or tree mutations are rejected. It also supports an embedded full-list
  context that supplies one real non-tail ListNode and checks the complete list
  afterward. Ordered integer groups now also accept within-group permutations
  while preserving outer order and duplicate counts. BST deletion now additionally
  permits any valid strict BST with exactly the input values minus the requested
  key, without a balancing requirement. Shortest string encodings permit tied
  optimal grammar expressions with bounded decoding. Ordered decimal lists now
  enforce finite numeric values and absolute 10^-5 tolerance. All 358 published imports
  have matching passing reports in the 459-problem package under this judge contract.
- The interim benchmark now records kernel high-water RSS for both backend
  runs, not occasional memory samples. It excludes browser/driver memory.
- Current 453-problem Chrome/M3 Pro run: library/search p95 1.28/1.23 ms,
  detail p95 1.13 ms for Word Search, 1.10 ms for the 100,000-node selected-
  list problem, and 1.97 ms for the enlarged matching problem; dashboard p95
  is 1.38 ms (100 requests per route, six routes). Startup is
  234 ms and backend peak RSS is 296.19 MiB across browsing large array and
  linked-list details and restarting. All 352 imported references and
  upgraded Spiral Matrix/Tree Height and all four original overlap targets pass in
  Pyodide with external HTTP blocked (358 reference suites total).
  The Recover Binary Search Tree suite finishes in 40.9 ms after runtime load,
  including both 1,000-node chains and all sixteen deterministic cases. Existing
  large in-place, string, stock, circuit, candy, and tree fixtures still pass.
  Browser checks also verify grading explanations,
  returned-copy/count-only rejection, strict prefix counts, and reordered survivors.
  Equal-valued nodes in the wrong order and replacement TreeNodes are rejected
  despite matching displayed values; correct in-place rewiring is accepted.
  Balanced-BST checks accept a different valid shape and reject wrong inorder,
  missing duplicates, internal imbalance, and invalid node values in Chrome.
  Selected ListNode checks accept the constant-space splice and reject both a
  wrong deleted value and replacement nodes whose displayed values look correct.
  Ordered-group checks accept different within-round leaf orderings and reject
  reversed rounds, changed multiplicities, omitted groups, and noninteger values.
  Each new batch-thirty-four wrong algorithm is also rejected in the browser,
  and an unchanged all-equal upside-down tree fails the original-node-order check.
  BST recovery also rejects both wrong algorithms, replacement/swapped nodes,
  noninteger values, and falsey inserted children. Genuine falsey original nodes
  with preserved links and restored Morris threads pass; leftover cycles fail.
  Both incorrect algorithms for all ten batch-thirty-six problems are rejected
  in Chrome; the UTF-8 structural-rule clarification renders in the problem UI.
  All sixteen batch-thirty-seven wrong algorithms are also rejected. Numeric
  permutations accept reversed outer order but reject duplicate/missing rows
  and collapsing all rows to the same internal order. Its 40,320-output boundary
  passes within a 238.1 ms suite; both 200-by-200 basin cases pass within a
  200.2 ms suite after Pyodide load. The row-order explanation renders in the UI.
  All eighteen batch-thirty-eight wrong algorithms are rejected. Ocean coordinates
  accept reordered cells but reject row/column swaps, omissions, and duplicates;
  the plateau and coordinate rules render in the UI. Source-scale XOR, subset DP,
  and ocean suites finish in 508.7, 328.9, and 230.5 ms respectively after load.
  All twenty-two batch-thirty-nine wrong algorithms are rejected. Character
  prefixes enforce actual input mutation and strict integer counts while ignoring
  the tail; word-square answers permit outer reordering but reject changed row
  order and duplicated/missing squares. Multi-digit compression examples render
  the compound count/prefix output correctly. Batch-39 suites finish in 35.6–130.5 ms
  after load, including the thousand-item arithmetic-subsequence DP and deep
  tree/conditional inputs.
  All eight batch-forty wrong algorithms are rejected. BST deletion accepts
  predecessor/successor roots and unbalanced shapes while rejecting invalid
  ordering, missing/extra/noninteger values, cycles, shared children, and array
  returns. Its 10,000-node cases pass within a 103.1 ms suite; the circular-loop
  suite takes 46.7 ms and million-block repetition suite 34.1 ms. The 21-case
  minimax suite, including the heavier (20,150) hidden case, finishes in 1,748.0 ms
  after runtime load, within the three-second execution deadline.
  All 24 batch-forty-one wrong algorithms are rejected. Missing-value lists allow
  reordered answers but reject duplicate or omitted values. The IP problem's
  full-notation restriction renders in the UI and is enforced by the worker.
  Batch-41 reference suites finish in 33.8–237.5 ms after load, including all
  100,000-/200,000-element and 500-point stress fixtures.
  All eight batch-forty-two wrong algorithms are rejected; concatenated-word
  outputs permit reordering but reject omitted, repeated, or unsplittable words.
  The multi-piece explanation renders in the UI. The word, matchstick, binary
  budget, and heater suites finish in 72.0, 36.2, 359.9, and 114.8 ms respectively
  after load, including every source-scale stress fixture.
  Batch 43 accepts tied encodings (`10[a]`, `a9[a]`, `9[a]a`, `5[aa]`) but rejects
  both wrong reference mutants, wrong decoded text, nonminimal expressions,
  malformed grammar, oversized expansion, and bracketed ties that save no space.
  Failure details retain the actual output and explain the contract. Fresh-worker
  recovery passes afterward. All 20 reference cases, including four large/nested
  fixtures, finish in 316.6 ms after runtime load.
  All twelve batch-44 wrong algorithms are rejected, including ordinary-cell
  traversal that incorrectly accepts a rolling destination. The STOP-versus-pass
  distinction renders beside the visible maze examples. Polygon, complement,
  aggregate bit distance, magical string, license formatting, and rolling-maze
  suites finish in 55.0, 33.5, 90.5, 48.3, 51.9, and 46.0 ms after runtime load,
  respectively, including all source-scale fixtures.
  The version-2 matching suite includes the 100,000-item fixtures and finishes
  in 230.0 ms. The worker rejects an artificial 30,000-result cap and the old
  positive-only complement on zero. Both domain extensions render in the UI.
  Backend memory includes the larger lazy-loaded matching and median payloads; the
  normal problem response still omits hidden tests and reference solutions.
  Batch 45's 21-case median suite, including five source-scale fixtures, finishes
  in 1,253.5 ms after runtime load. Both wrong algorithms fail. Ordered decimal
  checks accept close absolute approximations and integer equivalents, reject
  large-value relative-error traps, missing/reordered values and wrong types,
  refuse non-finite outputs, and recover on the next worker. A helper-class
  implementation passes behind the ordinary function entry point. The tolerance
  explanation and non-integer median example render in the problem UI.
  All twelve batch-46 wrong algorithms are rejected. Subsequence rows may reorder
  but may not reverse internally, duplicate, or disappear; the equality and
  lexicographic-minimality explanations render beside the examples. Base,
  permutation, recursive game, one-flip stream, subsequence, and rectangle suites
  finish in 34.5, 250.0, 34.4, 167.0, 148.0, and 34.7 ms after runtime load,
  respectively, including all maximum-size cases.
  All eight batch-47 wrong algorithms are rejected. Run, reverse-pair, sign-count,
  and diagonal suites finish in 158.9, 598.5, 34.4, and 67.7 ms after runtime load,
  respectively. Original interval-union and next-greater adapters pass source
  samples and 10,000-attack / 1,000-query fixtures. The two duplicate IDs are
  absent from the manifest and return 404 from the problem API. Zero-sign,
  equal-negative-pair, and rectangular-diagonal explanations render in the UI.
  Zuma's 24-case suite, including six full-size fixtures, finishes in 419.9 ms
  after runtime load. Both wrong insertion/cascade algorithms are rejected. The
  examples explain preparatory moves and whole-group chain reactions in the UI.
  Full five-color hands remain supported with the independently checked interval
  lower bound; no deadline or source-domain reduction was needed.
  All ten batch-49 wrong algorithms are rejected. Hole instructions, capital,
  circular successors, rolling distance, and ring spelling suites finish in
  55.8, 362.2, 66.8, 52.2, and 572.3 ms after runtime load, respectively.
  This includes full 100×100 dense/snake mazes, 100,000-project sets, 10,000-value
  circular arrays, and 100-character ring/key states. Distinct stopping and hole
  rules, affordability, wraparound, and press-cost explanations render in the UI.
  All eight batch-50 wrong tree algorithms are rejected. Mode, subtree-frequency,
  bottom-left, and row-maximum suites finish in 73.6, 113.6, 69.9, and 83.8 ms
  after runtime load, including 10,000-node chains and broad trees.
  Any-order tied outputs accept reversed order but reject duplicate or missing
  entries. The original step-count reference also passes, and its Fibonacci
  adaptation passes every source input from 0 through 30. A duplicate 509 ID
  is absent from the manifest and returns 404 from the problem API.
  All twelve batch-51 wrong algorithms are rejected. Keyboard, base-seven,
  ranks, perfect-number, palindrome-subsequence, and washing suites finish in
  35.2, 35.2, 70.6, 38.1, 278.4, and 63.7 ms after runtime load, respectively.
  Reordered selected words pass, but changed case and lost/extra occurrences
  fail. Source-scale fixtures include 10,000 items, 1000-character strings,
  full numeric bounds, and 250,000,000 washing rounds without simulation.
  All six rule-specific example explanations render in the problem pane.
  All eight batch-52 wrong algorithms are rejected. Capital, uncommon-subsequence,
  dictionary-deletion, and arrangement suites finish in
  36.1, 35.1, 358.5, and 55.7 ms after runtime load, respectively.
  All 15 legal arrangement inputs pass. The two-string adaptation covers
  length-100 words and rejects truncation; the binary-balance adaptation passes
  100,000 entries and rejects noncontiguous counting. Both duplicate IDs return
  404 and are absent from the library. All four example explanations render.
  All eight batch-53 wrong algorithms are rejected. Residue, abbreviation,
  mine-reveal, and BST-gap suites finish in
  114.6, 123.1, 47.1, and 142.5 ms after runtime load, respectively.
  Large abbreviation groups, 50-by-50 boards, 10,000-node trees, and 100,000-entry
  arrays pass. Mutated BST values fail while a correct copied mine board passes.
  Read-only tree checks additionally reject equal-looking replacements,
  equal-valued child swaps, bool-for-int values, and inserted nodes. Falsey
  originals and fully restored Morris threads pass, followed by normal recovery.
  The duplicate 783 ID is absent and returns 404. All four rule-specific
  example explanations render in the problem pane.
  This is not the full-catalog gate. Exact snapshot hashes and unrounded values
  are in `catalog_import/benchmarks/current.json`.
  Reports also bind the judge contract, built worker, frontend index, and browser
  verifier hashes; the verifier refuses a stale built worker until it is rebuilt.
- Current automated suite: 790 backend tests and 19 frontend tests pass. The
  conversion regressions check all 3,999 valid Roman numerals, the division
  reference's prohibited-operator rule, and string multiplication's avoidance
  of whole-input integer conversion. No deployment or push has been performed.
- Transfer-script tests verify local/custom database path precedence, external
  backup destinations, valid SQLite snapshots, missing-source refusal, and
  unchanged source databases. The handoff retains the existing progress seed.
- Atomic ledger/report/candidate saves preserve the previous complete JSON file
  if replacement is interrupted; a regression test exercises that failure path.

Next: continue behavioral review of the remaining original exercises (nearby
contracts must not be merged blindly), expand verified imports in reproducible
batches, extend ordinary tree/list adapters where required, and run the final
benchmark only when all eligible imports are complete. Current browser metrics
must be labeled interim; a partial-catalog measurement cannot prove the final gate.

Upcoming contract review: sources 470 and 478 require separate protocol review
for injected randomness or constructor/call sequences; they remain pending,
not silently converted to deterministic lookup exercises. Source 479 joins the
finite-domain decision below.

Source 510 is an ordinary BST successor problem and remains in scope: its
function receives one actual node with parent links, not a root argument.
It needs a parent-aware selected-node adapter and identity checks. Do not
exclude it merely because its node type is a class, or silently replace its
interface with the existing root-plus-selected-node successor exercise.

## Pending owner decision: finite input domains

Beautiful Arrangement (526) is not blocked by this limit: its source domain is
n=1..15, allowing two visible examples and thirteen distinct hidden cases.
It is now imported in batch 52: independent inclusion-exclusion counting verifies
the entire domain, literal permutations cross-check n=1..8, and both wrong
algorithms are rejected. The finite-domain exceptions below are still unresolved.

LeetCode 22 and 479 accept only n=1…8; LeetCode 51 and 52 accept only n=1…9. These
contracts cannot supply two visible inputs plus twelve different hidden inputs
without fabricating out-of-range cases. They remain pending, not excluded or
counted as completed. Owner confirmation has been requested for an exception
that exhaustively tests every valid input once. No exception is enabled yet.
