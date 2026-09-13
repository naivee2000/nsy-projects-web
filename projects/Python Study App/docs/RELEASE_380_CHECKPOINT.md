# 380-problem handoff checkpoint

This is a usable partial-catalog release, not completion of the workbook goal.
The immutable local tag is `python-study-380-checkpoint`. Preparing this release
does not push, deploy, replace live progress, or refresh the progress seed.
The earlier 363-, 345-, and 326-problem tags remain unchanged.

## What is ready

- 380 runnable problems: 101 originals and 279 verified workbook imports.
- Every import has two explained visible examples, at least twelve distinct
  hidden tests, two rejected plausible wrong solutions, and 500 oracle comparisons.
- All 363 problems from the previous handoff retain their IDs, versions, and content.
- The release ledger records 73 overlaps, 155 exclusions, and 3,122 pending rows.
  Pending content does not appear in the library.
- 379 backend tests and 16 frontend tests pass; the frontend build succeeds.
- The matching Chrome/Pyodide report covers all 279 imported references, incorrect
  answers, timeout recovery, offline assets, and saved progress through a restart.
- Across 100 requests per route, library/search p95 is 1.48/1.72 ms and
  detail/dashboard p95 is at most 1.81 ms on this M3 Pro. Backend startup is
  346 ms; backend peak RSS is 131.45 MiB, excluding browser and test driver.
  These are interim measurements, not acceptance of the eventual full catalog.

The report in `catalog_import/benchmarks/current.json` binds the catalog, ledger,
judge, built frontend assets, and browser verifier by hash. Release preparation
rechecks those bindings, rebuilds the catalog, and reruns backend/frontend tests
in an isolated checkout. It reuses the matching batch-38 browser run; it does
not represent a new browser run.

Eleven additional candidate problems from batch 39 remain only in the laptop's
unfinished working changes. They are deliberately excluded from this tag until
their remaining regression, browser, and packaging checks are complete. Keep
those working changes when resuming; do not reset or clean them away.

## 1. Publish this checkpoint from the laptop

From the repository root:

```bash
git status --short
git show --stat python-study-380-checkpoint
git push origin main python-study-380-checkpoint
```

These are instructions, not a push already performed. Do not use `git add .`:
unfinished batch-39 files are intentionally uncommitted and are not sent by a
push. Do not force-push if the remote has newer work. If later development has
already advanced `main` and you only want this checkpoint, publish only the tag:
`git push origin python-study-380-checkpoint`.

## 2. Update the existing website computer

First back up its **current runtime database** using its configured path and an
external backup destination; see [Backing up online progress](DEPLOYMENT.md#backing-up-online-progress).
Keep its private configuration and persistent database. Do not copy this laptop's
`data/`, delete the destination database, or reapply the progress seed.

At the destination repository root, confirm `git status --short` is clean and
`git branch --show-current` reports `main`. Resolve local changes without
discarding them. Run the following **in order, stopping on any error**:

```bash
git fetch origin tag python-study-380-checkpoint
git merge --ff-only python-study-380-checkpoint
test "$(git rev-parse HEAD)" = "$(git rev-parse 'python-study-380-checkpoint^{commit}')"
cd "projects/Python Study App"
.venv/bin/python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
.venv/bin/python -m pytest -q
pm2 restart nsy-python-study --update-env
curl -fsS http://127.0.0.1:8791/api/health
```

The revision check must pass before installing or restarting. If the destination
has diverged or is ahead of the tag, inspect its history rather than resetting it.
Use Python 3.11+ and Node.js 22.12+. These commands reuse the existing configured
website service; they do not create a deployment. For local use, replace the
PM2 restart with `./run_local.sh` and open `http://127.0.0.1:8765`.
For a first installation, follow [DEPLOYMENT.md](DEPLOYMENT.md). The existing seed
is an old one-time snapshot, not a live sync of this laptop's latest progress.

## 3. Confirm the handoff before resuming expansion

- Health reports `problemCount: 380` (approved personal variants may add more).
- Website health reports `authenticated-website` and `authEnabled: true`.
- Library opens; Pacific Atlantic Water Flow and Strong Password Checker appear.
- Your Passed problems and saved drafts remain available.
- Run examples, submit, save a draft, restart, and confirm that progress remains.

After the owner confirms the update, resume from the existing laptop ledger and
batch-39 working files. Do not restart the import or change published problem IDs.
The other computer continues using this checkpoint and saving progress in its own
database. Later catalog batches reach it only after an explicit code update,
frontend build, and restart; no further progress transfer is needed. The workbook
is not required on the website computer for studying.
