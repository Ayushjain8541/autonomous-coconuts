import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseAnalysis } from '../client/contract.ts';
import { schematicSample, sliderSample, advancePlayback, dashboardRows, maneuverReview, eventRoute, reportAgeHours } from '../client/encounter-model.ts';
const analysis = parseAnalysis(JSON.parse(readFileSync(new URL('../../contracts/fixtures/analysis-demo.json',import.meta.url),'utf8')));

test('schematic TCA center separation matches actual miss distance under the one shared scale',()=>{
 for(const miss of [0,.01,800,8000,1e7]){
  const sample=schematicSample(miss,.5)!;
  const distance=Math.hypot(...sample.primary.map((v,i)=>sample.debris[i]-v))*sample.metresPerUnit;
  assert.ok(Math.abs(distance-miss)<=Math.max(1e-9,miss*1e-12));
  assert.equal(sample.separationM,miss);
 }
 assert.equal(schematicSample(null,.5),null);
 assert.equal(schematicSample(-1,.5),null);
});
test('both models share deterministic bounded normalized time, and TCA is minimum separation',()=>{
 const approach=schematicSample(800,0)!,tca=schematicSample(800,.5)!,departure=schematicSample(800,1)!;
 assert.notDeepEqual(approach.primary,departure.primary);assert.notDeepEqual(approach.debris,departure.debris);
 assert.equal(approach.separationM,departure.separationM);assert.ok(approach.separationM>tca.separationM);
 assert.deepEqual(schematicSample(800,-4),approach);assert.deepEqual(schematicSample(800,9),departure);
});
test('rubber-band resistance affects only visual thumb offset, never logical simulation time',()=>{
 assert.equal(sliderSample(-.7).time,0);assert.equal(sliderSample(1.9).time,1);
 assert.ok(sliderSample(-.7).visualOffset<0);assert.ok(sliderSample(1.9).visualOffset>0);
 assert.ok(Math.abs(sliderSample(100).visualOffset)<=22);
 assert.equal(sliderSample(1.9,true).visualOffset,0);
 assert.equal(sliderSample(.36).time,.36);assert.equal(sliderSample(.36).visualOffset,0);
});
test('playback reaches exact TCA, clamps endpoints and rejects negative elapsed time',()=>{
 assert.equal(advancePlayback(.499,100,1),.5);assert.ok(advancePlayback(.5,100,1)>.5);
 assert.equal(advancePlayback(.999,100,2),1);assert.equal(advancePlayback(.2,-10,1),.2);
});
test('dashboard search, risk and stable sorting preserve server classification and source order',()=>{
 const before=structuredClone(analysis.encounters);
 assert.equal(dashboardRows(analysis.encounters,'safe','all','priority')[0].event_id,'demo-safe-20h');
 assert.equal(dashboardRows(analysis.encounters,'','critical','horizon').length,1);
 assert.equal(dashboardRows(analysis.encounters,'','all','priority')[0].severity,'critical');
 assert.deepEqual(analysis.encounters,before);
});
test('planning is a distinct operator-review recommendation from authoritative severity',()=>{
 assert.match(maneuverReview('critical'),/operator review/);assert.match(maneuverReview('elevated'),/Monitor/);
 assert.match(maneuverReview('safe'),/No immediate/);assert.equal(maneuverReview('unknown'),'Undetermined');
});
test('history route decodes real event identities and rejects malformed links',()=>{
 assert.equal(eventRoute('/encounters/demo-critical-36h'),'demo-critical-36h');assert.equal(eventRoute('/encounters/a%20b'),'a b');
 assert.equal(eventRoute('/encounters/%invalid'),null);assert.equal(eventRoute('/'),null);
});
test('report age requires explicit valid source and reference clocks and never accepts future timestamps',()=>{
 assert.equal(reportAgeHours('2026-10-31T03:00:00Z','2026-10-31T04:00:00Z'),1);
 assert.equal(reportAgeHours(null,'2026-10-31T04:00:00Z'),null);
 assert.equal(reportAgeHours('invalid','2026-10-31T04:00:00Z'),null);
 assert.equal(reportAgeHours('2026-11-01T03:00:00Z','2026-10-31T04:00:00Z'),null);
 assert.equal(reportAgeHours('2026-10-31T03:00:00Z',null),null);
});

test('report-age clocks must declare a timezone rather than inherit the browser locale',()=>{
 assert.equal(reportAgeHours('2026-10-31T03:00:00','2026-10-31T04:00:00Z'),null);
 assert.equal(reportAgeHours('2026-10-31T03:00:00Z','2026-10-31T04:00:00'),null);
 assert.equal(reportAgeHours('2026-10-31T11:00:00+08:00','2026-10-31T04:00:00Z'),1);
});
