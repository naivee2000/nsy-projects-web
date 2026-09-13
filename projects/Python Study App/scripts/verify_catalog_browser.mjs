// Isolated Chrome/Pyodide smoke test and real-HTTP benchmark. Never touches live progress.
// Install Playwright for this optional development check, or set PLAYWRIGHT_MODULE.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE ? pathToFileURL(process.env.PLAYWRIGHT_MODULE).href : 'playwright');
const temp = await fs.mkdtemp(path.join(os.tmpdir(), 'code-practice-catalog-check-'));
const socket = net.createServer();
await new Promise(resolve => socket.listen(0, '127.0.0.1', resolve));
const port = socket.address().port;
await new Promise(resolve => socket.close(resolve));
const base = `http://127.0.0.1:${port}`;
const python = process.env.CODE_PRACTICE_PYTHON || path.join(root, '.venv/bin/python');
let server, browser, startupMs, memoryReportPath, runNumber = 0;
const serverMemoryRuns = [];
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const manifestPath = path.join(root, 'catalog_data/manifest.json');
const ledgerPath = path.join(root, 'catalog_import/ledger.json');
const manifestText = await fs.readFile(manifestPath, 'utf8');
const ledgerText = await fs.readFile(ledgerPath, 'utf8');
const manifest = JSON.parse(manifestText);
const ledger = JSON.parse(ledgerText);
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const judgeHash = createHash('sha256');
for (const name of ['code_practice/schemas.py', 'code_practice/validation.py', 'frontend/public/judge-worker.js']) {
  judgeHash.update(name);
  judgeHash.update(await fs.readFile(path.join(root, name)));
}
const workerAsset = await fs.readFile(path.join(root, 'frontend/dist/judge-worker.js'));
assert.equal(sha256(workerAsset), sha256(await fs.readFile(path.join(root, 'frontend/public/judge-worker.js'))),
  'Rebuild the frontend before verifying a changed judge worker');
const report = { scope: 'Current published catalog; not the final full-catalog acceptance benchmark',
  catalogCount: manifest.count, workbookCounts: ledger.counts, generatedAt: new Date().toISOString(),
  catalogManifestSha256: createHash('sha256').update(manifestText).digest('hex'),
  ledgerSha256: createHash('sha256').update(ledgerText).digest('hex'),
  judgeContractSha256: judgeHash.digest('hex'),
  workerAssetSha256: sha256(workerAsset),
  frontendIndexSha256: sha256(await fs.readFile(path.join(root, 'frontend/dist/index.html'))),
  browserVerifierSha256: sha256(await fs.readFile(fileURLToPath(import.meta.url))),
  hardware: { platform: os.platform(), architecture: os.arch(), cpu: os.cpus()[0].model, memoryGiB: os.totalmem() / 2**30 },
  worker: [], endpoints: {}, checks: [] };

async function start() {
  const started = performance.now();
  memoryReportPath = path.join(temp, `server-memory-${++runNumber}.json`);
  server = spawn(python, [path.join(root, 'scripts/benchmark_server.py'), '--port', String(port), '--memory-report', memoryReportPath], {
    cwd: root, env: { ...process.env, CODE_PRACTICE_DATA_DIR: temp,
      CODE_PRACTICE_DB: path.join(temp, 'progress.db'), CODE_PRACTICE_SEED_DB: '',
      CODE_PRACTICE_AUTH_USERNAME: '', CODE_PRACTICE_SESSION_SECRET: '',
      CODE_PRACTICE_CATALOG_DIR: path.join(root, 'catalog_data') }, stdio: ['ignore', 'ignore', 'pipe'],
  });
  let stderr = '';
  server.stderr.on('data', data => { stderr += data; });
  for (let i = 0; i < 100; i++) {
    if (server.exitCode !== null) throw new Error(stderr);
    try {
      const response = await fetch(`${base}/api/health`);
      if (response.ok) { startupMs = performance.now() - started; return; }
    } catch {}
    await sleep(100);
  }
  throw new Error(`Server did not become healthy: ${stderr}`);
}

async function stop() {
  if (server && server.exitCode === null) {
    const exited = new Promise(resolve => server.once('exit', resolve));
    server.kill('SIGTERM');
    await exited;
    const memory = JSON.parse(await fs.readFile(memoryReportPath, 'utf8'));
    assert(memory.peakRssBytes > 0, 'OS peak RSS must be available');
    serverMemoryRuns.push(memory);
    server = null;
  }
}

async function request(route, body, method = 'POST') {
  const response = await fetch(base + route, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  assert(response.ok, `${route}: ${await response.clone().text()}`);
  return response.json();
}

async function judge(page, problem, source) {
  return page.evaluate(async ({ problem, source }) => {
    const worker = new Worker('/judge-worker.js');
    try {
      await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Pyodide warmup timed out')), 20000);
        worker.onerror = event => { clearTimeout(timer); reject(new Error(event.message)); };
        worker.onmessage = event => {
          clearTimeout(timer);
          if (event.data.type === 'ready') resolve();
          else reject(new Error(event.data.message));
        };
        worker.postMessage({ type: 'warmup' });
      });
      const started = performance.now();
      return await new Promise(resolve => {
        const timer = setTimeout(() => { worker.terminate(); resolve({ status: 'timeout', runtimeMs: performance.now() - started }); }, 3000);
        worker.onmessage = event => { clearTimeout(timer); resolve(event.data); };
        worker.postMessage({ signature: problem.signature, tests: problem.tests, source, stopOnFailure: false });
      });
    } finally { worker.terminate(); }
  }, { problem, source });
}

