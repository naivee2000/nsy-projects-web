const form = document.querySelector("#searchForm");
const collectButton = document.querySelector("#collectButton");
const generationButton = document.querySelector("#generationButton");
const queryInput = document.querySelector("#query");
const maxAgeInput = document.querySelector("#maxAge");
const captureSource = document.querySelector("#captureSource");
const captureUrl = document.querySelector("#captureUrl");
const captureText = document.querySelector("#captureText");
const msrpPrice = document.querySelector("#msrpPrice");
const msrpUrl = document.querySelector("#msrpUrl");
const metrics = document.querySelector("#summaryMetrics");
const chart = document.querySelector("#chart");
const depreciationChart = document.querySelector("#depreciationChart");
const rows = document.querySelector("#bucketRows");
const sourceStatus = document.querySelector("#sourceStatus");
const collectorStatus = document.querySelector("#collectorStatus");
const generationStatus = document.querySelector("#generationStatus");
const generationImpactPanel = document.querySelector("#generationImpactPanel");
const collectionPlan = document.querySelector("#collectionPlan");
const sourceEvidence = document.querySelector("#sourceEvidence");
const chartTitle = document.querySelector("#chartTitle");
const chartSub = document.querySelector("#chartSub");
const depreciationChartSub = document.querySelector("#depreciationChartSub");
const runStamp = document.querySelector("#runStamp");
const resolverPanel = document.querySelector("#resolverPanel");
let activeJobId = "";
let activeJobResult = null;
let activeGenerationJobId = "";
let activeGenerationImpact = null;

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await runResearch();
});

collectButton.addEventListener("click", async () => {
  await startCollection();
});

generationButton.addEventListener("click", async () => {
  await startGenerationResearch();
});

loadStatus();
renderEmptyState();

async function runResearch() {
  if (!queryInput.value.trim()) {
    activeJobId = "";
    activeJobResult = null;
    activeGenerationJobId = "";
    activeGenerationImpact = null;
    renderEmptyState();
    return;
  }
  const payload = {
    query: queryInput.value,
    captureSource: captureSource.value,
    captureUrl: captureUrl.value,
    captureText: captureText.value,
    msrpPrice: msrpPrice.value,
    msrpUrl: msrpUrl.value,
    maxAge: maxAgeInput?.value || 10,
    jobId: activeJobResult ? activeJobId : "",
    generationJobId: activeGenerationImpact ? activeGenerationJobId : "",
    generationImpact: activeGenerationImpact
  };
  const response = await fetch("/api/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const report = await response.json();
  if (!response.ok) {
    throw new Error(report.error || "Research failed");
  }
  renderReport(report);
}

async function loadStatus() {
  const response = await fetch("/api/site-status");
  const data = await response.json();
  renderCollectorAvailability(data.collector);
  renderGenerationAvailability(data.generationResearch);
  sourceStatus.innerHTML = data.sources
    .map((source) => {
      const cls = source.status.includes("api") ? "sourceItem api" : "sourceItem";
      return `<div class="${cls}">
        <strong>${escapeHtml(source.name)}</strong>
        <span>${escapeHtml(source.status.replaceAll("_", " "))}</span>
        <span>${escapeHtml(source.result)}</span>
      </div>`;
    })
    .join("");
}

function renderCollectorAvailability(collector) {
  const status = collector?.available ? "Available" : "Not configured";
  const detail = collector?.available
    ? `${collector.codexPath}${collector.dryRun ? " · dry run" : ""}`
    : collector?.message || "Install Codex or set CODEX_BIN.";
  collectorStatus.innerHTML = `<div class="collectorItem">
    <strong>${escapeHtml(status)}</strong>
    <span>${escapeHtml(detail)}</span>
    <span id="jobStatusLine">No collection job running.</span>
  </div>`;
  collectButton.disabled = !collector?.available;
}

function renderGenerationAvailability(researcher) {
  const status = researcher?.available ? "Available" : "Not configured";
  const detail = researcher?.available
    ? `${researcher.codexPath}${researcher.dryRun ? " · dry run" : ""}`
    : researcher?.message || "Install Codex or set CODEX_BIN.";
  generationStatus.innerHTML = `<div class="collectorItem">
    <strong>${escapeHtml(status)}</strong>
    <span>${escapeHtml(detail)}</span>
    <span id="generationStatusLine">No generation research loaded.</span>
  </div>`;
  generationButton.disabled = !researcher?.available;
}

async function startCollection() {
  if (!queryInput.value.trim()) {
    activeJobId = "";
    activeJobResult = null;
    renderEmptyState();
    setJobStatus("No collection job running.");
    return;
  }
  activeJobId = "";
  activeJobResult = null;
  collectButton.disabled = true;
  setJobStatus("Starting collection job...");
  const response = await fetch("/api/collect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: queryInput.value, maxAge: maxAgeInput?.value || 10 })
  });
  const job = await response.json();
  if (!response.ok) {
    setJobStatus(job.error || "Could not start collection.");
    collectButton.disabled = false;
    return;
  }
  activeJobId = job.id;
  pollCollection(job.id);
}

