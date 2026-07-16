# NSY Projects Website Design

This folder holds the static website design for `NSYPROJECTS.COM`.

- `index.html` is the public entry page with the top menu, About Me section, and sign-in links.
- `about.html` is the personal About Me page.
- `projects.html` is the public project directory.
- `projects/dem-claim/index.html` is the stable NSY project URL and redirects to the live DEM claim workflow.
- `projects/car-compare/index.html` is the stable NSY project URL and redirects to the authenticated Car Compare app.
- `assets/hero-projects.png` is an original generated hero background for this site.
- `_redirects` keeps old login URLs pointed at the real backend sign-in.

DEM claim processing, real login/session code, uploads, OCR, and Excel generation stay in `../projects/dem-claim/` and are served through `https://dem.nsyprojects.com/`.

## Current UX/Auth Notes

- Public navigation uses explicit destinations, not browser-history Back controls. Home has no Back button; project detail pages use fixed links such as Back to Projects.
- The top-right Sign in link sends users to `https://dem.nsyprojects.com/login` with a return URL for the current page.
- After successful sign-in, the backend sets `nsy_signed_in=1` for `.nsyprojects.com`; static pages use it only for display state.
- Static pages must not rely on that cookie for security. The DEM app itself enforces the real backend session before showing uploads or APIs.
- The old fake `login.html` page has been removed and `/login` plus `/login.html` redirect to the backend login.

## Deployment Notes

- Cloudflare Pages project: `nsy-projects`.
- Public site domain: `https://nsyprojects.com/`.
- DEM backend domain: `https://dem.nsyprojects.com/`.
- Car Compare backend domain: `https://carcompare.nsyprojects.com/`.
- DEM backend runs separately through the FastAPI app in `../projects/dem-claim/app/`.
- Car Compare runs separately through `../projects/Car Compare/app.py`; its canonical host instructions are in `../projects/Car Compare/docs/DEPLOYMENT.md`.
- Before publishing a Car Compare backend update, run its unit tests, `scripts/benchmark_search_accuracy.py`, browser-worker self-test, and deploy preflight as documented in `../projects/Car Compare/docs/PERFORMANCE_ACCURACY_BENCHMARK.md`.
- Do not put upload, OCR, workbook generation, or password checking code into this static folder.
- The Projects page should stay app-neutral: the top-right control is account state only, while each project card links to its own stable `/projects/<slug>/` entry.
- Future backend apps should use their own subdomain, such as `invoice.nsyprojects.com` or `ops.nsyprojects.com`, with Cloudflare Tunnel routing each hostname to the right local port or server.
- Static-only future projects can stay under `nsyprojects.com/projects/<slug>/` or deploy as separate Cloudflare Pages routes.
- The static Car Compare project page is only a stable redirect. Do not move collection, shared-session validation, Codex, browser automation, or cache logic into `web_ui/`.

## Current Verified Flow

Verified on 2026-06-17 with real Google Chrome:

- `nsyprojects.com` public navigation loads without generic Back buttons.
- `Sign in` opens the backend login page.
- Login returns users to the requested page or app.
- DEM app tasks can produce Excel downloads through both deterministic OCR and Codex fallback.
