# 363-problem handoff checkpoint

This is a usable partial-catalog release, not completion of the workbook goal.
Its immutable local tag is `python-study-363-checkpoint`. Preparing it does not
push, deploy, replace live progress, or refresh the progress seed. The earlier
345- and 326-problem tags remain unchanged. All measurements here describe this
checkpoint, not future development on `main`.

## What is ready

- 363 runnable problems: 101 originals plus 262 validated workbook imports.
- Every import has two explained visible examples, at least twelve distinct
  hidden tests, two rejected plausible wrong solutions, and 500 oracle comparisons.
- All 345 problems from the last handoff retain their IDs, versions, and content.
- The saved ledger accounts for 72 overlaps, 155 exclusions, and 3,140 pending
  records. Pending content is not shown in the live library.
- 355 backend tests and 16 frontend tests pass; the frontend build succeeds.
- Chrome/Pyodide checks pass for all 262 imported references, incorrect answers,
  judge recovery, offline assets, saved drafts, and progress through a restart.
- Across 100 requests per route, library/search p95 is 1.81/1.50 ms and
  detail/dashboard p95 is at most 4.62 ms on this M3 Pro. Backend startup is
  341 ms; backend peak RSS is 115.30 MiB, excluding browser and test driver.
  This is an interim 363-problem measurement, not the final full-catalog gate.

The report in `catalog_import/benchmarks/current.json` binds the tested catalog,
ledger, judge, frontend assets, and browser verifier by hash.

## 1. Publish from this laptop when ready

From the repository root, inspect the working tree and branch:

```bash
git status --short
git branch --show-current
git push origin main python-study-363-checkpoint
```

These are instructions, not a push already performed. Do not force-push if the
remote has newer work; reconcile it first. The tag identifies this exact catalog
even if later development adds more problems to `main`.

## 2. Update the existing website computer

First back up its **current runtime database**, using its actual configured
path and an external backup destination. Follow
[Backing up online progress](DEPLOYMENT.md#backing-up-online-progress).
Keep its private configuration and persistent database unchanged. Do not copy
this laptop's `data/` or reapply `seed_data/initial_progress.db`.

From the destination repository root, confirm `git status --short` is clean and
the branch is `main`. Stop and resolve local changes without discarding them.
Then run these commands **in order, stopping on any error**:

```bash
git fetch origin main tag python-study-363-checkpoint
git merge --ff-only python-study-363-checkpoint
test "$(git rev-parse HEAD)" = "$(git rev-parse 'python-study-363-checkpoint^{commit}')"
cd "projects/Python Study App"
.venv/bin/python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
.venv/bin/python -m pytest -q
pm2 restart nsy-python-study --update-env
curl -fsS http://127.0.0.1:8791/api/health
```

The revision check must pass before installing/restarting. If the destination
has diverged or is already ahead of the tag, inspect its history instead of
resetting it. Use Node.js 22.12+ and Python 3.11+. These commands reuse the
existing configured website service; they do not set up a new deployment.
For local-only use, run `./run_local.sh` instead of PM2 and open port 8765.
For a first installation, follow [DEPLOYMENT.md](DEPLOYMENT.md); the existing
seed is only copied when the runtime database does not exist and is not a live
sync of this laptop's latest progress.

## 3. Verify the update, then resume expansion

- Health reports `problemCount: 363` (approved personal variants may add more).
- Website health reports `authenticated-website` and `authEnabled: true`;
  unauthenticated progress requests remain blocked.
- Library opens; Decode String and Frog Jump are available.
- Your Passed problems and saved drafts remain present.
- Run examples, submit, save a draft, restart, and confirm progress remains.

After the owner confirms this handoff, resume development from the existing
ledger on this laptop. Do not restart the import or change existing problem IDs.
The website keeps studying against this checkpoint and saving progress in its
own database. Future batches reach it only after another explicit push, update,
frontend build, and restart; catalog updates do not require another progress
transfer. The workbook is not required on the website computer for studying.
