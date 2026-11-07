"""Fixed native command advisory controls; never executes a source or target."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
sys.path.insert(0, str(PLUGIN / 'scripts'))
import native_command_preflight as checker


class NativeCommandPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ('implementation/elm-build-loop-v1/loop.py',
                     'window-integration-qa/qa_run.py', 'window-integration-qa/qa_launch.py',
                     'docs/warlock-build-loop/v2/loop.py'):
            self.write(name, (REPO / name).read_bytes())
        self.runner = 'tools/run_webkit_provider_probe.py'
        self.packet = '.warlock-contributor/evidence/nextloop-20261106/native-provider-probe/probe-packet.json'
        self.write(self.runner, b'# fixed fixture bytes, not executed\n')
        self.write(self.packet, b'{"fixture":"packet"}\n')
        self.candidate = {'id': 'fixture', 'scope': 'native',
            'argv': ['/usr/bin/python3', '-B', str(self.root / 'window-integration-qa/qa_run.py'),
                     '--', '/usr/bin/python3', '-B', str(self.root / self.runner),
                     '--sha256', self.sha(self.packet)],
            'manifest': {'runners': {self.runner: self.sha(self.runner)},
                         'profiles': {self.packet: self.sha(self.packet)}}}

    def write(self, name, body):
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)

    def sha(self, name):
        return hashlib.sha256((self.root / name).read_bytes()).hexdigest()

    def inspect(self, candidate=None):
        self.write('candidate.json', json.dumps(candidate or self.candidate).encode())
        return checker.inspect(self.root, 'candidate.json', self.sha('candidate.json'))

    def test_fixed_portable_command_is_advisory_only(self):
        result = self.inspect()
        self.assertEqual(result['status'], 'consistent-advisory-only')
        for flag in ('executionAuthorized', 'executionPerformed', 'nativeAuthority', 'sourceReady'):
            self.assertIs(result[flag], False)

    def test_candidate_digest_matches_core_for_nonascii_text(self):
        self.candidate['expectedObservation'] = 'caf\u00e9 remains literal'
        result = self.inspect()
        expected = hashlib.sha256(json.dumps(self.candidate, sort_keys=True,
            separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()
        self.assertEqual(result['candidateSha256'], expected)

    def test_archived_launcher_alias_is_refused(self):
        candidate = copy.deepcopy(self.candidate)
        candidate['argv'][2] = '/home/hoskinson/window-integration-qa/qa_run.py'
        with self.assertRaisesRegex(ValueError, 'command'):
            self.inspect(candidate)

    def test_python_flags_separator_runner_and_extra_args_are_fixed(self):
        for index, value in ((0, 'python3'), (1, '-I'), (3, '--anything'),
                             (4, '/bin/sh'), (5, '-c'), (6, '/tmp/runner.py'),
                             (7, '--packet'), (8, '0' * 64)):
            candidate = copy.deepcopy(self.candidate)
            candidate['argv'][index] = value
            with self.subTest(index=index), self.assertRaises(ValueError):
                self.inspect(candidate)
        candidate = copy.deepcopy(self.candidate)
        candidate['argv'].append('extra')
        with self.assertRaises(ValueError):
            self.inspect(candidate)

    def test_each_original_native_guard_change_refuses(self):
        for name in ('implementation/elm-build-loop-v1/loop.py',
                     'window-integration-qa/qa_run.py', 'window-integration-qa/qa_launch.py'):
            original = (self.root / name).read_bytes()
            self.write(name, original + b'\n# changed\n')
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.inspect()
            self.write(name, original)

    def test_changed_portable_binding_wrapper_refuses(self):
        name = 'docs/warlock-build-loop/v2/loop.py'
        self.write(name, (self.root / name).read_bytes() + b'\n# changed\n')
        with self.assertRaises(ValueError):
            self.inspect()

    def test_runner_or_packet_changed_bytes_refuse(self):
        for name in (self.runner, self.packet):
            original = (self.root / name).read_bytes()
            self.write(name, original + b' ')
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.inspect()
            self.write(name, original)

    def test_missing_manifest_binding_or_wrong_scope_refuses(self):
        candidate = copy.deepcopy(self.candidate)
        candidate['scope'] = 'cpu'
        with self.assertRaises(ValueError):
            self.inspect(candidate)
        for role in ('runners', 'profiles'):
            candidate = copy.deepcopy(self.candidate)
            candidate['manifest'][role] = {}
            with self.subTest(role=role), self.assertRaises(ValueError):
                self.inspect(candidate)

    def test_duplicate_json_and_changed_candidate_hash_refuse(self):
        self.write('candidate.json', b'{"scope":"native","scope":"cpu"}')
        with self.assertRaises(ValueError):
            checker.inspect(self.root, 'candidate.json', self.sha('candidate.json'))
        with self.assertRaises(ValueError):
            checker.inspect(self.root, 'candidate.json', '0' * 64)

    def test_candidate_symlink_and_parent_escape_refuse(self):
        self.write('real.json', json.dumps(self.candidate).encode())
        (self.root / 'candidate.json').symlink_to(self.root / 'real.json')
        with self.assertRaises(ValueError):
            checker.inspect(self.root, 'candidate.json', self.sha('real.json'))
        with self.assertRaises(ValueError):
            checker.inspect(self.root, '../real.json', self.sha('real.json'))

    def test_intermediate_guard_directory_symlink_refuses(self):
        original = self.root / 'window-integration-qa'
        original.rename(self.root / 'other')
        original.symlink_to(self.root / 'other', target_is_directory=True)
        with self.assertRaises(ValueError):
            self.inspect()


if __name__ == '__main__':
    unittest.main()
