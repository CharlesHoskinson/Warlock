#!/usr/bin/env python3
"""Root protected controls: retain all16 prior tests and exercise actual nested source."""
import ast
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

source = Path(__file__).with_name('test_classifier_refusal.py')
spec = importlib.util.spec_from_file_location('prior_refusal_controls', source)
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)

class DiagnosticPriority(prior.ClassifierRefusal):
    def production_process_maps(self):
        tree = ast.parse(Path(prior.args.launcher).read_text())
        selected = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                    and node.name == 'process_maps']
        self.assertEqual(len(selected), 1)
        module = ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[]))
        namespace = dict(vars(prior.l))
        namespace.update(
            current=Mock(), context={'base': self.base, 'collector': self.collector,
                                     'current': object(), 'foundation': {'graphics': {'devices': {}}}},
            assets={'opener': {'sha256': 'a' * 64, 'path': '/owned/opener'}},
            clock=self.clock, output=self.root, receipt=self.receipt,
            packet={'processInventory': {}}, lease=object(), endpoint={},
            missing_named_mappings=Mock(return_value={}),
            owned_feedback_mappings=Mock(return_value=({'checked': True}, {'qualification': 'fixture-only'})))
        exec(compile(module, str(prior.args.launcher), 'exec'), namespace)
        return namespace['process_maps'], namespace

    def real_snapshot(self, base, proc, clock, **kwargs):
        with patch.object(prior.c, 'Path', side_effect=lambda *parts: self.root):
            return prior.c.generated_snapshot(base, proc, clock, **kwargs)

    def test_preparatory_census_cannot_mask_classifier_exception(self):
        self.collector.failure_census_context.side_effect = ValueError('diagnostic census mismatch')
        self.collector.generated_snapshot = Mock(side_effect=self.real_snapshot)
        process, namespace = self.production_process_maps()
        with patch.object(prior.c, 'classify_generated_snapshot', side_effect=self.original):
            with patch.object(prior.l, 'opener_refusal_fd_diagnostics') as fd_reads:
                with self.assertRaises(ValueError) as caught:
                    process('opener', self.proc, 42, ['/owned/opener'], asset_role='opener')
        self.assertIs(caught.exception, self.original)
        self.collector.generated_snapshot.assert_called_once()
        namespace['current'].assert_called_once()
        fd_reads.assert_not_called()
        item = self.receipt['openerClassifierRefusal']
        self.assertEqual(item['originalSnapshot']['rows'], self.rows)
        self.assertEqual(Path(item['originalSnapshot']['raw']['path']).read_bytes(), prior.RAW)
        self.assertFalse(item['ownedAcrossCapture'])

    def test_preparatory_census_cannot_change_successful_classifier_route(self):
        self.collector.failure_census_context.side_effect = ValueError('diagnostic census mismatch')
        self.collector.generated_snapshot = Mock(return_value=(self.rows, None, 'fixture-hash'))
        process, namespace = self.production_process_maps()
        result = process('opener', self.proc, 42, ['/owned/opener'], asset_role='opener')
        self.assertEqual(result, {'checked': True})
        self.assertNotIn('openerClassifierRefusal', self.receipt)
        namespace['owned_feedback_mappings'].assert_called_once()
        self.assertEqual(self.base.check_process.call_count, 2)

    def test_raw_file_retained_when_strict_diagnostic_identity_fails(self):
        self.collector.failure_census_context.side_effect = ValueError('foreign diagnostic scope')
        with patch.object(prior.l, 'opener_refusal_fd_diagnostics') as fd_reads:
            self.capture()
        item = self.receipt['openerClassifierRefusal']
        self.assertEqual(Path(item['originalSnapshot']['raw']['path']).read_bytes(), prior.RAW)
        self.assertFalse(item['ownedAcrossCapture'])
        self.assertIn('foreign diagnostic scope', item['captureError'])
        fd_reads.assert_not_called()

    def test_raw_file_retained_when_diagnostic_deadline_check_fails(self):
        self.base.left.side_effect = TimeoutError('original deadline')
        with patch.object(prior.l, 'opener_refusal_fd_diagnostics') as fd_reads:
            self.capture()
        item = self.receipt['openerClassifierRefusal']
        self.assertEqual(Path(item['originalSnapshot']['raw']['path']).read_bytes(), prior.RAW)
        self.assertFalse(item['ownedAcrossCapture'])
        self.assertIn('TimeoutError', item['captureError'])
        fd_reads.assert_not_called()

    def test_missing_pre_snapshot_identity_never_grants_fd_reads(self):
        self.collector.failure_census_context.return_value = prior.IDENTITY.copy()
        with patch.object(prior.l, 'opener_refusal_fd_diagnostics') as fd_reads:
            prior.l.capture_opener_classifier_refusal(
                self.collector, self.base, self.proc, 42, 'a' * 64, self.clock,
                self.root, self.receipt, None, prior.RAW, self.rows, {}, self.original)
        fd_reads.assert_not_called()
        item = self.receipt['openerClassifierRefusal']
        self.assertEqual(Path(item['originalSnapshot']['raw']['path']).read_bytes(), prior.RAW)
        self.assertFalse(item['ownedAcrossCapture'])
        self.assertIsNone(item['identityBeforeSnapshot'])

if __name__ == '__main__':
    unittest.main(argv=[__file__] + prior.remaining if hasattr(prior, 'remaining') else [__file__])
