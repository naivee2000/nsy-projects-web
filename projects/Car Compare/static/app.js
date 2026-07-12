const form = document.querySelector("#searchForm");
const collectButton = document.querySelector("#collectButton");
const collectButtonLabel = document.querySelector("#collectButtonLabel");
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
const emptyWorkspace = document.querySelector("#emptyWorkspace");
const resultsSurface = document.querySelector("#resultsSurface");
const sourceCount = document.querySelector("#sourceCount");
const queryError = document.querySelector("#queryError");
const runPanel = document.querySelector("#runPanel");
const runStage = document.querySelector("#runStage");
const runElapsed = document.querySelector("#runElapsed");
const runDetail = document.querySelector("#runDetail");
const retryButton = document.querySelector("#retryButton");
const resultNotice = document.querySelector("#resultNotice");
const runError = document.querySelector("#runError");
const analyzeImportedButton = document.querySelector("#analyzeImportedButton");
let activeJobId = "";
let activeJobResult = null;
let activeGenerationJobId = "";
let activeGenerationImpact = null;
let activeGenerationQuery = "";
let generationResearchAvailable = false;
let generationJobRunning = false;
let collectorAvailable = false;
let collectionJobRunning = false;
let activeRun = null;
let runSequence = 0;
let runTimer = null;

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

const chartColors = Object.freeze({
  background: "#11171a",
  text: "#8fa0a6",
  grid: "#273238",
  gridSoft: "#202b30",
  axis: "#405057",
  observed: "#31d7c8",
  observedFill: "#17383a",
  projected: "#8b86ff",
  projectedFill: "#2a2751",
  average: "#c9f255",
  median: "#e9f0f2",
  loss: "#f4b85a",
  lossFill: "#4b371c",
  lossProjectedFill: "#302d55",
  percent: "#ff7b72"
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await startCollection();
});
retryButton?.addEventListener("click", async () => {
  if (!activeRun) return;
  if (activeRun.mode === "manual") await analyzeImportedData();
  else await startCollection();
});
analyzeImportedButton?.addEventListener("click", async () => {
  await analyzeImportedData();
});
queryInput.addEventListener("input", clearQueryError);
queryInput.addEventListener("invalid", (event) => {
  event.preventDefault();
  showQueryError("Enter a make and model before starting research.");
});

renderEmptyState();
syncCollectButton();
loadStatus();

async function runResearch(run = activeRun) {
  if (!run || !isActiveRun(run) || run.failed) return;
  const reportRequestSequence = (run.reportRequestSequence || 0) + 1;
  run.reportRequestSequence = reportRequestSequence;
  const previousReportRequest = run.reportPromise || Promise.resolve();
  const reportRequest = previousReportRequest
    .catch(() => undefined)
    .then(async () => {
      if (!isActiveRun(run) || run.failed) return;
      const payload = {
        query: run.rawQuery,
        captureSource: run.captureSource,
        captureUrl: run.captureUrl,
        captureText: run.captureText,
        msrpPrice: run.msrpPrice,
        msrpUrl: run.msrpUrl,
        maxAge: run.maxAge,
        jobId: run.collectionResult ? run.collectionJobId : "",
        generationJobId: run.generationResult ? run.generationJobId : "",
        generationImpact: run.generationResult || null
      };
      setRunProgress(run, "Calculating depreciation", "Validating accepted rows, deduplicating vehicles, and building the value curve.");
      let report;
      try {
        report = await fetchJson("/api/research", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
      } catch (error) {
        if (!isActiveRun(run) || run.failed || reportRequestSequence < run.reportRequestSequence) return;
        throw error;
      }
      if (!isActiveRun(run) || run.failed) return;
      renderReport(report);
      run.reportRendered = true;
      resultsSurface.classList.remove("isStale");
      resultsSurface.setAttribute("aria-busy", "false");
    });
  run.reportPromise = reportRequest;
  try {
    await reportRequest;
  } finally {
    if (run.reportPromise === reportRequest) run.reportPromise = null;
  }
}

async function loadStatus() {
  try {
    const data = await fetchJson("/api/site-status");
    renderCollectorAvailability(data.collector);
    renderGenerationAvailability(data.generationResearch);
    sourceCount.textContent = `${data.sources.length} feeds`;
    sourceStatus.innerHTML = data.sources
      .map((source) => {
        const cls = source.status.includes("api") ? "sourceItem api" : "sourceItem";
        return `<div class="${cls}">
          <strong>${escapeHtml(source.name)}</strong>
          <span>${escapeHtml(source.status.replaceAll("_", " "))}</span>
          <span class="sourceDetail" title="${escapeHtml(source.result)}">${escapeHtml(source.result)}</span>
        </div>`;
      })
      .join("");
  } catch (error) {
    collectorAvailable = false;
    sourceCount.textContent = "Unavailable";
    sourceStatus.innerHTML = `<p class="mutedText">Source status could not be loaded. You can still analyze manually imported data.</p>`;
    renderCollectorAvailability({ available: false, message: readableError(error) });
    renderGenerationAvailability({ available: false, message: readableError(error) });
  }
}

function renderCollectorAvailability(collector) {
  collectorAvailable = Boolean(collector?.available || collector?.visorAvailable || collector?.websiteCollectorAvailable);
  const status = collectorAvailable ? "Available" : "Website collection offline";
  let detail = collector?.message || "Visor and Codex website collection are unavailable.";
  if (collector?.visorAvailable && collector?.websiteCollectorAvailable) {
    detail = `Visor + Codex website collection ready${collector.dryRun ? " · dry run" : ""}`;
  } else if (collector?.visorAvailable) {
    detail = "Visor market facets available; Codex website collection is offline.";
  } else if (collector?.websiteCollectorAvailable) {
    detail = `Codex website collection ready${collector.dryRun ? " · dry run" : ""}`;
  }
  collectorStatus.dataset.state = collectorAvailable ? "ready" : "offline";
  collectorStatus.innerHTML = `<div class="collectorItem">
    <strong>${escapeHtml(status)}</strong>
    <span title="${escapeHtml(collector?.codexPath || "")}">${escapeHtml(detail)}</span>
    <span id="jobStatusLine">No collection job running.</span>
  </div>`;
  syncCollectButton();
}

function renderGenerationAvailability(researcher) {
  generationResearchAvailable = Boolean(researcher?.available);
  const status = generationResearchAvailable ? "Automatic" : "Not configured";
  const detail = researcher?.available
    ? `Launch-event research enabled${researcher.dryRun ? " · dry run" : ""}`
    : researcher?.message || "Install Codex or set CODEX_BIN.";
  generationStatus.dataset.state = generationResearchAvailable ? "ready" : "offline";
  generationStatus.innerHTML = `<div class="collectorItem">
    <strong>${escapeHtml(status)}</strong>
    <span title="${escapeHtml(researcher?.codexPath || "")}">${escapeHtml(detail)}</span>
    <span id="generationStatusLine">${generationResearchAvailable ? "Runs automatically for the current vehicle." : "Generation forecast skipped."}</span>
  </div>`;
}

async function startCollection() {
  let run;
  try {
    run = await prepareRun("collection");
    if (!run) return;
    setJobStatus("Starting market collection...");
    startGenerationResearch(run);
    const job = await fetchJson("/api/collect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: run.rawQuery, maxAge: run.maxAge })
    });
    if (!isActiveRun(run) || run.failed) return;
    run.collectionJobId = job.id;
    activeJobId = job.id;
    pollCollection(run);
  } catch (error) {
    failRun(run, error);
  }
}

