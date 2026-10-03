// Exercises the deployed build with isolated accounts and progress, never live data.
import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { chromium } = await import(pathToFileURL(path.join(root, 'frontend/node_modules/playwright/index.mjs')).href);
const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'study-account-check-'));
const socket = net.createServer();
await new Promise((resolve, reject) => { socket.once('error', reject); socket.listen(0, '127.0.0.1', resolve); });
const port = socket.address().port;
await new Promise(resolve => socket.close(resolve));
const base = `http://127.0.0.1:${port}`;
const env = { ...process.env, CODE_PRACTICE_DATA_DIR: temporary,
  CODE_PRACTICE_DB: path.join(temporary, 'code_practice.db'), CODE_PRACTICE_SEED_DB: '',
  CODE_PRACTICE_AUTH_USERNAME: '', CODE_PRACTICE_SESSION_SECRET: '',
  CODE_PRACTICE_REQUIRE_LOGIN: '1', CODE_PRACTICE_PUBLIC_ORIGIN: base };
const python = path.join(root, '.venv/bin/python');
const setup = spawnSync(python, ['-c', "from code_practice import accounts,database; accounts.initialize('admin'); accounts.set_password('owner','owner-test-password'); database.save_draft('pair-sum-indices','# original owner draft')"], { cwd: root, env, encoding: 'utf8' });
assert.equal(setup.status, 0, setup.stderr);
let server, browser;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function start() {
  server = spawn(python, ['-m', 'uvicorn', 'code_practice.app:app', '--host', '127.0.0.1', '--port', String(port)], { cwd: root, env, stdio: ['ignore', 'ignore', 'pipe'] });
  let errors = '';
  server.stderr.on('data', data => { errors += data; });
  for (let i = 0; i < 100; i++) {
    if (server.exitCode !== null) throw new Error(errors);
    try { if ((await fetch(`${base}/api/health`)).ok) return; } catch {}
    await sleep(100);
  }
  throw new Error(errors || 'Server startup timed out');
}
async function stop() {
  if (server && server.exitCode === null) {
    const exited = new Promise(resolve => server.once('exit', resolve));
    server.kill('SIGTERM'); await exited;
  }
}
async function login(page, username, password) {
  await page.getByLabel('Username', { exact: true }).fill(username);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
}
async function detail(page) {
  return page.evaluate(async () => (await fetch('/api/problems/pair-sum-indices')).json());
}
const source = 'def pair_sum_indices(nums, target):\n    seen = {}\n    for i, value in enumerate(nums):\n        if target - value in seen:\n            return [seen[target - value], i]\n        seen[value] = i\n    return []\n';
try {
  await start();
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto(base);
  await login(page, 'admin', 'owner-test-password');
  await page.getByRole('button', { name: 'Accounts', exact: true }).click();
  await page.getByLabel('New username').fill('browser-student');
  await page.getByLabel('Temporary password', { exact: true }).fill('temporary-student-password');
  await page.getByRole('button', { name: 'Create account', exact: true }).click();
  await page.getByText('browser-student', { exact: true }).waitFor();
  await page.screenshot({ path: path.join(temporary, 'admin-accounts.png'), fullPage: true });
  await page.getByRole('button', { name: 'Sign out', exact: true }).click();
  await login(page, 'browser-student', 'temporary-student-password');
  await page.getByLabel('Current password').fill('temporary-student-password');
  await page.getByLabel('New password', { exact: true }).fill('personal-student-password');
  await page.getByLabel('Confirm new password').fill('personal-student-password');
  await page.getByRole('button', { name: 'Save password', exact: true }).click();
  await page.getByRole('button', { name: 'My account', exact: true }).waitFor();
  assert.equal(await page.getByRole('button', { name: 'Accounts', exact: true }).count(), 0);
  assert.notEqual((await detail(page)).savedDraft, '# original owner draft');
  await page.getByRole('button', { name: 'Library', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Pair Sum Indices');
  await page.getByRole('button', { name: /Pair Sum Indices/ }).click();
  await page.locator('.monaco-editor .view-lines').waitFor();
  // Monaco's model API avoids keyboard auto-indentation changing the test code.
  await page.evaluate(value => window.monaco.editor.getModels()[0].setValue(value), source);
  await page.waitForResponse(response => response.url().endsWith('/pair-sum-indices/draft') && response.request().method() === 'PUT' && response.ok());
  await page.getByRole('button', { name: 'Run examples', exact: true }).click();
  await page.getByText('Examples passed', { exact: true }).waitFor({ timeout: 30000 });
  await page.getByRole('button', { name: 'Submit', exact: true }).click();
  await page.waitForResponse(response => response.url().endsWith('/api/attempts') && response.ok(), { timeout: 30000 });
  assert.equal((await detail(page)).solved, true);
  await stop(); await start();
  await page.reload();
  await page.getByRole('button', { name: 'My account', exact: true }).click();
  const persisted = await detail(page);
  assert.equal(persisted.savedDraft, source); assert.equal(persisted.solved, true);
  await page.getByRole('button', { name: 'Sign out', exact: true }).click();
  await login(page, 'admin', 'owner-test-password');
  await page.getByRole('button', { name: 'Accounts', exact: true }).waitFor();
  const owner = await detail(page);
  assert.equal(owner.savedDraft, '# original owner draft'); assert.equal(owner.solved, false);
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ passed: true, checks: ['admin creates account', 'temporary password replacement', 'member runs Pyodide examples and submits', 'profile isolation', 'restart persistence', 'owner progress preserved'], screenshot: path.join(temporary, 'admin-accounts.png') }));
} finally {
  await browser?.close(); await stop();
}
