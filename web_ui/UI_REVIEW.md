# NSY Projects UI Review

Last updated: 2026-06-17

## Ten Issues Fixed

1. Public pages used browser-history Back controls, which could send users away from the site. Removed generic Back from Home, About, and Projects; site navigation now uses explicit destinations.
2. Home Sign in used a fixed return target. It now sends the current URL as `next`, so users return to the page where they started.
3. About had no sign-in state. It now shows Sign in or Signed in consistently with Home and Projects.
4. Projects showed a protected project status that did not react after login. It now changes from Login required to Available when the shared display cookie is present.
5. About content was a placeholder. Replaced it with usable background, focus, and projects copy.
6. The Home hero lead used `white-space: nowrap`, which could overflow on narrower screens. Removed that forced no-wrap behavior.
7. The DEM redirect page jumped immediately with little context. It now shows a short transition page with Back to Projects and direct app links.
8. The backend login page looked DEM-specific. It now uses generic NSY Projects sign-in title and heading.
9. The backend login page had no clear cancel path. It now has Cancel and NSY Projects controls, with Cancel using the safe `next` destination when appropriate.
10. The DEM app page had no way back to the website or to log out. The Chinese app shell now includes fixed links to the project list, home page, and logout.

## Remaining Product Note

The current shared `nsy_signed_in` cookie is only for static-page display state. Real access control still happens in the DEM backend session. A future multi-project account system should move this into a central backend auth service.

## 2026-06-17 Verification Update

- Real Google Chrome was used to test `https://dem.nsyprojects.com/`.
- Login, app shell navigation, OCR-only Excel generation, Codex fallback Excel generation, and download links all worked after the backend stdin fix.
- OCR-only test used `Load1.png` plus `Discharge1.png`.
- Codex fallback test used `Load3.png` plus `Discharge3.png`.
- Backend uploads and generated workbooks now expire after 24 hours by default; the UI delete action removes the job folder immediately.
