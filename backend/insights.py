"""Bounded Anthropic encounter explanations with shared context and citation checks."""
import copy
import hashlib
import http.client
import json
import multiprocessing
import threading
import time
import urllib.error
import urllib.request
from collections import OrderedDict
from .config import load_settings
from .llm_context import (CONTEXT_VERSION, OPERATIONS_BRIEF, ProviderError,
                          build_analysis_context, event_evidence, provider_context, review_options, _statement)

EXPLANATION_SCHEMA = {'type': 'object', 'properties': {'items': {'type': 'array', 'items': {
    'type': 'object', 'properties': {'event_id': {'type': 'string'}, 'next_step_id': {'type': 'string'}},
    'required': ['event_id', 'next_step_id'], 'additionalProperties': False}}},
    'required': ['items'], 'additionalProperties': False}
INSIGHT_PROMPT = OPERATIONS_BRIEF + """
For each encounter, choose ONE eligible review_options option_id as next_step_id. Use the exact assessment, missing measurements and timing context to prioritize the most useful review step. Return every requested event exactly once. Do not invent or rewrite options. Prefer obtaining missing Pc for an unknown assessment, and operations or flight-dynamics review for critical cases. A supplied example Pc is not a missing value."""
_PROVIDER_SLOTS = threading.BoundedSemaphore(2)


class InsightRequestError(ValueError):
    def __init__(self, message, code='INVALID_REQUEST', status=400):
        super().__init__(message)
        self.code, self.status, self.details = code, status, []


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _http_worker(url, data, headers, timeout, channel):
    """Keep blocking DNS/header/body operations in a terminable worker."""
    try:
        request = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.build_opener(_NoRedirect()).open(request, timeout=timeout) as response:
            raw = response.read(1024 * 1024 + 1)
        channel.send((True, raw))
    except urllib.error.HTTPError as error:
        if error.code in {401, 403}:
            message = 'Anthropic rejected the credential or model access. Check your local settings.'
        elif error.code == 429:
            message = 'Anthropic rate limit reached. Retry explicitly later; numeric analysis is still available.'
        else:
            message = 'Anthropic request failed. Check model access and provider availability.'
        error.close()
        channel.send((False, message))
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
        channel.send((False, 'Anthropic timed out or could not be reached. Numeric analysis is still available.'))
    except Exception:
        channel.send((False, 'Anthropic transport failed. Numeric analysis is still available.'))
    finally:
        channel.close()


def _bounded_provider_read(request, timeout):
    # Socket timeouts reset after each read. A spawned process gives the whole
    # exchange a real deadline and lets us stop DNS or slow headers/body too.
    context = multiprocessing.get_context('spawn')
    receive, send = context.Pipe(duplex=False)
    worker = context.Process(target=_http_worker, args=(request.full_url, request.data,
        dict(request.header_items()), timeout, send), daemon=True)
    deadline = time.monotonic() + timeout
    try:
        worker.start()
        send.close()
        remaining = deadline - time.monotonic()
        if remaining <= 0 or not receive.poll(remaining):
            raise ProviderError('Anthropic timed out. Numeric analysis is still available.')
        success, value = receive.recv()
        if not success:
            raise ProviderError(value)
        return value
    except (EOFError, OSError, RuntimeError):
        raise ProviderError('Anthropic transport failed. Numeric analysis is still available.') from None
    finally:
        receive.close()
        send.close()
        if worker.pid is not None:
            if worker.is_alive():
                worker.terminate()
            worker.join(timeout=.2)
            if worker.is_alive():
                worker.kill()
                worker.join(timeout=.2)
            worker.close()


class AnthropicClient:
    def __init__(self, api_key, model, timeout=25, base_url='https://api.anthropic.com'):
        self._api_key, self.model, self.timeout = api_key, model, timeout
        self._base_url = base_url.rstrip('/')
        self.cache_identity = hashlib.sha256((model + '\0' + api_key).encode()).hexdigest()

    def explain(self, events, facts, operations_context):
        return self.generate_structured(INSIGHT_PROMPT,
            provider_context({'task': 'encounter_insights', 'operations_context': operations_context,
             'events': events, 'facts': facts}), EXPLANATION_SCHEMA, max_tokens=2048)

    def generate_structured(self, system, content, schema, max_tokens=4096):
        if not self._api_key:
            raise ProviderError('Add ANTHROPIC_API_KEY to the ignored .env.local file to enable insights.')
        payload = {'model': self.model, 'max_tokens': min(max_tokens, 4096), 'system': system,
                   'messages': [{'role': 'user', 'content': json.dumps(content)}],
                   'output_config': {'format': {'type': 'json_schema', 'schema': schema}}}
        request = urllib.request.Request(self._base_url + '/v1/messages', data=json.dumps(payload).encode(),
                                         headers={'Content-Type': 'application/json', 'x-api-key': self._api_key,
                                                  'anthropic-version': '2023-06-01'}, method='POST')
        try:
            if not _PROVIDER_SLOTS.acquire(blocking=False):
                raise ProviderError('Insight requests are busy; retry explicitly later.')
            try:
                raw = _bounded_provider_read(request, self.timeout)
            finally:
                _PROVIDER_SLOTS.release()
            if len(raw) > 1024 * 1024:
                raise ProviderError('Anthropic response exceeded the response limit.')
            message = json.loads(raw)
            if message.get('stop_reason') != 'end_turn':
                raise ProviderError('Anthropic did not return a complete supported explanation.')
            text = ''.join(x.get('text', '') for x in message.get('content', []) if x.get('type') == 'text')
            return json.loads(text)
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            if isinstance(error, ProviderError):
                raise
            raise ProviderError('Anthropic returned an invalid structured explanation.') from None



