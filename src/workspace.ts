import {encountersForDays} from './demo-data';
import {createSatellite} from './satellite';
import {mountEncounterPage} from './encounter-page';
import {dashboardRows,eventRoute,type SortOrder} from '../web/client/encounter-model.ts';
import {loadDemo,uploadAnalysis} from '../web/client/api.ts';
import {ApiError,parseAnalysis,type AnalysisResult,type Encounter} from '../web/client/contract.ts';
import {filteredEncounters,globalCritical,outsideFilter,probability} from '../web/client/state.ts';
import analysisFixture from '../contracts/fixtures/analysis-demo.json';

const element=<K extends keyof HTMLElementTagNameMap>(tag:K,text?:string,className?:string)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e};
export function setupWorkspace(onLayout:()=>void,closeGlobeHelp:()=>void){
 const main=document.querySelector('main')!,stage=document.querySelector<HTMLElement>('.earth-stage')!,motion=matchMedia('(prefers-reduced-motion: reduce)');
 const fragment=document.createElement('div');
 fragment.innerHTML=`<div class="import-position"><button id="load-demo">Load Demo</button><div class="magnetic-hit"><button id="import-toggle" aria-expanded="false" aria-controls="import-dropdown">Import</button></div><div id="import-dropdown" hidden><button id="choose-file" class="spotlight-surface"><span>Choose a CSV file</span><span class="import-description">Send to analysis API</span></button><button id="choose-preview" class="preview-choice">UI preview only · any local file</button></div></div><input id="file-input" type="file" hidden><div id="workspace-loading" role="status" hidden><strong>Preparing workspace</strong><span></span></div><section id="workspace-error" role="alert" hidden><h2>Analysis unavailable</h2><p></p><ul></ul><div><button id="dismiss-api-error">Close</button><button id="local-fixture">Open local synthetic fixture</button></div></section><section class="encounter-panel" aria-labelledby="encounter-heading" hidden><div class="panel-heading"><div><h2 id="encounter-heading" tabindex="-1">Encounter overview</h2><p class="demo-label"></p></div><label class="time-filter">Time frame<select id="time-frame">${Array.from({length:7},(_,i)=>`<option value="${i+1}"${i===6?' selected':''}>${i+1} ${i===0?'day':'days'}</option>`).join('')}</select></label></div><div class="risk-summary" aria-label="Risk summary"></div><p class="workspace-file">Selected file: <span id="filename">None · Load Demo or import CSV</span></p><p id="analysis-meta"></p><details id="analysis-warnings"><summary>Source, model and warnings</summary><div></div></details><section id="critical-banner" aria-label="Global critical alert" hidden></section><label class="critical-filter"><input type="checkbox" id="critical-only"> Critical within 24h</label><div class="table-tools"><label>Search event<input id="event-search" type="search" placeholder="Event identifier"></label><label>Risk<select id="risk-filter"><option value="all">All risks</option><option value="critical">Critical</option><option value="elevated">Elevated</option><option value="safe">Safe</option><option value="unknown">Unknown</option></select></label><label>Sort<select id="event-sort"><option value="priority">Risk priority</option><option value="horizon">Closest first</option><option value="pc">Highest Pc</option><option value="distance">Smallest miss</option><option value="event">Event ID</option></select></label></div><div class="encounter-scroll" tabindex="0" role="region" aria-label="Encounter results, scroll for more rows"><table><thead></thead><tbody id="encounter-rows"></tbody></table><p id="no-encounters" hidden></p></div><p class="table-summary" aria-live="polite"></p><section id="relative-timeline" aria-label="Relative encounter timeline" hidden><h3>Relative horizon</h3><p id="timeline-basis"></p><div class="timeline-events"></div></section></section>`;
 main.append(...Array.from(fragment.childNodes));
 const $=<T extends HTMLElement=HTMLElement>(selector:string)=>document.querySelector<T>(selector)!;
 const toggle=$<HTMLButtonElement>('#import-toggle'),dropdown=$('#import-dropdown'),choose=$<HTMLButtonElement>('#choose-file'),previewChoice=$<HTMLButtonElement>('#choose-preview'),demoButton=$<HTMLButtonElement>('#load-demo'),input=$<HTMLInputElement>('#file-input'),loading=$('#workspace-loading'),panel=$('.encounter-panel'),select=$<HTMLSelectElement>('#time-frame'),criticalOnly=$<HTMLInputElement>('#critical-only'),errorPanel=$('#workspace-error');
 const search=$<HTMLInputElement>('#event-search'),risk=$<HTMLSelectElement>('#risk-filter'),sort=$<HTMLSelectElement>('#event-sort');
 const missionHeader=element('header',undefined,'mission-header');missionHeader.innerHTML='<div><h1>Autonomous Coconuts</h1><p>Encounter console</p></div><span class="header-source"></span>';missionHeader.append($('.time-filter'));main.append(missionHeader);
 const satellite=createSatellite(stage,motion);
 let busy=false,pickerMode:'api'|'preview'='api',preview=false,explicitLocalFixture=false,analysis:AnalysisResult|null=null,selectedId:string|null=null,request:AbortController|undefined;
 function close(restore=false){dropdown.hidden=true;toggle.setAttribute('aria-expanded','false');if(restore)toggle.focus()}
 toggle.addEventListener('click',()=>{if(busy)return;const open=dropdown.hidden;dropdown.hidden=!open;toggle.setAttribute('aria-expanded',String(open))});
 function pick(mode:'api'|'preview'){if(busy)return;pickerMode=mode;input.value='';input.accept=mode==='api'?'.csv,text/csv':'';input.click()}
 choose.addEventListener('click',()=>pick('api'));previewChoice.addEventListener('click',()=>pick('preview'));
 document.addEventListener('pointerdown',event=>{if(!(event.target as Element).closest('.import-position'))close()});
 document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!dropdown.hidden){event.preventDefault();close(true)}});
 const hit=$('.magnetic-hit');hit.addEventListener('pointermove',event=>{if(motion.matches||busy||event.pointerType==='touch')return;const r=hit.getBoundingClientRect();toggle.style.transform=`translate(${(event.clientX-r.left-r.width/2)*.25}px,${(event.clientY-r.top-r.height/2)*.25}px)`});hit.addEventListener('pointerleave',()=>{toggle.style.transform=''});
 choose.addEventListener('pointermove',event=>{if(motion.matches)return;const r=choose.getBoundingClientRect();choose.style.setProperty('--spot-x',`${event.clientX-r.left}px`);choose.style.setProperty('--spot-y',`${event.clientY-r.top}px`)});
 const schematic=element('section',undefined,'schematic-selection');schematic.setAttribute('aria-label','Schematic encounter selection');schematic.hidden=true;stage.append(schematic);
 function setBusy(value:boolean,message='Analyzing CSV through API…'){
  busy=value;for(const button of [toggle,choose,previewChoice,demoButton])button.disabled=value;toggle.style.transform='';loading.hidden=!value;
  if(value){close();closeGlobeHelp();loading.querySelector('strong')!.textContent=message;loading.querySelector('span')!.textContent=pickerMode==='preview'?'UI preview only · filename used; contents not read':'Waiting for backend response · no fixture substitution';satellite.start()}else satellite.stop();
 }
 function cancelInsights(){page?.dispose();page=undefined;}
 function showError(error:unknown){errorPanel.hidden=false;const value=error instanceof ApiError?error:new ApiError('INVALID_RESPONSE',(error as Error).message||'The request failed.');errorPanel.querySelector('p')!.textContent=`${value.code}: ${value.message}`;const list=errorPanel.querySelector('ul')!;list.replaceChildren();for(const d of value.details)list.append(element('li',`${d.row===null?'File':`Row ${d.row}`} · ${d.column??'general'}: ${d.reason}`));if(value.total!==null)list.prepend(element('li',`${value.total} total validation errors; showing ${value.details.length}.`));else if(value.details.length)list.prepend(element('li',`${value.details.length} validation details returned; no total supplied.`))}
 $('#dismiss-api-error').addEventListener('click',()=>{errorPanel.hidden=true;demoButton.focus()});
 function showDashboard(){panel.hidden=false;main.classList.add('dashboard');onLayout();$('#encounter-heading').focus()}
 function applyAnalysis(value:AnalysisResult,local=false){cancelInsights();analysis=value;preview=false;explicitLocalFixture=local;errorPanel.hidden=true;selectedId=null;select.value='7';criticalOnly.checked=false;persistAnalysis();showDashboard();render();syncRoute()}
 async function runAnalysis(action:()=>Promise<AnalysisResult>,message:string,filename:string){if(busy)return;request?.abort();request=new AbortController();cancelInsights();pickerMode='api';setBusy(true,message);errorPanel.hidden=true;let timedOut=false;const timeout=window.setTimeout(()=>{timedOut=true;request?.abort()},45000);try{applyAnalysis(await action());$('#filename').textContent=filename}catch(error){if(timedOut)showError(new ApiError('REQUEST_TIMEOUT','The analysis request timed out after 45 seconds. Previous results were preserved. Retry Load Demo or Import.'));else if((error as Error).name!=='AbortError')showError(error)}finally{clearTimeout(timeout);setBusy(false)}}
 demoButton.addEventListener('click',()=>{void runAnalysis(()=>loadDemo(request?.signal),'Loading synthetic demo from API…','API synthetic demo')});
 $('#local-fixture').addEventListener('click',()=>{applyAnalysis(parseAnalysis(analysisFixture),true);$('#filename').textContent='Canonical local fixture · explicitly selected'});
 input.addEventListener('change',()=>{const file=input.files?.[0];if(!file||busy)return;if(pickerMode==='api'){void runAnalysis(()=>uploadAnalysis(file,request?.signal),'Analyzing CSV through API…',file.name);return}
  $('#filename').textContent=file.name;
  errorPanel.hidden=true;
  cancelInsights();setBusy(true,'Preparing workspace');main.classList.add('preparing');panel.hidden=true;schematic.hidden=true;main.classList.remove('dashboard');onLayout();
  // Explicit filename-only UI preview. This timer does not represent parsing or API work.
  window.setTimeout(()=>{preview=true;analysis=null;selectedId=null;explicitLocalFixture=false;main.classList.remove('preparing');showDashboard();render();setBusy(false)},1000);
 });
 function currentRows(){return analysis?dashboardRows(filteredEncounters(analysis,Number(select.value),criticalOnly.checked),search.value,risk.value,sort.value as SortOrder):[]}
 function selectionButton(row:Encounter,label=row.event_id){const button=element('button',label,'event-select');button.type='button';button.dataset.eventId=row.event_id;button.setAttribute('aria-pressed',String(selectedId===row.event_id));button.addEventListener('click',()=>{selectEncounter(row.event_id)});return button}
 function render(){
  const body=$('#encounter-rows'),head=$('thead');body.replaceChildren();head.replaceChildren();const header=element('tr');for(const title of preview?['Object','Encounter time UTC','Miss distance km','Status']:['Event','Lead time h','Predicted Pc','Miss m','Status'])header.append(element('th',title));for(const th of Array.from(header.children))th.setAttribute('scope','col');head.append(header);
  $('.header-source').textContent=preview?'UI preview only':`${analysis!.source.mode} · ${analysis!.model.status}`;
  $('.demo-label').textContent=preview?'UI preview only · not processed or file-derived':`${analysis!.source.label}${explicitLocalFixture?' · local fixture':''}`;
  $('#analysis-meta').textContent=preview?'35 canned UI rows · not an AnalysisResult':`${analysis!.source.mode} · model ${analysis!.model.status}${analysis!.model.version?` (${analysis!.model.version})`:''} · ${analysis!.source.report_count} source reports`;
  $('.risk-summary').hidden=preview;$('.table-tools').hidden=preview;$('#analysis-warnings').hidden=preview;criticalOnly.parentElement!.hidden=preview;$('#relative-timeline').hidden=preview;schematic.hidden=preview;
  $('#critical-banner').hidden=true;
  if(preview){for(const row of encountersForDays(Number(select.value))){const tr=element('tr',undefined,`severity-${row.severity.toLowerCase()}`);for(const value of [row.object,row.time,row.distance])tr.append(element('td',value));const status=element('td');status.append(element('span',row.severity,'severity-tag'));tr.append(status);body.append(tr)}$('.table-summary').textContent=`${body.children.length} demo encounters · January 1–${select.value}, 2030 UTC`;$('#no-encounters').hidden=true;return}
  const value=analysis!,warnings=$('#analysis-warnings div');warnings.replaceChildren();for(const text of [`Analysis ${value.analysis_id}`,`Target: ${value.model.target}`,`Feature schema: ${value.model.feature_schema_version??'Unavailable'}`,`Time basis: ${value.time_basis}${value.scenario_clock_utc?` · synthetic clock ${value.scenario_clock_utc}`:''}`,`Source checksum: ${value.source.sha256??'Unavailable'}`,...value.warnings])warnings.append(element('p',text));
  const critical=globalCritical(value);if(critical){const banner=$('#critical-banner');banner.hidden=false;banner.replaceChildren(element('strong',`Critical encounter in ${critical.time_to_tca_hours}h`),element('p','Global alert · all horizons · not limited by list filters'),selectionButton(critical,'View encounter'))}
  const summary=$('.risk-summary');summary.replaceChildren();for(const [label,count]of [['Total encounters',value.encounters.length],['Critical',value.encounters.filter(e=>e.severity==='critical').length],['Elevated',value.encounters.filter(e=>e.severity==='elevated').length],['Within horizon',filteredEncounters(value,Number(select.value),false).length]]){const card=element('div');card.append(element('span',String(label)),element('strong',String(count)));summary.append(card);}
  const rows=currentRows();for(const row of rows){const tr=element('tr',undefined,`severity-${row.severity}`);tr.dataset.eventId=row.event_id;const first=element('td');first.append(selectionButton(row));tr.append(first,element('td',row.time_to_tca_hours.toLocaleString()),element('td',probability(row.predicted_pc)),element('td',row.miss_distance_m===null?'Unavailable':row.miss_distance_m.toLocaleString()));const status=element('td');status.append(element('span',row.severity,'severity-tag'));tr.append(status);body.append(tr)}
  $('#no-encounters').hidden=rows.length>0;$('#no-encounters').textContent=criticalOnly.checked&&filteredEncounters(value,Number(select.value),true).length===0?'No critical encounters within 24 hours':search.value.trim()||risk.value!=='all'?'No encounters match the current search and risk filters.':'No encounters in this time frame.';
  $('.table-summary').textContent=`${rows.length} of ${value.encounters.length} encounters · ${value.time_basis==='per_event_latest_report'?'hours as of each event’s latest report':'hours from synthetic scenario clock'}`;
  $('#timeline-basis').textContent=value.time_basis==='per_event_latest_report'?'Hours remaining as of each encounter’s latest report; not a shared calendar.':'Hours remaining from the labeled synthetic scenario clock.';
  const timeline=$('.timeline-events');timeline.replaceChildren();const max=Math.max(24,...value.encounters.map(e=>e.time_to_tca_hours));for(const row of value.encounters){const button=selectionButton(row,`${row.event_id} · ${row.time_to_tca_hours}h`);button.style.setProperty('--horizon',`${row.time_to_tca_hours/max*100}%`);timeline.append(button)}
  schematic.replaceChildren(element('p','Schematic selection aid · no global coordinates'));for(const row of value.encounters.slice(0,10))schematic.append(selectionButton(row));if(value.encounters.length>10)schematic.append(element('p','First 10 selection links; all encounters remain in the list and timeline.'));

 }
 select.addEventListener('change',render);criticalOnly.addEventListener('change',render);search.addEventListener('input',render);risk.addEventListener('change',render);sort.addEventListener('change',render);
 const routeHost=element('section',undefined,'encounter-page');routeHost.hidden=true;main.append(routeHost);
 let page:ReturnType<typeof mountEncounterPage>|undefined;
 let dashboardScroll=0;
 function persistAnalysis(){try{if(analysis)sessionStorage.setItem('coconuts-normalized-analysis-v1',JSON.stringify({analysis,localFixture:explicitLocalFixture}));}catch{/* Quota/private browsing: route still works until refresh. */}}
 function selectEncounter(id:string){
  if(!analysis||!analysis.encounters.some(row=>row.event_id===id))return;
  selectedId=id;dashboardScroll=$('.encounter-scroll').scrollTop;
  history.pushState({coconuts:true},'',`/encounters/${encodeURIComponent(id)}`);syncRoute();
 }
 function backDashboard(){history.pushState({coconuts:true},'','/');syncRoute();}
 function syncRoute(){
  page?.dispose();page=undefined;cancelInsights();
  const id=eventRoute(location.pathname);
  if(id===null&&location.pathname.startsWith('/encounters/')){panel.hidden=true;routeHost.hidden=false;main.classList.add('encounter-route');routeHost.replaceChildren(element('h1','Invalid encounter link'));const back=element('button','Back to Dashboard');back.addEventListener('click',backDashboard);routeHost.append(back);return;}
  if(id===null){routeHost.hidden=true;main.classList.remove('encounter-route');if(analysis||preview){showDashboard();render();$('.encounter-scroll').scrollTop=dashboardScroll;}onLayout();return;}
  panel.hidden=true;routeHost.hidden=false;main.classList.add('encounter-route');
  const row=analysis?.encounters.find(value=>value.event_id===id);
  if(!analysis||!row){routeHost.replaceChildren(element('h1',analysis?'Encounter not found':'Encounter context unavailable'),element('p',analysis?'This event ID is not present in the retained analysis.':'Load the originating analysis or demo. No event data was fabricated for this deep link.'));const back=element('button','Back to Dashboard');back.addEventListener('click',backDashboard);routeHost.append(back);}
  else {selectedId=id;page=mountEncounterPage(routeHost,analysis,row,explicitLocalFixture,backDashboard,outsideFilter(id,currentRows()));}
  onLayout();
 }
 window.addEventListener('popstate',syncRoute);
 try{const saved=sessionStorage.getItem('coconuts-normalized-analysis-v1');if(saved){const data=JSON.parse(saved);analysis=parseAnalysis(data.analysis);explicitLocalFixture=data.localFixture===true&&analysis.analysis_id===analysisFixture.analysis_id;$('#filename').textContent=`Retained analysis: ${analysis.source.label}`;if(analysis)showDashboard();render();}}catch{try{sessionStorage.removeItem('coconuts-normalized-analysis-v1');}catch{/* Storage unavailable. */}}
 syncRoute();
 motion.addEventListener('change',()=>{toggle.style.transform=''});window.addEventListener('pagehide',event=>{if(!event.persisted){satellite.dispose();page?.dispose();request?.abort();cancelInsights()}});
}
