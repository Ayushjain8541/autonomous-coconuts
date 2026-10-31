import json
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from backend.analysis import AnalysisService
from backend.config import load_settings
from backend.insights import AnthropicClient, InsightsService, InsightRequestError


class ProviderHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.requests.append(request)
        packet = json.loads(request['messages'][0]['content'])
        self.server.last_packet = packet
        mode = self.server.mode
        if mode == 'truncated':
            self.send_response(200);self.send_header('Transfer-Encoding','chunked');self.end_headers()
            self.wfile.write(b'20\r\n{}');self.wfile.flush();self.close_connection=True;return
        if mode == 'slow_headers':
            try:
                self.wfile.write(b'HTTP/1.0 200 OK\r\nX-Slow: ');self.wfile.flush()
                for _ in range(6):
                    time.sleep(.2);self.wfile.write(b'x');self.wfile.flush()
                self.wfile.write(b'\r\n\r\n{}');self.wfile.flush()
            except OSError:pass
            self.close_connection=True;return
        if mode == 'error':
            self.send_response(429);self.end_headers();return
        if mode == 'bad':
            result = {'items': [{'event_id': packet['events'][0]['event_id'], 'next_step_id': 'MADE_UP_REVIEW'}]}
        else:
            result = {'items': [{'event_id': e['event_id'], 'next_step_id': e['review_options'][0]['option_id']} for e in packet['events']]}
        response = {'id': 'msg_test', 'type': 'message', 'role': 'assistant', 'model': 'test-model',
                    'content': [{'type': 'text', 'text': json.dumps(result)}],
                    'stop_reason': 'refusal' if mode == 'refusal' else 'end_turn',
                    'usage': {'input_tokens': 1, 'output_tokens': 1}}
        raw = json.dumps(response).encode();self.send_response(200);self.send_header('Content-Length',str(len(raw)));self.end_headers()
        try:
            if mode == 'slow':
                chunk_size=(len(raw)+5)//6
                for offset in range(0,len(raw),chunk_size):
                    time.sleep(.2);self.wfile.write(raw[offset:offset+chunk_size]);self.wfile.flush()
            else:self.wfile.write(raw)
        except OSError:pass
    def log_message(self,*args):pass


class InsightsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provider=ThreadingHTTPServer(('127.0.0.1',0),ProviderHandler)
        cls.thread=threading.Thread(target=cls.provider.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.provider.shutdown();cls.provider.server_close();cls.thread.join(timeout=2)
    def setUp(self):
        self.provider.mode='good';self.provider.requests=[]
        self.analysis=AnalysisService().demo()
        self.client=AnthropicClient('test-credential','test-model',timeout=2,base_url='http://127.0.0.1:%s'%self.provider.server_port)
        self.service=InsightsService(client_factory=lambda:self.client)
        self.ids=[self.analysis['encounters'][0]['event_id']]

    def test_real_http_provider_response_becomes_grounded_summary_and_citations(self):
        result=self.service.generate(self.analysis,self.ids)
        self.assertEqual(result['status'],'ready')
        self.assertEqual(result['analysis_id'],self.analysis['analysis_id'])
        item=result['items'][0]
        self.assertIn('Assessment: Critical.',item['summary'])
        self.assertIn('is below its 1000 m criterion',item['summary'])
        self.assertIn('from the reference, outside the 24-hour window',item['summary'])
        self.assertIn('Escalate to mission operations',item['summary'])
        self.assertEqual(item['event_id'],self.ids[0])
        self.assertTrue(item['fact_refs'])
        self.assertTrue(any('Synthetic' in x or 'synthetic' in x for x in item['limitations']))
        request=self.provider.requests[0]
        self.assertEqual(request['output_config']['format']['type'],'json_schema')
        self.assertNotIn('api_key',json.dumps(self.provider.last_packet))
        context=self.provider.last_packet
        self.assertEqual(context['operations_context']['model'], self.analysis['model'])
        reason=context['events'][0]['classification_reasons'][1]
        self.assertEqual((reason['field'], reason['operator'], reason['value'], reason['threshold']),
                         ('miss_distance_m', '<', 800, 1000))
        self.assertIn('not a time trend', request['system'])
        self.assertIn('not countdowns', request['system'])

    def test_cache_avoids_duplicate_paid_requests(self):
        self.service.generate(self.analysis,self.ids);self.service.generate(self.analysis,self.ids)
        self.assertEqual(len(self.provider.requests),1)

    def test_overall_deadline_bounds_slow_headers_and_body_and_releases_capacity(self):
        self.client.timeout=.5
        for mode in ['slow','slow_headers','slow']:
            with self.subTest(mode=mode):
                self.provider.mode=mode
                started=time.monotonic()
                result=self.service.generate(AnalysisService().demo(),self.ids)
                self.assertEqual(result['status'],'unavailable')
                self.assertLess(time.monotonic()-started,.9)
                self.assertTrue(any('timed out' in x for x in result['warnings']))
        self.provider.mode='good';self.client.timeout=2
        self.assertEqual(self.service.generate(self.analysis,self.ids)['status'],'ready')

    def test_provider_failure_refusal_and_unsupported_claim_are_unavailable(self):
        for mode in ['error','refusal','bad']:
            with self.subTest(mode=mode):
                self.provider.mode=mode
                result=InsightsService(client_factory=lambda:self.client).generate(self.analysis,self.ids)
                self.assertEqual(result['status'],'unavailable')
                self.assertEqual(result['items'],[])
                self.assertTrue(result['warnings'])

    def test_unknown_duplicate_and_excessive_ids_rejected_before_provider(self):
        for ids in [[],['unknown'],self.ids*2,['a']*11]:
            with self.subTest(ids=ids):
                with self.assertRaises(InsightRequestError):self.service.generate(self.analysis,ids)
        self.assertEqual(len(self.provider.requests),0)

    def test_missing_key_is_unavailable_without_changing_analysis(self):
        service=InsightsService(client_factory=lambda:AnthropicClient('', 'test-model'))
        result=service.generate(self.analysis,self.ids)
        self.assertEqual(result['status'],'unavailable')
        self.assertEqual(self.analysis['encounters'][0]['severity'],'critical')
        self.assertEqual(len(self.provider.requests),0)

    def test_config_reads_ignored_env_without_executing_or_exposing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'.env.local'
            p.write_text('ANTHROPIC_API_KEY="test-credential"\nANTHROPIC_MODEL=test-model\nANTHROPIC_TIMEOUT_SECONDS=12\n')
            settings=load_settings(Path(directory),environ={})
            self.assertEqual(settings.api_key,'test-credential')
            self.assertEqual(settings.model,'test-model')
            self.assertNotIn('test-credential',repr(settings))
            p.write_text('ANTHROPIC_API_KEY=changed-locally\n')
            self.assertEqual(load_settings(Path(directory),environ={}).api_key,'changed-locally')

    def test_full_reports_have_a_separate_bounded_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            settings=load_settings(Path(directory),environ={})
            self.assertEqual(settings.timeout,25)
            self.assertEqual(settings.report_timeout,60)
            settings=load_settings(Path(directory),environ={'ANTHROPIC_REPORT_TIMEOUT_SECONDS':'75'})
            self.assertEqual(settings.report_timeout,75)
            self.assertEqual(load_settings(Path(directory),environ={'ANTHROPIC_REPORT_TIMEOUT_SECONDS':'inf'}).report_timeout,60)
