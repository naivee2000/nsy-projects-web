#!/usr/bin/env node

import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { chromium } from "playwright";
import * as z from "zod/v4";

const ALLOWED_HOSTS = [
  "autotrader.com",
  "cars.com",
  "cargurus.com",
  "edmunds.com",
  "finder.porsche.com",
  "bmwusa.com",
  "visor.vin",
];
const DEFAULT_MAX_PAGES = 5;
const MAX_PAGES = 5;
const DEFAULT_TIMEOUT_MS = 12 * 60 * 1000;
const SOURCE_HOSTS = {
  autotrader_browser: "autotrader.com",
  edmunds_browser: "edmunds.com",
  porsche_finder_browser: "finder.porsche.com",
};

export function normalizeInput(input, defaultDeadline = Date.now() / 1000 + DEFAULT_TIMEOUT_MS / 1000) {
  const deadline = input.deadline_at == null ? defaultDeadline : Number(input.deadline_at);
  if (!Number.isFinite(deadline) || deadline <= 0) throw new Error("deadline_at must be UNIX seconds.");
  return { ...input, max_pages: Math.max(1, Math.min(MAX_PAGES, Math.floor(Number(input.max_pages) || DEFAULT_MAX_PAGES))), deadline_at: deadline };
}

export class Deadline {
  constructor(at) { this.at = at * 1000; }
  timeout(cap = DEFAULT_TIMEOUT_MS) {
    const remaining = Math.floor(this.at - Date.now());
    if (remaining <= 0) throw new Error("deadline_exceeded");
    return Math.min(cap, remaining);
  }
  async run(operation, cap) {
    const ms = this.timeout(cap);
    let timer;
    try {
      return await Promise.race([operation(ms), new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error("deadline_exceeded")), ms);
      })]);
    } finally { clearTimeout(timer); }
  }
  async pause(ms = 250) {
    await new Promise((resolve) => setTimeout(resolve, this.timeout(ms)));
    this.timeout();
  }
}

export function captureScope(geography = "unknown", verified = false) {
  return { validation_revision: 3, validation_status: verified ? "verified" : "unverified", geography, captured_at: Date.now() / 1000, complete: verified };
}

export function scopeIsNational(scope) {
  return scope?.validation_revision === 3 && scope.validation_status === "verified" && scope.geography === "nationwide" && scope.complete === true;
}

// Read selected controls, never option availability, page titles, or listing locations.
export function readScopeDOM() {
  const visible = (node) => {
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
  };
  const label = (node) => [node.getAttribute("aria-label"), node.getAttribute("title"), node.closest('fieldset')?.querySelector('legend')?.textContent,
    ...Array.from(node.labels || [], (item) => item.textContent),
    ...(node.getAttribute("aria-labelledby") || "").split(/\s+/).filter(Boolean).map((id) => document.getElementById(id)?.textContent),
  ].filter(Boolean).join(" ").trim();
  const controls = [];
  for (const node of document.querySelectorAll('select,input[type="range"],[role="slider"],input[type="radio"],input[type="checkbox"],[role="radio"],[role="checkbox"],[role="combobox"],button,[data-testid*="filter-chip"],[data-testid*="selected-filter"]')) {
    if (!visible(node)) continue;
    const name = label(node);
    const text = (node.innerText || node.textContent || "").trim();
    const role = node.getAttribute("role");
    if (node.tagName === "SELECT") {
      const values = Array.from(node.selectedOptions || [], (option) => option.textContent.trim());
      controls.push({ kind: "select", name, value: values.join(" "), values });
    } else if (node.type === "range" || role === "slider") {
      controls.push({ kind: "slider", name, value: node.getAttribute("aria-valuetext") || "", max: node.getAttribute("aria-valuemax") || node.max, now: node.getAttribute("aria-valuenow") || node.value });
    } else if (node.checked || node.getAttribute("aria-checked") === "true") {
      controls.push({ kind: "radio", name, value: Array.from(node.labels || [], (item) => item.textContent).join(" ").trim() || text || node.getAttribute("aria-label") || node.value || "" });
    } else if (role === "combobox" || /(?:radius|distance)/i.test(`${name} ${text}`) || /selected-filter|filter-chip/i.test(node.getAttribute("data-testid") || "")) {
      controls.push({ kind: "selected", name, value: text || node.getAttribute("aria-valuetext") || node.value || "" });
    }
  }
  const links = Array.from(document.querySelectorAll('a[href]')).filter(visible);
  const resultLinks = Array.from(document.querySelectorAll('a[href*="/cars-for-sale/vehicle/"],a[href*="/cars-for-sale/inventory/"],a[href*="/inventory/"],a[href*="/vin/"],a[href*="listing"],a[href*="/details/"]')).filter(visible);
  const resultText = resultLinks.map((node) => `${node.href}|${node.closest('article,[data-testid*="card"],li')?.innerText || node.innerText}`).join("\n");
  const text = document.body?.innerText || "";
  return {
    url: location.href, title: document.title, text: text.slice(0, 30_000), controls,
    ready_state: document.readyState, document_id: performance.timeOrigin,
    busy: Array.from(document.querySelectorAll('[aria-busy="true"],[role="progressbar"],[data-testid*="loading"],.loading-spinner')).some(visible),
    result_count: resultLinks.length, fingerprint: resultText,
    nationwide_links: links.filter((node) => /^(?:nationwide|all miles|unlimited|any distance)$/i.test((node.innerText || "").trim())).map((node) => node.href),
  };
}

function sourceUrlMatches(rawUrl, source) {
  try {
    const url = new URL(rawUrl);
    const host = SOURCE_HOSTS[source];
    return Boolean(host && url.protocol === "https:" && (url.hostname === host || url.hostname.endsWith(`.${host}`)));
  } catch { return false; }
}

const SCOPE_FIELDS = ["make", "model", "trim", "years", "conditions", "body", "drivetrain"];

function scopeValue(value, field) {
  const clean = String(value ?? "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const aliases = {
    conditions: { "certified pre owned": "cpo", "certified used": "cpo", certified: "cpo", "pre owned": "used", "brand new": "new" },
    drivetrain: { "all wheel drive": "awd", "rear wheel drive": "rwd", "front wheel drive": "fwd", "four wheel drive": "4wd" },
    body: { "sport utility vehicle": "suv", "sport utility": "suv" },
  };
  return aliases[field]?.[clean] || clean;
}

function controlField(control) {
  if (SCOPE_FIELDS.includes(control.field)) return control.field;
  const name = control.name || "";
  if (/year/i.test(name)) return "years";
  if (/condition|new.*used|inventory type/i.test(name)) return "conditions";
  if (/drive.?train|drive type/i.test(name)) return "drivetrain";
  if (/body|body style/i.test(name)) return "body";
  if (/trim/i.test(name)) return "trim";
  if (/model/i.test(name)) return "model";
  if (/make|manufacturer|brand/i.test(name)) return "make";
  return null;
}

