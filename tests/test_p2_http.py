import json
import threading
import unittest
import urllib.error
import urllib.request
from backend.server import make_server
from backend.analysis import AnalysisService
from backend.config import Settings
from backend.insights import AnthropicClient, InsightsService

CSV = b'event_id,time_to_tca,miss_distance,risk\na,3,900,-6\na,2,800,-5\n'


def model(request):
    return {'model_version':'http-boundary-v1','feature_schema_version':'1','predictions':[
        {'event_id':e['event_id'],'predicted_pc':0.0001,'predicted_log10_pc':-4,'status':'ready','warnings':[]}
        for e in request['events']]}


class P2HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=make_server(port=0, analysis_service=AnalysisService(predictor=model),
            insights_service=InsightsService(client_factory=lambda:AnthropicClient('', 'test')),
            settings_loader=lambda:Settings(),max_upload_bytes=1024)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base='http://127.0.0.1:%s'%cls.server.server_port
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=2)
    def request(self,path,data=None,content_type=None,method=None,headers=None):
        h=headers or {}
        if content_type:h['Content-Type']=content_type
        req=urllib.request.Request(self.base+path,data=data,headers=h,method=method)
        try:
            with urllib.request.urlopen(req,timeout=4) as response:
                body=response.read();return response.status,json.loads(body) if body else None,response.headers
        except urllib.error.HTTPError as error:
            return error.code,json.load(error),error.headers

    def test_multipart_csv_upload_retrieval_and_prediction_contract(self):
        body=b'--boundary\r\nContent-Disposition: form-data; name="file"; filename="reports.csv"\r\nContent-Type: text/csv\r\n\r\n'+CSV+b'\r\n--boundary--\r\n'
        status,data,_=self.request('/api/analyses',body,'multipart/form-data; boundary=boundary')
        self.assertEqual(status,200)
        self.assertEqual(data['source']['report_count'],2)
        self.assertEqual(data['encounters'][0]['predicted_pc'],0.0001)
        self.assertEqual(data['encounters'][0]['latest_report_id'],'row-3')
        code,saved,_=self.request('/api/analyses/'+data['analysis_id'])
        self.assertEqual(code,200);self.assertEqual(saved,data)

    def test_raw_csv_convenience_and_error_detail(self):
        status,data,_=self.request('/api/analyses',CSV,'text/csv')
        self.assertEqual(status,200)
        status,error,_=self.request('/api/analyses',b'event_id,time_to_tca,miss_distance\na,NaN,800\n','text/csv')
        self.assertEqual(status,422)
        self.assertEqual(error['error']['details'][0]['column'],'time_to_tca')
        self.assertEqual(error['error']['total_errors'],1)

    def test_oversized_or_unsupported_uploads_do_not_succeed(self):
        status,error,_=self.request('/api/analyses',b'x'*1025,'text/csv')
        self.assertEqual(status,413);self.assertEqual(error['error']['code'],'UPLOAD_TOO_LARGE')
        status,error,_=self.request('/api/analyses',b'{}','application/json')
        self.assertEqual(status,415)
        status,error,_=self.request('/api/analyses',b'bad','multipart/form-data')
        self.assertEqual(status,400)

    def test_demo_insights_are_separate_and_unknown_ids_are_errors(self):
        _,demo,_=self.request('/api/demo')
        payload=json.dumps({'event_ids':[demo['encounters'][0]['event_id']]}).encode()
        status,insights,_=self.request('/api/analyses/'+demo['analysis_id']+'/insights',payload,'application/json')
        self.assertEqual(status,200);self.assertEqual(insights['status'],'unavailable')
        status,error,_=self.request('/api/analyses/no-such-analysis/insights',payload,'application/json')
        self.assertEqual(status,404)
        status,error,_=self.request('/api/analyses/'+demo['analysis_id']+'/insights',b'{"event_ids":["unknown"]}','application/json')
        self.assertEqual(status,400);self.assertEqual(error['error']['code'],'UNKNOWN_EVENT')

    def test_local_cors_preflight_and_schema(self):
        status,_,headers=self.request('/api/analyses',method='OPTIONS',headers={'Origin':'http://localhost:5173'})
        self.assertEqual(status,204);self.assertEqual(headers['Access-Control-Allow-Origin'],'http://localhost:5173')
        status,error,_=self.request('/api/health',headers={'Origin':'https://unexpected.example'})
        self.assertEqual(status,403)
        status,data,_=self.request('/api/schema')
        self.assertEqual(status,200);self.assertEqual(data['limits']['max_upload_bytes'],1024)
        self.assertEqual(data['analysis']['properties']['schema_version']['const'],'1.0')

    def test_complete_http_analysis_to_grounded_provider_insights(self):
        from test_insights import ProviderHandler
        from http.server import ThreadingHTTPServer
        provider=ThreadingHTTPServer(('127.0.0.1',0),ProviderHandler)
        provider.mode='good';provider.requests=[]
        thread=threading.Thread(target=provider.serve_forever,daemon=True);thread.start()
        client=AnthropicClient('test-credential','test-model',base_url='http://127.0.0.1:%s'%provider.server_port)
        api=make_server(port=0, analysis_service=AnalysisService(predictor=model),
                        insights_service=InsightsService(client_factory=lambda:client),settings_loader=lambda:Settings())
        api_thread=threading.Thread(target=api.serve_forever,daemon=True);api_thread.start()
        try:
            base='http://127.0.0.1:%s'%api.server_port
            upload=urllib.request.Request(base+'/api/analyses',data=CSV,headers={'Content-Type':'text/csv'})
            with urllib.request.urlopen(upload,timeout=3) as response: analysis=json.load(response)
            request=urllib.request.Request(base+'/api/analyses/'+analysis['analysis_id']+'/insights',
                data=b'{"event_ids":["a"]}',headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(request,timeout=3) as response: result=json.load(response)
            self.assertEqual(result['status'],'ready')
            self.assertEqual(result['items'][0]['event_id'],'a')
            self.assertIn('critical',result['items'][0]['summary'])
            self.assertEqual(result['items'][0]['fact_refs'][0]['event_id'],'a')
        finally:
            api.shutdown();api.server_close();api_thread.join(timeout=2)
            provider.shutdown();provider.server_close();thread.join(timeout=2)
