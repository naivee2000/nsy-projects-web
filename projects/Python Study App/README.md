# Code Practice Lab

A private, local-only Python interview-practice app. It includes 100 distinct coding problems, a browser-isolated Pyodide judge, progressive wrong-answer coaching, hints, a guided daily queue, review scheduling, SQLite progress, and an optional Codex-assisted variant workflow.

## Start the app

Requirements: Python 3, Node.js/npm, and macOS or another Unix-like system.

```bash
./run_local.sh
```

The first run installs dependencies and builds the frontend. Later runs work without internet. Open [http://127.0.0.1:8765](http://127.0.0.1:8765). The server binds only to `127.0.0.1`; there is no login or deployment mode.

If frontend source changes, run `npm --prefix frontend run build` before starting again, or remove `frontend/dist` and use `./run_local.sh`.

## Study workflow

- **Today** assigns one fixed daily set: five easy problems, four when the set includes medium work, or three when it includes a hard/advanced problem. Finished items disappear without being replaced, and a completion message remains until the next local calendar day.
- **Daily review** separately assigns up to five previously passed problems and removes each one after a successful review submission that day.
- **Library** filters all approved problems by title and topic.
- **Back navigation** returns a problem to the page that opened it—Today or Library—without clearing the Library filters.
- **Run examples** executes only visible tests. Every problem has two hand-curated teaching examples: a representative case, a contrasting or boundary case, and a short explanation of why the shown output is correct.
- **Submit** executes the hidden package and records the outcome.
- **Local Coach** explains one likely mistake at a time after an unresolved run. Its three-step ladder moves from concrete evidence to a debugging question without revealing the full solution.
- **Ask Codex coach** is optional and runs only after an explicit click. It sends the problem, visible failure evidence, and current draft to the locally authenticated Codex CLI for deeper Socratic feedback. It requires Codex login and may require internet access.
- Hints unlock in concept, strategy, pseudocode, and editorial order.
- Draft code, attempts, mastery, and review dates are stored in `data/code_practice.db`.

## Easy-problem quality bar

The catalog uses original wording and implementations; it does not copy LeetCode statements. LeetCode's official Easy catalog and study-plan patterns are used only as a difficulty benchmark: an Easy problem should still require at least one reusable invariant, data-structure choice, recurrence, or edge-case decision.

A catalog audit replaced seven syntax-level exercises while keeping the total at exactly 100 problems (33 easy, 56 medium, and 11 advanced):

- Range Span → **Balanced Pivot Index** for running-left and derived-right prefix sums.
- Reverse Word Order → **Word Pattern Bijection** for two-way mapping consistency.
- Longest Word Length → **Formable Word Total** for character-frequency inventory reasoning.
- Count Negative Cells → **Missing and Repeated Grid Values** for matrix flattening and frequency reconciliation.
- Boundary Land Cells → **Flood Fill Region** for recursive connectivity and the same-color guard.
- Linked List Length → **Deduplicate a Sorted Linked List** for in-place pointer rewiring.
- Recursive Sum to N → **Recursive Step Combinations** for a memoized two-state recurrence.

Short introductory problems remain only when they isolate a useful interview pattern. Examples include local peaks for safe neighbor boundaries, matrix transposition for coordinate mapping, run-length encoding for run-boundary state, recursive tree sum/leaf count for structural base cases, and linked-list middle for fast/slow pointers.

Research references: [LeetCode 75](https://leetcode.com/studyplan/leetcode-75/), [Find Pivot Index](https://leetcode.com/problems/find-pivot-index/), [Word Pattern](https://leetcode.com/problems/word-pattern/), [Find Words That Can Be Formed by Characters](https://leetcode.com/problems/find-words-that-can-be-formed-by-characters/), [Find Missing and Repeated Values](https://leetcode.com/problems/find-missing-and-repeated-values/), [Flood Fill](https://leetcode.com/problems/flood-fill/), [Remove Duplicates from Sorted List](https://leetcode.com/problems/remove-duplicates-from-sorted-list/), and [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/).

The submitted Python runs in a fresh browser Web Worker. FastAPI stores results but never executes submitted code. The offline coach performs static syntax-tree inspection only, so normal studying does not depend on an AI service or internet connection. The optional Codex coach runs ephemerally in a read-only sandbox, receives no reference solution or hidden-test evidence, and is filtered to reject complete solutions and code-heavy answers. Hidden tests are hidden from the normal problem response, but—as expected for a personal browser judge—they can be inspected with browser developer tools.

## Back up progress

```bash
./backup_data.sh
```

Backups are written under `backups/`, which is intentionally excluded from Git.

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

- One local user
- Python function-signature problems only
- No authentication, hosting, PM2, Cloudflare, or synchronization
- No server-side execution of submitted answers
- Optional Codex coaching never blocks offline studying
