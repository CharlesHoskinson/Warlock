"""A rewritten observation cannot buy more investigation time."""
import json
import unittest

import test_warlock as fixtures


class VerdictProgressTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli
        self.fixture.start()
        self.claim = self.fixture.claim()
        self.fixture.record_claim(self.claim)

    def record(self):
        return json.loads((self.repo / '.warlock-contributor/slice.json').read_text())

    def test_reworded_scope_and_missing_observations_do_not_reset_timer(self):
        since = json.loads(self.cli('check').stdout)['progress']['lastRecordedProgressUTC']
        for wording in ('Native input still missing', 'Await actual keyboard evidence'):
            self.claim.update(scope='Replay result: ' + wording,
                              missingObservations=[wording], reviewer='different observer')
            self.fixture.record_claim(self.claim)
        packet = json.loads(self.cli('check').stdout)
        self.assertEqual(packet['progress']['lastRecordedProgressUTC'], since)
        self.assertEqual(packet['progress']['iterationsWithoutProgress'], 2)
        self.assertIn('two-iterations-without-progress', packet['progress']['reasons'])
        self.assertTrue(packet['ok'])

    def test_new_report_bytes_and_path_with_same_disposition_are_requalification(self):
        report = self.fixture.write('implementation/warlock/qa/evidence/repeated.json',
                                    {'timestamp': 'new', 'observation': 'same partial result'})
        self.claim.update(scope='Another execution of component replay',
                          evidence=[{'path': str(report.relative_to(self.repo)),
                                     'sha256': fixtures.digest(report)}])
        self.fixture.record_claim(self.claim)
        self.assertFalse(self.record()['iterations'][-1]['meaningfulProgress'])

    def test_new_disposition_counts_once_and_oscillating_labels_cannot_reset(self):
        self.claim['disposition'] = 'failed'
        self.fixture.record_claim(self.claim)
        self.assertTrue(self.record()['iterations'][-1]['meaningfulProgress'])
        for disposition in ('partial', 'failed'):
            self.claim['disposition'] = disposition
            self.fixture.record_claim(self.claim)
            self.assertFalse(self.record()['iterations'][-1]['meaningfulProgress'])
        self.assertEqual(json.loads(self.cli('check').stdout)['progress']['iterationsWithoutProgress'], 2)

    def test_historical_policies_keep_their_original_rewording_interpretation(self):
        for policy in (1, 2, 3):
            with self.subTest(policy=policy):
                record = self.record()
                record['iterations'] = record['iterations'][:1]
                record['iterations'][0]['progressPolicy'] = policy
                newer = json.loads(json.dumps(record['iterations'][0]))
                newer['claims'][0]['scope'] = 'Historical reworded observation'
                record['iterations'].append(newer)
                self.fixture.write('.warlock-contributor/slice.json', record)
                self.cli('check')
                self.claim['scope'] = 'Current wording after historical record'
                self.fixture.record_claim(self.claim)
                current = self.record()['iterations'][-1]
                self.assertEqual(current['progressPolicy'], 4)
                self.assertFalse(current['meaningfulProgress'])
                self.cli('check')

    def test_forged_progress_for_reworded_observation_is_rejected(self):
        self.claim['scope'] = 'Reworded only'
        self.fixture.record_claim(self.claim)
        record = self.record()
        record['iterations'][-1]['meaningfulProgress'] = True
        self.fixture.write('.warlock-contributor/slice.json', record)
        packet = json.loads(self.cli('check', ok=False).stdout)
        self.assertIn('Iteration progress assertion differs from source hashes/recorded verdict', packet['errors'])

    def test_real_authored_change_still_resets_recorded_progress(self):
        self.claim['scope'] = 'Same observation reworded'
        self.fixture.record_claim(self.claim)
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'actual source delta\n')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'Changed authored behavior')
        self.assertTrue(self.record()['iterations'][-1]['meaningfulProgress'])
        self.assertEqual(json.loads(self.cli('check').stdout)['progress']['iterationsWithoutProgress'], 0)
