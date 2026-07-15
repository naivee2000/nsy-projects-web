const form = document.querySelector("#searchForm");
const collectButton = document.querySelector("#collectButton");
const collectButtonLabel = document.querySelector("#collectButtonLabel");
const queryInput = document.querySelector("#query");
const queryLabel = document.querySelector("#queryLabel");
const compareQueryField = document.querySelector("#compareQueryField");
const compareQueryInput = document.querySelector("#compareQuery");
const compareQueryError = document.querySelector("#compareQueryError");
const singleModeButton = document.querySelector("#singleModeButton");
const compareModeButton = document.querySelector("#compareModeButton");
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
const valueLegend = document.querySelector("#valueLegend");
const lossLegend = document.querySelector("#lossLegend");
const tableTitle = document.querySelector("#tableTitle");
const bucketTableHead = document.querySelector("#bucketTableHead");
const bucketTable = document.querySelector(".ageBucketTable");
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
const codexFallbackLink = document.querySelector("#codexFallbackLink");
const resultNotice = document.querySelector("#resultNotice");
const runError = document.querySelector("#runError");
const analyzeImportedButton = document.querySelector("#analyzeImportedButton");
const advancedBlock = document.querySelector(".advancedBlock");
const interpretationNotice = document.querySelector("#interpretationNotice");
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
let fallbackPollTimer = null;
let researchMode = "single";

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
  appreciation: "#c9f255",
  appreciationFill: "#2f3c1d",
  depreciation: "#f4b85a",
  depreciationFill: "#4b371c",
  lossProjectedFill: "#302d55",
  percent: "#ff7b72",
  carA: "#31d7c8",
  carAFill: "#17383a",
  carB: "#c9f255",
  carBFill: "#2f3c1d"
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (researchMode === "compare") await startComparison();
  else await startCollection();
});
retryButton?.addEventListener("click", async () => {
  if (!activeRun) return;
  if (activeRun.mode === "manual") await analyzeImportedData();
  else if (activeRun.mode === "comparison") await startComparison();
  else await startCollection();
});
codexFallbackLink?.addEventListener("click", () => {
  if (!activeRun?.fallbackJobs?.length) return;
  setJobStatus("Codex Desktop handoff opened; waiting for verified Chrome marketplace imports.");
  runDetail.textContent = "Send the prefilled @Chrome task. The temporary monitor will refresh this report when Codex imports accepted rows.";
});
analyzeImportedButton?.addEventListener("click", async () => {
  await analyzeImportedData();
});
singleModeButton?.addEventListener("click", () => setResearchMode("single"));
compareModeButton?.addEventListener("click", () => setResearchMode("compare"));
queryInput.addEventListener("input", clearPrimaryQueryError);
compareQueryInput?.addEventListener("input", clearCompareQueryError);
queryInput.addEventListener("invalid", (event) => {
  event.preventDefault();
  showQueryError("Enter a make and model before starting research.");
});
compareQueryInput?.addEventListener("invalid", (event) => {
  event.preventDefault();
  showCompareQueryError("Enter a second make and model before starting comparison.");
});

setResearchMode("single", false);
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
    const cacheReady = collector?.captureCache?.ready ? " · persistent verified cache" : "";
    detail = collector?.browserWorkerAvailable
      ? `Visor + Codex + audited browser worker ready${collector?.backgroundMode ? " · background workers" : ""}${collector?.persistentBrowserReady ? ` · ${collector.persistentBrowserMode || "persistent profile"}` : " · Playwright browser required"}${collector?.hostChromeFallbackReady ? " · zero-click Chrome retry" : ""}${collector?.codexSearchFallbackReady ? " · indexed source recovery" : ""}${cacheReady}${collector.dryRun ? " · dry run" : ""}`
      : "Visor available; Codex is logged in but the audited browser worker needs npm install.";
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

function setResearchMode(mode, resetWorkspace = true) {
  if (collectionJobRunning) return;
  researchMode = mode === "compare" ? "compare" : "single";
  const comparing = researchMode === "compare";
  form.classList.toggle("compareMode", comparing);
  compareQueryField.hidden = !comparing;
  compareQueryInput.required = comparing;
  queryLabel.textContent = comparing ? "Car A" : "Vehicle query";
  document.querySelector("#queryHelp").textContent = comparing
    ? "Enter a make, model, and trim."
    : "Enter a make, model, and trim. Common spelling mistakes are corrected automatically.";
  singleModeButton.setAttribute("aria-pressed", String(!comparing));
  compareModeButton.setAttribute("aria-pressed", String(comparing));
  if (advancedBlock) advancedBlock.hidden = comparing;
  if (generationResearchAvailable && !generationJobRunning) {
    setGenerationStatus(comparing ? "Runs automatically for both vehicles." : "Runs automatically for the current vehicle.");
  }
  clearQueryError();
  syncCollectButton();
  if (!resetWorkspace) return;
  stopFallbackMonitor();
  activeRun = null;
  runPanel.hidden = true;
  clearRunMessages();
  renderEmptyState();
  (comparing ? compareQueryInput : queryInput).focus();
}

async function startComparison() {
  let run;
  try {
    run = await prepareComparisonRun();
    if (!run) return;

    const collectionTasks = run.vehicles.map((vehicle, index) => collectComparisonVehicle(run, vehicle, index));
    const generationTasks = generationResearchAvailable
      ? run.vehicles.map((vehicle, index) => researchComparisonGeneration(run, vehicle, index))
      : [];
    if (!generationResearchAvailable) {
      run.vehicles.forEach((vehicle) => { vehicle.generationComplete = true; });
      setGenerationStatus("Generation forecast skipped for this comparison.");
    }
    await Promise.all([...collectionTasks, ...generationTasks]);

    setRunProgress(run, "Building comparison", "Aligning both median curves, cumulative losses, percentages, and forecast adjustments by vehicle age.");
    const reports = await Promise.all(run.vehicles.map((vehicle) => buildComparisonReport(run, vehicle)));
    if (!isActiveRun(run) || run.failed) return;
    run.reports = reports;
    run.lastReport = reports;
    renderComparison(reports[0], reports[1]);
    setJobStatus("Completed: both vehicle market collections are loaded.");
    const completedGeneration = run.vehicles.filter((vehicle) => vehicle.generationResult).length;
    setGenerationStatus(
      generationResearchAvailable
        ? `Completed for ${completedGeneration} of 2 vehicles${completedGeneration < 2 ? "; market-only forecast retained where unavailable." : "."}`
        : "Generation forecast skipped for this comparison."
    );
    completeRun(
      run,
      "Comparison complete",
      `${reports[0].summary.displayName} and ${reports[1].summary.displayName} are aligned across the same ${run.maxAge}-year horizon.`
    );
    beginFallbackMonitoring(
      run,
      run.vehicles
        .filter((vehicle) => vehicle.collectionJob?.fallback?.status === "pending")
        .map((vehicle) => ({
          jobId: vehicle.collectionJobId,
          label: vehicle.label,
          updatedAt: Number(vehicle.collectionJob.updatedAt || 0),
          fallback: vehicle.collectionJob.fallback,
        }))
    );
  } catch (error) {
    failRun(run, error);
  }
}

async function prepareComparisonRun() {
  clearQueryError();
  clearRunMessages();
  const rawQueryA = queryInput.value.trim();
  const rawQueryB = compareQueryInput.value.trim();
  if (!rawQueryA) {
    showQueryError("Enter the first make and model before starting comparison.");
    queryInput.focus();
    return null;
  }
  if (!rawQueryB) {
    showCompareQueryError("Enter the second make and model before starting comparison.");
    compareQueryInput.focus();
    return null;
  }

  const maxAge = clamp(Number(maxAgeInput?.value || 10), 1, 20);
  const run = {
    id: ++runSequence,
    mode: "comparison",
    startedAt: Date.now(),
    maxAge,
    failed: false,
    vehicles: [],
    reports: [],
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
    showResultNotice("Previous results remain visible while the new comparison runs.", "partial");
  }
  startRunClock(run);

  const rawQueries = [rawQueryA, rawQueryB];
  for (let index = 0; index < rawQueries.length; index += 1) {
    const label = index === 0 ? "Car A" : "Car B";
    setRunProgress(run, `Resolving ${label}`, `Checking the ${label} make, model, trim, spelling, and year constraints.`);
    const plan = await fetchJson("/api/collection-plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: rawQueries[index], maxAge })
    });
    if (!isActiveRun(run) || run.failed) return null;
    if (plan.resolution?.confidence === "low") {
      const error = new AppRequestError(`${label} could not be resolved confidently. Check the vehicle name and try again.`, 400, index === 0 ? "validation" : "compare_validation");
      if (index === 1) showCompareQueryError(error.message);
      throw error;
    }
    const canonicalQuery = plan.resolution?.canonical || rawQueries[index];
    const correction = (plan.resolution?.corrections || [])
      .map((item) => `${item.original} → ${item.corrected}`)
      .join(", ");
    run.vehicles.push({
      label,
      rawQuery: rawQueries[index],
      canonicalQuery,
      key: `${canonicalQuery.toLowerCase()}|${maxAge}`,
      plan,
      resolution: plan.resolution,
      resolutionMessage: correction ? `Corrected ${correction}.` : "",
      collectionJobId: "",
      collectionResult: null,
      generationJobId: "",
      generationResult: null,
      generationComplete: false,
    });
  }

  if (run.vehicles[0].key === run.vehicles[1].key) {
    const error = new AppRequestError("Choose two different vehicles for comparison.", 400, "compare_validation");
    showCompareQueryError(error.message);
    throw error;
  }
  return run;
}

