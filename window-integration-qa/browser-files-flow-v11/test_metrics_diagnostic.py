"""Actual owned kernel metadata checks, without a GUI or authority grants."""
import base64
import hashlib
import json
import mmap
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import metrics_diagnostic
from metrics_diagnostic import observe

class KernelObservation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.profile = Path(self.tmp.name)
        self.profile.chmod(0o700)
        self.pid = os.getpid()
        self.root = {'pid': self.pid, 'start': Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19]}
        exe = Path('/proc/self/exe').resolve()
        self.frozen = {str(exe): {'sha256': hashlib.sha256(exe.read_bytes()).hexdigest(), 'mode': stat.S_IMODE(exe.stat().st_mode)}}
        self.file = None
        self.mapping = None

    def tearDown(self):
        if self.mapping is not None:
            self.mapping.close()
        if self.file is not None:
            self.file.close()
        self.tmp.cleanup()

    def allocate(self):
        directory = self.profile / 'BrowserMetrics'
        directory.mkdir(mode=0o700)
        path = directory / ('BrowserMetrics-1234-' + format(self.pid, 'X') + '.pma')
        self.file = path.open('w+b')
        path.chmod(0o600)
        self.file.truncate(4 * 1024 * 1024)
        self.mapping = mmap.mmap(self.file.fileno(), 0)
        path.unlink()

    def batch(self):
        return {'processes': [{'identity': dict(self.root), 'rawMapsBase64': base64.b64encode(Path('/proc/self/maps').read_bytes()).decode()}]}

    def test_deleted_regular_kernel_inode_and_raw_blocks(self):
        self.allocate()
        proof = {}
        observe(proof, self.batch(), self.root, self.profile, self.frozen, lambda: None)
        self.assertTrue(proof['completed'])
        self.assertFalse(proof['authorityGranted'])
        self.assertEqual(len(proof['observations']), 1)
        row = proof['observations'][0]
        self.assertTrue(row['filenamePIDMatches'])
        self.assertTrue(row['matchingFDs'])
        for fd in row['matchingFDs']:
            self.assertEqual(fd['stat']['st_nlink'], 0)
            self.assertEqual(fd['stat']['fullMode'], 0o600)
            self.assertEqual(fd['stat']['st_size'], 4 * 1024 * 1024)
            self.assertEqual(fd['stat']['st_ino'], row['mapping']['inode'])
            self.assertEqual(fd['fdinfo']['ino'], row['mapping']['inode'])
            raw = base64.b64decode(fd['rawFdinfo']['base64'], validate=True)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), fd['rawFdinfo']['sha256'])
        json.dumps(proof)

    def test_no_candidate_never_grants_authority(self):
        proof = {}
        observe(proof, self.batch(), self.root, self.profile, self.frozen, lambda: None)
        self.assertEqual(proof['observations'], [])
        self.assertFalse(proof['authorityGranted'])

    def test_stale_start_refuses_before_metadata(self):
        proof = {}
        with self.assertRaisesRegex(RuntimeError, 'lifetime changed'):
            observe(proof, self.batch(), {**self.root, 'start': '0'}, self.profile, self.frozen, lambda: None)
        self.assertFalse(proof['authorityGranted'])

    def test_profile_mode_change_refuses(self):
        proof = {}
        self.profile.chmod(0o755)
        with self.assertRaisesRegex(RuntimeError, 'private browser profile'):
            observe(proof, self.batch(), self.root, self.profile, self.frozen, lambda: None)
        self.assertEqual(proof['profile']['fullMode'], 0o755)

    def test_duplicate_snapshot_refuses(self):
        proof = {}
        batch = self.batch()
        batch['processes'] *= 2
        with self.assertRaisesRegex(RuntimeError, 'One exact readable'):
            observe(proof, batch, self.root, self.profile, self.frozen, lambda: None)

    def test_final_guard_failure_retains_stat(self):
        self.allocate()
        calls = []
        def guard():
            calls.append(True)
            if len(calls) == 2:
                raise RuntimeError('actual owned guard drift')
        proof = {}
        with self.assertRaisesRegex(RuntimeError, 'guard drift'):
            observe(proof, self.batch(), self.root, self.profile, self.frozen, guard)
        self.assertTrue(proof['observations'][0]['matchingFDs'][0]['stat'])
        self.assertFalse(proof['completed'])

    def test_fdinfo_read_failure_retains_inode_and_error(self):
        self.allocate()
        proof = {}
        original = metrics_diagnostic.bounded
        def read(path, limit=4 * 1024 * 1024):
            if 'fdinfo' in Path(path).parts:
                raise PermissionError(13, 'diagnostic fdinfo denied', str(path))
            return original(path, limit)
        with patch('metrics_diagnostic.bounded', read):
            observe(proof, self.batch(), self.root, self.profile, self.frozen, lambda: None)
        for fd in proof['observations'][0]['matchingFDs']:
            self.assertEqual(fd['errors']['fdinfo']['errno'], 13)
            self.assertEqual(fd['stat']['st_nlink'], 0)
        self.assertFalse(proof['authorityGranted'])

if __name__ == '__main__':
    unittest.main()
