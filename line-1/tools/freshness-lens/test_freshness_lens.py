import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('freshness', Path(__file__).with_name('freshness_lens.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.report = {'schema': 'endpoint-sentry/v1', 'ok': True,
                       'checked_at': '2026-10-16T00:00:00Z'}

    def check(self, at, age=60, tolerance=0):
        return m.analyze(self.report, at, age, tolerance)

    def test_recent(self):
        self.assertEqual(self.check('2026-10-16T00:00:30Z')['outcome'], 'recent')

    def test_age_boundary(self):
        self.assertEqual(self.check('2026-10-16T00:01:00Z')['outcome'], 'recent')
        self.assertEqual(self.check('2026-10-16T00:01:00.000001Z')['outcome'], 'stale')

    def test_zero_budget(self):
        self.assertEqual(self.check('2026-10-16T00:00:00Z', 0)['outcome'], 'recent')
        self.assertEqual(self.check('2026-10-16T00:00:01Z', 0)['outcome'], 'stale')

    def test_future(self):
        self.assertEqual(self.check('2026-10-15T23:59:59Z')['outcome'], 'future')

    def test_future_tolerance_boundary(self):
        self.assertEqual(self.check('2026-10-15T23:59:59Z', tolerance=1)['outcome'], 'recent')
        self.assertEqual(self.check('2026-10-15T23:59:58.999999Z', tolerance=1)['outcome'], 'future')

    def test_equivalent_offset(self):
        self.assertEqual(self.check('2026-10-16T08:00:00+08:00')['age_seconds'], 0)

    def test_failed_probe_can_be_recent(self):
        self.report['ok'] = False
        result = self.check('2026-10-16T00:00:01Z')
        self.assertEqual(result['outcome'], 'recent')
        self.assertFalse(result['source_ok'])

    def test_missing_timestamp(self):
        del self.report['checked_at']
        self.assertEqual(self.check('2026-10-16T00:00:00Z')['outcome'], 'unknown')

    def test_malformed_recorded_timestamp(self):
        for value in [True, 42, '2026-10-16T00:00:00', '2026-02-30T00:00:00Z', 'bad']:
            self.report['checked_at'] = value
            self.assertEqual(self.check('2026-10-16T00:00:00Z')['outcome'], 'unknown')

    def test_invalid_evaluation(self):
        for value in ['bad', '2026-10-16', '2026-10-16T00:00:00', None]:
            with self.assertRaises(ValueError): self.check(value)

    def test_budgets(self):
        for value in [-1, True, 1.5, 315360001]:
            with self.assertRaises(ValueError): self.check('2026-10-16T00:00:00Z', value)
            with self.assertRaises(ValueError): self.check('2026-10-16T00:00:00Z', tolerance=value)

    def test_wrapper(self):
        self.report = {'schema':'deadline-sentry/v1', 'ok':True, 'probe':self.report}
        self.assertEqual(self.check('2026-10-16T00:00:00Z')['evidence'], '/probe/checked_at')
        self.report['ok'] = False
        with self.assertRaises(ValueError): self.check('2026-10-16T00:00:00Z')

    def test_watchdog_without_probe(self):
        self.report = {'schema':'deadline-sentry/v1', 'ok':False}
        self.assertEqual(self.check('2026-10-16T00:00:00Z')['outcome'], 'unknown')
        self.report['ok'] = True
        with self.assertRaises(ValueError): self.check('2026-10-16T00:00:00Z')

    def test_no_mutation(self):
        before = copy.deepcopy(self.report)
        self.check('2026-10-16T00:00:00Z')
        self.assertEqual(self.report, before)

    def test_invalid_schema_and_health(self):
        for report in [[], {}, {'schema':'other', 'ok':True},
                       {'schema':'endpoint-sentry/v1', 'ok':1}]:
            with self.assertRaises(ValueError):
                m.analyze(report, '2026-10-16T00:00:00Z', 60)

    def test_real_capture(self):
        path = Path('line-1/tools/endpoint-doctor/observed-live.json')
        result = m.analyze(m._loader.load_report(path), '2026-10-16T00:02:23.567439Z', 300)
        self.assertEqual(result['outcome'], 'stale')
        self.assertEqual(result['age_seconds'], 3600)

    def test_loader_rejects_duplicate_and_nonfinite(self):
        for raw in [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":1e999}']:
            with self.assertRaises(ValueError): m._loader.strict_json(raw)

    def test_loader_refuses_outside_workspace(self):
        with self.assertRaises(ValueError): m._loader.load_report('../outside-report.json')

if __name__ == '__main__':
    unittest.main()
