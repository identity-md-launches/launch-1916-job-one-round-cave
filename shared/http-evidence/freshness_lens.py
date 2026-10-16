#!/usr/bin/env python3
"""Evaluate the age of saved public HTTP evidence; never infer current health."""
import argparse
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import re
import sys

# Reuse the existing strict, workspace-confined report loader, without networking.
_spec = importlib.util.spec_from_file_location(
    'freshness_payload_loader', Path(__file__).resolve().parent / 'payload_lens.py')
_loader = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_loader)
SCHEMA = 'freshness-lens/v1'
STAMP = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$')


def timestamp(value):
    if not isinstance(value, str) or not STAMP.fullmatch(value):
        raise ValueError('timestamp must be RFC3339 with seconds and an explicit offset')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return result.astimezone(timezone.utc)


def seconds(value, name):
    if type(value) is not int or not 0 <= value <= 315360000:
        raise ValueError(name + ' must be an integer from 0 to 315360000')
    return value


def analyze(source, at, max_age, future_tolerance=0):
    evaluated = timestamp(at)
    seconds(max_age, 'max_age')
    seconds(future_tolerance, 'future_tolerance')
    if not isinstance(source, dict):
        raise ValueError('report must be an object')
    wrapper = source.get('schema') == 'deadline-sentry/v1'
    prefix = '/probe' if wrapper else ''
    if wrapper and type(source.get('ok')) is not bool:
        raise ValueError('invalid wrapper health')
    if wrapper and 'probe' not in source:
        if source['ok']:
            raise ValueError('successful wrapper lacks probe')
        probe = None
    else:
        probe = source.get('probe') if wrapper else source
        if (not isinstance(probe, dict) or probe.get('schema') != 'endpoint-sentry/v1'
                or type(probe.get('ok')) is not bool):
            raise ValueError('expected Endpoint Sentry or Deadline Sentry report')
        if wrapper and source['ok'] != probe['ok']:
            raise ValueError('wrapper and probe health disagree')
    result = {'schema': SCHEMA, 'outcome': 'unknown',
              'evaluated_at': evaluated.isoformat(), 'max_age_seconds': max_age,
              'future_tolerance_seconds': future_tolerance,
              'source_ok': probe['ok'] if probe else False,
              'evidence': prefix + '/checked_at' if probe else '/probe',
              'limits': ['Age is measured from probe start, not completion or server Date.',
                         'Timestamps and saved reports are unauthenticated clock claims.',
                         'Recent evidence does not establish current endpoint health.',
                         'No request, retry, wait or environment inspection is performed.']}
    if probe is None or probe.get('checked_at') is None:
        result['reason'] = 'No probe start timestamp was retained.'
        return result
    try:
        checked = timestamp(probe['checked_at'])
    except (ValueError, OverflowError):
        result['reason'] = 'Recorded probe start timestamp is malformed or lacks an offset.'
        return result
    age = evaluated - checked
    result['checked_at'] = checked.isoformat()
    result['age_seconds'] = age.total_seconds()
    if age < -timedelta(seconds=future_tolerance):
        result['outcome'] = 'future'
        result['reason'] = 'Probe starts after evaluation time beyond the allowed clock tolerance.'
    elif age > timedelta(seconds=max_age):
        result['outcome'] = 'stale'
        result['reason'] = 'Probe start is older than the declared age budget.'
    else:
        result['outcome'] = 'recent'
        result['reason'] = 'Probe start falls within the declared age and clock budgets.'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('report')
    parser.add_argument('--at', required=True, help='explicit evaluation timestamp, including UTC offset')
    parser.add_argument('--max-age', type=int, required=True, help='age budget in seconds')
    parser.add_argument('--future-tolerance', type=int, default=0, help='explicit clock skew budget in seconds')
    args = parser.parse_args(argv)
    try:
        result = analyze(_loader.load_report(args.report), args.at, args.max_age,
                         args.future_tolerance)
    except (OSError, ValueError, UnicodeError, RecursionError, OverflowError):
        print(json.dumps({'schema': SCHEMA, 'error': 'Invalid input, budget, timestamp or workspace path.'}))
        return 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result['outcome'] == 'recent' else 1


if __name__ == '__main__':
    sys.exit(main())
