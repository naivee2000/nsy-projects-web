# Code Practice Lab Private Website Deployment

This deployment keeps the FastAPI service and SQLite progress on the always-on website Mac. GitHub carries one initial progress snapshot; after first start, the deployment Mac's persistent database becomes the only live copy.

For the verified 430-problem release and the existing-install update sequence, see [RELEASE_430_CHECKPOINT.md](RELEASE_430_CHECKPOINT.md). The later 459-problem package is local development, not a tagged release or a prerequisite for using this checkpoint. Preparing development work did not deploy, push, or refresh the progress seed. Earlier checkpoint checklists remain historical documentation for their unchanged tags.

## Production shape

```text
authenticated browser
→ private study hostname
→ Cloudflare Tunnel
→ http://127.0.0.1:8791
→ PM2: FastAPI + compiled React frontend
→ persistent SQLite database on the deployment Mac
```

The service must remain bound to `127.0.0.1`. The Cloudflare route is the only public route. The owner may use the existing NSY sign-in session; other people use study-only accounts created by the owner. Authentication protects saved drafts, attempts, hidden submission packages, and progress APIs. Each authenticated identity selects its own progress database.

## How the one-time progress transfer works

The private repository contains `seed_data/initial_progress.db`, a consistent snapshot of the owner's current local progress. Production sets both:

```text
CODE_PRACTICE_SEED_DB=<checkout>/seed_data/initial_progress.db
CODE_PRACTICE_DATA_DIR=<persistent directory outside the checkout>
```

On startup:

1. If `<persistent directory>/code_practice.db` does not exist, the app validates and copies the seed there.
2. If the runtime database already exists, the seed is ignored.
3. All new online attempts, drafts, hints, mastery, and review dates are written only to the runtime database.
4. Git pulls, app restarts, and later seed-file changes never overwrite that runtime database.

Deleting the persistent runtime database causes the next start to return to the original seed snapshot. Keep backups of the runtime database after online studying begins.

## 1. Refresh the seed only for a first-time progress transfer

On the current study Mac:

```bash
cd "projects/Python Study App"
./scripts/refresh_progress_seed.sh
sqlite3 seed_data/initial_progress.db "PRAGMA integrity_check;"
```

Commit the seed only to the private repository. It contains personal draft and attempt source code.
Skip this step if the website computer already has the progress you want to keep. Pulling a refreshed seed will not merge it into an existing runtime database. A later deliberate migration must be backed up and handled separately; do not delete the destination database just to force seed installation.

## 2. Install on the deployment Mac

```bash
git clone https://github.com/naivee2000/nsy-projects-web.git
cd "nsy-projects-web/projects/Python Study App"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
npm --prefix frontend install
npm --prefix frontend run build
PYTHONPATH=. .venv/bin/pytest -q
```

Create a persistent directory outside the checkout. Replace the example path with a location owned by the PM2 user:

```bash
mkdir -p "/path/to/persistent/code-practice-data"
```

## 3. Configure the private PM2 service

```bash
cp ops/pm2-python-study.example.cjs ops/pm2-python-study.config.cjs
mkdir -p ops/logs
```

Edit the ignored private config and set:

- `repoRoot` to the Git checkout root.
- `persistentDataDir` to the persistent directory created above.
- `CODE_PRACTICE_PUBLIC_ORIGIN` to the final HTTPS study hostname.
- `CODE_PRACTICE_AUTH_USERNAME` to the username used by the NSY sign-in service.
- `CODE_PRACTICE_SESSION_SECRET` to the exact `DEM_SESSION_SECRET` used by the NSY sign-in service.
- `CODEX_BIN` to the local Codex executable if online Codex coaching should be available.

Never commit the private PM2 file, session secret, Codex login, Cloudflare credentials, or runtime database.

Start the service:

```bash
pm2 start ops/pm2-python-study.config.cjs
pm2 save
pm2 status nsy-python-study
curl -fsS http://127.0.0.1:8791/api/health
```

Production health should report `"mode":"authenticated-website"` and `"authEnabled":true`.

## 4. Allow the shared login to return to the study hostname

On the DEM sign-in service, add the study hostname to `DEM_ALLOWED_NEXT_HOSTS` in its private environment. Multiple extra hosts are comma-separated:

```text
DEM_ALLOWED_NEXT_HOSTS=replace-with-study-hostname.nsyprojects.com
```

Restart the DEM service after updating its environment. Its session cookie domain must remain `.nsyprojects.com` so the study hostname receives the signed `dem_session` cookie.

## 5. Add the Cloudflare Tunnel route

Add the chosen hostname before the tunnel's final catch-all rule, preserving all existing routes:

```yaml
ingress:
  - hostname: replace-with-study-hostname.nsyprojects.com
    service: http://127.0.0.1:8791
  - service: http_status:404
```

Restart the existing tunnel. Confirm an unauthenticated browser is sent to the study login page. **Admin: continue with NSY login** sends the owner to the existing NSY sign-in service; members use their study username and password.

## Updating code without losing progress

Start at the repository root, on `main`. Back up the destination runtime database first using its actual configured path (see below). If `git status --short` shows local changes, stop and resolve them without discarding private configuration or work.

