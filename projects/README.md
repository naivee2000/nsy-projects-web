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
- `Python Study App/` - Code Practice Lab, a private Python interview-practice app with 291 runnable problems so far, recursion exercises from easy through hard, a Pyodide judge, visible test tracing, progressive hints, mastery tracking, saved drafts, and persistent SQLite progress. Its 3,629-row workbook expansion is in progress. It runs locally without login or as an authenticated personal website whose backend remains on `127.0.0.1` behind the existing tunnel.

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

Passing the two explained examples is labeled **Examples passed** and states that the code is correct for those shown cases. Submit then runs the twelve hidden cases. Passed hidden cases stay summarized, while a failed hidden case has a clickable dropdown containing the test input, expected output, and the current code's output or error. A successful full submission persistently marks the problem **Passed** in the workspace header and problem library, and updates dashboard progress.

All 101 problems use two hand-curated visible examples instead of shared placeholder inputs. Each pair demonstrates the problem's defining rule plus a contrasting or boundary case, and the interface explains in plain language why each output follows from its input. Catalog tests require these explanations and verify representative regression cases such as balanced prefix sums, valid versus invalid mappings, invalid bracket nesting, linked-list splicing, and missing/repeated matrix values.

The original Easy catalog is benchmarked against reusable patterns in LeetCode's official Easy problems, while retaining original wording and implementations. A quality audit removed seven syntax-only exercises—including Range Span and Longest Word Length—and replaced them with Balanced Pivot Index, Word Pattern Bijection, Formable Word Total, Missing and Repeated Grid Values, Flood Fill Region, Deduplicate a Sorted Linked List, and Recursive Step Combinations. Merge Two Sorted Linked Lists was later added for dummy-head, tail-pointer, and existing-node splicing practice. Before workbook expansion, this original catalog contained 101 problems: 34 easy, 56 medium, and 11 advanced.

The library fetches 30 summaries at a time, with server-side search and filters for topic, difficulty, and passed/unsolved status. Problem details load on demand. Daily recommendations and the optional weekly challenge exclude problems already marked Passed, including accepted solutions older than the latest 500 attempts.

The workbook expansion currently accounts for 3,629 rows: 70 existing equivalents,
190 verified new problems, 130 documented design/interactive exclusions, and 3,239
pending records. Ordinary trees and linked lists remain included.
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
The overlap total includes 69 original exercises plus one approved import that
also covers a narrower workbook contract. Rotated minimum 153 maps to 154 after
500 seeded correctness/logarithmic-read checks, without a duplicate progress ID.
Run `.venv/bin/python -m code_practice.reconcile_overlaps` from the app folder
after revalidating changed overlap targets and before repackaging. Stale source,
target, judge, or proof data blocks publication rather than silently retaining
an unproved equivalence. Normal studying does not execute these offline checks.

Published content is portable under `Python Study App/catalog_data/`; startup does not execute reference solutions. Transfer this folder with the app, retain the destination computer's existing progress database, and restart after updates. Rebuild packaged content with `.venv/bin/python -m code_practice.package_catalog` from the app folder; that command never opens or replaces progress. Backup and restoration instructions and the interim browser benchmark command are in the app README. Full import and full-catalog performance acceptance remain unfinished.

Monaco editor and Pyodide runtime assets are included in the local frontend build, so studying needs no CDN after installation. Import validation runs in bounded per-problem processes and quarantines failures. The Chrome check uses a temporary progress database, blocks external requests, tests restart persistence, measures 100 requests per API route, and records OS-reported backend peak memory. No deployment or push is part of this expansion work.

The Today page assigns one fixed workload-capped set per local calendar day: five Easy problems; normally two Medium plus one Easy (or at most three Medium when no Easy remains); or one Hard plus at most one Medium. Completed items disappear from that fixed set without being replaced. After the final assigned problem passes, the app shows a finished message and waits until the next day to create another set. A separate fixed daily review checklist selects up to five previously passed problems. Review priority combines spaced-review due dates with difficulty, failures after the first successful solve, time spent relative to the estimate, and whether the latest attempt failed. A full five-problem review uses at most three focus slots for linked lists, recursion, binary search, and recursive matrix/grid traversal, reserving two slots for other completed topics whenever available; hint usage does not influence review selection. A review disappears after another successful full submission that day, is not replaced, and the section shows a finished message after every assigned review is checked.

Linked-list and tree problems show the full `ListNode` or `TreeNode` class definition above the function in the editable code pane. The app also prepends the required class when reopening an older saved draft that predates this feature.

The private repository also carries a one-time SQLite seed containing the current owner progress. On the first website start, it is copied to a persistent directory outside the checkout. Later online progress lives only in that deployment-host database and survives restarts and Git pulls without being overwritten by the seed.

Detailed setup, testing, backups, architecture, and coaching safeguards are documented in `Python Study App/README.md`; deployment and progress-transfer instructions are in `Python Study App/docs/DEPLOYMENT.md`.