// Exact selected sets are intentional: a broader filter cannot prove a narrow search.
export function inspectRequestedScope(controls, requested) {
  const fields = {};
  for (const field of SCOPE_FIELDS) {
    const expected = requested?.[field];
    const required = ["make", "model", "years", "conditions"].includes(field);
    if (expected == null || (Array.isArray(expected) ? !expected.length : !String(expected).trim()) || (field === "trim" && /^(?:unspecified|all|any)$/i.test(String(expected).trim()))) {
      const narrowed = controls.filter((control) => controlField(control) === field).flatMap((control) => control.values || [control.value]).filter((value) => value && !/^(?:all(?:\s+.*)?|any(?:\s+.*)?|unspecified|select(?:\s+.*)?)$/i.test(String(value).trim()));
      fields[field] = { status: required ? "unknown" : narrowed.length ? "mismatch" : "not_requested", expected: expected ?? null, observed: narrowed };
      continue;
    }
    const selected = controls.filter((control) => controlField(control) === field);
    let observed = selected.flatMap((control) => control.values || [control.value]).filter((value) => value != null && String(value).trim());
    if (field === "years") {
      const lower = selected.find((control) => /min|from|start/i.test(control.name || ""));
      const upper = selected.find((control) => /max|to\b|end/i.test(control.name || ""));
      const range = lower && upper ? [lower.value, upper.value] : observed.length === 1 && /^\s*\d{4}\s*(?:-|\u2013|to)\s*\d{4}\s*$/i.test(observed[0]) ? String(observed[0]).match(/\d{4}/g) : null;
      if (range) {
        const [start, end] = range.map(Number);
        observed = Number.isInteger(start) && end >= start && end - start <= 120 ? Array.from({ length: end - start + 1 }, (_, index) => start + index) : [];
      } else if (lower || upper) observed = [];
    }
    const wanted = [...new Set((Array.isArray(expected) ? expected : [expected]).map((value) => scopeValue(value, field)))].sort();
    const actual = [...new Set(observed.map((value) => scopeValue(value, field)))].sort();
    fields[field] = { status: !actual.length ? "unknown" : JSON.stringify(actual) === JSON.stringify(wanted) ? "matched" : "mismatch", expected, observed, selected_controls: selected };
  }
  return { status: Object.values(fields).some((item) => item.status === "mismatch") ? "mismatch" : Object.values(fields).some((item) => item.status === "unknown") ? "unknown" : "matched", fields };
}

export function inspectSearchScope(snapshot, source, httpStatus = 200, requestedScope = null) {
  const text = `${snapshot.title || ""}\n${snapshot.text || ""}`;
  const selected = (snapshot.controls || []).filter((control) =>
    /radius|distance|search area|location/i.test(control.name || "") ||
    (control.kind === "slider" && /nationwide/i.test(control.value || "")) ||
    /^(?:nationwide|all miles|unlimited|any distance)$/i.test(control.value || ""));
  const national = selected.some((control) => /\b(?:nationwide|all miles|unlimited|any distance)\b/i.test(control.value || "") &&
    (control.kind !== "slider" || String(control.now) === String(control.max)));
  const local = selected.some((control) => /\b\d[\d,]*\s*(?:mi\b|miles\b|km\b)/i.test(control.value || "") && !/nationwide|all miles/i.test(control.value || ""));
  const geography = local ? "local" : national ? "nationwide" : "unknown";
  const vehicle = inspectRequestedScope(snapshot.controls || [], requestedScope);
  const evidence = { requested_scope: requestedScope, selected_controls: snapshot.controls || [], geography_controls: selected, constraints: vehicle.fields, constraint_status: vehicle.status, final_url: snapshot.url, result_refresh_confirmed: false };
  const result = (status) => ({ status, scope: captureScope(geography), evidence });
  if (httpStatus === 429 || /too many requests|rate limit(?:ed| exceeded)?|temporarily throttled/i.test(text)) return result("rate_limited");
  if ([401, 403].includes(httpStatus) || /page unavailable|access denied|verify you are human|security verification|captcha|unusual activity|network restrictions|do not have permission/i.test(text)) return result("blocked");
  if (!sourceUrlMatches(snapshot.url, source)) return result("filter_mismatch");
  if (snapshot.busy || httpStatus >= 500) return result("loading");
  const url = new URL(snapshot.url);
  const urlMatches = source === "autotrader_browser" ? url.searchParams.get("searchRadius") === "0"
    : source === "porsche_finder_browser" ? url.searchParams.get("position")?.split(",").at(-1) === "-1" : true;
  if (local || !urlMatches || vehicle.status === "mismatch") return result("filter_mismatch");
  if (!national || vehicle.status === "unknown") return result("filter_unknown");
  if (snapshot.result_count > 0) return result("ready");
  if (/\b(?:no (?:matching )?(?:vehicles|cars|results|listings)(?: found| available)?|0 (?:matching )?(?:vehicles|cars|results|listings))\b/i.test(snapshot.text || "")) return result("verifiedzero");
  return result("loading");
}

export function validateHostScope(capture, requestedScope) {
  const pages = Array.isArray(capture.pages) ? capture.pages : [];
  const validations = pages.map((page) => {
    const snapshot = page.scope_snapshot || {};
    const result = inspectSearchScope(snapshot, capture.source, 200, requestedScope);
    result.evidence.result_refresh_confirmed = page.result_refresh_confirmed === true;
    if (["ready", "verifiedzero"].includes(result.status) && page.result_refresh_confirmed !== true) result.status = "loading";
    return result;
  });
  const failure = validations.find((result) => !["ready", "verifiedzero"].includes(result.status));
  const verified = validations.length > 0 && !failure;
  return {
    status: failure?.status || (verified ? validations.every((result) => result.status === "verifiedzero") ? "verifiedzero" : "ready" : "filter_unknown"),
    scope: captureScope(verified ? "nationwide" : failure?.scope.geography, verified),
    evidence: { requested_scope: requestedScope, result_refresh_confirmed: verified, pages: validations.map((result) => ({ ...result.evidence, status: result.status })) },
  };
}

async function scopeSnapshot(page, deadline) {
  return deadline.run(() => page.evaluate(readScopeDOM));
}

