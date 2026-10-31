import {encountersForDays} from './demo-data';
import {createSatellite} from './satellite';
import {mountEncounterPage} from './encounter-page';
import {dashboardRows,eventRoute,horizonStops,discreteHorizon,sliderSample,type SortOrder} from '../web/client/encounter-model.ts';
import {loadDemo,uploadAnalysis} from '../web/client/api.ts';
import {ApiError,parseAnalysis,type AnalysisResult,type Encounter} from '../web/client/contract.ts';
import {filteredEncounters,globalCritical,outsideFilter,probability,OperationGuard} from '../web/client/state.ts';
import analysisFixture from '../contracts/fixtures/analysis-demo.json';

const element=<K extends keyof HTMLElementTagNameMap>(tag:K,text?:string,className?:string)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e};
export function setupWorkspace(onLayout:()=>void,closeGlobeHelp:()=>void){
 const main=document.querySelector('main')!,stage=document.querySelector<HTMLElement>('.earth-stage')!,motion=matchMedia('(prefers-reduced-motion: reduce)');
 const fragment=document.createElement('div');
 fragment.innerHTML=`<div class="import-position"><button id="load-demo">Load Demo</button><div class="magnetic-hit"><button id="import-toggle" aria-expanded="false" aria-controls="import-dropdown">Import</button></div><div id="import-dropdown" role="dialog" aria-label="Import conjunction data" hidden><button id="close-import" aria-label="Close import panel">×</button><button id="choose-file" class="spotlight-surface"><span>Import CSV file</span><span class="import-description">Click anywhere to select a file</span></button><button id="choose-preview" class="preview-choice">UI preview only · any local file</button></div></div><input id="file-input" type="file" hidden><div id="workspace-loading" role="status" hidden><strong>Preparing workspace</strong><span></span></div><section id="workspace-error" role="alert" hidden><h2>Analysis unavailable</h2><p></p><ul></ul><div><button id="dismiss-api-error">Close</button><button id="local-fixture">Open local synthetic fixture</button></div></section><section class="encounter-panel" aria-labelledby="encounter-heading" hidden><div class="panel-heading"><div><h2 id="encounter-heading" tabindex="-1">Encounter overview</h2></div><div class="time-filter"><span id="horizon-label">Time frame</span><div id="time-frame" class="rubber-slider horizon-slider" role="slider" tabindex="0" aria-labelledby="horizon-label" aria-valuemin="0" aria-valuemax="3" aria-valuenow="2" aria-valuetext="7 days"><div class="slider-track"><div class="slider-progress"></div><span class="slider-thumb"></span></div></div><div class="horizon-stops"><span>24 h</span><span>3 d</span><span>7 d</span><span>All</span></div></div></div><div class="risk-summary" aria-label="Risk summary"></div><span id="filename" hidden></span><span id="analysis-meta" hidden></span><details id="analysis-warnings"><summary>Data details</summary><div></div></details><section id="critical-banner" aria-label="Global critical alert" hidden></section><label class="critical-filter"><input type="checkbox" id="critical-only"> Critical within 24h</label><div class="table-tools"><label>Search event<input id="event-search" type="search" placeholder="Event identifier"></label><label>Risk<select id="risk-filter"><option value="all">All risks</option><option value="critical">Critical</option><option value="elevated">Elevated</option><option value="safe">Safe</option><option value="unknown">Unknown</option></select></label><label>Sort<select id="event-sort"><option value="priority">Risk priority</option><option value="horizon">Closest first</option><option value="pc">Highest Pc</option><option value="distance">Smallest miss</option><option value="event">Event ID</option></select></label></div><div class="encounter-scroll" tabindex="0" role="region" aria-label="Encounter results, scroll for more rows"><table><thead></thead><tbody id="encounter-rows"></tbody></table><p id="no-encounters" hidden></p></div><p class="table-summary" aria-live="polite"></p></section>`;
 main.append(...Array.from(fragment.childNodes));
 const $=<T extends HTMLElement=HTMLElement>(selector:string)=>document.querySelector<T>(selector)!;
 const toggle=$<HTMLButtonElement>('#import-toggle'),dropdown=$('#import-dropdown'),choose=$<HTMLButtonElement>('#choose-file'),previewChoice=$<HTMLButtonElement>('#choose-preview'),demoButton=$<HTMLButtonElement>('#load-demo'),input=$<HTMLInputElement>('#file-input'),loading=$('#workspace-loading'),panel=$('.encounter-panel'),select=$('#time-frame'),criticalOnly=$<HTMLInputElement>('#critical-only'),errorPanel=$('#workspace-error');
 const search=$<HTMLInputElement>('#event-search'),risk=$<HTMLSelectElement>('#risk-filter'),sort=$<HTMLSelectElement>('#event-sort');
 const missionHeader=element('header',undefined,'mission-header');missionHeader.innerHTML='<div><h1><img class="brand-logo" src="/brand/coconut-autonomous.jpeg" alt="Coconut Autonomous" width="1983" height="793"></h1><p>Encounter console</p></div><span class="header-source"></span>';missionHeader.append($('.time-filter'));main.append(missionHeader);
 const landing=element('section',undefined,'landing-page');landing.innerHTML='<h1><img class="brand-logo" src="/brand/coconut-autonomous.jpeg" alt="Coconut Autonomous" width="1983" height="793"></h1><h2>Satellite Collision Risk, Made Clear</h2><p>Spot risky close approaches, understand the danger, and explore each encounter in 3D.</p><div class="landing-actions"><button class="launch-dashboard">Launch Dashboard</button><button class="landing-import">Import Conjunction Data</button><button class="landing-demo">Load Demo</button></div>';main.append(landing);
 landing.querySelector('.launch-dashboard')!.addEventListener('click',()=>navigateDashboard());landing.querySelector('.landing-import')!.addEventListener('click',()=>openImport(landingImport));landing.querySelector('.landing-demo')!.addEventListener('click',()=>{errorFocus=landing.querySelector<HTMLElement>('.landing-demo');demoButton.click();});
 const landingImport=landing.querySelector<HTMLButtonElement>('.landing-import')!;landingImport.setAttribute('aria-controls','import-dropdown');landingImport.setAttribute('aria-expanded','false');
 main.append(dropdown);const importError=element('section',undefined,'import-error');importError.hidden=true;importError.setAttribute('role','alert');importError.innerHTML='<h3>Import unavailable</h3><p></p><ul></ul>';dropdown.append(importError);const importStatus=element('p','','import-description');importStatus.setAttribute('role','status');dropdown.append(importStatus);
 const satellite=createSatellite(stage,motion);
 let errorFocus:HTMLElement|null=null;
 let busy=false,pickerMode:'api'|'preview'='api',preview=false,explicitLocalFixture=false,analysis:AnalysisResult|null=null,selectedId:string|null=null,request:AbortController|undefined;
 let importInvoker:HTMLElement=toggle,importOperation=false,closeTimer=0;const operations=new OperationGuard();
 function positionImport(){const r=importInvoker.getBoundingClientRect();const width=Math.min(280,innerWidth-32);dropdown.style.width=`${width}px`;dropdown.style.left=`${Math.max(16,Math.min(innerWidth-width-16,r.right-width))}px`;dropdown.style.top=`${Math.max(16,Math.min(innerHeight-dropdown.offsetHeight-16,r.bottom+12))}px`;}
 function openImport(invoker:HTMLElement){if(busy)return;clearTimeout(closeTimer);importInvoker=invoker;dropdown.hidden=false;dropdown.classList.remove('closing');dropdown.inert=false;positionImport();for(const button of [toggle,landingImport])button.setAttribute('aria-expanded',String(button===invoker));choose.focus({preventScroll:true});}
 function close(restore=false,cancel=true){if(cancel&&busy&&importOperation){operations.cancel();request?.abort();setBusy(false);importOperation=false;}if(dropdown.hidden)return;for(const button of [toggle,landingImport])button.setAttribute('aria-expanded','false');dropdown.classList.add('closing');dropdown.inert=true;if(restore)importInvoker.focus({preventScroll:true});closeTimer=window.setTimeout(()=>{dropdown.hidden=true;dropdown.classList.remove('closing')},motion.matches?0:150);}
 toggle.addEventListener('click',()=>{if(dropdown.hidden||dropdown.classList.contains('closing'))openImport(toggle);else close(true)});
 $('#close-import').addEventListener('click',()=>close(true));window.addEventListener('resize',()=>{if(!dropdown.hidden)positionImport()});
 function pick(mode:'api'|'preview'){if(busy)return;errorFocus=document.activeElement instanceof HTMLElement?document.activeElement:null;pickerMode=mode;input.value='';input.accept=mode==='api'?'.csv,text/csv':'';input.click()}
 choose.addEventListener('click',()=>pick('api'));previewChoice.addEventListener('click',()=>pick('preview'));
 document.addEventListener('pointerdown',event=>{if(!dropdown.contains(event.target as Node)&&!importInvoker.contains(event.target as Node))close()});
 document.addEventListener('keydown',event=>{if(dropdown.hidden)return;if(event.key==='Escape'){event.preventDefault();close(true)}});
 // The wrapper never moves: pointer offsets remain stable while the button translates.
 function magnetic(button:HTMLButtonElement){
  let hit=button.parentElement!;
  if(!hit.classList.contains('magnetic-hit')){hit=element('span',undefined,'magnetic-hit');button.before(hit);hit.append(button);}
  button.classList.add('magnet-btn');
  const reset=()=>{button.style.transform=''};
  hit.addEventListener('pointermove',event=>{if(motion.matches||button.disabled||event.pointerType!=='mouse'){reset();return;}const r=hit.getBoundingClientRect();button.style.transform=`translate(${(event.clientX-r.left-r.width/2)*.35}px,${(event.clientY-r.top-r.height/2)*.35}px)`});
  hit.addEventListener('pointerleave',reset);button.addEventListener('blur',reset);motion.addEventListener('change',reset);
 }
 [toggle,...Array.from(landing.querySelectorAll<HTMLButtonElement>('button'))].forEach(magnetic);
 choose.addEventListener('pointermove',event=>{if(motion.matches)return;const r=choose.getBoundingClientRect();choose.style.setProperty('--spot-x',`${event.clientX-r.left}px`);choose.style.setProperty('--spot-y',`${event.clientY-r.top}px`)});
 let horizonIndex=2;
 const horizonDays=()=>horizonStops[horizonIndex];
 function setHorizon(index:number){horizonIndex=Math.min(3,Math.max(0,index));select.setAttribute('aria-valuenow',String(horizonIndex));select.setAttribute('aria-valuetext',['24 hours','3 days','7 days','All encounters'][horizonIndex]);select.querySelector<HTMLElement>('.slider-thumb')!.style.left=select.querySelector<HTMLElement>('.slider-progress')!.style.width=`${horizonIndex/3*100}%`;if(analysis||preview)render();}
 function seekHorizon(event:PointerEvent){const box=select.getBoundingClientRect(),raw=(event.clientX-box.left)/box.width;setHorizon(discreteHorizon(raw));select.querySelector<HTMLElement>('.slider-thumb')!.style.transform=`translateX(calc(-50% + ${sliderSample(raw,motion.matches).visualOffset*box.width/100}px))`;}
 select.addEventListener('pointerdown',event=>{select.focus();select.setPointerCapture(event.pointerId);seekHorizon(event)});select.addEventListener('pointermove',event=>{if(select.hasPointerCapture(event.pointerId))seekHorizon(event)});
 function releaseHorizon(event:PointerEvent){if(select.hasPointerCapture(event.pointerId))select.releasePointerCapture(event.pointerId);select.querySelector<HTMLElement>('.slider-thumb')!.style.transform='translateX(-50%)';}
 select.addEventListener('pointerup',releaseHorizon);select.addEventListener('pointercancel',releaseHorizon);select.addEventListener('lostpointercapture',()=>{select.querySelector<HTMLElement>('.slider-thumb')!.style.transform='translateX(-50%)'});
 select.addEventListener('keydown',event=>{const values:Record<string,number>={ArrowRight:horizonIndex+1,ArrowUp:horizonIndex+1,ArrowLeft:horizonIndex-1,ArrowDown:horizonIndex-1,Home:0,End:3};if(event.key in values){event.preventDefault();setHorizon(values[event.key]);}});
 setHorizon(2);
 function setBusy(value:boolean,message='Analyzing CSV through API…'){
  busy=value;dropdown.setAttribute('aria-busy',String(value&&importOperation));importStatus.textContent=value&&importOperation?'Analyzing selected CSV…':'';for(const button of [toggle,choose,previewChoice,demoButton,...Array.from(landing.querySelectorAll<HTMLButtonElement>('button'))])button.disabled=value;landing.setAttribute('aria-busy',String(value));landing.querySelector<HTMLButtonElement>('.landing-demo')!.textContent=value?'Preparing…':'Load Demo';toggle.style.transform='';loading.hidden=!value;
  if(value){if(!importOperation)close();closeGlobeHelp();loading.querySelector('strong')!.textContent=message;loading.querySelector('span')!.textContent=pickerMode==='preview'?'UI preview only · filename used; contents not read':'Waiting for backend response · no fixture substitution';satellite.start()}else satellite.stop();
 }
 function cancelInsights(){page?.dispose();page=undefined;}
 function showError(error:unknown){const target=importOperation?importError:errorPanel;target.hidden=false;const value=error instanceof ApiError?error:new ApiError('INVALID_RESPONSE',(error as Error).message||'The request failed.');target.querySelector('p')!.textContent=`${value.code}: ${value.message}`;const list=target.querySelector('ul')!;list.replaceChildren();for(const d of value.details)list.append(element('li',`${d.row===null?'File':`Row ${d.row}`} · ${d.column??'general'}: ${d.reason}`));if(value.total!==null)list.prepend(element('li',`${value.total} total validation errors; showing ${value.details.length}.`));else if(value.details.length)list.prepend(element('li',`${value.details.length} validation details returned; no total supplied.`))}
 $('#dismiss-api-error').addEventListener('click',()=>{errorPanel.hidden=true;const target=location.pathname==='/'?(errorFocus?.closest('.landing-page')?errorFocus:landing.querySelector<HTMLButtonElement>('.launch-dashboard')):demoButton;target?.focus()});
 function showDashboard(){panel.hidden=false;main.classList.add('dashboard');onLayout();$('#encounter-heading').focus()}
 function applyAnalysis(value:AnalysisResult,local=false){close(false,false);importError.hidden=true;cancelInsights();analysis=value;preview=false;explicitLocalFixture=local;errorPanel.hidden=true;selectedId=null;horizonIndex=2;setHorizon(2);criticalOnly.checked=false;persistAnalysis();history.pushState({coconuts:true},'','/dashboard');showDashboard();render();syncRoute()}
 async function runAnalysis(action:(signal:AbortSignal)=>Promise<AnalysisResult>,message:string,filename:string,isImport=false){
  if(busy)return;const token=operations.begin();importOperation=isImport;importError.hidden=true;request?.abort();const localRequest=new AbortController();request=localRequest;
  if(!(errorFocus?.closest('.landing-page')&&location.pathname==='/'))errorFocus=document.activeElement instanceof HTMLElement?document.activeElement:null;
  pickerMode='api';setBusy(true,message);errorPanel.hidden=true;let timedOut=false;
  const timeout=window.setTimeout(()=>{timedOut=true;localRequest.abort()},45000);
  try{const result=await action(localRequest.signal);if(!operations.current(token)||localRequest.signal.aborted)return;applyAnalysis(result);$('#filename').textContent=filename}
  catch(error){if(!operations.current(token))return;if(timedOut)showError(new ApiError('REQUEST_TIMEOUT','The analysis request timed out after 45 seconds. Previous results were preserved. Retry Load Demo or Import.'));else if((error as Error).name!=='AbortError')showError(error)}
  finally{clearTimeout(timeout);if(operations.current(token)){setBusy(false);if(importOperation&&!importError.hidden)openImport(importInvoker);importOperation=false;}}
 }
 demoButton.addEventListener('click',()=>{void runAnalysis(signal=>loadDemo(signal),'Loading synthetic demo from API…','API synthetic demo')});
 $('#local-fixture').addEventListener('click',()=>{applyAnalysis(parseAnalysis(analysisFixture),true);$('#filename').textContent='Canonical local fixture · explicitly selected'});
 input.addEventListener('change',()=>{const file=input.files?.[0];if(!file||busy)return;if(pickerMode==='api'){void runAnalysis(signal=>uploadAnalysis(file,signal),'Analyzing CSV through API…',file.name,true);return}
  $('#filename').textContent=file.name;
  errorPanel.hidden=true;
  cancelInsights();setBusy(true,'Preparing workspace');main.classList.add('preparing');panel.hidden=true;main.classList.remove('dashboard');onLayout();
  // Explicit filename-only UI preview. This timer does not represent parsing or API work.
  window.setTimeout(()=>{preview=true;analysis=null;selectedId=null;explicitLocalFixture=false;main.classList.remove('preparing');history.pushState({coconuts:true},'','/dashboard');showDashboard();render();syncRoute();setBusy(false)},1000);
 });
 function currentRows(){return analysis?dashboardRows(filteredEncounters(analysis,horizonDays(),criticalOnly.checked),search.value,risk.value,sort.value as SortOrder):[]}
 function selectionButton(row:Encounter,label=row.event_id){const button=element('button',label,'event-select');button.type='button';button.dataset.eventId=row.event_id;button.setAttribute('aria-pressed',String(selectedId===row.event_id));button.addEventListener('click',()=>{selectEncounter(row.event_id)});return button}
 function render(){
  if(!analysis&&!preview)return;
  const body=$('#encounter-rows'),head=$('thead');body.replaceChildren();head.replaceChildren();const header=element('tr');for(const title of preview?['Object','Encounter time UTC','Miss distance km','Status']:['Event','Lead time h','Predicted Pc','Miss m','Status'])header.append(element('th',title));for(const th of Array.from(header.children))th.setAttribute('scope','col');head.append(header);
  $('.header-source').textContent=preview?'UI preview only':analysis!.source.mode==='synthetic_demo'?'Demo data':analysis!.model.status==='unavailable'?'Imported CSV · prediction unavailable':'Imported CSV';

  $('#analysis-meta').textContent=preview?'35 canned UI rows · not an AnalysisResult':`${analysis!.source.mode} · model ${analysis!.model.status}${analysis!.model.version?` (${analysis!.model.version})`:''} · ${analysis!.source.report_count} source reports`;
  $('.risk-summary').hidden=preview;$('.table-tools').hidden=preview;$('#analysis-warnings').hidden=preview;criticalOnly.parentElement!.hidden=preview;
  $('#critical-banner').hidden=true;
  if(preview){for(const row of encountersForDays(Math.min(7,horizonDays()))){const tr=element('tr',undefined,`severity-${row.severity.toLowerCase()}`);for(const value of [row.object,row.time,row.distance])tr.append(element('td',value));const status=element('td');status.append(element('span',row.severity,'severity-tag'));tr.append(status);body.append(tr)}$('.table-summary').textContent=`${body.children.length} demo encounters · January 1–${Math.min(7,horizonDays())}, 2030 UTC`;$('#no-encounters').hidden=true;return}
  const value=analysis!,warnings=$('#analysis-warnings div');warnings.replaceChildren();for(const text of [`Source: ${value.source.label}`,`Mode: ${value.source.mode} · model ${value.model.status}${value.model.version?` (${value.model.version})`:''}`,`Reports: ${value.source.report_count}`,`Analysis ${value.analysis_id}`,`Target: ${value.model.target}`,`Feature schema: ${value.model.feature_schema_version??'Unavailable'}`,`Time basis: ${value.time_basis}${value.scenario_clock_utc?` · synthetic clock ${value.scenario_clock_utc}`:''}`,`Source checksum: ${value.source.sha256??'Unavailable'}`,...value.warnings])warnings.append(element('p',text));
  const critical=globalCritical(value);if(critical){const banner=$('#critical-banner');banner.hidden=false;banner.innerHTML='<svg class="warning-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 3 2 21h20L12 3Z"/><path d="M12 9v5m0 3v1"/></svg>';banner.append(element('strong',`Critical encounter in ${critical.time_to_tca_hours}h`),element('p','Global alert · all horizons · not limited by list filters'),selectionButton(critical,'View encounter'))}
  const summary=$('.risk-summary');summary.replaceChildren();for(const [label,count]of [['Total encounters',value.encounters.length],['Critical',value.encounters.filter(e=>e.severity==='critical').length],['Elevated',value.encounters.filter(e=>e.severity==='elevated').length],['Within selected time frame',filteredEncounters(value,horizonDays(),false).length]]){const card=element('div',undefined,`kpi-${String(label).toLowerCase().split(' ')[0]}`);card.append(element('span',String(label)),element('strong',String(count)));summary.append(card);}
  const rows=currentRows();for(const row of rows){const tr=element('tr',undefined,`severity-${row.severity}`);tr.dataset.eventId=row.event_id;tr.setAttribute('aria-label',`Open encounter ${row.event_id}, ${row.severity}`);tr.addEventListener('click',event=>{if(!(event.target as Element).closest('button'))selectEncounter(row.event_id)});const first=element('td');first.append(selectionButton(row));tr.append(first,element('td',row.time_to_tca_hours.toLocaleString()),element('td',probability(row.predicted_pc)),element('td',row.miss_distance_m===null?'Unavailable':row.miss_distance_m.toLocaleString()));const status=element('td');status.append(element('span',row.severity,'severity-tag'));tr.append(status);body.append(tr)}
  $('#no-encounters').hidden=rows.length>0;$('#no-encounters').textContent=criticalOnly.checked&&filteredEncounters(value,horizonDays(),true).length===0?'No critical encounters within 24 hours':search.value.trim()||risk.value!=='all'?'No encounters match the current search and risk filters.':'No encounters in this time frame.';
  $('.table-summary').textContent=`${rows.length} of ${value.encounters.length} encounters · ${value.time_basis==='per_event_latest_report'?'hours as of each event’s latest report':'hours from synthetic scenario clock'}`;


 }
 criticalOnly.addEventListener('change',render);search.addEventListener('input',render);risk.addEventListener('change',render);sort.addEventListener('change',render);
 const routeHost=element('section',undefined,'encounter-page');routeHost.hidden=true;main.append(routeHost);
 let page:ReturnType<typeof mountEncounterPage>|undefined;
 let dashboardScroll=0;
 function persistAnalysis(){try{if(analysis)sessionStorage.setItem('coconuts-normalized-analysis-v1',JSON.stringify({analysis,localFixture:explicitLocalFixture}));}catch{/* Quota/private browsing: route still works until refresh. */}}
 function selectEncounter(id:string){
  if(!analysis||!analysis.encounters.some(row=>row.event_id===id))return;
  selectedId=id;dashboardScroll=$('.encounter-scroll').scrollTop;
  history.pushState({coconuts:true},'',`/encounters/${encodeURIComponent(id)}`);syncRoute();
 }
 function navigateDashboard(){history.pushState({coconuts:true},'','/dashboard');syncRoute();}function backDashboard(){navigateDashboard();}
 function syncRoute(){
  page?.dispose();page=undefined;cancelInsights();
  const id=eventRoute(location.pathname);
  const isLanding=location.pathname==='/';landing.hidden=!isLanding;main.classList.toggle('landing-route',isLanding);stage.hidden=location.pathname.startsWith('/encounters/');stage.inert=stage.hidden;
  main.classList.toggle('encounter-route',location.pathname.startsWith('/encounters/'));
  if(isLanding){panel.hidden=true;routeHost.hidden=true;main.classList.remove('dashboard');const heading=landing.querySelector<HTMLHeadingElement>('h1')!;heading.tabIndex=-1;heading.focus({preventScroll:true});onLayout();return;}
  if(id===null&&location.pathname.startsWith('/encounters/')){panel.hidden=true;routeHost.hidden=false;main.classList.add('encounter-route');routeHost.replaceChildren(element('h1','Invalid encounter link'));const back=element('button','Back to Dashboard');back.addEventListener('click',backDashboard);routeHost.append(back);return;}
  if(id===null){routeHost.hidden=true;main.classList.remove('encounter-route');showDashboard();if(analysis||preview){render();$('.encounter-scroll').scrollTop=dashboardScroll;}else{$('#no-encounters').hidden=false;$('#no-encounters').textContent='Load Demo or import conjunction data to begin.';$('.risk-summary').hidden=true;}onLayout();return;}
  panel.hidden=true;routeHost.hidden=false;main.classList.add('encounter-route');
  const row=analysis?.encounters.find(value=>value.event_id===id);
  if(!analysis||!row){routeHost.replaceChildren(element('h1',analysis?'Encounter not found':'Encounter context unavailable'),element('p',analysis?'This event ID is not present in the retained analysis.':'Load the originating analysis or demo. No event data was fabricated for this deep link.'));const back=element('button','Back to Dashboard');back.addEventListener('click',backDashboard);routeHost.append(back);}
  else {selectedId=id;page=mountEncounterPage(routeHost,analysis,row,explicitLocalFixture,backDashboard,outsideFilter(id,currentRows()));}
  onLayout();
 }
 window.addEventListener('popstate',()=>{close();syncRoute()});
 try{const saved=sessionStorage.getItem('coconuts-normalized-analysis-v1');if(saved){const data=JSON.parse(saved);analysis=parseAnalysis(data.analysis);explicitLocalFixture=data.localFixture===true&&analysis.analysis_id===analysisFixture.analysis_id;$('#filename').textContent=`Retained analysis: ${analysis.source.label}`;if(analysis)showDashboard();render();}}catch{try{sessionStorage.removeItem('coconuts-normalized-analysis-v1');}catch{/* Storage unavailable. */}}
 syncRoute();
 motion.addEventListener('change',()=>{toggle.style.transform=''});window.addEventListener('pagehide',event=>{if(!event.persisted){satellite.dispose();page?.dispose();request?.abort();cancelInsights()}});
}
