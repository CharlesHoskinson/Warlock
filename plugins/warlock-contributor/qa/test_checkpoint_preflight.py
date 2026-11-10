"""Read-only Boolean representation controls; no publication or continuity effects."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PLUGIN = Path(os.environ.get('WARLOCK_CHECKPOINT_PLUGIN', str(Path(__file__).resolve().parents[1])))
REPO = Path(os.environ.get('WARLOCK_PREFLIGHT_REPO', str(PLUGIN.parents[1])))
sys.path.insert(0, str(PLUGIN / 'scripts'))
import checkpoint_preflight as checker


class CheckpointPreflightTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        guard = self.root / 'tools/warlock_continuity.py'
        guard.parent.mkdir()
        guard.write_bytes((REPO / 'tools/warlock_continuity.py').read_bytes())
        self.path = self.root / 'draft.json'

    def inspect(self, value):
        self.path.write_text(json.dumps(value, ensure_ascii=False))
        before = self.path.read_bytes()
        result = checker.inspect(self.root, 'draft.json', hashlib.sha256(before).hexdigest())
        self.assertEqual(self.path.read_bytes(), before)
        return result

    def test_false_is_advisory_only_and_preserves_nonascii_bytes(self):
        result = self.inspect({'goalStatus': 'active', 'externalBlocker': False, 'note': 'café'})
        self.assertEqual(result['status'], 'consistent-advisory-only')
        self.assertIs(result['externalBlocker'], False)
        for field in ('executionAuthorized', 'executionPerformed', 'checkpointWritten',
                      'wakeAcknowledged', 'freshGoalVerified', 'nativeAuthority', 'sourceReady'):
            self.assertIs(result[field], False)

    def test_true_blocker_is_not_coerced_or_waived(self):
        result = self.inspect({'goalStatus': 'active', 'externalBlocker': True})
        self.assertIs(result['externalBlocker'], True)
        self.assertIs(result['wakeAcknowledged'], False)

    def test_null_zero_strings_arrays_and_objects_are_not_booleans(self):
        for value in (None, 0, 1, 'false', 'true', [], {}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Boolean'):
                self.inspect({'externalBlocker': value})

    def test_missing_field_and_nonobject_json_refused(self):
        for value in ({}, [], None, False):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.inspect(value)

    def test_status_and_nonce_are_not_invented_or_reinterpreted(self):
        for status in ('paused', 'completed', 'stopped'):
            result = self.inspect({'goalStatus': status, 'externalBlocker': False})
            self.assertIs(result['freshGoalVerified'], False)
            self.assertIs(result['wakeAcknowledged'], False)
        result = self.inspect({'externalBlocker': False})
        self.assertIs(result['wakeAcknowledged'], False)

    def test_digest_mismatch_refuses_without_rewriting(self):
        self.path.write_text('{"externalBlocker":false}')
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            checker.inspect(self.root, 'draft.json', '0' * 64)
        self.assertEqual(self.path.read_bytes(), before)

    def test_duplicate_keys_and_malformed_json_refused(self):
        for value in (b'{"externalBlocker":null,"externalBlocker":false}', b'{'):
            self.path.write_bytes(value)
            with self.subTest(value=value), self.assertRaises(ValueError):
                checker.inspect(self.root, 'draft.json', hashlib.sha256(value).hexdigest())

    def test_guard_drift_refuses_without_importing_guard(self):
        guard = self.root / 'tools/warlock_continuity.py'
        guard.write_bytes(b'raise RuntimeError("must never import")\n')
        with self.assertRaisesRegex(ValueError, 'guard'):
            self.inspect({'externalBlocker': False})

    def test_symlink_parent_leaf_and_traversal_refused(self):
        self.path.write_text('{"externalBlocker":false}')
        expected = hashlib.sha256(self.path.read_bytes()).hexdigest()
        (self.root / 'link.json').symlink_to(self.path)
        (self.root / 'linked').symlink_to(self.root, target_is_directory=True)
        for name in ('link.json', 'linked/draft.json', '../draft.json', str(self.path)):
            with self.subTest(name=name), self.assertRaises(ValueError):
                checker.inspect(self.root, name, expected)

    def test_changed_during_read_and_oversized_input_refused(self):
        self.path.write_text('{"externalBlocker":false}')
        expected = hashlib.sha256(self.path.read_bytes()).hexdigest()
        original = checker._read
        calls = 0

        def changed(root, name, limit):
            nonlocal calls
            if name == 'draft.json':
                calls += 1
                if calls > 1:
                    return b'{"externalBlocker":true}'
            return original(root, name, limit)

        with patch.object(checker, '_read', side_effect=changed), self.assertRaises(ValueError):
            checker.inspect(self.root, 'draft.json', expected)
        self.path.write_bytes(b' ' * (1048576 + 1))
        with self.assertRaises(ValueError):
            checker.inspect(self.root, 'draft.json', hashlib.sha256(self.path.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