async function startGenerationResearch() {
  if (!queryInput.value.trim()) {
    activeGenerationJobId = "";
    activeGenerationImpact = null;
    renderGenerationImpact(null);
    setGenerationStatus("No generation research loaded.");
    return;
  }
  activeGenerationJobId = "";
  activeGenerationImpact = null;
  generationButton.disabled = true;
  renderGenerationImpact(null);
  setGenerationStatus("Starting generation impact research...");
  const response = await fetch("/api/generation-impact", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: queryInput.value, maxAge: maxAgeInput?.value || 10 })
  });
  const job = await response.json();
  if (!response.ok) {
    setGenerationStatus(job.error || "Could not start generation research.");
    generationButton.disabled = false;
    return;
  }
  activeGenerationJobId = job.id;
  pollGenerationResearch(job.id);
}

async function pollCollection(jobId) {
  const response = await fetch(`/api/collect/${encodeURIComponent(jobId)}`);
  const job = await response.json();
  if (!response.ok) {
    setJobStatus(job.error || "Collection job not found.");
    collectButton.disabled = false;
    return;
  }
  setJobStatus(`${job.status}: ${job.message || ""}`);
  if (["queued", "running"].includes(job.status)) {
    setTimeout(() => pollCollection(jobId), 3000);
    return;
  }
  collectButton.disabled = false;
  if (job.result) {
    activeJobResult = job.result;
  }
  if (job.status === "completed") {
    setJobStatus(`Completed: ${(job.result?.listings || []).length} listings collected.`);
    await runResearch();
  } else {
    setJobStatus(`${job.status}: ${job.error || job.message || "Collection did not complete."}`);
  }
}

async function pollGenerationResearch(jobId) {
  const response = await fetch(`/api/generation-impact/${encodeURIComponent(jobId)}`);
  const job = await response.json();
  if (!response.ok) {
    setGenerationStatus(job.error || "Generation research job not found.");
    generationButton.disabled = false;
    return;
  }
  setGenerationStatus(`${job.status}: ${job.message || ""}`);
  if (["queued", "running"].includes(job.status)) {
    setTimeout(() => pollGenerationResearch(jobId), 4000);
    return;
  }
  generationButton.disabled = false;
  if (job.result) {
    activeGenerationImpact = job.result;
    renderGenerationImpact(job.result);
  }
  if (job.status === "completed") {
    const adjustmentCount = (job.result?.adjustments || []).length;
    setGenerationStatus(`Completed: ${adjustmentCount} forecast adjustment${adjustmentCount === 1 ? "" : "s"} loaded.`);
    await runResearch();
  } else {
    setGenerationStatus(`${job.status}: ${job.error || job.message || "Generation research did not complete."}`);
  }
}

function setJobStatus(text) {
  const line = document.querySelector("#jobStatusLine");
  if (line) line.textContent = text;
}

function setGenerationStatus(text) {
  const line = document.querySelector("#generationStatusLine");
  if (line) line.textContent = text;
}

function renderEmptyState() {
  chartTitle.textContent = "Depreciation Trend";
  chartSub.textContent = "";
  depreciationChartSub.textContent = "";
  runStamp.textContent = "Depreciation research";
  resolverPanel.innerHTML = "";
  metrics.innerHTML = "";
  chart.innerHTML = "";
  depreciationChart.innerHTML = "";
  rows.innerHTML = "";
  sourceEvidence.innerHTML = "";
  collectionPlan.innerHTML = "";
  renderGenerationImpact(activeGenerationImpact);
}

