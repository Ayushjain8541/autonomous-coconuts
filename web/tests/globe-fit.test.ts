import test from 'node:test';
import assert from 'node:assert/strict';
import { globeFitHeight } from '../client/globe-fit.ts';
test('hidden encounter context never yields an infinite or NaN camera height',()=>{
 for(const size of [[0,0],[0,200],[200,0],[NaN,200],[200,Infinity]])assert.equal(globeFitHeight(...size as [number,number]),null);
 for(const size of [[1280,720],[390,260],[180,150],[768,400]]){const fit=globeFitHeight(...size as [number,number]);assert.ok(fit!==null&&Number.isFinite(fit)&&fit>0);}
});
