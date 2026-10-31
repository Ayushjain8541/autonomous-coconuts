"""Readable PDF export; ReportLab is an optional extra for the numeric API."""
import io
import threading
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape


class PDFError(ValueError):
    code,status,details='PDF_UNAVAILABLE',503,[]


_FONT_LOCK=threading.Lock()


def render_pdf(report):
    try:
        import reportlab
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
    except ImportError:
        raise PDFError('PDF export needs the PDF extra: install backend/requirements.txt in the server environment.') from None
    with _FONT_LOCK:
        if 'Coconuts' not in pdfmetrics.getRegisteredFontNames():
            fonts=Path(reportlab.__file__).parent/'fonts'
            pdfmetrics.registerFont(TTFont('Coconuts',str(fonts/'Vera.ttf')))
            pdfmetrics.registerFont(TTFont('Coconuts-Bold',str(fonts/'VeraBd.ttf')))
            pdfmetrics.registerFontFamily('Coconuts',normal='Coconuts',bold='Coconuts-Bold',italic='Coconuts',boldItalic='Coconuts-Bold')
    navy=colors.HexColor('#132B40');green=colors.HexColor('#087D73');muted=colors.HexColor('#516474')
    pale=colors.HexColor('#EFF5F7');line=colors.HexColor('#D5E1E7')
    styles={
        'title':ParagraphStyle('title',fontName='Coconuts-Bold',fontSize=25,leading=30,textColor=navy,spaceAfter=10),
        'h1':ParagraphStyle('h1',fontName='Coconuts-Bold',fontSize=16,leading=21,textColor=navy,spaceBefore=16,spaceAfter=8,keepWithNext=True),
        'h2':ParagraphStyle('h2',fontName='Coconuts-Bold',fontSize=12,leading=17,textColor=navy,spaceBefore=12,spaceAfter=6,keepWithNext=True),
        'body':ParagraphStyle('body',fontName='Coconuts',fontSize=9,leading=14,textColor=navy,spaceAfter=7,splitLongWords=True),
        'small':ParagraphStyle('small',fontName='Coconuts',fontSize=7.5,leading=11,textColor=muted,spaceAfter=7,splitLongWords=True),
        'metric':ParagraphStyle('metric',fontName='Coconuts-Bold',fontSize=18,leading=24,textColor=green),
        'cell':ParagraphStyle('cell',fontName='Coconuts',fontSize=8,leading=11,textColor=navy,spaceAfter=0),
    }
    def plain(value):
        return str(value).replace('\u2013','-').replace('\u2014','-').replace('\u2011','-').replace('\u2019',"'").replace('\u2018',"'").replace('\u201c','"').replace('\u201d','"')
    def p(value,style='body'):return Paragraph(escape(plain(value)).replace('\n','<br/>'),styles[style])
    def number(value):return 'Unavailable' if value is None else ('%.4g'%value)
    def evidence(statement):
        owners=[]
        for key in statement['fact_ids']:
            fact=report['facts'][key]
            owner='encounter '+fact['event_id'] if fact['event_id'] else 'overall encounter assessment'
            if owner not in owners:owners.append(owner)
        return p('Supporting assessment: '+'; '.join(owners),'small')
    body=[];out=io.BytesIO()
    doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=43,leftMargin=43,topMargin=43,bottomMargin=44,
        title='Satellite operations risk report',author='Autonomous Coconuts')
    width=A4[0]-86
    body.extend([p('AUTONOMOUS COCONUTS / SATELLITE OPERATIONS','small'),p('Satellite encounter report','title')])
    demonstration=report['source']['mode']=='synthetic_demo'
    mode='DEMONSTRATION REPORT - EXAMPLE ENCOUNTER DATA' if demonstration else 'REVIEW OF UPLOADED ENCOUNTER REPORTS'
    body.append(p(mode,'small'))
    try:prepared=datetime.fromisoformat(report['generated_at'].replace('Z','+00:00')).astimezone(timezone.utc).strftime('%d %b %Y, %H:%M UTC')
    except ValueError:prepared=report['generated_at']
    body.append(p('Prepared '+prepared,'small'))
    if demonstration:body.append(p('This example illustrates an encounter review. It does not describe live spacecraft or current collision threats.','small'))
    elif report['model']['status']=='unavailable':body.append(p('Collision-probability estimates are unavailable. Review unassessed encounters before making decisions.','small'))
    stats=report['statistics'];counts=stats['severity_counts']
    metrics=[]
    for label,value in [('Encounters reviewed',stats['total_encounters']),('Critical',counts['critical']),('Elevated',counts['elevated']),('Needs assessment',counts['unknown'])]:
        metrics.append([p(value,'metric'),p(label,'small')])
    grid=Table([metrics],colWidths=[width/4]*4)
    grid.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),pale),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    body.extend([Spacer(1,8),grid,p('Safe tier: %s | Critical within 24h of the report reference: %s | Missing risk estimates: %s'%(counts['safe'],stats['critical_within_24h'],stats['prediction_counts']['unavailable']),'small')])
    body.append(p('Pc is the estimated probability of collision. Predicted separation is the expected distance between the objects at closest approach.','small'))
    body.append(p('Operational summary','h1'))
    if report['executive_summary']:
        body.extend([p(report['executive_summary']['text']),evidence(report['executive_summary'])])
    else:body.append(p('The written assessment could not be generated. Review the encounter values, classifications and scenario comparisons below.'))
    if report['key_findings']:
        body.append(p('What needs attention','h1'))
        for finding in report['key_findings']:body.extend([p(finding['text']),evidence(finding)])
    body.append(p('Review coverage','h2'))
    included=len(report['coverage']['included_event_ids']);omitted=report['coverage']['omitted_encounters']
    body.append(p('Critical cases are reviewed first, followed by elevated cases and those needing assessment. Reported time to closest approach determines the order within each tier.'))
    body.append(p(('All reviewed encounters are included in the detailed assessment below.' if not omitted else
        'Detailed assessments cover %s of %s encounters. The remaining %s are available in the dashboard.'%(included,stats['total_encounters'],omitted))))
    if report['time_basis']=='per_event_latest_report':body.append(p('Times are measured from each encounter\'s source report, not from today. Confirm current tracking for operational use.'))
    body.append(p('Scenario comparisons show how assumed changes would affect classification. They do not calculate an avoidance maneuver.','small'))
    body.append(PageBreak())
    body.append(p('Encounter assessments','h1'))
    narratives={item['event_id']:item for item in report['priority_events']}
    for i,event_id in enumerate(report['coverage']['included_event_ids']):
        fact=report['facts'];prefix='event.%s.'%i
        baseline={field:fact[prefix+field]['value'] for field in ['predicted_pc','reported_pc','miss_distance_m','severity','time_to_tca_hours']}
        body.append(p('Encounter '+event_id,'h2'))
        tier='NEEDS ASSESSMENT' if baseline['severity']=='unknown' else baseline['severity'].upper()
        body.append(p('Assessment: %s | Estimated Pc %s | Predicted separation %s m | Closest approach in %s h from the report reference'%(tier,number(baseline['predicted_pc']),number(baseline['miss_distance_m']),number(baseline['time_to_tca_hours']))))
        body.append(p('Pc in the source report: '+number(baseline['reported_pc']) if baseline['reported_pc'] is not None else 'No source Pc was provided for comparison.','small'))
        item=narratives.get(event_id)
        if item:
            if item.get('assessment_status')=='factual_fallback':body.append(p('A conflicting explanation was excluded. The recorded assessment is shown below.','small'))
            body.extend([p(item['assessment']['text']),evidence(item['assessment'])])
            for action in item['actions']:
                body.append(Paragraph('<b>'+escape(plain(action['label']))+'</b>: '+escape(plain(action['rationale']['text'])),styles['body']))
        rows=[[p(x,'cell') for x in ['If estimates changed','Estimated Pc','Separation (m)','Assessment']]]
        rows.append([p(x,'cell') for x in ['Current assessment',number(baseline['predicted_pc']),number(baseline['miss_distance_m']),tier.title()]])
        names={'pc_lower':'Lower Pc estimate (x 0.1)','distance_larger':'Greater separation (x 2)','combined':'Both changes together'}
        for scenario in report['what_if_scenarios']:
            if scenario['event_id']!=event_id:continue
            outcome='Needs assessment' if scenario['resulting_severity']=='unknown' else scenario['resulting_severity'].title()
            rows.append([p(x,'cell') for x in [names[scenario['scenario_id']],number(scenario['assumed_pc']),number(scenario['assumed_miss_distance_m']),outcome if scenario['status']=='hypothetical' else 'Not assessed']])
        table=Table(rows,colWidths=[width*.40,width*.18,width*.23,width*.19],repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),pale),('LINEBELOW',(0,0),(-1,0),.7,line),
            ('LINEBELOW',(0,1),(-1,-1),.3,line),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        body.extend([Spacer(1,5),KeepTogether([p('Scenario comparisons for encounter '+event_id,'small'),table]),Spacer(1,9)])
    if report['what_if_summary']:
        body.extend([p('Implications for the review','h1'),p(report['what_if_summary']['text']),evidence(report['what_if_summary'])])
    body.append(p('Planning notes and report details','h1'))
    body.append(p('Use this briefing to set review priorities. Confirm current tracking and ask the flight-dynamics team to assess any avoidance options. Scenario assumptions do not establish an achievable change in orbit or collision risk.','small'))
    for warning in report['warnings']:
        if warning.startswith(('Synthetic demo:','Synthetic relative geometry','Lead times are measured','Source miss distance')):continue
        if 'threshold-direction' in warning:warning='An explanation conflicted with the encounter assessment; recorded values are shown instead.'
        body.append(p('Review note: '+warning,'small'))
    body.append(p('Data used: %s source reports covering %s encounters.'%(stats['source_report_count'],stats['total_encounters']),'small'))
    origin='Demonstration values' if demonstration else ('Model estimates supplied with this assessment' if report['model']['status']=='ready' else 'Risk estimates not available')
    body.append(p('Risk estimate source: '+origin,'small'))
    if not demonstration and report['model']['status']=='ready':
        target=report['model']['target'];lower=target.lower()
        if 'per-report' in lower or 'per telemetry row' in lower:target='Collision-risk estimate from each encounter\'s source telemetry report.'
        elif 'final' in lower and 'report' in lower:target='Forecast of a later reported risk estimate, using earlier encounter telemetry.'
        body.append(p('Assessment scope: '+target,'small'))
    if report['model']['version']:body.append(p('Model reference: '+report['model']['version'],'small'))
    body.append(p('Report reference: '+report['report_id']+' | Assessment reference: '+report['analysis_id'],'small'))
    if report['source'].get('sha256'):body.append(p('Source SHA-256: '+report['source']['sha256'],'small'))
    def footer(canvas,document):
        canvas.setStrokeColor(line);canvas.line(43,34,A4[0]-43,34)
        canvas.setFont('Coconuts',7);canvas.setFillColor(muted)
        canvas.drawString(43,22,('DEMONSTRATION DATA | ' if demonstration else 'FOR OPERATIONS REVIEW | ')+'Report '+report['report_id'][:12])
        canvas.drawRightString(A4[0]-43,22,str(document.page))
    doc.build(body,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
