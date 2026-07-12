#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { chromium } from "playwright";
import * as z from "zod/v4";

const ALLOWED_HOSTS = [
  "autotrader.com",
  "cars.com",
  "cargurus.com",
  "edmunds.com",
  "bmwusa.com",
  "visor.vin",
];
const DEFAULT_MAX_PAGES = 20;
const DEFAULT_TIMEOUT_MS = 5 * 60 * 1000;
const RECENT_YEAR_TARGET = 15;
const OLDER_YEAR_TARGET = 8;

function tokens(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/\bx\s+drive\b/g, "xdrive")
    .replace(/\b4\s*matic\b/g, "4matic")
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
  const excluded = tokens(input.exclude_keywords.join(" "));
  const missing = required.filter((token) => !observed.has(token));
  const conflicting = excluded.filter((token) => observed.has(token));
  const year = Number(text.match(/\b(?:19|20)\d{2}\b/)?.[0] || 0);
  const price = parsePrice(lines);

  if (missing.length) return { accepted: false, reason: "missing_required_tokens" };
  if (conflicting.length) return { accepted: false, reason: "excluded_variant" };
  if (!year || year < input.start_year || year > input.end_year) return { accepted: false, reason: "outside_year_range" };
  if (!price) return { accepted: false, reason: "missing_price" };

  const m4CompetitionFamily = required.includes("m4") && required.includes("competition");
  if (m4CompetitionFamily && year >= 2016 && year <= 2020 && !(observed.has("zcp") || (observed.has("competition") && observed.has("package")))) {
    return { accepted: false, reason: "unverified_historical_competition_package" };
  }

  const titleLines = lines.filter((line) => /\b(?:19|20)\d{2}\b/.test(line) || required.some((token) => tokens(line).includes(token)));
  const title = (titleLines.slice(0, 4).join(" ") || lines.slice(0, 4).join(" ")).slice(0, 500);
  const trim = lines.find((line) => /\bcompetition\b/i.test(line)) || "";
  const lower = text.toLowerCase();
  const condition = /^new\b/i.test(title) || /\bnew vehicle\b/.test(lower) ? "new" : /\bcertified|\bcpo\b/.test(lower) ? "cpo" : "used";
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

async function launchBrowser() {
  const cdpUrl = process.env.CAR_COMPARE_BROWSER_CDP_URL || "";
  if (cdpUrl) {
    const browser = await chromium.connectOverCDP(cdpUrl, { timeout: 15_000 });
    return { browser, owned: false };
  }
  const headless = process.env.CAR_COMPARE_BROWSER_HEADFUL !== "1";
  const executablePath = process.env.CAR_COMPARE_BROWSER_EXECUTABLE || "";
  const attempts = executablePath
    ? [{ executablePath }]
    : [{}, { channel: "chrome" }, { channel: "msedge" }];
  let lastError;
  for (const option of attempts) {
    try {
      return { browser: await chromium.launch({ headless, ...option }), owned: true };
    } catch (error) {
      lastError = error;
    }
  }
  throw new Error(`No usable Chromium browser found. Run npm exec playwright install chromium. ${lastError?.message || ""}`);
}

