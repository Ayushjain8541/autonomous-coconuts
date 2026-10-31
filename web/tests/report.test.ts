import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {parseAnalysis,parseInsights,parseApiError} from '../client/contract.ts';
import {generateReport,downloadReportPdf} from '../client/api.ts';
import {parseReport,REPORT_TIMEOUT_MS,INSIGHT_TIMEOUT_MS} from '../client/report.ts';
const analysis=parseAnalysis(JSON.parse(readFileSync(new URL('../../contracts/fixtures/analysis-demo.json',import.meta.url),'utf8')));
const report=()=>({schema_version:'1.0',analysis_id:analysis.analysis_id,report_id:'report-1',generated_at:'2026-10-31T04:00:00Z',status:'unavailable',source:analysis.source,model:analysis.model,time_basis:analysis.time_basis,warnings:['Provider unavailable'],limitations:['Advisory only'],pdf_url:`/api/analyses/${analysis.analysis_id}/reports/report-1.pdf`});
test('geometry fact references accepted without relaxing event or analysis identity',()=>{
 const raw={schema_version:'1.0',analysis_id:analysis.analysis_id,status:'ready',warnings:[],items:[{event_id:analysis.encounters[0].event_id,summary:'Inspect source geometry',limitations:[],fact_refs:[{event_id:analysis.encounters[0].event_id,field:'geometry'}]}]};
 assert.equal(parseInsights(raw,analysis,[analysis.encounters[0].event_id]).items[0].fact_refs[0].field,'geometry');
 assert.throws(()=>parseInsights({...raw,analysis_id:'stale'},analysis,[analysis.encounters[0].event_id]));
 raw.items[0].fact_refs[0].event_id=analysis.encounters[1].event_id;assert.throws(()=>parseInsights(raw,analysis,[analysis.encounters[0].event_id]));
});
test('canonical total_errors retains true bounded validation count, with legacy fallback',()=>{
 const details=Array.from({length:120},(_,i)=>({row:i+1,column:'event_id',reason:'missing'}));
 const result=parseApiError({error:{code:'INVALID_CSV',message:'Invalid',details,total_errors:300,total_error_count:120}},422);
 assert.equal(result.details.length,100);assert.equal(result.total,300);
 assert.equal(parseApiError({error:{code:'INVALID_CSV',message:'Invalid',details:[],total_error_count:12}},422).total,12);
});
test('report response binds analysis, provenance and exact same-origin PDF path',()=>{
 assert.equal(parseReport(report(),analysis).status,'unavailable');
 for(const patch of [{analysis_id:'stale'},{report_id:'../escape'},{pdf_url:'https://example.com/x.pdf'},{pdf_url:'//example.com/x.pdf'},{pdf_url:report().pdf_url+'?redirect=x'},{source:{...analysis.source,label:'other'}},{status:'fixture'},{model:{...analysis.model,status:'ready'}}])assert.throws(()=>parseReport({...report(),...patch},analysis));
 assert.ok(REPORT_TIMEOUT_MS>95_000);assert.ok(INSIGHT_TIMEOUT_MS>60_000);
});
test('report transport posts empty object and downloads real PDF even without narrative',async()=>{
 const original=globalThis.fetch;const calls:{url:string;init:RequestInit}[]=[];
 globalThis.fetch=async(url,init={})=>{calls.push({url:String(url),init});return String(url).endsWith('.pdf')?new Response('%PDF-1.7\nfixture',{headers:{'Content-Type':'application/pdf'}}):new Response(JSON.stringify(report()));};
 try{const result=await generateReport(analysis);assert.equal(result.status,'unavailable');const blob=await downloadReportPdf(result);assert.ok(blob.size>5);assert.equal(calls[0].url,`/api/analyses/${analysis.analysis_id}/report`);assert.equal(calls[0].init.body,'{}');assert.equal(calls[0].init.method,'POST');assert.equal(calls[1].url,result.pdf_url);assert.equal(calls[1].init.redirect,'error');}finally{globalThis.fetch=original;}
});
test('PDF unavailable errors and non-PDF bodies never masquerade as downloads',async()=>{
 const original=globalThis.fetch;const parsed=parseReport(report(),analysis);
 try{
  globalThis.fetch=async()=>new Response(JSON.stringify({error:{code:'PDF_UNAVAILABLE',message:'Install PDF dependency',details:[]}}),{status:503});
  await assert.rejects(()=>downloadReportPdf(parsed),{code:'PDF_UNAVAILABLE'});
  globalThis.fetch=async()=>new Response('html',{headers:{'Content-Type':'text/html'}});await assert.rejects(()=>downloadReportPdf(parsed),{code:'PDF_UNAVAILABLE'});
  globalThis.fetch=async()=>new Response('not a pdf',{headers:{'Content-Type':'application/pdf'}});await assert.rejects(()=>downloadReportPdf(parsed),{code:'PDF_UNAVAILABLE'});
  await assert.rejects(()=>downloadReportPdf({...parsed,pdf_url:'https://example.com/stolen'}),{code:'INVALID_REPORT'});
 }finally{globalThis.fetch=original;}
});
test('report and PDF requests propagate cancellation for navigation and bounded waiting',async()=>{
 const original=globalThis.fetch;const controller=new AbortController();let received:AbortSignal|null|undefined;
 globalThis.fetch=async(_url,init={})=>{received=init.signal;throw new DOMException('Aborted','AbortError');};
 try{controller.abort();await assert.rejects(()=>generateReport(analysis,controller.signal),{name:'AbortError'});assert.equal(received,controller.signal);await assert.rejects(()=>downloadReportPdf(parseReport(report(),analysis),controller.signal),{name:'AbortError'});}finally{globalThis.fetch=original;}
});
