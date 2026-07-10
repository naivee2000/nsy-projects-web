const form = document.querySelector("#jobForm");
const input = document.querySelector("#pdfFiles");
const fileList = document.querySelector("#fileList");
const statusBox = document.querySelector("#status");
const downloadLink = document.querySelector("#downloadLink");
const scanBtn = document.querySelector("#scanBtn");
const referenceList = document.querySelector("#referenceList");
const capabilityList = document.querySelector("#capabilityList");
const jobList = document.querySelector("#jobList");

function badge(text, status) {
  const item = document.createElement("span");
  item.className = `badge badge-${status}`;
  item.textContent = text;
  return item;
}

function renderFiles() {
  fileList.innerHTML = "";
  for (const file of input.files) {
    const item = document.createElement("div");
    item.className = "file-pill";
    item.textContent = file.name;
    fileList.appendChild(item);
  }
}

async function scanReferences() {
  referenceList.innerHTML = "";
  statusBox.textContent = "Scanning reference PDFs...";
  const response = await fetch("/api/reference-pdfs");
  const data = await response.json();
  for (const item of data.items) {
    const card = document.createElement("article");
    card.className = "reference-card";
    const title = document.createElement("strong");
    title.textContent = item.path;
    const meta = document.createElement("span");
    const project = item.project_id ? ` · ${item.project_id}` : "";
    meta.textContent = `${item.kind}${project} · ${item.pages ?? "?"} pages · ${item.size_mb} MB`;
    card.append(title, meta, badge(item.support.status, item.support.status));
    referenceList.appendChild(card);
  }
  statusBox.textContent = `Found ${data.items.length} reference PDFs.`;
}

async function loadCapabilities() {
  capabilityList.innerHTML = "";
  const response = await fetch("/api/capabilities");
  const data = await response.json();
  for (const [generatorId, details] of Object.entries(data.supported_generators || {})) {
    const row = document.createElement("div");
    row.className = "capability-row";
    row.append(badge(generatorId, "supported"), document.createTextNode(details.description));
    capabilityList.appendChild(row);
  }
  for (const [modelId, details] of Object.entries(data.supported_sensor_models || {})) {
    const row = document.createElement("div");
    row.className = "capability-row";
    row.append(badge(modelId, "supported"), document.createTextNode(`${details.name_en} · ${details.signal}`));
    capabilityList.appendChild(row);
  }
  for (const [projectId, details] of Object.entries(data.supported_projects)) {
    const row = document.createElement("div");
    row.className = "capability-row";
    row.append(badge(projectId, "supported"), document.createTextNode(details.description));
    capabilityList.appendChild(row);
  }
  for (const [projectId, reason] of Object.entries(data.known_unsupported_projects)) {
    const row = document.createElement("div");
    row.className = "capability-row";
    row.append(badge(projectId, "known-unsupported"), document.createTextNode(reason));
    capabilityList.appendChild(row);
  }
  const setupResponse = await fetch("/api/setup");
  const setup = await setupResponse.json();
  const codex = setup.codex || {};
  const codexRow = document.createElement("div");
  codexRow.className = "capability-row";
  const codexState = codex.ready ? "supported" : "unknown";
  const codexLabel = codex.ready ? "Codex ready" : (codex.enabled ? "Codex unavailable" : "Codex optional");
  const codexDetail = codex.ready
    ? `Server-side advisory · ${codex.auth_method || "saved login"}`
    : (codex.message || "Enable AUTO_CAD_CODEX_ADVISORY on the deployment host.");
  codexRow.append(badge(codexLabel, codexState), document.createTextNode(codexDetail));
  capabilityList.appendChild(codexRow);
}

async function loadJobs() {
  const response = await fetch("/api/jobs");
  const data = await response.json();
  jobList.innerHTML = "";
  for (const job of data.jobs.slice(0, 5)) {
    const item = document.createElement("div");
    item.className = "job-row";
    const left = document.createElement("span");
    left.textContent = `${job.job} · ${job.project_id || job.analysis?.project_id || "no project"} · ${job.status}`;
    item.append(left);
    if (job.download_available) {
      const link = document.createElement("a");
      link.href = job.download_url;
      link.textContent = "ZIP";
      item.append(link);
    }
    jobList.appendChild(item);
  }
}

input.addEventListener("change", renderFiles);
scanBtn.addEventListener("click", () => {
  scanReferences().catch((error) => {
    statusBox.textContent = `Scan failed: ${error}`;
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  downloadLink.hidden = true;
  statusBox.textContent = "Generating CAD outputs...";
  const body = new FormData(form);
  const response = await fetch("/api/jobs", {
    method: "POST",
    body,
  });
  if (!response.ok) {
    let message = await response.text();
    try {
      const payload = JSON.parse(message);
      const deterministic = payload.detail?.analysis?.message || payload.detail?.message || message;
      const advisory = payload.detail?.codex_advisory;
      message = advisory?.status === "analyzed"
        ? `${deterministic}\nCodex advisory: ${advisory.summary}\nNext: ${advisory.recommended_next_step}`
        : (advisory ? `${deterministic}\nCodex advisory unavailable: ${advisory.summary}` : deterministic);
    } catch {
      // Keep raw message.
    }
    statusBox.textContent = `Generation unavailable: ${message}`;
    return;
  }
  const data = await response.json();
  downloadLink.href = data.download_url;
  downloadLink.hidden = false;
  const checks = data.manifest.verification.slice(0, 5).join("\n");
  statusBox.textContent = `Job ${data.job} complete.\n${checks}`;
  await loadJobs();
});

loadCapabilities().catch(() => {});
scanReferences().catch(() => {});
loadJobs().catch(() => {});