async function extractCards(page) {
  return page.evaluate(() => {
    const selectors = [
      'a[href*="/cars-for-sale/vehicle/"]',
      'a[href*="/cars-for-sale/inventory/"]',
      'a[href*="/inventory/"]',
      'a[href*="/vin/"]',
      'a[href*="listing"]',
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

async function scrollResults(page) {
  for (let index = 0; index < 8; index += 1) {
    await page.mouse.wheel(0, 1400);
    await page.waitForTimeout(500);
  }
}

async function clickNext(page, source) {
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
    const beforeUrl = page.url();
    const beforeLength = await page.locator("body").innerText().then((text) => text.length).catch(() => 0);
    await locator.click({ timeout: 10_000 });
    await page.waitForTimeout(1600);
    await page.waitForLoadState("domcontentloaded", { timeout: 15_000 }).catch(() => {});
    const afterLength = await page.locator("body").innerText().then((text) => text.length).catch(() => 0);
    return { clicked: true, changed: page.url() !== beforeUrl || afterLength > beforeLength + 100 };
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

async function collectSingleSearch(input) {
  if (!hostAllowed(input.url)) throw new Error("URL host is not in the Car Compare browser allowlist.");
  const launched = await launchBrowser();
  const browser = launched.browser;
  const startedAt = Date.now();
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
  try {
    const context = launched.owned
      ? await browser.newContext({
          locale: "en-US",
          userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
          viewport: { width: 1440, height: 1000 },
        })
      : browser.contexts()[0];
    const page = await context.newPage();
    await page.goto(input.url, { waitUntil: "domcontentloaded", timeout: 45_000 });
    await page.waitForTimeout(3000);

    const pageTitle = await page.title();
    const bodyLead = await page.locator("body").innerText().then((text) => text.slice(0, 600)).catch(() => "");
    if (/page unavailable|access denied|verify you are human|security verification|captcha/i.test(`${pageTitle} ${bodyLead}`)) {
      accessBlocked = true;
      accessMessage = `${pageTitle}: ${bodyLead}`.replace(/\s+/g, " ").slice(0, 500);
      stopReason = "access_wall";
    }

    for (let pageNumber = 1; !accessBlocked && pageNumber <= input.max_pages; pageNumber += 1) {
      if (Date.now() - startedAt >= DEFAULT_TIMEOUT_MS) {
        stopReason = "time_limit";
        break;
      }
      await scrollResults(page);
      const cards = await extractCards(page);
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
        const key = row.vin || row.url || `${row.year}|${row.price}|${row.mileage ?? ""}|${row.title}`;
        if (seen.has(key)) {
          rejected.duplicate = (rejected.duplicate || 0) + 1;
          continue;
        }
        seen.add(key);
        listings.push(row);
      }
      for (const card of historicalCandidates.slice(0, 8)) {
        detailPagesOpened += 1;
        const detail = await context.newPage();
        let detailText = "";
        try {
          await detail.goto(card.url, { waitUntil: "domcontentloaded", timeout: 30_000 });
          await detail.waitForTimeout(1000);
          detailText = await detail.locator("body").innerText().catch(() => "");
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
        const key = row.vin || row.url || `${row.year}|${row.price}|${row.mileage ?? ""}|${row.title}`;
        if (seen.has(key)) {
          rejected.duplicate = (rejected.duplicate || 0) + 1;
          continue;
        }
        seen.add(key);
        listings.push(row);
      }
      const added = listings.length - before;
      pageRecords.push({ page: pageNumber, url: page.url(), cards_examined: cards.length, accepted_new: added, detail_pages_opened: historicalCandidates.slice(0, 8).length });
      stalePages = added ? 0 : stalePages + 1;
      const quota = quotaSummary(listings, input);
      if (quota.met) {
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
      const next = await clickNext(page, input.source);
      if (!next.clicked) {
        stopReason = "source_exhausted";
        break;
      }
      loadMoreClicked += 1;
      if (!next.changed) stalePages += 1;
    }
    await page.close();
    if (launched.owned) await context.close();
  } finally {
    if (launched.owned) await browser.close();
  }

  const quota = quotaSummary(listings, input);
  const audit = {
    version: 1,
    source: input.source,
    url: input.url,
    browser_verified: true,
    status: accessBlocked ? "blocked" : listings.length ? (quota.met ? "collected" : "partial") : "unavailable",
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
  if (source === "autotrader_browser") {
    url.searchParams.set("startYear", String(year));
    url.searchParams.set("endYear", String(year));
  } else if (source === "edmunds_browser") {
    url.searchParams.set("year", String(year));
  }
  return url.href;
}

async function persistAudit(audit) {
  const auditDir = process.env.CAR_COMPARE_BROWSER_AUDIT_DIR;
  if (!auditDir) return;
  await fs.mkdir(auditDir, { recursive: true });
  const safeSource = audit.source.replace(/[^a-z0-9_-]+/gi, "_");
  await fs.writeFile(path.join(auditDir, `browser_capture_${safeSource}.json`), JSON.stringify(audit, null, 2));
}

async function collectSource(input) {
  if (!input.split_by_year || input.start_year === input.end_year) return collectSingleSearch(input);
  const results = [];
  for (let year = input.end_year; year >= input.start_year; year -= 1) {
    results.push(await collectSingleSearch({
      ...input,
      url: urlForYear(input.url, input.source, year),
      start_year: year,
      end_year: year,
      skip_persist: true,
    }));
  }

  const listings = [];
  const seen = new Set();
  const rejected = {};
  const pageRecords = [];
  for (const result of results) {
    for (const [reason, count] of Object.entries(result.rejected_by_reason || {})) {
      rejected[reason] = (rejected[reason] || 0) + Number(count || 0);
    }
    for (const row of result.listings || []) {
      const key = row.vin || row.url || `${row.year}|${row.price}|${row.mileage ?? ""}|${row.title}`;
      if (seen.has(key)) continue;
      seen.add(key);
      listings.push(row);
    }
    pageRecords.push(...(result.page_records || []).map((record) => ({ ...record, search_year: result.year_quota ? Number(Object.keys(result.year_quota.targets || {})[0]) : null })));
  }
  const quota = quotaSummary(listings, input);
  const anyBlocked = results.some((result) => result.status === "blocked");
  const audit = {
    version: 1,
    source: input.source,
    url: input.url,
    browser_verified: true,
    status: listings.length ? (quota.met ? "collected" : "partial") : anyBlocked ? "blocked" : "unavailable",
    pages_examined: results.reduce((sum, result) => sum + Number(result.pages_examined || 0), 0),
    cards_examined: results.reduce((sum, result) => sum + Number(result.cards_examined || 0), 0),
    accepted: listings.length,
    rejected_by_reason: rejected,
    load_more_clicked: results.reduce((sum, result) => sum + Number(result.load_more_clicked || 0), 0),
    detail_pages_opened: results.reduce((sum, result) => sum + Number(result.detail_pages_opened || 0), 0),
    stop_reason: "year_searches_complete",
    access_message: results.filter((result) => result.access_message).map((result) => result.access_message).join(" | ").slice(0, 1000),
    year_quota: quota,
    page_records: pageRecords,
    year_searches: results.map((result) => ({
      year: Number(Object.keys(result.year_quota?.targets || {})[0] || 0),
      status: result.status,
      pages_examined: result.pages_examined,
      cards_examined: result.cards_examined,
      accepted: result.accepted,
      stop_reason: result.stop_reason,
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
  process.stdout.write("Car Compare browser worker self-test passed.\n");
}

if (process.argv.includes("--self-test")) {
  selfTest();
} else if (process.argv.includes("--collect-json")) {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const input = JSON.parse(Buffer.concat(chunks).toString("utf8"));
  const audit = await collectSource(input);
  process.stdout.write(`${JSON.stringify(audit)}\n`);
  process.exit(0);
} else {
  const server = new McpServer({ name: "car-compare-browser", version: "1.0.0" });
  server.registerTool("collect_vehicle_source", {
    description: "Open an allowlisted public car marketplace, paginate visible results, deterministically extract listing cards, and persist an auditable capture for the Car Compare job.",
    inputSchema: {
      source: z.string(),
      url: z.string().url(),
      required_keywords: z.array(z.string()),
      exclude_keywords: z.array(z.string()).default([]),
      start_year: z.number().int().min(1980).max(2100),
      end_year: z.number().int().min(1980).max(2100),
      current_year: z.number().int().min(1980).max(2100),
      max_pages: z.number().int().min(1).max(DEFAULT_MAX_PAGES).default(DEFAULT_MAX_PAGES),
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
