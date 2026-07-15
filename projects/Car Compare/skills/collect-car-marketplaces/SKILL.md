---
name: collect-car-marketplaces
description: Manually repair or supplement a finished Car Compare collection job through Codex and the connected Chrome profile when the automatic host-Chrome worker is unavailable. Use when the app exposes an unexpired manual fallback lease, when the user asks Codex to flip marketplace pages, or when a supervised Chrome-visible capture is explicitly required.
---

# Collect Car Marketplaces

Car Compare normally performs this work automatically through its project-local AppleScript host-Chrome worker, followed when necessary by a schema-constrained native Codex web-search pass over official indexed pages. Its audited browser sources are Autotrader, Edmunds, and Porsche Finder for Porsche queries. Use this supervised skill only for an unexpired lease that remains after those automatic paths were unavailable or failed. Use `@Chrome` and the connected ChatGPT Chrome extension for website access. Do not launch a background `codex exec`: an independent CLI process cannot claim the desktop task's Chrome connection.

If Chrome is not connected, stop and tell the operator to open Chrome and confirm that the ChatGPT extension says `Connected`. Do not silently switch to the built-in Browser.

## Workflow

1. Choose the Car Compare base URL:
   - Default to `http://127.0.0.1:8787` for the local app.
   - Use the user's deployed URL when they explicitly identify that run and its authenticated session is available in Browser.
2. Open `<base>/api/codex-browser-actions`. It returns only unexpired temporary leases. Select the job ID named in the task; when a comparison task names two IDs, repair both. Do not process unrelated jobs.
3. For each listed source, open its exact target URL in the task's Chrome tab group.
4. Confirm the page visibly matches the requested make/model before extracting anything.
   - On Porsche Finder, confirm the Location filter says `Nationwide`; the URL position radius must end in `,-1`.
   - For 911 Carrera searches, preserve the generated category filters. Carrera family includes configured Carrera descendants, Base includes only Carrera coupe/cabriolet, and an unqualified 911 includes all 911 trims.
5. Expand the public result list:
   - Scroll through the result page.
   - Click a visible `See More Results`, `Show More Results`, `Load More`, or next-page control when present.
   - After every click, verify that the visible card count, result text, URL, or page height changed.
   - Stop after three expansion clicks, source exhaustion, or enough visible coverage for the task.
6. Read the visible rendered text from the identified result page. Preserve it verbatim; do not rewrite listing titles, prices, mileages, VINs, or trims. Limit a single capture to 250,000 characters.
7. Open `<base>/codex-action?jobId=<job-id>&source=<source>` in another Chrome tab in the same task group.
8. Fill the source URL, verbatim visible result text, pages examined, visible cards examined, and expansion-click count. Submit `Import verified capture`.
9. Verify the page reports accepted exact rows. Repeat for the other source while the lease remains active.
10. Reopen `<base>/api/codex-browser-actions`. Stop as soon as the named job IDs are absent; the app closes a lease after all blocked sources are repaired and its active report monitor refreshes automatically.

## Rules

- Stop on a CAPTCHA, login wall, paywall, security interstitial, or access refusal. Never bypass or rotate identities/profiles.
- Use only public visible listing content. Do not inspect cookies, local storage, hidden application state, or private account data.
- Do not hand-author structured listing rows. The import endpoint runs Car Compare's deterministic parser and trim rules.
- Include Competition xDrive and convertible variants when the resolved query permits them. Preserve Base, CS, CSL, GTS, and historical ZCP distinctions; the app remains authoritative for acceptance.
- Treat a zero-row import as a diagnostic result, not permission to loosen matching rules.
- If the import reports that the temporary lease expired, stop. Never create a recurring task or keep polling; the operator can start a new Car Compare collection.
- Report accepted rows per source and any remaining blocked source clearly.