function renderReport(report) {
  const observed = report.buckets.filter((bucket) => bucket.observed).length;
  const predicted = report.buckets.filter((bucket) => bucket.predicted).length;
  const maxAge = report.summary.maxAge || Math.max(10, ...report.buckets.map((bucket) => bucket.age || 0));
  const ageOne = report.buckets.find((bucket) => bucket.age === 1);
  const horizonBucket = report.buckets.find((bucket) => bucket.age === maxAge);

  chartTitle.textContent = report.summary.displayName || "Depreciation Trend";
  chartSub.textContent = `${report.summary.listingCount} listings, ${observed} observed buckets, ${predicted} projected buckets`;
  depreciationChartSub.textContent = "Cumulative loss from Age 0 median over vehicle age";
  runStamp.textContent = `Run year ${report.summary.currentYear} · ${maxAge}-year horizon`;

  renderResolver(report.resolution || report.collectionPlan?.resolution);
  metrics.innerHTML = [
    ["MSRP Ref", report.msrp.price > 0 ? money.format(report.msrp.price) : "Needs MSRP"],
    ["Age 1 Median", ageOne?.median ? money.format(ageOne.median) : "No data"],
    [`Age ${maxAge} Trend`, horizonBucket?.trend_median ? money.format(horizonBucket.trend_median) : "No data"],
    ["Sources", Object.keys(report.summary.sources).length || 0],
    ["Duplicates", report.summary.duplicatesRemoved || 0],
    ["Status", report.summary.dataQuality === "needs_collection" ? "Needs capture" : report.summary.needsMsrpCapture ? "Needs MSRP" : "Ready"]
  ]
    .map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`)
    .join("");

  renderChart(report.buckets);
  renderDepreciationChart(report.buckets);
  renderTable(report.buckets);
  renderEvidence(report.evidence || {});
  renderGenerationImpact(report.generationImpact);
  renderPlan(report.collectionPlan);
}

function renderResolver(resolution) {
  if (!resolverPanel) return;
  if (!resolution?.chips?.length) {
    resolverPanel.innerHTML = "";
    return;
  }
  const warnings = resolution.warnings || [];
  resolverPanel.innerHTML = `<div class="resolverHead">
      <div>
        <h2>Parsed Vehicle</h2>
        <p>${escapeHtml(resolution.canonical || "Unknown vehicle")}</p>
      </div>
      <span class="resolverConfidence ${escapeHtml(resolution.confidence || "medium")}">${escapeHtml(resolution.confidence || "medium")} confidence</span>
    </div>
    <div class="chipRow">
      ${resolution.chips.map((chip) => `<span class="chip ${escapeHtml(chip.mode)}" title="${escapeHtml(`${chip.label}: ${chip.value} (${chip.mode})`)}">
        <b>${escapeHtml(chip.label)}</b>${escapeHtml(chip.value)}
      </span>`).join("")}
    </div>
    ${warnings.length ? `<div class="resolverWarnings">${warnings.map((warning) => `<span>${escapeHtml(warning)}</span>`).join("")}</div>` : ""}`;
}

function renderChart(buckets) {
  const width = 980;
  const height = 460;
  const margin = { top: 24, right: 28, bottom: 48, left: 78 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const maxAge = Math.max(1, ...buckets.map((bucket) => Number(bucket.age) || 0));
  const candidates = buckets.flatMap((b) => [b.high, b.q3, b.median, b.average, b.trend_median].filter(Boolean));
  if (!candidates.length) {
    chart.innerHTML = `<rect x="0" y="0" width="${width}" height="${height}" fill="white"></rect>
      <text x="${width / 2}" y="${height / 2 - 8}" text-anchor="middle" class="emptyChart">No market data yet</text>
      <text x="${width / 2}" y="${height / 2 + 22}" text-anchor="middle" font-size="13" fill="#627077">Use the collection plan, import visible listing text, then rerun research.</text>`;
    return;
  }
  const maxValue = Math.max(...candidates) * 1.08;
  const minValue = Math.min(...candidates) * 0.86;

  const x = (age) => margin.left + (age / maxAge) * plotW;
  const y = (value) => margin.top + (1 - (value - minValue) / (maxValue - minValue)) * plotH;

  const yTicks = tickValues(minValue, maxValue, 5);
  const ageStep = maxAge <= 10 ? 1 : maxAge <= 15 ? 2 : 5;
  let svg = "";
  svg += `<rect x="0" y="0" width="${width}" height="${height}" fill="white"></rect>`;
  for (const tick of yTicks) {
    const ty = y(tick);
    svg += `<line x1="${margin.left}" y1="${ty}" x2="${width - margin.right}" y2="${ty}" stroke="#e8ecea"></line>`;
    svg += `<text x="${margin.left - 12}" y="${ty + 4}" text-anchor="end" font-size="12" fill="#627077">${money.format(tick)}</text>`;
  }
  for (let age = 0; age <= maxAge; age += ageStep) {
    const tx = x(age);
    svg += `<line x1="${tx}" y1="${margin.top}" x2="${tx}" y2="${height - margin.bottom}" stroke="#f0f2f0"></line>`;
    svg += `<text x="${tx}" y="${height - 18}" text-anchor="middle" font-size="12" fill="#627077">${age}</text>`;
  }
  svg += `<text x="${margin.left + plotW / 2}" y="${height - 2}" text-anchor="middle" font-size="12" fill="#627077">Vehicle age</text>`;

  const observedPoints = buckets.filter((b) => b.trend_median && !b.predicted).map((b) => `${x(b.age)},${y(b.trend_median)}`);
  const projectedPoints = buckets.filter((b) => b.trend_median && b.age >= firstPredictedAge(buckets) - 1).map((b) => `${x(b.age)},${y(b.trend_median)}`);
  if (observedPoints.length > 1) {
    svg += `<polyline points="${observedPoints.join(" ")}" fill="none" stroke="#007a78" stroke-width="3"></polyline>`;
  }
  if (projectedPoints.length > 1) {
    svg += `<polyline points="${projectedPoints.join(" ")}" fill="none" stroke="#6f5aa7" stroke-width="3" stroke-dasharray="8 7"></polyline>`;
  }

  for (const bucket of buckets) {
    if (!bucket.median || !bucket.q1 || !bucket.q3 || !bucket.low || !bucket.high) continue;
    const cx = x(bucket.age);
    const boxW = bucket.age === 0 ? 14 : 38;
    const color = bucket.predicted ? "#6f5aa7" : "#007a78";
    const fill = bucket.predicted ? "#efeaf9" : "#e5f3f2";
    const lowY = y(bucket.low);
    const highY = y(bucket.high);
    const q1Y = y(bucket.q1);
    const q3Y = y(bucket.q3);
    const medY = y(bucket.median);
    const avgY = bucket.average ? y(bucket.average) : medY;
    const dash = bucket.predicted ? `stroke-dasharray="5 5"` : "";
    svg += `<g>`;
    svg += `<title>Age ${bucket.age}: median ${money.format(bucket.median)}</title>`;
    svg += `<line x1="${cx}" y1="${highY}" x2="${cx}" y2="${lowY}" stroke="${color}" stroke-width="2" ${dash}></line>`;
    svg += `<line x1="${cx - 12}" y1="${highY}" x2="${cx + 12}" y2="${highY}" stroke="${color}" stroke-width="2" ${dash}></line>`;
    svg += `<line x1="${cx - 12}" y1="${lowY}" x2="${cx + 12}" y2="${lowY}" stroke="${color}" stroke-width="2" ${dash}></line>`;
    svg += `<rect x="${cx - boxW / 2}" y="${q3Y}" width="${boxW}" height="${Math.max(2, q1Y - q3Y)}" rx="4" fill="${fill}" stroke="${color}" stroke-width="2" ${dash}></rect>`;
    svg += `<line x1="${cx - boxW / 2}" y1="${medY}" x2="${cx + boxW / 2}" y2="${medY}" stroke="#1c2528" stroke-width="2"></line>`;
    svg += `<circle cx="${cx}" cy="${avgY}" r="4.5" fill="#d39b28" stroke="white" stroke-width="1.5"></circle>`;
    svg += `</g>`;
  }

  chart.innerHTML = svg;
}

function renderDepreciationChart(buckets) {
  const width = 980;
  const height = 420;
  const margin = { top: 44, right: 132, bottom: 48, left: 86 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const points = buckets
    .map((bucket) => ({
      age: Number(bucket.age) || 0,
      loss: finiteNumber(bucket.depreciation_from_baseline),
      pct: finiteNumber(bucket.depreciation_from_baseline_pct),
      predicted: Boolean(bucket.predicted)
    }))
    .filter((point) => point.loss !== null && point.pct !== null);

  if (!points.length || Math.max(...points.map((point) => point.loss)) <= 0) {
    depreciationChart.innerHTML = `<rect x="0" y="0" width="${width}" height="${height}" fill="white"></rect>
      <text x="${width / 2}" y="${height / 2 - 8}" text-anchor="middle" class="emptyChart">No depreciation data yet</text>
      <text x="${width / 2}" y="${height / 2 + 22}" text-anchor="middle" font-size="13" fill="#627077">Run research with Age 0 market values to calculate depreciation.</text>`;
    return;
  }

  const maxAge = Math.max(1, ...points.map((point) => point.age));
  const maxLoss = Math.max(...points.map((point) => point.loss), 1) * 1.08;
  const maxPct = Math.max(...points.map((point) => point.pct), 0.01) * 1.08;
  const xMax = maxAge + 0.65;
  const zeroY = margin.top + plotH;
  const x = (age) => margin.left + (age / xMax) * plotW;
  const yLoss = (value) => margin.top + (1 - value / maxLoss) * plotH;
  const yPct = (value) => margin.top + (1 - value / maxPct) * plotH;
  const dollarTicks = uniqueNumbers(tickValues(0, maxLoss, 5));
  const pctTicks = uniqueNumbers(tickValues(0, maxPct, 5));
  const ageStep = maxAge <= 10 ? 1 : maxAge <= 15 ? 2 : 5;
  const barW = Math.min(40, Math.max(12, plotW / Math.max(points.length * 1.8, 1)));

  let svg = "";
  svg += `<rect x="0" y="0" width="${width}" height="${height}" fill="white"></rect>`;
  for (const tick of dollarTicks) {
    const ty = yLoss(tick);
    svg += `<line x1="${margin.left}" y1="${ty}" x2="${width - margin.right}" y2="${ty}" stroke="#e8ecea"></line>`;
    svg += `<text x="${margin.left - 12}" y="${ty + 4}" text-anchor="end" font-size="12" fill="#627077">${money.format(tick)}</text>`;
  }
  for (const tick of pctTicks) {
    const ty = yPct(tick);
    svg += `<text x="${width - margin.right + 16}" y="${ty + 4}" text-anchor="start" font-size="12" fill="#627077">${fmtAxisPct(tick)}</text>`;
  }
  for (let age = 0; age <= maxAge; age += ageStep) {
    const tx = x(age);
    svg += `<line x1="${tx}" y1="${margin.top}" x2="${tx}" y2="${zeroY}" stroke="#f0f2f0"></line>`;
    svg += `<text x="${tx}" y="${height - 18}" text-anchor="middle" font-size="12" fill="#627077">${age}</text>`;
  }
  svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${zeroY}" stroke="#cfd7d4"></line>`;
  svg += `<line x1="${width - margin.right}" y1="${margin.top}" x2="${width - margin.right}" y2="${zeroY}" stroke="#cfd7d4"></line>`;
  svg += `<line x1="${margin.left}" y1="${zeroY}" x2="${width - margin.right}" y2="${zeroY}" stroke="#cfd7d4"></line>`;
  svg += `<text x="${margin.left + plotW / 2}" y="${height - 2}" text-anchor="middle" font-size="12" fill="#627077">Vehicle age</text>`;
  svg += `<text transform="translate(18 ${margin.top + plotH / 2}) rotate(-90)" text-anchor="middle" font-size="12" fill="#627077">Total loss from Age 0 median</text>`;
  svg += `<text transform="translate(${width - 20} ${margin.top + plotH / 2}) rotate(90)" text-anchor="middle" font-size="12" fill="#627077">Total depreciation %</text>`;

  for (const point of points) {
    const cx = x(point.age);
    const top = yLoss(point.loss);
    const color = point.predicted ? "#c7badf" : "#e2ad3f";
    const stroke = point.predicted ? "#6f5aa7" : "#b87919";
    svg += `<g>`;
    svg += `<title>Age ${point.age}: ${money.format(point.loss)} total loss, ${fmtPct(point.pct)} total depreciation</title>`;
    svg += `<rect x="${cx - barW / 2}" y="${top}" width="${barW}" height="${Math.max(0, zeroY - top)}" rx="4" fill="${color}" stroke="${stroke}" stroke-width="1.5"></rect>`;
    svg += `</g>`;
  }

  const firstProjected = firstPredictedAge(buckets);
  const pctObserved = points.filter((point) => !point.predicted).map((point) => `${x(point.age)},${yPct(point.pct)}`);
  const pctProjected = points.filter((point) => point.age >= firstProjected - 1).map((point) => `${x(point.age)},${yPct(point.pct)}`);
  if (pctObserved.length > 1) {
    svg += `<polyline points="${pctObserved.join(" ")}" fill="none" stroke="#b5472f" stroke-width="3"></polyline>`;
  }
  if (pctProjected.length > 1) {
    svg += `<polyline points="${pctProjected.join(" ")}" fill="none" stroke="#6f5aa7" stroke-width="3" stroke-dasharray="8 7"></polyline>`;
  }
  for (const point of points) {
    const stroke = point.predicted ? "#6f5aa7" : "#b5472f";
    const cx = x(point.age);
    const cy = yPct(point.pct);
    const labelY = Math.max(margin.top - 14, cy - 12);
    svg += `<text x="${cx}" y="${labelY}" text-anchor="middle" font-size="11" font-weight="760" fill="${stroke}">${fmtPct(point.pct)}</text>`;
    svg += `<circle cx="${cx}" cy="${cy}" r="4.5" fill="white" stroke="${stroke}" stroke-width="2"></circle>`;
  }

  depreciationChart.innerHTML = svg;
}

