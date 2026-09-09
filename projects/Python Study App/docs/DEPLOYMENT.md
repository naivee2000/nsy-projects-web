# Code Practice Lab Private Website Deployment

This deployment keeps the FastAPI service and SQLite progress on the always-on website Mac. GitHub carries one initial progress snapshot; after first start, the deployment Mac's persistent database becomes the only live copy.

## Production shape

```text
authenticated browser
→ private study hostname
→ Cloudflare Tunnel
→ http://127.0.0.1:8791
→ PM2: FastAPI + compiled React frontend
→ persistent SQLite database on the deployment Mac
```

The service must remain bound to `127.0.0.1`. The Cloudflare route is the only public route, and the existing NSY sign-in session protects the page, saved drafts, attempt source code, visible submission packages, and progress APIs.

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

## 1. Refresh the seed before the first push

On the current study Mac:

```bash
cd "projects/Python Study App"
./scripts/refresh_progress_seed.sh
sqlite3 seed_data/initial_progress.db "PRAGMA integrity_check;"
```

Commit the seed only to the private repository. It contains personal draft and attempt source code.

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

Restart the existing tunnel. Confirm an unauthenticated browser is sent to the NSY sign-in page and an authenticated browser can open the study app.

## Updating code without losing progress

```bash
git pull --ff-only
cd "projects/Python Study App"
.venv/bin/python -m pip install -r requirements.txt
npm --prefix frontend install
npm --prefix frontend run build
PYTHONPATH=. .venv/bin/pytest -q
pm2 restart nsy-python-study --update-env
curl -fsS http://127.0.0.1:8791/api/health
```

Because `CODE_PRACTICE_DATA_DIR` points outside the checkout and seed installation only happens when the runtime database is absent, these updates preserve online progress.

## Backing up online progress

Stop writes briefly or use SQLite's online backup command:

```bash
sqlite3 "/path/to/persistent/code-practice-data/code_practice.db" ".backup '/path/to/backups/code-practice-$(date +%Y%m%d-%H%M%S).db'"
```

Do not refresh or recommit `seed_data/initial_progress.db` after online studying begins unless deliberately performing another one-time migration. The deployment runtime database is authoritative from that point forward.

## Acceptance checklist

- [ ] Seed database passes `PRAGMA integrity_check`.
- [ ] First start copies the seed into the persistent directory.
- [ ] A later restart preserves a new online draft and attempt.
- [ ] Service listens on `127.0.0.1:8791`, never `0.0.0.0`.
- [ ] Health reports authenticated website mode.
- [ ] Unauthenticated page requests redirect to NSY sign-in.
- [ ] Unauthenticated API requests return `401`.
- [ ] Authenticated study flow can run examples, submit, and persist progress.
- [ ] Git pull and PM2 restart do not replace the runtime database.
- [ ] Runtime database backups are stored outside the Git checkout.
