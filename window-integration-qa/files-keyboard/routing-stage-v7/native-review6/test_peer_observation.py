"""Exact observer boundary using the retained same-name counterexample; no reader claim."""
import ast
import copy
import json
from pathlib import Path
import unittest


R = Path(__file__).resolve().parent
recorded = json.loads((R / 'diagnosis/recent-peer-mismatch.json').read_text())['capturedRequestAndWrongObservation']


def matcher():
    source = ast.parse((R / 'run_native.py').read_text())
    method = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'reader_peer_matches')
    namespace = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<actual-observer-match>', 'exec'), namespace)
    return namespace['reader_peer_matches']


class PeerTests(unittest.TestCase):
    def target(self):
        result = copy.deepcopy(recorded['observed'])
        result['objectName'] = 'Dashboard.rr'
        return result

    def recent_peer(self):
        target = self.target()
        return {'name': target['name'], 'description': target['description'], 'role': 'list item',
                'identity': 'QGuiApplication.ProxiedWindow.Dashboard.rr', 'app_bus': ':1.176',
                'object_path': '/diagnostic-current-recent-peer'}

    def test_recorded_same_name_media_peer_refused(self):
        stale = copy.deepcopy(recorded['readerFocus']['focus'])
        stale['description'] = self.target()['description']
        self.assertFalse(matcher()(stale, self.target()))

    def test_role_suffix_and_description_independently_required(self):
        for key, changed in [('role', 'button'), ('identity', 'QGuiApplication.ProxiedWindow.Dashboard.mt'),
                             ('identity', 'prefixNotDashboard.rr'), ('description', '/different/logical/path'),
                             ('name', 'different name'), ('object_path', None), ('app_bus', None)]:
            current = self.recent_peer()
            current[key] = changed
            self.assertFalse(matcher()(current, self.target()), key)

    def test_supported_exact_peer_matches(self):
        self.assertTrue(matcher()(self.recent_peer(), self.target()))

    def test_unsupported_role_and_incomplete_peer_refuse(self):
        target = self.target()
        target['role'] = 999
        current = self.recent_peer()
        current['role'] = None
        self.assertFalse(matcher()(current, target))
        self.assertFalse(matcher()({}, self.target()))

    def test_actual_wait_records_mismatch_until_correct_peer_arrives(self):
        tree = ast.parse((R / 'run_native.py').read_text())
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ['reader_peer_matches', 'reader_target']]
        stale = copy.deepcopy(recorded['readerFocus']['focus'])
        stale['description'] = self.target()['description']
        observations = iter([{'focus': stale}, {'focus': self.recent_peer()}])
        def wait(function, label):
            return function() or function()
        namespace = {'state': lambda: next(observations), 'wait': wait, 'report': {}}
        exec(compile(ast.Module(body=functions, type_ignores=[]), '<actual-observer-wait>', 'exec'), namespace)
        result = namespace['reader_target'](self.target())
        self.assertEqual(result['focus']['identity'], 'QGuiApplication.ProxiedWindow.Dashboard.rr')
        entries = namespace['report']['peerObservationTrace'][0]['observations']
        self.assertEqual([e['matches'] for e in entries], [False, True])


if __name__ == '__main__':
    unittest.main()
