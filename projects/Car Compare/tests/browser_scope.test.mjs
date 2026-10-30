import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectSearchScope, validateHostScope} from '../scripts/car_compare_browser_mcp.mjs';

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
