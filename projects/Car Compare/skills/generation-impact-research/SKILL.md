---
name: generation-impact-research
description: Research vehicle generation timing and estimate the extra depreciation shock when a replacement generation launches. Use when Car Compare or the user asks Codex to forecast how a new generation, redesign, facelift, successor model, platform change, EV replacement, or discontinued generation may affect a researched car's future depreciation.
---

# Generation Impact Research

## Goal

Produce a sourced JSON result that Car Compare can apply as a visible forecast adjustment. Keep observed market prices factual; estimate only extra future depreciation caused by a generation-change event.

## Workflow

1. Identify the requested vehicle, including make, model, trim, body style, drivetrain, and current model year context when available.
2. Research the current generation:
   - generation/platform code or common generation name
   - start model year
   - expected or confirmed end model year
   - whether the requested trim is part of that generation
3. Research next-generation timing:
   - official manufacturer statements first
   - reputable automotive news or release calendars next
   - forum speculation only as weak supporting evidence, never as the sole basis for a high-confidence result
4. Estimate extra depreciation from prior generation transitions:
   - Prefer the same model's previous transition.
   - If same-model evidence is sparse, use close siblings from the same brand/platform/segment.
   - Compare outgoing-generation prices shortly before and shortly after the replacement launch, controlling for normal age depreciation when possible.
   - Estimate the incremental shock, not the whole YoY depreciation.
5. Return age-based adjustments:
   - `age` is years from the app's current Age 0 baseline.
   - `calendar_year` is the year when the extra shock is expected to affect resale values.
   - `extra_depreciation_pct` is the incremental drop to apply on top of normal depreciation.

## Estimation Rules

- Use a low-confidence result if launch timing is uncertain.
- Use `status: "blocked"` when there is no credible source for either timing or impact.
- Keep `extra_depreciation_pct` between `0.02` and `0.12` for most cars unless strong evidence supports more.
- Typical priors when history is weak:
  - mainstream high-volume car: `0.03` to `0.07`
  - luxury car: `0.05` to `0.10`
  - performance/luxury performance car: `0.06` to `0.12`
  - tech-heavy EV: `0.08` to `0.15`
  - collector/limited enthusiast car: `0.00` to `0.05`, and explain if no negative shock is expected
- Add a smaller follow-on adjustment one year later only when historical evidence suggests a second repricing wave.
- Never imply precision that the evidence does not support; round percentages to 1 decimal percentage point when reasoning, and output decimals such as `0.06`.

## Sources

Use source records for every important claim:

- official manufacturer pages, press releases, order guides, configurators
- reputable automotive publications
- auction/used-market analyses
- indexed listings, pricing guides, or aggregate market pages

Do not bypass CAPTCHAs, login walls, paywalls, or site restrictions.

## Output

Return only JSON matching `car_compare/generation_impact_schema.json`.

When field semantics are unclear, read `references/output_contract.md`. Before saving or returning hand-written JSON, you may run `scripts/normalize_generation_impact.py <file>` to normalize adjustment ages and percentages.

If no credible adjustment is found, return `status: "blocked"` with empty `adjustments`, source notes, and a clear explanation in `notes`.

For a usable result, include at least one adjustment:

```json
{
  "age": 2,
  "calendar_year": 2028,
  "extra_depreciation_pct": 0.06,
  "label": "New generation launch shock",
  "basis": "Prior same-model transition showed an estimated 5-8% extra outgoing-generation repricing."
}
```
