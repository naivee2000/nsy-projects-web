const jobSelect = document.querySelector("#actionJobId");
const sourceSelect = document.querySelector("#actionSource");
const urlInput = document.querySelector("#actionUrl");
const textInput = document.querySelector("#actionVisibleText");
const pagesInput = document.querySelector("#actionPages");
const cardsInput = document.querySelector("#actionCards");
const clicksInput = document.querySelector("#actionClicks");
const form = document.querySelector("#captureImportForm");
const submitButton = document.querySelector("#actionSubmit");
const context = document.querySelector("#actionContext");
const status = document.querySelector("#actionStatus");

let actions = [];
const SOURCE_LABELS = {
  autotrader_browser: "Autotrader",
  edmunds_browser: "Edmunds",
  porsche_finder_browser: "Porsche Finder",
};

function selectedAction() {
  return actions.find((item) => item.jobId === jobSelect.value) || null;
}

function renderSources(preferredSource = "") {
  const action = selectedAction();
  sourceSelect.replaceChildren();
  for (const item of action?.sources || []) {
    const option = document.createElement("option");
    option.value = item.source;
    option.textContent = SOURCE_LABELS[item.source] || item.source;
    option.dataset.url = item.url;
    sourceSelect.append(option);
  }
  if (preferredSource && [...sourceSelect.options].some((option) => option.value === preferredSource)) {
    sourceSelect.value = preferredSource;
  }
  renderUrl();
  context.textContent = action ? `${action.query} · ${action.maxAge}-year horizon` : "No blocked marketplace captures are waiting.";
}

function renderUrl() {
  document.querySelector("#actionScopeVerified").checked = false;
  urlInput.value = sourceSelect.selectedOptions[0]?.dataset.url || "";
}

async function loadActions() {
  const response = await fetch("/api/codex-browser-actions", { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`Could not load browser actions (${response.status}).`);
  actions = (await response.json()).actions || [];
  const params = new URLSearchParams(location.search);
  const preferredJob = params.get("jobId") || "";
  const preferredSource = params.get("source") || "";
  jobSelect.replaceChildren();
  for (const action of actions) {
    const option = document.createElement("option");
    option.value = action.jobId;
    option.textContent = `${action.query} · ${action.jobId.slice(0, 8)}`;
    jobSelect.append(option);
  }
  if (preferredJob && actions.some((item) => item.jobId === preferredJob)) jobSelect.value = preferredJob;
  renderSources(preferredSource);
  submitButton.disabled = actions.length === 0;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submitButton.disabled = true;
  status.className = "actionStatus";
  status.textContent = "Importing and validating visible listing rows...";
  try {
    const response = await fetch("/api/codex-browser-capture", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        jobId: jobSelect.value,
        source: sourceSelect.value,
        url: urlInput.value,
        visibleText: textInput.value,
        pagesExamined: Number(pagesInput.value),
        cardsExamined: Number(cardsInput.value),
        loadMoreClicked: Number(clicksInput.value),
        scope: {
          validation_revision: 3,
          validation_status: document.querySelector("#actionScopeVerified").checked ? "verified" : "unverified",
          geography: "nationwide",
          query_key: selectedAction()?.queryKey,
          requested_scope: selectedAction()?.requestedScope,
          result_refresh_confirmed: document.querySelector("#actionScopeVerified").checked,
          verification_method: "supervised_visible_controls",
          captured_at: Date.now() / 1000,
          complete: true,
        },
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `Import failed (${response.status}).`);
    status.className = "actionStatus success";
    status.textContent = `${payload.accepted} exact rows accepted from ${payload.source}.`;
    textInput.value = "";
    await loadActions();
  } catch (error) {
    status.className = "actionStatus error";
    status.textContent = error.message || String(error);
  } finally {
    submitButton.disabled = actions.length === 0;
  }
});

jobSelect.addEventListener("change", () => renderSources());
sourceSelect.addEventListener("change", renderUrl);

loadActions().catch((error) => {
  status.className = "actionStatus error";
  status.textContent = error.message || String(error);
  submitButton.disabled = true;
});