function renderPlan(plan) {
  if (!plan?.targets?.length) {
    collectionPlan.innerHTML = "";
    return;
  }
  collectionPlan.innerHTML = plan.targets
    .map((target) => `<div class="planItem">
      <strong>${escapeHtml(target.source)}</strong>
      <a href="${escapeHtml(target.url)}" target="_blank" rel="noreferrer">${escapeHtml(target.url)}</a>
      <span>${escapeHtml(target.method)} · ${escapeHtml(target.load_more)}</span>
      <span>Required: ${escapeHtml((target.required_keywords || target.trim_keywords || []).join(", ") || "none")}</span>
      <span>Exclude: ${escapeHtml((target.exclude_keywords || []).join(", ") || "none")}</span>
      <span>${target.nationwide ? "Nationwide target" : "Location-limited target"} · ${escapeHtml(target.location_policy || "")}</span>
      ${target.validation?.length ? `<span>Validation: ${escapeHtml(target.validation.join(" "))}</span>` : ""}
    </div>`)
    .join("");
}

function renderTable(buckets) {
  rows.innerHTML = buckets
    .map((bucket) => {
      const type = bucket.age === 0 ? ageZeroLabel(bucket) : bucket.predicted && bucket.age > 10 ? "Long Projection" : bucket.predicted ? "Predicted" : "Observed";
      return `<tr>
        <td>Age ${bucket.age}</td>
        <td>${bucket.model_year ?? ""}</td>
        <td><span class="badge">${type}</span></td>
        <td>${bucket.sample_count}</td>
        <td>${fmtMoney(bucket.average)}</td>
        <td>${fmtMoney(bucket.median)}</td>
        <td>${fmtMoney(bucket.q1)}</td>
        <td>${fmtMoney(bucket.q3)}</td>
        <td>${fmtMoney(bucket.depreciation_from_previous)}</td>
        <td>${fmtPct(bucket.depreciation_from_previous_pct)}</td>
        <td>${fmtMoney(bucket.depreciation_from_baseline)}</td>
        <td>${fmtPct(bucket.depreciation_from_baseline_pct)}</td>
        <td>${renderGenerationCell(bucket)}</td>
      </tr>`;
    })
    .join("");
}

