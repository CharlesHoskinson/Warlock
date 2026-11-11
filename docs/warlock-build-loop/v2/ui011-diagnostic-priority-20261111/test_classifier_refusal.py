#!/usr/bin/env python3
"""Protected Root CPU controls. No GUI, loader, signal, input or native execution."""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

parser = argparse.ArgumentParser()
parser.add_argument('--collector', required=True)
parser.add_argument('--launcher', required=True)
args, remaining = parser.parse_known_args()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

c = load('refusal_collector', args.collector)
l = load('refusal_launcher', args.launcher)
RAW = b'1000-2000 r--p 00000000 00:01 55 /memfd:unknown (deleted)\n'
IDENTITY = {'pid': 123, 'birth': 42, 'uid': 1000, 'image': 'a' * 64,
            'namespaces': {'pid': 'pid:[1]', 'mnt': 'mnt:[1]', 'user': 'user:[1]', 'net': 'net:[1]'},
            'cgroup': 'owned', 'executableLink': '/owned/opener'}

class ClassifierRefusal(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'maps').write_bytes(RAW)
        self.base = SimpleNamespace(left=Mock(return_value=1), check_process=Mock())
        self.proc = SimpleNamespace(pid=123)
        self.clock = {'deadline': 999}
        self.rows = c.parse_complete_maps(RAW)
        self.receipt = {}
        self.collector = SimpleNamespace(failure_census_context=Mock(return_value=copy.deepcopy(IDENTITY)),
                                         MAPS_CAP=c.MAPS_CAP)
        self.original = ValueError('original classifier refusal')

    def snapshot(self, callback):
        with patch.object(c, 'Path', side_effect=lambda *parts: self.root):
            return c.generated_snapshot(self.base, self.proc, self.clock,
                                        on_classifier_refusal=callback)

    def capture(self):
        return l.capture_opener_classifier_refusal(
            self.collector, self.base, self.proc, 42, 'a' * 64, self.clock,
            self.root, self.receipt, copy.deepcopy(IDENTITY), RAW,
            copy.deepcopy(self.rows), {}, self.original)

    def test_exact_original_raw_rows_links_reach_callback(self):
        calls = []
        with self.assertRaisesRegex(ValueError, 'other memfd'):
            self.snapshot(lambda *values: calls.append(values))
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][:3], (RAW, self.rows, {}))
        self.assertIsInstance(calls[0][3], ValueError)

    def test_callback_failure_does_not_replace_original(self):
        with patch.object(c, 'classify_generated_snapshot', side_effect=self.original):
            with self.assertRaises(ValueError) as caught:
                self.snapshot(Mock(side_effect=RuntimeError('diagnostic failure')))
        self.assertIs(caught.exception, self.original)

    def test_no_callback_on_success(self):
        (self.root / 'maps').write_bytes(b'1000-2000 rw-p 00000000 00:00 0 [heap]\n')
        callback = Mock()
        rows, generated, sha = self.snapshot(callback)
        callback.assert_not_called()
        self.assertIsNone(generated)
        self.assertEqual(sha, hashlib.sha256((self.root / 'maps').read_bytes()).hexdigest())
        self.assertEqual(len(rows), 1)

    def test_parse_error_is_not_mislabeled_classifier_input(self):
        (self.root / 'maps').write_bytes(b'not kernel maps\n')
        callback = Mock()
        with self.assertRaises(ValueError):
            self.snapshot(callback)
        callback.assert_not_called()

    def test_timeout_before_classifier_has_no_capture(self):
        self.base.left.side_effect = TimeoutError('original deadline')
        callback = Mock()
        with self.assertRaises(TimeoutError):
            self.snapshot(callback)
        callback.assert_not_called()

    def test_capture_retains_exact_raw_and_private_mode(self):
        with patch.object(l, 'opener_refusal_fd_diagnostics', return_value={'complete': True, 'entries': []}):
            self.capture()
        item = self.receipt['openerClassifierRefusal']
        raw_path = Path(item['originalSnapshot']['raw']['path'])
        self.assertEqual(raw_path.read_bytes(), RAW)
        self.assertEqual(raw_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(item['originalSnapshot']['rows'], self.rows)
        self.assertEqual(item['originalSnapshot']['links'], {})
        self.assertFalse(item['qualification'])
        self.assertFalse(item['creatorAttested'])
        self.assertEqual(item['originalError']['message'], str(self.original))

    def test_foreign_birth_blocks_later_fd_reads(self):
        self.collector.failure_census_context.side_effect = ValueError('foreign birth')
        with patch.object(l, 'opener_refusal_fd_diagnostics') as scan:
            self.capture()
        scan.assert_not_called()
        item = self.receipt['openerClassifierRefusal']
        self.assertFalse(item['ownedAcrossCapture'])
        self.assertIn('foreign birth', item['captureError'])
        self.assertEqual(item['originalSnapshot']['rows'], self.rows)

    def test_timeout_is_recorded_without_replacing_original(self):
        self.base.left.side_effect = TimeoutError('original deadline')
        with patch.object(l, 'opener_refusal_fd_diagnostics') as scan:
            self.capture()
        scan.assert_not_called()
        self.assertIn('TimeoutError', self.receipt['openerClassifierRefusal']['captureError'])
        self.assertEqual(self.receipt['openerClassifierRefusal']['originalError']['message'], str(self.original))

    def test_inaccessible_fd_evidence_remains_unknown(self):
        with patch.object(l, 'opener_refusal_fd_diagnostics', return_value={
                'complete': False, 'error': 'PermissionError', 'entries': [], 'origin': 'unknown'}):
            self.capture()
        item = self.receipt['openerClassifierRefusal']
        self.assertFalse(item['laterFdDiagnostics']['complete'])
        self.assertEqual(item['laterFdDiagnostics']['origin'], 'unknown')
        self.assertFalse(item['qualification'])

    def test_changed_after_identity_is_not_attested(self):
        changed = dict(IDENTITY, birth=43)
        self.collector.failure_census_context.side_effect = [copy.deepcopy(IDENTITY), changed]
        with patch.object(l, 'opener_refusal_fd_diagnostics', return_value={'complete': True, 'entries': []}):
            self.capture()
        self.assertFalse(self.receipt['openerClassifierRefusal']['ownedAcrossCapture'])

    def test_existing_capture_file_is_not_overwritten(self):
        path = self.root / 'opener-classifier-refusal.maps'
        path.write_bytes(b'previous')
        with patch.object(l, 'opener_refusal_fd_diagnostics', return_value={}):
            self.capture()
        self.assertEqual(path.read_bytes(), b'previous')
        self.assertIn('FileExistsError', self.receipt['openerClassifierRefusal']['captureError'])

    def test_fd_directory_refusal_is_bounded_unknown(self):
        with patch.object(l.os, 'scandir', side_effect=PermissionError('not accessible')):
            result = l.opener_refusal_fd_diagnostics(self.base, self.proc, self.clock, self.rows)
        self.assertFalse(result['complete'])
        self.assertIn('PermissionError', result['error'])
        self.assertEqual(result['origin'], 'unknown')

    def test_no_fd_body_read_or_process_mutation(self):
        tree = ast.parse(Path(args.launcher).read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'opener_refusal_fd_diagnostics')
        calls = {ast.unparse(node.func) for node in ast.walk(function) if isinstance(node, ast.Call)}
        for forbidden in ('os.read', 'os.pread', 'os.write', 'os.kill', 'subprocess.run', 'subprocess.Popen'):
            self.assertNotIn(forbidden, calls)
        self.assertIn('os.close', calls)

    def test_original_limits_and_classifier_unchanged(self):
        here = Path(__file__).parent
        baseline = ast.parse((here / 'preimages/run_labwc_gl_foundation_window_rule_20261108.py').read_text())
        current = ast.parse(Path(args.collector).read_text())
        for name in ('parse_complete_maps', 'classify_generated_snapshot', 'strict_snapshot_files'):
            first = next(node for node in baseline.body if isinstance(node, ast.FunctionDef) and node.name == name)
            second = next(node for node in current.body if isinstance(node, ast.FunctionDef) and node.name == name)
            self.assertEqual(ast.dump(first, include_attributes=False), ast.dump(second, include_attributes=False))
        self.assertEqual(l.JOURNEY_NS, 28_000_000_000)
        self.assertEqual(l.CLEANUP_NS, 2_000_000_000)

    def test_callback_issued_only_for_opener(self):
        source = Path(args.launcher).read_text()
        self.assertIn("if role == 'opener':", source)
        self.assertIn('on_classifier_refusal=on_refusal', source)
        self.assertIn('capture_opener_classifier_refusal(', source)

    def test_exact_rows_not_later_maps_reread(self):
        tree = ast.parse(Path(args.launcher).read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'capture_opener_classifier_refusal')
        calls = {ast.unparse(node.func) for node in ast.walk(function) if isinstance(node, ast.Call)}
        self.assertNotIn('collector.generated_snapshot', calls)
        self.assertNotIn('base.mapped', calls)

if __name__ == '__main__':
    unittest.main(argv=[__file__] + remaining)
