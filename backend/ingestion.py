"""Strict, bounded CSV parsing into the public P3 batch request shape."""
import csv
import hashlib
import io
import math

MAX_UPLOAD_BYTES = 64 * 1024 * 1024
MAX_REPORTS = 100000
REQUIRED_COLUMNS = {'event_id', 'time_to_tca', 'miss_distance'}
TEXT_COLUMNS = {'event_id', 'mission_id', 'c_object_type'}


class CSVError(ValueError):
    def __init__(self, message, details=None, code='INVALID_CSV', total_errors=None):
        super().__init__(message)
        self.code = code
        self.details = details or []
        self.total_errors = len(self.details) if total_errors is None else total_errors


def parse_csv(raw, max_rows=MAX_REPORTS, max_bytes=MAX_UPLOAD_BYTES):
    if not isinstance(raw, bytes) or not raw:
        raise CSVError('Upload a nonempty UTF-8 CSV file.')
    if len(raw) > max_bytes:
        raise CSVError('CSV exceeds the upload limit.', code='UPLOAD_TOO_LARGE')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise CSVError('CSV must be UTF-8 encoded.') from None
    reader = csv.DictReader(io.StringIO(text, newline=''), strict=True)
    try:
        headers = reader.fieldnames
    except csv.Error:
        raise CSVError('Could not parse the CSV header.') from None
    if not headers:
        raise CSVError('CSV has no header.')
    headers = [x.strip() for x in headers]
    if len(headers) > 256 or any(not x or len(x) > 128 for x in headers) or len(set(headers)) != len(headers):
        raise CSVError('CSV headers must be unique, nonempty names (at most 256).', [{'row': 1, 'column': None, 'reason': 'invalid or duplicate header'}])
    missing = sorted(REQUIRED_COLUMNS - set(headers))
    if missing:
        raise CSVError('Missing required CSV columns.', [{'row': 1, 'column': x, 'reason': 'required column missing'} for x in missing])
    reader.fieldnames = headers
    groups, errors, error_count, count = {}, [], 0, 0
    def issue(row, column, reason):
        nonlocal error_count
        error_count += 1
        if len(errors) < 50:
            errors.append({'row': row, 'column': column, 'reason': reason})
    try:
        for row_number, record in enumerate(reader, start=2):
            count += 1
            if count > max_rows:
                raise CSVError('CSV exceeds the report-count limit.', code='UPLOAD_TOO_LARGE')
            before = error_count
            if None in record or any(value is None for value in record.values()):
                issue(row_number, None, 'row has a different number of cells than the header')
                continue
            fields = {}
            for name, value in record.items():
                value = value.strip()
                if name in TEXT_COLUMNS:
                    if name == 'event_id' and (not value or len(value) > 128):
                        issue(row_number, name, 'required nonempty event ID, at most 128 characters')
                    fields[name] = value or None
                    continue
                if not value:
                    fields[name] = None
                    if name in REQUIRED_COLUMNS:
                        issue(row_number, name, 'required numeric value missing')
                    continue
                try:
                    number = float(value)
                    if not math.isfinite(number):
                        raise ValueError()
                    if (name in {'time_to_tca', 'miss_distance', 'relative_speed'} or '_sigma_' in name) and number < 0:
                        raise ValueError()
                    if name == 'time_to_tca' and not math.isfinite(number * 24):
                        raise ValueError()
                    if name == 'risk' and number > 0:
                        raise ValueError()
                    fields[name] = number
                except ValueError:
                    issue(row_number, name, 'expected a finite number in the documented source range')
            if error_count == before:
                event_id = fields['event_id']
                groups.setdefault(event_id, []).append({'report_id': 'row-%s' % row_number, 'fields': fields})
    except csv.Error:
        raise CSVError('Malformed CSV quoting or field size.', [{'row': reader.line_num, 'column': None, 'reason': 'CSV parsing failed'}]) from None
    if error_count:
        raise CSVError('CSV rejected: %s validation error(s); no rows were analyzed.' % error_count, errors, total_errors=error_count)
    if not count:
        raise CSVError('CSV contains a header but no reports.')
    return {'source_sha256': hashlib.sha256(raw).hexdigest(), 'report_count': count,
            'events': [{'event_id': key, 'reports': groups[key]} for key in sorted(groups)]}
