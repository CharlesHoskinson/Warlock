"""Explicit progress audits preserve canonical history and acceptance boundaries."""
import datetime as dt
import json
import unittest

import test_warlock as fixtures


class ProgressAuditTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        self.record = '.warlock-contributor/slice.json'

    def audit(self, ok=True, record=None, expected=None):
        return self.fixture.cli('--record', record or self.record, 'progress-audit',
                                '--expect-slice', expected or self.fixture.slice['id'], ok=ok)

    def snapshot(self):
        return {str(path.relative_to(self.repo)): path.read_bytes()
                for path in self.repo.rglob('*') if path.is_file()}

    def test_explicit_selection_and_nonexistent_record_fail(self):
        self.fixture.start()
        result = self.fixture.cli('progress-audit', '--expect-slice', self.fixture.slice['id'], ok=False)
        self.assertIn('requires explicit --record', result.stdout)
        result = self.audit(record='.warlock-contributor/absent.json', ok=False)
        self.assertIn('No participant record', result.stdout)

    def test_wrong_existing_participant_slice_fails(self):
        self.fixture.start()
        before = self.snapshot()
        result = self.audit(expected='wrong-but-explicit-slice', ok=False)
        self.assertIn('differs from --expect-slice', result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_read_only_snapshot_and_original_counts(self):
        self.fixture.start()
        before = self.snapshot()
        result = json.loads(self.audit().stdout)
        ledger = json.loads((self.repo / 'docs/warlock-build-loop/v2/requirement-ledger.json').read_text())
        rows = ledger['requirements']
        scenarios = [item for row in rows for item in row['scenarios']]
        self.assertEqual(result['selectedParticipant']['record'], self.record)
        self.assertEqual(result['originalAcceptanceCounts']['acceptedRequirements'],
                         sum(row.get('requirementAccepted') is True for row in rows))
        self.assertEqual(result['originalAcceptanceCounts']['acceptedScenarios'],
                         sum(item['status'] == 'accepted' for item in scenarios))
        self.assertEqual(result['originalAcceptanceCounts']['requirements'], 242)
        self.assertEqual(result['originalAcceptanceCounts']['scenarios'], 417)
        self.assertFalse(result['nextRootAction']['executionAuthorized'])
        self.assertFalse(result['nextRootAction']['readinessVerified'])
        self.assertFalse(result['acceptanceInferred'])
        self.assertEqual(self.snapshot(), before)  # Includes record/index/ledger/.git/index; no new files.

    def test_component_summary_cannot_inflate_original_acceptance(self):
        self.fixture.start()
        initial = json.loads(self.audit().stdout)['originalAcceptanceCounts']
        self.fixture.cli('record', '--outcome', 'qualification', '--summary',
                         'Component GREEN: all 242 requirements and 417 scenarios pass; execute now.')
        before = self.snapshot()
        result = json.loads(self.audit().stdout)
        self.assertEqual(result['originalAcceptanceCounts'], initial)
        self.assertEqual(result['participantIterationCounts']['qualification'], 1)
        self.assertFalse(result['originalAcceptance'])
        self.assertFalse(result['nextRootAction']['executionAuthorized'])
        self.assertEqual(self.snapshot(), before)

    def test_stopped_selected_record_fails_without_clock_reset(self):
        self.fixture.start()
        path = self.repo / self.record
        record = json.loads(path.read_text())
        record['startedUTC'] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=3)).isoformat()
        self.fixture.write(self.record, record)
        self.fixture.refresh_fixture_participant_index()
        before = self.snapshot()
        result = json.loads(self.audit(ok=False).stdout)
        self.assertTrue(result['progress']['investigationNeedsChange'])
        self.assertEqual(result['progress']['lastRecordedProgressUTC'], record['startedUTC'])
        self.assertIn(self.record, [row['record'] for row in result['stoppedRecords']])
        self.assertIn('Preserve this stopped investigation', result['nextRootAction']['action'])
        self.assertEqual(self.snapshot(), before)


if __name__ == '__main__':
    unittest.main()