function renderGenerationCell(bucket) {
  if (!bucket.generation_adjustment_pct) return "";
  const label = bucket.generation_adjustment_label || "Generation adjustment";
  const basis = bucket.generation_adjustment_basis || "";
  return `<span class="impactBadge" title="${escapeHtml(basis)}">${escapeHtml(label)} ${fmtPct(bucket.generation_adjustment_pct)}</span>`;
}

function renderGenerationImpact(impact) {
  if (!generationImpactPanel) return;
  if (!impact?.adjustments?.length) {
    generationImpactPanel.innerHTML = `<p class="mutedText">No generation impact adjustment loaded.</p>`;
    return;
  }
  const nextGen = impact.next_generation || {};
  const estimate = impact.impact_estimate || {};
  generationImpactPanel.innerHTML = `<div class="generationSummary">
    <strong>${escapeHtml(nextGen.expected_model_year ? `Next gen ${nextGen.expected_model_year}` : "Generation timing researched")}</strong>
    <span>${escapeHtml(nextGen.confidence || "unknown")} confidence · base shock ${fmtPct(estimate.extra_drop_pct)}</span>
    <span>${escapeHtml(estimate.rationale || nextGen.notes || "")}</span>
    <div class="impactList">
      ${impact.adjustments.map((item) => `<span>${escapeHtml(`Age ${item.age}`)} · ${item.calendar_year || ""} · ${fmtPct(item.extra_depreciation_pct)}</span>`).join("")}
    </div>
  </div>`;
}

