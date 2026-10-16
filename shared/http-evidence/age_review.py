#!/usr/bin/env python3
"""Export saved probe age evidence and summarize exact changes without cell values."""
import argparse
import csv
import io
import json
import sys

import change_summary
import freshness_lens
import payload_contract
import reconcile

COLUMNS = ('url', 'outcome', 'source_ok', 'checked_at', 'evaluated_at',
           'age_seconds', 'max_age_seconds', 'future_tolerance_seconds',
           'evidence', 'report_sha256')
NOTICE = ('Saved timestamp claims only; recent does not establish endpoint health. '
          'Summary omits data cells, but exposes column names, counts and schema. '
          'Identical stale snapshots can compare equal. No network or writes.')


def snapshot(path, at, max_age, future_tolerance=0):
    source, digest = payload_contract.load_source(path)
    judgment = freshness_lens.analyze(source, at, max_age, future_tolerance)
    url, _ = payload_contract.source_url(source)
    row = {key: judgment.get(key, '') for key in COLUMNS}
    row.update(url=url, source_ok=str(judgment['source_ok']).lower(),
               report_sha256=digest)
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerow(row)
    return output.getvalue(), judgment


def compare(before, after):
    # Validate the projection, never pretend CSV is authenticated source evidence.
    for path in (before, after):
        header, groups, count = reconcile.load_table(path, ['url'])
        if header != list(COLUMNS) or not count:
            raise ValueError('nonempty age snapshots with exact headers required')
        for key in groups:
            payload_contract.source_url({'url': key[0]})
    return dict(change_summary.summarize(before, after, ['url']),
                handoff='http-age-review/v1', scope=NOTICE)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest='command', required=True)
    snap = sub.add_parser('snapshot')
    snap.add_argument('report')
    snap.add_argument('--at', required=True)
    snap.add_argument('--max-age', type=int, required=True)
    snap.add_argument('--future-tolerance', type=int, default=0)
    diff = sub.add_parser('compare')
    diff.add_argument('before')
    diff.add_argument('after')
    args = parser.parse_args(argv)
    try:
        if args.command == 'snapshot':
            output, result = snapshot(args.report, args.at, args.max_age, args.future_tolerance)
            code = int(result['outcome'] != 'recent')
        else:
            result = compare(args.before, args.after)
            output = json.dumps(result, indent=2, ensure_ascii=True) + '\n'
            code = int(not result['equal'])
    except (ValueError, OSError, TypeError, KeyError, OverflowError, RecursionError):
        print(json.dumps({'error': 'Invalid workspace evidence, age options or snapshot schema.'}),
              file=sys.stderr)
        return 2
    sys.stdout.write(output)
    return code


if __name__ == '__main__':
    sys.exit(main())