export async function waitForSearchScope(page, input, deadline, { before = null, navigation = false, httpStatus = 200 } = {}) {
  let previous = "";
  let refreshed = navigation || before == null;
  let last;
  const waitUntil = Math.min(deadline.at, Date.now() + 15_000);
  do {
    const snapshot = await scopeSnapshot(page, deadline);
    last = inspectSearchScope(snapshot, input.source, httpStatus, input.requested_scope);
    if (["blocked", "rate_limited"].includes(last.status)) return { ...last, snapshot };
    if (before && (snapshot.busy || snapshot.fingerprint !== before.fingerprint || snapshot.result_count !== before.result_count)) refreshed = true;
    const signature = JSON.stringify([snapshot.url, snapshot.controls, snapshot.fingerprint, last.status]);
    if (["ready", "verifiedzero"].includes(last.status) && refreshed && signature === previous) {
      last.scope = captureScope("nationwide", true);
      last.evidence.result_refresh_confirmed = true;
      return { ...last, snapshot };
    }
    previous = snapshot.busy ? "" : signature;
    if (["filter_mismatch", "filter_unknown"].includes(last.status) && !snapshot.busy && before == null) return { ...last, snapshot };
    await deadline.pause();
  } while (Date.now() < waitUntil);
  return { ...last, status: ["filter_mismatch", "filter_unknown"].includes(last?.status) ? last.status : "loading", scope: captureScope(last?.scope.geography), snapshot: await scopeSnapshot(page, deadline) };
}

async function setNationwideControl(page, source, deadline) {
  if (source === "edmunds_browser") {
    const sliders = page.locator('[role="slider"],input[type="range"]');
    for (let index = 0; index < await sliders.count(); index += 1) {
      const slider = sliders.nth(index);
      const name = await slider.evaluate((node) => [node.getAttribute("aria-label"), ...Array.from(node.labels || [], (label) => label.textContent), ...(node.getAttribute("aria-labelledby") || "").split(/\s+/).filter(Boolean).map((id) => document.getElementById(id)?.textContent)].filter(Boolean).join(" "));
      if (!/radius|distance/i.test(name) || !await slider.isVisible()) continue;
      await slider.focus({ timeout: deadline.timeout(3000) });
      await slider.press("End", { timeout: deadline.timeout(3000) });
      const value = await slider.getAttribute("aria-valuetext");
      if (!/^nationwide$/i.test(value || "")) continue;
      // End moves the slider; Enter and blur commit keyboard-driven site controls.
      await slider.press("Enter", { timeout: deadline.timeout(3000) });
      await slider.press("Tab", { timeout: deadline.timeout(3000) });
      const apply = page.getByRole("button", { name: /^(?:apply|apply filters|show results|update results)$/i }).first();
      if (await apply.isVisible()) await apply.click({ timeout: deadline.timeout(3000) });
      return true;
    }
  }
  const selects = page.locator("select");
  for (let index = 0; index < await selects.count(); index += 1) {
    const select = selects.nth(index);
    if (!await select.isVisible()) continue;
    const option = await select.evaluate((node) => Array.from(node.options).find((item) => /^(?:nationwide|all miles|unlimited|any distance)$/i.test(item.textContent.trim()))?.value);
    if (option == null) continue;
    await select.selectOption(option, { timeout: deadline.timeout(3000) });
    return true;
  }
  return false;
}

export async function prepareNationwide(page, input, deadline, httpStatus = 200) {
  const initial = await waitForSearchScope(page, input, deadline, { navigation: true, httpStatus });
  if (scopeIsNational(initial.scope) || ["blocked", "rate_limited"].includes(initial.status)) return initial;
  if (!sourceUrlMatches(page.url(), input.source)) return initial;
  if (await deadline.run(() => setNationwideControl(page, input.source, deadline))) {
    const changed = await waitForSearchScope(page, input, deadline, { before: initial.snapshot });
    if (scopeIsNational(changed.scope) || ["blocked", "rate_limited"].includes(changed.status)) return changed;
    // Same cards can legitimately survive a radius change. A fresh navigation is
    // required in that case; a changed slider label alone cannot validate them.
    const response = await page.reload({ waitUntil: "domcontentloaded", timeout: deadline.timeout(45_000) });
    return waitForSearchScope(page, input, deadline, { navigation: true, httpStatus: response?.status() || 200 });
  }
  const url = new URL(page.url());
  if (input.source === "autotrader_browser") url.searchParams.set("searchRadius", "0");
  else if (input.source === "porsche_finder_browser") {
    const position = url.searchParams.get("position")?.split(",");
    if (position?.length === 4) { position[3] = "-1"; url.searchParams.set("position", position.join(",")); }
  } else {
    const discovered = initial.snapshot.nationwide_links?.find((href) => sourceUrlMatches(href, input.source));
    if (discovered) url.href = discovered;
  }
  if (url.href === page.url()) return initial;
  const response = await page.goto(url.href, { waitUntil: "domcontentloaded", timeout: deadline.timeout(45_000) });
  return waitForSearchScope(page, input, deadline, { navigation: true, httpStatus: response?.status() || 200 });
}
const RECENT_YEAR_TARGET = 15;
const OLDER_YEAR_TARGET = 8;
function defaultProfilePath() {
  return path.join(os.homedir(), ".car-compare", "browser-profile");
}

function tokens(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/\bx\s+drive\b/g, "xdrive")
    .replace(/\b4\s*matic\b/g, "4matic")
    .replace(/\b(m[2345])comp\b/g, "$1 competition")
    .replace(/\bcomp\b/g, "competition")
    .replace(/\bzcp\b/g, "zcp competition")
    .replace(/\bc2s\b/g, "carrera s")
    .replace(/\bc4s\b/g, "carrera 4s")
    .replace(/\bc2\b/g, "carrera")
    .replace(/\bc4\b/g, "carrera 4")
    .replace(/\bdual\s+motor\b/g, "awd")
    .replace(/\blr\b/g, "long range")
    .match(/[a-z0-9]+/g) || [];
}

function hostAllowed(rawUrl) {
  try {
    const url = new URL(rawUrl);
    return url.protocol === "https:" && ALLOWED_HOSTS.some((host) => url.hostname === host || url.hostname.endsWith(`.${host}`));
  } catch {
    return false;
  }
}

function parsePrice(lines) {
  for (const line of lines) {
    if (/\b(?:month|monthly|down|payment|lease|finance|mo\.?\b)/i.test(line)) continue;
    if (/\bmsrp\b/i.test(line)) continue;
    if (/\b(?:fee|fees|tax|taxes)\b/i.test(line)) continue;
    const match = line.includes("$")
      ? line.match(/\$\s*([0-9][0-9,]{3,})/)
      : line.match(/^\s*([0-9]{2,3}(?:,[0-9]{3})+)\s*$/);
    if (!match) continue;
    const value = Number(match[1].replaceAll(",", ""));
    if (value >= 500 && value <= 10_000_000) return value;
  }
  return null;
}

function parseMileage(text) {
  const match = text.match(/\b([0-9][0-9,.]*)\s*(?:k\s*)?(?:mi\.?|miles)\b/i);
  if (!match) return null;
  let value = Number(match[1].replaceAll(",", ""));
  if (/k\s*(?:mi\.?|miles)/i.test(match[0])) value *= 1000;
  return Number.isFinite(value) && value >= 0 && value <= 1_000_000 ? Math.round(value) : null;
}

