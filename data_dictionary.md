# Data Dictionary

## `data/campaigns.csv`

- `campaign_id`: Synthetic campaign identifier.
- `client_segment`: Fictional advertiser portfolio label.
- `vertical`: Mobile advertiser category.
- `primary_channel`: Main activation channel.
- `geo_cluster`: Regional planning cluster.
- `objective`: Primary optimization objective.
- `budget`: Campaign budget in dollars.
- `target_cpi`: Target cost per install.
- `target_roas`: Target return on ad spend.
- `launch_date`: Synthetic launch date.
- `account_owner`: Internal owner group.

## `data/daily_campaign_metrics.csv`

- `date`: Campaign metric date.
- `campaign_id`: Campaign identifier.
- `spend`: Daily spend.
- `impressions`: Won impressions.
- `bid_requests`: Modeled bid requests.
- `win_rate`: Impressions divided by bid requests.
- `installs`: Attributed installs.
- `retained_users`: Modeled D7 retained users.
- `attributed_revenue`: Attributed revenue.
- `cpi`: Spend divided by installs.
- `roas`: Revenue divided by spend.
- `d7_retention`: Retained users divided by installs.
- `pacing_index`: Actual spend pace compared with expected daily pace.
- `contextual_fit`: Fit between audience objective and app context.
- `signal_coverage`: Share of bid and attribution signals available for analysis.
- `creative_fatigue`: Modeled fatigue from creative age and performance decay.
- `measurement_reliability`: Modeled reliability of attribution and taxonomy signals.
- `predicted_value_index`: Explainable value score from contextual, creative, and retention signals.

## `data/contextual_bid_signals.csv`

- `signal_id`: Synthetic signal row identifier.
- `campaign_id`: Campaign identifier.
- `app_context`: Aggregated app or content context.
- `device_tier`: Device segment.
- `supply_path`: Supply source grouping.
- `bid_density`: Modeled available bid volume.
- `contextual_fit`: Fit between context and objective.
- `supply_quality`: Quality score for supply path.
- `win_rate_gap`: Under-captured win-rate opportunity.
- `predicted_ltv`: Modeled long-term value in dollars.
- `predicted_value_index`: Value score for the segment.
- `recommended_bid_change`: Suggested proportional bid movement.
- `estimated_opportunity`: Estimated upside in dollars.

## `data/creative_variants.csv`

- `creative_id`: Creative row identifier.
- `campaign_id`: Campaign identifier.
- `concept`: Creative concept family.
- `format`: Creative format.
- `spend_share`: Share of campaign spend.
- `thumbstop_rate`: Modeled attention rate.
- `conversion_index`: Conversion quality index.
- `fatigue_score`: Modeled creative fatigue.
- `learning_tag`: Recommended learning action.

## `data/measurement_qa_checks.csv`

- `qa_id`: QA row identifier.
- `campaign_id`: Campaign identifier.
- `issue_type`: Measurement or data quality issue.
- `issue_rate`: Modeled issue rate.
- `affected_spend`: Spend exposed to the issue.
- `severity_score`: QA priority score.
- `owner`: Internal owner.
- `status`: Workflow status.
