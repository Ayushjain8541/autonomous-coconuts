import {ApiError,type AnalysisResult} from './contract.ts';
/** Provider limits are 60s for insights and 90s for reports, plus transport cleanup. */
export const INSIGHT_TIMEOUT_MS=75_000;
export const REPORT_TIMEOUT_MS=100_000;
export interface AnalyticalReport {analysis_id:string;report_id:string;status:'ready'|'unavailable';pdf_url:string;warnings:string[];limitations:string[]}
const invalid=():never=>{throw new ApiError('INVALID_REPORT','The API returned an invalid or mismatched analytical report.');};
export function parseReport(raw:unknown,analysis:AnalysisResult):AnalyticalReport {
 if(!raw||typeof raw!=='object'||Array.isArray(raw))return invalid();
 const r=raw as Record<string,unknown>;
 const strings=(x:unknown):x is string[]=>Array.isArray(x)&&x.every(s=>typeof s==='string');
 const same=(a:unknown,b:unknown)=>{if(!a||typeof a!=='object')return false;return Object.entries(b as Record<string,unknown>).every(([key,value])=>(a as Record<string,unknown>)[key]===value);};
 if(r.schema_version!=='1.0'||r.analysis_id!==analysis.analysis_id||typeof r.report_id!=='string'||!/^[A-Za-z0-9_-]{1,128}$/.test(r.report_id)||(r.status!=='ready'&&r.status!=='unavailable')||typeof r.generated_at!=='string'||!Number.isFinite(Date.parse(r.generated_at))||!same(r.source,analysis.source)||!same(r.model,analysis.model)||r.time_basis!==analysis.time_basis||!strings(r.warnings)||!strings(r.limitations))return invalid();
 const path=`/api/analyses/${encodeURIComponent(analysis.analysis_id)}/reports/${encodeURIComponent(r.report_id)}.pdf`;
 // Relative, exact same-origin API route only; never follow a provider URL.
 if(r.pdf_url!==path)return invalid();
 return {analysis_id:analysis.analysis_id,report_id:r.report_id,status:r.status,pdf_url:path,warnings:r.warnings,limitations:r.limitations};
}
