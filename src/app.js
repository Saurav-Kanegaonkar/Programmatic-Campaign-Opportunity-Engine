const files = {
  summary: "analysis/outputs/summary.json",
  opportunities: "analysis/outputs/campaign_opportunity_queue.csv",
  signals: "analysis/outputs/contextual_signal_scores.csv",
  creatives: "analysis/outputs/creative_learning_matrix.csv",
  qa: "analysis/outputs/measurement_qa_queue.csv",
  recommendations: "analysis/outputs/client_recommendations.csv",
};

const state = {
  opportunities: [],
  signals: [],
  creatives: [],
  qa: [],
  recommendations: [],
  selectedCampaignId: null,
};

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const moneyPrecise = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const compactNumber = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
});

function parseCsv(text) {
  const rows = [];
  const lines = text.trim().split(/\r?\n/);
  const headers = splitCsvLine(lines.shift());
  for (const line of lines) {
    const cells = splitCsvLine(line);
    rows.push(Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""])));
  }
  return rows;
}

function splitCsvLine(line) {
  const cells = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const next = line[index + 1];
    if (char === '"' && quoted && next === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      cells.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  cells.push(current);
  return cells;
}

async function loadCsv(path) {
  const response = await fetch(path);
  return parseCsv(await response.text());
}

function byNumber(key, direction = "desc") {
  return (a, b) => {
    const delta = Number(a[key]) - Number(b[key]);
    return direction === "desc" ? -delta : delta;
  };
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function pillClass(value) {
  const score = Number(value);
  if (score >= 78) return "pill high";
  if (score >= 64) return "pill medium";
  return "pill low";
}

function renderSummary(summary) {
  setText("metricCampaigns", summary.campaigns);
  setText("metricRows", compactNumber.format(summary.daily_rows));
  setText("metricUpside", money.format(summary.modeled_missing_opportunity));
  setText("queueCount", `${state.opportunities.length} ranked`);
  setText("signalRowsCount", `${state.signals.length} segments`);
}

function renderOpportunityRows() {
  const target = document.getElementById("opportunityRows");
  target.innerHTML = state.opportunities
    .slice(0, 10)
    .map((row) => {
      const active = row.campaign_id === state.selectedCampaignId ? "active-row" : "";
      return `
        <tr class="${active}" data-campaign="${row.campaign_id}">
          <td><strong>${row.campaign_id}</strong><span>${row.vertical}</span></td>
          <td>${row.primary_channel}</td>
          <td>${row.avg_roas} / ${row.target_roas}</td>
          <td>${moneyPrecise.format(Number(row.avg_cpi))} / ${moneyPrecise.format(Number(row.target_cpi))}</td>
          <td><mark class="${pillClass(row.opportunity_score)}">${row.opportunity_score}</mark></td>
          <td>${row.primary_driver}</td>
          <td>${money.format(Number(row.estimated_missing_opportunity))}</td>
        </tr>
      `;
    })
    .join("");

  target.querySelectorAll("tr").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedCampaignId = row.dataset.campaign;
      renderOpportunityRows();
      renderDetails();
      renderSignals();
      renderQuality();
    });
  });
}

function renderDetails() {
  const selected = state.opportunities.find((row) => row.campaign_id === state.selectedCampaignId);
  if (!selected) return;
  setText("selectedCampaign", selected.campaign_id);
  setText("detailSegment", `${selected.client_segment}, ${selected.geo_cluster}`);
  setText("detailAction", selected.next_action);
  setText("detailConfidence", selected.confidence);
  const barData = [
    ["Opportunity score", Number(selected.opportunity_score)],
    ["Win rate", Number(selected.avg_win_rate) * 100],
    ["D7 retention", Number(selected.d7_retention) * 100],
  ];
  document.getElementById("scoreBars").innerHTML = barData
    .map(([label, value]) => `
      <div class="bar-row">
        <span>${label}</span>
        <div><i style="width:${Math.min(100, Math.max(4, value))}%"></i></div>
        <b>${value.toFixed(1)}</b>
      </div>
    `)
    .join("");
}

