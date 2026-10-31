export type Severity = 'critical'|'elevated'|'safe'|'unknown';
export type Availability = 'ready'|'fixture'|'unavailable';
export interface RuleReason {rule_id:string;field:string;operator?:string;value?:number;threshold?:number;unit?:string}
export interface Vector {r:number;t:number;n:number}
export interface Encounter {event_id:string;mission_id:string|null;report_count:number;latest_report_id:string;report_ids:string[];time_to_tca_hours:number;reported_pc:number|null;predicted_pc:number|null;predicted_log10_pc:number|null;prediction_status:Availability;miss_distance_m:number|null;relative_speed_mps:number|null;severity:Severity;flag_reasons:RuleReason[];geometry:null|{frame:'RTN';position_m:Vector|null;velocity_mps:Vector|null};globe_position:unknown;warnings:string[]}
export interface AnalysisResult {schema_version:'1.0';analysis_id:string;source:{mode:'synthetic_demo'|'uploaded_csv';label:string;sha256:string|null;report_count:number};time_basis:'scenario_clock'|'per_event_latest_report';scenario_clock_utc:string|null;model:{version:string|null;status:Availability;target:string;feature_schema_version:string|null};encounters:Encounter[];warnings:string[]}
export interface InsightItem {event_id:string;summary:string;fact_refs:{event_id:string;field:string}[];limitations:string[]}
export interface InsightsResult {schema_version:'1.0';analysis_id:string;status:Availability;items:InsightItem[];warnings:string[]}
export const factFields = ['predicted_pc','reported_pc','miss_distance_m','relative_speed_mps','time_to_tca_hours','severity','flag_reasons','prediction_status'];
const fail=(field:string):never=>{throw new Error(`Invalid API response: ${field}`)};
const object=(x:unknown,field:string):Record<string,unknown>=>typeof x==='object'&&x!==null&&!Array.isArray(x)?x as Record<string,unknown>:fail(field);
const str=(x:unknown,f:string):string=>typeof x==='string'&&x.length>0?x:fail(f);
const nullableString=(x:unknown,f:string)=>x===null?null:str(x,f);
const list=(x:unknown,f:string):unknown[]=>Array.isArray(x)?x:fail(f);
const strings=(x:unknown,f:string)=>list(x,f).map(item=>str(item,f));
const num=(x:unknown,f:string,min=0,max=Infinity):number=>typeof x==='number'&&Number.isFinite(x)&&x>=min&&x<=max?x:fail(f);
const nullableNum=(x:unknown,f:string,min=0,max=Infinity)=>x===null?null:num(x,f,min,max);
const integer=(x:unknown,f:string,min=0)=>{const n=num(x,f,min);return Number.isInteger(n)?n:fail(f)};
function member<T extends string>(x:unknown,values:readonly T[],f:string):T{return typeof x==='string'&&values.includes(x as T)?x as T:fail(f)}
function vector(x:unknown,f:string):Vector|null {if(x===null)return null;const v=object(x,f);return {r:num(v.r,f,-Infinity),t:num(v.t,f,-Infinity),n:num(v.n,f,-Infinity)}}
export function parseAnalysis(raw:unknown):AnalysisResult {
 const d=object(raw,'analysis');member(d.schema_version,['1.0'],'schema_version');const source=object(d.source,'source'),model=object(d.model,'model');
 const encounters=list(d.encounters,'encounters').map((item):Encounter=>{
  const e=object(item,'encounter'),g=e.geometry===null?null:object(e.geometry,'geometry');
  const predicted_pc=nullableNum(e.predicted_pc,'predicted_pc',0,1),log=nullableNum(e.predicted_log10_pc,'predicted_log10_pc',-Infinity,0);
  if(log!==null&&(predicted_pc===null||Math.abs(10**log-predicted_pc)>Math.max(Number.MIN_VALUE,(predicted_pc||Number.MIN_VALUE)*1e-6)))fail('Pc/log10 agreement');
  const report_ids=strings(e.report_ids,'report_ids'),latest_report_id=str(e.latest_report_id,'latest_report_id');if(!report_ids.includes(latest_report_id))fail('latest_report_id provenance');
  return {event_id:str(e.event_id,'event_id'),mission_id:nullableString(e.mission_id,'mission_id'),report_count:integer(e.report_count,'report_count',1),latest_report_id,report_ids,time_to_tca_hours:num(e.time_to_tca_hours,'time_to_tca_hours'),reported_pc:nullableNum(e.reported_pc,'reported_pc',0,1),predicted_pc,predicted_log10_pc:log,prediction_status:member(e.prediction_status,['ready','fixture','unavailable'],'prediction_status'),miss_distance_m:nullableNum(e.miss_distance_m,'miss_distance_m'),relative_speed_mps:nullableNum(e.relative_speed_mps,'relative_speed_mps'),severity:member(e.severity,['critical','elevated','safe','unknown'],'severity'),flag_reasons:list(e.flag_reasons,'flag_reasons').map(value=>{const r=object(value,'reason');return {rule_id:str(r.rule_id,'rule_id'),field:str(r.field,'field'),...(r.operator!==undefined?{operator:str(r.operator,'operator')}:{}),...(r.value!==undefined?{value:num(r.value,'reason value',-Infinity)}:{}),...(r.threshold!==undefined?{threshold:num(r.threshold,'threshold',-Infinity)}:{}),...(r.unit!==undefined?{unit:str(r.unit,'unit')}:{} )}}),geometry:g?{frame:member(g.frame,['RTN'],'geometry frame'),position_m:vector(g.position_m,'position_m'),velocity_mps:vector(g.velocity_mps,'velocity_mps')}:null,globe_position:e.globe_position,warnings:strings(e.warnings,'encounter warnings')};
 });
 if(new Set(encounters.map(e=>e.event_id)).size!==encounters.length)fail('duplicate event_id');
 const basis=member(d.time_basis,['scenario_clock','per_event_latest_report'],'time_basis'),clock=nullableString(d.scenario_clock_utc,'scenario_clock_utc');if(basis==='per_event_latest_report'&&clock!==null)fail('uploaded clock');if(clock!==null&&!Number.isFinite(Date.parse(clock)))fail('scenario_clock_utc');
 return {schema_version:'1.0',analysis_id:str(d.analysis_id,'analysis_id'),source:{mode:member(source.mode,['synthetic_demo','uploaded_csv'],'source.mode'),label:str(source.label,'source.label'),sha256:nullableString(source.sha256,'sha256'),report_count:integer(source.report_count,'source.report_count')},time_basis:basis,scenario_clock_utc:clock,model:{version:nullableString(model.version,'model.version'),status:member(model.status,['ready','fixture','unavailable'],'model.status'),target:str(model.target,'model.target'),feature_schema_version:nullableString(model.feature_schema_version,'feature_schema_version')},encounters,warnings:strings(d.warnings,'warnings')};
}
export function parseInsights(raw:unknown,analysis:AnalysisResult,requested:string[]):InsightsResult {
 const d=object(raw,'insights');member(d.schema_version,['1.0'],'schema_version');if(d.analysis_id!==analysis.analysis_id)fail('stale insights analysis_id');
 const known=new Set(analysis.encounters.map(e=>e.event_id));const items=list(d.items,'insight items').map(value=>{const i=object(value,'insight item'),id=str(i.event_id,'insight event_id');if(!known.has(id)||!requested.includes(id))fail('unknown insight event_id');return {event_id:id,summary:str(i.summary,'summary'),limitations:strings(i.limitations,'limitations'),fact_refs:list(i.fact_refs,'fact_refs').map(value=>{const ref=object(value,'fact reference');if(ref.event_id!==id||!factFields.includes(String(ref.field)))fail('unsupported insight fact reference');return {event_id:id,field:String(ref.field)}})}});
 if(new Set(items.map(i=>i.event_id)).size!==items.length)fail('duplicate insight');
 return {schema_version:'1.0',analysis_id:analysis.analysis_id,status:member(d.status,['ready','fixture','unavailable'],'insight status'),items,warnings:strings(d.warnings,'insight warnings')};
}
export interface ErrorDetail {row:number|null;column:string|null;reason:string}
export class ApiError extends Error {code:string;details:ErrorDetail[];total:number|null;constructor(code:string,message:string,details:ErrorDetail[]=[],total:number|null=null){super(message);this.name='ApiError';this.code=code;this.details=details;this.total=total}}
export function parseApiError(raw:unknown,status:number):ApiError {try{const e=object(object(raw,'error envelope').error,'error');const details=list(e.details,'details').slice(0,100).map(value=>{const d=object(value,'detail');return {row:d.row===null?null:integer(d.row,'row'),column:d.column===null?null:str(d.column,'column'),reason:str(d.reason,'reason')}});return new ApiError(str(e.code,'code'),str(e.message,'message'),details,typeof e.total_error_count==='number'?integer(e.total_error_count,'total_error_count'):null)}catch{return new ApiError('HTTP_ERROR',`Request failed (HTTP ${status}). The server did not return a valid error envelope.`)}}
