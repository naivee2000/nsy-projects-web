import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';

const digest = value => createHash('sha256').update(value).digest('hex');

async function judge(page, entry, language, source, examples, edit) {
  await edit(page, source);
  const response = page.waitForResponse(r => {
    if (!r.url().endsWith('/api/database/problems/' + entry.id + '/judge') || r.request().method() !== 'POST') return false;
    const sent = r.request().postDataJSON();
    return sent.language === language && sent.source === source && sent.examples === examples;
  }, { timeout: 90000 });
  await page.getByRole('button', { name: examples ? 'Run examples' : 'Submit', exact: true }).click();
  const result = await response;
  assert.equal(result.status(), 200, await result.text());
  return result.json();
}

async function verify(page, base, entry, edit) {
  await page.goto(base + '/database/library?search=' + entry.id);
  await page.getByRole('button', { name: new RegExp('^' + entry.id + '\\. ') }).click();
  const combinations = [];
  for (const [language, label] of [['mysql','MySQL'], ['pandas','Pandas']]) {
    const toggle = page.getByRole('button', { name: new RegExp('^' + label + '(?: · Passed)?$') });
    await toggle.click();
    await page.waitForFunction(label => [...document.querySelectorAll('[aria-pressed=true]')]
      .some(button => button.textContent.includes(label)), label);
    const reference = language === 'mysql' ? entry.sql : entry.pandas;
    let durationMs = 0;
    for (const examples of [true, false]) {
      const start = Date.now();
      const result = await judge(page, entry, language, reference, examples, edit);
      if (!examples) durationMs = Date.now() - start;
      assert.equal(result.accepted, true, JSON.stringify({ id:entry.id, language, examples,
        failed:result.cases.filter(c => !c.passed).slice(0,1) }));
      assert.equal(result.cases.length, examples ? 2 : 16);
    }
    const negatives = language === 'mysql' ? entry.wrong : entry.wrongPandas;
    assert.equal(new Set(negatives).size, 2);
    const rejected = [];
    for (const wrong of negatives) {
      const result = await judge(page, entry, language, wrong, false, edit);
      const mismatches = result.cases.filter(c => !c.passed && c.actual && !c.error);
      assert.ok(!result.accepted && mismatches.length, JSON.stringify({ id: entry.id, language,
        wrong: wrong.slice(0,180), outcome:result.accepted ? 'accepted' : result.cases.find(c=>!c.passed) }));
      rejected.push(mismatches.map(c => c.case));
    }
    combinations.push({ id:entry.id, language, status:'passed', cases:16, examples:2, wrongAnswersRejected:2,
      wrongAnswerFailedCases:rejected, durationMs });
  }
  return combinations;
}

function verified(row, id, fingerprint) {
  if (row?.fingerprint !== fingerprint || row.combinations?.length !== 2) return false;
  return ['mysql','pandas'].every(language => row.combinations.some(c =>
    c.id === id && c.language === language && c.status === 'passed' && c.examples === 2 &&
    c.cases === 16 && c.wrongAnswersRejected === 2 && c.wrongAnswerFailedCases?.length === 2 &&
    c.wrongAnswerFailedCases.every(cases => cases.length && cases.every(n => Number.isInteger(n) && n >= 1 && n <= 16))));
}

