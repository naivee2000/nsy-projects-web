// Fast Chrome/Pyodide gate for one changed import batch. Never touches live progress.
// Usage: PLAYWRIGHT_MODULE=... node scripts/verify_incremental_browser.mjs 532 533
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const arguments_ = process.argv.slice(2);
const reportFlag = arguments_.indexOf('--report');
const reportPath = reportFlag < 0 ? null : path.resolve(root, arguments_[reportFlag + 1] || '');
if (reportFlag >= 0) arguments_.splice(reportFlag, 2);
const requested = arguments_.map(value => value.startsWith('leetcode-') ? value : `leetcode-${Number(value)}`);
assert(requested.length > 0 && requested.every(id => /^leetcode-\d+$/.test(id)), 'Pass one or more numeric workbook IDs.');
assert.equal(new Set(requested).size, requested.length, 'IDs must be unique.');
const playwright = await import(process.env.PLAYWRIGHT_MODULE ? pathToFileURL(process.env.PLAYWRIGHT_MODULE).href : 'playwright');
const { chromium } = playwright.chromium ? playwright : playwright.default;
const manifest = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/manifest.json'), 'utf8'));
const selected = requested.map(id => {
  const entry = manifest.entries.find(item => item.id === id);
  assert(entry, `${id} is not packaged; package the validated batch first.`);
  return entry;
});
const socket = net.createServer();
await new Promise(resolve => socket.listen(0, '127.0.0.1', resolve));
const port = socket.address().port;
await new Promise(resolve => socket.close(resolve));
const base = `http://127.0.0.1:${port}`;
const temp = await fs.mkdtemp(path.join(os.tmpdir(), 'code-practice-incremental-'));
const python = process.env.CODE_PRACTICE_PYTHON || path.join(root, '.venv/bin/python');
let server, browser;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const report = { scope: 'Incremental batch gate; full-catalog benchmark intentionally not run', ids: requested, worker: [], checks: [] };

async function start() {
  server = spawn(python, [path.join(root, 'scripts/benchmark_server.py'), '--port', String(port),
    '--memory-report', path.join(temp, 'memory.json')], {
    cwd: root, env: { ...process.env, CODE_PRACTICE_DATA_DIR: temp, CODE_PRACTICE_DB: path.join(temp, 'progress.db'),
      CODE_PRACTICE_SEED_DB: '', CODE_PRACTICE_AUTH_USERNAME: '', CODE_PRACTICE_SESSION_SECRET: '',
      CODE_PRACTICE_CATALOG_DIR: path.join(root, 'catalog_data') }, stdio: ['ignore', 'ignore', 'pipe'],
  });
  let stderr = '';
  server.stderr.on('data', data => { stderr += data; });
  for (let attempt = 0; attempt < 100; attempt++) {
    if (server.exitCode !== null) throw new Error(stderr);
    try { if ((await fetch(`${base}/api/health`)).ok) return; } catch {}
    await sleep(100);
  }
  throw new Error(`Server did not become healthy: ${stderr}`);
}

async function stop() {
  if (server?.exitCode === null) {
    const exited = new Promise(resolve => server.once('exit', resolve));
    server.kill('SIGTERM');
    await exited;
  }
}

async function judge(page, problem, source) {
  return page.evaluate(async ({ problem, source }) => {
    const worker = new Worker('/judge-worker.js');
    try {
      await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Pyodide warmup timed out')), 20000);
        worker.onerror = event => { clearTimeout(timer); reject(new Error(event.message)); };
        worker.onmessage = event => { clearTimeout(timer); event.data.type === 'ready' ? resolve() : reject(new Error(event.data.message)); };
        worker.postMessage({ type: 'warmup' });
      });
      return await new Promise(resolve => {
        const timer = setTimeout(() => { worker.terminate(); resolve({ status: 'timeout' }); }, 3000);
        worker.onmessage = event => { clearTimeout(timer); resolve(event.data); };
        worker.postMessage({ signature: problem.signature, tests: problem.tests, source, stopOnFailure: false });
      });
    } finally { worker.terminate(); }
  }, { problem, source });
}

