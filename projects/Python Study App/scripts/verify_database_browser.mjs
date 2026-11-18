// Local end-to-end test and per-problem verification with a disposable profile store.
import { sweep } from './database_catalog_sweep.mjs';
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
import json, hashlib
from datetime import timedelta
from uuid import uuid4
from code_practice import accounts, database, database_track, review_v2
from code_practice.database_catalog import CATALOG, INVENTORY, pandas_starter
accounts.initialize('admin')
accounts.set_password('owner','owner-local-test-password')
user = accounts.create_user('database-member','member-local-test-password')
accounts.set_password(user['id'],'member-local-test-password')
reviewer = accounts.create_user('database-reviewer','reviewer-local-test-password')
accounts.set_password(reviewer['id'],'reviewer-local-test-password')
earlier = review_v2.local_day() - timedelta(days=21)
with database.profile_scope(reviewer['id']), database.db_session() as con:
    for key in (175,176):
        con.execute("INSERT INTO db_track_attempts VALUES (?,?,?,?,?,?,?,?)",
                    (str(uuid4()),key,'mysql','practice',str(earlier),CATALOG[key]['sql'],1,'{}'))
        database_track.save_event(con,key,earlier)
print(json.dumps([{'id': k, 'sql': v['sql'], 'pandas': pandas_starter(v, reference=True), 'wrong': v['wrong'], 'wrongPandas':[pandas_starter(v,body=b) for b in v['wrong_pandas']],
                    'contract':hashlib.sha256(json.dumps([v, INVENTORY[k]],ensure_ascii=False).encode()).hexdigest()}
                  for k,v in CATALOG.items()]))
