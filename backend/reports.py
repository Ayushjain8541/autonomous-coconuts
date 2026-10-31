"""Portfolio narratives and explicitly hypothetical rule-sensitivity comparisons."""
import copy
import math
import re
import threading
import time
import uuid
from collections import Counter, OrderedDict
from datetime import datetime, timezone
import ml
from .insights import ProviderError, AnthropicClient
from .config import load_settings
from .llm_context import CONTEXT_VERSION, NumericClaimError, OPERATIONS_BRIEF, build_analysis_context, event_evidence, geometry_availability, provider_context, _statement


def _object(properties):
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}


STATEMENT = _object({'text':{'type':'string'},'fact_ids':{'type':'array','items':{'type':'string'}}})
REPORT_OUTPUT_SCHEMA = _object({
    'executive_summary':STATEMENT,
    'key_findings':{'type':'array','items':STATEMENT},
    'encounters':{'type':'array','items':_object({'event_id':{'type':'string'},'assessment':STATEMENT,
        'actions':{'type':'array','items':_object({'action_id':{'type':'string'},'rationale':STATEMENT})}})},
    'what_if_summary':STATEMENT})
SYSTEM_PROMPT = OPERATIONS_BRIEF + """
Write a professional satellite operations report for the mission operations team. Lead with which encounters need review and why. Use the supplied reference_assessment, value_availability and exact classification comparisons as the baseline. A supplied example Pc is NOT a missing Pc. Preserve every supplied tier and comparison direction.
Keep the executive summary under 80 words: priorities and recommended review steps, with no numbers or event-by-event inventory; the tables carry the counts. Provide 2-3 short key findings. Explain every priority encounter once in supplied order, using one short assessment and at most two eligible review actions when sufficient. Action rationales explain the purpose of the review, not a new risk calculation.
For what_if_summary, copy the supplied what_if_reference text and fact_ids exactly. Its comparisons come directly from the classifier. Do not rewrite the scenario outcomes or multipliers; these are assumed inputs, not predicted maneuver benefits.
Cite each statement using exact fact_ids, in the array only. Each numeric claim must cite its source. Use the supplied display_value for hours when available; do not round other measurements arbitrarily. Cohort counts must cite portfolio.detailed_count. Refer to numeric identifiers as encounter <ID>. Do not compute additional counts or statistics or invent a new review window; only the supplied 24-hour window is configured. Only use eligible advisory action IDs.
Use estimated collision probability, predicted closest separation, and hours from the reference report/scenario clock. Avoid countdowns from today. Safe is not a clearance. For synthetic_demo, identify the report once as a demonstration using example values. Avoid developer words such as fixture, schema, validation, pipeline and fallback in the report prose. Return the required JSON structure only."""


class ReportError(ValueError):
    code, status, details = 'REPORT_NOT_FOUND', 404, []


def _default_report_client():
    settings=load_settings()
    return AnthropicClient(settings.api_key,settings.model,settings.report_timeout)


def _actions(event):
    result = []
    def add(code,label):result.append({'action_id':code,'label':label})
    if event['severity']=='critical':
        add('ESCALATE_REVIEW','Escalate to mission operations')
        add('REQUEST_FLIGHT_DYNAMICS','Ask flight dynamics to assess avoidance options')
    if event['prediction_status']=='unavailable':add('CHECK_PREDICTION','Obtain the missing risk estimate')
    if not all(geometry_availability(event).values()):add('CHECK_GEOMETRY','Request the missing encounter geometry')
    add('REFRESH_TRACKING','Refresh tracking before deciding')
    if event['severity'] in {'safe','elevated'}:add('MONITOR_UPDATES','Continue monitoring this encounter')
    return result