function renderSignals() {
  const selectedSignals = state.signals
    .filter((row) => row.campaign_id === state.selectedCampaignId)
    .sort(byNumber("estimated_opportunity"))
    .slice(0, 6);
  document.getElementById("signalCards").innerHTML = selectedSignals
    .map((row) => `
      <article class="signal-card">
        <div>
          <strong>${row.app_context}</strong>
          <span>${row.device_tier}, ${row.supply_path}</span>
        </div>
        <dl>
          <div><dt>Value</dt><dd>${row.predicted_value_index}</dd></div>
          <div><dt>LTV</dt><dd>${money.format(Number(row.predicted_ltv))}</dd></div>
          <div><dt>Bid</dt><dd>${Math.round(Number(row.recommended_bid_change) * 100)}%</dd></div>
          <div><dt>Upside</dt><dd>${money.format(Number(row.estimated_opportunity))}</dd></div>
        </dl>
      </article>
    `)
    .join("");

  const byContext = state.signals.reduce((acc, row) => {
    acc[row.app_context] = (acc[row.app_context] || 0) + Number(row.estimated_opportunity);
    return acc;
  }, {});
  const maxValue = Math.max(...Object.values(byContext));
  document.getElementById("contextChart").innerHTML = Object.entries(byContext)
    .sort((a, b) => b[1] - a[1])
    .map(([context, value]) => `
      <div class="context-row">
        <span>${context}</span>
        <div><i style="width:${(value / maxValue) * 100}%"></i></div>
        <b>${money.format(value)}</b>
      </div>
    `)
    .join("");
}

function renderQuality() {
  const selectedCreatives = state.creatives
    .filter((row) => row.campaign_id === state.selectedCampaignId)
    .sort(byNumber("fatigue_score"))
    .slice(0, 5);
  document.getElementById("creativeGrid").innerHTML = selectedCreatives
    .map((row) => `
      <article>
        <span>${row.format}</span>
        <h3>${row.concept}</h3>
        <dl>
          <div><dt>Fatigue</dt><dd>${Math.round(Number(row.fatigue_score) * 100)}%</dd></div>
          <div><dt>Conversion</dt><dd>${row.conversion_index}</dd></div>
        </dl>
        <b>${row.learning_tag}</b>
      </article>
    `)
    .join("");

  const selectedQa = state.qa
    .filter((row) => row.campaign_id === state.selectedCampaignId)
    .sort(byNumber("severity_score"))
    .slice(0, 5);
  document.getElementById("qaList").innerHTML = selectedQa
    .map((row) => `
      <article>
        <div>
          <strong>${row.issue_type}</strong>
          <span>${row.owner}, ${row.status}</span>
        </div>
        <mark class="${pillClass(row.severity_score)}">${row.severity_score}</mark>
        <b>${money.format(Number(row.affected_spend))}</b>
      </article>
    `)
    .join("");

  const recs = state.recommendations
    .filter((row) => row.campaign_id === state.selectedCampaignId)
    .slice(0, 2);
  document.getElementById("recommendationList").innerHTML = recs
    .map((row) => `
      <article>
        <strong>${row.recommendation}</strong>
        <p>${row.business_case}</p>
        <span>${row.client_talk_track}</span>
      </article>
    `)
    .join("");
}

function setupTabs() {
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      activateTab(button.dataset.tab);
      window.history.replaceState(null, "", `#${button.dataset.tab}`);
    });
  });
}

function activateTab(tabId) {
  const fallback = document.querySelector(".tab");
  const button = document.querySelector(`.tab[data-tab="${tabId}"]`) || fallback;
  document.querySelectorAll(".tab").forEach((tab) => tab.classList.remove("active"));
  document.querySelectorAll(".surface").forEach((surface) => surface.classList.remove("active"));
  button.classList.add("active");
  document.getElementById(button.dataset.tab).classList.add("active");
}

async function init() {
  const [summary, opportunities, signals, creatives, qa, recommendations] = await Promise.all([
    fetch(files.summary).then((response) => response.json()),
    loadCsv(files.opportunities),
    loadCsv(files.signals),
    loadCsv(files.creatives),
    loadCsv(files.qa),
    loadCsv(files.recommendations),
  ]);

  state.opportunities = opportunities.sort(byNumber("opportunity_score"));
  state.signals = signals.sort(byNumber("estimated_opportunity"));
  state.creatives = creatives;
  state.qa = qa;
  state.recommendations = recommendations;
  state.selectedCampaignId = state.opportunities[0]?.campaign_id;

  setupTabs();
  activateTab(window.location.hash.replace("#", "") || "cockpit");
  renderSummary(summary);
  renderOpportunityRows();
  renderDetails();
  renderSignals();
  renderQuality();
}

init();