function parseVin(text, rawUrl) {
  const combined = `${text} ${rawUrl}`.toUpperCase();
  return combined.match(/\b[A-HJ-NPR-Z0-9]{17}\b/)?.[0] || "";
}

function classifyCard(card, input) {
  const lines = String(card.text || "").split(/\n+/).map((line) => line.trim()).filter(Boolean);
  const text = lines.join(" ");
  const observed = new Set(tokens(text));
  const required = tokens(input.required_keywords.join(" "));
  const makeTokens = new Set(tokens((input.make_keywords || []).join(" ")));
  const excluded = tokens(input.exclude_keywords.join(" "));
  const missing = required.filter((token) => !observed.has(token) && !makeTokens.has(token));
  const conflicting = excluded.filter((token) => observed.has(token));
  const year = Number(text.match(/\b(?:19|20)\d{2}\b/)?.[0] || 0);
  const price = parsePrice(lines);

  if (missing.length) return { accepted: false, reason: "missing_required_tokens" };
  if (conflicting.length) return { accepted: false, reason: "excluded_variant" };
  if (!year || year < input.start_year || year > input.end_year) return { accepted: false, reason: "outside_year_range" };
  if (!price) return { accepted: false, reason: "missing_price" };

  const m4CompetitionFamily = required.includes("m4") && required.includes("competition");
  if (m4CompetitionFamily && /\bcompetition\s+package\s+(?:is\s+)?(?:available|optional|sold\s+separately)\b/i.test(text)) {
    return { accepted: false, reason: "unverified_historical_competition_package" };
  }
  if (m4CompetitionFamily && year >= 2016 && year <= 2020 && !(observed.has("zcp") || (observed.has("competition") && observed.has("package")))) {
    return { accepted: false, reason: "unverified_historical_competition_package" };
  }

  const titleLines = lines.filter((line) => /\b(?:19|20)\d{2}\b/.test(line) || required.some((token) => tokens(line).includes(token)));
  const title = (titleLines.slice(0, 4).join(" ") || lines.slice(0, 4).join(" ")).slice(0, 500);
  const trim = lines.find((line) => /\bcompetition\b/i.test(line)) || "";
  const lower = text.toLowerCase();
  const condition = lines.some((line) => /^(?:brand new|new vehicle|new)$/i.test(line))
    ? "new"
    : /\bcertified|\bcpo\b/.test(lower) ? "cpo" : "used";
  return {
    accepted: true,
    listing: {
      source: input.source,
      year,
      price,
      trim: trim.slice(0, 240),
      mileage: parseMileage(text),
      title,
      url: card.url,
      vin: parseVin(text, card.url),
      dealer: "",
      condition,
      confidence: "browser_worker_verified",
    },
  };
}

function configuredCdpUrl() {
  const configured = String(process.env.CAR_COMPARE_BROWSER_CDP_URL || "").trim().replace(/\/$/, "");
  if (configured) return { url: configured, configured: true };
  return { url: "", configured: false };
}

function backgroundModeEnabled() {
  return !["0", "false", "no", "off"].includes(String(process.env.CAR_COMPARE_BACKGROUND_MODE || "1").trim().toLowerCase());
}

async function cdpEndpointReady(rawUrl, deadline) {
  const url = new URL(rawUrl);
  if (!['127.0.0.1', 'localhost', '::1'].includes(url.hostname)) {
    throw new Error("The collection browser endpoint must use localhost.");
  }
  const response = await fetch(`${rawUrl}/json/version`, { signal: AbortSignal.timeout(deadline.timeout(2000)) });
  if (!response.ok) return false;
  const info = await response.json();
  return Boolean(info.Browser && info.webSocketDebuggerUrl);
}

async function launchBrowser(deadline = new Deadline(Date.now() / 1000 + DEFAULT_TIMEOUT_MS / 1000)) {
  const backgroundMode = backgroundModeEnabled();
  const cdp = configuredCdpUrl();
  if (cdp.configured) {
    try {
      if (!await cdpEndpointReady(cdp.url, deadline)) throw new Error("The configured endpoint is not ready.");
      const browser = await chromium.connectOverCDP(cdp.url, { timeout: deadline.timeout(30_000) });
      return { browser, context: browser.contexts()[0], owned: false, mode: "persistent_cdp_configured", backgroundMode: false };
    } catch (error) {
      throw new Error(`Persistent collection browser unavailable at ${cdp.url}. ${error?.message || error}`);
    }
  }
  const hasDisplay = process.platform !== "linux" || Boolean(process.env.DISPLAY || process.env.WAYLAND_DISPLAY);
  const forceHeadful = process.env.CAR_COMPARE_BROWSER_HEADFUL === "1";
  const headless = forceHeadful
    ? false
    : process.env.CAR_COMPARE_BROWSER_HEADLESS === "1" || backgroundMode || !hasDisplay;
  const executablePath = process.env.CAR_COMPARE_BROWSER_EXECUTABLE || "";
  const profilePath = process.env.CAR_COMPARE_BROWSER_PROFILE || defaultProfilePath();
  const attempts = executablePath
    ? [{ executablePath }]
    : [{}, { channel: "chrome" }, { channel: "msedge" }];
  let lastError;
  for (const option of attempts) {
    try {
      const context = await chromium.launchPersistentContext(profilePath, {
        timeout: deadline.timeout(30_000),
        headless,
        locale: "en-US",
        viewport: { width: 1440, height: 1000 },
        args: backgroundMode && !headless ? ["--start-minimized", "--window-position=-10000,-10000"] : [],
        ...option,
      });
      return {
        browser: context.browser(),
        context,
        owned: true,
        mode: headless ? "persistent_profile_headless" : "persistent_profile_headful",
        backgroundMode,
      };
    } catch (error) {
      lastError = error;
    }
  }
  throw new Error(`No usable Chromium browser found. Run npm exec playwright install chromium. ${lastError?.message || ""}`);
}

async function closeBrowserSession(launched) {
  if (!launched?.owned) return;
  if (launched.context) await launched.context.close();
  else if (launched.browser) await launched.browser.close();
}

