import {parseReport,type AnalyticalReport} from './report.ts';
import {ApiError,parseAnalysis,parseApiError,parseInsights,type AnalysisResult} from './contract.ts';
async function jsonRequest(path:string,init:RequestInit={}) {let response:Response;try{response=await fetch(path,init)}catch(error){if((error as Error).name==='AbortError')throw error;throw new ApiError('CONNECTION_UNAVAILABLE','Cannot reach the API. Check the backend connection; no local fixture was substituted.')}let data:unknown;try{data=await response.json()}catch{throw new ApiError('INVALID_RESPONSE',`The API returned unreadable JSON (HTTP ${response.status}).`)}if(!response.ok)throw parseApiError(data,response.status);return data}
export async function loadDemo(signal?:AbortSignal){return parseAnalysis(await jsonRequest('/api/demo',{signal}))}
export async function uploadAnalysis(file:File,signal?:AbortSignal){const form=new FormData();form.append('file',file);return parseAnalysis(await jsonRequest('/api/analyses',{method:'POST',body:form,signal}))}
export async function loadInsights(analysis:AnalysisResult,ids:string[],signal?:AbortSignal){if(ids.length<1||ids.length>10||new Set(ids).size!==ids.length||ids.some(id=>!analysis.encounters.some(e=>e.event_id===id)))throw new ApiError('UNKNOWN_EVENT','Choose 1–10 unique events belonging to this analysis.');return parseInsights(await jsonRequest(`/api/analyses/${encodeURIComponent(analysis.analysis_id)}/insights`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({event_ids:ids}),signal}),analysis,ids)}

export async function generateReport(analysis:AnalysisResult,signal?:AbortSignal){return parseReport(await jsonRequest(`/api/analyses/${encodeURIComponent(analysis.analysis_id)}/report`,{method:'POST',headers:{'Content-Type':'application/json'},body:'{}',signal}),analysis)}
/** Fetch first so PDF export failures remain visible instead of downloading JSON. */
export async function downloadReportPdf(report:AnalyticalReport,signal?:AbortSignal){
 const expected=`/api/analyses/${encodeURIComponent(report.analysis_id)}/reports/${encodeURIComponent(report.report_id)}.pdf`;
 if(report.pdf_url!==expected)throw new ApiError('INVALID_REPORT','Unexpected analytical PDF path.');
 let response:Response;try{response=await fetch(expected,{signal,redirect:'error'})}catch(error){if((error as Error).name==='AbortError')throw error;throw new ApiError('CONNECTION_UNAVAILABLE','Cannot reach the analytical PDF export.');}
 if(!response.ok){let error:unknown;try{error=await response.json()}catch{throw new ApiError('PDF_UNAVAILABLE',`Analytical PDF export failed (HTTP ${response.status}).`)}throw parseApiError(error,response.status);}
 if(response.headers.get('Content-Type')?.split(';')[0].trim().toLowerCase()!=='application/pdf')throw new ApiError('PDF_UNAVAILABLE','The export did not return a PDF.');
 const blob=await response.blob();if(await blob.slice(0,5).text()!=='%PDF-')throw new ApiError('PDF_UNAVAILABLE','The export returned an unreadable PDF.');
 return blob;
}
