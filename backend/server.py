#!/usr/bin/env python3
"""P2 local API: bounded uploads, stored assessments and grounded Anthropic insights."""
import argparse
import json
import os
import sys
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from backend.analysis import AnalysisService, AnalysisError
from backend.config import load_settings
from backend.ingestion import CSVError, MAX_UPLOAD_BYTES
from backend.insights import InsightsService, InsightRequestError
from backend.reports import ReportService, ReportError
from backend.report_pdf import render_pdf, PDFError

ASSETS = {'/': ('index.html', 'text/html; charset=utf-8'),
          '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
          '/styles.css': ('styles.css', 'text/css; charset=utf-8')}


class RequestError(ValueError):
    def __init__(self, message, code='INVALID_REQUEST', status=400):
        super().__init__(message)
        self.code, self.status, self.details = code, status, []


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(30)

    def reply(self, status, data, content_type='application/json; charset=utf-8', download_name=None):
        body = json.dumps(data, allow_nan=False).encode() if isinstance(data, dict) else data
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if download_name:self.send_header('Content-Disposition','attachment; filename="'+download_name+'"')
        origin = self.headers.get('Origin')
        if origin and origin in self.server.settings_loader().cors_origins:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Max-Age', '600')
        self.end_headers()
        self.wfile.write(body)

    def _origin_allowed(self):
        origin = self.headers.get('Origin')
        return not origin or origin in self.server.settings_loader().cors_origins or origin == 'http://' + self.headers.get('Host', '')

    def _error(self, error):
        code = getattr(error, 'code', 'INTERNAL_ERROR')
        status = getattr(error, 'status', 413 if code == 'UPLOAD_TOO_LARGE' else 422)
        detail = {'code': code, 'message': str(error), 'details': getattr(error, 'details', [])}
        if isinstance(error, CSVError):
            detail['total_errors'] = error.total_errors
        self.reply(status, {'error': detail})

    def _body(self, limit):
        if self.headers.get('Transfer-Encoding'):
            raise RequestError('Send a request with Content-Length, not chunked encoding.')
        try:
            length = int(self.headers.get('Content-Length', ''))
        except ValueError:
            raise RequestError('A valid Content-Length is required.') from None
        if length <= 0:
            raise RequestError('Request body must not be empty.')
        if length > limit:
            raise RequestError('Upload exceeds the size limit.', 'UPLOAD_TOO_LARGE', 413)
        body = self.rfile.read(length)
        if len(body) != length:
            raise RequestError('Request body was truncated.')
        return body

    def _upload(self):
        content_type = self.headers.get_content_type()
        if content_type == 'text/csv':
            return self._body(self.server.max_upload_bytes)
        if content_type != 'multipart/form-data':
            raise RequestError('Send multipart/form-data field file, or text/csv.', 'UNSUPPORTED_SCHEMA', 415)
        body = self._body(self.server.max_upload_bytes + 1024 * 1024)
        header = self.headers.get('Content-Type', '')
        message = BytesParser(policy=policy.default).parsebytes(('Content-Type: ' + header + '\r\nMIME-Version: 1.0\r\n\r\n').encode() + body)
        if not message.is_multipart() or message.defects:
            raise RequestError('Malformed multipart body or missing boundary.')
        parts = list(message.iter_parts())
        if len(parts) != 1 or parts[0].get_param('name', header='content-disposition') != 'file' or parts[0].is_multipart() or parts[0].defects:
            raise RequestError('Send exactly one form-data file field named file.')
        raw = parts[0].get_payload(decode=True)
        if not isinstance(raw, bytes):
            raise RequestError('The file field has no readable content.')
        if len(raw) > self.server.max_upload_bytes:
            raise RequestError('CSV exceeds the upload limit.', 'UPLOAD_TOO_LARGE', 413)
        return raw

    def do_OPTIONS(self):
        if not self._origin_allowed():
            return self._error(RequestError('Origin is not allowed.', 'ORIGIN_NOT_ALLOWED', 403))
        self.reply(204, b'')

    def do_GET(self):
        try:
            if not self._origin_allowed():
                raise RequestError('Origin is not allowed.', 'ORIGIN_NOT_ALLOWED', 403)
            path = urlsplit(self.path).path
            if path == '/api/health':
                settings = self.server.settings_loader()
                return self.reply(200, {'status': 'ok', 'mode': 'local_api', 'model': self.server.analysis.model_status,
                                        'insights': 'configured' if settings.api_key else 'unconfigured', 'provider': 'anthropic',
                                        'model_status_basis': 'last analysis result; demo fixtures do not mark a model ready'})
            if path == '/api/demo':
                return self.reply(200, self.server.analysis.demo())
            if path == '/api/schema':
                return self.reply(200, {'schema_version': '1.0', 'analysis': json.loads((ROOT / 'contracts/analysis-v1.schema.json').read_text()),
                                        'insights': json.loads((ROOT / 'contracts/insights-v1.schema.json').read_text()),
                                        'report': json.loads((ROOT / 'contracts/report-v1.schema.json').read_text()),
                                        'limits': {'max_upload_bytes': self.server.max_upload_bytes, 'max_reports': 100000,
                                                   'max_insight_events': 10, 'analysis_ttl_seconds': self.server.analysis.ttl_seconds}})
            if path.startswith('/api/analyses/') and len(path.split('/')) == 4:
                return self.reply(200, self.server.analysis.get(path.split('/')[-1]))
            parts=path.split('/')
            if len(parts)==6 and parts[1:3]==['api','analyses'] and parts[4]=='reports' and parts[5].endswith('.pdf'):
                self.server.analysis.get(parts[3])
                report=self.server.reports.get(parts[3],parts[5][:-4])
                return self.reply(200,render_pdf(report),'application/pdf',download_name='encounter-report-'+report['report_id'][:12]+'.pdf')
            if path in ASSETS:
                name, mime = ASSETS[path]
                return self.reply(200, (ROOT / 'web' / name).read_bytes(), mime)
            raise RequestError('Route not found.', 'NOT_FOUND', 404)
        except (RequestError, CSVError, AnalysisError, InsightRequestError, ReportError, PDFError) as error:
            self._error(error)
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception:
            self._error(RequestError('Backend failed to process this request; check local integration.', 'INTERNAL_ERROR', 500))

    def do_POST(self):
        self.close_connection = True
        try:
            if not self._origin_allowed():
                raise RequestError('Origin is not allowed.', 'ORIGIN_NOT_ALLOWED', 403)
            path = urlsplit(self.path).path
            if path == '/api/analyses':
                return self.reply(200, self.server.analysis.analyze(self._upload()))
            parts = path.split('/')
            if len(parts)==5 and parts[1:3]==['api','analyses'] and parts[4]=='report':
                if self.headers.get_content_type()!='application/json':
                    raise RequestError('Report requests require application/json.','UNSUPPORTED_SCHEMA',415)
                try:data=json.loads(self._body(1024))
                except (ValueError,UnicodeDecodeError):raise RequestError('Send an empty JSON object for report generation.') from None
                if not isinstance(data,dict) or data:raise RequestError('Send an empty JSON object for report generation.')
                return self.reply(200,self.server.reports.generate(self.server.analysis.get(parts[3])))
            if len(parts) == 5 and parts[1:3] == ['api', 'analyses'] and parts[4] == 'insights':
                if self.headers.get_content_type() != 'application/json':
                    raise RequestError('Insights requests require application/json.', 'UNSUPPORTED_SCHEMA', 415)
                try:
                    data = json.loads(self._body(16 * 1024))
                except (ValueError, UnicodeDecodeError) as error:
                    if isinstance(error, RequestError):
                        raise
                    raise RequestError('Invalid JSON insight request.') from None
                if not isinstance(data, dict) or set(data) != {'event_ids'}:
                    raise RequestError('Send one event_ids array.')
                analysis = self.server.analysis.get(parts[3])
                return self.reply(200, self.server.insights.generate(analysis, data['event_ids']))
            raise RequestError('Route not found.', 'NOT_FOUND', 404)
        except (RequestError, CSVError, AnalysisError, InsightRequestError, ReportError, PDFError) as error:
            self._error(error)
        except (TimeoutError, OSError):
            self._error(RequestError('Request timed out or the connection was interrupted.', 'INVALID_REQUEST', 408))
        except Exception:
            self._error(RequestError('Backend failed to process this request; check local integration.', 'INTERNAL_ERROR', 500))

    def log_message(self, format_string, *args):
        pass


def make_server(host='127.0.0.1', port=8000, analysis_service=None, insights_service=None,
                settings_loader=load_settings, max_upload_bytes=MAX_UPLOAD_BYTES, report_service=None):
    server = ThreadingHTTPServer((host, port), Handler)
    server.analysis = analysis_service or AnalysisService()
    server.insights = insights_service or InsightsService()
    server.reports = report_service or ReportService()
    server.settings_loader, server.max_upload_bytes = settings_loader, max_upload_bytes
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default=os.environ.get('COCONUTS_HOST', '127.0.0.1'))
    parser.add_argument('--port', type=int, default=int(os.environ.get('COCONUTS_PORT', '8000')))
    args = parser.parse_args()
    with make_server(args.host, args.port) as server:
        print('P2 API: http://%s:%s' % (args.host, server.server_port), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