def build_context(analysis, classifier=ml.classify_encounter):
    events=analysis['encounters'];counts=Counter(e['severity'] for e in events)
    predictions=Counter(e['prediction_status'] for e in events)
    statistics={'total_encounters':len(events),'source_report_count':analysis['source']['report_count'],
        'severity_counts':{k:counts[k] for k in ['critical','elevated','safe','unknown']},
        'prediction_counts':{k:predictions[k] for k in ['ready','fixture','unavailable']},
        'critical_within_24h':sum(e['severity']=='critical' and e['time_to_tca_hours']<=24 for e in events)}
    rank={'critical':0,'elevated':1,'unknown':2,'safe':3}
    selected=sorted(events,key=lambda e:(rank[e['severity']],e['time_to_tca_hours'],e['event_id']))[:10]
    facts={}
    def fact(key,value,field,event_id=None,unit=None,supporting_numbers=None):
        facts[key]={'value':value,'field':field,'event_id':event_id,'unit':unit,'supporting_numbers':supporting_numbers or []}
        return key
    fact('portfolio.total',len(events),'total_encounters',unit='encounters')
    fact('portfolio.source_reports',statistics['source_report_count'],'source_report_count',unit='reports')
    fact('portfolio.detailed_count',len(selected),'detailed_encounters',unit='encounters')
    for tier,value in statistics['severity_counts'].items():fact('portfolio.'+tier,value,'severity_counts.'+tier,unit='encounters')
    fact('portfolio.predictions_unavailable',predictions['unavailable'],'prediction_counts.unavailable',unit='encounters')
    for status in ['ready','fixture']:fact('portfolio.predictions_'+status,predictions[status],'prediction_counts.'+status,unit='encounters')
    fact('portfolio.critical_within_24h',statistics['critical_within_24h'],'critical_within_24h',unit='encounters',supporting_numbers=[24])
    fact('portfolio.model_status',analysis['model']['status'],'model.status')
    fact('portfolio.time_basis',analysis['time_basis'],'time_basis')
    priority=[];scenarios=[]
    for i,event in enumerate(selected):
        evidence=event_evidence(event,'event.%s'%i,facts)
        priority.append(dict(evidence,allowed_actions=_actions(event)))
        pc,distance=event['predicted_pc'],event['miss_distance_m']
        for code,pc_scale,distance_scale in [('pc_lower',.1,1),('distance_larger',1,2),('combined',.1,2)]:
            available=(pc is not None if pc_scale!=1 else True) and (distance is not None if distance_scale!=1 else True)
            assumed_pc=pc*pc_scale if pc is not None else None
            assumed_distance=distance*distance_scale if distance is not None else None
            available=available and all(x is None or math.isfinite(x) for x in [assumed_pc,assumed_distance])
            result=classifier(assumed_pc,assumed_distance) if available else {'severity':'unknown','flag_reasons':[]}
            prefix='scenario.%s.%s'%(i,code)
            scenario={'event_id':event['event_id'],'scenario_id':code,'status':'hypothetical' if available else 'unavailable',
                'pc_multiplier':pc_scale,'distance_multiplier':distance_scale,
                'assumed_pc':assumed_pc if available else None,'assumed_miss_distance_m':assumed_distance if available else None,
                'resulting_severity':result['severity'],'flag_reasons':result['flag_reasons'],
                'fact_ids':[]}
            for field in ['pc_multiplier','distance_multiplier','assumed_pc','assumed_miss_distance_m','resulting_severity','status']:
                supporting=[]
                if field=='resulting_severity':
                    supporting=[x for x in [pc,distance,scenario['assumed_pc'],scenario['assumed_miss_distance_m'],pc_scale,distance_scale,(1-pc_scale)*100,3]
                                if x is not None and math.isfinite(x)]
                    supporting.extend(r['threshold'] for r in result['flag_reasons'] if isinstance(r.get('threshold'),(int,float)))
                scenario['fact_ids'].append(fact(prefix+'.'+field,scenario[field],'what_if.'+field,event['event_id'],supporting_numbers=supporting))
            scenarios.append(scenario)
    interpretations=[]
    for event in selected:
        comparisons=[s for s in scenarios if s['event_id']==event['event_id']]
        interpretations.append({'event_id':event['event_id'],'baseline_severity':event['severity'],
            'outcomes':{s['scenario_id']:{'status':s['status'],'resulting_severity':s['resulting_severity'],
                'remaining_critical_triggers':[r['field'] for r in s['flag_reasons'] if r['rule_id'] in {'PC_CRITICAL','MISS_DISTANCE_CRITICAL'}],
                'fact_ids':s['fact_ids']} for s in comparisons}})
    focus=sorted(interpretations,key=lambda e: not (e['baseline_severity']=='critical'
        and e['outcomes']['pc_lower']['resulting_severity']=='critical'
        and e['outcomes']['distance_larger']['resulting_severity']=='critical'
        and e['outcomes']['combined']['resulting_severity']!='critical'))
    context={'statistics':statistics,'facts':facts,'priority_encounters':priority,'what_if_scenarios':scenarios,
            'what_if_interpretations':interpretations,'what_if_focus_event_ids':[e['event_id'] for e in focus[:2]],
            'source':analysis['source'],'model':analysis['model'],'time_basis':analysis['time_basis'],
            'operations_context':build_analysis_context(analysis)}
    context['what_if_reference']=_what_if_reference(context)
    return context


