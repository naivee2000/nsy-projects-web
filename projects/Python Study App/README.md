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

- **Today** recommends at most three problems: due review, weak-topic practice, then new material.
- **Library** filters all approved problems by title and topic.
- **Run examples** executes only visible tests.
- **Submit** executes the hidden package and records the outcome.
- **Local Coach** explains one likely mistake at a time after an unresolved run. Its three-step ladder moves from concrete evidence to a debugging question without revealing the full solution.
- **Ask Codex coach** is optional and runs only after an explicit click. It sends the problem, visible failure evidence, and current draft to the locally authenticated Codex CLI for deeper Socratic feedback. It requires Codex login and may require internet access.
- Hints unlock in concept, strategy, pseudocode, and editorial order.
- Draft code, attempts, mastery, and review dates are stored in `data/code_practice.db`.

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
- No server-side execution of submitted answers
