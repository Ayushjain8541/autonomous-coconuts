import copy
import importlib.util
import json
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
from backend.analysis import AnalysisService
from backend.config import Settings
from backend.reports import ReportService
from backend.report_pdf import render_pdf, PDFError
from backend.server import make_server
from test_reports import ReportClient

PDF_AVAILABLE=importlib.util.find_spec('reportlab') is not None


class ReportHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=ReportClient()
        cls.server=make_server(port=0,report_service=ReportService(client_factory=lambda:cls.client),settings_loader=lambda:Settings())
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base='http://127.0.0.1:%s'%cls.server.server_port
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=2)
    def setUp(self):
        self.client.change=None
        with urllib.request.urlopen(self.base+'/api/demo') as response:self.analysis=json.load(response)
        self.path='/api/analyses/'+self.analysis['analysis_id']+'/report'
    def request(self,path,data=None):
        req=urllib.request.Request(self.base+path,data=data,headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=5) as response:return response.status,response.read(),response.headers
        except urllib.error.HTTPError as error:return error.code,error.read(),error.headers

    def test_report_route_and_actionable_export_dependency_failure(self):
        status,raw,_=self.request(self.path,b'{}');report=json.loads(raw)
        self.assertEqual(status,200);self.assertEqual(report['status'],'ready')
        self.assertEqual(report['analysis_id'],self.analysis['analysis_id'])
        with patch('backend.server.render_pdf',side_effect=PDFError('Install the PDF extra.')):
            status,body,_=self.request(report['pdf_url'])
        self.assertEqual(status,503);self.assertEqual(json.loads(body)['error']['code'],'PDF_UNAVAILABLE')
        status,_,_=self.request('/api/analyses/'+self.analysis['analysis_id'])
        self.assertEqual(status,200)

    def test_unknown_report_analysis_and_malformed_request_are_rejected(self):
        self.assertEqual(self.request('/api/analyses/missing/report',b'{}')[0],404)
        self.assertEqual(self.request(self.path,b'{"invented":true}')[0],400)
        self.assertEqual(self.request('/api/analyses/'+self.analysis['analysis_id']+'/reports/missing.pdf')[0],404)

    @unittest.skipUnless(PDF_AVAILABLE,'Install backend/requirements.txt for PDF checks')
    def test_download_is_exact_report_and_does_not_generate_again(self):
        _,raw,_=self.request(self.path,b'{}');report=json.loads(raw);calls=self.client.calls
        status,pdf,headers=self.request(report['pdf_url'])
        self.assertEqual(status,200);self.assertTrue(pdf.startswith(b'%PDF-'))
        self.assertIn('attachment;',headers['Content-Disposition'])
        self.assertEqual(headers.get_content_type(),'application/pdf')
        self.assertEqual(self.client.calls,calls)
        self.client.change='failure'
        _,raw,_=self.request(self.path,b'{}') # cached successful report is unchanged
        self.assertEqual(json.loads(raw)['report_id'],report['report_id'])

    @unittest.skipUnless(PDF_AVAILABLE,'Install backend/requirements.txt for PDF checks')
    def test_failed_narrative_and_long_escaped_multipage_reports_export(self):
        self.client.change='failure'
        _,raw,_=self.request(self.path,b'{}');report=json.loads(raw)
        self.assertEqual(report['status'],'unavailable')
        self.assertEqual(self.request(report['pdf_url'])[0],200)
        report=ReportService(client_factory=lambda:ReportClient()).generate(self.analysis)
        long=copy.deepcopy(report)
        long['executive_summary']['text']='<tag> & <b>source text</b> '+('Long explanation. '*80)
        long['priority_events']*=4
        pdf=render_pdf(long)
        self.assertTrue(pdf.startswith(b'%PDF-'));self.assertIn(b'%%EOF',pdf)
        self.assertGreater(pdf.count(b'/Type /Page'),2)
