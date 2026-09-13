# 430-problem handoff checkpoint

This is a usable partial-catalog release, not completion of the workbook goal.
The immutable local tag is `python-study-430-checkpoint`. Preparing this checkpoint
does not push, deploy, refresh the progress seed, or replace either computer's
runtime database. All seven earlier checkpoint tags and checklists remain unchanged.

## What is included

- 430 runnable problems: 101 originals and 329 verified workbook imports.
- Eleven additions since the 419 checkpoint: Smallest Good Base, Find Permutation,
  Predict the Winner, Max Consecutive Ones II, Non-decreasing Subsequences,
  Construct the Rectangle, Max Consecutive Ones, Reverse Pairs, Target Sum,
  Diagonal Traverse, and Zuma Game.
- All imports have at least two explained visible examples, twelve distinct
  hidden tests, two rejected plausible wrong solutions, and 500 oracle comparisons.
- Existing problem IDs and content from the 419 checkpoint are preserved.
  The library, daily workload limits, broader reviews with weak-topic priority,
  saved drafts, Passed status, and persistent progress remain available.
- The workbook ledger records 78 overlaps, 329 imports, 155 exclusions, and
  3,067 pending records. Pending content is not in the runnable library.
- The release's complete backend suite passes 667 tests; all 19 frontend tests
  pass, and the production frontend build succeeds. Validation evidence for all
  329 imports and nine independently proved adaptations matches the packaged
  content; all 3,629 source snapshots match their ledger hashes.
- A fresh Chrome/Pyodide run passes all 329 imported reference suites plus four
  original reference suites, wrong-answer and output-contract checks, all five
  result categories, timeout recovery, offline assets, and real restart persistence.
- Across 100 requests per route, library/search p95 is 1.13/1.14 ms and the four
  measured detail/dashboard routes are at most 1.33 ms. Startup is 341 ms and
  backend peak RSS is 256.52 MiB on the test M3 Pro, excluding browser and driver.

These checks ran against the current packaged files, not an earlier checkpoint.
The benchmark's content, ledger, judge, built frontend, and verifier hashes are
checked before tagging. Tests use isolated temporary progress databases, not the
owner's study database. No unfinished import artifacts are included in this tag.

Normal studying needs neither the workbook nor import generation. Verification
details and the matching browser/performance report are in
[CATALOG_EXPANSION.md](CATALOG_EXPANSION.md) and
`catalog_import/benchmarks/current.json` at this tag. These partial-catalog
measurements do not establish completion of the full workbook performance gate.

## 1. Publish the checkpoint from this laptop

From the repository root, inspect and then publish this exact tag:

```bash
git status --short
git show --stat python-study-430-checkpoint
git push origin python-study-430-checkpoint
```

These are owner-run instructions; no push has been performed. The tag fixes the
version even if local development later advances. If you also want GitHub's
`main` updated to your inspected local `main`, use
`git push origin main python-study-430-checkpoint` instead. Never force-push over
newer work. Do not use `git add .` to collect unrelated changes or runtime data.

## 2. Update the existing website computer

First back up its **current runtime database** using its actual configured path:
see [Backing up online progress](DEPLOYMENT.md#backing-up-online-progress).
Keep the private service configuration and persistent database. Do not copy this
laptop's `data/`, delete the destination database, or reapply the old progress seed.

At the destination repository root, check `git status --short` and
`git branch --show-current`. These instructions expect a clean checkout on `main`.
Resolve any changes without discarding them. Run the following **in order,
stopping on any error**:

```bash
git fetch origin tag python-study-430-checkpoint
git merge --ff-only python-study-430-checkpoint
test "$(git rev-parse HEAD)" = "$(git rev-parse 'python-study-430-checkpoint^{commit}')"
cd "projects/Python Study App"
.venv/bin/python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
.venv/bin/python -m pytest -q
pm2 restart nsy-python-study --update-env
curl -fsS http://127.0.0.1:8791/api/health
```

The revision check must pass before installing or restarting. If the destination
is ahead of the tag or diverged, inspect its history rather than resetting it.
Use Python 3.11+ and Node.js 22.12+. These commands reuse the existing website
service; they do not configure a new deployment. For local use, replace the PM2
restart with `./run_local.sh` and open `http://127.0.0.1:8765`. For a first-time
installation, follow [DEPLOYMENT.md](DEPLOYMENT.md). The tracked seed is an old
one-time snapshot, not a live sync of this laptop's latest progress.

## 3. Check the update before resuming expansion

- Health reports `problemCount: 430` (approved personal variants may add more).
- Website health reports `authenticated-website` and `authEnabled: true`.
- The Library opens and Target Sum, Diagonal Traverse, and Zuma Game are available.
- Existing Passed problems and saved drafts are still present.
- Run examples, submit, save a draft, restart, and confirm progress remains.

The website keeps using this checkpoint and saves subsequent progress in its
own persistent database while development continues on this laptop. New approved
batches do not appear there automatically: they require another explicit code
update, frontend build, and service restart. Routine updates do not transfer or
merge progress. After confirming the website update, resume from the current
ledger and batch-48 checkpoint; do not re-import completed problems, rename
existing IDs, or move this tag. The remaining workbook goal stays unfinished.
