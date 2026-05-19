-- Campaigns with strong modeled upside and a clear optimization driver.
select
  campaign_id,
  client_segment,
  primary_channel,
  opportunity_score,
  estimated_missing_opportunity,
  primary_driver,
  confidence
from analysis_outputs.campaign_opportunity_queue
where opportunity_score >= 75
order by opportunity_score desc;

-- Contextual bid segments where value is high but win rate is still under-captured.
select
  campaign_id,
  app_context,
  device_tier,
  supply_path,
  predicted_value_index,
  win_rate_gap,
  recommended_bid_change,
  estimated_opportunity
from analysis_outputs.contextual_signal_scores
where predicted_value_index >= 75
  and win_rate_gap >= 0.15
order by estimated_opportunity desc;

-- Creative concepts that need rotation before fatigue erodes conversion quality.
select
  campaign_id,
  concept,
  format,
  fatigue_score,
  conversion_index,
  learning_tag
from analysis_outputs.creative_learning_matrix
where fatigue_score >= 0.55
order by fatigue_score desc, conversion_index asc;

-- Measurement issues that should be resolved before client reporting.
select
  campaign_id,
  issue_type,
  affected_spend,
  severity_score,
  owner,
  status
from analysis_outputs.measurement_qa_queue
where severity_score >= 35
order by severity_score desc;
