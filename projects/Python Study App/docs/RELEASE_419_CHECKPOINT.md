# 419-problem handoff checkpoint

This is a usable partial-catalog release, not completion of the workbook goal.
The immutable local tag is `python-study-419-checkpoint`. Preparing it does not
push, deploy, replace live progress, or refresh the progress seed. All six earlier
checkpoint tags and historical checklists remain unchanged.

## What is ready

- 419 runnable problems: 101 originals and 318 verified workbook imports.
- Every import has two explained visible examples, at least twelve distinct
  hidden tests, two rejected plausible wrong solutions, and 500 oracle comparisons.
- Seven additions since the 412 checkpoint: Convex Polygon, Number Complement,
  Total Hamming Distance, Magical String, License Key Formatting, The Maze, and
  Sliding Window Median.
- Number Complement and Assign Cookies have versioned domain extensions for
  zero and 100,000-item matching inputs respectively. Existing IDs, old Passed
  status, and saved drafts are preserved.
- The release ledger records 76 overlaps, 318 imports, 155 exclusions, and
  3,080 pending workbook records. Pending problems are not in the live library.
- 598 backend tests and 19 frontend tests pass; the frontend build succeeds.
- The matching Chrome/Pyodide report covers all 318 imported references,
  incorrect answers, timeout recovery, offline assets, and progress through an
  actual backend restart.
- Across 100 requests per route, library/search p95 is 1.55/1.68 ms; the measured
  detail/dashboard routes are at most 1.79 ms. Startup is 337 ms and backend peak
  RSS is 245.46 MiB on the test M3 Pro, excluding browser and test driver.
  These are interim measurements, not acceptance of the eventual full catalog.

Release preparation uses an isolated checkout of `ba72477`, reruns the backend
and frontend tests, rebuilds the frontend and catalog, and checks validation and
benchmark hash bindings. It reuses the matching batch-45 browser run in
`catalog_import/benchmarks/current.json`; it does not claim a new browser run.
Normal studying requires neither the source workbook nor import generation.

Six batch-46 candidates (483, 484, 486, 487, 491, 492) remain unfinished laptop
working files. Initial candidate validation is not release acceptance: targeted
regressions, catalog packaging, and browser checks still need to be completed.
The candidate/report files, local ledger changes, `import_batch_046.py`, and its
builder registration are intentionally excluded from this tag. Preserve them
when resuming; do not reset or clean them away.

## 1. Publish only this checkpoint from the laptop

From the repository root:

```bash
git status --short
git show --stat python-study-419-checkpoint
git push origin python-study-419-checkpoint
```

These are instructions, not a push already performed. Publishing only the tag
transfers the exact tested revision, even if local `main` later advances. Do not
use `git add .`: unfinished working files are deliberately outside the release.
If the owner also wants to update GitHub's `main`, use
`git push origin main python-study-419-checkpoint` instead, after inspecting what
`main` contains. Never force-push over newer remote work.

## 2. Update the existing website computer

First back up its **current runtime database**, using its configured path and an
external backup destination; see [Backing up online progress](DEPLOYMENT.md#backing-up-online-progress).
Keep private configuration and the persistent database. Do not copy the laptop's
`data/`, delete the destination database, or reapply the progress seed.

At the destination repository root, confirm `git status --short` is clean and
`git branch --show-current` reports `main`. Resolve changes without discarding
them. Run these commands **in order, stopping on any error**:

```bash
git fetch origin tag python-study-419-checkpoint
git merge --ff-only python-study-419-checkpoint
test "$(git rev-parse HEAD)" = "$(git rev-parse 'python-study-419-checkpoint^{commit}')"
cd "projects/Python Study App"
.venv/bin/python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
.venv/bin/python -m pytest -q
pm2 restart nsy-python-study --update-env
curl -fsS http://127.0.0.1:8791/api/health
```

The revision check must pass before installing or restarting. If the destination
is ahead of the tag or has diverged, inspect its history rather than resetting it.
These commands reuse the existing configured website service; they do not create
a deployment. Use Python 3.11+ and Node.js 22.12+. For local use, replace the PM2
restart with `./run_local.sh` and open `http://127.0.0.1:8765`. For first-time setup,
follow [DEPLOYMENT.md](DEPLOYMENT.md). The existing seed is an earlier one-time
snapshot, not a live sync of this laptop's latest study progress.

## 3. Confirm the update, then resume expansion

- Health reports `problemCount: 419` (approved personal variants may add more).
- Website health reports `authenticated-website` and `authEnabled: true`.
- The Library opens and The Maze and Sliding Window Median are available.
- Existing Passed problems and saved drafts remain available.
- Run examples, submit, save a draft, restart, and confirm progress remains.

After the owner confirms the other computer is updated, resume from the existing
laptop ledger and batch-46 files. Do not restart the import or change published
problem IDs. The website keeps using this checkpoint and saving new progress in
its own persistent database while development continues here. Future approved
batches reach it only through another explicit code update, frontend build, and
restart. Routine catalog updates do not need another progress transfer.
