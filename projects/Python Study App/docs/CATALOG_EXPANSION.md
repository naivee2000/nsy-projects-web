# Workbook catalog expansion

Status: in progress. Pending and quarantined records are not runnable imports.

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
- Current behavioral mapping: 72 existing equivalents (69 original exercises and
  three approved imports). Static evidence identifies 155 approved-scope
  design/interactive exclusions; 3,187 rows remain pending.
- 215 new imports in twenty-nine reviewed batches pass deterministic tests and
  500 independent oracle inputs each. The published catalog contains 316 problems.
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
- Auditing original overlap 104 reproduced a RecursionError at 10,000 nodes in
  Tree Height's version-1 recursive reference, despite its 20,000-node contract.
  Version 2 uses explicit DFS frames under the same ID and signature. A separate
  breadth-first oracle and 500 seeded binary-path shapes verify depth independently;
  deterministic cases include 10,000-/20,000-node right chains, a 20,000-node left
  chain, and a wide 20,000-node tree. Plausible edge-counting and left-only mistakes
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
- The shared judge now has validated contracts for flexible wiggle outputs,
  declared read-only parameters, and optional existing-node results. It also has
  a validated contract for selecting real TreeNode
  arguments from an input tree and requiring the returned node to retain its
  identity. Both batch-twenty-four LCA exercises use the contract, and copied
  nodes or tree mutations are rejected. It also supports an embedded full-list
  context that supplies one real non-tail ListNode and checks the complete list
  afterward. All 215 published imports have matching passing reports in the
  316-problem package.
- The interim benchmark now records kernel high-water RSS for both backend
  runs, not occasional memory samples. It excludes browser/driver memory.
- Current 316-problem Chrome/M3 Pro run: library/search p95 1.18/1.09 ms,
  detail p95 1.15 ms for Word Search and 1.15 ms for the 100,000-node selected-
  list problem, and dashboard p95 1.36 ms (100 requests per route). Startup is
  340 ms and backend peak RSS is 86.81 MiB after loading the largest linked-list
  detail. All 215 imported references and
  upgraded Spiral Matrix/Tree Height pass in Pyodide with external HTTP blocked.
  The nine batch-twenty-nine suites complete within 505 ms after runtime load.
  Count of Range Sum takes 505 ms including its 100,000-element case; the
  increasing matrix path takes 147.7 ms including a 40,000-cell snake; all
  32,768 length-15 abbreviations take 64.8 ms. The other six stay below 52 ms.
  Tree Height's suite with 20,000-node chains takes 99.4 ms. Existing
  large in-place, string, stock, circuit, candy, and tree fixtures still pass.
  Browser checks also verify grading explanations,
  returned-copy/count-only rejection, strict prefix counts, and reordered survivors.
  Equal-valued nodes in the wrong order and replacement TreeNodes are rejected
  despite matching displayed values; correct in-place rewiring is accepted.
  Balanced-BST checks accept a different valid shape and reject wrong inorder,
  missing duplicates, internal imbalance, and invalid node values in Chrome.
  Selected ListNode checks accept the constant-space splice and reject both a
  wrong deleted value and replacement nodes whose displayed values look correct.
  This is not the full-catalog gate. Exact snapshot hashes and unrounded values
  are in `catalog_import/benchmarks/current.json`.
- Current automated suite: 253 backend tests and 12 frontend tests pass. The
  conversion regressions check all 3,999 valid Roman numerals, the division
  reference's prohibited-operator rule, and string multiplication's avoidance
  of whole-input integer conversion. No deployment or push has been performed.
- Atomic ledger/report/candidate saves preserve the previous complete JSON file
  if replacement is interrupted; a regression test exercises that failure path.

Next: continue behavioral review of the remaining original exercises (nearby
contracts must not be merged blindly), expand verified imports in reproducible
batches, extend ordinary tree/list adapters where required, and run the final
benchmark only when all eligible imports are complete. Current browser metrics
must be labeled interim; a partial-catalog measurement cannot prove the final gate.

## Pending owner decision: finite input domains

LeetCode 22 accepts only n=1…8; LeetCode 51 and 52 accept only n=1…9. These
contracts cannot supply two visible inputs plus twelve different hidden inputs
without fabricating out-of-range cases. They remain pending, not excluded or
counted as completed. Owner confirmation has been requested for an exception
that exhaustively tests every valid input once. No exception is enabled yet.