async function extractCards(page) {
  return page.evaluate(() => {
    const selectors = [
      'a[href*="/cars-for-sale/vehicle/"]',
      'a[href*="/cars-for-sale/inventory/"]',
      'a[href*="/inventory/"]',
      'a[href*="/vin/"]',
      'a[href*="listing"]',
      'a[href*="/details/"]',
    ];
    const seen = new Set();
    const rows = [];
    for (const anchor of document.querySelectorAll(selectors.join(","))) {
      const rawUrl = anchor.href || "";
      const parsedUrl = new URL(rawUrl);
      parsedUrl.hash = "";
      const url = /\/cars-for-sale\/vehicle\/\d+|\/vin\/[A-HJ-NPR-Z0-9]{17}/i.test(parsedUrl.pathname)
        ? `${parsedUrl.origin}${parsedUrl.pathname}`
        : parsedUrl.href;
      if (!url || seen.has(url)) continue;
      let node = anchor;
      let selected = anchor.innerText || anchor.textContent || "";
      for (let depth = 0; depth < 7 && node; depth += 1, node = node.parentElement) {
        const candidate = node.innerText || node.textContent || "";
        if (candidate.length >= 50 && candidate.length <= 4000 && /(?:\$\s*)?[0-9]{2,3},[0-9]{3}/.test(candidate)) selected = candidate;
        if (/\b(?:19|20)\d{2}\b/.test(selected) && /(?:\$\s*)?[0-9]{2,3},[0-9]{3}/.test(selected) && selected.length >= 90) break;
      }
      if (!/\b(?:19|20)\d{2}\b/.test(selected) || !/(?:\$\s*)?[0-9]{2,3},[0-9]{3}/.test(selected)) continue;
      seen.add(url);
      rows.push({ url, text: selected.slice(0, 4000) });
      if (rows.length >= 400) break;
    }
    return rows;
  });
}

async function scrollResults(page, deadline) {
  for (let index = 0; index < 8; index += 1) {
    await deadline.run(() => page.mouse.wheel(0, 1400));
    await deadline.pause(500);
  }
}

export async function clickNext(page, input, deadline) {
  const { source } = input;
  const locators = source === "edmunds_browser"
    ? [page.getByRole("link", { name: /go to the next page/i }), page.getByRole("link", { name: /^next$/i })]
    : [
        page.getByRole("button", { name: /see more results/i }),
        page.getByRole("button", { name: /show more results/i }),
        page.getByRole("button", { name: /load more/i }),
        page.getByRole("link", { name: /next page/i }),
      ];
  for (const candidate of locators) {
    const locator = candidate.first();
    if (!(await locator.isVisible().catch(() => false))) continue;
    const before = await scopeSnapshot(page, deadline);
    await locator.click({ timeout: deadline.timeout(10_000) });
    const validation = await waitForSearchScope(page, input, deadline, { before });
    return { clicked: true, changed: scopeIsNational(validation.scope), validation };
  }
  return { clicked: false, changed: false };
}

function quotaSummary(listings, input) {
  const counts = {};
  for (const listing of listings) counts[listing.year] = (counts[listing.year] || 0) + 1;
  const targets = {};
  for (let year = input.start_year; year <= input.end_year; year += 1) {
    targets[year] = year >= input.current_year - 5 ? RECENT_YEAR_TARGET : OLDER_YEAR_TARGET;
  }
  const sparseYears = Object.entries(targets).filter(([year, target]) => (counts[year] || 0) < target).map(([year]) => Number(year));
  return { counts, targets, sparse_years: sparseYears, met: sparseYears.length === 0 };
}

function opensAccessWallCircuit(result) {
  return result?.stop_reason === "access_wall" || result?.status === "rate_limited";
}

function sparseYearsAfterRange(result, input) {
  const sparse = new Set(result?.year_quota?.sparse_years || []);
  return Array.from(sparse)
    .map(Number)
    .filter((year) => year >= input.start_year && year <= input.end_year)
    .sort((left, right) => right - left).slice(0, 4);
}