async function analyzeImportedData() {
  let run;
  try {
    run = await prepareRun("manual");
    if (!run) return;
    if (!run.captureText && !run.msrpPrice) {
      throw new AppRequestError("Paste visible listing text or enter an MSRP before analyzing imported data.", 400, "validation");
    }
    run.collectionComplete = true;
    await runResearch(run);
    completeRun(run, "Imported data analyzed", "The report uses only the inputs and verified references shown below.");
  } catch (error) {
    failRun(run, error);
  }
}

async function startGenerationResearch(run) {
  if (!generationResearchAvailable || !isActiveRun(run)) {
    run.generationComplete = true;
    return;
  }
  activeGenerationJobId = "";
  activeGenerationImpact = null;
  activeGenerationQuery = run.key;
  generationJobRunning = true;
  run.generationRunning = true;
  renderGenerationImpact(null);
  setGenerationStatus("Starting generation impact research...");
  try {
    const job = await fetchJson("/api/generation-impact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: run.rawQuery, maxAge: run.maxAge })
    });
    if (!isActiveRun(run) || run.failed) return;
    run.generationJobId = job.id;
    activeGenerationJobId = job.id;
    pollGenerationResearch(run);
  } catch (error) {
    if (!isActiveRun(run) || run.failed) return;
    generationJobRunning = false;
    run.generationRunning = false;
    run.generationComplete = true;
    setGenerationStatus(`Skipped: ${readableError(error)}`);
    if (run.collectionComplete) {
      await finishMarketOnlyRun(run, error);
    }
  }
}

async function pollCollection(run) {
  try {
    const job = await fetchJson(`/api/collect/${encodeURIComponent(run.collectionJobId)}`);
    if (!isActiveRun(run) || run.failed) return;
    const elapsed = formatElapsed(job.elapsedSeconds || elapsedSeconds(run));
    setJobStatus(`${friendlyJobState(job.status)}: ${job.message || ""}`);
    const resolvedPrefix = run.resolutionMessage ? `${run.resolutionMessage} ` : "";
    setRunProgress(run, "Collecting market data", `${resolvedPrefix}${job.message || "Checking sources."} · ${elapsed}`);
    if (["queued", "running"].includes(job.status)) {
      setTimeout(() => pollCollection(run), 3000);
      return;
    }
    if (job.status === "completed") {
      run.collectionComplete = true;
      run.collectionResult = job.result || null;
      activeJobResult = run.collectionResult;
      const collected = (job.result?.listings || []).length;
      setJobStatus(`Completed: ${collected.toLocaleString()} raw market observations returned.`);
      await runResearch(run);
      if (!isActiveRun(run) || run.failed) return;
      setCollectionRunning(false);
      setInputsLocked(false);
      if (run.generationRunning || run.reportPromise) {
        const detail = run.reportRendered
          ? "The market curve is ready; generation-impact adjustments are being applied."
          : "Market evidence is ready; the final curve is being calculated with generation-impact research.";
        setRunProgress(run, "Market curve ready", detail);
      } else {
        completeRun(run, "Research complete", resultSummaryText(run.lastReport));
      }
    } else {
      throw new AppRequestError(job.error || job.message || "Market collection did not complete.", 500, "collection");
    }
  } catch (error) {
    failRun(run, error);
  }
}