try {
  await start();
  report.startupMs = Math.round(startupMs);
  browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  const externalRequests = [];
  await page.route('**/*', route => {
    const url = new URL(route.request().url());
    if ((url.protocol === 'http:' || url.protocol === 'https:') && url.origin !== base) {
      externalRequests.push(url.href);
      return route.abort('blockedbyclient');
    }
    return route.continue();
  });
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(base);
  await page.getByRole('button', { name: 'Library', exact: true }).click();
  await page.getByRole('button', { name: 'Next', exact: true }).waitFor();
  await page.waitForFunction(() => document.querySelectorAll('.library-list .problem-card').length === 30);
  await page.getByRole('button', { name: 'Next', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('.library-pagination')?.textContent.includes('Page 2 of'));
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Word Search');
  await page.getByRole('button', { name: /Word Search.*Medium/ }).click();
  await page.getByRole('heading', { name: 'Word Search', exact: true }).waitFor();
  await page.locator('.monaco-editor textarea').waitFor({ state: 'attached' });
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  assert.equal(await page.getByPlaceholder('Search title, topic, or pattern').inputValue(), 'Word Search');
  report.checks.push('pagination, server search, problem open, back with search retained');
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Remove Duplicates from Sorted Array');
  await page.getByRole('button', { name: /Remove Duplicates from Sorted Array.*Easy/ }).click();
  await page.getByRole('note').waitFor();
  assert((await page.getByRole('note').textContent()).includes('return the integer count k'));
  assert((await page.locator('.example code').first().textContent()).includes('"prefix"'));
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Rotate Image');
  await page.getByRole('button', { name: /Rotate Image.*Medium/ }).click();
  await page.getByRole('note').waitFor();
  assert((await page.getByRole('note').textContent()).includes('a returned copy is not used'));
  report.checks.push('in-place and returned-prefix judging explanations render with the published examples');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Delete Node in a Linked List');
  await page.getByRole('button', { name: /Delete Node in a Linked List.*Easy/ }).click();
  await page.getByRole('note').waitFor();
  assert((await page.getByRole('note').textContent()).includes('actual non-tail node'));
  assert((await page.locator('.example code').first().textContent()).includes('"index":1'));
  report.checks.push('selected linked-node input and full-list mutation judging are explained beside examples');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Convert Sorted Array to Binary Search Tree');
  await page.getByRole('button', { name: /Convert Sorted Array to Binary Search Tree.*Easy/ }).click();
  await page.getByRole('note').waitFor();
  assert((await page.getByRole('note').textContent()).includes('exact shape is not required'));
  assert((await page.locator('.example code').first().textContent()).includes('One valid output'));
  report.checks.push('balanced tree examples explain that multiple output shapes are valid');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Wiggle Sort');
  await page.getByRole('button', { name: /Wiggle Sort.*Easy/ }).click();
  const wiggleNote = page.getByRole('note').filter({ hasText: 'Flexible wiggle judging' });
  await wiggleNote.waitFor();
  assert((await wiggleNote.textContent()).includes('any permutation'));
  assert((await page.locator('.example code').first().textContent()).includes('One valid output'));
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Find the Duplicate Number');
  await page.getByRole('button', { name: /Find the Duplicate Number.*Medium/ }).click();
  const readOnlyNote = page.getByRole('note').filter({ hasText: 'Read-only input judging' });
  await readOnlyNote.waitFor();
  assert((await readOnlyNote.textContent()).includes('remain unchanged'));
  report.checks.push('flexible wiggle outputs and read-only parameters are explained in the problem UI');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Wiggle Sort II');
  await page.getByRole('button', { name: /Wiggle Sort II.*Medium/ }).click();
  const strictWiggleNote = page.getByRole('note').filter({ hasText: 'Strict wiggle judging' });
  await strictWiggleNote.waitFor();
  assert((await strictWiggleNote.textContent()).includes('Adjacent values must not be equal'));
  assert((await page.locator('.example code').first().textContent()).includes('One valid output'));
  report.checks.push('strict wiggle examples explain inequality and multiple valid arrangements');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Find Leaves of Binary Tree');
  await page.getByRole('button', { name: /Find Leaves of Binary Tree.*Medium/ }).click();
  const groupsNote = page.getByRole('note').filter({ hasText: 'Ordered-group judging' });
  await groupsNote.waitFor();
  assert((await groupsNote.textContent()).includes('keep the groups in their required order'));
  assert((await page.locator('.example code').first().textContent()).includes('One valid output'));
  report.checks.push('leaf examples distinguish within-round permutations from chronological group order');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Rotate Array');
  await page.getByRole('button', { name: /Rotate Array.*Medium/ }).click();
  await page.getByRole('note').waitFor();
  assert((await page.getByRole('note').textContent()).includes('a returned copy is not used'));
  report.checks.push('new array-rotation problem explains original-input mutation beside its examples');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Recover Binary Search Tree');
  await page.getByRole('button', { name: /Recover Binary Search Tree.*Medium/ }).click();
  const structureNote = page.getByRole('note').filter({ hasText: 'Tree-structure judging' });
  await structureNote.waitFor();
  assert((await structureNote.textContent()).includes('Temporary traversal links must be restored'));
  report.checks.push('BST recovery explains value changes, preserved original nodes, and restored temporary links');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('UTF-8 Validation');
  await page.getByRole('button', { name: /UTF-8 Validation.*Medium/ }).click();
  assert((await page.locator('.problem-pane .statement').first().textContent()).includes('structural patterns only'));
  report.checks.push('UTF-8 instructions distinguish byte-prefix structure from additional Unicode validity restrictions');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Permutations II');
  await page.getByRole('button', { name: /Permutations II.*Medium/ }).click();
  assert((await page.locator('.problem-pane').textContent()).includes('order inside a permutation matters'));
  report.checks.push('numeric permutations explain outer-order flexibility without discarding row order');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Pacific Atlantic Water Flow');
  await page.getByRole('button', { name: /Pacific Atlantic Water Flow.*Medium/ }).click();
  assert((await page.locator('.problem-pane').textContent()).includes('equal or lower heights'));
  assert((await page.locator('.problem-pane').textContent()).includes('zero-based [row,column]'));
  report.checks.push('ocean-flow instructions explain downhill plateaus and ordered row/column coordinates');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('String Compression');
  await page.getByRole('button', { name: /String Compression.*Medium/ }).click();
  const characterNote = page.getByRole('note').filter({ hasText: 'In-place judging' });
  await characterNote.waitFor();
  assert((await characterNote.textContent()).includes('first k entries of chars'));
  assert((await page.locator('.example code').nth(1).textContent()).includes('"prefix":["a","b","1","2"]'));
  report.checks.push('character compression examples display the returned count and multi-digit mutated character prefix');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Delete Node in a BST');
  await page.getByRole('button', { name: /Delete Node in a BST.*Medium/ }).click();
  const deletionNote = page.getByRole('note').filter({ hasText: 'BST-deletion judging' });
  await deletionNote.waitFor();
  assert((await deletionNote.textContent()).includes('Balancing is not required'));
  assert((await page.locator('.example code').first().textContent()).includes('One valid output'));
  report.checks.push('BST deletion explains surviving-value checks and alternative unbalanced output shapes');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Validate IP Address');
  await page.getByRole('button', { name: /Validate IP Address.*Medium/ }).click();
  assert((await page.locator('.problem-pane').textContent()).includes('compressed :: notation'));
  assert((await page.locator('.problem-pane').textContent()).includes('NOT accepted'));
  report.checks.push('IP examples and constraints explain full eight-group IPv6 and forbid compressed notation');
  await page.getByRole('button', { name: 'Back', exact: true }).click();
  await page.getByPlaceholder('Search title, topic, or pattern').fill('Concatenated Words');
  await page.getByRole('button', { name: /Concatenated Words.*Advanced/ }).click();
  assert((await page.locator('.problem-pane').textContent()).includes('at least two strictly shorter'));
  assert((await page.locator('.problem-pane').textContent()).includes('three pieces'));
  report.checks.push('concatenated-word examples distinguish shorter-word reuse from accepting the unsplit candidate');

  for (const entry of manifest.entries.filter(e => e.source_id !== null || ['matrix-spiral-order', 'tree-max-depth'].includes(e.id))) {
    const problem = JSON.parse(await fs.readFile(path.join(root, 'catalog_data', entry.path), 'utf8'));
    const result = await judge(page, problem, problem.reference_solution);
    assert.equal(result.status, 'accepted', `${entry.id}: ${JSON.stringify(result)}`);
    assert.equal(result.cases.length, problem.tests.length);
    report.worker.push({ id: entry.id, status: result.status, cases: result.cases.length, runtimeMs: result.runtimeMs });
    if (report.worker.length % 25 === 0) console.log(`Verified ${report.worker.length} reference suites in Chrome`);
  }
  for (const id of [148, 149, 156, 164, 186, 189, 203]) {
    const problem = JSON.parse(await fs.readFile(path.join(root, `catalog_data/problems/leetcode-${id}.json`), 'utf8'));
    for (const wrong of problem.known_wrong_solutions) {
      assert.equal((await judge(page, problem, wrong)).status, 'wrong_answer', `leetcode-${id} wrong fixture`);
    }
  }
  for (const id of [386, 388, 390, 393, 394, 395, 397, 402, 403, 408]) {
    const problem = JSON.parse(await fs.readFile(path.join(root, `catalog_data/problems/leetcode-${id}.json`), 'utf8'));
    for (const wrong of problem.known_wrong_solutions) {
      assert.equal((await judge(page, problem, wrong)).status, 'wrong_answer', `leetcode-${id} wrong fixture`);
    }
  }
  report.checks.push('batch 36 wrong algorithms rejected, including incomplete byte groups, nested counts, noncontiguous windows, greedy frog choices, and zero-prefixed abbreviations');
  for (const id of [18, 30, 47, 87, 407, 410, 413, 414]) {
    const problem = JSON.parse(await fs.readFile(path.join(root, `catalog_data/problems/leetcode-${id}.json`), 'utf8'));
    for (const wrong of problem.known_wrong_solutions) {
      assert.equal((await judge(page, problem, wrong)).status, 'wrong_answer', `leetcode-${id} wrong fixture`);
    }
  }
  const permutation = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-47.json'), 'utf8'));
  const permutationCase = { ...permutation, tests: [permutation.tests[0]] };
  assert.equal((await judge(page, permutationCase,
    'def unique_number_permutations(nums):\n    return [[2,1,1],[1,2,1],[1,1,2]]')).status, 'accepted');
  for (const output of ['[[1,1,2]]*3', '[[1,1,2],[1,2,1]]', '[[1,1,2],[1,2,1],[2,1,1],[2,1,1]]']) {
    assert.equal((await judge(page, permutationCase,
      `def unique_number_permutations(nums):\n    return ${output}`)).status, 'wrong_answer');
  }
  report.checks.push('batch 37 wrong algorithms rejected; numeric permutations accept reversed outer order but reject duplicate, missing, and row-order-collapsed results');
  for (const id of [415, 416, 417, 418, 419, 420, 421, 423, 424]) {
    const problem = JSON.parse(await fs.readFile(path.join(root, `catalog_data/problems/leetcode-${id}.json`), 'utf8'));
    for (const wrong of problem.known_wrong_solutions) {
      assert.equal((await judge(page, problem, wrong)).status, 'wrong_answer', `leetcode-${id} wrong fixture`);
    }
  }
  const ocean = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-417.json'), 'utf8'));
  const coordinates = [[0,2],[1,0],[1,1],[1,2]];
  const oceanCase = { ...ocean, tests: [{ id: 'rectangular-coordinates', arguments: [[[1,2,3],[4,5,6]]],
    expected: coordinates, comparator: 'unordered' }] };
  assert.equal((await judge(page, oceanCase,
    `def pacific_atlantic_cells(heights):\n    return ${JSON.stringify([...coordinates].reverse())}`)).status, 'accepted');
  for (const output of [coordinates.map(([r,c]) => [c,r]), [...coordinates,coordinates[0]], coordinates.slice(1)]) {
    assert.equal((await judge(page, oceanCase,
      `def pacific_atlantic_cells(heights):\n    return ${JSON.stringify(output)}`)).status, 'wrong_answer');
  }
  report.checks.push('batch 38 wrong algorithms rejected; ocean coordinates allow outer reorder but reject transposition, missing cells, and duplicates');
  for (const id of [422, 425, 433, 436, 437, 438, 439, 440, 443, 445, 446]) {
    const problem = JSON.parse(await fs.readFile(path.join(root, `catalog_data/problems/leetcode-${id}.json`), 'utf8'));
    for (const wrong of problem.known_wrong_solutions) {
      assert.equal((await judge(page, problem, wrong)).status, 'wrong_answer', `leetcode-${id} wrong fixture`);
    }
  }
  const characterCompression = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-443.json'), 'utf8'));
  const characterCase = { ...characterCompression, tests: [characterCompression.tests[0]] };
  assert.equal((await judge(page, characterCase,
    "def compress_characters(chars):\n    chars[:] = list('a2b2c3Z')\n    return 6")).status, 'accepted');
  for (const body of ["return 6", "return 'a2b2c3'", "chars=list('a2b2c3'); return 6",
    "chars[:6]=list('a2b2c4'); return 6", "chars[:6]=list('a2b2c3'); return True"]) {
    assert.equal((await judge(page, characterCase, `def compress_characters(chars):\n    ${body}`)).status, 'wrong_answer');
  }
  const wordSquares = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-425.json'), 'utf8'));
  const wordSquareCase = { ...wordSquares, tests: [wordSquares.tests[0]] };
  const squareRows = wordSquareCase.tests[0].expected;
  assert.equal((await judge(page, wordSquareCase,
    `def word_squares(words):\n    return ${JSON.stringify([...squareRows].reverse())}`)).status, 'accepted');
  for (const output of [squareRows.map(row => [...row].reverse()), squareRows.slice(1), [...squareRows,squareRows[0]]]) {
    assert.equal((await judge(page, wordSquareCase,
      `def word_squares(words):\n    return ${JSON.stringify(output)}`)).status, 'wrong_answer');
  }
  report.checks.push('batch 39 wrong algorithms rejected; character prefixes enforce original mutation and integer count while ignoring tails; word squares preserve row order and multiplicities');
  for (const id of [450,457,464,466]) {
    const problem = JSON.parse(await fs.readFile(path.join(root, `catalog_data/problems/leetcode-${id}.json`), 'utf8'));
    for (const wrong of problem.known_wrong_solutions) {
      assert.equal((await judge(page, problem, wrong)).status, 'wrong_answer', `leetcode-${id} wrong fixture`);
    }
  }
  const deletion = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-450.json'), 'utf8'));
  const deletionCase = { ...deletion, tests: [{ id: 'two-valid-roots', arguments: [[2,1,3],2],
    expected: [3,1], comparator: 'bst_delete' }] };
  for (const body of ['return TreeNode(3,TreeNode(1))','return TreeNode(1,None,TreeNode(3))']) {
    assert.equal((await judge(page, deletionCase, `def delete_bst_node(root,key):\n    ${body}`)).status, 'accepted');
  }
  for (const body of ['return root','return TreeNode(3)','return TreeNode(1,TreeNode(3))',
    'return TreeNode(3,TreeNode(1),TreeNode(3))']) {
    const failure = await judge(page, deletionCase, `def delete_bst_node(root,key):\n    ${body}`);
    assert.equal(failure.status, 'wrong_answer');
    assert(failure.cases[0].error.includes('Balancing is not required'));
    assert(failure.cases[0].actual !== undefined);
  }
  for (const body of ['return TreeNode(3,TreeNode(1.0))','return TreeNode(True)',
    'root.right=root; return root','child=TreeNode(1); return TreeNode(3,child,child)',
    'return [3,1]']) {
    assert.notEqual((await judge(page, deletionCase, `def delete_bst_node(root,key):\n    ${body}`)).status, 'accepted');
  }
  const unbalancedDeletion = { ...deletion, tests: [{ id: 'no-balance-requirement',
    arguments: [[3,2,4,1],99], expected: [3,2,4,1], comparator: 'bst_delete' }] };
  assert.equal((await judge(page, unbalancedDeletion,
    'def delete_bst_node(root,key):\n    return TreeNode(1,None,TreeNode(2,None,TreeNode(3,None,TreeNode(4))))')).status,'accepted');
  const lastDeletion = { ...deletion, tests: [{ id: 'delete-last', arguments: [[2],2], expected: [], comparator: 'bst_delete' }] };
  assert.equal((await judge(page,lastDeletion,'def delete_bst_node(root,key):\n    return None')).status,'accepted');
  assert.notEqual((await judge(page,lastDeletion,'def delete_bst_node(root,key):\n    return TreeNode(None)')).status,'accepted');
  report.checks.push('batch 40 wrong algorithms rejected; BST deletion accepts predecessor/successor roots and unbalanced shapes while rejecting missing/extra/noninteger values, cycles, shared children and array returns');
  for (const id of [447,448,452,453,454,455,456,459,461,462,467,468]) {
    const problem = JSON.parse(await fs.readFile(path.join(root, `catalog_data/problems/leetcode-${id}.json`), 'utf8'));
    for (const wrong of problem.known_wrong_solutions) {
      assert.equal((await judge(page, problem, wrong)).status, 'wrong_answer', `leetcode-${id} wrong fixture`);
    }
  }
  const missing = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-448.json'), 'utf8'));
  const missingCase = { ...missing, tests: [missing.tests[0]] };
  assert.equal((await judge(page, missingCase, 'def disappeared_numbers(nums):\n    return [6,5]')).status, 'accepted');
  for (const output of ['[5]', '[5,5,6]', '[4,6]']) {
    assert.equal((await judge(page, missingCase, `def disappeared_numbers(nums):\n    return ${output}`)).status, 'wrong_answer');
  }
  report.checks.push('batch 41 wrong algorithms rejected: ordered geometry, interval endpoints, distinct move rules, index multiplicities, strict patterns and IP grammar; missing values allow reorder but reject duplicates and omissions');
  for (const id of [472,473,474,475]) {
    const problem = JSON.parse(await fs.readFile(path.join(root, `catalog_data/problems/leetcode-${id}.json`), 'utf8'));
    for (const wrong of problem.known_wrong_solutions) {
      assert.equal((await judge(page, problem, wrong)).status, 'wrong_answer', `leetcode-${id} wrong fixture`);
    }
  }
  const concatenated = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-472.json'), 'utf8'));
  const concatenatedCase = { ...concatenated, tests: [concatenated.tests[0]] };
  const concatenatedExpected = concatenatedCase.tests[0].expected;
  assert.equal((await judge(page, concatenatedCase,
    `def concatenated_words(words):\n    return ${JSON.stringify([...concatenatedExpected].reverse())}`)).status, 'accepted');
  for (const output of [concatenatedExpected.slice(1), [...concatenatedExpected, concatenatedExpected[0]], [...concatenatedExpected, 'cat']]) {
    assert.equal((await judge(page, concatenatedCase,
      `def concatenated_words(words):\n    return ${JSON.stringify(output)}`)).status, 'wrong_answer');
  }
  report.checks.push('batch 42 wrong algorithms rejected: self-only or two-piece-only words, greedy side placement, repeated item use, duplicate erasure and wrong heater distances; concatenated results permit reorder only');
  const upside = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-156.json'), 'utf8'));
  const equalUpside = { ...upside, tests: [{ id: 'upside-original-order', arguments: [[1,1,1]],
    expected: [1,1,1], expected_node_order: [1,2,0] }] };
  const unchangedUpside = await judge(page, equalUpside, 'def upside_down_tree(root):\n    return root');
  assert.equal(unchangedUpside.status, 'wrong_answer');
  assert.deepEqual(unchangedUpside.cases[0].actual, unchangedUpside.cases[0].expected);
  assert(unchangedUpside.cases[0].error.includes('required order'));
  assert.equal((await judge(page, equalUpside, upside.reference_solution)).status, 'accepted');
  report.checks.push('batch 34 wrong algorithms rejected; upside-down tree checks original nodes even when output values coincide');
  const recovery = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-99.json'), 'utf8'));
  for (const wrong of recovery.known_wrong_solutions) {
    assert.equal((await judge(page, recovery, wrong)).status, 'wrong_answer');
  }
  const recoveryPair = { ...recovery, tests: [{ id: 'recover-pair', arguments: [[1,2]], expected: [2,1] }] };
  for (const body of ['root.val = 2; root.left = TreeNode(1)', 'root.val = 2.0; root.left.val = 1',
    'root.val = 2; root.left.val = True',
    'Ghost=type("Ghost",(TreeNode,),{"__bool__":lambda self:False}); root.val=2; root.left.val=1; root.right=Ghost(None)']) {
    const result = await judge(page, recoveryPair, `def recover_bst(root):\n    ${body}`);
    assert.equal(result.status, 'wrong_answer');
    assert(result.cases[0].error.includes('preserve every original node'));
  }
  const recoveryChildren = { ...recovery, tests: [{ id: 'recover-children', arguments: [[2,3,1]], expected: [2,1,3] }] };
  const switchedNodes = await judge(page, recoveryChildren, 'def recover_bst(root):\n    root.left,root.right = root.right,root.left');
  assert.equal(switchedNodes.status, 'wrong_answer');
  assert.deepEqual(switchedNodes.cases[0].actual, switchedNodes.cases[0].expected);
  const leftoverThread = await judge(page, recoveryPair, 'def recover_bst(root):\n    root.left.right = root');
  assert.equal(leftoverThread.status, 'runtime_error');
  assert(leftoverThread.cases[0].error.includes('cycle'));
  assert.equal((await judge(page, recoveryPair,
    'def recover_bst(root):\n    child=root.left; child.right=root; child.right=None; root.val=2; child.val=1')).status, 'accepted');
  assert.equal((await judge(page, recoveryPair, `class TreeNode:
    def __init__(self,val=0,left=None,right=None):
        self.val,self.left,self.right=val,left,right
    def __bool__(self):
        return False
def recover_bst(root):
    root.val,root.left.val=root.left.val,root.val
`)).status, 'accepted');
  assert.equal((await judge(page, recoveryChildren, recovery.reference_solution)).status, 'accepted');
  report.checks.push('BST recovery rejects copied/swapped/falsey-added nodes and noninteger values; real falsey nodes and restored Morris threads pass, leftover cycles fail, and the next run recovers');
  const tree = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-226.json'), 'utf8'));
  const compact = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-26.json'), 'utf8'));
  for (const source of ['def remove_duplicates(nums):\n    return len(set(nums))', 'def remove_duplicates(nums):\n    return True']) {
    const result = await judge(page, compact, source);
    assert.equal(result.status, 'wrong_answer');
    assert.deepEqual(result.cases[0].arguments, compact.tests[0].arguments);
    assert('return' in result.cases[0].actual && 'prefix' in result.cases[0].actual);
  }
  const removing = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-27.json'), 'utf8'));
  const reordered = await judge(page, removing, 'def remove_element(nums, val):\n    nums[:] = [v for v in nums if v != val][::-1]\n    return len(nums)');
  assert.equal(reordered.status, 'accepted');
  const rotation = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-48.json'), 'utf8'));
  const returnedCopy = await judge(page, rotation, 'def rotate_image(matrix):\n    return [list(row) for row in zip(*matrix[::-1])]');
  assert.equal(returnedCopy.status, 'wrong_answer');
  assert.deepEqual(returnedCopy.cases[0].actual, rotation.tests[0].arguments[0]);
  report.checks.push('in-place grading rejects count-only and returned-copy solutions; strict prefix counts, reordered survivors, and original input evidence verified');
  const cyclic = await judge(page, tree, 'def invert_tree(root):\n    if root:\n        root.left = root\n    return root');
  assert.equal(cyclic.status, 'runtime_error');
  assert(cyclic.cases.some(c => c.error?.includes('cycle')));
  const linked = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-25.json'), 'utf8'));
  const rewritesValues = await judge(page, linked, `def reverse_k_group(head, k):
    nodes = []
    current = head
    while current:
        nodes.append(current)
        current = current.next
    for start in range(0, len(nodes)-k+1, k):
        values = [node.val for node in nodes[start:start+k]][::-1]
        for node, value in zip(nodes[start:start+k], values):
            node.val = value
    return head
`);
  assert.equal(rewritesValues.status, 'wrong_answer');
  assert(rewritesValues.cases.some(c => c.error?.includes('original node')));
  report.checks.push('tree output cycles rejected; linked-list value rewriting rejected despite matching output values');
  const flattening = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-114.json'), 'utf8'));
  const reordering = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-143.json'), 'utf8'));
  const equalList = { ...reordering, tests: [{ id: 'equal-valued-order', arguments: [[1, 1, 1, 1]],
    expected: [1, 1, 1, 1], expected_node_order: [0, 3, 1, 2] }] };
  const noReorder = await judge(page, equalList, 'def reorder_list(head):\n    pass');
  assert.equal(noReorder.status, 'wrong_answer');
  assert.deepEqual(noReorder.cases[0].actual, noReorder.cases[0].expected);
  assert(noReorder.cases[0].error.includes('required order'));
  assert.equal((await judge(page, equalList, reordering.reference_solution)).status, 'accepted');
  const equalTree = { ...flattening, tests: [{ id: 'equal-tree-order', arguments: [[1, 1, 1]],
    expected: [1, null, 1, null, 1], expected_node_order: [0, 1, 2] }] };
  const wrongTreeOrder = await judge(page, equalTree, `def flatten_tree(root):
    left, right = root.left, root.right
    root.left = None
    root.right = right
    right.right = left
`);
  assert.equal(wrongTreeOrder.status, 'wrong_answer');
  assert.deepEqual(wrongTreeOrder.cases[0].actual, wrongTreeOrder.cases[0].expected);
  assert(wrongTreeOrder.cases[0].error.includes('required order'));
  const copiedTree = await judge(page, equalTree, `def flatten_tree(root):
    root.left = None
    root.right = TreeNode(1)
    root.right.right = TreeNode(1)
`);
  assert.equal(copiedTree.status, 'wrong_answer');
  assert(copiedTree.cases[0].error.includes('original nodes'));
  assert.equal((await judge(page, equalTree, flattening.reference_solution)).status, 'accepted');
  report.checks.push('in-place tree/list identity checked: copied nodes and wrong equal-value node order rejected, correct rewiring accepted');
  const lca = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-236.json'), 'utf8'));
  const descendantLca = { ...lca, tests: [lca.tests[1]] };
  assert.equal((await judge(page, descendantLca,
    'def lowest_common_ancestor(root, p, q):\n    return p')).status, 'accepted');
  const copiedAncestor = await judge(page, descendantLca,
    'def lowest_common_ancestor(root, p, q):\n    return TreeNode(p.val)');
  assert.equal(copiedAncestor.status, 'wrong_answer');
  assert(copiedAncestor.cases[0].error.includes('existing node'));
  const mutatedAncestor = await judge(page, descendantLca,
    'def lowest_common_ancestor(root, p, q):\n    p.left = None\n    return p');
  assert.equal(mutatedAncestor.status, 'wrong_answer');
  assert(mutatedAncestor.cases[0].error.includes('existing node'));
  report.checks.push('selected TreeNode arguments are real input references; copied return nodes and input-tree mutations are rejected');
  const selectedListNode = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-237.json'), 'utf8'));
  const selectedCase = { ...selectedListNode, tests: [selectedListNode.tests[0]] };
  assert.equal((await judge(page, selectedCase, selectedListNode.reference_solution)).status, 'accepted');
  const skipsSelectedValue = await judge(page, selectedCase,
    'def delete_node(node):\n    node.next = node.next.next');
  assert.equal(skipsSelectedValue.status, 'wrong_answer');
  const copiesRemainingNode = await judge(page, selectedCase, `def delete_node(node):
    successor = node.next
    node.val = successor.val
    node.next = ListNode(successor.next.val) if successor.next else None
`);
  assert.equal(copiesRemainingNode.status, 'wrong_answer');
  assert(copiesRemainingNode.cases[0].error.includes('selected node'));
  report.checks.push('selected ListNode deletion accepts the in-place splice and rejects wrong-value or replacement-node mutations');
  const arrayBst = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-108.json'), 'utf8'));
  const listBst = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-109.json'), 'utf8'));
  const treeCase = (problem, values, expected) => ({ ...problem, tests: [{
    id: 'flexible-tree-contract', arguments: [values], expected, comparator: 'balanced_bst', visible: true,
  }] });
  const alternate = await judge(page, treeCase(arrayBst, [1, 3], [3, 1]),
    'def sorted_array_bst(nums):\n    return TreeNode(1, None, TreeNode(3))');
  assert.equal(alternate.status, 'accepted');
  assert.notDeepEqual(alternate.cases[0].actual, alternate.cases[0].expected);
  const wrongOrder = await judge(page, treeCase(arrayBst, [1, 3], [3, 1]),
    'def sorted_array_bst(nums):\n    return TreeNode(1, TreeNode(3))');
  assert.equal(wrongOrder.status, 'wrong_answer');
  assert.deepEqual(wrongOrder.cases[0].actual, [1, 3]);
  assert(wrongOrder.cases[0].error.includes('only one valid output'));
  const deepImbalance = await judge(page, treeCase(arrayBst, [1, 2, 3, 4, 5, 6, 7], [4, 2, 6, 1, 3, 5, 7]),
    'def sorted_array_bst(nums):\n    return TreeNode(4, TreeNode(3, TreeNode(2, TreeNode(1))), TreeNode(5, None, TreeNode(6, None, TreeNode(7))))');
  assert.equal(deepImbalance.status, 'wrong_answer');
  const duplicateJob = treeCase(listBst, [1, 1, 1], [1, 1, 1]);
  assert.equal((await judge(page, duplicateJob,
    'def sorted_list_bst(head):\n    return TreeNode(1)')).status, 'wrong_answer');
  assert.equal((await judge(page, duplicateJob, listBst.reference_solution)).status, 'accepted');
  const emptyJob = treeCase(listBst, [], []);
  assert.equal((await judge(page, emptyJob, 'def sorted_list_bst(head):\n    return None')).status, 'accepted');
  for (const value of ['None', 'True', '1.0']) {
    const invalidValue = await judge(page, emptyJob, `def sorted_list_bst(head):\n    return TreeNode(${value})`);
    assert.equal(invalidValue.status, 'runtime_error');
    assert(invalidValue.message.includes('integer values'));
  }
  report.checks.push('balanced BST properties accept alternative shapes; reject wrong inorder, lost duplicates, internal imbalance, and noninteger nodes; empty ListNode input returns an empty tree');
  const wiggle = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-280.json'), 'utf8'));
  const wiggleCase = { ...wiggle, tests: [{ id: 'flexible-wiggle', arguments: [[1, 2, 3, 4, 5, 6]],
    expected: [1, 3, 2, 5, 4, 6], comparator: 'wiggle', visible: true }] };
  assert.equal((await judge(page, wiggleCase,
    'def wiggle_sort(nums):\n    nums[:] = [1, 4, 2, 5, 3, 6]')).status, 'accepted');
  assert.equal((await judge(page, wiggleCase,
    'def wiggle_sort(nums):\n    nums.sort()')).status, 'wrong_answer');
  assert.equal((await judge(page, wiggleCase,
    'def wiggle_sort(nums):\n    nums[:] = [1, 4, 2, 5, 3, 3]')).status, 'wrong_answer');
  const strictWiggle = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-324.json'), 'utf8'));
  const strictCase = { ...strictWiggle, tests: [{ id: 'strict-wiggle', arguments: [[1, 1, 2, 2, 3, 3]],
    expected: [2, 3, 1, 3, 1, 2], comparator: 'strict_wiggle', visible: true }] };
  assert.equal((await judge(page, strictCase,
    'def wiggle_sort_strict(nums):\n    nums[:] = [1, 2, 1, 3, 2, 3]')).status, 'accepted');
  for (const output of ['[1, 2, 2, 3, 1, 3]', '[1, 3, 1, 3, 1, 3]',
    '[True, 2, 1, 3, 2, 3]', '[1.0, 2, 1, 3, 2, 3]', '[[1], 2, 1, 3, 2, 3]']) {
    assert.equal((await judge(page, strictCase,
      `def wiggle_sort_strict(nums):\n    nums[:] = ${output}`)).status, 'wrong_answer');
  }
  assert.equal((await judge(page, strictCase,
    'def wiggle_sort_strict(nums):\n    return [1, 2, 1, 3, 2, 3]')).status, 'wrong_answer');
  report.checks.push('strict wiggle accepts alternative integer permutations and rejects equality, changed multisets, noninteger values, and returned copies');
  const leaves = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-366.json'), 'utf8'));
  const leafCase = { ...leaves, tests: [{ id: 'leaf-rounds', arguments: [[1,2,3,4,5]],
    expected: [[4,5,3],[2],[1]], comparator: 'unordered_rows', visible: true }] };
  assert.equal((await judge(page, leafCase,
    'def leaf_removal_rounds(root):\n    return [[3,5,4],[2],[1]]')).status, 'accepted');
  for (const output of ['[[1],[2],[3,4,5]]', '[[3,4],[2],[1]]', '[[3,4,5,5],[2],[1]]',
    '[[3,4,5],[1]]', '[[3,4,5],[2],[True]]', '[[3,4,5],[2],[1.0]]', '[[[3],4,5],[2],[1]]']) {
    assert.equal((await judge(page, leafCase,
      `def leaf_removal_rounds(root):\n    return ${output}`)).status, 'wrong_answer');
  }
  report.checks.push('ordered integer groups accept within-round permutations and reject reversed rounds, lost/extra occurrences, missing groups, and malformed values');
  const successor = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-285.json'), 'utf8'));
  const noSuccessor = { ...successor, tests: [{ id: 'no-successor', arguments: [[2, 1, 3], 3], expected: null }] };
  assert.equal((await judge(page, noSuccessor, successor.reference_solution)).status, 'accepted');
  const copiedSuccessor = { ...successor, tests: [{ id: 'copied-successor', arguments: [[2, 1, 3], 1], expected: 2 }] };
  assert.equal((await judge(page, copiedSuccessor,
    'def inorder_successor(root, p):\n    return TreeNode(2)')).status, 'wrong_answer');
  const duplicate = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-287.json'), 'utf8'));
  const mutatingDuplicate = await judge(page, { ...duplicate, tests: [duplicate.tests[0]] },
    'def find_duplicate(nums):\n    nums.sort()\n    return 2');
  assert.equal(mutatingDuplicate.status, 'wrong_answer');
  assert(mutatingDuplicate.cases[0].error.includes('Do not modify'));
  report.checks.push('worker accepts alternative wiggle permutations and None node results, while rejecting invalid multisets, copied nodes, and read-only input mutation');
  const problem = JSON.parse(await fs.readFile(path.join(root, 'catalog_data/problems/leetcode-11.json'), 'utf8'));
  const mutates = await judge(page, problem, 'def max_water_area(height):\n    height.clear()\n    return -1');
  assert.deepEqual(mutates.cases[0].arguments, problem.tests[0].arguments);
  report.checks.push('failed test evidence preserves original input even when the submission mutates it');
  for (const [expected, source] of [
    ['wrong_answer', 'def max_water_area(height):\n    return -1'],
    ['syntax_error', 'def max_water_area(:'],
    ['runtime_error', 'def max_water_area(height):\n    raise ValueError("test")'],
    ['timeout', 'def max_water_area(height):\n    while True: pass'],
    ['accepted', problem.reference_solution],
  ]) {
    const result = await judge(page, problem, source);
    assert.equal(result.status, expected);
    if (expected === 'timeout') assert(result.runtimeMs < 4000);
    report.worker.push({ id: 'judge-recovery', status: result.status, runtimeMs: result.runtimeMs });
  }
  await request('/api/problems/leetcode-11/draft', { source_code: problem.reference_solution }, 'PUT');
  await request('/api/attempts', { problem_id: problem.id, problem_version: problem.version,
    source_code: problem.reference_solution, result: 'accepted', runtime_ms: 1,
    tests_passed: 12, tests_total: 12, elapsed_study_seconds: 60, hint_level: 0 });
  await stop();
  await start();
  const restored = await (await fetch(`${base}/api/problems/leetcode-11`)).json();
  assert.equal(restored.savedDraft, problem.reference_solution);
  assert.equal(restored.solved, true);
  report.checks.push('draft and accepted progress survive a real backend restart');
  for (const route of ['/api/problems?page_size=30', '/api/problems?search=tree&topic=recursion', '/api/problems/leetcode-79', '/api/problems/leetcode-237', '/api/dashboard']) {
    const times = [];
    await (await fetch(base + route)).arrayBuffer();
    for (let i = 0; i < 100; i++) {
      const started = performance.now();
      const response = await fetch(base + route);
      assert(response.ok);
      await response.arrayBuffer();
      times.push(performance.now() - started);
    }
    times.sort((a, b) => a - b);
    report.endpoints[route] = { requests: 100, p50Ms: times[49], p95Ms: times[94], maxMs: times[99] };
    const detailOrDashboard = route === '/api/dashboard' || (route.startsWith('/api/problems/') && !route.includes('?'));
    assert(times[94] <= (detailOrDashboard ? 500 : 300));
  }
  await stop();
  report.serverPeakRssMiB = Math.max(...serverMemoryRuns.map(run => run.peakRssBytes)) / 2**20;
  report.serverMemoryRuns = serverMemoryRuns;
  report.memoryMethod = 'OS-reported backend process high-water RSS across the initial run and restart; excludes browser and benchmark driver';
  assert.deepEqual(errors, []);
  assert.deepEqual(externalRequests, [], 'Studying must not request external editor/runtime assets');
  report.checks.push('Monaco editor and Pyodide work with all external HTTP requests blocked');
  report.checks.push('no browser page errors');
  assert.equal(await fs.readFile(manifestPath, 'utf8'), manifestText, 'Catalog changed during verification; rerun on a stable snapshot');
  assert.equal(await fs.readFile(ledgerPath, 'utf8'), ledgerText, 'Ledger changed during verification; rerun on a stable snapshot');
  await fs.mkdir(path.join(root, 'catalog_import/benchmarks'), { recursive: true });
  await fs.writeFile(path.join(root, 'catalog_import/benchmarks/current.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
} finally {
  if (browser) await browser.close();
  await stop();
  // Only the exact isolated test directory created above is removed.
  await fs.rm(temp, { recursive: true, force: true });
}