export async function collectSingleSearch(rawInput, browserSession = null) {
  const input = normalizeInput(rawInput);
  const deadline = new Deadline(input.deadline_at);
  if (!hostAllowed(input.url)) throw new Error("URL host is not in the Car Compare browser allowlist.");
  const launched = browserSession || await launchBrowser(deadline);
  const ownsSession = browserSession == null;
  const browser = launched.browser;
  const listings = [];
  const seen = new Set();
  const rejected = {};
  const pageRecords = [];
  let stalePages = 0;
  let stopReason = "max_pages";
  let loadMoreClicked = 0;
  let detailPagesOpened = 0;
  let accessBlocked = false;
  let accessMessage = "";
  let validation = { status: "loading", scope: captureScope(), evidence: {} };
  let failureStatus = "";
  let isolatedContext = null;
  let page = null;
  let retryAfter = null;
  try {
    const context = launched.context || (
      launched.owned
        ? (isolatedContext = await browser.newContext({
          locale: "en-US",
          viewport: { width: 1440, height: 1000 },
        }))
        : browser.contexts()[0]
    );
    if (!context) throw new Error("The browser did not expose a usable context.");
    page = await deadline.run(() => context.newPage());
    page.setDefaultTimeout(deadline.timeout(10_000));
    let responseStatus = 200;
    page.on("response", (response) => {
      if (sourceUrlMatches(response.url(), input.source) && (response.request().isNavigationRequest() || ["fetch", "xhr"].includes(response.request().resourceType()))) {
        if ([403, 429].includes(response.status())) responseStatus = response.status();
        if (response.status() === 429) retryAfter = response.headers()["retry-after"] || null;
      }
    });
    const response = await page.goto(input.url, { waitUntil: "domcontentloaded", timeout: deadline.timeout(45_000) });
    responseStatus = [403, 429].includes(responseStatus) ? responseStatus : response?.status() || 200;
    validation = await prepareNationwide(page, input, deadline, responseStatus);
    if (!scopeIsNational(validation.scope)) {
      failureStatus = validation.status;
      accessBlocked = true;
      accessMessage = `${validation.snapshot?.title || ""}: ${validation.snapshot?.text || ""}`.replace(/\s+/g, " ").slice(0, 500);
      stopReason = validation.status === "blocked" ? "access_wall" : validation.status;
    } else if (validation.status === "verifiedzero") {
      stopReason = "verifiedzero";
    }

    for (let pageNumber = 1; !accessBlocked && validation.status !== "verifiedzero" && pageNumber <= input.max_pages; pageNumber += 1) {
      deadline.timeout();
      await scrollResults(page, deadline);
      validation = await waitForSearchScope(page, input, deadline, { httpStatus: responseStatus });
      if (!scopeIsNational(validation.scope)) { failureStatus = validation.status; stopReason = validation.status; break; }
      const cards = await deadline.run(() => extractCards(page));
      const before = listings.length;
      const historicalCandidates = [];
      for (const card of cards) {
        const result = classifyCard(card, input);
        if (!result.accepted) {
          if (result.reason === "unverified_historical_competition_package") {
            historicalCandidates.push(card);
            continue;
          }
          rejected[result.reason] = (rejected[result.reason] || 0) + 1;
          continue;
        }
        const row = result.listing;
        row.scope = { ...validation.scope };
        const key = row.vin || row.url || `${row.year}|${row.price}|${row.mileage ?? ""}|${row.title}`;
        if (seen.has(key)) {
          rejected.duplicate = (rejected.duplicate || 0) + 1;
          continue;
        }
        seen.add(key);
        listings.push(row);
      }
      for (const card of historicalCandidates.slice(0, 8)) {
        deadline.timeout();
        if (!sourceUrlMatches(card.url, input.source)) continue;
        detailPagesOpened += 1;
        const detail = await deadline.run(() => context.newPage());
        let detailText = "";
        try {
          await detail.goto(card.url, { waitUntil: "domcontentloaded", timeout: deadline.timeout(30_000) });
          await deadline.pause(1000);
          detailText = await deadline.run(() => detail.locator("body").innerText()).catch(() => "");
        } catch {
          detailText = "";
        } finally {
          await detail.close();
        }
        const verified = classifyCard({ ...card, text: `${card.text}\n${detailText.slice(0, 20_000)}` }, input);
        if (!verified.accepted) {
          rejected.unverified_historical_competition_package = (rejected.unverified_historical_competition_package || 0) + 1;
          continue;
        }
        const row = verified.listing;
        row.scope = { ...validation.scope };
        const key = row.vin || row.url || `${row.year}|${row.price}|${row.mileage ?? ""}|${row.title}`;
        if (seen.has(key)) {
          rejected.duplicate = (rejected.duplicate || 0) + 1;
          continue;
        }
        seen.add(key);
        listings.push(row);
      }
      const added = listings.length - before;
      pageRecords.push({ page: pageNumber, url: page.url(), cards_examined: cards.length, accepted_new: added, detail_pages_opened: historicalCandidates.slice(0, 8).length, scope: validation.scope, search_scope: validation.evidence });
      if (!input.skip_persist) await persistAudit({
        source: input.source, url: input.url, status: "partial", browser_verified: true,
        scope: validation.scope, search_scope: validation.evidence, listings,
        pages_examined: pageRecords.length, page_records: pageRecords,
        cards_examined: pageRecords.reduce((sum, record) => sum + record.cards_examined, 0),
        accepted: listings.length, stop_reason: "checkpoint", year_quota: quotaSummary(listings, input),
        rejected_by_reason: rejected, load_more_clicked: loadMoreClicked,
      });
      stalePages = added ? 0 : stalePages + 1;
      const quota = quotaSummary(listings, input);
      const minimumPagesBeforeQuota = input.source === "porsche_finder_browser"
        ? Math.min(input.max_pages, 3)
        : 1;
      if (quota.met && pageNumber >= minimumPagesBeforeQuota) {
        stopReason = "year_targets_met";
        break;
      }
      if (stalePages >= 3) {
        stopReason = "three_pages_without_new_matches";
        break;
      }
      if (pageNumber >= input.max_pages) {
        stopReason = "max_pages";
        break;
      }
      const next = await deadline.run(() => clickNext(page, input, deadline));
      if (!next.clicked) {
        stopReason = "source_exhausted";
        break;
      }
      loadMoreClicked += 1;
      if (!next.changed) {
        validation = next.validation;
        failureStatus = validation.status;
        stopReason = validation.status;
        break;
      }
    }
  } catch (error) {
    stopReason = Date.now() >= deadline.at || error?.message === "deadline_exceeded" ? "deadline_exceeded" : "capture_error";
    failureStatus = "loading";
    accessMessage = String(error?.message || error).slice(0, 500);
    validation = { ...validation, scope: captureScope(validation.scope.geography) };
  } finally {
    if (page) await page.close().catch(() => {});
    if (isolatedContext) await isolatedContext.close().catch(() => {});
    if (ownsSession) await closeBrowserSession(launched);
  }

  const acceptedScope = listings.length ? listings[0].scope : validation.scope;
  const quota = quotaSummary(listings, input);
  const audit = {
    version: 2,
    source: input.source,
    url: input.url,
    browser_mode: launched.mode,
    background_mode: Boolean(launched.backgroundMode),
    browser_verified: scopeIsNational(acceptedScope),
    scope: acceptedScope,
    search_scope: { ...validation.evidence, ...validation.scope },
    status: listings.length && failureStatus ? "partial" : failureStatus || (listings.length ? (quota.met ? "collected" : "partial") : validation.status === "verifiedzero" ? "verifiedzero" : "filter_mismatch"),
    retry_after: retryAfter,
    pages_examined: pageRecords.length,
    cards_examined: pageRecords.reduce((sum, page) => sum + page.cards_examined, 0),
    accepted: listings.length,
    rejected_by_reason: rejected,
    load_more_clicked: loadMoreClicked,
    detail_pages_opened: detailPagesOpened,
    stop_reason: stopReason,
    access_message: accessMessage,
    year_quota: quota,
    page_records: pageRecords,
    listings,
  };
  if (!input.skip_persist) await persistAudit(audit);
  return audit;
}

function urlForYear(rawUrl, source, year) {
  const url = new URL(rawUrl);
  url.searchParams.delete("pagenumber");
  url.searchParams.delete("page");
  if (source === "autotrader_browser") {
    url.searchParams.set("startYear", String(year));
    url.searchParams.set("endYear", String(year));
  } else if (source === "edmunds_browser") {
    url.searchParams.set("year", String(year));
  } else if (source === "porsche_finder_browser") {
    url.searchParams.set("minimum-model-year", String(year));
    url.searchParams.set("maximum-model-year", String(year));
  }
  return url.href;
}

async function persistAudit(audit) {
  const auditDir = process.env.CAR_COMPARE_BROWSER_AUDIT_DIR;
  if (!auditDir) return;
  await fs.mkdir(auditDir, { recursive: true });
  const safeSource = audit.source.replace(/[^a-z0-9_-]+/gi, "_");
  const destination = path.join(auditDir, `browser_capture_${safeSource}.json`);
  const temporary = `${destination}.${process.pid}.tmp`;
  await fs.writeFile(temporary, JSON.stringify(audit, null, 2));
  await fs.rename(temporary, destination);
}

function failedCapture(input, error, launched = {}) {
  const scope = captureScope();
  return {
    version: 2, source: input.source, url: input.url, status: "loading",
    stop_reason: Date.now() / 1000 >= input.deadline_at || error?.message === "deadline_exceeded" ? "deadline_exceeded" : "capture_error",
    browser_mode: launched.mode || "not_started", background_mode: Boolean(launched.backgroundMode),
    browser_verified: false, scope, search_scope: { ...scope, result_refresh_confirmed: false },
    error: String(error?.message || error).slice(0, 1000), accepted: 0, listings: [],
  };
}

export async function collectSource(rawInput, browserSession = null) {
  const input = normalizeInput(rawInput);
  try {
    new Deadline(input.deadline_at).timeout();
    return await collectSourceImpl(input, browserSession);
  } catch (error) {
    const audit = failedCapture(input, error, browserSession || {});
    if (!input.skip_persist) await persistAudit(audit);
    return audit;
  }
}

