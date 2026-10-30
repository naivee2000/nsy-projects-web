---
name: collect-car-marketplaces
description: Manually repair or supplement a finished Car Compare collection job through Codex and the connected Chrome profile when the automatic host-Chrome worker is unavailable. Use when the app exposes an unexpired manual fallback lease, when the user asks Codex to flip marketplace pages, or when a supervised Chrome-visible capture is explicitly required.
---

# Collect Car Marketplaces

Car Compare normally uses its background browser worker and then its project-local host-Chrome fallback. Indexed web search is discovery-only: snippets cannot supply verified prices or national inventory counts. Its browser sources are Autotrader, Edmunds, and Porsche Finder for Porsche queries. Use this supervised skill only for an unexpired lease that remains after automatic paths were unavailable or failed. Use `@Chrome` for website access. Do not launch an independent `codex exec` to claim this task's Chrome connection.

If Chrome is not connected, stop and tell the operator to open Chrome and confirm that the ChatGPT extension says `Connected`. Do not silently switch to the built-in Browser.

## Workflow

1. Choose the Car Compare base URL:
   - Default to `http://127.0.0.1:8787` for the local app.
   - Use the user's deployed URL when they explicitly identify that run and its authenticated session is available in Browser.
2. Open `<base>/api/codex-browser-actions`. It returns only unexpired temporary leases. Select the job ID named in the task; when a comparison task names two IDs, repair both. Do not process unrelated jobs.
3. For each listed source, open its exact target URL in the task's Chrome tab group.
4. Match every field in the action's `requestedScope`: make/model, trim, years, condition, body and drivetrain, plus nationwide distance. An unspecified field must not have an extra active restriction. Apply changed controls and wait for refreshed results; the URL, page title, and available filter options alone are not proof. A Carrera S request must not broaden to the whole Carrera family.
   - On Porsche Finder, confirm the Location filter says `Nationwide`; the URL position radius must end in `,-1`.
   - For 911 Carrera searches, preserve the generated category filters. Carrera family includes configured Carrera descendants, Base includes only Carrera coupe/cabriolet, and an unqualified 911 includes all 911 trims.
5. Expand the public result list:
   - Scroll through the result page.
   - Click a visible `See More Results`, `Show More Results`, `Load More`, or next-page control when present.
   - After every click, verify that the visible card count, result text, URL, or page height changed.
   - Stop after three expansion clicks, source exhaustion, or enough visible coverage for the task.
6. Read the visible rendered text from the identified result page. Preserve it verbatim; do not rewrite listing titles, prices, mileages, VINs, or trims. Limit a single capture to 250,000 characters.
7. Open `<base>/codex-action?jobId=<job-id>&source=<source>` in another Chrome tab in the same task group.
8. Fill the source URL, verbatim visible result text, pages examined, visible cards examined, and expansion-click count. Check the scope confirmation only after completing step 4, then submit `Import verified capture`. If nationwide selection cannot be verified, leave it unchecked and report the source as unverified.
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
- Imports use validation revision 3 and retain the capture time within the active lease. The UI submits `requested_scope`, `result_refresh_confirmed`, and `verification_method: supervised_visible_controls` with the query key. A checkbox is a supervised attestation, not machine verification of the website.
- Automatic work shares one 12-minute deadline, five initial pages per source, four two-page targeted searches per job, and two active operations per source on a host. A later manual repair is a separate, explicit lease, not a way to extend an automatic job indefinitely. Do not create a recurring monitor.
