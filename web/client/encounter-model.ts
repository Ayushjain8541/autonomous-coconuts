import type { AnalysisResult, Encounter, Severity } from './contract.ts';

export const clampTime = (value: number) => Math.min(1, Math.max(0, Number.isFinite(value) ? value : 0));
export function phaseLabel(time: number) {
  const t = clampTime(time);
  return Math.abs(t - .5) < .015 ? 'Closest approach' : t < .5 ? 'Approach' : 'Departure';
}
export function maneuverReview(severity: Severity): string {
  return ({critical:'Maneuver planning required',elevated:'Further assessment recommended',safe:'No immediate maneuver planning indicated',unknown:'Risk assessment unavailable'})[severity];
}
export function remainingTime(hours: number): string {
  const minutes = Math.round(hours * 60), h = Math.floor(minutes / 60), m = minutes % 60;
  return `${h}h${m ? ` ${m}m` : ''} remaining`;
}
/** Mode B only. Normalized conceptual paths, NOT propagation of supplied RTN states. */
export function schematicSample(missDistanceM: number | null, time: number) {
  if (missDistanceM === null || !Number.isFinite(missDistanceM) || missDistanceM < 0) return null;
  const t = clampTime(time), metresPerUnit = Math.max(missDistanceM / 4, 1);
  const relativeX = (t - .5) * 24, gap = missDistanceM / metresPerUnit;
  const primary: [number, number, number] = [0, 0, 0];
  const debris: [number, number, number] = [relativeX * .8, gap, relativeX * .6];
  return {time:t,primary,debris,metresPerUnit,separationM:Math.hypot(relativeX, gap) * metresPerUnit};
}
export type SortOrder = 'priority' | 'horizon' | 'pc' | 'distance' | 'event';
export function dashboardRows(rows: Encounter[], search: string, risk: string, sort: SortOrder) {
  const priority = {critical:0,elevated:1,safe:2,unknown:3};
  const result = rows.filter(row => row.event_id.toLowerCase().includes(search.trim().toLowerCase()) && (risk === 'all' || row.severity === risk));
  return result.sort((a,b) => {
    const comparison = sort === 'priority' ? priority[a.severity] - priority[b.severity] : sort === 'horizon' ? a.time_to_tca_hours - b.time_to_tca_hours : sort === 'pc' ? (b.predicted_pc ?? -1) - (a.predicted_pc ?? -1) : sort === 'distance' ? (a.miss_distance_m ?? Infinity) - (b.miss_distance_m ?? Infinity) : 0;
    return comparison || (sort === 'priority' ? a.time_to_tca_hours - b.time_to_tca_hours : 0) || a.event_id.localeCompare(b.event_id);
  });
}
export function eventRoute(path: string): string | null {
  const match = /^\/encounters\/([^/]+)\/?$/.exec(path);
  if (!match) return null;
  try { return decodeURIComponent(match[1]); } catch { return null; }
}

/** Requires two explicit clocks; lead time is never report age. */
export function reportAgeHours(reportTimestamp: string | null, referenceClock: string | null): number | null {
  if (!reportTimestamp || !referenceClock) return null;
  const zonedIso = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
  if (!zonedIso.test(reportTimestamp) || !zonedIso.test(referenceClock)) return null;
  const report = Date.parse(reportTimestamp), reference = Date.parse(referenceClock);
  if (!Number.isFinite(report) || !Number.isFinite(reference) || report > reference) return null;
  return (reference - report) / 3_600_000;
}
export function sliderSample(raw: number, reducedMotion = false) {
  const time = clampTime(raw), overshoot = Number.isFinite(raw) ? raw - time : 0;
  return {time,visualOffset:reducedMotion ? 0 : overshoot * .32 * 100};
}
export function advancePlayback(time: number, elapsedMs: number, speed: number) {
  const next = clampTime(time + Math.max(0, Math.min(100, elapsedMs)) / 10000 * Math.max(0, speed));
  return time < .5 && next >= .5 ? .5 : next;
}

