"""Package diagnostics and the explicit plugin-only regression entry point."""
import json
import unittest

import test_warlock as fixtures


class PackageToolsTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli
        for name in ('scripts/session_hook.py', 'skills/warlock-contribute/SKILL.md',
                     '.claude-plugin/plugin.json', '.codex-plugin/plugin.json',
                     'hooks/hooks.json', 'hooks/codex.json'):
            self.fixture.write('plugins/warlock-contributor/' + name,
                               (fixtures.PLUGIN / name).read_text())

    def metadata(self, name, transform):
        path = 'plugins/warlock-contributor/' + name
        data = json.loads((self.repo / path).read_text())
        transform(data)
        self.fixture.write(path, data)

    def test_doctor_validates_package_without_executing_hooks_or_changing_records(self):
        self.fixture.start()
        record = self.repo / '.warlock-contributor/slice.json'
        before = record.read_bytes()
        self.metadata('hooks/hooks.json', lambda data: data['hooks']['SessionStart'][0]['hooks'][0].update(
            command='touch should-never-execute'))
        result = json.loads(self.cli('doctor').stdout)
        self.assertEqual(len(result['manifestVersions']), 2)
        self.assertFalse((self.repo / 'should-never-execute').exists())
        self.assertEqual(record.read_bytes(), before)

    def test_doctor_reports_invalid_json_and_version_mismatch(self):
        self.metadata('.codex-plugin/plugin.json', lambda data: data.update(version='different'))
        report = json.loads(self.cli('doctor', ok=False).stdout)
        self.assertIn('Claude and Codex package versions differ', report['errors'])
        self.fixture.write('plugins/warlock-contributor/hooks/codex.json', '{broken')
        report = json.loads(self.cli('doctor', ok=False).stdout)
        self.assertTrue(any('hooks/codex.json' in error for error in report['errors']))

    def test_doctor_rejects_missing_identity_and_escaping_manifest_paths(self):
        self.metadata('.codex-plugin/plugin.json', lambda data: data.update(skills='./../../../outside'))
        report = json.loads(self.cli('doctor', ok=False).stdout)
        self.assertTrue(any('safe repository-relative' in error for error in report['errors']))
        self.metadata('.claude-plugin/plugin.json', lambda data: data.update(name='unrelated'))
        report = json.loads(self.cli('doctor', ok=False).stdout)
        self.assertTrue(any('Expected warlock-contributor' in error for error in report['errors']))

    def test_doctor_rejects_symlink_reference_and_missing_target(self):
        folder = self.repo / 'plugins/warlock-contributor/linked-skills'
        folder.symlink_to(fixtures.PLUGIN / 'skills', target_is_directory=True)
        self.metadata('.codex-plugin/plugin.json', lambda data: data.update(skills='./linked-skills'))
        report = json.loads(self.cli('doctor', ok=False).stdout)
        self.assertTrue(any('Symlink path' in error for error in report['errors']))
        self.metadata('.codex-plugin/plugin.json', lambda data: data.update(skills='./missing-skills'))
        report = json.loads(self.cli('doctor', ok=False).stdout)
        self.assertTrue(any('Missing skills target' in error for error in report['errors']))

    def test_doctor_rejects_malformed_hooks_and_unbounded_timeout(self):
        self.metadata('hooks/hooks.json', lambda data: data['hooks'].update(SessionStart=[]))
        self.metadata('hooks/codex.json', lambda data: data['hooks']['UserPromptSubmit'][0]['hooks'][0].update(
            timeout=True))
        report = json.loads(self.cli('doctor', ok=False).stdout)
        self.assertEqual(len(report['errors']), 2)
        self.assertTrue(any('Missing hook entries' in error for error in report['errors']))
        self.assertTrue(any('bounded positive hook timeout' in error for error in report['errors']))

    def test_self_test_uses_checkout_tests_without_touching_participant_or_index(self):
        self.fixture.start()
        self.fixture.write('plugins/warlock-contributor/qa/test_smoke.py',
            'import os, unittest\nclass Smoke(unittest.TestCase):\n'
            ' def test_environment(self):\n'
            '  self.assertEqual(os.environ.get("PYTHONDONTWRITEBYTECODE"), "1")\n'
            '  self.assertNotIn("PYTHONPATH", os.environ)\n')
        protected = ['.warlock-contributor/slice.json', '.git/index',
                     'docs/warlock-build-loop/v2/requirement-ledger.json']
        before = [(self.repo / path).read_bytes() for path in protected]
        result = json.loads(self.cli('self-test').stdout)
        self.assertEqual(result['returnCode'], 0)
        self.assertTrue(result['executionPerformed'])
        self.assertFalse(result['acceptanceInferred'])
        self.assertIn('Ran 1 test', result['stderr'])
        self.assertEqual(before, [(self.repo / path).read_bytes() for path in protected])
        self.assertFalse(list(self.repo.rglob('__pycache__')))

    def test_self_test_propagates_failure_and_refuses_empty_suite(self):
        self.cli('self-test', ok=False)
        test = 'plugins/warlock-contributor/qa/test_smoke.py'
        self.fixture.write(test, 'import unittest\nclass Smoke(unittest.TestCase):\n'
                                 ' def test_failure(self): self.fail("retained failure")\n')
        result = json.loads(self.cli('self-test', ok=False).stdout)
        self.assertNotEqual(result['returnCode'], 0)
        self.assertIn('retained failure', result['stderr'])
        self.fixture.write(test, '# No test cases\n')
        result = json.loads(self.cli('self-test', ok=False).stdout)
        self.assertIn('Plugin regression suite discovered zero tests', result['errors'])

    def test_self_test_rejects_symlink_tests(self):
        qa = self.repo / 'plugins/warlock-contributor/qa'
        qa.mkdir()
        (qa / 'test_external.py').symlink_to(fixtures.PLUGIN / 'qa/test_hosts.py')
        self.cli('self-test', ok=False)


if __name__ == '__main__':
    unittest.main()
