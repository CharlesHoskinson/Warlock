"""Delivery notes retain uncertainty and report source state without mutations."""
import json
import subprocess
import sys
import unittest

import test_warlock as fixtures


class ContributionReportTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli

    def markdown(self, ok=True):
        result = subprocess.run(
            [sys.executable, '-B', str(fixtures.CHECKER), '--repo', str(self.repo),
             'report', '--markdown'], capture_output=True, text=True, env=self.fixture.env)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result.stdout

    def test_no_record_and_conflicting_formats_fail(self):
        self.cli('report', ok=False)
        self.fixture.start()
        self.cli('report', '--markdown', ok=False)  # Fixture already supplies --json.

    def test_plan_is_not_a_result_and_report_writes_nothing(self):
        self.fixture.start()
        record = self.repo / '.warlock-contributor/slice.json'
        ledger = self.repo / 'docs/warlock-build-loop/v2/requirement-ledger.json'
        before = (record.read_bytes(), ledger.read_bytes(), (self.repo / '.git/index').read_bytes())
        packet = json.loads(self.cli('report').stdout)
        self.assertEqual(packet['intendedBehavior'], self.fixture.slice['after'])
        self.assertIsNone(packet['observedResult'])
        self.assertEqual(packet['selectedChanges'], [])
        self.assertIsNone(packet['observations'][0]['recordedDisposition'])
        self.assertFalse(packet['releaseAccepted'])
        text = self.markdown()
        self.assertIn('No iteration recorded.', text)
        self.assertIn('execution is not inferred', text)
        self.assertEqual(before, (record.read_bytes(), ledger.read_bytes(), (self.repo / '.git/index').read_bytes()))

    def test_partial_evidence_scope_and_missing_observation_survive_rendering(self):
        self.fixture.start()
        claim = self.fixture.claim(scope='typed replay only; no physical or AT observation')
        self.fixture.record_claim(claim)
        packet = json.loads(self.cli('report').stdout)
        observation = packet['observations'][0]
        self.assertEqual(observation['scope'], claim['scope'])
        self.assertEqual(observation['missingObservations'], claim['missingObservations'])
        self.assertEqual(observation['evidence'], claim['evidence'])
        self.assertTrue(observation['evidenceMatchesCurrentSources'])
        text = self.markdown()
        self.assertIn(claim['scope'], text)
        self.assertIn(claim['missingObservations'][0], text)
        self.assertIn('recorded disposition partial', text)

    def test_uncommitted_source_remains_visible_after_recording_fix(self):
        self.fixture.start()
        source = 'implementation/warlock/src/Desktop.elm'
        self.fixture.write(source, 'implemented feedback\n')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'Feedback changed; native evidence pending')
        packet = json.loads(self.cli('report').stdout)
        self.assertEqual(packet['changedSinceLastRecord'], [])
        self.assertEqual(packet['selectedChanges'][0]['path'], source)
        self.assertTrue(packet['selectedChanges'][0]['uncommitted'])
        self.assertIn('uncommitted', self.markdown())
        self.fixture.run_git('add', source)
        self.fixture.run_git('commit', '-qm', 'feedback implementation')
        committed = json.loads(self.cli('report').stdout)
        self.assertFalse(committed['selectedChanges'][0]['uncommitted'])

    def test_stale_source_and_changed_report_are_reported_with_failure(self):
        self.fixture.start()
        self.fixture.record_claim(self.fixture.claim())
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'changed after observation\n')
        packet = json.loads(self.cli('report', ok=False).stdout)
        self.assertFalse(packet['observations'][0]['evidenceMatchesCurrentSources'])
        self.assertTrue(packet['errors'])
        text = self.markdown(ok=False)
        self.assertIn('Error:', text)
        self.assertIn('not current', text)
        self.fixture.write('implementation/warlock/qa/evidence/result.json', {'changed': True})
        packet = json.loads(self.cli('report', ok=False).stdout)
        self.assertTrue(any('changed evidence' in e for e in packet['errors']))

    def test_historical_claim_is_not_rendered_as_current_acceptance(self):
        self.fixture.start()
        self.fixture.record_claim(self.fixture.claim())
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'a later fix\n')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'Later implementation; replay not repeated')
        packet = json.loads(self.cli('report').stdout)
        self.assertFalse(packet['observations'][0]['evidenceMatchesCurrentSources'])
        self.assertEqual(packet['observations'][0]['recordedDisposition'], 'partial')
        self.assertFalse(packet['releaseAccepted'])

    def test_deleted_source_is_reported_and_foreign_drafts_are_never_delivery_changes(self):
        self.fixture.write('foreign.txt', 'protected draft\n')
        self.fixture.start()
        source = 'implementation/warlock/src/Desktop.elm'
        (self.repo / source).unlink()
        packet = json.loads(self.cli('report').stdout)
        self.assertEqual([c['path'] for c in packet['selectedChanges']], [source])
        self.assertIsNone(packet['selectedChanges'][0]['currentSha256'])
        self.assertIn('foreign.txt', packet['protectedForeignPaths'])
        self.assertIn('deleted', self.markdown())

    def test_markdown_cannot_inject_links_html_or_a_second_result_heading(self):
        self.fixture.start()
        self.cli('record', '--outcome', 'qualification', '--summary',
                 'Observed <script>alert(1)</script>\n# Accepted\n[claim](https://example.invalid)')
        text = self.markdown()
        self.assertNotIn('<script>', text)
        self.assertNotIn('\n# Accepted', text)
        self.assertNotIn('[claim](', text)
        self.assertIn('recorded disposition none', text)


if __name__ == '__main__':
    unittest.main()
