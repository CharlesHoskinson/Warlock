"""Fresh fixture regression: exact source, synthetic recorded hierarchy, no reader claim."""
import ast
from pathlib import Path
import unittest


def peer(path):
    return {'app_bus': ':1.171', 'object_path': path}


class NavigationTests(unittest.TestCase):
    def execute(self, initial, outputs, target):
        source = ast.parse(Path(__file__).with_name('run_native.py').read_text())
        function = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'navigate_to')
        current = [peer(initial)]
        called = []
        remaining = iter(outputs)
        def command(name):
            called.append(name)
            current[0] = peer(next(remaining))
        namespace = {'report': {}, 'state': lambda: {'navigator': current[0]}, 'command': command}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<actual-fixture-navigation>', 'exec'), namespace)
        result = namespace['navigate_to']((':1.171', target), 'recorded-peer')
        return result, called, namespace['report']

    def test_recorded_branch_parent_is_exact_row_target(self):
        result, called, _ = self.execute('3836-branch', ['3838-row'], '3838-row')
        self.assertTrue(result)
        self.assertEqual(called, ['MoveToParent'])

    def test_current_target_does_not_navigate_away(self):
        result, called, _ = self.execute('row', [], 'row')
        self.assertTrue(result)
        self.assertEqual(called, [])

    def test_exact_target_reached_after_child_or_sibling(self):
        for outputs, expected in [(['parent', 'target'], 2), (['parent', 'first', 'target'], 3)]:
            result, called, _ = self.execute('old', outputs, 'target')
            self.assertTrue(result)
            self.assertEqual(len(called), expected)

    def test_edge_no_progress_stops_after_one_sibling_command(self):
        result, called, report = self.execute('branch', ['row', 'branch', 'branch'], 'unreachable')
        self.assertFalse(result)
        self.assertEqual(called, ['MoveToParent', 'MoveToFirstChild', 'MoveToNextSibling'])
        self.assertEqual(report['navigatorTrace'][0]['steps'][-1]['stopReason'], 'no progress or repeated peer')

    def test_revisited_peer_cycle_stops(self):
        result, called, _ = self.execute('old', ['parent', 'first', 'second', 'first'], 'unreachable')
        self.assertFalse(result)
        self.assertEqual(len(called), 4)

    def test_distinct_peer_search_remains_bounded(self):
        result, called, report = self.execute('old', ['parent', 'first'] + [str(n) for n in range(180)], 'unreachable')
        self.assertFalse(result)
        self.assertEqual(len(called), 182)
        self.assertEqual(report['navigatorTrace'][0]['steps'][-1]['stopReason'], 'bounded sibling limit')


if __name__ == '__main__':
    unittest.main()
