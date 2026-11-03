// Full review UI against isolated accounts/data; never production progress.
import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { chromium } = await import(pathToFileURL(path.join(root,'frontend/node_modules/playwright/index.mjs')).href);
const temporary = await fs.mkdtemp(path.join(os.tmpdir(),'study-review-v2-'));
const socket = net.createServer();
await new Promise((resolve,reject) => { socket.once('error',reject);socket.listen(0,'127.0.0.1',resolve); });
const port = socket.address().port;
await new Promise(resolve => socket.close(resolve));
const base = `http://127.0.0.1:${port}`;
const env = { ...process.env, CODE_PRACTICE_DATA_DIR:temporary, CODE_PRACTICE_DB:path.join(temporary,'code_practice.db'),
  CODE_PRACTICE_SEED_DB:'',CODE_PRACTICE_AUTH_USERNAME:'',CODE_PRACTICE_SESSION_SECRET:'',CODE_PRACTICE_REQUIRE_LOGIN:'1',
  CODE_PRACTICE_REVIEW_V2:'1',CODE_PRACTICE_PUBLIC_ORIGIN:base };
const python=path.join(root,'.venv/bin/python');
const source='def pair_sum_indices(nums, target):\n    seen = {}\n    for i, value in enumerate(nums):\n        if target - value in seen:\n            return [seen[target - value], i]\n        seen[value] = i\n    return []\n';
const setup=spawnSync(python,['-c',`from datetime import datetime,timedelta,timezone
from code_practice import accounts,database,review_v2
accounts.initialize('admin')
accounts.set_password('owner','owner-test-password')
source=${JSON.stringify(source)}
database.save_draft('pair-sum-indices',source)
with database.db_session() as c:
 c.execute("INSERT INTO attempts(problem_id,problem_version,source_code,result,runtime_ms,tests_passed,tests_total,created_at) VALUES('pair-sum-indices',1,?,'accepted',1,12,12,?)",(source,(datetime.now(timezone.utc)-timedelta(days=5)).isoformat()))
 review_v2.sync_problem(c,'pair-sum-indices')
`],{cwd:root,env,encoding:'utf8'});
assert.equal(setup.status,0,setup.stderr);
let server,browser,page;
async function start() {
  server=spawn(python,['-m','uvicorn','code_practice.app:app','--host','127.0.0.1','--port',String(port)],{cwd:root,env,stdio:['ignore','ignore','pipe']});
  let errors='';server.stderr.on('data',x=>{errors+=x;});
  for(let i=0;i<100;i++) {
    if(server.exitCode!==null)throw new Error(errors);
    try { if((await fetch(base+'/api/health')).ok)return; } catch {}
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  throw new Error(errors||'Server failed to start');
}
async function stop() {
  if(server&&server.exitCode===null){const ended=new Promise(resolve=>server.once('exit',resolve));server.kill('SIGTERM');await ended;}
}
try {
  await start();browser=await chromium.launch({channel:'chrome',headless:true});
  page=await browser.newPage({viewport:{width:1400,height:1000}});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(base);
  await page.getByLabel('Username',{exact:true}).fill('admin');
  await page.getByLabel('Password',{exact:true}).fill('owner-test-password');
  await page.getByRole('button',{name:'Sign in',exact:true}).click();
  await page.getByRole('button',{name:/Pair Sum Indices/}).click();
  await page.getByText('Fresh review workspace',{exact:true}).waitFor();
  await page.locator('.monaco-editor .view-lines').waitFor();
  const first=await page.evaluate(()=>window.monaco.editor.getModels()[0].getValue());
  assert.notEqual(first,source);assert.ok(first.includes('Write your solution here'));
  async function setCode(value) {
    const saved=page.waitForResponse(r=>r.url().includes('/api/reviews/sessions/')&&r.url().endsWith('/draft')&&r.request().method()==='PUT'&&r.ok());
    await page.evaluate(code=>window.monaco.editor.getModels()[0].setValue(code),value);
    await saved;
  }
  async function submit() {
    const saved=page.waitForResponse(r=>r.url().endsWith('/api/attempts')&&r.ok(),{timeout:30000});
    await page.getByRole('button',{name:'Submit',exact:true}).click();
    return (await saved).json();
  }
  async function dashboard() {return page.evaluate(async()=>(await fetch('/api/dashboard')).json());}
  await setCode(source);
  let result=await submit();assert.equal(result.reviewEvent.automaticGrade,'good');
  await page.getByRole('button',{name:'Very easy',exact:true}).click();
  await page.getByText(/Your rating: Very easy/).waitFor();
  const feedbackDate=await page.getByLabel('Review feedback').innerText();
  result=await submit();assert.equal(result.reviewEvent.manualGrade,'easy');
  assert.equal(await page.getByLabel('Review feedback').innerText(),feedbackDate);
  await setCode('def pair_sum_indices(nums, target):\n    return []\n');
  result=await submit();assert.equal(result.reviewEvent.latestResult,'wrong_answer');
  assert.equal(result.reviewEvent.manualGrade,null);
  let overview=await dashboard();assert.equal(overview.reviewComplete,false);assert.equal(overview.reviewRemainingCount,1);
  await page.getByRole('button',{name:'Today',exact:true}).click();
  await page.getByRole('button',{name:/Pair Sum Indices/}).click();
  await page.locator('.monaco-editor .view-lines').waitFor();
  assert.ok((await page.evaluate(()=>window.monaco.editor.getModels()[0].getValue())).includes('return []'));
  await setCode(source);result=await submit();assert.equal(result.reviewEvent.automaticGrade,'hard');
  await page.getByRole('button',{name:'View my previous solution (records help)',exact:true}).click();
  await page.locator('.previous-solution').waitFor();
  assert.equal((await page.locator('.previous-solution').innerText()).trimEnd(),source.trimEnd());
  await page.getByText(/Automatic rating: Need more review/).waitFor();
  await page.getByRole('button',{name:'Finished independently',exact:true}).click();
  await page.getByText(/Your rating: Finished independently/).waitFor();
  await page.getByRole('button',{name:'Use automatic rating',exact:true}).click();
  await page.getByText(/Automatic rating: Need more review/).waitFor();
  await page.getByRole('button',{name:'Today',exact:true}).click();
  await page.getByText('Review scores, due dates and cooldowns',{exact:true}).click();
  await page.getByLabel('Search review scores').fill('Pair Sum Indices');
  const scoreRow=page.locator('.review-score-table tbody tr').filter({hasText:'Pair Sum Indices'});
  await scoreRow.waitFor();
  await scoreRow.locator('summary').click();
  await page.getByText(/Urgency:/).waitFor();
  await page.screenshot({path:path.join(temporary,'scores-desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:path.join(temporary,'scores-mobile.png'),fullPage:true});
  await stop();await start();await page.reload();
  overview=await dashboard();assert.equal(overview.reviewComplete,true);
  const integrity=spawnSync(python,['-c',`from code_practice import database,review_v2
with database.db_session() as c:
 assert c.execute("SELECT count(*) FROM review_events WHERE problem_id='pair-sum-indices' AND event_date=?",(str(review_v2.local_day()),)).fetchone()[0]==1
 assert database.get_draft('pair-sum-indices')==${JSON.stringify(source)}
 assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
`],{cwd:root,env,encoding:'utf8'});
  assert.equal(integrity.status,0,integrity.stderr);assert.deepEqual(errors,[]);
  console.log(JSON.stringify({passed:true,checks:['fresh review draft','original solution preserved','same-day spacing idempotence','optional grading and clearing','failure remains pending','draft resumes','help changes automatic grade','score view','mobile layout','restart persistence'],screenshots:temporary}));
} catch (error) {
  if (page) {
    await page.screenshot({path:path.join(temporary,'failure.png'),fullPage:true}).catch(()=>{});
    console.error(JSON.stringify({diagnostics:temporary,scorePanel:await page.locator('.review-scores').innerText().catch(()=>null)}));
  }
  throw error;
} finally {await browser?.close();await stop();}
