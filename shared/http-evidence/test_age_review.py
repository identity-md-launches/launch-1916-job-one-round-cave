"""Behavioral checks for timestamp evidence carried into exact CSV summaries."""
import contextlib
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

import age_review as tool

LIVE = 'line-1/tools/endpoint-doctor/observed-live.json'
RECENT = '2026-10-15T23:03:23.567439Z'
STALE = '2026-10-16T00:02:23.567439Z'


class AgeReviewTests(unittest.TestCase):
    def setUp(self):
        Path('test/scratch').mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(dir='test/scratch')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def save(self, name, text):
        path = self.root / name
        path.write_text(text)
        return path

    def test_saved_success_ages_without_changing_health_or_source(self):
        before, recent = tool.snapshot(LIVE, RECENT, 300)
        after, stale = tool.snapshot(LIVE, STALE, 300)
        self.assertEqual((recent['outcome'], stale['outcome']), ('recent', 'stale'))
        self.assertTrue(stale['source_ok'])
        b, a = list(csv.DictReader(io.StringIO(before)))[0], list(csv.DictReader(io.StringIO(after)))[0]
        self.assertEqual(b['report_sha256'], a['report_sha256'])
        result = tool.compare(self.save('b.csv', before), self.save('a.csv', after))
        self.assertFalse(result['equal'])
        self.assertTrue(result['complete'])
        self.assertEqual({r['column'] for r in result['changed_columns']},
                         {'outcome', 'age_seconds', 'evaluated_at'})
        self.assertNotIn(b['url'], json.dumps(result))
        self.assertFalse(result['cell_values_included'])

    def test_duplicate_urls_remain_ambiguous_even_if_identical(self):
        text, _ = tool.snapshot(LIVE, RECENT, 300)
        rows = text.splitlines(keepends=True)
        a = self.save('a.csv', text)
        b = self.save('b.csv', text + rows[1])
        result = tool.compare(a, b)
        self.assertFalse(result['complete'])
        self.assertEqual(result['unpaired_records'], {'before': 1, 'after': 2})

    def test_unknown_timestamp_is_retained_not_zero(self):
        source = json.loads(Path(LIVE).read_text())
        source.get('probe', source).pop('checked_at')
        text, result = tool.snapshot(self.save('missing.json', json.dumps(source)), RECENT, 300)
        self.assertEqual(result['outcome'], 'unknown')
        row = next(csv.DictReader(io.StringIO(text)))
        self.assertEqual(row['age_seconds'], '')
        self.assertEqual(row['checked_at'], '')

    def test_future_and_failed_but_recent_are_distinct(self):
        _, future = tool.snapshot(LIVE, '2020-01-01T00:00:00Z', 300)
        self.assertEqual(future['outcome'], 'future')
        source = json.loads(Path(LIVE).read_text())
        source['ok'] = False
        source.get('probe', source)['ok'] = False
        text, result = tool.snapshot(self.save('failed.json', json.dumps(source)), RECENT, 300)
        self.assertEqual(result['outcome'], 'recent')
        self.assertEqual(next(csv.DictReader(io.StringIO(text)))['source_ok'], 'false')

    def test_equal_stale_snapshots_are_equal_not_healthy(self):
        text, _ = tool.snapshot(LIVE, STALE, 300)
        path = self.save('stale.csv', text)
        self.assertTrue(tool.compare(path, path)['equal'])

    def test_refusals_emit_no_partial_stdout(self):
        for args in [
            ['snapshot', LIVE, '--at', RECENT, '--max-age', '-1'],
            ['snapshot', str(self.save('duplicate.json', '{"ok":true,"ok":false}')),
             '--at', RECENT, '--max-age', '300'],
            ['snapshot', str(self.save('watchdog.json', '{"schema":"deadline-sentry/v1","ok":false}')),
             '--at', RECENT, '--max-age', '300'],
            ['compare', str(self.save('bad.csv', 'url\nhttps://example.org\n')),
             str(self.root/'bad.csv')]]:
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(tool.main(args), 2)
            self.assertEqual(out.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
