import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseAnalysis } from '../client/contract.ts';
import { schematicSample, sliderSample, advancePlayback, dashboardRows, maneuverReview, eventRoute, reportAgeHours, discreteHorizon, horizonStops, animatedMetric, easeOutCubic, playbackStep, pointerEncounterTime, encounterMotion, relativeMotionSample } from '../client/encounter-model.ts';
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
 assert.deepEqual(approach.primary,[0,0,0]);assert.deepEqual(departure.primary,[0,0,0]);assert.notDeepEqual(approach.debris,departure.debris);
 assert.equal(approach.separationM,departure.separationM);assert.ok(approach.separationM>tca.separationM);
 assert.deepEqual(schematicSample(800,-4),approach);assert.deepEqual(schematicSample(800,9),departure);
});
test('rubber-band resistance affects only visual thumb offset, never logical simulation time',()=>{
 assert.equal(sliderSample(-.7).time,0);assert.equal(sliderSample(1.9).time,1);
 assert.ok(sliderSample(-.7).visualOffset<0);assert.ok(sliderSample(1.9).visualOffset>0);
 assert.equal(sliderSample(2).visualOffset,32);
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
 assert.equal(maneuverReview('critical'),'Maneuver planning required');assert.equal(maneuverReview('elevated'),'Further assessment recommended');
 assert.match(maneuverReview('safe'),/No immediate/);assert.equal(maneuverReview('unknown'),'Risk assessment unavailable');
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

test('discrete horizon snaps into four valid stops without overshoot leaking to filters',()=>{
 assert.deepEqual(horizonStops,[1,3,7,Infinity]);
 for(const [raw,index]of [[-2,0],[0,0],[.33,1],[.67,2],[1,3],[5,3]])assert.equal(discreteHorizon(raw),index);
});
test('priority puts safe before unknown, then lead time, then stable event ID',()=>{
 const base=analysis.encounters[0];
 const rows=[{...base,event_id:'unknown',severity:'unknown' as const,time_to_tca_hours:1},{...base,event_id:'safe',severity:'safe' as const},{...base,event_id:'late',time_to_tca_hours:50},{...base,event_id:'z',time_to_tca_hours:20},{...base,event_id:'a',time_to_tca_hours:20}];
 assert.deepEqual(dashboardRows(rows,'','all','priority').map(r=>r.event_id),['a','z','late','safe','unknown']);
});
test('count-up keeps probability exponent stable, exact final formatting, and null distinct',()=>{
 assert.equal(animatedMetric(.0002,0,'pc'),'0.000 × 10⁻⁴');
 assert.equal(animatedMetric(.0002,1,'pc'),'2.000 × 10⁻⁴');
 assert.match(animatedMetric(.0002,.3,'pc'),/× 10⁻⁴$/);
 assert.equal(animatedMetric(null,.5,'pc'),'Unavailable');assert.equal(animatedMetric(0,1,'pc'),'0');
 assert.equal(animatedMetric(36,1,'time'),'36 h');assert.equal(animatedMetric(800,1,'distance'),'800 m');assert.equal(animatedMetric(800.123,1,'distance'),'800.123 m');assert.equal(animatedMetric(8000.123,1,'distance'),'8.000123 km');assert.equal(animatedMetric(8000,1,'distance'),'8 km');
 assert.equal(easeOutCubic(0),0);assert.equal(easeOutCubic(1),1);assert.equal(easeOutCubic(.5),.875);
});

test('automatic playback holds exactly at TCA for 1750ms once without hidden clock drift',()=>{
 let state=playbackStep(.499,100,1,0,false);assert.deepEqual(state,{time:.5,holdMs:1750,held:true});
 for(let i=0;i<17;i++){state=playbackStep(state.time,100,1,state.holdMs,state.held);assert.equal(state.time,.5);}
 assert.equal(state.holdMs,50);state=playbackStep(state.time,50,1,state.holdMs,state.held);assert.equal(state.holdMs,0);assert.equal(state.time,.5);
 state=playbackStep(state.time,100,1,state.holdMs,state.held);assert.ok(state.time>.5);
 assert.equal(playbackStep(.499,100,1,0,true).holdMs,0);
});

test('pointer TCA capture gives a stable exact minimum without quantizing other phases',()=>{
 for(const value of [.49,.495,.5,.505,.51])assert.equal(pointerEncounterTime(value),.5);
 for(const value of [0,.1,.489,.511,.84,1])assert.equal(pointerEncounterTime(value),value);
 assert.equal(pointerEncounterTime(-1),0);assert.equal(pointerEncounterTime(2),1);
 assert.equal(playbackStep(pointerEncounterTime(.497),100,1,0,true).holdMs,0);
});

test('canonical fixture motion consumes actual response RTN vectors and has exact TCA distance',()=>{
 const row=analysis.encounters.find(r=>r.event_id==='demo-critical-36h')!;
 const model=encounterMotion(analysis,row,analysis.analysis_id)!;assert.ok(model);
 assert.deepEqual(model.position,[800,0,0]);assert.deepEqual(model.velocity,[0,7500,0]);
 const tca=relativeMotionSample(model,.5);assert.equal(tca.separationM,800);assert.deepEqual(tca.debris,[4,0,0]);
 const before=relativeMotionSample(model,0),after=relativeMotionSample(model,1);assert.ok(before.debris[1]<0);assert.ok(after.debris[1]>0);assert.equal(before.separationM,after.separationM);
 const changed={...row,miss_distance_m:1600,geometry:{frame:'RTN' as const,position_m:{r:1600,t:0,n:0},velocity_mps:{r:0,t:0,n:3000}}};
 const other=encounterMotion(analysis,changed,analysis.analysis_id)!;assert.equal(relativeMotionSample(other,.5).separationM,1600);assert.ok(relativeMotionSample(other,1).debris[2]>0);assert.equal(relativeMotionSample(other,1).debris[1],0);
});
test('unknown epochs, missing geometry and non-TCA states never acquire fabricated motion',()=>{
 const row=analysis.encounters[0];
 assert.equal(encounterMotion({...analysis,source:{...analysis.source,mode:'uploaded_csv'}},row,analysis.analysis_id),null);
 assert.equal(encounterMotion({...analysis,analysis_id:'other'},row,analysis.analysis_id),null);
 assert.equal(encounterMotion({...analysis,model:{...analysis.model,status:'ready'}},row,analysis.analysis_id),null);
 for(const other of analysis.encounters.filter(r=>r.geometry===null))assert.equal(encounterMotion(analysis,other,analysis.analysis_id),null);
 assert.equal(encounterMotion(analysis,{...row,miss_distance_m:900},analysis.analysis_id),null);
 assert.equal(encounterMotion(analysis,{...row,geometry:{frame:'RTN',position_m:{r:800,t:0,n:0},velocity_mps:{r:1,t:7500,n:0}}},analysis.analysis_id),null);
 assert.equal(encounterMotion(analysis,{...row,geometry:{frame:'RTN',position_m:{r:800,t:0,n:0},velocity_mps:{r:0,t:0,n:0}}},analysis.analysis_id),null);
});