export async function sweep({page,base,get,edit,root,temporary,references,frontend,errors}) {
  const ids = process.argv.find(s => s.startsWith('--ids='))?.slice(6).split(',').map(Number);
  if (ids) assert.equal(new Set(ids).size, ids.length, 'Duplicate verification IDs');
  if (ids) for (const id of ids) assert.ok(references.some(x => x.id === id), 'Missing playable ID ' + id);
  const reportDir = path.resolve(process.argv.find(s => s.startsWith('--report-dir='))?.slice(13) || temporary);
  await fs.mkdir(reportDir, { recursive:true });
  const inventory = JSON.parse(await fs.readFile(path.join(root,'database_catalog/inventory.json')));
  const files = ['code_practice/database_exercise.py','code_practice/database_catalog.py','code_practice/database_judge.py','code_practice/database_routes.py',
    'frontend/public/database-worker.js','scripts/database_catalog_sweep.mjs','scripts/verify_database_browser.mjs',
    'scripts/start_database_judge.sh','frontend/package-lock.json'];
  const parts = await Promise.all(files.map(f => fs.readFile(path.join(root,f))));
  const index = await fs.readFile(path.join(frontend,'index.html'),'utf8');
  const assets = [...index.matchAll(/(?:src|href)="(\/assets\/[^"]+)"/g)].map(match => match[1]);
  assert.ok(assets.some(asset => asset.endsWith('.js')) && assets.some(asset => asset.endsWith('.css')));
  const wheels = JSON.parse(await fs.readFile(path.join(frontend,'pyodide/pyodide-lock.json')));
  const container = process.env.CODE_PRACTICE_MYSQL_CONTAINER;
  const mysqlImage = execFileSync('docker',['inspect','--format','{{.Config.Image}}',container],{encoding:'utf8'}).trim();
  const mysql = execFileSync('docker',['exec',container,'mysqld','--version'],{encoding:'utf8'}).trim();
  const runtime = {mysqlImage, mysql, pyodide:wheels.info.version, pandas:wheels.packages.pandas.version};
  parts.push(Buffer.from(index),Buffer.from(JSON.stringify(runtime)),...await Promise.all(
    ['database-worker.js','pyodide/pyodide-lock.json',...assets].map(asset => fs.readFile(path.join(frontend,asset)))));
  const version = digest(Buffer.concat(parts));
  const report = [];
  const contracts = {};
  for (const entry of references.filter(e=>!ids || ids.includes(e.id))) {
    const fingerprint = digest(version + JSON.stringify(entry));
    const file = path.join(reportDir, String(entry.id) + '.json');
    const previous = await fs.readFile(file,'utf8').then(JSON.parse).catch(()=>null);
    let row;
    if (verified(previous, entry.id, fingerprint)) {
      row = previous;
    } else {
      try {
        row = { fingerprint, combinations: await verify(page,base,entry,edit) };
        assert.deepEqual(errors, []);
      } catch (error) {
        await fs.writeFile(file + '.failure', JSON.stringify({id:entry.id,fingerprint,judge:version,detail:String(error)}) + '\n');
        throw error;
      }
      const next = file + '.' + process.pid + '.tmp';
      await fs.writeFile(next,JSON.stringify(row,null,2)+'\n');
      await fs.rename(next,file);
      await fs.rm(file+'.failure',{force:true});
    }
    assert.ok(verified(row, entry.id, fingerprint));
    contracts[entry.id] = fingerprint;
    report.push(...row.combinations);
    console.log(JSON.stringify({ id:entry.id, passed:2, referenceCases:32, rejections:4 }));
  }
  if (!ids) {
    const sorted = items => items.map(e=>e.id).sort((a,b)=>a-b);
    assert.deepEqual(sorted(references),sorted(inventory));
    const library = [];
    for (let n=1; library.length < inventory.length; n++) {
      const next = await get(page, '/api/database/problems?playable=true&page=' + n);
      assert.equal(next.total, 323);
      assert.ok(next.items.length && next.items.every(item => item.runnable));
      library.push(...next.items);
    }
    assert.deepEqual(sorted(library), sorted(inventory));
    assert.equal(new Set(report.map(r=>r.id+'-'+r.language)).size,646);
    await fs.writeFile(path.join(reportDir,'report.json'),JSON.stringify({total:323,passed:646,pending:0,
      judgeFingerprint:version,catalogFingerprint:digest(JSON.stringify(contracts)),problemFingerprints:contracts,runtime,
      referenceCases:report.reduce((s,r)=>s+r.cases,0),
      wrongAnswerSubmissionsRejected:report.reduce((s,r)=>s+r.wrongAnswersRejected,0), combinations:report},null,2)+'\n');
  }
  console.log('Verified '+report.length+' language combinations. Evidence: '+reportDir);
}