try {
  const workerAsset = await fs.readFile(path.join(root, 'frontend/dist/judge-worker.js'));
  assert.equal(createHash('sha256').update(workerAsset).digest('hex'),
    createHash('sha256').update(await fs.readFile(path.join(root, 'frontend/public/judge-worker.js'))).digest('hex'),
    'Rebuild the frontend before browser validation.');
  await start();
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const pageErrors = [];
  const externalRequests = [];
  await page.route('**/*', route => {
    const url = new URL(route.request().url());
    if ((url.protocol === 'http:' || url.protocol === 'https:') && url.origin !== base) {
      externalRequests.push(url.href);
      return route.abort('blockedbyclient');
    }
    return route.continue();
  });
  page.on('pageerror', error => pageErrors.push(error.message));
  await page.goto(base);
  await page.getByRole('button', { name: 'Library', exact: true }).click();
  const first = JSON.parse(await fs.readFile(path.join(root, 'catalog_data', selected[0].path), 'utf8'));
  await page.getByPlaceholder('Search title, topic, or pattern').fill(first.title);
  await page.locator('button.problem-card').filter({ has: page.getByText(first.title, { exact: true }) }).click();
  await page.getByRole('heading', { name: first.title, exact: true }).waitFor();
  await page.locator('.monaco-editor textarea').waitFor({ state: 'attached' });
  report.checks.push('library search, changed problem detail, and editor render');

  for (const entry of selected) {
    const problem = JSON.parse(await fs.readFile(path.join(root, 'catalog_data', entry.path), 'utf8'));
    const accepted = await judge(page, problem, problem.reference_solution);
    assert.equal(accepted.status, 'accepted', `${entry.id} reference: ${JSON.stringify(accepted)}`);
    assert.equal(accepted.cases.length, problem.tests.length);
    report.worker.push({ id: entry.id, status: accepted.status, cases: accepted.cases.length });
    for (const wrong of problem.known_wrong_solutions) {
      assert.equal((await judge(page, problem, wrong)).status, 'wrong_answer', `${entry.id} wrong algorithm`);
    }
  }
  report.checks.push('every changed reference and both documented wrong algorithms ran in fresh Pyodide workers');

  for (const id of ['leetcode-11', 'tree-max-depth', 'merge-two-sorted-linked-lists']) {
    if (requested.includes(id)) continue;
    const entry = manifest.entries.find(item => item.id === id);
    if (!entry) continue;
    const problem = JSON.parse(await fs.readFile(path.join(root, 'catalog_data', entry.path), 'utf8'));
    assert.equal((await judge(page, problem, problem.reference_solution)).status, 'accepted', `${id} smoke reference`);
  }
  const smoke = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-11.json'), 'utf8'));
  for (const [expected, source] of [
    ['wrong_answer', 'def max_water_area(height):\n    return -1'],
    ['syntax_error', 'def max_water_area(:'],
    ['runtime_error', 'def max_water_area(height):\n    raise ValueError("test")'],
    ['timeout', 'def max_water_area(height):\n    while True: pass'],
    ['accepted', smoke.reference_solution],
  ]) assert.equal((await judge(page, smoke, source)).status, expected, `judge recovery ${expected}`);
  report.checks.push('array/tree/list smoke references and five judge result categories');

  const health = await (await fetch(`${base}/api/health`)).json();
  assert.equal(health.problemCount, manifest.count);
  const search = await (await fetch(`${base}/api/problems?search=${encodeURIComponent(first.title)}`)).json();
  assert(search.items.some(item => item.id === first.id));
  assert.equal((await fetch(`${base}/api/problems/${first.id}`)).status, 200);
  assert.deepEqual(pageErrors, []);
  assert.deepEqual(externalRequests, []);
  report.checks.push('health, search, detail API, blocked external assets, and no page errors');
  if (reportPath) {
    assert(reportPath.startsWith(`${root}${path.sep}catalog_import${path.sep}benchmarks${path.sep}`),
      '--report must be under catalog_import/benchmarks.');
    await fs.mkdir(path.dirname(reportPath), { recursive: true });
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
  }
  console.log(JSON.stringify(report));
} finally {
  if (browser) await browser.close();
  await stop();
  await fs.rm(temp, { recursive: true, force: true });
}
