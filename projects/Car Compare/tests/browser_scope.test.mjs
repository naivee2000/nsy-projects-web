import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {inspectRequestedScope, inspectSearchScope, validateHostScope} from '../scripts/car_compare_browser_mcp.mjs';

const requested = {make:'BMW',model:'M4',trim:'Competition',years:[2023],conditions:['used','cpo'],body:'',drivetrain:''};
const controls = Object.entries(requested).filter(([,value]) => value.length).map(([field,value]) => ({field,kind:'select',name:field,values:Array.isArray(value)?value:[value]}));
controls.push({kind:'select',name:'Distance',value:'Nationwide'});
const snapshot = {url:'https://www.edmunds.com/inventory/srp.html',controls,result_count:5,text:'5 vehicles',busy:false};
test('matching scope is ready; title is unnecessary', () => assert.equal(inspectSearchScope(snapshot,'edmunds_browser',200,requested).status,'ready'));
for (const [field,value] of [['make','Ford'],['model','F-150'],['trim','Base'],['years',2024],['conditions','new']]) {
  test(`reject wrong ${field}`, () => {
    const changed = {...snapshot,controls:controls.map(c => c.field === field ? {...c,values:[value]} : c)};
    assert.equal(inspectSearchScope(changed,'edmunds_browser',200,requested).status,'filter_mismatch');
  });
}
test('missing fields never verify empty inventory', () => assert.equal(inspectSearchScope({...snapshot,controls:controls.slice(-1),result_count:0,text:'0 vehicles'},'edmunds_browser',200,requested).status,'filter_unknown'));
test('loading and rate limits are not zero', () => {
  assert.equal(inspectSearchScope({...snapshot,busy:true,result_count:0,text:'0 vehicles'},'edmunds_browser',200,requested).status,'loading');
  assert.equal(inspectSearchScope(snapshot,'edmunds_browser',429,requested).status,'rate_limited');
});
test('host Chrome requires refreshed evidence on every page', () => {
  const capture = {source:'edmunds_browser',pages:[{scope_snapshot:snapshot,result_refresh_confirmed:false}]};
  assert.notEqual(validateHostScope(capture,requested).scope.validation_status,'verified');
  capture.pages[0].result_refresh_confirmed = true;
  assert.equal(validateHostScope(capture,requested).scope.validation_status,'verified');
});
test('base is a real restriction, not all trims', () => assert.equal(inspectSearchScope(snapshot,'edmunds_browser',200,{...requested,trim:'Base'}).status,'filter_mismatch'));
test('broad request cannot claim a narrowed trim filter', () => assert.equal(inspectSearchScope(snapshot,'edmunds_browser',200,{...requested,trim:''}).status,'filter_mismatch'));

const lexus = JSON.parse(fs.readFileSync(new URL('./fixtures/lexus_nx_20261102.json',import.meta.url)));
test('actual Lexus labeled bounds parse, but redirected model remains unverified',()=>{
  const capture=lexus.browsers[0], page=capture.pages[0].scope_snapshot;
  const result=inspectSearchScope(page,capture.source,200,capture.requested_scope);
  assert.equal(result.evidence.constraints.years.status,'matched');
  assert.notEqual(result.evidence.constraints.model.status,'matched');
  assert.notEqual(result.status,'ready');
});
test('actual Edmunds local radius is not national evidence',()=>{
  const capture=lexus.browsers[1];
  assert.equal(inspectSearchScope(capture.pages[0].scope_snapshot,capture.source,200,capture.requested_scope).status,'filter_mismatch');
});
test('source family and condition labels normalize without confusing manufacturer certified with make',()=>{
  const query={...requested,make:'Lexus',model:'NX',trim:''};
  const selected=[{kind:'chip',name:'Selected filter',value:'Lexus'},
    {kind:'radio',name:'NX Models',value:'NX Models'},
    {kind:'radio',name:'Used',value:'Used'},
    {kind:'radio',name:'Manufacturer Certified',value:'Manufacturer Certified'},
    {kind:'selected',name:'Min Year: 2023',value:'Min Year\n2023'},
    {kind:'selected',name:'Max Year: 2023',value:'Max Year\n2023'}];
  assert.equal(inspectRequestedScope(selected,query).status,'matched');
});
test('later failed page preserves only earlier verified pages',()=>{
  const result=validateHostScope({source:'edmunds_browser',pages:[
    {scope_snapshot:snapshot,result_refresh_confirmed:true},
    {scope_snapshot:{...snapshot,controls:[]},result_refresh_confirmed:true}]},requested);
  assert.equal(result.status,'partial');
  assert.deepEqual(result.accepted_pages,[0]);
  assert.equal(result.failure_reason,'filter_unknown');
});
test('genuine access wall and rate limit have distinct reasons',()=>{
  assert.equal(inspectSearchScope({...snapshot,text:'Access denied'},'edmunds_browser',403,requested).status,'blocked');
  assert.equal(inspectSearchScope(snapshot,'edmunds_browser',429,requested).status,'rate_limited');
});
test('a nationwide label with uncommitted slider position remains unknown',()=>{
  const changed={...snapshot,controls:[...controls.slice(0,-1),{kind:'slider',name:'Search radius',value:'Nationwide',max:7,now:1}]};
  assert.equal(inspectSearchScope(changed,'edmunds_browser',200,requested).status,'filter_unknown');
});
test('staged year text cannot override conflicting committed chips and sliders',()=>{
  const selected=[...controls.filter(c=>c.field!=='years'),
    {kind:'selected',name:'Min Year',value:'2016'},
    {kind:'selected',name:'Max Year',value:'2026'},
    {kind:'slider',name:'Min Year',value:'2024'},
    {kind:'chip',name:'Selected filter',value:'2024-2026'}];
  assert.equal(inspectRequestedScope(selected,{...requested,years:Array.from({length:11},(_,i)=>2016+i)}).fields.years.status,'mismatch');
});
test('Edmunds model-family catalog does not itself prove every member selected',()=>{
  const query={...requested,make:'Lexus',model:'NX',trim:''};
  const selected=controls.filter(c=>!['make','model','trim'].includes(c.field));
  selected.push({kind:'select',name:'Search by Make Make & Model make',value:'Lexus'},
    {kind:'chip',name:'Selected filter',value:'Lexus NX'});
  const snap={...snapshot,controls:selected,model_catalog:['NX','NX 300']};
  assert.equal(inspectSearchScope(snap,'edmunds_browser',200,query).status,'filter_mismatch');
  selected.push({kind:'chip',name:'Selected filter',value:'Lexus NX 300'});
  assert.equal(inspectSearchScope(snap,'edmunds_browser',200,query).status,'ready');
});
test('explicit numeric trim can be proven by the selected model variant only',()=>{
  const query={...requested,make:'Lexus',model:'LC',trim:'500'};
  const selected=controls.filter(c=>!['make','model','trim'].includes(c.field));
  selected.push({field:'make',value:'Lexus'},{field:'model',value:'LC 500'});
  assert.equal(inspectRequestedScope(selected,query).status,'matched');
  selected.at(-1).value='LC';
  assert.equal(inspectRequestedScope(selected,query).fields.trim.status,'unknown');
});
