import test from 'node:test';
import assert from 'node:assert/strict';
import fixture from '../../contracts/fixtures/analysis-demo.json' with {type:'json'};
import {parseAnalysis} from '../client/contract.ts';
import {encounterMotion} from '../client/encounter-model.ts';
import {sphereFraming,sceneVisibility} from '../client/scene-framing.ts';

test('Critical → Elevated → Safe → Critical keeps reference satellite visible without inventing geometry',()=>{
 const analysis=parseAnalysis(fixture);
 for(const id of ['demo-critical-36h','demo-elevated-12h','demo-safe-20h','demo-critical-36h']){
  const row=analysis.encounters.find(row=>row.event_id===id)!;
  const model=encounterMotion(analysis,row,analysis),visible=sceneVisibility(model!==null);
  assert.equal(visible.primary,true);
  assert.equal(visible.debris,id==='demo-critical-36h');
  assert.equal(visible.vectors,id==='demo-critical-36h');
 }
});
test('sphere framing contains bounds on both viewport axes across scales and usable clipping/zoom',()=>{
 for(const radius of [.01,2,1000,1e8])for(const aspect of [.35,1,2.5]){
  const fit=sphereFraming(radius,aspect),half=42*Math.PI/360;
  assert.ok(fit.distance*Math.sin(half)>radius);
  assert.ok(fit.distance*Math.sin(Math.atan(Math.tan(half)*aspect))>radius);
  assert.ok(fit.near<fit.distance-radius);
  assert.ok(fit.far>fit.maxDistance+radius);
  assert.ok(fit.minDistance<fit.distance&&fit.maxDistance>fit.distance);
 }
});
test('portrait resize increases fit distance; invalid bounds remain finite',()=>{
 assert.ok(sphereFraming(4,.5).distance>sphereFraming(4,2).distance);
 assert.ok(Object.values(sphereFraming(NaN,0)).every(Number.isFinite));
});
