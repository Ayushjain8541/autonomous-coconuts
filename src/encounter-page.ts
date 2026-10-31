import {INSIGHT_TIMEOUT_MS,REPORT_TIMEOUT_MS} from '../web/client/report.ts';
import type { AnalysisResult, Encounter } from '../web/client/contract.ts';
import { ApiError, parseInsights } from '../web/client/contract.ts';
import { generateReport, downloadReportPdf, loadInsights } from '../web/client/api.ts';
import { maneuverReview, animatedMetric } from '../web/client/encounter-model.ts';
import fixture from '../contracts/fixtures/insights-demo.json';
import { mountPlayback } from './encounter-scene';

function text(tag:string,value:string,className='') {
  const e=document.createElement(tag);e.textContent=value;e.className=className;return e;
}
export function mountEncounterPage(host:HTMLElement,analysis:AnalysisResult,row:Encounter,localFixture:boolean,onBack:()=>void,outside:boolean) {
  host.innerHTML=`<header class="encounter-page-header"><button class="back-dashboard">← Back to Dashboard</button><div><h1 tabindex="-1"></h1><p class="encounter-source"></p></div></header><div class="encounter-page-content"><section class="encounter-intelligence" aria-label="Encounter intelligence"><section class="assessment-card"><h2>Encounter intelligence</h2><div class="planning-alert"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 3 2 21h20L12 3Z"/><path d="M12 9v5m0 3v1"/></svg><p class="planning-decision"></p></div><div class="risk-class"><span>Risk class</span><strong></strong></div><div class="key-metrics"></div><p class="outside-page-filter" hidden>Selected encounter is outside the current dashboard filter.</p></section><div class="report-download"><button disabled aria-describedby="report-download-status"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></svg>Download Latest Source Report</button><small id="report-download-status">Coming soon</small></div><div class="report-download analytical-report"><button class="generate-report">Download Analytical PDF</button><small class="analytical-report-status" role="status">Full analysis briefing · separate from the source report</small></div><details class="insight-card"><summary>AI Insights <span class="insight-status">Not requested</span></summary><div class="insight-content" aria-live="polite"><p>Explain this encounter using the analysis facts.</p><button class="request-insights">Explain assessment</button></div></details></section><section class="encounter-visualization" aria-label="Interactive encounter schematic"></section></div>`;
  const title=host.querySelector<HTMLElement>('h1')!;title.textContent=row.event_id;title.focus();
  host.querySelector('.back-dashboard')!.addEventListener('click',onBack);
  host.querySelector('.encounter-source')!.textContent=analysis.source.mode==='synthetic_demo'?'Demo data':analysis.model.status==='unavailable'?'Imported CSV · prediction unavailable':'Imported CSV';
  const assessment=host.querySelector<HTMLElement>('.assessment-card')!;assessment.dataset.risk=row.severity;
  host.querySelector('.planning-decision')!.textContent=maneuverReview(row.severity);
 const icon=host.querySelector('.planning-alert svg')!;icon.innerHTML=row.severity==='safe'?'<path d="M12 3 3 7v5c0 5 9 9 9 9s9-4 9-9V7l-9-4Z"/><path d="m8 12 3 3 5-6"/>':row.severity==='unknown'?'<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-11v2"/>':row.severity==='elevated'?'<path d="m8 3-5 5v8l5 5h8l5-5V8l-5-5H8Z"/><path d="M12 7v7m0 2v1"/>':'<path d="M12 3 2 21h20L12 3Z"/><path d="M12 9v5m0 3v1"/>';
 const effects=text('button','Pause effects','effects-toggle');effects.setAttribute('aria-pressed','false');assessment.querySelector('.risk-class')!.append(effects);effects.addEventListener('click',()=>{const paused=assessment.classList.toggle('effects-paused');effects.textContent=paused?'Resume effects':'Pause effects';effects.setAttribute('aria-pressed',String(paused));});
  host.querySelector('.risk-class strong')!.textContent=row.severity.toUpperCase();host.querySelector('.risk-class strong')!.setAttribute('data-text',row.severity.toUpperCase());
  const metrics=host.querySelector('.key-metrics')!;
  const definitions=[['Time to closest approach',row.time_to_tca_hours,'time'],['Predicted collision probability (Pc)',row.predicted_pc,'pc'],['Predicted miss distance',row.miss_distance_m,'distance']] as const;
  const values=definitions.map(([label,value,kind])=>{const group=text('div','');const output=text('strong',animatedMetric(value,1,kind));output.setAttribute('aria-label',animatedMetric(value,1,kind));group.append(text('span',label),output);metrics.append(group);return output;});
  const qualifier=text('p',analysis.time_basis==='per_event_latest_report'?'As of latest source report':'Demo scenario horizon','metric-qualifier');metrics.children[0].append(qualifier);
  const predictionQualifier=row.prediction_status==='unavailable'||analysis.model.status==='unavailable'?'Prediction unavailable':row.prediction_status==='fixture'||analysis.model.status==='fixture'?'Fixture prediction':'Model prediction';metrics.children[1].append(text('p',predictionQualifier,'metric-qualifier'));
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');let metricFrame=0;
  const started=performance.now();
  function animate(now:number){const progress=reduced.matches?1:Math.min(1,(now-started)/1000);definitions.forEach(([,value,kind],i)=>{values[i].textContent=animatedMetric(value,progress,kind)});if(progress<1)metricFrame=requestAnimationFrame(animate);}
  if(!reduced.matches)metricFrame=requestAnimationFrame(animate);
  host.querySelector<HTMLElement>('.outside-page-filter')!.hidden=!outside;
  const playback=mountPlayback(host.querySelector<HTMLElement>('.encounter-visualization')!,analysis,row);
  const insight=host.querySelector('.insight-content')!,status=host.querySelector('.insight-status')!,explainButton=host.querySelector<HTMLButtonElement>('.request-insights')!;let controller=new AbortController();let active=true,timedOut=false,timeout=0,requested=false;
  function requestExplanation(){
   if(requested)return;if(document.activeElement===explainButton)host.querySelector<HTMLElement>('.insight-card>summary')!.focus();requested=true;timedOut=false;controller=new AbortController();status.textContent='Pending';explainButton.disabled=true;explainButton.textContent='Requesting explanation…';insight.replaceChildren(text('p','Requesting a grounded explanation…'),explainButton);
   timeout=window.setTimeout(()=>{timedOut=true;controller.abort()},INSIGHT_TIMEOUT_MS);
   const operation=localFixture?Promise.resolve(parseInsights({...fixture,items:fixture.items.filter(i=>i.event_id===row.event_id)},analysis,[row.event_id])):loadInsights(analysis,[row.event_id],controller.signal);
   operation.then(result=>{
    clearTimeout(timeout);if(!active||controller.signal.aborted||result.analysis_id!==analysis.analysis_id)return;
    status.textContent=result.status;explainButton.disabled=false;explainButton.textContent='Refresh explanation';insight.replaceChildren(explainButton);requested=false;const item=result.items.find(i=>i.event_id===row.event_id);
    if(item){insight.append(text('p',item.summary,'assistant-message'));for(const limitation of item.limitations)insight.append(text('p',limitation));insight.append(text('p',`Grounded fields: ${item.fact_refs.map(ref=>ref.field).join(', ')}`));}else insight.append(text('p','No explanation is available for this encounter.'));
    for(const warning of result.warnings)insight.append(text('p',warning));
   }).catch(error=>{clearTimeout(timeout);if(!active||(controller.signal.aborted&&!timedOut))return;const unavailable=timedOut||(error instanceof ApiError&&error.code==='INSIGHTS_UNAVAILABLE');status.textContent=unavailable?'Unavailable':'Error';insight.replaceChildren(text('p',timedOut?'Explanation request timed out. Numeric analysis remains available.':(error as Error).message),text('p','Risk and numeric assessment remain available.'));requested=false;explainButton.disabled=false;explainButton.textContent='Retry explanation';insight.append(explainButton);});
  }
  explainButton.addEventListener('click',requestExplanation);
  const reportButton=host.querySelector<HTMLButtonElement>('.generate-report')!,reportStatus=host.querySelector<HTMLElement>('.analytical-report-status')!;
  let reportController:AbortController|null=null,reportTimeout=0,reportTimedOut=false,objectUrl:string|null=null;
  reportButton.addEventListener('click',async()=>{
   if(reportController)return;
   if(localFixture){reportStatus.textContent='Unavailable for a local UI preview. Load the API demo or import an analysis first.';return;}
   const requestController=new AbortController();reportController=requestController;reportTimedOut=false;reportButton.disabled=true;reportStatus.textContent='Generating full-analysis briefing and PDF…';
   reportTimeout=window.setTimeout(()=>{reportTimedOut=true;requestController.abort()},REPORT_TIMEOUT_MS);
   try{
    const report=await generateReport(analysis,requestController.signal);
    if(!active||requestController.signal.aborted||report.analysis_id!==analysis.analysis_id)return;
    const narrative=report.status==='unavailable'?'Narrative unavailable; deterministic analysis PDF available.':'Analytical report ready.';
    reportStatus.textContent=narrative+' Downloading PDF…';
    clearTimeout(reportTimeout);
    reportTimeout=window.setTimeout(()=>{reportTimedOut=true;requestController.abort()},REPORT_TIMEOUT_MS);
    const blob=await downloadReportPdf(report,requestController.signal);
    if(!active||requestController.signal.aborted)return;
    if(objectUrl)URL.revokeObjectURL(objectUrl);objectUrl=URL.createObjectURL(blob);
    const link=document.createElement('a');link.href=objectUrl;link.download=`analytical-report-${report.report_id}.pdf`;host.append(link);link.click();link.remove();
    reportStatus.textContent=[narrative,'PDF download started.',...report.warnings].join(' ');
   }catch(error){if(!active||(requestController.signal.aborted&&!reportTimedOut))return;reportStatus.textContent=reportTimedOut?'Analytical report timed out. Retry; numeric assessment remains available.':`${error instanceof ApiError?error.code+': ':''}${(error as Error).message} Numeric assessment remains available.`;}
   finally{clearTimeout(reportTimeout);if(active){reportButton.disabled=false;reportButton.textContent='Download Analytical PDF';}reportController=null;}
  });

  return {dispose(){active=false;clearTimeout(reportTimeout);reportController?.abort();if(objectUrl)URL.revokeObjectURL(objectUrl);cancelAnimationFrame(metricFrame);clearTimeout(timeout);controller.abort();playback.dispose();host.replaceChildren();}};
}
