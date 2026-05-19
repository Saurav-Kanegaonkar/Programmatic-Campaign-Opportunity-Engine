import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "analysis" / "outputs"
SEED = 20260519


def clamp(value, low, high):
    return max(low, min(high, value))


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def weighted_choice(rng, items):
    total = sum(weight for _, weight in items)
    pick = rng.uniform(0, total)
    current = 0
    for item, weight in items:
        current += weight
        if pick <= current:
            return item
    return items[-1][0]


def p_value_from_lift(lift_pct, sample_units):
    z_score = abs(lift_pct) / max(1.8, 18 / math.sqrt(max(sample_units, 1)))
    return round(clamp(math.exp(-z_score), 0.001, 0.45), 3)


def main():
    rng = random.Random(SEED)
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    verticals = [
        ("Mobile games", 1.22),
        ("Fintech app", 1.05),
        ("Subscription wellness", 0.96),
        ("Travel booking", 1.08),
        ("Food delivery", 1.12),
        ("Retail marketplace", 1.01),
    ]
    channels = ["Mobile UA", "Retargeting", "CTV assist", "Influencer assist"]
    geos = ["US tier 1", "EMEA growth", "APAC growth", "LATAM test"]
    objectives = ["D7 retention", "ROAS", "paid installs", "reactivation", "LTV"]
    creative_concepts = ["social proof", "progression reward", "limited offer", "problem solution", "creator testimonial"]
    app_contexts = ["puzzle games", "finance content", "fitness apps", "travel planning", "food utility", "shopping apps"]

    campaigns = []
    start = date(2026, 2, 2)
    for idx in range(1, 19):
        vertical, vertical_factor = rng.choice(verticals)
        channel = weighted_choice(rng, [("Mobile UA", 5), ("Retargeting", 3), ("CTV assist", 2), ("Influencer assist", 1)])
        budget = rng.randrange(65000, 520000, 5000)
        target_cpi = round(rng.uniform(2.15, 8.75) / vertical_factor, 2)
        target_roas = round(rng.uniform(1.05, 1.85) * vertical_factor, 2)
        campaign = {
            "campaign_id": f"CMP{idx:03d}",
            "client_segment": f"Advertiser portfolio {idx:02d}",
            "vertical": vertical,
            "primary_channel": channel,
            "geo_cluster": rng.choice(geos),
            "objective": rng.choice(objectives),
            "budget": budget,
            "target_cpi": target_cpi,
            "target_roas": target_roas,
            "launch_date": (start + timedelta(days=rng.randrange(0, 18))).isoformat(),
            "account_owner": rng.choice(["Growth analytics", "Client strategy", "Optimization pod"]),
        }
        campaigns.append(campaign)

    daily_rows = []
    signal_rows = []
    creative_rows = []
    qa_rows = []
    recommendation_rows = []
    campaign_rollups = {}

    for campaign in campaigns:
        campaign_id = campaign["campaign_id"]
        budget = int(campaign["budget"])
        vertical_factor = dict(verticals)[campaign["vertical"]]
        objective_factor = 1.10 if campaign["objective"] in {"D7 retention", "LTV", "ROAS"} else 0.94
        channel_factor = {
            "Mobile UA": 1.00,
            "Retargeting": 1.16,
            "CTV assist": 0.88,
            "Influencer assist": 0.82,
        }[campaign["primary_channel"]]
        base_fit = rng.uniform(0.48, 0.88)
        base_win_rate = rng.uniform(0.18, 0.43)
        base_retention = rng.uniform(0.16, 0.39) * vertical_factor
        target_cpi = float(campaign["target_cpi"])
        target_roas = float(campaign["target_roas"])
        spend_total = 0
        sales_total = 0
        installs_total = 0
        impressions_total = 0
        roas_values = []
        cpi_values = []
        retention_values = []
        pacing_values = []
        win_values = []

        for day_offset in range(70):
            current_date = date.fromisoformat(campaign["launch_date"]) + timedelta(days=day_offset)
            seasonality = 1 + 0.13 * math.sin(day_offset / 8) + rng.uniform(-0.07, 0.07)
            pacing = clamp(rng.gauss(0.92, 0.16) * seasonality, 0.45, 1.28)
            spend = int((budget / 70) * pacing)
            impressions = int(spend * rng.uniform(285, 740) * channel_factor)
            win_rate = clamp(base_win_rate + rng.uniform(-0.07, 0.08), 0.07, 0.58)
            contextual_fit = clamp(base_fit + rng.uniform(-0.12, 0.13), 0.22, 0.96)
            creative_fatigue = clamp(day_offset / 100 + rng.uniform(0.02, 0.28), 0.04, 0.93)
            signal_coverage = clamp(rng.gauss(0.82, 0.13), 0.42, 0.99)
            measurement_reliability = clamp(rng.gauss(0.86, 0.11) - creative_fatigue * 0.12, 0.46, 0.99)
            value_index = clamp(
                54
                + contextual_fit * 28
                + signal_coverage * 16
                + base_retention * 22
                - creative_fatigue * 18
                + rng.uniform(-7, 7),
                30,
                99,
            )
            installs = max(12, int((spend / target_cpi) * (value_index / 74) * rng.uniform(0.78, 1.16)))
            retained_users = int(installs * clamp(base_retention + contextual_fit * 0.08 + rng.uniform(-0.04, 0.04), 0.08, 0.55))
            revenue = round(spend * (target_roas * (value_index / 78) * objective_factor * channel_factor) * rng.uniform(0.78, 1.22), 2)
            cpi = round(spend / max(installs, 1), 2)
            roas = round(revenue / max(spend, 1), 2)
            d7_retention = round(retained_users / max(installs, 1), 3)

            spend_total += spend
            sales_total += revenue
            installs_total += installs
            impressions_total += impressions
            roas_values.append(roas)
            cpi_values.append(cpi)
            retention_values.append(d7_retention)
            pacing_values.append(pacing)
            win_values.append(win_rate)

            daily_rows.append({
                "date": current_date.isoformat(),
                "campaign_id": campaign_id,
                "spend": spend,
                "impressions": impressions,
                "bid_requests": int(impressions / max(win_rate, 0.01)),
                "win_rate": round(win_rate, 3),
                "installs": installs,
                "retained_users": retained_users,
                "attributed_revenue": revenue,
                "cpi": cpi,
                "roas": roas,
                "d7_retention": d7_retention,
                "pacing_index": round(pacing, 3),
                "contextual_fit": round(contextual_fit, 3),
                "signal_coverage": round(signal_coverage, 3),
                "creative_fatigue": round(creative_fatigue, 3),
                "measurement_reliability": round(measurement_reliability, 3),
                "predicted_value_index": round(value_index, 1),
            })

        campaign_rollups[campaign_id] = {
            "spend": spend_total,
            "revenue": sales_total,
            "installs": installs_total,
            "impressions": impressions_total,
            "avg_roas": sum(roas_values) / len(roas_values),
            "avg_cpi": sum(cpi_values) / len(cpi_values),
            "avg_retention": sum(retention_values) / len(retention_values),
            "avg_pacing": sum(pacing_values) / len(pacing_values),
            "avg_win_rate": sum(win_values) / len(win_values),
        }

        for context_idx, app_context in enumerate(app_contexts, 1):
            context_fit = clamp(base_fit + rng.uniform(-0.18, 0.22), 0.18, 0.98)
            supply_quality = clamp(rng.gauss(0.78, 0.15), 0.34, 0.99)
            win_gap = clamp(rng.gauss(0.12, 0.09) + context_fit * 0.08, 0.01, 0.42)
            bid_density = rng.randrange(42000, 380000, 1000)
            predicted_ltv = round((2.8 + vertical_factor * 2.1 + context_fit * 3.6 + supply_quality * 1.4) * rng.uniform(0.84, 1.18), 2)
            value_index = round(clamp(38 + context_fit * 32 + supply_quality * 18 + win_gap * 42, 20, 99), 1)
            recommended_bid_change = round(clamp((value_index - 68) / 90 + win_gap / 2, -0.12, 0.32), 3)
            opportunity = int(bid_density * win_gap * predicted_ltv * 0.018)
            signal_rows.append({
                "signal_id": f"{campaign_id}-SIG{context_idx:02d}",
                "campaign_id": campaign_id,
                "app_context": app_context,
                "device_tier": rng.choice(["high memory Android", "mid-tier Android", "new iOS", "older iOS"]),
                "supply_path": rng.choice(["direct SDK", "exchange curated", "open auction", "retargeting pool"]),
                "bid_density": bid_density,
                "contextual_fit": round(context_fit, 3),
                "supply_quality": round(supply_quality, 3),
                "win_rate_gap": round(win_gap, 3),
                "predicted_ltv": predicted_ltv,
                "predicted_value_index": value_index,
                "recommended_bid_change": recommended_bid_change,
                "estimated_opportunity": opportunity,
            })

        for creative_idx, concept in enumerate(creative_concepts, 1):
            fatigue = clamp(rng.gauss(0.44 + creative_idx * 0.04, 0.17), 0.08, 0.91)
            thumbstop = clamp(rng.gauss(0.31, 0.08) - fatigue * 0.05, 0.12, 0.58)
            conversion_index = clamp(rng.gauss(83, 18) * (1 - fatigue * 0.28), 32, 128)
            spend_share = clamp(rng.gauss(0.18, 0.07), 0.04, 0.38)
            creative_rows.append({
                "creative_id": f"{campaign_id}-CR{creative_idx:02d}",
                "campaign_id": campaign_id,
                "concept": concept,
                "format": rng.choice(["playable", "short video", "static", "creator cutdown", "CTV cutdown"]),
                "spend_share": round(spend_share, 3),
                "thumbstop_rate": round(thumbstop, 3),
                "conversion_index": round(conversion_index, 1),
                "fatigue_score": round(fatigue, 3),
                "learning_tag": rng.choice(["scale", "refresh hook", "rotate audience", "test CTA", "holdout needed"]),
            })

        qa_candidates = [
            ("SKU or event mapping gap", rng.uniform(0.05, 0.24)),
            ("late postback delivery", rng.uniform(0.04, 0.22)),
            ("audience overlap risk", rng.uniform(0.03, 0.2)),
            ("CTV to mobile attribution lag", rng.uniform(0.02, 0.18)),
            ("creative taxonomy missing", rng.uniform(0.04, 0.26)),
        ]
        for qa_idx, (issue, issue_rate) in enumerate(qa_candidates, 1):
            severity_score = clamp(issue_rate * 100 + rng.uniform(6, 34), 4, 68)
            qa_rows.append({
                "qa_id": f"{campaign_id}-QA{qa_idx:02d}",
                "campaign_id": campaign_id,
                "issue_type": issue,
                "issue_rate": round(issue_rate, 3),
                "affected_spend": int(budget * issue_rate * rng.uniform(0.65, 1.18)),
                "severity_score": round(severity_score, 1),
                "owner": rng.choice(["Analytics", "Engineering", "Data Science", "Client strategy"]),
                "status": rng.choice(["open", "triaged", "monitoring", "ready for fix"]),
            })

    signal_by_campaign = defaultdict(list)
    for row in signal_rows:
        signal_by_campaign[row["campaign_id"]].append(row)

    creative_by_campaign = defaultdict(list)
    for row in creative_rows:
        creative_by_campaign[row["campaign_id"]].append(row)

    qa_by_campaign = defaultdict(list)
    for row in qa_rows:
        qa_by_campaign[row["campaign_id"]].append(row)

    opportunity_queue = []
    for campaign in campaigns:
        campaign_id = campaign["campaign_id"]
        rollup = campaign_rollups[campaign_id]
        signals = signal_by_campaign[campaign_id]
        creatives = creative_by_campaign[campaign_id]
        qas = qa_by_campaign[campaign_id]
        roas_gap = max(0, float(campaign["target_roas"]) - rollup["avg_roas"])
        cpi_gap = max(0, rollup["avg_cpi"] - float(campaign["target_cpi"]))
        pacing_gap = abs(1 - rollup["avg_pacing"])
        win_gap = sum(float(row["win_rate_gap"]) for row in signals) / len(signals)
        avg_value = sum(float(row["predicted_value_index"]) for row in signals) / len(signals)
        fatigue = sum(float(row["fatigue_score"]) for row in creatives) / len(creatives)
        qa_severity = sum(float(row["severity_score"]) for row in qas) / len(qas)
        missing_opportunity = int(
            roas_gap * rollup["spend"] * 0.45
            + cpi_gap * rollup["installs"] * 0.35
            + win_gap * rollup["spend"] * 0.8
            + fatigue * rollup["spend"] * 0.22
            + qa_severity * 850
        )
        opportunity_score = round(clamp(
            38
            + roas_gap * 16
            + cpi_gap * 5
            + pacing_gap * 19
            + win_gap * 50
            + fatigue * 18
            + qa_severity * 0.18
            + avg_value * 0.18,
            0,
            100,
        ), 1)
        primary_driver = max(
            [
                ("ROAS under target", roas_gap * 100),
                ("CPI inflation", cpi_gap * 16),
                ("bid win-rate gap", win_gap * 100),
                ("creative fatigue", fatigue * 65),
                ("measurement risk", qa_severity),
            ],
            key=lambda item: item[1],
        )[0]
        next_action = {
            "ROAS under target": "Reallocate spend toward high-value contexts and retest bid caps",
            "CPI inflation": "Tighten acquisition bids and split retargeting recovery pool",
            "bid win-rate gap": "Increase bids on high-LTV contexts with capped holdout",
            "creative fatigue": "Rotate concept family and isolate winning creative dimensions",
            "measurement risk": "Fix QA owner path before client readout",
        }[primary_driver]
        confidence = "High" if qa_severity < 31 and avg_value > 68 else "Medium" if qa_severity < 48 else "Needs validation"
        opportunity_queue.append({
            "campaign_id": campaign_id,
            "client_segment": campaign["client_segment"],
            "vertical": campaign["vertical"],
            "primary_channel": campaign["primary_channel"],
            "geo_cluster": campaign["geo_cluster"],
            "budget": campaign["budget"],
            "spend": rollup["spend"],
            "avg_roas": round(rollup["avg_roas"], 2),
            "target_roas": campaign["target_roas"],
            "avg_cpi": round(rollup["avg_cpi"], 2),
            "target_cpi": campaign["target_cpi"],
            "d7_retention": round(rollup["avg_retention"], 3),
            "avg_win_rate": round(rollup["avg_win_rate"], 3),
            "opportunity_score": opportunity_score,
            "estimated_missing_opportunity": missing_opportunity,
            "primary_driver": primary_driver,
            "next_action": next_action,
            "confidence": confidence,
        })
        recommendation_rows.append({
            "campaign_id": campaign_id,
            "client_segment": campaign["client_segment"],
            "recommendation": next_action,
            "business_case": f"{primary_driver} is the largest explainable constraint with ${missing_opportunity:,} modeled upside.",
            "internal_owner": "Analytics" if primary_driver in {"ROAS under target", "CPI inflation"} else "Data Science" if primary_driver == "bid win-rate gap" else "Client strategy",
            "client_talk_track": f"Focus the next optimization review on {primary_driver.lower()} and validate the change against retained user value.",
        })

    opportunity_queue.sort(key=lambda row: float(row["opportunity_score"]), reverse=True)
    signal_scores = sorted(signal_rows, key=lambda row: float(row["estimated_opportunity"]), reverse=True)
    creative_learning = sorted(creative_rows, key=lambda row: (float(row["fatigue_score"]), -float(row["conversion_index"])), reverse=True)
    qa_queue = sorted(qa_rows, key=lambda row: float(row["severity_score"]), reverse=True)
    recommendation_rows.sort(key=lambda row: next(item["opportunity_score"] for item in opportunity_queue if item["campaign_id"] == row["campaign_id"]), reverse=True)

    write_csv(DATA_DIR / "campaigns.csv", campaigns, list(campaigns[0].keys()))
    write_csv(DATA_DIR / "daily_campaign_metrics.csv", daily_rows, list(daily_rows[0].keys()))
    write_csv(DATA_DIR / "contextual_bid_signals.csv", signal_rows, list(signal_rows[0].keys()))
    write_csv(DATA_DIR / "creative_variants.csv", creative_rows, list(creative_rows[0].keys()))
    write_csv(DATA_DIR / "measurement_qa_checks.csv", qa_rows, list(qa_rows[0].keys()))
    write_csv(DATA_DIR / "client_recommendations.csv", recommendation_rows, list(recommendation_rows[0].keys()))
    write_csv(OUTPUT_DIR / "campaign_opportunity_queue.csv", opportunity_queue, list(opportunity_queue[0].keys()))
    write_csv(OUTPUT_DIR / "contextual_signal_scores.csv", signal_scores, list(signal_scores[0].keys()))
    write_csv(OUTPUT_DIR / "creative_learning_matrix.csv", creative_learning, list(creative_learning[0].keys()))
    write_csv(OUTPUT_DIR / "measurement_qa_queue.csv", qa_queue, list(qa_queue[0].keys()))
    write_csv(OUTPUT_DIR / "client_recommendations.csv", recommendation_rows, list(recommendation_rows[0].keys()))

    summary = {
        "seed": SEED,
        "campaigns": len(campaigns),
        "daily_rows": len(daily_rows),
        "contextual_signal_rows": len(signal_rows),
        "creative_rows": len(creative_rows),
        "qa_rows": len(qa_rows),
        "top_campaign": opportunity_queue[0],
        "modeled_missing_opportunity": sum(int(row["estimated_missing_opportunity"]) for row in opportunity_queue),
        "average_opportunity_score": round(sum(float(row["opportunity_score"]) for row in opportunity_queue) / len(opportunity_queue), 1),
    }
    write_json(OUTPUT_DIR / "summary.json", summary)

    print(f"Generated {len(campaigns)} campaigns and {len(daily_rows):,} daily rows.")
    print(
        f"Top opportunity: {opportunity_queue[0]['campaign_id']} "
        f"score={opportunity_queue[0]['opportunity_score']} "
        f"driver={opportunity_queue[0]['primary_driver']}"
    )


if __name__ == "__main__":
    main()
