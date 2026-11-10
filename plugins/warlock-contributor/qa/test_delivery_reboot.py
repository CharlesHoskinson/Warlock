"""Explicit same-history reboot recovery never excludes unobserved downtime."""
import copy
import datetime as dt
import json
import unittest

import test_delivery_authorization as authorization
from test_delivery_flow import DeliveryFixture, engine


class DeliveryRebootTests(DeliveryFixture):
    cli_at = authorization.DeliveryAuthorizationTests.cli_at
    append_at = authorization.DeliveryAuthorizationTests.append_at
    ref = authorization.DeliveryAuthorizationTests.ref

    def sample(self, seconds=3600, boot='reboot-b', counter=10):
        origin = self.record()['delivery']['clockOrigin']
        return {'utc': (dt.datetime.fromisoformat(origin['utc']) + dt.timedelta(seconds=seconds)).isoformat(),
                'bootId': boot, 'monotonicNs': counter * 1000000000,
                'boottimeNs': counter * 1000000000}

    def event(self, sample, suffix='1'):
        module = engine()
        record = self.record()
        events = record['delivery']['events']
        last = events[-1]['clockSample'] if events else record['delivery']['clockOrigin']
        goal = {'schema': 1, 'status': 'active', 'observedUTC': sample['utc']}
        evidence = {'schema': 1, 'kind': 'same-history-clock-reconciliation',
                    'recordPath': self.record_path,
                    'deliveryIdentitySha256': module.json_sha256(module.delivery_identity(record)),
                    'historySha256': module.json_sha256(events),
                    'previousSampleSha256': module.json_sha256(last),
                    'observedBootId': sample['bootId'], 'observedUTC': sample['utc'],
                    'goalObservation': self.ref('clock-goal-' + suffix, goal)}
        return {'eventId': 'reconcile-' + suffix, 'kind': 'clock-reconciled',
                'evidence': self.ref('clock-evidence-' + suffix, evidence)}, evidence, goal

    def test_expired_reboot_renews_before_reconciliation_but_cannot_execute(self):
        self.start_delivery()
        self.ready()
        before = self.record()
        sample = self.sample(10800)
        module = engine()
        progress = module.delivery_progress_status(before, sample=sample)
        self.assertTrue(progress['authorizationExpired'])
        self.assertTrue(progress['reconciliationRequired'])
        event, _, _ = self.event(sample)
        self.append_at(event, sample, ok=False)
        renewal, _, _, _ = authorization.DeliveryAuthorizationTests.renewal(self, sample)
        self.append_at(renewal, sample)
        after_renewal = self.record()
        self.assertEqual(after_renewal['delivery']['events'][:-1], before['delivery']['events'])
        self.assertEqual(module.delivery_identity(after_renewal), module.delivery_identity(before))
        self.assertTrue(module.delivery_progress_status(after_renewal, sample=sample)['reconciliationRequired'])
        self.cli_at(sample, 'delivery-precheck', '--candidate', 'c1', '--scope', 'cpu',
                    '--expect-selection', '1', ok=False)
        event, _, _ = self.event(sample, 'after-renewal')
        self.append_at(event, sample)
        self.cli_at(sample, 'delivery-precheck', '--candidate', 'c1', '--scope', 'cpu',
                    '--expect-selection', '1')
        after = self.record()
        self.assertEqual(after['delivery']['clockOrigin'], before['delivery']['clockOrigin'])
        self.assertEqual(module.record_identity(after, self.record_path), module.record_identity(before, self.record_path))

    def test_reboot_reconciles_ready_candidate_without_reset_or_suspend_credit(self):
        self.start_delivery()
        candidate = self.ready()
        before = self.record()
        state = (self.repo / 'docs/warlock-build-loop/v2/STATE.json').read_bytes()
        sample = self.sample()
        module = engine()
        self.assertTrue(module.delivery_progress_status(before, sample=sample)['reconciliationRequired'])
        event, _, _ = self.event(sample)
        result = self.append_at(event, sample)
        after = self.record()
        self.assertEqual(after['delivery']['events'][:-1], before['delivery']['events'])
        self.assertEqual(module.delivery_identity(after), module.delivery_identity(before))
        self.assertEqual(state, (self.repo / 'docs/warlock-build-loop/v2/STATE.json').read_bytes())
        progress = result['nextRootAction']['progress']
        self.assertFalse(progress['reconciliationRequired'])
        self.assertGreaterEqual(progress['secondsSinceRecordedProgress'], 3599)
        self.assertTrue(progress['planChangeRequired'])
        self.assertLessEqual(progress['suspendedSeconds'], 1)
        self.assertEqual(progress['lastRecordedProgressUTC'], before['delivery']['clockOrigin']['utc'])
        self.assertEqual(result['nextRootAction']['candidateSha256'], candidate)
        self.assertNotIn('deliveryAdvance', after['delivery']['events'][-1])
        self.cli_at(sample, 'delivery-precheck', '--candidate', 'c1', '--scope', 'cpu', '--expect-selection', '1')

    def test_second_reboot_requires_new_evidence_and_accumulates_elapsed(self):
        self.start_delivery()
        first = self.sample(1800)
        event, _, _ = self.event(first)
        self.append_at(event, first)
        second = self.sample(3600, 'reboot-c')
        self.assertTrue(engine().delivery_progress_status(self.record(), sample=second)['reconciliationRequired'])
        self.append_at(event, second, ok=False)
        event2, _, _ = self.event(second, '2')
        self.append_at(event2, second)
        status = engine().delivery_progress_status(self.record(), sample=second)
        self.assertEqual(status['secondsSinceRecordedProgress'], 3600)
        self.assertEqual(status['suspendedSeconds'], 0)
        self.assertFalse(status['reconciliationRequired'])

    def test_duplicate_reconciliation_without_discontinuity_refused(self):
        self.start_delivery()
        sample = self.sample()
        event, _, _ = self.event(sample)
        self.append_at(event, sample)
        second, _, _ = self.event(sample, '2')
        self.append_at(second, sample, ok=False)

    def test_same_boot_counter_regression_requires_explicit_reconciliation(self):
        self.start_delivery()
        origin = self.record()['delivery']['clockOrigin']
        sample = self.sample(3600, origin['bootId'], 0)
        event, _, _ = self.event(sample)
        self.append_at(event, sample)
        status = engine().delivery_progress_status(self.record(), sample=sample)
        self.assertEqual(status['secondsSinceRecordedProgress'], 3600)
        self.assertTrue(status['planChangeRequired'])

    def test_wall_clock_regression_expired_authority_and_inactive_goal_refused(self):
        self.start_delivery()
        for seconds in (-1, 10800):
            sample = self.sample(seconds)
            event, _, _ = self.event(sample)
            self.append_at(event, sample, ok=False)
        sample = self.sample()
        event, evidence, goal = self.event(sample)
        goal['status'] = 'paused'
        evidence['goalObservation'] = self.ref('clock-paused', goal)
        event['evidence'] = self.ref('clock-paused-evidence', evidence)
        self.append_at(event, sample, ok=False)

    def test_stale_history_wrong_boot_wrong_identity_and_old_goal_refused(self):
        self.start_delivery()
        sample = self.sample()
        original, evidence, goal = self.event(sample)
        for key, value in [('historySha256', '0' * 64), ('previousSampleSha256', '0' * 64),
                           ('deliveryIdentitySha256', '0' * 64), ('observedBootId', 'foreign-boot')]:
            changed = dict(evidence, **{key: value})
            event = dict(original, evidence=self.ref('bad-' + key, changed))
            self.append_at(event, sample, ok=False)
        goal['observedUTC'] = (dt.datetime.fromisoformat(sample['utc']) - dt.timedelta(seconds=121)).isoformat()
        evidence['goalObservation'] = self.ref('old-goal', goal)
        self.append_at(dict(original, evidence=self.ref('old-evidence', evidence)), sample, ok=False)

    def test_caller_cannot_supply_bridge_or_advance_or_expiry(self):
        self.start_delivery()
        sample = self.sample()
        event, _, _ = self.event(sample)
        for key, value in [('reconciliation', {}), ('deliveryAdvance', 'fake'),
                           ('authorizationExpiresUTC', '2099-01-01T00:00:00+00:00')]:
            self.append_at(dict(event, **{key: value}), sample, ok=False)

    def test_running_and_terminal_unconsumed_job_refused(self):
        self.start_delivery()
        sha = self.ready()
        self.append(self.started(sha))
        sample = self.sample()
        event, _, _ = self.event(sample)
        self.append_at(event, sample, ok=False)
        # Closing across reboot remains permitted, but leaves the handle occupied.
        self.append_at(self.terminal(sha, consumed=False), sample)
        event2, _, _ = self.event(sample, '2')
        self.append_at(event2, sample, ok=False)

    def test_reconciliation_retains_repeated_failure_reason(self):
        self.start_delivery()
        for index in (1, 2):
            sha = self.candidate('failed-' + str(index))
            self.append(self.review(sha))
            job = 'failed-job-' + str(index)
            self.append(self.started(sha, job))
            terminal = self.terminal(sha, job=job, classification='failed', exit_code=1)
            report = json.loads((self.repo / terminal['report']['path']).read_text())
            report['failureSignature'] = 'same-observed-failure'
            terminal['report'] = self.ref('failed-report-' + str(index), report)
            self.append(terminal)
        before = self.record()
        sample = self.sample()
        event, _, _ = self.event(sample)
        self.append_at(event, sample)
        status = engine().delivery_progress_status(self.record(), sample=sample)
        self.assertIn('two-experiments-with-same-failure', status['reasons'])
        self.assertEqual(self.record()['delivery']['events'][:-1], before['delivery']['events'])

    def test_historical_receipt_age_does_not_expire_valid_reconciliation(self):
        self.start_delivery()
        sample = self.sample()
        event, _, _ = self.event(sample)
        self.append_at(event, sample)
        later = dict(sample, utc=(dt.datetime.fromisoformat(sample['utc']) + dt.timedelta(seconds=600)).isoformat(),
                     monotonicNs=610000000000, boottimeNs=610000000000)
        self.cli_at(later, 'handoff')
        module = engine()
        record = self.record()
        record['_recordPath'] = self.record_path
        reqs = {row['id']: row for row in module.requirement_document(self.repo)['requirements']}
        for mutation in ('historySha256', 'currentSampleSha256'):
            damaged = copy.deepcopy(record)
            damaged['delivery']['events'][-1]['reconciliation'][mutation] = '0' * 64
            with self.assertRaises(ValueError):
                module.delivery_state(self.repo, damaged, reqs)


    def test_decreasing_suspend_offset_requires_reconciliation(self):
        self.start_delivery()
        origin = self.record()['delivery']['clockOrigin']
        sample = dict(origin, utc=(dt.datetime.fromisoformat(origin['utc']) + dt.timedelta(seconds=100)).isoformat(),
                      monotonicNs=origin['monotonicNs'] + 100000000000,
                      boottimeNs=origin['boottimeNs'] + 50000000000)
        # Ensure the absolute sample remains valid even on a host without prior suspend.
        record = self.record()
        record['delivery']['clockOrigin'] = dict(origin, boottimeNs=origin['boottimeNs'] + 100000000000)
        sample['boottimeNs'] += 100000000000
        status = engine().delivery_progress_status(record, sample=sample)
        self.assertTrue(status['reconciliationRequired'])
        self.assertIsNone(status['suspendedSeconds'])

    def test_subsecond_skew_uses_existing_whole_second_comparison(self):
        self.start_delivery()
        record = self.record()
        origin = record['delivery']['clockOrigin']
        origin['boottimeNs'] += 100000000000
        sample = dict(origin, utc=(dt.datetime.fromisoformat(origin['utc']) + dt.timedelta(seconds=2)).isoformat(),
                      monotonicNs=origin['monotonicNs'] + 1000000100,
                      boottimeNs=origin['boottimeNs'] + 1000000000)
        status = engine().delivery_progress_status(record, sample=sample)
        self.assertFalse(status['reconciliationRequired'])
        self.assertEqual(status['suspendedSeconds'], 0)
        # Crossing the original whole-second boundary stays fail-closed.
        sample['boottimeNs'] = origin['boottimeNs'] + 999999999
        self.assertTrue(engine().delivery_progress_status(record, sample=sample)['reconciliationRequired'])

    def test_consumed_terminal_allows_reconciliation_without_relabeling(self):
        self.start_delivery()
        sha = self.ready()
        self.append(self.started(sha))
        sample = self.sample()
        self.append_at(self.terminal(sha, consumed=False), sample)
        before = self.record()['delivery']['events'][-1]
        self.append_at({'eventId': 'consume-old-job', 'kind': 'execution-consumed',
                        'jobId': 'j1', 'outerHandle': 'handle-j1'}, sample)
        event, _, _ = self.event(sample)
        self.append_at(event, sample)
        self.assertEqual(self.record()['delivery']['events'][-3], before)
        self.assertFalse(engine().delivery_progress_status(self.record(), sample=sample)['reconciliationRequired'])

    def test_measured_suspend_before_and_after_reboot_remains_measured(self):
        self.start_delivery()
        origin = self.record()['delivery']['clockOrigin']
        measured = dict(origin, utc=(dt.datetime.fromisoformat(origin['utc']) + dt.timedelta(seconds=110)).isoformat(),
                        monotonicNs=origin['monotonicNs'] + 10000000000,
                        boottimeNs=origin['boottimeNs'] + 110000000000)
        self.append_at({'eventId': 'known-suspend', 'kind': 'plan-changed', 'reason': 'Measured pause',
                        'owner': 'root', 'nextAction': 'Continue reviewed queue'}, measured)
        sample = self.sample(1010)
        event, _, _ = self.event(sample)
        self.append_at(event, sample)
        later = dict(sample, utc=(dt.datetime.fromisoformat(sample['utc']) + dt.timedelta(seconds=110)).isoformat(),
                     monotonicNs=sample['monotonicNs'] + 10000000000,
                     boottimeNs=sample['boottimeNs'] + 110000000000)
        status = engine().delivery_progress_status(self.record(), sample=later)
        self.assertEqual(status['secondsSinceRecordedProgress'], 920)
        self.assertEqual(status['suspendedSeconds'], 200)
        self.assertEqual(status['lastRecordedProgressUTC'], origin['utc'])


if __name__ == '__main__':
    unittest.main()
