import unittest
from pathlib import Path

import origins


ROOT = Path(__file__).parent / 'examples'


class OriginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = origins.analyze(ROOT)
        cls.sites = {(site['module'], site['name']): site for site in cls.result['sites']}

    def test_follows_reexport_alias_to_definition(self):
        site = self.sites['app', 'launch']
        self.assertEqual(site['status'], 'resolved')
        self.assertEqual(site['origins'][0]['module'], 'implementation')
        self.assertEqual(site['origins'][0]['symbol'], 'run')
        self.assertEqual([part['module'] for part in site['chain']],
                         ['app', 'facade', 'implementation'])

    def test_direct_from_import_points_to_definition(self):
        site = self.sites['facade', 'run']
        self.assertEqual(site['origins'][0]['path'], 'implementation.py')
        self.assertEqual(site['origins'][0]['line'], 1)

    def test_wildcard_is_explicitly_unresolved(self):
        site = self.sites['app', '*']
        self.assertEqual(site['reason'], 'wildcard_import')

    def test_analysis_has_source_manifest(self):
        self.assertEqual(self.result['status'], 'complete')
        self.assertEqual(self.result['inventory']['files'], 4)
        self.assertTrue(all(len(item['sha256']) == 64 for item in self.result['inventory']['manifest']))

    def test_reexport_cycle_stops_with_witness(self):
        bindings = {
            ('alpha', 'item'): [{'kind': 'reexport', 'target_module': 'beta',
                                 'target_symbol': 'item'}],
            ('beta', 'item'): [{'kind': 'reexport', 'target_module': 'alpha',
                                'target_symbol': 'item'}],
        }
        result = origins.trace('alpha', 'item', bindings)
        self.assertEqual(result['status'], 'cycle')
        self.assertEqual([(step['module'], step['symbol']) for step in result['chain']],
                         [('alpha', 'item'), ('beta', 'item'), ('alpha', 'item')])

    def test_multiple_bindings_are_not_guessed(self):
        bindings = {('pkg', 'value'): [
            {'kind': 'definition', 'line': 1, 'path': 'pkg.py', 'definition': 'Assign'},
            {'kind': 'definition', 'line': 2, 'path': 'pkg.py', 'definition': 'FunctionDef'},
        ]}
        result = origins.trace('pkg', 'value', bindings)
        self.assertEqual(result['status'], 'ambiguous')


if __name__ == '__main__':
    unittest.main()