function ageZeroLabel(bucket) {
  const confidence = String(bucket.confidence || "");
  if (confidence.includes("new")) return "New Market";
  if (confidence.includes("msrp")) return "MSRP Ref";
  return "Age 0 Market";
}

function renderEvidence(evidence) {
  const sourceRows = evidence.sources || [];
  const collectorSources = evidence.collectorSources || [];
  const facets = evidence.facets || [];
  const listings = evidence.listings || [];
  const notes = evidence.collectorNotes || [];

  if (!sourceRows.length && !collectorSources.length && !facets.length && !listings.length) {
    sourceEvidence.innerHTML = `<p class="mutedText">No source evidence yet.</p>`;
    return;
  }

  sourceEvidence.innerHTML = `
    ${notes.length ? `<div class="evidenceNotes">${notes.map((note) => `<p>${escapeHtml(note)}</p>`).join("")}</div>` : ""}
    <details open class="evidenceGroup">
      <summary>Source Pages (${sourceRows.length || collectorSources.length})</summary>
      <div class="evidenceSources">
        ${renderSourceRows(sourceRows, collectorSources)}
      </div>
    </details>
    <details open class="evidenceGroup">
      <summary>Source Data Snapshots (${facets.length})</summary>
      ${facets.length ? renderFacetTable(facets) : `<p class="mutedText">No raw facet snapshots were returned for this run.</p>`}
    </details>
    <details class="evidenceGroup">
      <summary>Listing / Sample Rows (${evidence.listingCount || listings.length}${evidence.listingCount > listings.length ? ` shown ${listings.length}` : ""})</summary>
      ${renderListingTable(listings)}
    </details>
  `;
}