def _what_if_reference(context):
    sentences=[];refs=[]
    labels={'pc_lower':'Pc multiplied by 0.1 alone','distance_larger':'separation multiplied by 2 alone','combined':'combining both assumptions'}
    for eid in context['what_if_focus_event_ids']:
        outcomes=[]
        for scenario in context['what_if_scenarios']:
            if scenario['event_id'] != eid:continue
            outcome=('is unavailable' if scenario['status']=='unavailable' else 'yields '+scenario['resulting_severity'])
            if scenario['resulting_severity']=='critical':
                triggers=[{'predicted_pc':'probability','miss_distance_m':'separation'}[r['field']]
                          for r in scenario['flag_reasons'] if r['rule_id'] in {'PC_CRITICAL','MISS_DISTANCE_CRITICAL'}]
                if triggers:outcome+=' ('+' and '.join(triggers)+' criterion remains active)'
            outcomes.append(labels[scenario['scenario_id']]+' '+outcome)
            refs.extend(k for k in scenario['fact_ids'] if context['facts'][k]['field'] in {'what_if.resulting_severity','what_if.status'})
        sentences.append('Encounter %s: %s.' % (eid, '; '.join(outcomes)))
    sentences.append('These comparisons use assumed inputs; they do not establish a feasible maneuver or predict its outcome.')
    return _statement({'text':' '.join(sentences),'fact_ids':refs},context['facts'],limit=2400)