async function collectSourceImpl(input, browserSession = null) {
  if (!input.split_by_year || input.start_year === input.end_year) return collectSingleSearch(input, browserSession);
  const results = [];
  const targetedResults = [];
  const deadline = new Deadline(input.deadline_at);
  const launched = browserSession || await launchBrowser(deadline);
  const ownsSession = browserSession == null;
  let rangeResult = null;
  try {
    rangeResult = await collectSingleSearch({ ...input, skip_persist: true }, launched);
    results.push(rangeResult);
    if (scopeIsNational(rangeResult.scope) && rangeResult.status !== "verifiedzero") {
      for (const year of sparseYearsAfterRange(rangeResult, input)) {
        if (Date.now() >= deadline.at) break;
        const result = await collectSingleSearch({
          ...input,
          url: urlForYear(input.url, input.source, year),
          start_year: year,
          end_year: year,
          max_pages: Math.min(2, input.max_pages),
          requested_scope: input.requested_scope ? { ...input.requested_scope, years: [year] } : null,
          skip_persist: true,
        }, launched);
        results.push(result);
        targetedResults.push(result);
        if (!scopeIsNational(result.scope) || opensAccessWallCircuit(result)) break;
      }
    }
  } finally {
    if (ownsSession) await closeBrowserSession(launched);
  }

  const listings = [];
  const seen = new Set();
  const rejected = {};
  const pageRecords = [];
  for (const result of results) {
    for (const [reason, count] of Object.entries(result.rejected_by_reason || {})) {
      rejected[reason] = (rejected[reason] || 0) + Number(count || 0);
    }
    for (const row of scopeIsNational(result.scope) ? result.listings || [] : []) {
      const key = row.vin || row.url || `${row.year}|${row.price}|${row.mileage ?? ""}|${row.title}`;
      if (seen.has(key)) continue;
      seen.add(key);
      listings.push(row);
    }
    const isRangeSearch = result === rangeResult;
    pageRecords.push(...(result.page_records || []).map((record) => ({
      ...record,
      search_year: isRangeSearch ? null : (result.year_quota ? Number(Object.keys(result.year_quota.targets || {})[0]) : null),
      search_kind: isRangeSearch ? "range" : "year",
    })));
  }
  const quota = quotaSummary(listings, input);
  const failure = results.find((result) => !scopeIsNational(result.scope));
  const scope = listings.length ? listings[0].scope : failure ? captureScope(failure.scope?.geography) : captureScope("nationwide", true);
  const finalQuota = failure ? quotaSummary(listings, input) : quota;
  const accessWallCircuitOpen = results.some((result) => result.stop_reason === "access_wall");
  const requestedYears = input.end_year - input.start_year + 1;
  const plannedTargetYears = rangeResult ? sparseYearsAfterRange(rangeResult, input) : [];
  const audit = {
    version: 2,
    source: input.source,
    url: input.url,
    browser_mode: results[0]?.browser_mode || launched.mode,
    background_mode: results.some((result) => result.background_mode) || Boolean(launched.backgroundMode),
    browser_verified: scopeIsNational(scope),
    scope,
    search_scope: { ...scope, result_refresh_confirmed: scopeIsNational(scope), searches: results.map((result) => result.search_scope) },
    status: failure && listings.length ? "partial" : failure?.status || (listings.length ? (finalQuota.met ? "collected" : "partial") : rangeResult?.status === "verifiedzero" ? "verifiedzero" : "filter_mismatch"),
    retry_after: results.find((result) => result.retry_after)?.retry_after || null,
    pages_examined: results.reduce((sum, result) => sum + Number(result.pages_examined || 0), 0),
    cards_examined: results.reduce((sum, result) => sum + Number(result.cards_examined || 0), 0),
    accepted: listings.length,
    rejected_by_reason: rejected,
    load_more_clicked: results.reduce((sum, result) => sum + Number(result.load_more_clicked || 0), 0),
    detail_pages_opened: results.reduce((sum, result) => sum + Number(result.detail_pages_opened || 0), 0),
    stop_reason: Date.now() >= deadline.at ? "deadline_exceeded" : failure ? failure.stop_reason : accessWallCircuitOpen
      ? "access_wall_circuit_breaker"
      : quota.met
        ? "year_targets_met"
        : targetedResults.length
          ? "range_then_sparse_years_complete"
          : "range_search_complete",
    access_message: results.filter((result) => result.access_message).map((result) => result.access_message).join(" | ").slice(0, 1000),
    year_quota: finalQuota,
    page_records: pageRecords,
    requested_year_searches: requestedYears,
    range_search: rangeResult ? {
      status: rangeResult.status,
      pages_examined: rangeResult.pages_examined,
      cards_examined: rangeResult.cards_examined,
      accepted: rangeResult.accepted,
      load_more_clicked: rangeResult.load_more_clicked,
      stop_reason: rangeResult.stop_reason,
      scope: rangeResult.scope,
      search_scope: rangeResult.search_scope,
    } : null,
    attempted_year_searches: targetedResults.length,
    avoided_year_searches: Math.max(0, requestedYears - plannedTargetYears.length),
    skipped_year_searches: Math.max(0, plannedTargetYears.length - targetedResults.length),
    year_searches: targetedResults.map((result) => ({
      year: Number(Object.keys(result.year_quota?.targets || {})[0] || 0),
      status: result.status,
      pages_examined: result.pages_examined,
      cards_examined: result.cards_examined,
      accepted: result.accepted,
      stop_reason: result.stop_reason,
      scope: result.scope,
      search_scope: result.search_scope,
    })),
    listings,
  };
  await persistAudit(audit);
  return audit;
}

function selfTest() {
  const input = {
    source: "autotrader_browser",
    required_keywords: ["BMW", "M4", "Competition"],
    exclude_keywords: ["CS", "CSL", "GTS"],
    start_year: 2016,
    end_year: 2026,
    current_year: 2026,
  };
  const current = classifyCard({ url: "https://www.autotrader.com/cars-for-sale/inventory/1", text: "Used 2024 BMW M4 Competition xDrive Convertible\n$78,500\n12,400 miles" }, input);
  const historical = classifyCard({ url: "https://www.autotrader.com/cars-for-sale/inventory/2", text: "2018 BMW M4 Coupe with factory ZCP Competition Package\n$48,900\n31,000 miles" }, input);
  const rejected = classifyCard({ url: "https://www.autotrader.com/cars-for-sale/inventory/3", text: "2024 BMW M4 CS\n$119,000\n4,000 miles" }, input);
  if (!current.accepted || !historical.accepted || rejected.accepted || !hostAllowed(current.listing.url)) throw new Error("Browser worker self-test failed.");
  const porscheInput = { ...input, source: "porsche_finder_browser", required_keywords: ["Porsche", "911", "Carrera"], exclude_keywords: [], start_year: 2025, end_year: 2025 };
  const porsche = classifyCard({ url: "https://finder.porsche.com/us/en-US/details/porsche-911-carrera-s-preowned-ABC123", text: "2025 Porsche 911 Carrera S (992 II)\nCertified Pre-Owned\n8,206 mi\n$159,084.00\nEstimated Dealer Fees: $85" }, porscheInput);
  const porscheNew = classifyCard({ url: "https://finder.porsche.com/us/en-US/details/porsche-911-carrera-new-DEF456", text: "2025 Porsche 911 Carrera (992 II)\nNew\n$141,250.00" }, porscheInput);
  const yearlyPorsche = new URL(urlForYear("https://finder.porsche.com/us/en-US/search/911?model=911&page=3", "porsche_finder_browser", 2024));
  if (!porsche.accepted || porsche.listing.condition !== "cpo" || porsche.listing.price !== 159084 || !porscheNew.accepted || porscheNew.listing.condition !== "new" || !hostAllowed(porsche.listing.url) || yearlyPorsche.searchParams.get("minimum-model-year") !== "2024" || yearlyPorsche.searchParams.get("maximum-model-year") !== "2024" || yearlyPorsche.searchParams.has("page")) {
    throw new Error("Porsche Finder browser worker self-test failed.");
  }
  const sparseYears = sparseYearsAfterRange({ year_quota: { sparse_years: [2023, 2025, 2030] } }, { start_year: 2023, end_year: 2026 });
  if (sparseYears.join(",") !== "2025,2023") throw new Error("Range-first collection self-test failed.");
  const cdp = configuredCdpUrl();
  if (cdp.configured || !opensAccessWallCircuit({ stop_reason: "access_wall" })) {
    throw new Error("Browser runtime self-test failed.");
  }
  if (process.env.CAR_COMPARE_BACKGROUND_MODE == null && !backgroundModeEnabled()) {
    throw new Error("Background browser mode should be enabled by default.");
  }
  process.stdout.write("Car Compare browser worker self-test passed.\n");
}