async function collectComparisonVehicle(run, vehicle, index) {
  if (!isActiveRun(run) || run.failed) return;
  const position = `${index + 1} of ${run.vehicles.length}`;
  setJobStatus(`${vehicle.label}: starting market collection (${position}).`);
  setRunProgress(
    run,
    `Collecting ${vehicle.label}`,
    `${vehicle.resolutionMessage ? `${vehicle.resolutionMessage} ` : ""}${vehicle.canonicalQuery} is ${position}; independent source work runs concurrently while the backend coordinates shared-browser access.`
  );
  const started = await fetchJson("/api/collect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: vehicle.rawQuery, maxAge: run.maxAge })
  });
  vehicle.collectionJobId = started.id;
  activeJobId = started.id;
  const job = await waitForComparisonJob(run, `/api/collect/${encodeURIComponent(started.id)}`, 3000, (current) => {
    const elapsed = formatElapsed(current.elapsedSeconds || elapsedSeconds(run));
    setJobStatus(`${vehicle.label}: ${friendlyJobState(current.status)}: ${current.message || ""}`);
    setRunProgress(run, `Collecting ${vehicle.label}`, `${vehicle.canonicalQuery} · ${current.message || "Checking sources."} · ${elapsed}`);
  });
  if (job.status !== "completed") {
    throw new AppRequestError(`${vehicle.label} collection failed: ${job.error || job.message || "No completed market result was returned."}`, 500, "collection");
  }
  vehicle.collectionResult = job.result || null;
  vehicle.collectionJob = job;
  activeJobResult = vehicle.collectionResult;
  const collected = Number(job.result?.listings?.length || 0);
  setJobStatus(`${vehicle.label}: completed with ${collected.toLocaleString()} raw market observations.`);
  if (job.fallback?.status === "pending") {
    const otherJobs = (run.fallbackJobs || []).filter((item) => item.jobId !== job.id);
    beginFallbackMonitoring(run, [...otherJobs, {
      jobId: job.id,
      label: vehicle.label,
      updatedAt: Number(job.updatedAt || 0),
      fallback: job.fallback,
    }]);
  }
}

async function researchComparisonGeneration(run, vehicle, index) {
  if (!isActiveRun(run) || run.failed) return;
  setGenerationStatus(`${vehicle.label}: starting generation-impact research (${index + 1} of 2).`);
  setRunProgress(run, `Researching ${vehicle.label}`, `Checking replacement-generation timing and depreciation impact for ${vehicle.canonicalQuery}.`);
  try {
    const started = await fetchJson("/api/generation-impact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: vehicle.rawQuery, maxAge: run.maxAge })
    });
    vehicle.generationJobId = started.id;
    const job = await waitForComparisonJob(run, `/api/generation-impact/${encodeURIComponent(started.id)}`, 4000, (current) => {
      setGenerationStatus(`${vehicle.label}: ${friendlyJobState(current.status)}: ${current.message || ""}`);
      setRunProgress(run, `Researching ${vehicle.label}`, current.message || `Evaluating generation events for ${vehicle.canonicalQuery}.`);
    });
    vehicle.generationComplete = true;
    if (job.status === "completed" && job.result) {
      vehicle.generationResult = job.result;
      return;
    }
    vehicle.generationError = job.error || job.message || "Generation research did not complete.";
  } catch (error) {
    vehicle.generationComplete = true;
    vehicle.generationError = readableError(error);
  }
  setGenerationStatus(`${vehicle.label}: skipped (${vehicle.generationError}).`);
}

async function waitForComparisonJob(run, url, intervalMs, onUpdate) {
  while (isActiveRun(run) && !run.failed) {
    const job = await fetchJson(url);
    if (!isActiveRun(run) || run.failed) return job;
    onUpdate(job);
    if (!["queued", "running"].includes(job.status)) return job;
    await delay(intervalMs);
  }
  throw new AppRequestError("The comparison was replaced by a newer request.", 409, "stale");
}

