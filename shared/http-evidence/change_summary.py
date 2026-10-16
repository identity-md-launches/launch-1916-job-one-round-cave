#!/usr/bin/env python3
"""Summarize exact CSV differences without emitting data-cell values."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys


def load_engine():
    source = Path(__file__).resolve().parent / 'reconcile.py'
    spec = importlib.util.spec_from_file_location('csv_summary_engine', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


engine = load_engine()


def summarize(before, after, keys):
    """Compute fresh evidence; never accept an externally supplied report."""
    result = engine.reconcile(before, after, keys)
    counts = {}
    for row in result['changed']:
        for column in row['fields']:
            counts[column] = counts.get(column, 0) + 1
    ambiguous_before = sum(len(group['before']) for group in result['ambiguous'])
    ambiguous_after = sum(len(group['after']) for group in result['ambiguous'])
    return {
        'format': 'csv-summary/v1',
        'equal': result['equal'],
        'complete': result['complete'],
        'keys': result['keys'],
        'schema': result['schema'],
        'summary': result['summary'],
        'changed_cells_on_common_columns': sum(counts.values()),
        'changed_columns': [
            {'column': column, 'changed_rows': counts[column]}
            for column in sorted(counts, key=lambda c: (-counts[c], c))
        ],
        'unpaired_records': {'before': ambiguous_before, 'after': ambiguous_after},
        'cell_values_included': False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before')
    parser.add_argument('after')
    parser.add_argument('--key', action='append', required=True)
    args = parser.parse_args(argv)
    try:
        report = summarize(args.before, args.after, args.key)
    except (ValueError, OSError):
        # Parser/OS exceptions can contain a filename or malformed CSV content.
        # Keep this command's diagnostics value-free as well as its stdout.
        print(json.dumps({'error': 'Cannot compare inputs; check workspace-local CSVs and distinct key columns.'}), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2))
    return 0 if report['equal'] else 1


if __name__ == '__main__':
    sys.exit(main())
