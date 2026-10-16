#!/usr/bin/env python3
"""Offline round-34 demonstrations, plus one optional bounded public observation."""
import json
from pathlib import Path
import subprocess
import sys


def main():
    results = []
    scratch = Path('test/scratch/gathering34/new')
    scratch.mkdir(parents=True, exist_ok=True)

    def run(name, script, args, expected=0, output=None):
        command = [sys.executable, '-B', script, *map(str, args)]
        p = subprocess.run(command, capture_output=True, text=True, timeout=20)
        results.append({'name': name, 'command': command, 'exit_code': p.returncode,
                        'expected_exit_code': expected, 'passed': p.returncode == expected,
                        'stdout': p.stdout, 'stderr': p.stderr})
        if p.returncode != expected:
            raise RuntimeError(name + ': unexpected exit code')
        if output:
            Path(output).write_text(p.stdout)
        return p.stdout

    live = 'line-1/tools/endpoint-doctor/observed-live.json'
    recent = '2026-10-15T23:03:23.567439Z'
    stale = '2026-10-16T00:02:23.567439Z'
    lens = 'line-1/tools/freshness-lens/freshness_lens.py'
    run('Retained public capture recent at explicit historical time', lens,
        [live, '--at', recent, '--max-age', '300'])
    run('Same successful public capture becomes stale', lens,
        [live, '--at', stale, '--max-age', '300'], 1)
    run('Timestamp budget refused', lens, [live, '--at', stale, '--max-age', '-1'], 2)
    summary = 'line-2/tools/csv-summary/summary.py'
    run('Inventory changes summarized without cells', summary,
        ['line-2/tools/csv-gate/demo-before.csv', 'line-2/tools/csv-gate/demo-after.csv', '--key', 'item'], 1)
    tokens = 'shared/token-read-plan/observed.csv'
    run('Historical real ZTO-first IMD-second rows equal', summary,
        [tokens, tokens, '--key', 'chain_id', '--key', 'token_address', '--key', 'field'])
    run('Insufficient token key remains globally ambiguous', summary,
        [tokens, tokens, '--key', 'token_address'], 1)
    origin = 'line-3/tools/import-origin-trace/origins.py'
    run('Static origin fixture includes unresolved wildcard', origin,
        ['line-3/tools/import-origin-trace/examples', '--json'])
    run('Origin strict mode preserves wildcard limitation', origin,
        ['line-3/tools/import-origin-trace/examples', '--json', '--strict'], 1)
    run('Origin real shared worker source never executed', origin,
        ['shared/import-drift', '--json'])
    run('Origin input budget refuses partial scan', origin,
        ['shared/import-drift', '--json', '--max-files', '1'], 2)
    rehearsal = 'line-4/tools/calldata-rehearsal/calldata_rehearsal.py'
    run('Static unsigned ZTO address argument', rehearsal,
        ['--selector', '0x70a08231', '--types', 'address', '--values', '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e'])
    run('Event schema demo', 'line-4/tools/event-lens/event_lens.py', ['--demo'])
    run('Saved real framing source', 'line-1/tools/framing-lens/framing_lens.py',
        ['line-1/tools/framing-lens/observed-live.json'])
    run('Global slice verdict beyond final window', 'line-2/tools/csv-slice/slice.py',
        ['line-2/tools/csv-gate/demo-before.csv', 'line-2/tools/csv-gate/demo-after.csv',
         '--key', 'item', '--offset', '999'], 1)
    age = 'shared/http-evidence/age_review.py'
    before = 'shared/http-evidence/observed-age-recent34.csv'
    after = 'shared/http-evidence/observed-age-stale34.csv'
    run('Shared recent snapshot', age,
        ['snapshot', live, '--at', recent, '--max-age', '300'], output=before)
    run('Shared stale snapshot retains successful source', age,
        ['snapshot', live, '--at', stale, '--max-age', '300'], 1, after)
    review = json.loads(run('Shared compact exact age change', age,
        ['compare', before, after], 1, 'shared/http-evidence/observed-age-review34.json'))
    assert {r['column'] for r in review['changed_columns']} == {'outcome', 'age_seconds', 'evaluated_at'}
    assert review['complete'] and not review['equal']
    run('Shared equality does not establish recency', age, ['compare', after, after])
    lines = Path(before).read_text().splitlines(keepends=True)
    duplicate = scratch/'duplicate.csv'
    duplicate.write_text(Path(before).read_text()+lines[1])
    ambiguous = json.loads(run('Shared duplicate URL rows never paired', age,
        ['compare', before, duplicate], 1))
    assert not ambiguous['complete'] and ambiguous['unpaired_records'] == {'before': 1, 'after': 2}
    run('Shared unsupported timestamp budget refuses export', age,
        ['snapshot', live, '--at', recent, '--max-age', '-1'], 2)
    report = {'round': 34, 'ok': all(r['passed'] for r in results), 'results': results}
    # Compact evidence to keep every delivered file below 100 KB.
    Path('gathering/new-tool-checks34.json').write_text(json.dumps(report, separators=(',', ':'))+'\n')
    print(json.dumps({'ok': report['ok'], 'checks': len(results)}))


if __name__ == '__main__':
    main()
