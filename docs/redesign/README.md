# Website redesign handoff

Prepared 2026-10-23 for transfer through GitHub. The owner requested merging the tested redesign into **main** and will deploy it from the other computer. No production service was restarted or deployed from this checkout.

Repository: `naivee2000/nsy-projects-web`, branch: `main`. The original handoff branch is retained as `codex/website-redesign-handoff`.

## Final design

- **Home:** original “Project Lab” wording and introduction, ivory/green paper sculpture, Explore Projects and About Me. No app screenshots or individual project list.
- **About:** original biography prose with clearer sections and responsive spacing.
- **Sign-in:** the real `LOGIN_HTML` in `projects/dem-claim/app/auth_gate.py`, with the same public header, navigation, footer, Georgia heading, ivory background and forest-green controls. English labels, keyboard focus and accessible errors. Native POST, escaping, safe return/Cancel rules, password checking, sessions and cookies are preserved.
- **Projects and launchers:** existing content, routes and destination links, with compatible shared styling.

## Continue on the other computer

If the other computer is already on `main`, update it with:

```sh
git pull --ff-only
```

If it is on the earlier handoff branch, switch first (preserve any local edits):

```sh
git switch main
git pull --ff-only
```

For a new checkout:

```sh
git clone https://github.com/naivee2000/nsy-projects-web.git
cd nsy-projects-web
```

Everything needed for this design is committed: HTML/CSS, optimized artwork, original artwork source, screenshots, the real login template, focused tests, and a local preview runner. Hallmark, image-generation access, Node/browser-audit packages and this computer's temporary files are **not** required to use or continue the implementation.

## Preview without deploying

From the repository root, serve the public site:

```sh
python3 -m http.server 8785 --bind 127.0.0.1 --directory web_ui
```

Open `http://127.0.0.1:8785/`.

In another terminal, use the existing DEM virtualenv, or create one if absent:

```sh
python3 -m venv projects/dem-claim/app/.venv
projects/dem-claim/app/.venv/bin/python -m pip install -r projects/dem-claim/app/requirements.txt
projects/dem-claim/app/.venv/bin/python projects/dem-claim/app/preview_login.py
```

Open `http://127.0.0.1:8788/login`. Use disposable credentials **preview / preview-only** to verify success and logout; any incorrect password shows the real error state. The preview binds only to loopback, generates an in-memory secret, uses separate preview cookie names, creates no data files and does not load the DEM processing app or deployment configuration. Stop each preview with Ctrl+C. It is not a production entrypoint.

The static Home page deliberately retains the real `https://dem.nsyprojects.com/login` destination. Clicking Sign in there opens the existing live version. Open the local login URL directly when reviewing these changes. Cancel and public navigation also retain their real public destinations. Python's static server does not interpret Cloudflare `_redirects`.

## Verification

```sh
projects/dem-claim/app/.venv/bin/python -m unittest discover -s projects/dem-claim/app -p 'test_auth_gate.py' -v
git diff --check
```

Verified before handoff:

- A clean export of the committed files passed all five auth tests, local HTTP checks for all seven public pages and their CSS/artwork, and preview-runner invalid/successful login, cookie and logout checks. Public HTML references and handoff Markdown links resolve without this computer’s audit files. The installed DEM virtualenv supplied the dependencies listed in `requirements.txt`.

- Five auth regressions pass: native accessible form; escaped/focused errors; return-value escaping; return/Cancel policy; login/logout endpoint redirects and cookies with synthetic credentials.
- Final Home/About render checks: zero failures or warnings, with documented compact-layout exceptions. Final normal/error sign-in checks: zero failures, Reflex findings or warnings.
- Desktop and mobile captures inspected; responsive checks included narrow mobile, tablet, 1280×800 and wide desktop layouts.
- All 12 shared login palette/font/container/display-size values match the public tokens.
- Original Home heading and paragraphs preserved. Native form works without JavaScript; public navigation is usable without JavaScript.
- Existing Projects/launcher URLs, `site.js`, `_redirects` and auth contracts remain intact.

### Current screenshots

| Page | Desktop | Mobile |
| --- | --- | --- |
| Home | [View](screenshots/home-desktop.webp) | [View](screenshots/home-mobile.webp) |
| About | [View](screenshots/about-desktop.webp) | [View](screenshots/about-mobile.webp) |
| Sign-in | [View](screenshots/signin-desktop.webp) | [View](screenshots/signin-mobile.webp) |

[Sign-in error state](screenshots/signin-error-mobile.webp)

## Files and cleanup

- Shared design system: [web_ui/design.md](../../web_ui/design.md).
- Public implementation: `web_ui/index.html`, `about.html`, `styles.css`, `tokens.css`, `base.css`.
- Artwork exports and prompt: [paper-sculpture.md](../../web_ui/assets/paper-sculpture.md).
- Editable full-resolution artwork master: [source/paper-sculpture.png](source/paper-sculpture.png).
- Backend template/test/preview: `projects/dem-claim/app/{auth_gate,test_auth_gate,preview_login}.py`.

Removed the obsolete laptop hero assets, abandoned app screenshot assets, duplicate Hallmark captures/logs, and loose `output/` folder. Kept only the selected artwork source and current portable screenshots. Historical tracked assets remain recoverable from Git. Existing runtime environments, project data, uploads, caches, credentials and unrelated projects were not cleaned or transferred.

## Deployment boundary

The handoff and main-workflow commits use `[CF-Pages-Skip]` and `[skip ci]` in their messages to suppress automatic deployment. See [Cloudflare's skip-deployment documentation](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/). Preserve those markers for transfer-only pushes. The owner will perform the actual release from the designated deployment computer.

On the designated deployment computer, when ready to replace the old version:

1. Public frontend: deploy **only `web_ui`**, including both paper-sculpture WebP exports and all three CSS files, through the existing Cloudflare Pages `nsy-projects` workflow. Do not deploy the repository root, `docs`, environments, data or secrets.
2. Sign-in backend: use the existing [DEM deployment procedure](../../projects/dem-claim/docs/DEPLOYMENT.md). The real secure entrypoint remains `app_zh_secure:app`; restart only `nsy-dem-app` after release. Do not deploy `preview_login.py` as the service or use its disposable credentials.
3. No migration, new runtime dependency or new production secret is required by this redesign. Keep the other computer's existing credentials, cookies configuration and persistent runtime data.
4. Verify public pages and the live login success/error/return/logout flow. Frontend and backend are separate releases. Roll back their corresponding code revisions independently if necessary.
