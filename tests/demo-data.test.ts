import test from 'node:test';
import assert from 'node:assert/strict';
import { encounters, encountersForDays } from '../src/demo-data.ts';

test('time frame includes complete selected days and excludes later encounters',()=>{
  for(let days=1;days<=7;days++){
    const rows=encountersForDays(days);
    assert.equal(rows.length,days*5);
    assert.ok(rows.every(row=>row.day>=0&&row.day<days));
    assert.deepEqual(rows,encounters.slice(0,days*5));
  }
});
test('demo rows remain stable through repeated filtering and carry textual status',()=>{
  const before=structuredClone(encounters);
  encountersForDays(1);encountersForDays(7);encountersForDays(2);
  assert.deepEqual(encounters,before);
  assert.equal(new Set(encounters.map(row=>row.id)).size,35);
  assert.deepEqual(new Set(encounters.map(row=>row.severity)),new Set(['Critical','Safe','Elevated']));
});
test('invalid time frames cannot silently expand the result set',()=>{
  for(const days of [0,8,-1,1.5,NaN,Infinity]) assert.deepEqual(encountersForDays(days),[]);
});
