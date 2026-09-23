# NSY Projects Website Design

This folder holds the static website design for `NSYPROJECTS.COM`.

- `index.html` is the public entry page with the top menu, About Me section, and sign-in links.
- `about.html` is the personal About Me page.
- `projects.html` is the public project directory.
- `projects/*/index.html` are stable launcher pages. Each opens its app only after a visitor activates the link.
- `styles.css` contains the site's shared palette, type scale, spacing scale, and page styles.
- `site.js` updates the displayed account state and copyright year.
- `assets/hero-projects-*.avif` and `assets/hero-projects-*.webp` are the served responsive hero images. The original `hero-projects.png` remains as an unserved source asset.
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

- The warm editorial design uses one stylesheet, one 1120px maximum container, nine color tokens, seven type tokens (12/14/16/20/28/44/64px), and eight spacing tokens (4/8/12/16/24/32/48/80px).
- Major headings use the system serif stack Georgia, Times New Roman, Songti SC, SimSun, serif. Body text, navigation, project titles, and controls use the platform system sans-serif stack. No web fonts are requested.
- The responsive container subtracts two token-based gutters: 24px each at widths of 768px and above, 16px each below 768px. All authored margin, padding, and gap values use spacing tokens, zero, or auto.
- At widths of 800px and above, the home introduction splits its available width 3:2 with a 48px gap. The image frame is 4:3. Below 800px, the image follows the copy. The shared AVIF preload and picture sizes describe the image frame: 429px at the maximum container, 40vw minus 38.4px between 800px and 1167px, and the available container width on smaller screens. The 38.4px offset is 40% of the two 24px gutters plus the 48px column gap; it is an image sizing calculation, not an extra spacing token.
- The existing two AVIF and two WebP hero variants remain served; the source PNG is retained but not requested.
- The project directory is one list with horizontal rules. Desktop rows put title/status beside description/tags; below 800px those groups stack. Every row is one anchor to its stable launcher.
- All seven pages share navigation, the skip link, footer, and account display. Launchers retain their existing app destinations and wait for explicit user activation. This refresh does not change application UI or authentication.
- Hover feedback changes colors only. Keyboard focus has a visible three-pixel outline. Reduced-motion preferences disable color transitions.

## Current Verified Flow

Verified on 2026-06-17 with real Google Chrome:

- `nsyprojects.com` public navigation loads without generic Back buttons.
- `Sign in` opens the backend login page.
- Login returns users to the requested page or app.
- DEM app tasks can produce Excel downloads through both deterministic OCR and Codex fallback.
