# Analysis Plan

## Objective

Identify where a mobile programmatic campaign portfolio has the most actionable missing opportunity and convert that analysis into client-ready recommendations.

## Steps

1. Generate synthetic campaign, daily delivery, contextual signal, creative, QA, and recommendation datasets.
2. Aggregate daily delivery into campaign-level ROAS, CPI, retention, pacing, and win-rate metrics.
3. Score contextual segments using predicted LTV, contextual fit, supply quality, win-rate gap, and bid-density assumptions.
4. Score creative and measurement constraints from fatigue, conversion index, affected spend, and QA severity.
5. Calculate campaign opportunity score from ROAS gap, CPI gap, pacing gap, win-rate gap, creative fatigue, QA severity, and contextual value.
6. Write ranked outputs for the browser workbench and SQL-style analysis checks.

## Decision Outputs

- Campaigns to escalate in the next optimization review.
- Contextual app and supply-path segments to bid up, cap, or validate.
- Creative concepts to rotate, retest, or hold out.
- QA issues that need Engineering, Data Science, Analytics, or Client Strategy ownership.