function renderSourceRows(sourceRows, collectorSources) {
  const collectorBySource = new Map((collectorSources || []).map((item) => [item.source, item]));
  const merged = sourceRows.length
    ? sourceRows
    : (collectorSources || []).map((item) => ({
        source: item.source,
        count: 0,
        kind: item.status,
        urls: item.url ? [item.url] : [],
        conditions: {},
        years: {}
      }));
  return merged
    .map((source) => {
      const collector = collectorBySource.get(source.source);
      const urls = unique([...(source.urls || []), collector?.url].filter(Boolean));
      return `<div class="evidenceSource">
        <div>
          <strong>${escapeHtml(source.source)}</strong>
          <span>${escapeHtml(source.kind || "source")} · ${Number(source.count || 0).toLocaleString()} rows · ${escapeHtml(formatCounts(source.conditions))}</span>
          ${collector?.notes ? `<span>${escapeHtml(collector.notes)}</span>` : ""}
          ${Object.keys(source.years || {}).length ? `<span>Years: ${escapeHtml(formatCounts(source.years))}</span>` : ""}
        </div>
        <div class="evidenceLinks">
          ${urls.length ? urls.slice(0, 8).map((url) => `<a href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(shortUrl(url))}</a>`).join("") : `<span>No URL captured</span>`}
          ${urls.length > 8 ? `<span>+${urls.length - 8} more URLs in row table</span>` : ""}
        </div>
      </div>`;
    })
    .join("");
}

function renderFacetTable(facets) {
  return `<div class="tableWrap evidenceTableWrap">
    <table class="evidenceTable">
      <thead>
        <tr>
          <th>Source</th>
          <th>Condition</th>
          <th>Year</th>
          <th>Found</th>
          <th>Median</th>
          <th>Mean</th>
          <th>Range</th>
          <th>Mileage</th>
          <th>Price Bins</th>
          <th>URL</th>
        </tr>
      </thead>
      <tbody>
        ${facets.map((facet) => `<tr>
          <td>${escapeHtml(facet.source || "")}</td>
          <td>${escapeHtml(facet.condition || "")}</td>
          <td>${facet.year ?? ""}</td>
          <td>${fmtNumber(facet.num_found)}</td>
          <td>${fmtMoney(facet.price_stats?.median)}</td>
          <td>${fmtMoney(facet.price_stats?.mean)}</td>
          <td>${fmtMoney(facet.price_stats?.min)}-${fmtMoney(facet.price_stats?.max)}</td>
          <td>${fmtMileage(facet.mileage_stats?.median)}</td>
          <td>${renderMiniBins(facet.price_bins || [])}</td>
          <td>${facet.url ? `<a href="${escapeHtml(facet.url)}" target="_blank" rel="noreferrer">open</a>` : ""}</td>
        </tr>`).join("")}
      </tbody>
    </table>
  </div>`;
}

