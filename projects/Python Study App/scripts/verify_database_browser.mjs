// Local end-to-end test and per-problem verification with a disposable profile store.
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from '../frontend/node_modules/playwright/index.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'database-track-browser-'));
const portServer = net.createServer();
await new Promise(resolve => portServer.listen(0, '127.0.0.1', resolve));
const port = portServer.address().port;
await new Promise(resolve => portServer.close(resolve));
const base = `http://127.0.0.1:${port}`;
const python = path.join(root, '.venv/bin/python');
const env = {
  ...process.env, CODE_PRACTICE_DATA_DIR: temporary, CODE_PRACTICE_DB: path.join(temporary, 'owner.db'),
  CODE_PRACTICE_FRONTEND_DIST: process.env.CODE_PRACTICE_FRONTEND_DIST || path.join(root, 'frontend/dist-local'),
  CODE_PRACTICE_SEED_DB: '', CODE_PRACTICE_AUTH_USERNAME: '', CODE_PRACTICE_SESSION_SECRET: '',
  CODE_PRACTICE_REQUIRE_LOGIN: '1', CODE_PRACTICE_PUBLIC_ORIGIN: base,
};
const setup = spawnSync(python, ['-c', `
import json
from code_practice import accounts
from code_practice.database_catalog import CATALOG,pandas_starter
accounts.initialize('admin')
accounts.set_password('owner','owner-local-test-password')
user = accounts.create_user('database-member','member-local-test-password')
accounts.set_password(user['id'],'member-local-test-password')
print(json.dumps([{'id': k, 'sql': v['sql'], 'pandas': pandas_starter(v, reference=True), 'wrong': v['wrong']}
                  for k,v in CATALOG.items()]))
`], { cwd: root, env, encoding: 'utf8' });
assert.equal(setup.status, 0, setup.stderr);
const references = JSON.parse(setup.stdout);
let server, browser;
async function start() {
  server = spawn(python, ['-m', 'uvicorn', 'code_practice.app:app', '--host', '127.0.0.1', '--port', String(port)],
    { cwd: root, env, stdio: ['ignore', 'ignore', 'pipe'] });
  let errors = '';
  server.stderr.on('data', data => { errors += data; });
  for (let i = 0; i < 100; i++) {
    if (server.exitCode !== null) throw new Error(errors);
    if (await fetch(base + '/api/health').then(r => r.ok).catch(() => false)) return;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error(errors || 'Server did not start');
}
async function stop() {
  if (server?.exitCode === null) {
    const exited = once(server, 'exit');
    server.kill('SIGTERM');
    await exited;
  }
}
async function login(page, username, password, entry = '/') {
  await page.goto(base + entry);
  await page.getByLabel('Username', { exact: true }).fill(username);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.getByRole('button', { name: 'Sign in', exact: true }).click();
  await page.getByRole('button', { name: /^Database/ }).waitFor();
}
const get = (page, url) => page.evaluate(async endpoint => {
  const res = await fetch(endpoint);
  if (!res.ok) throw Error(await res.text());
  return res.json();
}, url);
const edit = (page, source) => page.evaluate(value => {
  const active = window.monaco.editor.getEditors().find(editor => editor.getDomNode()?.offsetWidth > 0);
  active.getModel().setValue(value);
}, source);

try {
  await start();
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 990 } });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  await login(page, 'admin', 'owner-local-test-password');
  const before = await get(page, '/api/dashboard');
  await page.getByRole('button', { name: 'Library', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Pair Sum Indices');
  await page.getByRole('button', { name: /Pair Sum Indices/ }).click();
  await page.locator('.monaco-editor .view-lines').waitFor();
  const pairSum = 'def pair_sum_indices(nums, target):\n    seen = {}\n    for i, value in enumerate(nums):\n        if target - value in seen:\n            return [seen[target - value], i]\n        seen[value] = i\n    return []\n';
  await edit(page, pairSum);
  await page.getByRole('button', { name: 'Submit', exact: true }).click();
  await page.waitForResponse(res => res.url().endsWith('/api/attempts') && res.ok(), { timeout: 30000 });
  console.log('Algorithm submission recorded.');
  const afterAlgo = await get(page, '/api/dashboard');
  assert.equal(afterAlgo.solvedCount, before.solvedCount + 1);
  assert.deepEqual(afterAlgo.database, before.database);

  await page.getByRole('button', { name: /^Database/ }).click();
  await page.getByRole('heading', { name: 'Database Today' }).waitFor();
  const item = before.database.newProblems[0];
  const target = references.find(reference => reference.id === item.id);
  const itemName = new RegExp(`^${item.id}\\. `);
  const detailPath = `/api/database/problems/${item.id}`;
  await page.getByRole('button', { name: itemName }).click();
  await page.locator('[aria-label="Database editor"] .monaco-editor .view-lines').waitFor();
  await edit(page, target.sql);
  await page.getByRole('button', { name: 'Run examples', exact: true }).click();
  await page.getByRole('heading', { name: 'All cases passed' }).waitFor({ timeout: 30000 });
  assert.equal((await get(page, '/api/dashboard')).database.solved, 0);
  await page.getByRole('button', { name: 'Submit', exact: true }).click();
  await page.getByRole('heading', { name: 'All cases passed' }).waitFor({ timeout: 60000 });
  await page.getByRole('button', { name: 'MySQL · Passed', exact: true }).waitFor();
  const afterDb = await get(page, '/api/dashboard');
  assert.equal(afterDb.solvedCount, afterAlgo.solvedCount);
  assert.equal(afterDb.database.newProblems.length, before.database.newProblems.length - 1);
  await page.getByRole('button', { name: 'Pandas', exact: true }).click();
  await page.getByRole('button', { name: 'Pandas', exact: true, pressed: true }).waitFor();
  await edit(page, target.pandas);
  await page.getByRole('button', { name: 'Submit', exact: true }).click();
  await page.getByRole('button', { name: 'Pandas · Passed', exact: true }).waitFor({ timeout: 60000 });
  assert.equal((await get(page, '/api/dashboard')).database.solved, 1);
  console.log('Both Database languages passed in the editor.');
  await page.screenshot({ path: path.join(temporary, 'database-editor.png'), fullPage: false });
  const location = page.url();
  await stop();
  await start();
  await page.reload();
  await page.getByRole('heading', { name: itemName }).waitFor();
  assert.equal(page.url(), location);
  const restored = await get(page, detailPath);
  assert.deepEqual(restored.drafts, { mysql: target.sql, pandas: target.pandas });
  assert.deepEqual(restored.passedLanguages, ['mysql', 'pandas']);

  const memberPage = await browser.newPage();
  await login(memberPage, 'database-member', 'member-local-test-password', '/database/problem/' + item.id);
  await memberPage.getByRole('heading', { name: itemName }).waitFor();
  assert.equal(new URL(memberPage.url()).pathname, '/database/problem/' + item.id);
  assert.equal((await get(memberPage, '/api/dashboard')).database.solved, 0);
  assert.deepEqual((await get(memberPage, detailPath)).drafts, {});
  await memberPage.close();

  console.log('Both drafts and account isolation verified after restart.');
  const report = [];
  for (const entry of process.argv.includes('--ui-only') ? [] : references) {
    const outcomes = await page.evaluate(async ({ entry }) => {
      const session = await fetch('/api/auth/me').then(response => response.json());
      const headers = { 'Content-Type': 'application/json', 'X-Requested-With': 'CodePractice',
        'X-Study-Profile': session.user.id };
      const endpoint = `/api/database/problems/${entry.id}`;
      const grade = async (source, language, results) => {
        const response = await fetch(endpoint + '/judge', { method: 'POST', headers, body: JSON.stringify({
          source, language, results, request_id: crypto.randomUUID(),
        }) });
        if (!response.ok) throw Error(await response.text());
        return response.json();
      };
      const pack = await fetch(endpoint + '/pandas-cases', { headers }).then(response => response.json());
      const output = await new Promise((resolve, reject) => {
        const worker = new Worker('/database-worker.js');
        const timer = setTimeout(() => { worker.terminate(); reject(Error('Pandas timeout')); }, 30000);
        worker.onmessage = ({ data }) => {
          if (data.ready) return;
          clearTimeout(timer);
          worker.terminate();
          if (data.error) reject(Error(data.error));
          else resolve(data.results);
        };
        worker.postMessage({ ...pack, source: entry.pandas });
      });
      const mysql = await grade(entry.sql, 'mysql');
      const pandas = await grade(entry.pandas, 'pandas', output);
      const rejected = [];
      for (const wrong of entry.wrong) {
        rejected.push(!(await grade(wrong, 'mysql')).accepted);
      }
      return { mysql, pandas, rejected };
    }, { entry });
    assert.ok(outcomes.mysql.accepted, JSON.stringify({ id: entry.id, mysql: outcomes.mysql.cases.filter(c => !c.passed) }));
    assert.ok(outcomes.pandas.accepted, JSON.stringify({ id: entry.id, pandas: outcomes.pandas.cases.filter(c => !c.passed) }));
    assert.deepEqual(outcomes.rejected, [true, true], `Incorrect answers must fail on #${entry.id}`);
    const row = { id: entry.id, mysqlCases: outcomes.mysql.cases.length, pandasCases: outcomes.pandas.cases.length,
      wrongAnswersRejected: outcomes.rejected.length };
    report.push(row);
    console.log(JSON.stringify(row));
  }
  assert.deepEqual(errors, []);
  const inventory = JSON.parse(await fs.readFile(path.join(root, 'database_catalog/inventory.json')));
  const combinations = inventory.flatMap(problem => ['mysql', 'pandas'].map(language => {
    const result = report.find(row => row.id === problem.id);
    return { id: problem.id, language, status: result ? 'passed' : 'pending',
      ...(result && { cases: result[language + 'Cases'] }) };
  }));
  await fs.writeFile(path.join(temporary, 'report.json'),
    JSON.stringify({ total: inventory.length, passed: report.length * 2, combinations,
      ...(report.length && { wrongAnswerChecks: { language: 'mysql', rejectedPerVerifiedProblem: 2 } }) }, null, 2) + '\n');
  console.log('Report and screenshot stored in ' + temporary);
} finally {
  await browser?.close();
  await stop();
}