def _default_client():
    settings = load_settings()
    return AnthropicClient(settings.api_key, settings.model, settings.timeout)


class InsightsService:
    def __init__(self, client_factory=None, clock=time.monotonic):
        self.client_factory, self.clock = client_factory or _default_client, clock
        self._cache, self._lock = OrderedDict(), threading.RLock()
        self._inflight = threading.BoundedSemaphore(2)

    def generate(self, analysis, event_ids):
        if (not isinstance(event_ids, list) or not 1 <= len(event_ids) <= 10 or
                any(not isinstance(x, str) for x in event_ids) or len(set(event_ids)) != len(event_ids)):
            raise InsightRequestError('Request 1–10 unique event IDs.')
        events = {e['event_id']: e for e in analysis['encounters']}
        if any(x not in events for x in event_ids):
            raise InsightRequestError('An event ID does not belong to this analysis.', 'UNKNOWN_EVENT')
        base = {'schema_version': '1.0', 'analysis_id': analysis['analysis_id'], 'status': 'unavailable', 'items': [], 'warnings': []}
        facts = {}
        evidence = [dict(event_evidence(events[eid], 'event.%s' % i, facts), review_options=review_options(events[eid]))
                    for i, eid in enumerate(event_ids)]
        try:
            client = self.client_factory()
            key = (CONTEXT_VERSION, analysis['analysis_id'], tuple(event_ids), client.cache_identity)
            with self._lock:
                cached = self._cache.get(key)
                if cached and self.clock() - cached[0] < 600:
                    return copy.deepcopy(cached[1])
            if not self._inflight.acquire(blocking=False):
                raise ProviderError('Insight requests are busy; retry explicitly later.')
            try:
                selected = client.explain(evidence, facts, build_analysis_context(analysis))
            finally:
                self._inflight.release()
            if not isinstance(selected, dict) or set(selected) != {'items'} or not isinstance(selected['items'], list):
                raise ProviderError('Unsupported insight response shape.')
            mapping = {}
            for item in selected['items']:
                if not isinstance(item, dict) or set(item) != {'event_id', 'next_step_id'}:
                    raise ProviderError('Unsupported insight response item.')
                eid = item['event_id']
                if not isinstance(eid, str) or eid not in event_ids or eid in mapping:
                    raise ProviderError('Insight output referenced an unknown or duplicate event.')
                choices = {option['option_id']: option for option in evidence[event_ids.index(eid)]['review_options']}
                if not isinstance(item['next_step_id'], str) or item['next_step_id'] not in choices:
                    raise ProviderError('Insight proposed an ineligible review step.')
                mapping[eid] = choices[item['next_step_id']]
            if set(mapping) != set(event_ids):
                raise ProviderError('Insight output omitted a requested encounter.')
            items = []
            for eid in event_ids:
                option = mapping[eid]
                event_context = evidence[event_ids.index(eid)]
                baseline_refs = [event_context['fact_ids'][field] for field in
                                 ['severity', 'predicted_pc', 'miss_distance_m', 'time_to_tca_hours', 'flag_reasons']+option['fact_fields']]
                statement = _statement({'text': event_context['reference_assessment']+' '+option['text'],
                                        'fact_ids': list(dict.fromkeys(baseline_refs))}, facts, eid, limit=1200)
                refs = sorted({facts[key]['field'] for key in statement['fact_ids']})
                limitations = ['Pc estimates and configured assessment tiers are not observed collision outcomes or operational clearance.']
                if analysis['source']['mode'] == 'synthetic_demo':
                    limitations.append('Synthetic demo values; not observed telemetry or trained predictions.')
                if events[eid]['prediction_status'] == 'unavailable':
                    limitations.append('The trained prediction is unavailable for this encounter.')
                items.append({'event_id': eid, 'summary': statement['text'],
                              'fact_refs': [{'event_id': eid, 'field': field} for field in refs], 'limitations': limitations})
            result = dict(base, status='ready', items=items)
            with self._lock:
                self._cache[key] = (self.clock(), copy.deepcopy(result))
                while len(self._cache) > 64:
                    self._cache.popitem(last=False)
            return result
        except ProviderError as error:
            return dict(base, warnings=[str(error)])
