import contextlib
import csv
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('summary_tool', Path(__file__).with_name('summary.py'))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class SummaryTests(unittest.TestCase):
    def setUp(self):
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name, rows):
        path = self.root / name
        with path.open('w', newline='', encoding='utf-8') as stream:
            csv.writer(stream).writerows(rows)
        return str(path)

    def compare(self, before, after, keys=('id',)):
        return tool.summarize(self.write('before.csv', before), self.write('after.csv', after), keys)

    def test_reordered_equal(self):
        r = self.compare([['id','v'],['a','x'],['b','y']], [['v','id'],['y','b'],['x','a']])
        self.assertTrue(r['equal'])
        self.assertTrue(r['complete'])
        self.assertEqual(r['changed_columns'], [])

    def test_per_column_counts_and_stable_ties(self):
        r = self.compare([['id','z','a'],['x','1','2'],['y','3','4']],
                         [['id','z','a'],['x','11','22'],['y','33','4']])
        self.assertEqual(r['changed_columns'], [{'column':'z','changed_rows':2}, {'column':'a','changed_rows':1}])
        self.assertEqual(r['changed_cells_on_common_columns'], 3)
        self.assertEqual(r['summary']['changed'], 2)
        r = self.compare([['id','z','a'],['x','1','2']], [['id','z','a'],['x','11','22']])
        self.assertEqual([c['column'] for c in r['changed_columns']], ['a','z'])

    def test_added_removed_not_cell_changes(self):
        r = self.compare([['id','v'],['old','secret-before']], [['id','v'],['new','secret-after']])
        self.assertEqual((r['summary']['added'], r['summary']['removed']), (1,1))
        self.assertEqual(r['changed_cells_on_common_columns'], 0)
        self.assertNotIn('secret', json.dumps(r))
        self.assertNotIn('old', json.dumps(r))

    def test_schema_drift_is_not_equality(self):
        r = self.compare([['id','old'],['x','a']], [['id','new'],['x','b']])
        self.assertFalse(r['equal'])
        self.assertTrue(r['complete'])
        self.assertEqual(r['schema'], {'added_columns':['new'],'removed_columns':['old']})
        self.assertEqual(r['summary']['unchanged_on_common_columns'], 1)

    def test_duplicate_groups_unpaired_on_both_sides(self):
        r = self.compare([['id','v'],['x','a'],['x','a'],['y','z']],
                         [['id','v'],['x','b'],['y','z'],['y','z'],['y','z']])
        self.assertFalse(r['complete'])
        self.assertFalse(r['equal'])
        self.assertEqual(r['summary']['ambiguous_keys'], 2)
        self.assertEqual(r['unpaired_records'], {'before':3,'after':4})
        self.assertEqual(r['changed_cells_on_common_columns'], 0)

    def test_duplicate_only_before(self):
        r = self.compare([['id'],['x'],['x']], [['id']])
        self.assertEqual(r['unpaired_records'], {'before':2,'after':0})
        self.assertEqual(r['summary']['removed'], 0)

    def test_composite_key_and_exact_strings(self):
        r = self.compare([['id','part','v'],['x','1','01'],['x','2','a\nb']],
                         [['id','part','v'],['x','1','1'],['x','2','a\nb ']], ('id','part'))
        self.assertTrue(r['complete'])
        self.assertEqual(r['changed_cells_on_common_columns'], 2)

    def test_header_only(self):
        self.assertTrue(self.compare([['id','v']], [['id','v']])['equal'])

    def test_empty_key_keeps_engine_semantics(self):
        r = self.compare([['id','v'],['','a']], [['id','v'],['','b']])
        self.assertTrue(r['complete'])
        self.assertEqual(r['summary']['changed'], 1)

    def test_values_absent_in_all_categories(self):
        before = [['id','v'],['PRIVATE_KEY_A','PRIVATE_OLD'],['PRIVATE_REM','PRIVATE_R'],['PRIVATE_DUP','PRIVATE_D'],['PRIVATE_DUP','PRIVATE_E']]
        after = [['id','v'],['PRIVATE_KEY_A','PRIVATE_NEW'],['PRIVATE_ADD','PRIVATE_A'],['PRIVATE_DUP','PRIVATE_F']]
        r = self.compare(before, after)
        self.assertNotIn('PRIVATE', json.dumps(r))
        self.assertFalse(r['cell_values_included'])

    def test_cli_statuses_and_generic_failure(self):
        before = self.write('before.csv', [['id','v'],['PRIVATE','old']])
        after = self.write('after.csv', [['id','v'],['PRIVATE','new']])
        for candidate, expected in [(before,0),(after,1),(str(self.root/'PRIVATE-missing.csv'),2)]:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = tool.main([before,candidate,'--key','id'])
            self.assertEqual(code, expected)
            self.assertNotIn('PRIVATE', out.getvalue()+err.getvalue())
            if expected == 2:
                self.assertEqual(out.getvalue(), '')

    def test_invalid_keys_and_malformed_rows(self):
        before = self.write('before.csv', [['id','v'],['x','1']])
        malformed = self.write('after.csv', [['id','v'],['PRIVATE']])
        for keys, after in [(('missing',),before), (('id','id'),before), (('id',),malformed)]:
            with self.assertRaises(ValueError):
                tool.summarize(before, after, keys)


if __name__ == '__main__':
    unittest.main()