```bash
git status --short
git pull --ff-only
cd "projects/Python Study App"
.venv/bin/python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
PYTHONPATH=. .venv/bin/pytest -q
pm2 restart nsy-python-study --update-env
curl -fsS http://127.0.0.1:8791/api/health
```

Because `CODE_PRACTICE_DATA_DIR` points outside the checkout and seed installation only happens when the runtime database is absent, these updates preserve online progress.

## Upgrading from the single-owner version

Use the existing persistent directory and PM2 settings. Before the first account upgrade, back up the website's existing owner database using its configured path. Pull the update, install Python dependencies, rebuild the frontend, and restart using the sequence above. Refresh open browser tabs after the update.

Startup automatically retains the original owner database and initializes the account registry beside it. No seed refresh, progress export from the laptop, or replacement of the website's database is needed. The account registry initially names the owner using `CODE_PRACTICE_AUTH_USERNAME` (or `admin` for local mode); that username then persists. Sign in through the existing NSY owner link, open **Accounts**, and create other people's accounts. Share each username and temporary password privately; users replace the temporary password at first login.

The data directory now contains:

```text
code_practice.db                          original owner progress
accounts.db                              users, password hashes, study sessions
profiles/<account-id>/code_practice.db    each member's separate progress
```

If `CODE_PRACTICE_DB` overrides the owner database location, keep that setting. The registry and member profiles always stay under `CODE_PRACTICE_DATA_DIR`. All study data stays on the deployment computer, and ordinary code updates leave it in place. Members share the catalog and judge but have separate saved code, attempts, hints, completion status, daily/review assignments, and mastery. New profiles do not copy the owner seed. Account disabling retains all progress, and password resets revoke prior study sessions.

The owner's existing shared login remains valid and can be used to set a study password from Accounts. For recovery directly on the host, set the same data-directory/database environment as PM2 and run:

```bash
.venv/bin/python -m code_practice.accounts reset-owner
```

This prompts for the new password without putting it in command history. A standalone installation without NSY authentication can use `CODE_PRACTICE_REQUIRE_LOGIN=1` after setting the owner password; keep the correct HTTPS `CODE_PRACTICE_PUBLIC_ORIGIN`. Never expose the default no-login local mode through a tunnel.

Study session cookies are host-only, HTTP-only, and Secure with an HTTPS public origin. A study account does not create a session for DEM or other NSY apps. Login attempts are limited, and account administration requires the owner role. Codex coaching uses the host owner's local credentials, so members only receive offline coaching.

## Backing up and restoring all accounts

With the service's `CODE_PRACTICE_DATA_DIR` and optional `CODE_PRACTICE_DB` exported in your shell, run `./backup_data.sh`. Once the account registry exists, the helper produces a directory containing `accounts.db`, `owner/code_practice.db`, and every `profiles/<account-id>/code_practice.db`. Existing owner-only `.db` backups cannot restore other accounts.

For a coherent whole-app transfer, stop the study service briefly before backing up, then restart it. The helper uses SQLite's backup API and refuses to overwrite an existing backup directory. Store backups privately outside the repository; they contain credentials, sessions, and private code.

To restore on another host, stop the destination service and back up any existing destination data first. Restore `accounts.db` and the complete `profiles/` directory into the configured persistent data directory. Restore `owner/code_practice.db` from the backup to the configured `CODE_PRACTICE_DB` path (normally `<data directory>/code_practice.db`). Keep the registry and all profile files from the same backup together, then restart. Copying only the owner database is not a multi-account transfer. If no runtime owner database exists, normal seed rules still apply, so restore it before starting.

## Backing up online progress

Stop writes briefly or use SQLite's online backup command:

```bash
sqlite3 "/path/to/persistent/code-practice-data/code_practice.db" ".backup '/path/to/backups/code-practice-$(date +%Y%m%d-%H%M%S).db'"
```

Alternatively, from the app folder, the helper accepts the same database location as the app:

```bash
CODE_PRACTICE_DATA_DIR="/path/to/persistent/code-practice-data" \
CODE_PRACTICE_BACKUP_DIR="/path/to/backups" ./backup_data.sh
```

Use `CODE_PRACTICE_DB="/exact/path/to/progress.db"` instead if the service has a custom filename. Supply these settings in the terminal explicitly; PM2's private environment does not export them to your shell.

Do not refresh or recommit `seed_data/initial_progress.db` after online studying begins unless deliberately performing another one-time migration. The deployment runtime database is authoritative from that point forward.

## Acceptance checklist

- [ ] Seed database passes `PRAGMA integrity_check`.
- [ ] First start copies the seed into the persistent directory.
- [ ] A later restart preserves a new online draft and attempt.
- [ ] Service listens on `127.0.0.1:8791`, never `0.0.0.0`.
- [ ] Health reports authenticated website mode.
- [ ] Unauthenticated page requests redirect to study sign-in; the NSY owner link works.
- [ ] Unauthenticated API requests return `401`.
- [ ] Authenticated study flow can run examples, submit, and persist progress.
- [ ] Git pull and PM2 restart do not replace the runtime database.
- [ ] A new member starts with empty progress, cannot manage accounts, and cannot see the owner's drafts.
- [ ] Member progress and account access survive a restart; backups include the registry and every profile.
- [ ] Runtime database backups are stored outside the Git checkout.