`], { cwd: root, env, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 });
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
async function edit(page, source) {
  // getEditors() initializes Monaco services. Wait for the actual editor to finish loading first.
  await page.locator('.monaco-editor:visible .view-lines').first().waitFor();
  const handle = await page.waitForFunction(() => window.monaco?.editor.getEditors()
    .find(editor => editor.getDomNode()?.offsetWidth > 0 && editor.getModel()));
  try { await handle.evaluate((editor, value) => editor.getModel().setValue(value), source); }
  finally { await handle.dispose(); }
}

try {
  await start();
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 990 } });
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  await login(page, 'admin', 'owner-local-test-password');
  if (!process.argv.includes('--catalog-only')) {
  const before = await get(page, '/api/dashboard');
  await page.getByRole('button', { name: 'Library', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Pair Sum Indices');
  await page.getByRole('button', { name: /Pair Sum Indices/ }).click();
  await page.locator('.monaco-editor .view-lines').waitFor();
  const pairSum = 'def pair_sum_indices(nums, target):\n    seen = {}\n    for i, value in enumerate(nums):\n        if target - value in seen:\n            return [seen[target - value], i]\n        seen[value] = i\n    return []\n';
  await edit(page, pairSum);
  await Promise.all([
    page.waitForResponse(res => res.url().endsWith('/api/attempts') && res.ok(), { timeout: 30000 }),
    page.getByRole('button', { name: 'Submit', exact: true }).click(),
  ]);
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
  const desktop = page.viewportSize();
  for (const viewport of [{ width: 390, height: 844 }, { width: 844, height: 390 },
    { width: 390, height: 844 }, { width: 920, height: 800 }, { width: 1024, height: 800 }, desktop]) {
    await page.setViewportSize(viewport);
    await page.waitForFunction(() => {
      const pane = document.querySelector('[aria-label="Database editor"]');
      const bounds = pane.getBoundingClientRect();
      const code = pane.querySelector('.monaco-editor').getBoundingClientRect();
      const submit = pane.querySelector('.submit-button').getBoundingClientRect();
      return Math.abs(code.width - bounds.width) <= 2 && submit.right <= Math.min(bounds.right, innerWidth) + 1
        && document.documentElement.scrollWidth <= innerWidth + 1;
    });
  }
  console.log('Editor and Submit stayed within the Database pane across rotation and desktop resizing.');
  const splitter = page.getByRole('separator', { name: 'Resize instructions and code panels' });
  const algoSplit = await page.evaluate(() => localStorage.getItem('code-practice-workspace-split'));
  await splitter.press('ArrowRight');
  assert.equal(await splitter.getAttribute('aria-valuenow'), '44');
  assert.equal(await page.evaluate(() => localStorage.getItem('code-practice-workspace-split')), algoSplit);
  await splitter.dblclick();
  assert.equal(await splitter.getAttribute('aria-valuenow'), '42');
  await edit(page, '-- MySQL draft');
  await page.getByRole('button', { name: 'Pandas', exact: true }).click();
  await page.getByRole('button', { name: 'Pandas', exact: true, pressed: true }).waitFor();
  await edit(page, '# Pandas draft');
  await page.getByRole('button', { name: 'MySQL', exact: true }).click();
  await page.getByRole('button', { name: 'MySQL', exact: true, pressed: true }).waitFor();
  await page.waitForFunction(() => window.monaco.editor.getEditors().some(e => e.getDomNode()?.offsetWidth && e.getValue() === '-- MySQL draft'));
  await page.locator('[aria-label="Database editor"]').getByRole('button', { name: 'Reset' }).click();
  assert.equal((await get(page, detailPath)).drafts.pandas, '# Pandas draft');
  const starter = (await get(page, detailPath)).starters.mysql;
  await page.waitForFunction(code => window.monaco.editor.getEditors().some(e => e.getDomNode()?.offsetWidth && e.getValue() === code), starter);
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
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByRole('heading', { name: 'Database Today' }).waitFor();
  const checkedCard = page.getByRole('button', { name: itemName });
  await checkedCard.getByText('Done today', { exact: true }).waitFor();
  const fullSet = (await get(page, '/api/dashboard')).database;
  assert.deepEqual(fullSet.dailyAssignment.map(p => p.id), before.database.dailyAssignment.map(p => p.id));
  assert.deepEqual(fullSet.dailyAssignment.filter(p => p.completedToday).map(p => p.id), [item.id]);
  await page.getByRole('button', { name: 'Browse all' }).click();
  await page.getByLabel('Filter by completion').selectOption('passed');
  await page.getByRole('button', { name: itemName }).click();
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByRole('heading', { name: 'Database Library' }).waitFor();
  assert.equal(await page.getByLabel('Filter by completion').inputValue(), 'passed');
  assert.equal(new URL(page.url()).searchParams.get('completion'), 'passed');

  const memberPage = await browser.newPage();
  await login(memberPage, 'database-member', 'member-local-test-password', '/database/problem/' + item.id);
  await memberPage.getByRole('heading', { name: itemName }).waitFor();
  assert.equal(new URL(memberPage.url()).pathname, '/database/problem/' + item.id);
  assert.equal((await get(memberPage, '/api/dashboard')).database.solved, 0);
  assert.deepEqual((await get(memberPage, detailPath)).drafts, {});
  // Submit to the same problem from separate signed-in accounts at the same time.
  const parallel = references.find(row => row.id === 185);
  const path185 = '/api/database/problems/185';
  await Promise.all([page, memberPage].map(async (tab, index) => {
    await tab.goto(base + '/database/problem/185');
    const label = index === 0 ? 'MySQL' : 'Pandas';
    const code = index === 0 ? parallel.sql : parallel.pandas;
    await tab.getByRole('button', { name: label, exact: true }).click();
    await tab.getByRole('button', { name: label, exact: true, pressed: true }).waitFor();
    await edit(tab, code);
  }));
  await Promise.all([page, memberPage].map(async (tab, index) => {
    const label = index === 0 ? 'MySQL' : 'Pandas';
    await tab.getByRole('button', {name:'Submit',exact:true}).click();
    await tab.getByRole('button', {name:label + ' · Passed',exact:true}).waitFor({ timeout:60000 });
    const saved = await get(tab, path185);
    assert.deepEqual(saved.passedLanguages, [label.toLowerCase()]);
    assert.equal(saved.drafts[label.toLowerCase()], index === 0 ? parallel.sql : parallel.pandas);
  }));
  await memberPage.close();

  const reviewer = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  reviewer.on('pageerror', error => errors.push(String(error)));
  await login(reviewer, 'database-reviewer', 'reviewer-local-test-password', '/database/review');
  const reviewCard = reviewer.getByRole('button', { name: /^175\. / });
  await reviewCard.waitFor();
  assert.equal(await reviewCard.locator('.passed-label').count(), 0);
  await reviewCard.click();
  const sql = references.find(p => p.id === 175).sql;
  await edit(reviewer, sql);
  await reviewer.getByRole('button', { name: 'Run examples' }).click();
  await reviewer.getByRole('heading', { name: 'All cases passed' }).waitFor();
  await reviewer.getByRole('button', { name: 'Back', exact: true }).click();
  await reviewCard.waitFor();
  assert.equal(await reviewCard.locator('.passed-label').count(), 0);
  await reviewCard.click();
  await reviewer.locator('[aria-label="Database editor"] .monaco-editor .view-lines').waitFor();
  await reviewer.getByRole('button', { name: 'Submit', exact: true }).click();
  await reviewer.getByText('This problem is marked Passed and saved to your progress.').waitFor();
  await reviewer.getByRole('button', { name: 'Back', exact: true }).click();
  await reviewCard.getByText('Done today', { exact: true }).waitFor();
  await reviewer.reload();
  await reviewCard.getByText('Done today', { exact: true }).waitFor();
  assert.equal(await reviewer.getByRole('button', { name: /^176\. / }).locator('.passed-label').count(), 0);
  const overview = (await get(reviewer, '/api/dashboard')).database;
  assert.equal(overview.reviewAssignment.length, 2);
  assert.equal(overview.reviews.length, 1);
  const scores = reviewer.locator('.review-scores:visible');
  await scores.locator('summary').first().click();
  await scores.getByLabel('Filter review status').selectOption('assigned');
  await reviewer.waitForFunction(() => [...document.querySelectorAll('.review-scores')]
    .some(table => table.offsetWidth && table.querySelectorAll('tbody tr').length === 2));
  await reviewer.getByRole('button', { name: 'Today', exact: true }).click();
  const newItem = overview.newProblems[0];
  const newCard = reviewer.getByRole('button', { name: new RegExp('^' + newItem.id + '\\. ') });
  await newCard.click();
  await edit(reviewer, references.find(p => p.id === newItem.id).sql);
  await reviewer.getByRole('button', { name: 'Submit', exact: true }).click();
  await reviewer.getByText('This problem is marked Passed and saved to your progress.').waitFor();
  await reviewer.getByRole('button', { name: 'Back', exact: true }).click();
  await newCard.getByText('Done today', { exact: true }).waitFor();
  await reviewCard.getByText('Done today', { exact: true }).waitFor();
  await reviewer.getByRole('heading', { name: 'Your next problems' }).evaluate(node => node.scrollIntoView());
  await reviewer.screenshot({ path: path.join(temporary, 'database-checklist.png') });
  await reviewer.close();
  console.log('Daily and review checkmarks persist in place. Back restores Today, Review and filtered Library.');

  console.log('Both drafts and account isolation verified after restart.');
  }
  if (!process.argv.includes('--ui-only')) await sweep({page, base, get, edit, root, temporary, references,
    frontend: env.CODE_PRACTICE_FRONTEND_DIST, errors});
} finally {
  await browser?.close();
  await stop();
}