export const horizonStops = [1,3,7,Infinity] as const;
export function discreteHorizon(raw:number) { return Math.round(clampTime(raw)*3); }
export function easeOutCubic(progress:number) { return 1-(1-clampTime(progress))**3; }
export function animatedMetric(value:number|null,progress:number,kind:'time'|'pc'|'distance') {
 if(value===null)return 'Unavailable';
 const p=easeOutCubic(progress);
 if(kind==='pc'){
  if(value===0)return '0';
  const [mantissa,exponent]=value.toExponential(3).split('e');
  const superscripts:Record<string,string>={'-':'⁻','+':'','0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'};
  return `${(Number(mantissa)*p).toFixed(3)} × 10${String(Number(exponent)).split('').map(c=>superscripts[c]).join('')}`;
 }
 const scale=kind==='distance'&&value>=1000?1000:1;
 return `${(value*p/scale).toLocaleString(undefined,{maximumFractionDigits:kind==='time'?3:scale===1000?6:3})} ${kind==='time'?'h':scale===1000?'km':'m'}`;
}

/** A playback pass holds exactly at TCA once; elapsed time never advances invisibly. */
export function playbackStep(time:number,elapsedMs:number,speed:number,holdMs:number,held:boolean){
 const elapsed=Math.max(0,Math.min(100,elapsedMs));
 if(holdMs>0)return {time:.5,holdMs:Math.max(0,holdMs-elapsed),held:true};
 const next=advancePlayback(time,elapsed,speed);
 if(!held&&time<.5&&next===.5)return {time:.5,holdMs:1750,held:true};
 return {time:next,holdMs:0,held};
}

/** Pointer-only TCA capture keeps the minimum-distance annotation inspectable. */
export function pointerEncounterTime(value:number){const time=clampTime(value);return Math.abs(time-.5)<=.010000000001?.5:time;}

/** Source vectors are not epoch-tagged. Only the canonical synthetic fixture may
 * illustrate a short linear interval by explicitly assuming its state is at TCA. */
export function encounterMotion(analysis:AnalysisResult,row:Encounter,canonical:AnalysisResult){
 const g=row.geometry,r=g?.position_m,v=g?.velocity_mps;
 if(analysis.source.mode!=='synthetic_demo'||analysis.model.status!=='fixture'||row.prediction_status!=='fixture'||g?.frame!=='RTN'||!r||!v||row.miss_distance_m===null)return null;
 // Demo copies receive fresh analysis identities. Trust the fixture's content and
 // provenance, never a mutable/literal analysis ID or an uploaded epoch-free state.
 const expected=canonical.encounters.find(e=>e.event_id===row.event_id);
 const same=(a:unknown,b:unknown):boolean=>{if(a===b)return true;if(Array.isArray(a)&&Array.isArray(b))return a.length===b.length&&a.every((value,i)=>same(value,b[i]));if(a&&b&&typeof a==='object'&&typeof b==='object'){const x=a as Record<string,unknown>,y=b as Record<string,unknown>;return Object.keys(x).length===Object.keys(y).length&&Object.keys(x).every(key=>Object.hasOwn(y,key)&&same(x[key],y[key]));}return false;};
 if(!same(analysis.source,canonical.source)||!same(analysis.model,canonical.model)||analysis.time_basis!==canonical.time_basis||analysis.scenario_clock_utc!==canonical.scenario_clock_utc||!expected||!same(row,expected))return null;
 const position=[r.r,r.t,r.n] as [number,number,number],velocity=[v.r,v.t,v.n] as [number,number,number];
 if(![...position,...velocity,row.miss_distance_m].every(Number.isFinite)||row.miss_distance_m<0)return null;
 const gap=Math.hypot(...position),speed=Math.hypot(...velocity),dot=position.reduce((sum,n,i)=>sum+n*velocity[i],0);
 if(speed<=0||Math.abs(gap-row.miss_distance_m)>Math.max(.001,gap*1e-6)||Math.abs(dot)>Math.max(.001,gap*speed*1e-6))return null;
 const metresPerUnit=Math.max(gap/4,1),halfWindowSeconds=12*metresPerUnit/speed;
 return {position,velocity,metresPerUnit,halfWindowSeconds};
}
export function relativeMotionSample(model:NonNullable<ReturnType<typeof encounterMotion>>,time:number){
 const t=clampTime(time),seconds=(t-.5)*2*model.halfWindowSeconds;
 const relative=model.position.map((n,i)=>n+model.velocity[i]*seconds) as [number,number,number];
 return {time:t,seconds,primary:[0,0,0] as [number,number,number],debris:relative.map(n=>n/model.metresPerUnit) as [number,number,number],metresPerUnit:model.metresPerUnit,separationM:Math.hypot(...relative)};
}