class ReportService:
    def __init__(self,client_factory=None,clock=time.monotonic,classifier=ml.classify_encounter):
        self.client_factory,self.clock,self.classifier=client_factory or _default_report_client,clock,classifier
        self._reports,self._cache=OrderedDict(),{}
        self._lock,self._slots=threading.RLock(),threading.BoundedSemaphore(2)

    def get(self,analysis_id,report_id):
        with self._lock:
            saved=self._reports.get(report_id)
            if not saved or self.clock()-saved[0]>=3600 or saved[1]['analysis_id']!=analysis_id:
                raise ReportError('Report not found or expired; generate it again.')
            return copy.deepcopy(saved[1])

    def generate(self,analysis):
        context=build_context(analysis,self.classifier);now=self.clock();client=self.client_factory()
        key=(CONTEXT_VERSION,analysis['analysis_id'],client.cache_identity)
        with self._lock:
            cached=self._cache.get(key)
            if cached:
                saved=self._reports.get(cached)
                if saved and now-saved[0]<600:return copy.deepcopy(saved[1])
        report_id=uuid.uuid4().hex
        result={'schema_version':'1.0','analysis_id':analysis['analysis_id'],'report_id':report_id,
            'generated_at':datetime.now(timezone.utc).isoformat(),'status':'unavailable',
            'source':copy.deepcopy(analysis['source']),'model':copy.deepcopy(analysis['model']),'time_basis':analysis['time_basis'],
            'statistics':context['statistics'],'facts':context['facts'],'what_if_scenarios':context['what_if_scenarios'],
            'coverage':{'included_event_ids':[e['event_id'] for e in context['priority_encounters']],
                        'omitted_encounters':len(analysis['encounters'])-len(context['priority_encounters']),
                        'policy':'Critical, elevated, unknown, safe; then earliest source-relative lead time; maximum ten detailed encounters.'},
            'executive_summary':None,'key_findings':[],'priority_events':[],'what_if_summary':None,
            'limitations':['Use this briefing to prioritize review; confirm current tracking before deciding on an avoidance plan.',
                'What-if cases assume different risk estimates or separations; they do not show a feasible maneuver or predict its outcome.',
                'Interpretations may need specialist review; check the supporting encounter values before acting.',
                'Detailed reviews cover up to ten priority encounters; the overall counts include every encounter.'],
            'warnings':list(analysis['warnings']),
            'pdf_url':'/api/analyses/%s/reports/%s.pdf'%(analysis['analysis_id'],report_id)}
        if analysis['source']['mode']=='synthetic_demo':result['limitations'].append('Synthetic demonstration values are used here; these are not current satellite observations.')
        if analysis['time_basis']=='per_event_latest_report':result['limitations'].append('Lead times come from separate source reports, rather than a shared live clock.')
        try:
            if not self._slots.acquire(blocking=False):raise ProviderError('Report generation is busy; retry explicitly later.')
            try:output=client.generate_structured(SYSTEM_PROMPT,provider_context(context),REPORT_OUTPUT_SCHEMA,max_tokens=4096)
            finally:self._slots.release()
            if not isinstance(output,dict) or set(output)!={'executive_summary','key_findings','encounters','what_if_summary'}:
                raise ProviderError('Invalid report output shape.')
            summary=_statement(output['executive_summary'],context['facts'],limit=1400)
            findings=output['key_findings'];items=output['encounters']
            if not isinstance(findings,list) or not 2<=len(findings)<=5:raise ProviderError('Invalid report findings count.')
            checked=[]
            for index, finding in enumerate(findings):
                try:checked.append(_statement(finding,context['facts']))
                except NumericClaimError:
                    if index%2:
                        replacement={'text':'The detailed review covers %s encounters; %s critical encounters fall within 24 hours of their report reference.' % (
                            len(context['priority_encounters']),context['statistics']['critical_within_24h']),
                            'fact_ids':['portfolio.detailed_count','portfolio.critical_within_24h']}
                    else:
                        replacement={'text':'The analysis contains %s encounters, including %s in the critical assessment tier.' % (
                            context['statistics']['total_encounters'],context['statistics']['severity_counts']['critical']),
                            'fact_ids':['portfolio.total','portfolio.critical']}
                    checked.append(_statement(replacement,context['facts']))
                    result['warnings'].append('AI key finding %s included unsupported numbers and was replaced with the cited analysis facts.'%(index+1))
            findings=checked
            if not isinstance(items,list) or len(items)!=len(context['priority_encounters']):raise ProviderError('Report omitted priority encounters.')
            normalized=[]
            for item,event in zip(items,context['priority_encounters']):
                if not isinstance(item,dict) or set(item)!={'event_id','assessment','actions'} or item['event_id']!=event['event_id']:
                    raise ProviderError('Report changed encounter identities or priority order.')
                assessment=_statement(item['assessment'],context['facts'],event['event_id'])
                assessment_status='cited_narrative'
                narrative=assessment['text']
                if (re.search(r'\b(?:Pc|probability)\b',narrative,re.I) and 'distance' in narrative.lower()
                        and re.search(r'\bboth\b.{0,60}\b(?:above|below)\b.{0,80}\bthreshold',narrative,re.I)):
                    # Mixed Pc/distance directions are easily misrepresented in
                    # prose. Preserve the actual rule result rather than ship it.
                    refs=event['fact_ids'];values=context['facts']
                    pc=values[refs['predicted_pc']]['value'];distance=values[refs['miss_distance_m']]['value']
                    severity=values[refs['severity']]['value']
                    assessment={'text':'This encounter is in the %s tier. Estimated collision probability (Pc): %s; predicted closest separation: %s m. Review the assessment before making an operational decision.'%(
                        severity,'unavailable' if pc is None else '%.6g'%pc,'unavailable' if distance is None else '%.6g'%distance),
                        'fact_ids':[refs['severity'],refs['predicted_pc'],refs['miss_distance_m']]}
                    assessment_status='factual_fallback'
                    result['warnings'].append('A mixed Pc/distance threshold-direction claim was omitted for %s; baseline facts are shown.'%event['event_id'])
                choices={x['action_id']:x['label'] for x in event['allowed_actions']};actions=item['actions'];seen=set();valid=[]
                if not isinstance(actions,list) or not 1<=len(actions)<=3:raise ProviderError('Invalid advisory action count.')
                for action in actions:
                    if not isinstance(action,dict) or set(action)!={'action_id','rationale'} or not isinstance(action['action_id'],str) or action['action_id'] not in choices or action['action_id'] in seen:
                        raise ProviderError('Report proposed an unsupported advisory action.')
                    seen.add(action['action_id'])
                    valid.append({'action_id':action['action_id'],'label':choices[action['action_id']],
                        'rationale':_statement(action['rationale'],context['facts'],event['event_id'],600)})
                normalized.append({'event_id':event['event_id'],'assessment':assessment,'assessment_status':assessment_status,'actions':valid})
            proposed=_statement(output['what_if_summary'],context['facts'],limit=2400)
            what_if=copy.deepcopy(context['what_if_reference'])
            if proposed['text']!=what_if['text']:
                result['warnings'].append('The what-if prose uses the exact classification comparison; a rewritten AI interpretation was omitted.')
            result.update(status='ready',executive_summary=summary,key_findings=findings,priority_events=normalized,what_if_summary=what_if)
        except ProviderError as error:result['warnings'].append(str(error))
        with self._lock:
            self._reports[report_id]=(now,copy.deepcopy(result))
            while len(self._reports)>32:self._reports.popitem(last=False)
            if result['status']=='ready':self._cache[key]=report_id
            self._cache={k:v for k,v in self._cache.items() if v in self._reports}
        return result
