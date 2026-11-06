"""Last-spawn delivery checks retain the frozen native supervisor."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import test_loop as baseline

loop = baseline.loop


class DeliveryLaunchGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '.warlock-contributor').mkdir()
        (self.root / '.warlock-contributor/.records.lock').touch()
        self.checker = Mock()
        self.checker.safe.side_effect = lambda root, name: root / name
        self.checker.open_parent.side_effect = lambda path, create: (os.open(path.parent, os.O_RDONLY), path.name)
        self.checker.context.return_value = ({}, {})
        self.checker.read.return_value = {'workflowPolicy': 2}
        self.command = ['reviewed', '--fixed']
        self.checker.validate_execution_precheck.return_value = {
            'nextRootAction': {'argv': self.command, 'candidateSha256': 'a' * 64}}
        self.record = '.warlock-contributor/slice.json'

    def guard(self, spawn):
        with patch.object(loop, 'contributor_module', return_value=self.checker):
            return loop.guarded_delivery_spawn(self.root, self.record, 'candidate', 2,
                                               'native', self.command, spawn)

    def test_drift_after_an_earlier_check_refuses_before_spawn(self):
        self.checker.validate_execution_precheck(self.root, {}, {}, {}, 'candidate', 'native', 2)
        self.checker.validate_execution_precheck.side_effect = ValueError('source or selection changed')
        spawn = Mock()
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.guard(spawn)
        spawn.assert_not_called()

    def test_different_reviewed_argv_never_spawns(self):
        self.checker.validate_execution_precheck.return_value = {'nextRootAction': {
            'argv': ['different'], 'candidateSha256': 'a' * 64}}
        spawn = Mock()
        with self.assertRaisesRegex(ValueError, 'command differs'):
            self.guard(spawn)
        spawn.assert_not_called()

    def test_spawn_failure_does_not_create_a_phantom_participant_job(self):
        before = {str(p.relative_to(self.root)): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file()}
        with self.assertRaisesRegex(OSError, 'spawn refused'):
            self.guard(Mock(side_effect=OSError('spawn refused')))
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes()
                                for p in self.root.rglob('*') if p.is_file()})

    def test_success_emits_actual_birth_without_acceptance(self):
        child = Mock(pid=999999)
        stat = '999999 (guarded) ' + ' '.join(['S'] + ['0'] * 18 + ['777'])
        output = io.StringIO()
        with patch.object(Path, 'read_text', return_value=stat), contextlib.redirect_stdout(output):
            self.assertIs(self.guard(Mock(return_value=child)), child)
        receipt = json.loads(output.getvalue())['deliveryLaunch']
        self.assertEqual(receipt['pid'], child.pid)
        self.assertEqual(receipt['startTicks'], '777')
        self.assertFalse(receipt['acceptanceInferred'])

    def test_post_spawn_receipt_failure_retires_owned_process(self):
        child = Mock(pid=999999)
        with patch.object(Path, 'read_text', side_effect=OSError('birth unavailable')), \
             patch.object(loop.os, 'killpg') as kill:
            with self.assertRaisesRegex(OSError, 'birth unavailable'):
                self.guard(Mock(return_value=child))
        kill.assert_called_once_with(child.pid, loop.signal.SIGTERM)
        child.wait.assert_called_once_with(timeout=5)

    def test_supervision_requires_a_new_owned_process_group(self):
        process_module = Mock()
        args = Mock(record=self.record, candidate='candidate', expect_selection=2)
        proxy = loop.DeliverySubprocess(process_module, self.root, args, 'native')
        with self.assertRaisesRegex(ValueError, 'process-group'):
            proxy.Popen(self.command)
        process_module.Popen.assert_not_called()


if __name__ == '__main__':
    unittest.main()
