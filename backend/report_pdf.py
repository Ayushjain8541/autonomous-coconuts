"""Readable PDF export; ReportLab is an optional extra for the numeric API."""
import io
import threading
from pathlib import Path
from xml.sax.saxutils import escape


class PDFError(ValueError):
    code,status,details='PDF_UNAVAILABLE',503,[]


_FONT_LOCK=threading.Lock()


def render_pdf(report):
    try:
        import reportlab
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
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
        grouped={}
        for key in statement['fact_ids']:
            fact=report['facts'][key]
            owner=fact['event_id'] or 'Portfolio'
            labels=grouped.setdefault(owner,[])
            field={'predicted_pc':'forecast Pc','reported_pc':'reported Pc','miss_distance_m':'miss distance (m)',
                'time_to_tca_hours':'lead time (h)','flag_reasons':'trigger thresholds','what_if.resulting_severity':'what-if rule results'}.get(fact['field'],fact['field'].replace('_',' ').replace('.',': '))
            if field not in labels:labels.append(field)
        return p('Evidence: '+'; '.join(owner+': '+', '.join(labels) for owner,labels in grouped.items()),'small')
    body=[];out=io.BytesIO()
    doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=43,leftMargin=43,topMargin=43,bottomMargin=44,
        title='Satellite encounter risk briefing',author='Autonomous Coconuts')
    width=A4[0]-86
    body.extend([p('AUTONOMOUS COCONUTS / DECISION SUPPORT','small'),p('Encounter risk briefing','title')])
    mode='SYNTHETIC DEMO' if report['source']['mode']=='synthetic_demo' else 'UPLOADED HISTORICAL REPORTS'
    body.append(p(mode+' | AI narrative: '+report['status'].upper()+' | Model: '+report['model']['status'],'small'))
    body.append(p('Generated '+report['generated_at']+' | Analysis '+report['analysis_id'],'small'))
    stats=report['statistics'];counts=stats['severity_counts']
    metrics=[]
    for label,value in [('Encounters',stats['total_encounters']),('Critical',counts['critical']),('Elevated',counts['elevated']),('Unknown',counts['unknown'])]:
        metrics.append([p(value,'metric'),p(label,'small')])
    grid=Table([metrics],colWidths=[width/4]*4)
    grid.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),pale),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    body.extend([Spacer(1,8),grid,p('Safe: %s | Critical within 24h of source reference: %s | Predictions unavailable: %s'%(counts['safe'],stats['critical_within_24h'],stats['prediction_counts']['unavailable']),'small')])
    body.append(p('Executive briefing','h1'))
    if report['executive_summary']:
        body.extend([p(report['executive_summary']['text']),evidence(report['executive_summary'])])
    else:body.append(p('AI narrative is unavailable. The portfolio counts and hypothetical rule comparisons below remain deterministic results.'))
    if report['key_findings']:
        body.append(p('Key findings','h1'))
        for finding in report['key_findings']:body.extend([p(finding['text']),evidence(finding)])
    body.extend([p('Coverage and interpretation','h2'),p(report['coverage']['policy'])])
    body.append(p('%s encounters are outside the detailed narrative. Review the full dashboard before drawing portfolio-wide conclusions.'%report['coverage']['omitted_encounters']))
    if report['time_basis']=='per_event_latest_report':body.append(p('Lead times are relative to each historical encounter report. They are not deadlines measured from today.'))
    body.append(p('All what-if values are independent assumptions. They do not establish a feasible maneuver or predict risk reduction.','small'))
    body.append(PageBreak())
    body.append(p('Priority encounters and what-if analysis','h1'))
    narratives={item['event_id']:item for item in report['priority_events']}
    for i,event_id in enumerate(report['coverage']['included_event_ids']):
        fact=report['facts'];prefix='event.%s.'%i
        baseline={field:fact[prefix+field]['value'] for field in ['predicted_pc','reported_pc','miss_distance_m','severity','time_to_tca_hours']}
        body.append(p(event_id,'h2'))
        body.append(p('Baseline: %s | Pc %s | Miss distance %s m | Lead time %s h'%(baseline['severity'].upper(),number(baseline['predicted_pc']),number(baseline['miss_distance_m']),number(baseline['time_to_tca_hours']))))
        body.append(p('Forecast Pc: '+number(baseline['predicted_pc'])+' | Reported Pc: '+number(baseline['reported_pc']),'small'))
        item=narratives.get(event_id)
        if item:
            if item.get('assessment_status')=='factual_fallback':body.append(p('AI threshold-direction claim omitted; baseline facts shown.','small'))
            body.extend([p(item['assessment']['text']),evidence(item['assessment'])])
            for action in item['actions']:
                body.append(Paragraph('<b>'+escape(plain(action['label']))+'</b>: '+escape(plain(action['rationale']['text'])),styles['body']))
                body.append(evidence(action['rationale']))
        rows=[[p(x,'cell') for x in ['Assumption','Pc','Miss distance (m)','Rule result']]]
        rows.append([p(x,'cell') for x in ['Baseline',number(baseline['predicted_pc']),number(baseline['miss_distance_m']),baseline['severity']]])
        names={'pc_lower':'Pc x 0.1 only','distance_larger':'Distance x 2 only','combined':'Pc x 0.1; distance x 2'}
        for scenario in report['what_if_scenarios']:
            if scenario['event_id']!=event_id:continue
            rows.append([p(x,'cell') for x in [names[scenario['scenario_id']],number(scenario['assumed_pc']),number(scenario['assumed_miss_distance_m']),scenario['resulting_severity'] if scenario['status']=='hypothetical' else 'Unavailable']])
        table=Table(rows,colWidths=[width*.40,width*.18,width*.23,width*.19],repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),pale),('LINEBELOW',(0,0),(-1,0),.7,line),
            ('LINEBELOW',(0,1),(-1,-1),.3,line),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        body.extend([Spacer(1,5),KeepTogether([table]),Spacer(1,9)])
    if report['what_if_summary']:
        body.extend([p('What the comparison means','h1'),p(report['what_if_summary']['text']),evidence(report['what_if_summary'])])
    body.append(p('Method, provenance and limits','h1'))
    body.append(p('Advisory briefing, not a maneuver instruction or safety clearance. Fact references and numerical membership are checked; interpretation still requires review. Coverage, source mode and hypothetical assumptions are disclosed above.','small'))
    for warning in report['warnings']:body.append(p('Note: '+warning,'small'))
    body.append(p('Model target: '+report['model']['target'],'small'))
    body.append(p('Source reports: %s | Model version: %s'%(stats['source_report_count'],report['model']['version'] or 'Unavailable'),'small'))
    if report['source'].get('sha256'):body.append(p('Source SHA-256: '+report['source']['sha256'],'small'))
    def footer(canvas,document):
        canvas.setStrokeColor(line);canvas.line(43,34,A4[0]-43,34)
        canvas.setFont('Coconuts',7);canvas.setFillColor(muted)
        canvas.drawString(43,22,'ADVISORY / ASSUMPTIONS REQUIRE REVIEW | Report '+report['report_id'][:12])
        canvas.drawRightString(A4[0]-43,22,str(document.page))
    doc.build(body,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
