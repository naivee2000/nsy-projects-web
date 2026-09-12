# 345-problem handoff checkpoint

This is a usable partial-catalog release, not completion of the workbook goal.
Its local Git tag is `python-study-345-checkpoint`. No push, deployment, live
progress replacement, or seed refresh is part of preparing this checkpoint.
All counts and measurements on this page describe that tag, not later `main`
commits. The README and expansion ledger describe the current development catalog.
The earlier `python-study-326-checkpoint` tag remains unchanged; this new tag
includes the nineteen additional validated problems from batches 32 and 33.

## What ships

- 345 runnable problems: all 101 originals plus 244 approved workbook imports.
- Each import has two explained visible examples, at least twelve distinct hidden
  tests, two rejected plausible wrong implementations, and 500 oracle comparisons.
- All 326 problems from the previous checkpoint retain their IDs, versions, and content.
- The ledger retains 72 overlaps, 155 exclusions, and 3,158 pending records.
  Pending/quarantined content is not available in the live library.
- Code, judge assets, packaged questions, provenance, and resumable development
  records travel through Git. Runtime progress does not.

The browser verification report in `catalog_import/benchmarks/current.json` at this tag
identifies the exact tested manifest and ledger hashes. It covers real Chrome/
Pyodide execution, offline assets, pagination, errors, timeout recovery, and
progress persistence through a backend restart. This is an interim performance
measurement of the shipped 345, not the final full-workbook benchmark.

Verification: 311 backend tests and 15 frontend tests pass; the frontend build
succeeds. All 244 imported references pass in Chrome/Pyodide, including large
inputs, strict-wiggle alternatives, and ordered leaf-removal groups. The recorded
browser report matches this release's manifest and ledger hashes. Library/search
p95 is 1.22/1.09 ms; detail/dashboard p95 is at most 2.25 ms over 100 requests per
route on this M3 Pro. Backend startup is 338 ms and peak RSS is 84.24 MiB.
Other hardware can differ.

## 1. Push when ready, from this laptop

From the repository root, inspect the branch and changes first:

```bash
git status --short
git branch --show-current
git push origin main python-study-345-checkpoint
```

Do not force-push. If the remote has newer work, reconcile it before publishing.
The tag is an immutable reference to this checkpoint; later `main` commits may
contain more approved problems. These commands are instructions, not actions
already performed during release preparation.

## 2. Update the existing website computer

1. Confirm its persistent progress path in the private PM2 configuration. Keep
   that path and its database unchanged. Back it up before updating; use
   [the production backup instructions](DEPLOYMENT.md#backing-up-online-progress).
2. From the destination repository root, ensure `git status --short` is clean
   and `git branch --show-current` reports `main`. Do not discard local changes.
3. Fetch and fast-forward to the exact release tag, reinstall locked dependencies,
   build, test, and restart. Fetching does not install later development batches:

```bash
git fetch origin main tag python-study-345-checkpoint
git merge --ff-only python-study-345-checkpoint
test "$(git rev-parse HEAD)" = "$(git rev-parse 'python-study-345-checkpoint^{commit}')"
cd "projects/Python Study App"
.venv/bin/python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
.venv/bin/python -m pytest -q
pm2 restart nsy-python-study --update-env
curl -fsS http://127.0.0.1:8791/api/health
```

Run the commands in order and stop on any error; do not restart a failed build.
The revision check must succeed before continuing. If this computer is already
ahead of the tag or has diverged, stop and inspect its history; do not reset or
force-push to make it match.
This uses the existing configured PM2 service and hostname; it does not create
a new deployment. The frontend needs Node.js 22.12+ (24 LTS recommended).
For a new computer without the app installed, follow [DEPLOYMENT.md](DEPLOYMENT.md)
instead. For local-only operation, use `./run_local.sh` instead of PM2.

## 3. Confirm the handoff before resuming expansion

- Health reports `problemCount: 345` for this checkpoint. Approved personal
  variants can increase this total.
- In website mode, health reports `authenticated-website` and `authEnabled: true`;
  unauthenticated progress API requests remain blocked.
- Library opens and an imported problem such as Find Leaves of Binary Tree is available.
- Your previously Passed problems and saved drafts remain present.
- Run examples, submit, save a draft, restart, and confirm the new progress remains.
- Keep the backup outside the checkout. Never copy this laptop's `data/` over
  an existing destination database during a catalog update.

If the destination already has live progress, do **not** refresh or reapply the
seed. If it is a first installation and you want this laptop's latest progress,
refresh and commit `seed_data/initial_progress.db` immediately before that
one-time transfer using the deployment guide. The seed is copied only when the
destination runtime database is absent; it is not continuous synchronization.

## Continuing the goal afterward

Resume import work on this laptop only when requested. Keep adding validated
batches, maintain stable existing problem IDs, and publish only passing content.
The other computer keeps using its installed checkpoint and writing progress
locally. It will not see development changes until an explicit later push, pull,
frontend build, and backend restart. Those catalog updates must retain the
destination's live database; no repeated progress migration is needed.

The workbook does not need to be copied to the website computer for studying.
Portable source snapshots and the pending ledger remain in the repository for
resuming development. Full-import completion and its final performance gate
remain unfinished.