function renderListingTable(listings) {
  if (!listings.length) {
    return `<p class="mutedText">No listing/sample rows are available.</p>`;
  }
  return `<div class="tableWrap evidenceTableWrap">
    <table class="evidenceTable listingEvidenceTable">
      <thead>
        <tr>
          <th>#</th>
          <th>Source</th>
          <th>Condition</th>
          <th>Year</th>
          <th>Price</th>
          <th>Mileage</th>
          <th>VIN</th>
          <th>Dealer</th>
          <th>Title / Link</th>
        </tr>
      </thead>
      <tbody>
        ${listings.map((item) => `<tr>
          <td>${item.index ?? ""}</td>
          <td>${escapeHtml(item.source || "")}</td>
          <td>${escapeHtml(item.condition || "")}</td>
          <td>${item.year ?? ""}</td>
          <td>${fmtMoney(item.price)}</td>
          <td>${fmtMileage(item.mileage)}</td>
          <td>${escapeHtml(item.vin || "")}</td>
          <td>${escapeHtml(item.dealer || "")}</td>
          <td>${item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.title || item.url)}</a>` : escapeHtml(item.title || "")}</td>
        </tr>`).join("")}
      </tbody>
    </table>
  </div>`;
}

function renderMiniBins(bins) {
  if (!bins.length) return "";
  const maxCount = Math.max(...bins.map((bin) => bin.count || 0), 1);
  return `<div class="miniBins">${bins.slice(0, 16).map((bin) => {
    const height = Math.max(10, Math.round(((bin.count || 0) / maxCount) * 42));
    const label = `${fmtMoney(bin.lower)}-${fmtMoney(bin.upper)} · ${fmtNumber(bin.count)}`;
    return `<span style="height:${height}px" title="${escapeHtml(label)}"></span>`;
  }).join("")}</div>`;
}

function formatCounts(value) {
  const entries = Object.entries(value || {});
  if (!entries.length) return "no breakdown";
  return entries.map(([key, count]) => `${key}: ${count}`).join(", ");
}

function unique(values) {
  return [...new Set(values)];
}

function uniqueNumbers(values) {
  return [...new Set(values.map((value) => Number(value.toFixed(6))))];
}

function shortUrl(url) {
  try {
    const parsed = new URL(url);
    return `${parsed.hostname}${parsed.pathname}${parsed.search ? "?" : ""}`;
  } catch {
    return url;
  }
}

function tickValues(minValue, maxValue, count) {
  const span = maxValue - minValue;
  const step = niceNumber(span / (count - 1));
  const start = Math.floor(minValue / step) * step;
  const ticks = [];
  for (let value = start; value <= maxValue + step; value += step) {
    if (value > 0) ticks.push(value);
  }
  return ticks.slice(0, count + 1);
}

function niceNumber(value) {
  const exponent = Math.floor(Math.log10(value));
  const fraction = value / Math.pow(10, exponent);
  const niceFraction = fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 5 ? 5 : 10;
  return niceFraction * Math.pow(10, exponent);
}

function firstPredictedAge(buckets) {
  const found = buckets.find((bucket) => bucket.predicted);
  return found ? found.age : 11;
}

function fmtMoney(value) {
  return value == null ? "" : money.format(value);
}

function fmtPct(value) {
  return value == null ? "" : `${(value * 100).toFixed(1)}%`;
}

function fmtAxisPct(value) {
  const percent = value * 100;
  return `${percent < 10 ? percent.toFixed(1) : percent.toFixed(0)}%`;
}

function fmtNumber(value) {
  return value == null ? "" : Number(value).toLocaleString();
}

function fmtMileage(value) {
  return value == null ? "" : `${Number(value).toLocaleString()} mi`;
}

function finiteNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
