import type {AnalysisResult,Encounter} from './contract.ts';
export const probability=(value:number|null)=>value===null?'Unavailable':value===0?'0':value.toExponential(3);
export const measure=(value:number|null,unit:string)=>value===null?'Unavailable':`${value.toLocaleString(undefined,{maximumFractionDigits:3})} ${unit}`;
export function filteredEncounters(analysis:AnalysisResult,days:number,criticalOnly:boolean){return analysis.encounters.filter(e=>e.time_to_tca_hours<=days*24&&(!criticalOnly||(e.severity==='critical'&&e.time_to_tca_hours>=0&&e.time_to_tca_hours<=24)))}
export function globalCritical(analysis:AnalysisResult):Encounter|undefined{return analysis.encounters.filter(e=>e.severity==='critical').sort((a,b)=>a.time_to_tca_hours-b.time_to_tca_hours||a.event_id.localeCompare(b.event_id))[0]}
export function outsideFilter(id:string|null,rows:Encounter[]){return id!==null&&!rows.some(row=>row.event_id===id)}
export class InsightGuard {private revision=0;begin(){return ++this.revision}invalidate(){++this.revision}current(token:number,expectedAnalysis:string,currentAnalysis:string,expectedEvent:string,currentEvent:string|null){return token===this.revision&&expectedAnalysis===currentAnalysis&&expectedEvent===currentEvent}}

/** Cancelling or replacing an operation invalidates even a late successful response. */
export class OperationGuard {private generation=0;begin(){return ++this.generation}cancel(){++this.generation}current(token:number){return token===this.generation}}