async function pollGenerationResearch(run) {
  try {
    const job = await fetchJson(`/api/generation-impact/${encodeURIComponent(run.generationJobId)}`);
    if (!isActiveRun(run) || run.failed) return;
    setGenerationStatus(`${friendlyJobState(job.status)}: ${job.message || ""}`);
    if (["queued", "running"].includes(job.status)) {
      setTimeout(() => pollGenerationResearch(run), 4000);
      return;
    }
    generationJobRunning = false;
    run.generationRunning = false;
    run.generationComplete = true;
    if (job.result) {
      run.generationResult = job.result;
      activeGenerationImpact = job.result;
      renderGenerationImpact(job.result);
    }
    if (job.status === "completed") {
      const adjustmentCount = (job.result?.adjustments || []).length;
      setGenerationStatus(`Completed: ${adjustmentCount} forecast adjustment${adjustmentCount === 1 ? "" : "s"} loaded.`);
      if (run.collectionComplete) {
        await runResearch(run);
        completeRun(run, "Research complete", resultSummaryText(run.lastReport));
      }
    } else {
      setGenerationStatus(`${friendlyJobState(job.status)}: ${job.error || job.message || "Generation research did not complete."}`);
      if (run.collectionComplete) await finishMarketOnlyRun(run);
    }
  } catch (error) {
    if (!isActiveRun(run) || run.failed) return;
    generationJobRunning = false;
    run.generationRunning = false;
    run.generationComplete = true;
    setGenerationStatus(`Skipped: ${readableError(error)}`);
    if (run.collectionComplete) await finishMarketOnlyRun(run, error);
  }
}

async function finishMarketOnlyRun(run, generationError = null) {
  if (!isActiveRun(run) || run.failed) return;
  if (run.reportPromise) {
    try {
      await run.reportPromise;
    } catch (reportError) {
      if (isActiveRun(run) && !run.failed) failRun(run, reportError);
      return;
    }
  }
  if (!isActiveRun(run) || run.failed) return;
  if (!run.reportRendered) {
    failRun(
      run,
      generationError?.kind === "auth"
        ? generationError
        : new AppRequestError("The market report could not be built. Please retry the research.", 500, "research")
    );
    return;
  }
  completeRun(run, "Market research complete", "Generation-impact research was unavailable for this run.");
}

async function prepareRun(mode) {
  clearQueryError();
  clearRunMessages();
  const snapshot = snapshotRunInputs();
  if (!snapshot.rawQuery) {
    showQueryError("Enter a make and model before starting research.");
    queryInput.focus();
    return null;
  }
  const run = {
    ...snapshot,
    id: ++runSequence,
    mode,
    startedAt: Date.now(),
    key: "",
    collectionJobId: "",
    collectionResult: null,
    collectionComplete: mode === "manual",
    generationJobId: "",
    generationResult: null,
    generationRunning: false,
    generationComplete: mode === "manual",
    reportRendered: false,
    reportRequestSequence: 0,
    reportPromise: null,
    failed: false,
    lastReport: null,
  };
  activeRun = run;
  activeJobId = "";
  activeJobResult = null;
  clearGenerationState();
  setCollectionRunning(true);
  setInputsLocked(true);
  resultsSurface.setAttribute("aria-busy", "true");
  if (!resultsSurface.hidden) {
    resultsSurface.classList.add("isStale");
    showResultNotice("Previous results remain visible while the new search runs.", "partial");
  }
  startRunClock(run);
  setRunProgress(run, "Resolving vehicle", "Checking make, model, trim, spelling, and year constraints before collection.");
  const plan = await fetchJson("/api/collection-plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: run.rawQuery, maxAge: run.maxAge })
  });
  if (!isActiveRun(run)) return null;
  run.resolution = plan.resolution;
  run.canonicalQuery = plan.resolution?.canonical || run.rawQuery;
  run.key = `${run.canonicalQuery.toLowerCase()}|${run.maxAge}`;
  const correction = (plan.resolution?.corrections || [])
    .map((item) => `${item.original} → ${item.corrected}`)
    .join(", ");
  if (correction) {
    run.resolutionMessage = `Corrected ${correction}. Researching ${run.canonicalQuery}.`;
    setRunProgress(run, "Vehicle resolved", run.resolutionMessage);
  } else {
    run.resolutionMessage = `Researching ${run.canonicalQuery}.`;
  }
  if (plan.resolution?.confidence === "low") {
    throw new AppRequestError("The make or model could not be resolved confidently. Check the vehicle name and try again.", 400, "validation");
  }
  return run;
}

function clearGenerationState() {
  activeGenerationJobId = "";
  activeGenerationImpact = null;
  activeGenerationQuery = "";
  generationJobRunning = false;
}

function setJobStatus(text) {
  const line = document.querySelector("#jobStatusLine");
  if (line) line.textContent = text;
}

function setGenerationStatus(text) {
  const line = document.querySelector("#generationStatusLine");
  if (line) line.textContent = text;
}

function setCollectionRunning(running) {
  collectionJobRunning = running;
  syncCollectButton();
}

function syncCollectButton() {
  collectButton.disabled = !collectorAvailable || collectionJobRunning;
  collectButton.classList.toggle("isBusy", collectionJobRunning);
  collectButtonLabel.textContent = collectionJobRunning ? "Researching" : "Collect & Research";
  if (analyzeImportedButton) analyzeImportedButton.disabled = collectionJobRunning;
}

