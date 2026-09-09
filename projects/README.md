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
- `Python Study App/` - Code Practice Lab, a private Python interview-practice app with 101 distinct problems, recursion exercises from easy through hard, a Pyodide judge, visible test tracing, progressive hints, mastery tracking, saved drafts, and persistent SQLite progress. It runs locally without login or as an authenticated personal website whose backend remains on `127.0.0.1` behind the existing tunnel.

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

The Easy catalog is benchmarked against reusable patterns in LeetCode's official Easy problems, while retaining original wording and implementations. A quality audit removed seven syntax-only exercises—including Range Span and Longest Word Length—and replaced them with Balanced Pivot Index, Word Pattern Bijection, Formable Word Total, Missing and Repeated Grid Values, Flood Fill Region, Deduplicate a Sorted Linked List, and Recursive Step Combinations. Merge Two Sorted Linked Lists was later added for dummy-head, tail-pointer, and existing-node splicing practice. The catalog now contains 101 problems: 34 easy, 56 medium, and 11 advanced.

The library completion filter can show all problems, only unsolved problems, or only passed problems for review. Daily recommendations and the optional weekly challenge exclude problems already marked Passed.

The Today page assigns one fixed workload-capped set per local calendar day: five Easy problems; normally two Medium plus one Easy (or at most three Medium when no Easy remains); or one Hard plus at most one Medium. Completed items disappear from that fixed set without being replaced. After the final assigned problem passes, the app shows a finished message and waits until the next day to create another set. A separate fixed daily review checklist selects up to five previously passed problems. Review priority combines spaced-review due dates with difficulty, failures after the first successful solve, time spent relative to the estimate, and whether the latest attempt failed. It also deliberately revisits linked lists, recursion, and binary search more often, with the strongest preference for recursive matrix/grid traversal; hint usage does not influence review selection. A review disappears after another successful full submission that day, is not replaced, and the section shows a finished message after every assigned review is checked.

Linked-list and tree problems show the full `ListNode` or `TreeNode` class definition above the function in the editable code pane. The app also prepends the required class when reopening an older saved draft that predates this feature.

The private repository also carries a one-time SQLite seed containing the current owner progress. On the first website start, it is copied to a persistent directory outside the checkout. Later online progress lives only in that deployment-host database and survives restarts and Git pulls without being overwritten by the seed.

Detailed setup, testing, backups, architecture, and coaching safeguards are documented in `Python Study App/README.md`; deployment and progress-transfer instructions are in `Python Study App/docs/DEPLOYMENT.md`.
