import type { AnalysisResult, Encounter } from '../web/client/contract.ts';
import { parseInsights } from '../web/client/contract.ts';
import { loadInsights } from '../web/client/api.ts';
import { probability, measure } from '../web/client/state.ts';
import { maneuverReview, remainingTime } from '../web/client/encounter-model.ts';
import fixture from '../contracts/fixtures/insights-demo.json';
import { mountPlayback } from './encounter-scene';

function text(tag:string,value:string,className='') {
  const e=document.createElement(tag);e.textContent=value;e.className=className;return e;
}
export function mountEncounterPage(host:HTMLElement,analysis:AnalysisResult,row:Encounter,localFixture:boolean,onBack:()=>void,outside:boolean) {
  host.innerHTML=`<header class="encounter-page-header"><button class="back-dashboard">← Back to Dashboard</button><div><h1 tabindex="-1"></h1><p class="encounter-source"></p></div><span class="severity-tag page-risk"></span></header><div class="encounter-page-content"><section class="encounter-intelligence" aria-label="Encounter intelligence"><section class="assessment-card"><h2>Encounter intelligence</h2><p class="planning-decision"></p><p class="operator-limit">Recommendation for operator review only. No maneuver has been calculated, executed or approved.</p><p class="encounter-lead"></p><p class="lead-basis"></p><div class="prediction-pair"></div><p class="model-identity"></p><p class="outside-page-filter" hidden>Selected encounter is outside the current dashboard filter.</p></section><section class="report-card"><h2>Latest source report</h2><div class="report-summary"></div><details><summary>Source identities and technical details</summary><div class="report-details"></div></details></section><section class="insight-card" aria-live="polite"><h2>Insights · pending</h2><p>Numeric assessment is available independently of explanations.</p></section></section><section class="encounter-visualization" aria-label="Interactive encounter schematic"></section></div>`;
  const title=host.querySelector<HTMLElement>('h1')!;title.textContent=row.event_id;title.focus();
  host.querySelector('.back-dashboard')!.addEventListener('click',onBack);
  host.querySelector('.encounter-source')!.textContent=`${analysis.source.label}${localFixture?' · explicit local fixture':''}`;
  const badge=host.querySelector<HTMLElement>('.page-risk')!;badge.textContent=row.severity;badge.dataset.risk=row.severity;
  host.querySelector('.planning-decision')!.textContent=maneuverReview(row.severity);
  host.querySelector('.encounter-lead')!.textContent=remainingTime(row.time_to_tca_hours);
  host.querySelector('.lead-basis')!.textContent=analysis.time_basis==='per_event_latest_report'?'As of this encounter’s latest source report. Not report age.':'Relative to the labeled synthetic scenario clock. Not report age.';
  const pair=host.querySelector('.prediction-pair')!;
  for(const [label,value]of [['Predicted Pc',probability(row.predicted_pc)],['Predicted miss distance',measure(row.miss_distance_m,'m')]]){const group=text('div','');group.append(text('span',label),text('strong',value));pair.append(group);}
  host.querySelector('.model-identity')!.textContent=`Prediction ${row.prediction_status} · model ${analysis.model.status} / ${analysis.model.version??'version not provided'}`;
  host.querySelector<HTMLElement>('.outside-page-filter')!.hidden=!outside;
  function facts(container:Element,pairs:string[][]){const dl=document.createElement('dl');for(const [label,value]of pairs)dl.append(text('dt',label),text('dd',value));container.append(dl);}
  facts(host.querySelector('.report-summary')!,[['Reported Pc',probability(row.reported_pc)],['Disposition / resolution','Not provided'],['Report age','Unavailable · report timestamp not provided'],['Latest report identifier',row.latest_report_id],['Report source','Not provided at report level'],['Report timestamp','Not provided']]);
  const technical=host.querySelector('.report-details')!;
  facts(technical,[['Report count',String(row.report_count)],['Report identities',row.report_ids.join(', ')],['Analysis source',analysis.source.label],['Analysis checksum',analysis.source.sha256??'Unavailable'],['Analysis ID',analysis.analysis_id],['Mission ID',row.mission_id??'Not provided'],['Predicted log10 Pc',row.predicted_log10_pc===null?'Unavailable':String(row.predicted_log10_pc)],['Relative speed',measure(row.relative_speed_mps,'m/s')],['Prediction target',analysis.model.target],['Feature schema',analysis.model.feature_schema_version??'Not provided']]);
  technical.append(text('h3','Authoritative server rule reasons'));
  for(const reason of row.flag_reasons)technical.append(text('p',`${reason.rule_id} · ${reason.field}${reason.operator?` ${reason.operator}`:''}${reason.value!==undefined?` value ${reason.value}`:''}${reason.threshold!==undefined?` threshold ${reason.threshold}`:''}${reason.unit?` ${reason.unit}`:''}`));
  if(row.geometry){facts(technical,[['Geometry frame','RTN · supplied source summary, not propagated'],['Position',row.geometry.position_m?`R ${row.geometry.position_m.r}, T ${row.geometry.position_m.t}, N ${row.geometry.position_m.n} m`:'Unavailable'],['Velocity',row.geometry.velocity_mps?`R ${row.geometry.velocity_mps.r}, T ${row.geometry.velocity_mps.t}, N ${row.geometry.velocity_mps.n} m/s`:'Unavailable']]);}else technical.append(text('p','RTN source geometry unavailable.'));
  for(const warning of [...analysis.warnings,...row.warnings])technical.append(text('p',warning));
  const playback=mountPlayback(host.querySelector<HTMLElement>('.encounter-visualization')!,row.miss_distance_m);
  const insight=host.querySelector('.insight-card')!,controller=new AbortController();let active=true,timedOut=false;const timeout=window.setTimeout(()=>{timedOut=true;controller.abort()},25000);
  const operation=localFixture?Promise.resolve(parseInsights({...fixture,items:fixture.items.filter(i=>i.event_id===row.event_id)},analysis,[row.event_id])):loadInsights(analysis,[row.event_id],controller.signal);
  operation.then(result=>{
    clearTimeout(timeout);if(!active||controller.signal.aborted||result.analysis_id!==analysis.analysis_id)return;
    insight.replaceChildren(text('h2',`Insights · ${result.status}`));const item=result.items.find(i=>i.event_id===row.event_id);
    if(item){insight.append(text('p',item.summary));for(const limitation of item.limitations)insight.append(text('p',limitation));insight.append(text('p',`Grounded fields: ${item.fact_refs.map(ref=>ref.field).join(', ')}`));}else insight.append(text('p','No explanation is available for this encounter.'));
    for(const warning of result.warnings)insight.append(text('p',warning));
  }).catch(error=>{clearTimeout(timeout);if(!active||(controller.signal.aborted&&!timedOut))return;insight.replaceChildren(text('h2','Insights · unavailable'),text('p',timedOut?'Explanation request timed out. Numeric analysis remains available.':(error as Error).message));});
  return {dispose(){active=false;clearTimeout(timeout);controller.abort();playback.dispose();host.replaceChildren();}};
}