function snapshotRunInputs() {
  return {
    rawQuery: queryInput.value.trim(),
    maxAge: clamp(Number(maxAgeInput?.value || 10), 1, 20),
    captureSource: captureSource.value.trim() || "manual_browser",
    captureUrl: captureUrl.value.trim(),
    captureText: captureText.value.trim(),
    msrpPrice: msrpPrice.value.trim(),
    msrpUrl: msrpUrl.value.trim(),
  };
}

function setInputsLocked(locked) {
  queryInput.disabled = locked;
  maxAgeInput.disabled = locked;
  captureSource.disabled = locked;
  captureUrl.disabled = locked;
  captureText.disabled = locked;
  msrpPrice.disabled = locked;
  msrpUrl.disabled = locked;
}

function isActiveRun(run) {
  return Boolean(run && activeRun && run.id === activeRun.id);
}

function setRunProgress(run, stage, detail) {
  if (!isActiveRun(run) || run.failed) return;
  runPanel.hidden = false;
  runPanel.dataset.state = "running";
  runStage.textContent = stage;
  runDetail.textContent = detail;
  updateRunElapsed(run);
  retryButton.hidden = true;
}

function completeRun(run, stage, detail) {
  if (!isActiveRun(run) || run.failed) return;
  stopRunClock();
  setCollectionRunning(false);
  setInputsLocked(false);
  resultsSurface.setAttribute("aria-busy", "false");
  runPanel.hidden = false;
  runPanel.dataset.state = "complete";
  runStage.textContent = stage;
  runDetail.textContent = detail || "Results are ready.";
  updateRunElapsed(run);
  retryButton.hidden = true;
  if (!resultsSurface.hidden) {
    resultsSurface.focus({ preventScroll: true });
    resultsSurface.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function failRun(run, error) {
  if (run && !isActiveRun(run)) return;
  if (run?.failed) return;
  if (run) run.failed = true;
  stopRunClock();
  setCollectionRunning(false);
  setInputsLocked(false);
  resultsSurface.setAttribute("aria-busy", "false");
  const message = readableError(error);
  runPanel.hidden = false;
  runPanel.dataset.state = "error";
  runStage.textContent = error?.kind === "auth" ? "Sign-in required" : "Research stopped";
  runDetail.textContent = message;
  retryButton.hidden = false;
  runError.hidden = false;
  runError.innerHTML = error?.kind === "auth"
    ? `${escapeHtml(message)} <a href="https://dem.nsyprojects.com/login?next=${encodeURIComponent(window.location.href)}">Sign in again</a>`
    : escapeHtml(message);
  if (error?.kind === "validation") showQueryError(message);
}

function startRunClock(run) {
  stopRunClock();
  updateRunElapsed(run);
  runTimer = window.setInterval(() => updateRunElapsed(run), 1000);
}

function stopRunClock() {
  if (runTimer) window.clearInterval(runTimer);
  runTimer = null;
}

function updateRunElapsed(run) {
  if (!runElapsed || !run) return;
  runElapsed.textContent = `${formatElapsed(elapsedSeconds(run))} elapsed`;
}

function elapsedSeconds(run) {
  return Math.max(0, Math.floor((Date.now() - run.startedAt) / 1000));
}

function clearRunMessages() {
  runError.hidden = true;
  runError.textContent = "";
  resultNotice.hidden = true;
  resultNotice.textContent = "";
  resultNotice.dataset.state = "";
}

function showResultNotice(message, state = "partial", actions = []) {
  resultNotice.hidden = false;
  resultNotice.dataset.state = state;
  resultNotice.innerHTML = `<p>${escapeHtml(message)}</p>${actions.join("")}`;
}

function showQueryError(message) {
  queryError.textContent = message;
  queryError.hidden = false;
  queryInput.setAttribute("aria-invalid", "true");
}

function clearQueryError() {
  queryError.textContent = "";
  queryError.hidden = true;
  queryInput.removeAttribute("aria-invalid");
}

async function fetchJson(url, options = {}, timeoutMs = 25000) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  let response;
  try {
    response = await fetch(url, { ...options, signal: controller.signal });
  } catch (error) {
    if (error?.name === "AbortError") throw new AppRequestError("The server took too long to respond. Please retry.", 408, "network");
    throw new AppRequestError("The network connection was interrupted. Please retry.", 0, "network");
  } finally {
    window.clearTimeout(timer);
  }
  const contentType = response.headers.get("content-type") || "";
  let payload = {};
  if (contentType.includes("application/json")) {
    try {
      payload = await response.json();
    } catch {
      throw new AppRequestError("The server returned invalid JSON. Please retry.", response.status, "response");
    }
  } else {
    throw new AppRequestError(
      response.status === 401 ? "Your session expired. Sign in again to continue." : "The server returned an unexpected response.",
      response.status,
      response.status === 401 ? "auth" : "response"
    );
  }
  if (!response.ok) {
    const kind = response.status === 401
      ? "auth"
      : response.status === 409
        ? "stale"
        : [400, 422].includes(response.status)
          ? "validation"
          : "http";
    throw new AppRequestError(payload.error || payload.detail || `Request failed (${response.status}).`, response.status, kind);
  }
  return payload;
}

class AppRequestError extends Error {
  constructor(message, status = 0, kind = "request") {
    super(message);
    this.status = status;
    this.kind = kind;
  }
}

function readableError(error) {
  return error?.message || "Research could not be completed. Please retry.";
}

function friendlyJobState(status) {
  return ({ queued: "Queued", running: "Running", completed: "Completed", partial: "Partial", blocked: "Blocked", failed: "Failed" })[status] || status;
}

function formatElapsed(seconds) {
  const value = Math.max(0, Number(seconds) || 0);
  const minutes = Math.floor(value / 60);
  return `${minutes}:${String(Math.floor(value % 60)).padStart(2, "0")}`;
}

function clamp(value, minimum, maximum) {
  return Math.max(minimum, Math.min(maximum, Number.isFinite(value) ? value : minimum));
}

function renderEmptyState() {
  chartTitle.textContent = "Depreciation Trend";
  chartSub.textContent = "";
  depreciationChartSub.textContent = "";
  runStamp.textContent = "Vehicle value intelligence";
  emptyWorkspace.hidden = false;
  resultsSurface.hidden = true;
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
  if (activeRun) activeRun.lastReport = report;
  const observed = report.buckets.filter((bucket) => bucket.observed).length;
  const predicted = report.buckets.filter((bucket) => bucket.predicted).length;
  const maxAge = report.summary.maxAge || Math.max(10, ...report.buckets.map((bucket) => bucket.age || 0));
  const ageOne = report.buckets.find((bucket) => bucket.age === 1);
  const horizonBucket = report.buckets.find((bucket) => bucket.age === maxAge);
  const estimatedBaseline = report.msrp?.source === "estimated_from_used_market";

  emptyWorkspace.hidden = true;
  resultsSurface.hidden = false;

  chartTitle.textContent = report.summary.displayName || "Depreciation Trend";
  const individualListingRows = Number(report.summary.individualListingRows ?? report.summary.dealerListings ?? 0);
  const dealerListings = Number(report.summary.dealerListings || 0);
  const aggregateObservationPoints = Number(report.summary.aggregateObservationPoints || 0);
  const aggregateMarketCount = Number(report.summary.aggregateMarketCount || aggregateObservationPoints);
  const sampleRows = Number(report.summary.sampleRows || 0);
  const countParts = [];
  if (individualListingRows) {
    const dealerDetail = dealerListings === individualListingRows ? " dealer" : " individual";
    countParts.push(`${individualListingRows.toLocaleString()}${dealerDetail} listing row${individualListingRows === 1 ? "" : "s"}`);
  }
  if (aggregateMarketCount) countParts.push(`${aggregateMarketCount.toLocaleString()} vehicles represented by aggregate facets`);
  if (sampleRows) countParts.push(`${sampleRows.toLocaleString()} demo rows`);
  if (!countParts.length) countParts.push("0 accepted market observations");
  chartSub.textContent = `${countParts.join(" · ")} · ${observed} observed buckets · ${predicted} projected buckets`;
  depreciationChartSub.textContent = estimatedBaseline
    ? "Cumulative loss from an estimated Age 0 baseline; add a verified MSRP to improve accuracy"
    : "Cumulative loss from the verified new-market or MSRP depreciation baseline";
  const generated = report.summary.generatedAt ? new Date(report.summary.generatedAt).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "just now";
  runStamp.textContent = `${generated} · ${maxAge}-year horizon`;

  renderResolver(report.resolution || report.collectionPlan?.resolution);
  metrics.innerHTML = [
    [estimatedBaseline ? "Est. Baseline" : "MSRP Ref", report.msrp.price > 0 ? money.format(report.msrp.price) : "Needs MSRP"],
    ["Age 1 Median", ageOne?.median ? money.format(ageOne.median) : "No data"],
    [`Age ${maxAge} Trend`, horizonBucket?.trend_median ? money.format(horizonBucket.trend_median) : "No data"],
    ["Data Mix", individualListingRows ? `${individualListingRows} individual` : aggregateMarketCount ? `${aggregateMarketCount} aggregate` : sampleRows ? `${sampleRows} demo` : "No matches"],
    ["Duplicates", report.summary.duplicatesRemoved || 0],
    ["Status", reportStatusLabel(report)]
  ]
    .map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`)
    .join("");

  renderChart(report.buckets);
  renderDepreciationChart(report.buckets);
  renderTable(report.buckets);
  renderEvidence(report.evidence || {});
  renderGenerationImpact(report.generationImpact);
  renderPlan(report.collectionPlan);
  renderResultNotice(report);
}

function reportStatusLabel(report) {
  if (report.summary.sampleMode) return "Demo mode";
  if (!report.summary.listingCount) return report.msrp?.price > 0 ? "MSRP only" : "No matches";
  if (report.summary.needsMsrpCapture) return "Needs MSRP";
  if (!(report.summary.individualListingRows ?? report.summary.dealerListings) && report.summary.aggregateMarketCount) return "Aggregate only";
  return "Ready";
}

function renderResultNotice(report) {
  const summary = report.summary || {};
  const notes = report.evidence?.collectorNotes || [];
  const successfulSourceStatuses = new Set(["collected", "success", "completed"]);
  const unavailable = (report.evidence?.collectorSources || []).filter((source) => {
    const status = String(source.status || "").toLowerCase();
    return status && !successfulSourceStatuses.has(status);
  });
  const recoveryActions = [];
  if (collectorAvailable) {
    recoveryActions.push('<button type="button" class="secondaryButton noticeAction" id="retrySourcesFromNotice">Retry sources</button>');
  }
  recoveryActions.push('<button type="button" class="secondaryButton noticeAction" id="openAdvancedFromNotice">Import listing text</button>');
  if (summary.sampleMode) {
    showResultNotice("Demo mode is enabled. Bundled rows are shown for interface testing and are not live market listings.", "partial");
    return;
  }
  if (!summary.listingCount) {
    const actions = [...recoveryActions];
    if (collectorAvailable && (summary.maxAge || 0) < 10) actions.push('<button type="button" class="secondaryButton noticeAction" id="setTenYearHorizon">Use a 10-year horizon</button>');
    showResultNotice(
      notes[0] || "No market observations matched the resolved make, model, trim, and year constraints. Retry the sources, broaden the horizon, or import visible listing text.",
      "partial",
      actions
    );
    bindResultNoticeActions();
    return;
  }
  if (report.msrp?.source === "estimated_from_used_market") {
    const msrpActions = collectorAvailable
      ? [
          '<button type="button" class="secondaryButton noticeAction" id="retrySourcesFromNotice">Retry sources</button>',
          '<button type="button" class="secondaryButton noticeAction" id="addMsrpFromNotice">Add verified MSRP</button>',
        ]
      : ['<button type="button" class="secondaryButton noticeAction" id="addMsrpFromNotice">Add verified MSRP</button>'];
    showResultNotice(
      "The Age 0 depreciation baseline is estimated from the youngest accepted used-market samples. Import a verified MSRP to improve the cumulative-loss curve.",
      "partial",
      msrpActions
    );
    bindResultNoticeActions();
    return;
  }
  if (!(summary.individualListingRows ?? summary.dealerListings) && summary.aggregateMarketCount) {
    showResultNotice(
      `This curve represents ${Number(summary.aggregateMarketCount).toLocaleString()} vehicles from weighted market facets. No individual dealer listings were accepted for this run.`,
      "partial",
      recoveryActions
    );
    bindResultNoticeActions();
    return;
  }
  if (unavailable.length) {
    showResultNotice(
      `${unavailable.length} source${unavailable.length === 1 ? "" : "s"} were partial or unavailable. The curve uses only the accepted evidence listed below.`,
      "partial",
      recoveryActions
    );
    bindResultNoticeActions();
    return;
  }
  resultNotice.hidden = true;
  resultNotice.textContent = "";
}

function bindResultNoticeActions() {
  document.querySelector("#retrySourcesFromNotice")?.addEventListener("click", () => startCollection());
  document.querySelector("#setTenYearHorizon")?.addEventListener("click", () => {
    maxAgeInput.value = 10;
    startCollection();
  });
  document.querySelector("#openAdvancedFromNotice")?.addEventListener("click", () => {
    const advanced = document.querySelector(".advancedBlock");
    if (advanced) advanced.open = true;
    captureText.focus();
  });
  document.querySelector("#addMsrpFromNotice")?.addEventListener("click", () => {
    const advanced = document.querySelector(".advancedBlock");
    if (advanced) advanced.open = true;
    msrpPrice.focus();
  });
}

function resultSummaryText(report) {
  if (!report) return "Results are ready.";
  const summary = report.summary || {};
  if (summary.sampleMode) return `${summary.displayName}: ${summary.sampleRows || summary.listingCount || 0} demo rows.`;
  if (!summary.listingCount) return "No matching market observations were accepted; review the recovery options above the charts.";
  const parts = [];
  const individualRows = summary.individualListingRows ?? summary.dealerListings;
  if (individualRows) parts.push(`${individualRows} individual listing rows`);
  if (summary.aggregateMarketCount) parts.push(`${summary.aggregateMarketCount} vehicles represented by aggregate facets`);
  return `${summary.displayName}: ${parts.join(" and ") || `${summary.listingCount} accepted observations`}.`;
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
  const accessibleTitle = `${chartTitle.textContent || "Vehicle"} depreciation trend`;
  const accessibleDescription = `${candidates.length ? "Observed and projected value curve" : "No accepted market observations"} across vehicle ages 0 through ${maxAge}.`;
  chart.setAttribute("aria-label", accessibleTitle);
  if (!candidates.length) {
    chart.innerHTML = `<title>${escapeHtml(accessibleTitle)}</title><desc>${escapeHtml(accessibleDescription)}</desc>
      <rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>
      <text x="${width / 2}" y="${height / 2 - 8}" text-anchor="middle" class="emptyChart">No market data yet</text>
      <text x="${width / 2}" y="${height / 2 + 22}" text-anchor="middle" font-size="13" fill="${chartColors.text}">Waiting for market observations.</text>`;
    return;
  }
  const maxValue = Math.max(...candidates) * 1.08;
  const minValue = Math.min(...candidates) * 0.86;

  const x = (age) => margin.left + (age / maxAge) * plotW;
  const y = (value) => margin.top + (1 - (value - minValue) / (maxValue - minValue)) * plotH;

  const yTicks = tickValues(minValue, maxValue, 5);
  const ageStep = maxAge <= 10 ? 1 : maxAge <= 15 ? 2 : 5;
  let svg = `<title>${escapeHtml(accessibleTitle)}</title><desc>${escapeHtml(accessibleDescription)}</desc>`;
  svg += `<rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>`;
  for (const tick of yTicks) {
    const ty = y(tick);
    svg += `<line x1="${margin.left}" y1="${ty}" x2="${width - margin.right}" y2="${ty}" stroke="${chartColors.grid}"></line>`;
    svg += `<text x="${margin.left - 12}" y="${ty + 4}" text-anchor="end" font-size="12" fill="${chartColors.text}">${money.format(tick)}</text>`;
  }
  for (let age = 0; age <= maxAge; age += ageStep) {
    const tx = x(age);
    svg += `<line x1="${tx}" y1="${margin.top}" x2="${tx}" y2="${height - margin.bottom}" stroke="${chartColors.gridSoft}"></line>`;
    svg += `<text x="${tx}" y="${height - 18}" text-anchor="middle" font-size="12" fill="${chartColors.text}">${age}</text>`;
  }
  svg += `<text x="${margin.left + plotW / 2}" y="${height - 2}" text-anchor="middle" font-size="12" fill="${chartColors.text}">Vehicle age</text>`;

  const observedPoints = buckets.filter((b) => b.trend_median && !b.predicted).map((b) => `${x(b.age)},${y(b.trend_median)}`);
  const projectedPoints = buckets.filter((b) => b.trend_median && b.age >= firstPredictedAge(buckets) - 1).map((b) => `${x(b.age)},${y(b.trend_median)}`);
  if (observedPoints.length > 1) {
    svg += `<polyline points="${observedPoints.join(" ")}" fill="none" stroke="${chartColors.observed}" stroke-width="3"></polyline>`;
  }
  if (projectedPoints.length > 1) {
    svg += `<polyline points="${projectedPoints.join(" ")}" fill="none" stroke="${chartColors.projected}" stroke-width="3" stroke-dasharray="8 7"></polyline>`;
  }

  for (const bucket of buckets) {
    if (!bucket.median || !bucket.q1 || !bucket.q3 || !bucket.low || !bucket.high) continue;
    const cx = x(bucket.age);
    const boxW = bucket.age === 0 ? 14 : 38;
    const color = bucket.predicted ? chartColors.projected : chartColors.observed;
    const fill = bucket.predicted ? chartColors.projectedFill : chartColors.observedFill;
    const lowY = y(bucket.low);
    const highY = y(bucket.high);
    const q1Y = y(bucket.q1);
    const q3Y = y(bucket.q3);
    const medY = y(bucket.median);
    const avgY = bucket.average ? y(bucket.average) : medY;
    const dash = bucket.predicted ? `stroke-dasharray="5 5"` : "";
    svg += `<g tabindex="0" role="img" aria-label="Age ${bucket.age}, median ${escapeHtml(money.format(bucket.median))}">`;
    svg += `<title>Age ${bucket.age}: median ${money.format(bucket.median)}</title>`;
    svg += `<line x1="${cx}" y1="${highY}" x2="${cx}" y2="${lowY}" stroke="${color}" stroke-width="2" ${dash}></line>`;
    svg += `<line x1="${cx - 12}" y1="${highY}" x2="${cx + 12}" y2="${highY}" stroke="${color}" stroke-width="2" ${dash}></line>`;
    svg += `<line x1="${cx - 12}" y1="${lowY}" x2="${cx + 12}" y2="${lowY}" stroke="${color}" stroke-width="2" ${dash}></line>`;
    svg += `<rect x="${cx - boxW / 2}" y="${q3Y}" width="${boxW}" height="${Math.max(2, q1Y - q3Y)}" rx="4" fill="${fill}" stroke="${color}" stroke-width="2" ${dash}></rect>`;
    svg += `<line x1="${cx - boxW / 2}" y1="${medY}" x2="${cx + boxW / 2}" y2="${medY}" stroke="${chartColors.median}" stroke-width="2"></line>`;
    svg += `<circle cx="${cx}" cy="${avgY}" r="4.5" fill="${chartColors.average}" stroke="${chartColors.background}" stroke-width="1.5"></circle>`;
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
  const accessibleTitle = `${chartTitle.textContent || "Vehicle"} cumulative depreciation`;
  const accessibleDescription = `${points.length ? "Dollar and percentage loss" : "No depreciation baseline available"} across the selected vehicle-age horizon.`;
  depreciationChart.setAttribute("aria-label", accessibleTitle);

  if (!points.length || Math.max(...points.map((point) => point.loss)) <= 0) {
    depreciationChart.innerHTML = `<title>${escapeHtml(accessibleTitle)}</title><desc>${escapeHtml(accessibleDescription)}</desc>
      <rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>
      <text x="${width / 2}" y="${height / 2 - 8}" text-anchor="middle" class="emptyChart">No depreciation data yet</text>
      <text x="${width / 2}" y="${height / 2 + 22}" text-anchor="middle" font-size="13" fill="${chartColors.text}">Waiting for an Age 0 market baseline.</text>`;
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

  let svg = `<title>${escapeHtml(accessibleTitle)}</title><desc>${escapeHtml(accessibleDescription)}</desc>`;
  svg += `<rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>`;
  for (const tick of dollarTicks) {
    const ty = yLoss(tick);
    svg += `<line x1="${margin.left}" y1="${ty}" x2="${width - margin.right}" y2="${ty}" stroke="${chartColors.grid}"></line>`;
    svg += `<text x="${margin.left - 12}" y="${ty + 4}" text-anchor="end" font-size="12" fill="${chartColors.text}">${money.format(tick)}</text>`;
  }
  for (const tick of pctTicks) {
    const ty = yPct(tick);
    svg += `<text x="${width - margin.right + 16}" y="${ty + 4}" text-anchor="start" font-size="12" fill="${chartColors.text}">${fmtAxisPct(tick)}</text>`;
  }
  for (let age = 0; age <= maxAge; age += ageStep) {
    const tx = x(age);
    svg += `<line x1="${tx}" y1="${margin.top}" x2="${tx}" y2="${zeroY}" stroke="${chartColors.gridSoft}"></line>`;
    svg += `<text x="${tx}" y="${height - 18}" text-anchor="middle" font-size="12" fill="${chartColors.text}">${age}</text>`;
  }
  svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${zeroY}" stroke="${chartColors.axis}"></line>`;
  svg += `<line x1="${width - margin.right}" y1="${margin.top}" x2="${width - margin.right}" y2="${zeroY}" stroke="${chartColors.axis}"></line>`;
  svg += `<line x1="${margin.left}" y1="${zeroY}" x2="${width - margin.right}" y2="${zeroY}" stroke="${chartColors.axis}"></line>`;
  svg += `<text x="${margin.left + plotW / 2}" y="${height - 2}" text-anchor="middle" font-size="12" fill="${chartColors.text}">Vehicle age</text>`;
  svg += `<text transform="translate(18 ${margin.top + plotH / 2}) rotate(-90)" text-anchor="middle" font-size="12" fill="${chartColors.text}">Total loss from depreciation baseline</text>`;
  svg += `<text transform="translate(${width - 20} ${margin.top + plotH / 2}) rotate(90)" text-anchor="middle" font-size="12" fill="${chartColors.text}">Total depreciation %</text>`;

  for (const point of points) {
    const cx = x(point.age);
    const top = yLoss(point.loss);
    const color = point.predicted ? chartColors.lossProjectedFill : chartColors.lossFill;
    const stroke = point.predicted ? chartColors.projected : chartColors.loss;
    svg += `<g tabindex="0" role="img" aria-label="Age ${point.age}, ${escapeHtml(money.format(point.loss))} total loss, ${escapeHtml(fmtPct(point.pct))} total depreciation">`;
    svg += `<title>Age ${point.age}: ${money.format(point.loss)} total loss, ${fmtPct(point.pct)} total depreciation</title>`;
    svg += `<rect x="${cx - barW / 2}" y="${top}" width="${barW}" height="${Math.max(0, zeroY - top)}" rx="4" fill="${color}" stroke="${stroke}" stroke-width="1.5"></rect>`;
    svg += `</g>`;
  }

  const firstProjected = firstPredictedAge(buckets);
  const pctObserved = points.filter((point) => !point.predicted).map((point) => `${x(point.age)},${yPct(point.pct)}`);
  const pctProjected = points.filter((point) => point.age >= firstProjected - 1).map((point) => `${x(point.age)},${yPct(point.pct)}`);
  if (pctObserved.length > 1) {
    svg += `<polyline points="${pctObserved.join(" ")}" fill="none" stroke="${chartColors.percent}" stroke-width="3"></polyline>`;
  }
  if (pctProjected.length > 1) {
    svg += `<polyline points="${pctProjected.join(" ")}" fill="none" stroke="${chartColors.projected}" stroke-width="3" stroke-dasharray="8 7"></polyline>`;
  }
  for (const point of points) {
    const stroke = point.predicted ? chartColors.projected : chartColors.percent;
    const cx = x(point.age);
    const cy = yPct(point.pct);
    const labelY = Math.max(margin.top - 14, cy - 12);
    svg += `<text x="${cx}" y="${labelY}" text-anchor="middle" font-size="11" font-weight="760" fill="${stroke}">${fmtPct(point.pct)}</text>`;
    svg += `<circle cx="${cx}" cy="${cy}" r="4.5" fill="${chartColors.background}" stroke="${stroke}" stroke-width="2"></circle>`;
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
      const type = bucket.age === 0
        ? ageZeroLabel(bucket)
        : bucket.generation_adjustment_pct
          ? bucket.predicted ? "Predicted + Gen" : "Forecast Adj"
          : bucket.predicted && bucket.age > 10 ? "Long Projection" : bucket.predicted ? "Predicted" : "Observed";
      return `<tr>
        <td>Age ${bucket.age}</td>
        <td>${bucket.model_year ?? ""}</td>
        <td>${bucket.forecast_year ?? ""}</td>
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
  const ratio = bucket.generation_adjustment_ratio ? ` · x${Number(bucket.generation_adjustment_ratio).toFixed(2)}` : "";
  const year = bucket.generation_adjustment_year ? ` · ${bucket.generation_adjustment_year}` : "";
  const original = bucket.generation_unadjusted_median ? `Before adjustment: ${fmtMoney(bucket.generation_unadjusted_median)}. ` : "";
  return `<span class="impactBadge" title="${escapeHtml(`${original}${basis}`)}">${escapeHtml(label)} ${fmtPct(bucket.generation_adjustment_pct)}${escapeHtml(ratio)}${escapeHtml(year)}</span>`;
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
  if (confidence.includes("estimated")) return "Estimated Baseline";
  if (confidence.includes("current_year_market")) return "Current-Year Market";
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
      <caption class="srOnly">Aggregate source price and mileage snapshots</caption>
      <thead>
        <tr>
          <th scope="col">Source</th>
          <th scope="col">Condition</th>
          <th scope="col">Year</th>
          <th scope="col">Found</th>
          <th scope="col">Median</th>
          <th scope="col">Mean</th>
          <th scope="col">Range</th>
          <th scope="col">Mileage</th>
          <th scope="col">Price Bins</th>
          <th scope="col">URL</th>
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
      <caption class="srOnly">Accepted dealer listings and aggregate sample rows</caption>
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Source</th>
          <th scope="col">Condition</th>
          <th scope="col">Year</th>
          <th scope="col">Price</th>
          <th scope="col">Mileage</th>
          <th scope="col">VIN</th>
          <th scope="col">Dealer</th>
          <th scope="col">Title / Link</th>
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
  if (value == null || value === "") return null;
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
