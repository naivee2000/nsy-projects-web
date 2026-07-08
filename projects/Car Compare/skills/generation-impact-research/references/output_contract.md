# Car Compare Generation Impact Contract

Use this reference when deciding field meanings for `car_compare/generation_impact_schema.json`.

## Adjustment Semantics

`extra_depreciation_pct` is incremental. It is not the full projected YoY depreciation. For example, if the ordinary retention model predicts a 7% loss and generation research estimates an extra 6% shock, the app applies the normal projection first and then multiplies the predicted value by `0.94`.

## Age Semantics

`age` is years from the current Age 0 baseline shown in Car Compare. If the app run year is 2026 and a replacement generation is expected to affect resale in 2028, use `age: 2` and `calendar_year: 2028`.

## Confidence

Use `high` only when launch timing is official or strongly confirmed and the depreciation estimate has same-model historical evidence. Use `medium` when timing is credible but the impact estimate depends on sibling/segment evidence. Use `low` for uncertain timing, weak market data, or heavily judgment-based estimates.

## Blocked Result

Return `status: "blocked"` and empty `adjustments` if credible sources do not support a usable generation-change adjustment.
