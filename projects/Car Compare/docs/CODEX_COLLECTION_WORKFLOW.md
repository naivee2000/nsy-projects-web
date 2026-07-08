# Codex Website Collection Workflow

This app is intentionally not a blind crawler. Codex should collect source data through visible website pages, official APIs, or user-authorized accounts/API keys.

## Normal Browser Collection

1. Enter a vehicle query in the app, for example:

   ```text
   Bentley Continental GT Speed
   Toyota Camry XSE
   BMW M4 Competition xDrive
   ```

2. Open the generated source URLs in the app's Collection Plan.

3. Confirm the page is a used-car result page for the requested make/model.

4. Scroll the result list. If the page shows a visible control such as `See More Results`, `Show More`, `Load More`, or `Next`, click it once and verify that listing text/count/scroll height changed. Repeat only while the page clearly loads more public rows.

5. Extract visible text from the loaded page section. Include:

   - year
   - make
   - model
   - trim/version
   - price
   - mileage
   - dealer when visible
   - VIN when visible
   - source URL

6. Paste the capture into the app's Capture Import box with the source name and URL.

7. Rerun research. The app will:

   - filter by requested model and trim keywords
   - deduplicate by VIN first
   - deduplicate likely same cars by year/title/trim/price/mileage/dealer
   - calculate observed buckets and project missing ages out to the selected horizon, up to 20 years

## Source Notes

Autotrader may redirect model-specific URLs to a make-level result page. That is acceptable if the visible capture includes the requested model; the app filters imported rows by model and trim.

Edmunds direct SRP URLs work for several tested models. If one is blank, use the visible Used Cars search form and select make/model manually.

Visor is best through its API/MCP when an API key is available. Public Visor pages are useful for facets, counts, trim/version distribution, and price/mileage bands.

For exact trims, do not rely only on substring matching. Reject neighboring variants that add a distinct trim/drivetrain token the user did not ask for, such as `EX-L` for `EX`, `GT500` for `GT`, `Carrera S` for base `Carrera`, or xDrive for a non-xDrive BMW Competition query.

## Stop Conditions

Stop using a source and switch to another source or manual import if the page shows a CAPTCHA, paywall, login-only wall, or refuses to load public listings. Do not try to bypass restrictions.