async function buildComparisonReport(run, vehicle) {
  const payload = {
    query: vehicle.rawQuery,
    maxAge: run.maxAge,
    jobId: vehicle.collectionJobId,
    generationJobId: vehicle.generationResult ? vehicle.generationJobId : "",
    generationImpact: vehicle.generationResult || null
  };
  return fetchJson("/api/research", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

function delay(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
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
      run.collectionJobUpdatedAt = Number(job.updatedAt || 0);
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
      beginFallbackMonitoring(run, job.fallback?.status === "pending" ? [{
        jobId: run.collectionJobId,
        label: "Vehicle",
        updatedAt: run.collectionJobUpdatedAt,
        fallback: job.fallback,
      }] : []);
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
  stopFallbackMonitor();
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
  collectButtonLabel.textContent = collectionJobRunning
    ? researchMode === "compare" ? "Comparing" : "Researching"
    : researchMode === "compare" ? "Compare & Research" : "Collect & Research";
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
  compareQueryInput.disabled = locked;
  singleModeButton.disabled = locked;
  compareModeButton.disabled = locked;
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
  stopFallbackMonitor();
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

function beginFallbackMonitoring(run, jobs) {
  if (!isActiveRun(run) || !jobs.length) {
    stopFallbackMonitor();
    return;
  }
  stopFallbackMonitor();
  run.fallbackJobs = jobs;
  codexFallbackLink.href = buildCodexFallbackLink(jobs);
  codexFallbackLink.hidden = false;
  const sourceCount = jobs.reduce((count, item) => count + (item.fallback?.sources?.length || 0), 0);
  const remaining = Math.min(...jobs.map((item) => Number(item.fallback?.remainingSeconds || 0)));
  setJobStatus(`Optional source repair is available for ${sourceCount} source${sourceCount === 1 ? "" : "s"} that automatic collection could not access; expires in ${formatLeaseTime(remaining)}.`);
  fallbackPollTimer = window.setTimeout(() => pollFallbackJobs(run), 5000);
}

function buildCodexFallbackLink(jobs) {
  const jobText = jobs.map((item) => `${item.jobId} (${item.label})`).join(", ");
  const prompt = `@Chrome Use $collect-car-marketplaces to repair only the active temporary Car Compare fallback lease for ${jobText}. The Car Compare base URL is ${window.location.origin}. Use the connected Chrome profile, import every source listed by /api/codex-browser-actions for these job IDs, then stop.`;
  const projectPath = jobs[0]?.fallback?.projectPath || "";
  const params = new URLSearchParams({ prompt });
  if (projectPath) params.set("path", projectPath);
  return `codex://threads/new?${params.toString()}`;
}

async function pollFallbackJobs(run) {
  if (!isActiveRun(run) || run.failed || !run.fallbackJobs?.length) return;
  try {
    const jobs = await Promise.all(
      run.fallbackJobs.map((item) => fetchJson(`/api/collect/${encodeURIComponent(item.jobId)}`))
    );
    if (!isActiveRun(run) || run.failed) return;
    let changed = false;
    for (const job of jobs) {
      const tracked = run.fallbackJobs.find((item) => item.jobId === job.id);
      if (tracked && Number(job.updatedAt || 0) > Number(tracked.updatedAt || 0)) {
        tracked.updatedAt = Number(job.updatedAt || 0);
        changed = true;
      }
      if (tracked) tracked.fallback = job.fallback;
      if (run.mode === "comparison") {
        const vehicle = run.vehicles.find((item) => item.collectionJobId === job.id);
        if (vehicle) {
          vehicle.collectionResult = job.result || vehicle.collectionResult;
          vehicle.collectionJob = job;
        }
      } else if (job.id === run.collectionJobId) {
        run.collectionResult = job.result || run.collectionResult;
        activeJobResult = run.collectionResult;
      }
    }
    if (changed && (run.mode !== "comparison" || run.reports?.length === 2)) {
      await refreshFallbackReport(run);
    }
    if (!isActiveRun(run) || run.failed) return;
    const pending = run.fallbackJobs.filter((item) => item.fallback?.status === "pending");
    if (pending.length) {
      run.fallbackJobs = pending;
      codexFallbackLink.href = buildCodexFallbackLink(pending);
      const remaining = Math.min(...pending.map((item) => Number(item.fallback?.remainingSeconds || 0)));
      setJobStatus(`Codex + Chrome fallback monitor active; ${pending.length} collection job${pending.length === 1 ? "" : "s"} waiting, ${formatLeaseTime(remaining)} remaining.`);
      fallbackPollTimer = window.setTimeout(() => pollFallbackJobs(run), 5000);
      return;
    }
    stopFallbackMonitor();
    const completed = jobs.some((job) => job.fallback?.status === "completed");
    setJobStatus(completed
      ? "Codex Chrome fallback finished; the report now includes accepted marketplace rows."
      : "Temporary Codex Chrome fallback expired; no background monitor remains active.");
    if (completed) {
      runPanel.dataset.state = "complete";
      runStage.textContent = run.mode === "comparison" ? "Comparison refreshed" : "Research refreshed";
      runDetail.textContent = "Verified Codex Chrome marketplace imports were applied to the report.";
    }
  } catch (error) {
    if (!isActiveRun(run) || run.failed) return;
    stopFallbackMonitor();
    setJobStatus(`Fallback monitor stopped: ${readableError(error)}`);
  }
}

async function refreshFallbackReport(run) {
  if (run.mode === "comparison") {
    const reports = await Promise.all(run.vehicles.map((vehicle) => buildComparisonReport(run, vehicle)));
    if (!isActiveRun(run) || run.failed) return;
    run.reports = reports;
    run.lastReport = reports;
    renderComparison(reports[0], reports[1]);
    return;
  }
  await runResearch(run);
}

function stopFallbackMonitor() {
  if (fallbackPollTimer) window.clearTimeout(fallbackPollTimer);
  fallbackPollTimer = null;
  codexFallbackLink.hidden = true;
}

function formatLeaseTime(seconds) {
  const value = Math.max(0, Number(seconds) || 0);
  const minutes = Math.ceil(value / 60);
  return minutes <= 1 ? "under 1 minute" : `${minutes} minutes`;
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

function showCompareQueryError(message) {
  compareQueryError.textContent = message;
  compareQueryError.hidden = false;
  compareQueryInput.setAttribute("aria-invalid", "true");
}

function clearPrimaryQueryError() {
  queryError.textContent = "";
  queryError.hidden = true;
  queryInput.removeAttribute("aria-invalid");
}

function clearCompareQueryError() {
  compareQueryError.textContent = "";
  compareQueryError.hidden = true;
  compareQueryInput.removeAttribute("aria-invalid");
}

function clearQueryError() {
  clearPrimaryQueryError();
  clearCompareQueryError();
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
  runStamp.textContent = researchMode === "compare" ? "Two-vehicle value intelligence" : "Vehicle value intelligence";
  const emptyTitle = emptyWorkspace.querySelector("h2");
  const emptyText = emptyWorkspace.querySelector("p");
  if (emptyTitle) emptyTitle.textContent = researchMode === "compare" ? "Comparison workspace standby" : "Market intelligence standby";
  if (emptyText) emptyText.textContent = researchMode === "compare"
    ? "Enter two vehicles above to compare their depreciation."
    : "Enter a vehicle above to start market research.";
  emptyWorkspace.hidden = false;
  resultsSurface.hidden = true;
  resolverPanel.innerHTML = "";
  metrics.innerHTML = "";
  chart.innerHTML = "";
  depreciationChart.innerHTML = "";
  rows.innerHTML = "";
  sourceEvidence.innerHTML = "";
  collectionPlan.innerHTML = "";
  if (interpretationNotice) {
    interpretationNotice.hidden = true;
    interpretationNotice.innerHTML = "";
  }
  renderGenerationImpact(activeGenerationImpact);
}

function renderReport(report) {
  if (activeRun) activeRun.lastReport = report;
  setSingleResultScaffolding();
  const observed = report.buckets.filter(bucketIsObservedMarket).length;
  const predicted = report.buckets.filter(bucketIsProjection).length;
  const sparse = report.buckets.filter(bucketIsSparseProjection).length;
  const maxAge = report.summary.maxAge || Math.max(10, ...report.buckets.map((bucket) => bucket.age || 0));
  const ageOne = report.buckets.find((bucket) => bucket.age === 1);
  const horizonBucket = report.buckets.find((bucket) => bucket.age === maxAge);
  const estimatedBaseline = report.msrp?.source === "estimated_from_used_market";
  const allTrimMarketMix = isAllTrimReport(report);
  const trimNormalized = trimNormalizationApplied(report);
  const msrpWarning = msrpScopeWarning(report);

  emptyWorkspace.hidden = true;
  resultsSurface.hidden = false;

  chartTitle.textContent = trimNormalized
    ? `${report.summary.displayName || "Vehicle"} · Trim-Normalized Depreciation`
    : allTrimMarketMix
    ? `${report.summary.displayName || "Vehicle"} · All-Trim Market Mix`
    : report.summary.displayName || "Depreciation Trend";
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
  const bucketParts = [`${observed} observed market bucket${observed === 1 ? "" : "s"}`, `${predicted} projected bucket${predicted === 1 ? "" : "s"}`];
  if (sparse) bucketParts.push(`${sparse} projected from insufficient samples`);
  chartSub.textContent = `${trimNormalized ? "Fixed reference trim mix · raw market medians remain in the table · " : allTrimMarketMix ? "Current market mix by model year · normalization unavailable · " : ""}${countParts.join(" · ")} · ${bucketParts.join(" · ")}`;
  depreciationChartSub.textContent = estimatedBaseline
    ? "Signed bars show annual value movement from an estimated Age 0 baseline; positive is appreciation and negative is depreciation"
    : trimNormalized
    ? "Signed bars show movement along the trim-normalized curve; the raw market median remains in the table"
    : "Signed bars show annual value movement; the line shows signed change from the Age 0 market median";
  const generated = report.summary.generatedAt ? new Date(report.summary.generatedAt).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "just now";
  runStamp.textContent = `${generated} · ${maxAge}-year horizon`;

  renderResolver(report.resolution || report.collectionPlan?.resolution);
  metrics.innerHTML = [
    [estimatedBaseline ? "Est. Baseline" : msrpWarning ? "MSRP Ref · Scope Check" : "MSRP Reference", report.msrp.price > 0 ? money.format(report.msrp.price) : "Needs MSRP"],
    ["Age 1 Market Median", bucketMarketMedian(ageOne) ? money.format(bucketMarketMedian(ageOne)) : "No data"],
    [`Age ${maxAge} ${bucketIsProjection(horizonBucket) ? "Forecast" : "Market Value"}`, bucketDisplayValue(horizonBucket) ? money.format(bucketDisplayValue(horizonBucket)) : "No data"],
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
  renderInterpretationNotice(report);
}

function setSingleResultScaffolding() {
  valueLegend.innerHTML = `
    <span><i class="line observed"></i>Observed curve</span>
    <span><i class="line projected"></i>Projection / sparse estimate</span>
    <span><i class="dot"></i>Average</span>
    <span><i class="forecastRing"></i>Generation-adjusted forecast</span>`;
  lossLegend.innerHTML = `
    <span><i class="barIcon appreciation"></i>Appreciation</span>
    <span><i class="barIcon depreciation"></i>Depreciation</span>
    <span><i class="line percent"></i>Change from Age 0</span>
    <span><i class="line projected"></i>Projected</span>`;
  tableTitle.textContent = "Age Buckets";
  bucketTable.classList.remove("comparisonTable");
  bucketTableHead.innerHTML = `<tr>
    <th scope="col">Age</th>
    <th scope="col">Model Year</th>
    <th scope="col">Calendar Year</th>
    <th scope="col">Type</th>
    <th scope="col">Samples</th>
    <th scope="col">Average</th>
    <th scope="col">Market Median</th>
    <th scope="col">Curve Value</th>
    <th scope="col">Q1</th>
    <th scope="col">Q3</th>
    <th scope="col">YoY Movement</th>
    <th scope="col">YoY Change</th>
    <th scope="col">Since Age 0</th>
    <th scope="col">Total Change</th>
    <th scope="col">Outliers</th>
    <th scope="col">Forecast Adj</th>
  </tr>`;
}

function renderComparison(reportA, reportB) {
  const reports = [reportA, reportB];
  const names = reports.map((report) => report.summary.displayName || "Vehicle");
  const maxAge = Math.max(...reports.map((report) => Number(report.summary.maxAge || 0)), 1);
  const comparisonAge = Math.min(5, maxAge);
  const comparisonBuckets = reports.map((report) => bucketAtAge(report, comparisonAge));
  const horizonBuckets = reports.map((report) => bucketAtAge(report, maxAge));
  const generatedDates = reports
    .map((report) => report.summary.generatedAt ? new Date(report.summary.generatedAt).getTime() : 0)
    .filter(Boolean);

  emptyWorkspace.hidden = true;
  resultsSurface.hidden = false;
  resultsSurface.classList.remove("isStale");
  resultsSurface.setAttribute("aria-busy", "false");
  chartTitle.textContent = `${names[0]} vs ${names[1]}`;
  const normalizedResults = reports.filter(trimNormalizationApplied).length;
  chartSub.textContent = `${comparisonEvidenceSummary(reportA)} · ${comparisonEvidenceSummary(reportB)} · aligned by vehicle age${normalizedResults ? ` · ${normalizedResults} trim-normalized curve${normalizedResults === 1 ? "" : "s"}` : reports.some(isAllTrimReport) ? " · all-trim normalization unavailable" : ""}`;
  depreciationChartSub.textContent = "Grouped signed bars show each year's value movement; labeled dots show signed change from each vehicle's own Age 0 median.";
  const generated = generatedDates.length
    ? new Date(Math.max(...generatedDates)).toLocaleString([], { dateStyle: "medium", timeStyle: "short" })
    : "just now";
  runStamp.textContent = `${generated} · two vehicles · ${maxAge}-year horizon`;

  valueLegend.innerHTML = `
    <span><i class="vehicleSwatch"></i>${escapeHtml(names[0])}</span>
    <span><i class="vehicleSwatch carB"></i>${escapeHtml(names[1])}</span>
    <span><i class="styleSwatch projected"></i>Predicted</span>`;
  lossLegend.innerHTML = `
    <span><i class="vehicleSwatch"></i>Car A</span>
    <span><i class="vehicleSwatch carB"></i>Car B</span>
    <span><i class="barSwatch"></i>YoY value movement</span>
    <span><i class="styleSwatch"></i>Change from Age 0</span>
    <span><i class="styleSwatch projected"></i>Predicted</span>`;
  tableTitle.textContent = "Comparison by Age";

  renderComparisonResolver(reportA, reportB);
  metrics.innerHTML = [
    { label: `${names[0]} baseline`, value: fmtMoney(bucketDisplayValue(bucketAtAge(reportA, 0))), className: "carA" },
    { label: `${names[1]} baseline`, value: fmtMoney(bucketDisplayValue(bucketAtAge(reportB, 0))), className: "carB" },
    { label: `Age ${comparisonAge} value change`, value: `A ${fmtSignedMoney(bucketSignedBaselineChange(reportA.buckets, comparisonBuckets[0])) || "-"} · B ${fmtSignedMoney(bucketSignedBaselineChange(reportB.buckets, comparisonBuckets[1])) || "-"}`, className: "" },
    { label: `Age ${comparisonAge} change %`, value: `A ${fmtSignedPct(bucketSignedBaselinePct(reportA.buckets, comparisonBuckets[0])) || "-"} · B ${fmtSignedPct(bucketSignedBaselinePct(reportB.buckets, comparisonBuckets[1])) || "-"}`, className: "" },
    { label: `Age ${maxAge} value`, value: `A ${fmtMoney(bucketDisplayValue(horizonBuckets[0])) || "-"} · B ${fmtMoney(bucketDisplayValue(horizonBuckets[1])) || "-"}`, className: "" },
    { label: "Accepted observations", value: `A ${Number(reportA.summary.listingCount || 0).toLocaleString()} · B ${Number(reportB.summary.listingCount || 0).toLocaleString()}`, className: "" },
  ].map((item) => `<div class="metric ${item.className}"><span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.value)}</strong></div>`).join("");

  renderComparisonChart(reportA, reportB);
  renderComparisonDepreciationChart(reportA, reportB);
  renderComparisonTable(reportA, reportB);
  renderComparisonTabs(sourceEvidence, [
    { title: names[0], className: "carA", html: evidenceMarkup(reportA.evidence || {}) },
    { title: names[1], className: "carB", html: evidenceMarkup(reportB.evidence || {}) },
  ], "evidence");
  renderComparisonTabs(collectionPlan, [
    { title: names[0], className: "carA", html: planMarkup(reportA.collectionPlan) },
    { title: names[1], className: "carB", html: planMarkup(reportB.collectionPlan) },
  ], "plan");
  renderComparisonGenerationImpact(reportA, reportB);
  renderComparisonResultNotice(reportA, reportB);
  renderComparisonInterpretationNotice(reportA, reportB);
}

function comparisonEvidenceSummary(report) {
  const summary = report.summary || {};
  const name = summary.displayName || "Vehicle";
  const individual = Number(summary.individualListingRows ?? summary.dealerListings ?? 0);
  const aggregate = Number(summary.aggregateMarketCount || 0);
  const parts = [];
  if (individual) parts.push(`${individual} individual`);
  if (aggregate) parts.push(`${aggregate} aggregate`);
  if (!parts.length && Number(summary.listingCount || 0)) parts.push(`${Number(summary.listingCount).toLocaleString()} accepted`);
  return `${name}: ${parts.join(" + ") || "no accepted observations"}`;
}

function renderComparisonResolver(reportA, reportB) {
  const items = [
    { label: "Car A", className: "carA", resolution: reportA.resolution || reportA.collectionPlan?.resolution },
    { label: "Car B", className: "carB", resolution: reportB.resolution || reportB.collectionPlan?.resolution },
  ];
  resolverPanel.innerHTML = `<div class="comparisonResolverGrid">${items.map((item) => {
    const resolution = item.resolution || {};
    const warnings = resolution.warnings || [];
    return `<section class="comparisonResolver ${item.className}">
      <div class="resolverHead">
        <div>
          <span class="vehicleKey ${item.className}">${item.label}</span>
          <h2>${escapeHtml(resolution.canonical || "Unknown vehicle")}</h2>
        </div>
        <span class="resolverConfidence ${escapeHtml(resolution.confidence || "medium")}">${escapeHtml(resolution.confidence || "medium")}</span>
      </div>
      <div class="chipRow">${(resolution.chips || []).map((chip) => `<span class="chip ${escapeHtml(chip.mode)}"><b>${escapeHtml(chip.label)}</b>${escapeHtml(chip.value)}</span>`).join("")}</div>
      ${warnings.length ? `<div class="resolverWarnings">${warnings.map((warning) => `<span>${escapeHtml(warning)}</span>`).join("")}</div>` : ""}
    </section>`;
  }).join("")}</div>`;
}

function renderComparisonResultNotice(reportA, reportB) {
  const reports = [reportA, reportB];
  const missing = reports.filter((report) => !Number(report.summary?.listingCount || 0));
  const estimated = reports.filter((report) => report.msrp?.source === "estimated_from_used_market");
  if (!missing.length && !estimated.length) {
    resultNotice.hidden = true;
    resultNotice.textContent = "";
    return;
  }
  const message = missing.length
    ? `${missing.map((report) => report.summary.displayName).join(" and ")} returned no accepted market observations; the comparison shows only available baseline or projected values.`
    : `${estimated.map((report) => report.summary.displayName).join(" and ")} uses an estimated Age 0 median baseline because verified new-market evidence was unavailable.`;
  showResultNotice(message, "partial", ['<button type="button" class="secondaryButton noticeAction" id="retryComparisonFromNotice">Retry comparison</button>']);
  document.querySelector("#retryComparisonFromNotice")?.addEventListener("click", () => startComparison());
}

function renderComparisonTabs(container, panels, prefix) {
  const tabId = `${prefix}ComparisonTabs`;
  container.innerHTML = `<div class="comparisonTabs" id="${tabId}" role="tablist" aria-label="${escapeHtml(prefix)} vehicle">
    ${panels.map((panel, index) => `<button type="button" class="${panel.className}" role="tab" aria-selected="${index === 0}" aria-controls="${prefix}Panel${index}">${escapeHtml(panel.title)}</button>`).join("")}
  </div>
  ${panels.map((panel, index) => `<div class="comparisonPanel" id="${prefix}Panel${index}" role="tabpanel" ${index === 0 ? "" : "hidden"}>${panel.html}</div>`).join("")}`;
  const tabs = [...container.querySelectorAll(`#${tabId} [role="tab"]`)];
  const tabPanels = [...container.querySelectorAll(".comparisonPanel")];
  tabs.forEach((tab, index) => tab.addEventListener("click", () => {
    tabs.forEach((item, itemIndex) => item.setAttribute("aria-selected", String(itemIndex === index)));
    tabPanels.forEach((panel, panelIndex) => { panel.hidden = panelIndex !== index; });
  }));
}

function renderComparisonGenerationImpact(reportA, reportB) {
  const reports = [reportA, reportB];
  generationImpactPanel.innerHTML = `<div class="comparisonGenerationList">${reports.map((report, index) => {
    const impact = report.generationImpact || {};
    const adjustments = impact.adjustments || [];
    const nextGen = impact.next_generation || {};
    return `<div class="comparisonGenerationItem ${index === 1 ? "carB" : "carA"}">
      <strong>${escapeHtml(report.summary.displayName || `Car ${index === 0 ? "A" : "B"}`)}</strong>
      ${adjustments.length
        ? `<span>Forecast scenario only · ${escapeHtml(nextGen.expected_model_year ? `Next gen ${nextGen.expected_model_year}` : "Generation event researched")} · ${adjustments.map((item) => `Age ${item.age} -${fmtPct(item.extra_depreciation_pct)}`).join(" · ")}</span>`
        : "<span>No generation adjustment loaded.</span>"}
    </div>`;
  }).join("")}</div>`;
}

function renderInterpretationNotice(report) {
  if (!interpretationNotice) return;
  const items = [];
  if (isAllTrimReport(report)) {
    items.push(trimNormalizationApplied(report)
      ? "The main curve holds the accepted trim mix more consistent across model years. Raw all-trim market medians remain in the table and may still rise when premium or collectible variants dominate current inventory."
      : "All-trim normalization did not have enough supported cohorts, so the curve remains a current market-mix view. Select a trim for a narrower result.");
  }
  const scopeWarning = msrpScopeWarning(report);
  if (scopeWarning) items.push(scopeWarning);
  const outlierCount = (report?.buckets || []).reduce(
    (total, bucket) => total + Number(bucket?.outlier_count || 0),
    0,
  );
  if (outlierCount) {
    items.push(`${outlierCount} extreme price row${outlierCount === 1 ? " is" : "s are"} retained in source evidence but excluded from IQR box-plot whiskers.`);
  }
  if (!items.length) {
    interpretationNotice.hidden = true;
    interpretationNotice.innerHTML = "";
    return;
  }
  interpretationNotice.hidden = false;
  interpretationNotice.innerHTML = `<strong>How to read this result</strong><ul>${items.map((item, index) => `<li${index > 0 ? ' class="msrpScopeWarning"' : ""}>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderComparisonInterpretationNotice(reportA, reportB) {
  if (!interpretationNotice) return;
  const reports = [reportA, reportB];
  const allTrim = reports.filter(isAllTrimReport);
  const scopeWarnings = reports.map(msrpScopeWarning).filter(Boolean);
  const items = [];
  if (allTrim.length) {
    const normalizedCount = allTrim.filter(trimNormalizationApplied).length;
    items.push(`${normalizedCount} of ${allTrim.length} all-trim result${allTrim.length === 1 ? "" : "s"} use${normalizedCount === 1 ? "s" : ""} a fixed reference trim mix. Raw market medians remain visible for comparison.`);
  }
  items.push(...scopeWarnings);
  if (!items.length) {
    interpretationNotice.hidden = true;
    interpretationNotice.innerHTML = "";
    return;
  }
  interpretationNotice.hidden = false;
  interpretationNotice.innerHTML = `<strong>Comparison scope</strong><ul>${items.map((item, index) => `<li${index >= (allTrim.length ? 1 : 0) ? ' class="msrpScopeWarning"' : ""}>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function isAllTrimReport(report) {
  const resolution = report?.resolution || report?.collectionPlan?.resolution || {};
  if (Array.isArray(resolution.include_all) && resolution.include_all.includes("trim")) return true;
  const trimChip = (resolution.chips || []).find((chip) => chip?.key === "trim");
  if (trimChip) return trimChip.mode === "all" || /^all trims$/i.test(String(trimChip.value || ""));
  if (!report?.query) return false;
  return !String(report.query.trim || "").trim();
}

function trimNormalizationApplied(report) {
  return String(report?.summary?.trimNormalization?.status || "").toLowerCase() === "applied";
}

function msrpScopeWarning(report) {
  if (!isAllTrimReport(report) || !finiteNumber(report?.msrp?.price)) return "";
  const label = String(report?.msrp?.label || "").trim();
  if (!label || /^user supplied msrp$/i.test(label) || report?.msrp?.source === "estimated_from_used_market") return "";
  const scope = namedMsrpScope(report, label);
  if (!scope) return "";
  const vehicle = report?.summary?.displayName || report?.resolution?.canonical || "this model";
  return `MSRP scope warning: ${money.format(report.msrp.price)} is labeled “${label}” and appears to reference ${scope}, while ${vehicle} includes all trims. Treat it as a named-configuration reference, not an all-trim baseline.`;
}

function namedMsrpScope(report, label) {
  const model = String(report?.query?.model || "").trim();
  if (model) {
    const lowerLabel = label.toLowerCase();
    const modelIndex = lowerLabel.indexOf(model.toLowerCase());
    if (modelIndex >= 0) {
      let suffix = label.slice(modelIndex + model.length);
      suffix = suffix.split(/\b(?:base\s+msrp|starting\s+msrp|msrp|excluding|including|price)\b/i)[0];
      suffix = suffix
        .replace(/\b(?:coupe|coupé|convertible|cabriolet|sedan|suv|wagon|hatchback|roadster|spyder|awd|rwd|4wd|fwd)\b/gi, " ")
        .replace(/[^a-z0-9+-]+/gi, " ")
        .replace(/\s+/g, " ")
        .trim();
      if (suffix && suffix.split(" ").length <= 6) return suffix;
    }
  }
  const labelKey = normalizedWords(label);
  const rows = [...(report?.listings || []), ...(report?.evidence?.listings || [])];
  const candidates = unique(rows.map((row) => String(row?.trim || "").trim()).filter(Boolean))
    .filter((trim) => normalizedWords(trim).length >= 2)
    .sort((left, right) => normalizedWords(left).length - normalizedWords(right).length);
  return candidates.find((trim) => labelKey.includes(normalizedWords(trim))) || "";
}

function normalizedWords(value) {
  return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function bucketAtAge(report, age) {
  return (report?.buckets || []).find((bucket) => Number(bucket.age) === Number(age)) || null;
}

function bucketDisplayValue(bucket) {
  if (!bucket) return null;
  if (bucketIsSparseProjection(bucket) && !bucket.predicted) return null;
  const curveMedian = finiteNumber(bucket.curve_median);
  if (curveMedian !== null) return curveMedian;
  if (bucketIsObservedMarket(bucket)) return bucketMarketMedian(bucket);
  return finiteNumber(bucket.trend_median) ?? finiteNumber(bucket.median);
}

function bucketMarketMedian(bucket) {
  if (!bucket) return null;
  if (Object.prototype.hasOwnProperty.call(bucket, "market_median")) {
    return finiteNumber(bucket.market_median);
  }
  return bucket.predicted ? null : finiteNumber(bucket.median);
}

function bucketIsObservedMarket(bucket) {
  if (!bucket || bucketIsProjection(bucket)) return false;
  return Boolean(bucket.observed) && bucketMarketMedian(bucket) !== null;
}

function bucketIsProjection(bucket) {
  if (!bucket) return false;
  const confidence = String(bucket.confidence || "").toLowerCase();
  return Boolean(bucket.predicted) || confidence.includes("projected") || bucketIsSparseProjection(bucket);
}

function bucketIsSparseProjection(bucket) {
  if (!bucket || Number(bucket.age) === 0) return false;
  const confidence = String(bucket.confidence || "").toLowerCase();
  if (/sparse|insufficient|low[_ -]?sample/.test(confidence)) return true;
  return Boolean(bucket.observed) && Number(bucket.sample_count || 0) === 1;
}

function bucketIsUnavailable(bucket) {
  if (!bucket) return true;
  const confidence = String(bucket.confidence || "").toLowerCase();
  return /not[_ -]?manufactured|unavailable|needs_age_zero|needs_collection/.test(confidence) && bucketDisplayValue(bucket) === null;
}

function bucketStatus(bucket) {
  if (!bucket) return { label: "Unavailable", className: "unavailable" };
  if (Number(bucket.age) === 0) return { label: ageZeroLabel(bucket), className: bucketIsProjection(bucket) ? "projected" : "observed" };
  if (bucketIsUnavailable(bucket)) {
    const confidence = String(bucket.confidence || "").toLowerCase();
    return { label: confidence.includes("not_manufactured") ? "Not manufactured" : "Unavailable", className: "unavailable" };
  }
  if (bucketIsSparseProjection(bucket)) {
    return { label: bucket.predicted ? "Insufficient sample → projected" : "Insufficient sample", className: "sparse" };
  }
  if (bucketIsProjection(bucket) && String(bucket.confidence || "").toLowerCase().includes("beyond_model_history")) {
    return { label: "Projection beyond model history", className: "projected" };
  }
  if (bucketIsProjection(bucket) && bucket.generation_adjustment_pct) {
    return { label: "Generation-adjusted forecast", className: "projected" };
  }
  if (bucketIsProjection(bucket)) {
    return { label: Number(bucket.age) > 10 ? "Long-range projection" : "Projected", className: "projected" };
  }
  if (finiteNumber(bucket.trim_normalized_median) !== null) {
    return { label: "Trim-normalized market", className: "observed" };
  }
  return { label: "Observed market", className: "observed" };
}

function bucketDistributionValue(bucket, field) {
  let value = finiteNumber(bucket?.[field]);
  if (value === null) return null;
  const ratio = finiteNumber(bucket?.generation_adjustment_ratio);
  if (bucketIsObservedMarket(bucket) && ratio !== null && ratio > 0 && ratio < 1) value /= ratio;
  if (field === "median" && bucketIsObservedMarket(bucket)) return bucketMarketMedian(bucket) ?? value;
  return value;
}

function bucketSignedPreviousChange(buckets, bucket) {
  if (!bucket) return null;
  const supplied = finiteNumber(bucket.value_change_from_previous);
  if (supplied !== null) return supplied;
  const ordered = [...(buckets || [])].sort((left, right) => Number(left.age) - Number(right.age));
  const index = ordered.indexOf(bucket);
  if (index < 0) return null;
  if (Number(bucket.age) === 0) return 0;
  const current = bucketDisplayValue(bucket);
  const previous = bucketDisplayValue(ordered[index - 1]);
  return current === null || previous === null ? null : current - previous;
}

function bucketSignedPreviousPct(buckets, bucket) {
  if (!bucket) return null;
  const supplied = finiteNumber(bucket.value_change_from_previous_pct);
  if (supplied !== null) return supplied;
  const ordered = [...(buckets || [])].sort((left, right) => Number(left.age) - Number(right.age));
  const index = ordered.indexOf(bucket);
  if (index < 0) return null;
  if (Number(bucket.age) === 0) return 0;
  const current = bucketDisplayValue(bucket);
  const previous = bucketDisplayValue(ordered[index - 1]);
  return current === null || previous === null || previous === 0 ? null : (current - previous) / previous;
}

function bucketSignedBaselineChange(buckets, bucket) {
  if (!bucket) return null;
  const supplied = finiteNumber(bucket.value_change_from_baseline);
  if (supplied !== null) return supplied;
  const baseline = [...(buckets || [])].sort((left, right) => Number(left.age) - Number(right.age))[0];
  const current = bucketDisplayValue(bucket);
  const start = bucketDisplayValue(baseline);
  return current === null || start === null ? null : current - start;
}

function bucketSignedBaselinePct(buckets, bucket) {
  if (!bucket) return null;
  const supplied = finiteNumber(bucket.value_change_from_baseline_pct);
  if (supplied !== null) return supplied;
  const baseline = [...(buckets || [])].sort((left, right) => Number(left.age) - Number(right.age))[0];
  const current = bucketDisplayValue(bucket);
  const start = bucketDisplayValue(baseline);
  return current === null || start === null || start === 0 ? null : (current - start) / start;
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
  chart.setAttribute("viewBox", `0 0 ${width} ${height}`);
  chart.style.minWidth = "";
  const margin = { top: 24, right: 28, bottom: 48, left: 78 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const maxAge = Math.max(1, ...buckets.map((bucket) => Number(bucket.age) || 0));
  const candidates = buckets.flatMap((bucket) => bucketDisplayValue(bucket) === null
    ? []
    : ["high", "q3", "median", "average"].map((field) => bucketDistributionValue(bucket, field)).concat(bucketDisplayValue(bucket)).filter((value) => value !== null));
  const accessibleTitle = `${chartTitle.textContent || "Vehicle"} market value trend`;
  const accessibleDescription = `${candidates.length ? "Observed market and projected value curve" : "No accepted market observations"} across vehicle ages 0 through ${maxAge}.`;
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

  const observedPoints = buckets
    .map((bucket) => ({ bucket, value: bucketDisplayValue(bucket) }))
    .filter((point) => point.value !== null && !bucketIsProjection(point.bucket))
    .map((point) => `${x(point.bucket.age)},${y(point.value)}`);
  const projectedPoints = buckets
    .map((bucket) => ({ bucket, value: bucketDisplayValue(bucket) }))
    .filter((point) => point.value !== null && Number(point.bucket.age) >= firstPredictedAge(buckets) - 1)
    .map((point) => `${x(point.bucket.age)},${y(point.value)}`);
  if (observedPoints.length > 1) {
    svg += `<polyline points="${observedPoints.join(" ")}" fill="none" stroke="${chartColors.observed}" stroke-width="3"></polyline>`;
  }
  if (projectedPoints.length > 1) {
    svg += `<polyline points="${projectedPoints.join(" ")}" fill="none" stroke="${chartColors.projected}" stroke-width="3" stroke-dasharray="8 7"></polyline>`;
  }

  for (const bucket of buckets) {
    const median = bucketDisplayValue(bucket);
    const q1 = bucketDistributionValue(bucket, "q1");
    const q3 = bucketDistributionValue(bucket, "q3");
    const low = bucketDistributionValue(bucket, "low");
    const high = bucketDistributionValue(bucket, "high");
    const average = bucketDistributionValue(bucket, "average") ?? median;
    if ([median, q1, q3, low, high].some((value) => value === null)) continue;
    const cx = x(bucket.age);
    const boxW = bucket.age === 0 ? 14 : 38;
    const projected = bucketIsProjection(bucket);
    const color = projected ? chartColors.projected : chartColors.observed;
    const fill = projected ? chartColors.projectedFill : chartColors.observedFill;
    const lowY = y(low);
    const highY = y(high);
    const q1Y = y(q1);
    const q3Y = y(q3);
    const medY = y(median);
    const avgY = y(average);
    const dash = projected ? `stroke-dasharray="5 5"` : "";
    const status = bucketStatus(bucket).label;
    svg += `<g tabindex="0" role="img" aria-label="Age ${bucket.age}, ${escapeHtml(status)}, median ${escapeHtml(money.format(median))}">`;
    svg += `<title>Age ${bucket.age}: ${money.format(median)} · ${escapeHtml(status)}</title>`;
    svg += `<line x1="${cx}" y1="${highY}" x2="${cx}" y2="${lowY}" stroke="${color}" stroke-width="2" ${dash}></line>`;
    svg += `<line x1="${cx - 12}" y1="${highY}" x2="${cx + 12}" y2="${highY}" stroke="${color}" stroke-width="2" ${dash}></line>`;
    svg += `<line x1="${cx - 12}" y1="${lowY}" x2="${cx + 12}" y2="${lowY}" stroke="${color}" stroke-width="2" ${dash}></line>`;
    svg += `<rect x="${cx - boxW / 2}" y="${q3Y}" width="${boxW}" height="${Math.max(2, q1Y - q3Y)}" rx="4" fill="${fill}" stroke="${color}" stroke-width="2" ${dash}></rect>`;
    svg += `<line x1="${cx - boxW / 2}" y1="${medY}" x2="${cx + boxW / 2}" y2="${medY}" stroke="${chartColors.median}" stroke-width="2"></line>`;
    svg += `<circle cx="${cx}" cy="${avgY}" r="4.5" fill="${chartColors.average}" stroke="${chartColors.background}" stroke-width="1.5"></circle>`;
    if (projected && bucket.generation_adjustment_pct) {
      svg += `<circle cx="${cx}" cy="${medY}" r="9" fill="none" stroke="${chartColors.projected}" stroke-width="2"></circle>`;
    }
    svg += `</g>`;
  }

  chart.innerHTML = svg;
}

function renderComparisonChart(reportA, reportB) {
  const series = [
    { name: reportA.summary.displayName || "Car A", shortName: "Car A", color: chartColors.carA, buckets: reportA.buckets || [] },
    { name: reportB.summary.displayName || "Car B", shortName: "Car B", color: chartColors.carB, buckets: reportB.buckets || [] },
  ];
  const allBuckets = series.flatMap((item) => item.buckets);
  const maxAge = Math.max(1, ...allBuckets.map((bucket) => Number(bucket.age) || 0));
  const width = Math.max(980, 240 + (maxAge * 70));
  const height = 460;
  const margin = { top: 30, right: 32, bottom: 48, left: 82 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const values = allBuckets.map(bucketDisplayValue).filter((value) => value !== null);
  const accessibleTitle = `${series[0].name} and ${series[1].name} value comparison`;
  chart.setAttribute("viewBox", `0 0 ${width} ${height}`);
  chart.style.minWidth = `${width}px`;
  chart.setAttribute("aria-label", accessibleTitle);

  if (!values.length) {
    chart.innerHTML = `<title>${escapeHtml(accessibleTitle)}</title><desc>No accepted market values are available.</desc>
      <rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>
      <text x="${width / 2}" y="${height / 2}" text-anchor="middle" class="emptyChart">No comparable market data yet</text>`;
    return;
  }

  let minValue = Math.max(0, Math.min(...values) * 0.86);
  let maxValue = Math.max(...values) * 1.08;
  if (maxValue <= minValue) {
    const padding = Math.max(1000, maxValue * 0.12);
    minValue = Math.max(0, minValue - padding);
    maxValue += padding;
  }
  const x = (age) => margin.left + (Number(age) / maxAge) * plotW;
  const y = (value) => margin.top + (1 - (value - minValue) / (maxValue - minValue)) * plotH;
  const ageStep = maxAge <= 10 ? 1 : maxAge <= 15 ? 2 : 5;
  let svg = `<title>${escapeHtml(accessibleTitle)}</title><desc>Market and forecast value curves aligned by vehicle age. Solid segments are observed market medians and dashed segments are projections.</desc>`;
  svg += `<rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>`;
  for (const tick of tickValues(minValue, maxValue, 5)) {
    const ty = y(tick);
    svg += `<line x1="${margin.left}" y1="${ty}" x2="${width - margin.right}" y2="${ty}" stroke="${chartColors.grid}"></line>`;
    svg += `<text x="${margin.left - 12}" y="${ty + 4}" text-anchor="end" font-size="12" fill="${chartColors.text}">${money.format(tick)}</text>`;
  }
  for (let age = 0; age <= maxAge; age += ageStep) {
    const tx = x(age);
    svg += `<line x1="${tx}" y1="${margin.top}" x2="${tx}" y2="${height - margin.bottom}" stroke="${chartColors.gridSoft}"></line>`;
    svg += `<text x="${tx}" y="${height - 18}" text-anchor="middle" font-size="12" fill="${chartColors.text}">${age}</text>`;
  }
  svg += `<line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="${chartColors.axis}"></line>`;
  svg += `<text x="${margin.left + plotW / 2}" y="${height - 2}" text-anchor="middle" font-size="12" fill="${chartColors.text}">Vehicle age</text>`;

  for (const item of series) {
    const points = item.buckets
      .map((bucket) => ({ bucket, value: bucketDisplayValue(bucket) }))
      .filter((point) => point.value !== null);
    const firstProjected = firstPredictedAge(item.buckets);
    const observed = points.filter((point) => !bucketIsProjection(point.bucket)).map((point) => `${x(point.bucket.age)},${y(point.value)}`);
    const projected = points.filter((point) => point.bucket.age >= firstProjected - 1).map((point) => `${x(point.bucket.age)},${y(point.value)}`);
    if (observed.length > 1) svg += `<polyline points="${observed.join(" ")}" fill="none" stroke="${item.color}" stroke-width="3"></polyline>`;
    if (projected.length > 1) svg += `<polyline points="${projected.join(" ")}" fill="none" stroke="${item.color}" stroke-width="3" stroke-dasharray="8 7"></polyline>`;
    for (const point of points) {
      const cx = x(point.bucket.age);
      const cy = y(point.value);
      const projectedPoint = bucketIsProjection(point.bucket);
      const dash = projectedPoint ? ' stroke-dasharray="4 3"' : "";
      svg += `<g tabindex="0" role="img" aria-label="${escapeHtml(item.name)}, age ${point.bucket.age}, value ${escapeHtml(money.format(point.value))}">`;
      svg += `<title>${escapeHtml(item.name)} · Age ${point.bucket.age} · ${money.format(point.value)} · ${escapeHtml(bucketStatus(point.bucket).label)}</title>`;
      if (projectedPoint && point.bucket.generation_adjustment_pct) {
        svg += `<circle cx="${cx}" cy="${cy}" r="8" fill="none" stroke="${chartColors.projected}" stroke-width="2"></circle>`;
      }
      svg += `<circle cx="${cx}" cy="${cy}" r="4.5" fill="${chartColors.background}" stroke="${item.color}" stroke-width="2.5"${dash}></circle>`;
      svg += `</g>`;
    }
  }
  chart.innerHTML = svg;
}

function renderDepreciationChart(buckets) {
  const width = 980;
  const height = 420;
  depreciationChart.setAttribute("viewBox", `0 0 ${width} ${height}`);
  depreciationChart.style.minWidth = "";
  const margin = { top: 44, right: 132, bottom: 48, left: 86 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const ordered = [...(buckets || [])].sort((left, right) => Number(left.age) - Number(right.age));
  const points = ordered
    .map((bucket) => ({
      bucket,
      age: Number(bucket.age) || 0,
      change: bucketSignedPreviousChange(ordered, bucket),
      pct: bucketSignedBaselinePct(ordered, bucket),
      projected: bucketIsProjection(bucket)
    }))
    .filter((point) => point.change !== null && point.pct !== null);
  const accessibleTitle = `${chartTitle.textContent || "Vehicle"} annual value movement and signed change from baseline`;
  const accessibleDescription = `${points.length ? "Year-over-year appreciation or depreciation and signed percentage change" : "No value baseline available"} across the selected vehicle-age horizon.`;
  depreciationChart.setAttribute("aria-label", accessibleTitle);

  if (points.length < 2) {
    depreciationChart.innerHTML = `<title>${escapeHtml(accessibleTitle)}</title><desc>${escapeHtml(accessibleDescription)}</desc>
      <rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>
      <text x="${width / 2}" y="${height / 2 - 8}" text-anchor="middle" class="emptyChart">No value movement data yet</text>
      <text x="${width / 2}" y="${height / 2 + 22}" text-anchor="middle" font-size="13" fill="${chartColors.text}">Waiting for an Age 0 market baseline.</text>`;
    return;
  }

  const maxAge = Math.max(1, ...points.map((point) => point.age));
  const [minChange, maxChange] = paddedSignedDomain(points.map((point) => point.change), 1000);
  const [minPct, maxPct] = paddedSignedDomain(points.map((point) => point.pct), 0.01);
  const xMax = maxAge + 0.65;
  const x = (age) => margin.left + (age / xMax) * plotW;
  const yChange = (value) => margin.top + (1 - (value - minChange) / (maxChange - minChange)) * plotH;
  const yPct = (value) => margin.top + (1 - (value - minPct) / (maxPct - minPct)) * plotH;
  const zeroY = yChange(0);
  const dollarTicks = signedTickValues(minChange, maxChange, 5);
  const pctTicks = signedTickValues(minPct, maxPct, 5);
  const ageStep = maxAge <= 10 ? 1 : maxAge <= 15 ? 2 : 5;
  const barW = Math.min(40, Math.max(12, plotW / Math.max(points.length * 1.8, 1)));

  let svg = `<title>${escapeHtml(accessibleTitle)}</title><desc>${escapeHtml(accessibleDescription)}</desc>`;
  svg += `<rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>`;
  for (const tick of dollarTicks) {
    const ty = yChange(tick);
    svg += `<line x1="${margin.left}" y1="${ty}" x2="${width - margin.right}" y2="${ty}" stroke="${chartColors.grid}"></line>`;
    svg += `<text x="${margin.left - 12}" y="${ty + 4}" text-anchor="end" font-size="12" fill="${chartColors.text}">${fmtSignedMoney(tick)}</text>`;
  }
  for (const tick of pctTicks) {
    const ty = yPct(tick);
    svg += `<text x="${width - margin.right + 16}" y="${ty + 4}" text-anchor="start" font-size="12" fill="${chartColors.text}">${fmtSignedPct(tick)}</text>`;
  }
  for (let age = 0; age <= maxAge; age += ageStep) {
    const tx = x(age);
    svg += `<line x1="${tx}" y1="${margin.top}" x2="${tx}" y2="${margin.top + plotH}" stroke="${chartColors.gridSoft}"></line>`;
    svg += `<text x="${tx}" y="${height - 18}" text-anchor="middle" font-size="12" fill="${chartColors.text}">${age}</text>`;
  }
  svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${margin.top + plotH}" stroke="${chartColors.axis}"></line>`;
  svg += `<line x1="${width - margin.right}" y1="${margin.top}" x2="${width - margin.right}" y2="${margin.top + plotH}" stroke="${chartColors.axis}"></line>`;
  svg += `<line x1="${margin.left}" y1="${zeroY}" x2="${width - margin.right}" y2="${zeroY}" stroke="${chartColors.axis}" stroke-width="2"></line>`;
  svg += `<text x="${margin.left + plotW / 2}" y="${height - 2}" text-anchor="middle" font-size="12" fill="${chartColors.text}">Vehicle age</text>`;
  svg += `<text transform="translate(18 ${margin.top + plotH / 2}) rotate(-90)" text-anchor="middle" font-size="12" fill="${chartColors.text}">YoY value change</text>`;
  svg += `<text transform="translate(${width - 20} ${margin.top + plotH / 2}) rotate(90)" text-anchor="middle" font-size="12" fill="${chartColors.text}">Change from Age 0 %</text>`;

  for (const point of points) {
    const cx = x(point.age);
    const changeY = yChange(point.change);
    const top = Math.min(changeY, zeroY);
    const fill = point.change > 0 ? chartColors.appreciationFill : point.change < 0 ? chartColors.depreciationFill : chartColors.gridSoft;
    const stroke = point.projected ? chartColors.projected : point.change > 0 ? chartColors.appreciation : chartColors.depreciation;
    const dash = point.projected ? ' stroke-dasharray="5 4"' : "";
    svg += `<g tabindex="0" role="img" aria-label="Age ${point.age}, ${escapeHtml(movementDescription(point.change))}, ${escapeHtml(fmtSignedPct(point.pct))} from Age 0">`;
    svg += `<title>Age ${point.age}: ${escapeHtml(movementDescription(point.change))} · ${fmtSignedPct(point.pct)} from Age 0</title>`;
    svg += `<rect x="${cx - barW / 2}" y="${top}" width="${barW}" height="${Math.max(1, Math.abs(zeroY - changeY))}" rx="4" fill="${fill}" stroke="${stroke}" stroke-width="1.5"${dash}></rect>`;
    svg += `</g>`;
  }

  const firstProjected = firstPredictedAge(buckets);
  const pctObserved = points.filter((point) => !point.projected).map((point) => `${x(point.age)},${yPct(point.pct)}`);
  const pctProjected = points.filter((point) => point.age >= firstProjected - 1).map((point) => `${x(point.age)},${yPct(point.pct)}`);
  if (pctObserved.length > 1) {
    svg += `<polyline points="${pctObserved.join(" ")}" fill="none" stroke="${chartColors.percent}" stroke-width="3"></polyline>`;
  }
  if (pctProjected.length > 1) {
    svg += `<polyline points="${pctProjected.join(" ")}" fill="none" stroke="${chartColors.projected}" stroke-width="3" stroke-dasharray="8 7"></polyline>`;
  }
  for (const point of points) {
    const stroke = point.projected ? chartColors.projected : chartColors.percent;
    const cx = x(point.age);
    const cy = yPct(point.pct);
    const labelY = point.pct >= 0 ? Math.max(14, cy - 12) : Math.min(height - margin.bottom + 18, cy + 18);
    svg += `<text x="${cx}" y="${labelY}" text-anchor="middle" font-size="11" font-weight="760" fill="${stroke}">${fmtSignedPct(point.pct)}</text>`;
    svg += `<circle cx="${cx}" cy="${cy}" r="4.5" fill="${chartColors.background}" stroke="${stroke}" stroke-width="2"></circle>`;
  }

  depreciationChart.innerHTML = svg;
}

function renderComparisonDepreciationChart(reportA, reportB) {
  const series = [
    { name: reportA.summary.displayName || "Car A", shortName: "A", color: chartColors.carA, fill: chartColors.carAFill, buckets: reportA.buckets || [] },
    { name: reportB.summary.displayName || "Car B", shortName: "B", color: chartColors.carB, fill: chartColors.carBFill, buckets: reportB.buckets || [] },
  ].map((item) => ({
    ...item,
    points: item.buckets.map((bucket) => ({
      bucket,
      age: Number(bucket.age) || 0,
      change: bucketSignedPreviousChange(item.buckets, bucket),
      pct: bucketSignedBaselinePct(item.buckets, bucket),
      projected: bucketIsProjection(bucket),
    })).filter((point) => point.change !== null && point.pct !== null)
  }));
  const allPoints = series.flatMap((item) => item.points);
  const maxAge = Math.max(1, ...allPoints.map((point) => point.age));
  const width = Math.max(980, 240 + (maxAge * 78));
  const height = 440;
  const margin = { top: 62, right: 132, bottom: 48, left: 88 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const accessibleTitle = `${series[0].name} and ${series[1].name} signed value movement comparison`;
  depreciationChart.setAttribute("viewBox", `0 0 ${width} ${height}`);
  depreciationChart.style.minWidth = `${width}px`;
  depreciationChart.setAttribute("aria-label", accessibleTitle);

  if (allPoints.length < 2) {
    depreciationChart.innerHTML = `<title>${escapeHtml(accessibleTitle)}</title><desc>No comparable value baseline is available.</desc>
      <rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>
      <text x="${width / 2}" y="${height / 2}" text-anchor="middle" class="emptyChart">No comparable value movement yet</text>`;
    return;
  }

  const [minChange, maxChange] = paddedSignedDomain(allPoints.map((point) => point.change), 1000);
  const [minPct, maxPct] = paddedSignedDomain(allPoints.map((point) => point.pct), 0.01);
  const xMax = maxAge + 0.7;
  const x = (age) => margin.left + (Number(age) / xMax) * plotW;
  const yChange = (value) => margin.top + (1 - (value - minChange) / (maxChange - minChange)) * plotH;
  const yPct = (value) => margin.top + (1 - (value - minPct) / (maxPct - minPct)) * plotH;
  const zeroY = yChange(0);
  const ageStep = maxAge <= 10 ? 1 : maxAge <= 15 ? 2 : 5;
  const slotWidth = plotW / Math.max(maxAge + 1, 1);
  const barWidth = Math.min(28, Math.max(10, slotWidth * 0.28));
  const barGap = 3;
  let svg = `<title>${escapeHtml(accessibleTitle)}</title><desc>Grouped signed bars compare year-over-year value movement. Colored lines and labeled dots compare signed change from each Age 0 baseline.</desc>`;
  svg += `<rect x="0" y="0" width="${width}" height="${height}" fill="${chartColors.background}"></rect>`;
  for (const tick of signedTickValues(minChange, maxChange, 5)) {
    const ty = yChange(tick);
    svg += `<line x1="${margin.left}" y1="${ty}" x2="${width - margin.right}" y2="${ty}" stroke="${chartColors.grid}"></line>`;
    svg += `<text x="${margin.left - 12}" y="${ty + 4}" text-anchor="end" font-size="12" fill="${chartColors.text}">${fmtSignedMoney(tick)}</text>`;
  }
  for (const tick of signedTickValues(minPct, maxPct, 5)) {
    const ty = yPct(tick);
    svg += `<text x="${width - margin.right + 16}" y="${ty + 4}" text-anchor="start" font-size="12" fill="${chartColors.text}">${fmtSignedPct(tick)}</text>`;
  }
  for (let age = 0; age <= maxAge; age += ageStep) {
    const tx = x(age);
    svg += `<line x1="${tx}" y1="${margin.top}" x2="${tx}" y2="${margin.top + plotH}" stroke="${chartColors.gridSoft}"></line>`;
    svg += `<text x="${tx}" y="${height - 18}" text-anchor="middle" font-size="12" fill="${chartColors.text}">${age}</text>`;
  }
  svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${margin.top + plotH}" stroke="${chartColors.axis}"></line>`;
  svg += `<line x1="${width - margin.right}" y1="${margin.top}" x2="${width - margin.right}" y2="${margin.top + plotH}" stroke="${chartColors.axis}"></line>`;
  svg += `<line x1="${margin.left}" y1="${zeroY}" x2="${width - margin.right}" y2="${zeroY}" stroke="${chartColors.axis}" stroke-width="2"></line>`;
  svg += `<text x="${margin.left + plotW / 2}" y="${height - 2}" text-anchor="middle" font-size="12" fill="${chartColors.text}">Vehicle age</text>`;
  svg += `<text transform="translate(18 ${margin.top + plotH / 2}) rotate(-90)" text-anchor="middle" font-size="12" fill="${chartColors.text}">YoY value change</text>`;
  svg += `<text transform="translate(${width - 20} ${margin.top + plotH / 2}) rotate(90)" text-anchor="middle" font-size="12" fill="${chartColors.text}">Change from Age 0 %</text>`;

  series.forEach((item, seriesIndex) => {
    for (const point of item.points) {
      const cx = x(point.age) + (seriesIndex === 0 ? -(barWidth + barGap) / 2 : (barWidth + barGap) / 2);
      const changeY = yChange(point.change);
      const top = Math.min(changeY, zeroY);
      const dash = point.projected ? ' stroke-dasharray="5 4"' : "";
      svg += `<g tabindex="0" role="img" aria-label="${escapeHtml(item.name)}, age ${point.age}, ${escapeHtml(movementDescription(point.change))}, ${escapeHtml(fmtSignedPct(point.pct))} from Age 0">`;
      svg += `<title>${escapeHtml(item.name)} · Age ${point.age} · ${escapeHtml(movementDescription(point.change))} · ${fmtSignedPct(point.pct)} from Age 0</title>`;
      svg += `<rect x="${cx - barWidth / 2}" y="${top}" width="${barWidth}" height="${Math.max(1, Math.abs(zeroY - changeY))}" rx="3" fill="${item.fill}" stroke="${item.color}" stroke-width="1.5"${dash}></rect>`;
      svg += `</g>`;
    }
    const firstProjected = firstPredictedAge(item.buckets);
    const observed = item.points.filter((point) => !point.projected).map((point) => `${x(point.age)},${yPct(point.pct)}`);
    const projected = item.points.filter((point) => point.age >= firstProjected - 1).map((point) => `${x(point.age)},${yPct(point.pct)}`);
    if (observed.length > 1) svg += `<polyline points="${observed.join(" ")}" fill="none" stroke="${item.color}" stroke-width="3"></polyline>`;
    if (projected.length > 1) svg += `<polyline points="${projected.join(" ")}" fill="none" stroke="${item.color}" stroke-width="3" stroke-dasharray="8 7"></polyline>`;
  });

  const pointsByAge = series.map((item) => new Map(item.points.map((point) => [point.age, point])));
  for (let age = 0; age <= maxAge; age += 1) {
    const pointA = pointsByAge[0].get(age);
    const pointB = pointsByAge[1].get(age);
    if (age === 0 && (pointA || pointB)) {
      const cy = yPct(0);
      svg += `<text x="${x(0)}" y="${cy - 13}" text-anchor="middle" font-size="11" font-weight="760" fill="${chartColors.text}">0% baseline</text>`;
    }
    [pointA, pointB].forEach((point, seriesIndex) => {
      if (!point) return;
      const item = series[seriesIndex];
      const cx = x(age);
      const cy = yPct(point.pct);
      const otherPoint = seriesIndex === 0 ? pointB : pointA;
      const otherY = otherPoint ? yPct(otherPoint.pct) : null;
      const close = otherY !== null && Math.abs(cy - otherY) < 22;
      const closeAnchor = close ? Math.min(cy, otherY) : cy;
      const labelY = age === 0 ? null : Math.max(16, closeAnchor - (close ? (seriesIndex === 0 ? 12 : 31) : 12));
      const dash = point.projected ? ' stroke-dasharray="4 3"' : "";
      if (labelY !== null) {
        svg += `<text x="${cx}" y="${labelY}" text-anchor="middle" font-size="10.5" font-weight="760" fill="${item.color}" stroke="${chartColors.background}" stroke-width="3" paint-order="stroke">${item.shortName} ${fmtSignedPct(point.pct)}</text>`;
      }
      svg += `<circle cx="${cx}" cy="${cy}" r="4.5" fill="${chartColors.background}" stroke="${item.color}" stroke-width="2.5"${dash}></circle>`;
    });
  }
  depreciationChart.innerHTML = svg;
}

function renderPlan(plan) {
  collectionPlan.innerHTML = planMarkup(plan);
}

function planMarkup(plan) {
  if (!plan?.targets?.length) return '<p class="mutedText">No collection plan is available.</p>';
  return plan.targets
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
      const status = bucketStatus(bucket);
      const previousChange = bucketSignedPreviousChange(buckets, bucket);
      const previousPct = bucketSignedPreviousPct(buckets, bucket);
      const baselineChange = bucketSignedBaselineChange(buckets, bucket);
      const baselinePct = bucketSignedBaselinePct(buckets, bucket);
      return `<tr>
        <td>Age ${bucket.age}</td>
        <td>${bucket.model_year ?? ""}</td>
        <td>${bucket.forecast_year ?? ""}</td>
        <td><span class="badge ${status.className}">${escapeHtml(status.label)}</span></td>
        <td>${bucket.sample_count}</td>
        <td>${fmtMoney(bucketDistributionValue(bucket, "average"))}</td>
        <td>${fmtMoney(bucketMarketMedian(bucket))}</td>
        <td>${fmtMoney(bucketDisplayValue(bucket))}</td>
        <td>${fmtMoney(bucketDistributionValue(bucket, "q1"))}</td>
        <td>${fmtMoney(bucketDistributionValue(bucket, "q3"))}</td>
        <td>${movementMarkup(previousChange)}</td>
        <td>${movementPercentMarkup(previousPct)}</td>
        <td>${movementMarkup(baselineChange)}</td>
        <td>${movementPercentMarkup(baselinePct)}</td>
        <td>${Number(bucket.outlier_count || 0).toLocaleString()}</td>
        <td>${renderGenerationCell(bucket)}</td>
      </tr>`;
    })
    .join("");
}

function renderComparisonTable(reportA, reportB) {
  const nameA = reportA.summary.displayName || "Car A";
  const nameB = reportB.summary.displayName || "Car B";
  const maxAge = Math.max(Number(reportA.summary.maxAge || 0), Number(reportB.summary.maxAge || 0), 1);
  bucketTable.classList.add("comparisonTable");
  bucketTableHead.innerHTML = `<tr>
      <th scope="col" rowspan="2">Age</th>
      <th scope="colgroup" colspan="4" class="vehicleGroup carA">${escapeHtml(nameA)}</th>
      <th scope="colgroup" colspan="4" class="vehicleGroup carB">${escapeHtml(nameB)}</th>
      <th scope="col" rowspan="2">Difference</th>
    </tr>
    <tr>
      <th scope="col">Market Median</th><th scope="col">Curve Value</th><th scope="col">Since Age 0</th><th scope="col">Change %</th>
      <th scope="col">Market Median</th><th scope="col">Curve Value</th><th scope="col">Since Age 0</th><th scope="col">Change %</th>
    </tr>`;
  rows.innerHTML = Array.from({ length: maxAge + 1 }, (_, age) => {
    const bucketA = bucketAtAge(reportA, age);
    const bucketB = bucketAtAge(reportB, age);
    return `<tr>
      <td>Age ${age}</td>
      <td>${fmtMoney(bucketMarketMedian(bucketA))}</td>
      <td>${fmtMoney(bucketDisplayValue(bucketA))}</td>
      <td>${movementMarkup(bucketSignedBaselineChange(reportA.buckets, bucketA))}</td>
      <td>${movementPercentMarkup(bucketSignedBaselinePct(reportA.buckets, bucketA))}</td>
      <td>${fmtMoney(bucketMarketMedian(bucketB))}</td>
      <td>${fmtMoney(bucketDisplayValue(bucketB))}</td>
      <td>${movementMarkup(bucketSignedBaselineChange(reportB.buckets, bucketB))}</td>
      <td>${movementPercentMarkup(bucketSignedBaselinePct(reportB.buckets, bucketB))}</td>
      <td class="differenceCell">${comparisonDifference(reportA, bucketA, reportB, bucketB, nameA, nameB)}</td>
    </tr>`;
  }).join("");
}

function comparisonDifference(reportA, bucketA, reportB, bucketB, nameA, nameB) {
  const pctA = bucketSignedBaselinePct(reportA.buckets, bucketA);
  const pctB = bucketSignedBaselinePct(reportB.buckets, bucketB);
  if (pctA === null || pctB === null) return "-";
  const difference = Math.abs(pctA - pctB);
  if (difference < 0.0005) return "Equal value retention";
  const strongerName = pctA > pctB ? nameA : nameB;
  return `<strong>${escapeHtml(strongerName)}</strong> retained ${fmtPoints(difference)} more value`;
}

function renderGenerationCell(bucket) {
  if (!bucket.generation_adjustment_pct) return "";
  const label = bucket.generation_adjustment_label || "Generation adjustment";
  const basis = bucket.generation_adjustment_basis || "";
  const ratio = bucket.generation_adjustment_ratio ? ` · x${Number(bucket.generation_adjustment_ratio).toFixed(2)}` : "";
  const year = bucket.generation_adjustment_year ? ` · ${bucket.generation_adjustment_year}` : "";
  const original = bucket.generation_unadjusted_median ? `Before adjustment: ${fmtMoney(bucket.generation_unadjusted_median)}. ` : "";
  const scope = bucketIsProjection(bucket) ? "Forecast only" : "Legacy overlay; raw market median retained";
  return `<span class="impactBadge" title="${escapeHtml(`${scope}. ${original}${basis}`)}">${escapeHtml(scope)} · -${fmtPct(bucket.generation_adjustment_pct)} · ${escapeHtml(label)}${escapeHtml(ratio)}${escapeHtml(year)}</span>`;
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
    <span>Forecast scenario only. Observed market medians remain unadjusted source summaries.</span>
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
  sourceEvidence.innerHTML = evidenceMarkup(evidence);
}

function evidenceMarkup(evidence) {
  const sourceRows = evidence.sources || [];
  const collectorSources = evidence.collectorSources || [];
  const facets = evidence.facets || [];
  const listings = evidence.listings || [];
  const notes = evidence.collectorNotes || [];

  if (!sourceRows.length && !collectorSources.length && !facets.length && !listings.length) {
    return `<p class="mutedText">No source evidence yet.</p>`;
  }

  return `
    ${notes.length ? `<div class="evidenceNotes">${notes.map((note) => `<p>${escapeHtml(note)}</p>`).join("")}</div>` : ""}
    <details open class="evidenceGroup">
      <summary>Source Pages (${sourceRows.length || collectorSources.length})</summary>
      <div class="evidenceSources">
        ${renderSourceRows(sourceRows, collectorSources)}
      </div>
    </details>
    <details open class="evidenceGroup">
      <summary>Raw Source Snapshots (${facets.length})</summary>
      ${facets.length ? `<p class="mutedText evidenceDefinition">Each row is one source and condition before combination. Found counts weight the aggregate market calculation; the comparison table shows the combined market median and any generation-adjusted curve value separately.</p>${renderFacetTable(facets)}` : `<p class="mutedText">No raw facet snapshots were returned for this run.</p>`}
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
          ${collector?.browser_verified ? `<span>Verified browser audit · ${Number(collector.pages_examined || 0)} pages · ${Number(collector.cards_examined || 0)} cards · ${Number(collector.accepted || 0)} accepted${collector.detail_pages_opened ? ` · ${Number(collector.detail_pages_opened)} detail checks` : ""}</span>` : ""}
          ${collector?.rejected_by_reason && Object.keys(collector.rejected_by_reason).length ? `<span>Rejected: ${escapeHtml(formatCounts(collector.rejected_by_reason))}</span>` : ""}
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
          <th scope="col">Raw Median</th>
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
          <th scope="col">Represents</th>
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
          <td>${Number(item.market_weight || 1).toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
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

function paddedSignedDomain(values, minimumSpan) {
  const finite = (values || []).map(finiteNumber).filter((value) => value !== null);
  if (!finite.length) return [-minimumSpan, minimumSpan];
  let minimum = Math.min(0, ...finite);
  let maximum = Math.max(0, ...finite);
  if (minimum === maximum) return [-minimumSpan, minimumSpan];
  const padding = Math.max(minimumSpan * 0.1, (maximum - minimum) * 0.1);
  if (minimum < 0) minimum -= padding;
  if (maximum > 0) maximum += padding;
  if (maximum - minimum < minimumSpan) {
    const extra = (minimumSpan - (maximum - minimum)) / 2;
    minimum -= extra;
    maximum += extra;
  }
  return [minimum, maximum];
}

function signedTickValues(minimum, maximum, count) {
  const span = maximum - minimum;
  const step = niceNumber(span / Math.max(2, count - 1));
  const ticks = [];
  for (let value = Math.ceil(minimum / step) * step; value <= maximum + step * 0.01; value += step) {
    ticks.push(Number(value.toFixed(8)));
  }
  if (minimum <= 0 && maximum >= 0 && !ticks.some((value) => Math.abs(value) < step * 0.001)) ticks.push(0);
  return uniqueNumbers(ticks).sort((left, right) => left - right);
}

function niceNumber(value) {
  const exponent = Math.floor(Math.log10(value));
  const fraction = value / Math.pow(10, exponent);
  const niceFraction = fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 5 ? 5 : 10;
  return niceFraction * Math.pow(10, exponent);
}

function firstPredictedAge(buckets) {
  const found = (buckets || []).find(bucketIsProjection);
  return found ? Number(found.age) : Number.POSITIVE_INFINITY;
}

function fmtMoney(value) {
  return value == null ? "" : money.format(value);
}

function fmtPct(value) {
  return value == null ? "" : `${(value * 100).toFixed(1)}%`;
}

function fmtSignedMoney(value) {
  const number = finiteNumber(value);
  if (number === null) return "";
  if (Math.abs(number) < 0.005) return money.format(0);
  return `${number > 0 ? "+" : "-"}${money.format(Math.abs(number))}`;
}

function fmtSignedPct(value) {
  const number = finiteNumber(value);
  if (number === null) return "";
  if (Math.abs(number) < 0.00005) return "0.0%";
  return `${number > 0 ? "+" : "-"}${(Math.abs(number) * 100).toFixed(1)}%`;
}

function movementDescription(value) {
  const number = finiteNumber(value);
  if (number === null) return "No comparable value";
  if (Math.abs(number) < 0.005) return "No value change";
  return `${money.format(Math.abs(number))} ${number > 0 ? "appreciation" : "depreciation"}`;
}

function movementMarkup(value) {
  const number = finiteNumber(value);
  if (number === null) return "";
  const className = number > 0.005 ? "appreciation" : number < -0.005 ? "depreciation" : "flat";
  const label = className === "appreciation" ? "appreciation" : className === "depreciation" ? "depreciation" : "no change";
  return `<span class="movement ${className}">${fmtSignedMoney(number)}<small>${label}</small></span>`;
}

function movementPercentMarkup(value) {
  const number = finiteNumber(value);
  if (number === null) return "";
  const className = number > 0.00005 ? "appreciation" : number < -0.00005 ? "depreciation" : "flat";
  return `<span class="movement ${className}">${fmtSignedPct(number)}</span>`;
}

function fmtPoints(value) {
  return `${(Number(value) * 100).toFixed(1)} pts`;
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
