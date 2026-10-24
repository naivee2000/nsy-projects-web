# NSY Projects Website Design

This folder holds the static website design for `NSYPROJECTS.COM`.

- `index.html` is the public entry page with the top menu, About Me section, and sign-in links.
- `about.html` is the personal About Me page.
- `projects.html` is the public project directory.
- `projects/*/index.html` are stable launcher pages. Each opens its app only after a visitor activates the link.
- `tokens.css` contains shared design tokens; `base.css` provides accessibility foundations; `styles.css` contains layouts and page styles. See `design.md` for the locked design system.
- `site.js` updates the displayed account state and copyright year.
- `assets/paper-sculpture-*.webp` are responsive exports of the selected abstract artwork. See `assets/paper-sculpture.md` for the generation prompt and provenance. Superseded app screenshots and unused laptop artwork have been removed.
- `_redirects` keeps old login URLs pointed at the real backend sign-in.

DEM claim processing, real login/session code, uploads, OCR, and Excel generation stay in `../projects/dem-claim/` and are served through `https://dem.nsyprojects.com/`.

## Current UX/Auth Notes

- Public navigation uses explicit destinations, not browser-history Back controls. Home has no Back button; project launchers use fixed links such as Back to Projects.
- The top-right Sign in link sends users to `https://dem.nsyprojects.com/login` with `https://nsyprojects.com/projects` as the return URL, including when JavaScript is unavailable. The legacy `/login` and `/login.html` redirects use the same destination.
- On Home, About, and launchers, the signed-in account link opens `/projects.html`. On Projects, the signed-in account action remains Sign out. Individual project cards open their stable launcher pages.
- After successful sign-in, the backend sets `nsy_signed_in=1` for `.nsyprojects.com`; static pages use it only for display state.
- Static pages must not rely on that cookie for security. The DEM app itself enforces the real backend session before showing uploads or APIs.
- The old fake `login.html` page has been removed and `/login` plus `/login.html` redirect to the backend login.

## Deployment Notes

- Cloudflare Pages project: `nsy-projects`.
- Public site domain: `https://nsyprojects.com/`.
- DEM backend domain: `https://dem.nsyprojects.com/`.
- Car Compare backend domain: `https://carcompare.nsyprojects.com/`.
- Python Study backend domain: `https://python.nsyprojects.com/`.
- Long-Term Stock Allocation Lab domain: `https://strategy.nsyprojects.com/` (public, no login).
- DEM backend runs separately through the FastAPI app in `../projects/dem-claim/app/`.
- Car Compare runs separately through `../projects/Car Compare/app.py`; its canonical host instructions are in `../projects/Car Compare/docs/DEPLOYMENT.md`.
- Before publishing a Car Compare backend update, run its unit tests, `scripts/benchmark_search_accuracy.py`, browser-worker self-test, and deploy preflight as documented in `../projects/Car Compare/docs/PERFORMANCE_ACCURACY_BENCHMARK.md`.
- Do not put upload, OCR, workbook generation, or password checking code into this static folder.
- The Projects page should stay app-neutral: the top-right control is account state only, while each project card links to its own stable `/projects/<slug>/` entry.
- Future backend apps should use their own subdomain, such as `invoice.nsyprojects.com` or `ops.nsyprojects.com`, with Cloudflare Tunnel routing each hostname to the right local port or server.
- Static-only future projects can stay under `nsyprojects.com/projects/<slug>/` or deploy as separate Cloudflare Pages routes.
- The static Car Compare project page is only a stable launcher. Do not move collection, shared-session validation, Codex, browser automation, or cache logic into `web_ui/`.

## Design and font decisions

- The warm editorial system retains ivory, forest green, Georgia headings and system-sans body text; no external font requests.
- The 1120px public container uses 24px gutters above 768px and 16px below. The Home hero uses 5:7 columns above 800px; smaller layouts stack copy before the abstract artwork.
- Home retains the original wording and links to the Projects directory, without listing projects or exposing app interfaces. About preserves the original prose in background, experience, interests and personal sections.
- Projects and the four launchers keep their destinations and structure, with compatible shared styling.
- Login matches the public header, navigation, footer, ivory palette and Georgia display scale. Its English form is self-contained, with native required fields, visible focus and announced errors. Authentication and return/cancel policies are unchanged.
- See [the portable handoff guide](../docs/redesign/README.md) for verification, current screenshots, local preview commands and separate deployment steps.

## Current Verified Flow

Verified on 2026-06-17 with real Google Chrome:

- `nsyprojects.com` public navigation loads without generic Back buttons.
- `Sign in` opens the backend login page.
- Login returns users to the requested page or app.
- DEM app tasks can produce Excel downloads through both deterministic OCR and Codex fallback.