async function writeJsonLine(value) {
  const line = `${JSON.stringify(value)}\n`;
  await new Promise((resolve, reject) => {
    process.stdout.write(line, (error) => error ? reject(error) : resolve());
  });
}

async function probeBrowser() {
  const launched = await launchBrowser();
  try {
    return {
      mode: launched.mode,
      background_mode: Boolean(launched.backgroundMode),
      contexts: launched.browser.contexts().length,
      pages: launched.browser.contexts().reduce((total, context) => total + context.pages().length, 0),
    };
  } finally {
    await closeBrowserSession(launched);
  }
}

async function runtimeStatus() {
  const executablePath = chromium.executablePath();
  try {
    await fs.access(executablePath);
    return {
      ready: true,
      mode: backgroundModeEnabled() ? "persistent-profile-background" : "persistent-profile",
      executable_path: executablePath,
      profile_path: process.env.CAR_COMPARE_BROWSER_PROFILE || defaultProfilePath(),
      background_mode: backgroundModeEnabled(),
    };
  } catch (error) {
    return { ready: false, mode: "missing-browser", executable_path: executablePath, error: String(error?.message || error) };
  }
}

export async function collectBatch(rawInputs, maxConcurrency = 2, deadlineAt = null) {
  const sharedDeadline = deadlineAt == null ? Date.now() / 1000 + DEFAULT_TIMEOUT_MS / 1000 : Number(deadlineAt);
  const inputs = rawInputs.map((input) => normalizeInput({ ...input, deadline_at: Math.min(input.deadline_at ?? sharedDeadline, sharedDeadline) }));
  if (!inputs.length) return [];
  let launched;
  try {
    const activeDeadlines = inputs.map((input) => input.deadline_at).filter((at) => at > Date.now() / 1000);
    launched = await launchBrowser(new Deadline(Math.min(sharedDeadline, Math.max(...activeDeadlines))));
  } catch (error) {
    return inputs.map((input) => failedCapture(input, error));
  }
  const results = new Array(inputs.length);
  const workerCount = Math.max(1, Math.min(4, Number(maxConcurrency) || 2, inputs.length || 1));
  let nextIndex = 0;
  try {
    async function worker() {
      while (nextIndex < inputs.length) {
        const index = nextIndex;
        nextIndex += 1;
        const input = inputs[index];
        try {
          results[index] = await collectSource(input, launched);
        } catch (error) {
          results[index] = failedCapture(input, error, launched);
        }
      }
    }
    await Promise.all(Array.from({ length: workerCount }, () => worker()));
  } finally {
    await closeBrowserSession(launched);
  }
  return results;
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href;
if (!isMain) {
  // Imported by the offline scope regression suite; do not start an MCP server.
} else if (process.argv.includes("--self-test")) {
  selfTest();
} else if (process.argv.includes("--scope-dom-script")) {
  process.stdout.write(`(${readScopeDOM.toString()})()`);
} else if (process.argv.includes("--validate-host-scope-json")) {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const { capture, requested_scope } = JSON.parse(Buffer.concat(chunks).toString("utf8"));
  await writeJsonLine(validateHostScope(capture, requested_scope));
} else if (process.argv.includes("--runtime-status")) {
  await writeJsonLine(await runtimeStatus());
} else if (process.argv.includes("--probe-browser")) {
  await writeJsonLine(await probeBrowser());
} else if (process.argv.includes("--collect-batch-json")) {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const input = JSON.parse(Buffer.concat(chunks).toString("utf8"));
  await writeJsonLine(await collectBatch(input.targets || [], input.max_concurrency, input.deadline_at));
} else if (process.argv.includes("--collect-json")) {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const input = JSON.parse(Buffer.concat(chunks).toString("utf8"));
  const audit = await collectSource(input);
  await writeJsonLine(audit);
  process.exitCode = 0;
} else {
  const server = new McpServer({ name: "car-compare-browser", version: "1.0.0" });
  server.registerTool("collect_vehicle_source", {
    description: "Open an allowlisted public car marketplace, paginate visible results, deterministically extract listing cards, and persist an auditable capture for the Car Compare job.",
    inputSchema: {
      source: z.string(),
      url: z.string().url(),
      requested_scope: z.object({
        make: z.string().min(1), model: z.string().min(1), trim: z.string().optional(),
        years: z.array(z.number().int().min(1980).max(2100)).min(1),
        conditions: z.array(z.enum(["new", "used", "cpo"])).min(1),
        body: z.string().optional(), drivetrain: z.string().optional(),
      }),
      required_keywords: z.array(z.string()),
      make_keywords: z.array(z.string()).default([]),
      exclude_keywords: z.array(z.string()).default([]),
      start_year: z.number().int().min(1980).max(2100),
      end_year: z.number().int().min(1980).max(2100),
      current_year: z.number().int().min(1980).max(2100),
      max_pages: z.number().int().min(1).max(MAX_PAGES).default(DEFAULT_MAX_PAGES),
      deadline_at: z.number().positive().optional(),
      split_by_year: z.boolean().default(false),
    },
  }, async (input) => {
    try {
      const audit = await collectSource(input);
      return { content: [{ type: "text", text: JSON.stringify(audit) }] };
    } catch (error) {
      return { isError: true, content: [{ type: "text", text: String(error?.message || error) }] };
    }
  });
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
