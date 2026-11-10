"""Human renewal extends one expiry without restarting the selected delivery."""
import contextlib
import datetime as dt
import io
import json
import os
import sys
import unittest
from unittest.mock import patch

import test_delivery_flow as flow
import test_warlock as fixtures
from test_delivery_flow import DeliveryFixture, engine


class DeliveryAuthorizationTests(DeliveryFixture):
    integrated_changed = flow.DeliveryFlowTests.integrated_changed
    rsi_event = flow.DeliveryFlowTests.rsi_event
    archived_guard = 'implementation/elm-build-loop-v1/loop.py'
    archived_guard_sha = '13216f4226f4fdb2e439604459e860763ce351fa77cec0f6082c30195372dbd6'

    def missing_canonical_guard(self):
        body = (fixtures.PLUGIN.parents[1] / self.archived_guard).read_bytes()
        target = self.fixture.write(self.archived_guard, body.decode())
        self.assertEqual(fixtures.digest(target), self.archived_guard_sha)
        self.fixture.run_git('add', self.archived_guard)
        self.fixture.run_git('commit', '-qm', 'canonical archived guard in original revision')
        # Model the tracked archived blob missing from the checkout at start,
        # without turning it into foreign dirty custody in this isolated fixture.
        self.fixture.run_git('update-index', '--assume-unchanged', self.archived_guard)
        target.unlink()
        return body

    def test_canonical_archived_guard_restoration_is_recorded_without_rewriting_old_rsi(self):
        body = self.missing_canonical_guard()
        sha, revision = self.integrated_changed()
        self.append(self.rsi_event(sha, revision))
        before = self.record()
        self.assertIsNone(before['delivery']['guardHashes'][self.archived_guard])
        (self.repo / self.archived_guard).write_bytes(body)
        sample = self.sample()
        renewal, _, _, _ = self.renewal(sample)
        self.append_at(renewal, sample)
        after = self.record()
        self.assertEqual(after['delivery']['guardHashes'], before['delivery']['guardHashes'])
        self.assertEqual(after['delivery']['events'][:-1], before['delivery']['events'])
        self.assertEqual(after['delivery']['clockOrigin'], before['delivery']['clockOrigin'])
        self.assertEqual(after['delivery']['events'][-1]['guardRestorations'], {self.archived_guard: self.archived_guard_sha})
        self.assertEqual(engine().effective_delivery_guards(after)[self.archived_guard], self.archived_guard_sha)
        self.cli_at(sample, 'handoff')
        module = engine()
        reqs = {row['id']: row for row in module.requirement_document(self.repo)['requirements']}
        for restorations in ({self.archived_guard: '0' * 64},
                             {'window-integration-qa/qa_launch.py': self.archived_guard_sha}):
            damaged = json.loads(json.dumps(after))
            damaged['_recordPath'] = self.record_path
            damaged['delivery']['events'][-1]['guardRestorations'] = restorations
            with self.assertRaisesRegex(ValueError, 'restoration transition'):
                module.delivery_state(self.repo, damaged, reqs)
        later = self.sample(4)
        next_event, _, _, _ = self.renewal(later, '2', previous=renewal['authorizationExpiresUTC'])
        (self.repo / self.archived_guard).write_bytes(body + b'\n# changed after restoration\n')
        self.append_at(next_event, later, ok=False)
        (self.repo / self.archived_guard).write_bytes(body)
        self.append_at(next_event, later)
        self.assertNotIn('guardRestorations', self.record()['delivery']['events'][-1])

    def test_guard_restoration_refuses_wrong_bytes_other_guard_and_caller_override(self):
        body = self.missing_canonical_guard()
        self.start_delivery()
        sample = self.sample()
        renewal, _, _, _ = self.renewal(sample)
        (self.repo / self.archived_guard).write_bytes(body + b'\n# changed\n')
        self.append_at(renewal, sample, ok=False)
        (self.repo / self.archived_guard).write_bytes(body)
        other = self.fixture.write('window-integration-qa/qa_launch.py', 'unauthorized missing guard restoration')
        self.append_at(renewal, sample, ok=False)
        other.unlink()
        injected = dict(renewal, guardRestorations={self.archived_guard: self.archived_guard_sha})
        self.append_at(injected, sample, ok=False)
        target = self.repo / self.archived_guard
        target.unlink()
        alternate = self.fixture.write('.warlock-contributor/guard-copy.py', body.decode())
        target.symlink_to(alternate)
        self.append_at(renewal, sample, ok=False)

    def test_guard_restoration_requires_canonical_blob_in_original_revision(self):
        self.start_delivery()
        body = (fixtures.PLUGIN.parents[1] / self.archived_guard).read_bytes()
        self.fixture.write(self.archived_guard, body.decode())
        sample = self.sample()
        renewal, _, _, _ = self.renewal(sample)
        self.append_at(renewal, sample, ok=False)

    def test_new_rsi_requires_recorded_restored_guard_in_snapshot(self):
        body = self.missing_canonical_guard()
        sha, revision = self.integrated_changed()
        (self.repo / self.archived_guard).write_bytes(body)
        sample = self.sample()
        renewal, _, _, _ = self.renewal(sample)
        self.append_at(renewal, sample)
        rsi = self.rsi_event(sha, revision)
        evidence = json.loads((self.repo / rsi['evidence']['path']).read_text())
        evidence['authorizationExpiresUTC'] = renewal['authorizationExpiresUTC']
        rsi['evidence'] = self.ref('restored-rsi', evidence)
        self.append_at(rsi, sample, ok=False)
        snapshot = json.loads((self.repo / evidence['baselineHarness']['path']).read_text())
        snapshot['fixedInputs']['guardFiles'][self.archived_guard] = {'sha256': self.archived_guard_sha, 'bytes': len(body)}
        evidence['baselineHarness'] = self.ref('restored-harness', snapshot)
        evidence['candidateHarness'] = evidence['baselineHarness']
        comparison = json.loads((self.repo / evidence['comparison']['path']).read_text())
        comparison['baselineSnapshotSha256'] = engine().snapshot_sha256(snapshot)
        comparison['candidateSnapshotSha256'] = comparison['baselineSnapshotSha256']
        comparison['immutableHashes']['guardFiles'] = engine().snapshot_sha256({self.archived_guard: self.archived_guard_sha})
        evidence['comparison'] = self.ref('restored-comparison', comparison)
        rsi['evidence'] = self.ref('complete-restored-rsi', evidence)
        self.append_at(rsi, sample)

    def sample(self, hours=3):
        origin = self.record()['delivery']['clockOrigin']
        return dict(origin, utc=(dt.datetime.fromisoformat(origin['utc']) + dt.timedelta(hours=hours)).isoformat(),
                    monotonicNs=origin['monotonicNs'] + hours * 3600 * 10**9,
                    boottimeNs=origin['boottimeNs'] + hours * 3600 * 10**9)

    def cli_at(self, sample, *args, ok=True):
        module = engine()
        output = io.StringIO()
        argv = [str(fixtures.CHECKER), '--repo', str(self.repo), '--record', self.record_path, '--json', *args]
        with patch.object(sys, 'argv', argv), patch.object(module, 'clock_sample', return_value=sample), \
                patch.dict(os.environ, self.fixture.env, clear=True), contextlib.redirect_stdout(output):
            code = module.main()
        result = json.loads(output.getvalue())
        self.assertEqual(code == 0, ok, result)
        return result

    def append_at(self, event, sample, ok=True):
        self.fixture.write('.warlock-contributor/renewal-event.json', event)
        before = (self.repo / self.record_path).read_bytes()
        result = self.cli_at(sample, 'delivery-event', '--event-file', '.warlock-contributor/renewal-event.json',
                             '--expect-record-sha', fixtures.digest(self.repo / self.record_path),
                             '--expect-selection', '1', ok=ok)
        if not ok:
            self.assertEqual(before, (self.repo / self.record_path).read_bytes())
        return result

    def ref(self, name, value):
        path = '.warlock-contributor/' + name + '.json'
        self.fixture.write(path, value)
        return {'path': path, 'sha256': fixtures.digest(self.repo / path)}

    def renewal(self, sample, suffix='1', previous=None):
        record = self.record()
        authorized = (dt.datetime.fromisoformat(sample['utc']) - dt.timedelta(seconds=1)).isoformat()
        expiry = (dt.datetime.fromisoformat(sample['utc']) + dt.timedelta(hours=24)).isoformat()
        human = {'schema': 1, 'kind': 'human-authorization', 'action': 'renew-same-record',
                 'authorizedUTC': authorized, 'authorizationExpiresUTC': expiry,
                 'text': 'Resume the same selected work for the next 24 hours.'}
        goal = {'schema': 1, 'status': 'active', 'observedUTC': sample['utc']}
        module = engine()
        evidence = {'schema': 1, 'kind': 'explicit-human-authorization-renewal',
                    'recordPath': self.record_path, 'owner': record['owner'], 'startedUTC': record['startedUTC'],
                    'deliveryIdentitySha256': module.json_sha256(module.delivery_identity(record)),
                    'previousExpiresUTC': previous or record['delivery']['authorizationExpiresUTC'],
                    'authorizationExpiresUTC': expiry, 'authorizedUTC': authorized,
                    'humanRequest': self.ref('human-' + suffix, human),
                    'goalObservation': self.ref('goal-' + suffix, goal)}
        event = {'eventId': 'renew-' + suffix, 'kind': 'authorization-renewed',
                 'authorizationExpiresUTC': expiry, 'evidence': self.ref('renewal-' + suffix, evidence)}
        return event, evidence, human, goal

    def test_expired_ready_candidate_renews_same_history_without_clock_or_identity_reset(self):
        self.start_delivery()
        candidate = self.ready()
        before = self.record()
        state_path = self.repo / 'docs/warlock-build-loop/v2/STATE.json'
        state_before = state_path.read_bytes()
        sample = self.sample()
        old_progress = engine().delivery_progress_status(before, sample=sample)
        self.assertTrue(old_progress['authorizationExpired'])
        self.precheck_at(sample, ok=False)
        event, _, _, _ = self.renewal(sample)
        result = self.append_at(event, sample)
        after = self.record()
        self.assertEqual(after['delivery']['events'][:-1], before['delivery']['events'])
        self.assertEqual(after['delivery']['clockOrigin'], before['delivery']['clockOrigin'])
        self.assertEqual(after['delivery']['authorizationExpiresUTC'], before['delivery']['authorizationExpiresUTC'])
        self.assertEqual(engine().record_identity(after, self.record_path), engine().record_identity(before, self.record_path))
        self.assertEqual(state_before, state_path.read_bytes())
        progress = result['nextRootAction']['progress']
        self.assertFalse(progress['authorizationExpired'])
        self.assertTrue(progress['planChangeRequired'])
        self.assertEqual(progress['secondsSinceRecordedProgress'], old_progress['secondsSinceRecordedProgress'])
        self.assertEqual(progress['lastRecordedProgressUTC'], old_progress['lastRecordedProgressUTC'])
        self.assertEqual(progress['effectiveAuthorizationExpiresUTC'], event['authorizationExpiresUTC'])
        self.assertEqual(result['nextRootAction']['candidateSha256'], candidate)
        self.assertEqual(result['nextRootAction']['kind'], 'execute')
        self.precheck_at(sample)
        self.fixture.cli('--record', '.warlock-contributor/replacement.json', 'start', '--owner', 'root',
                         '--workflow-policy', '2', '--delivery-plan-file', '.warlock-contributor/delivery-plan.json', ok=False)
        self.cli_at(sample, 'delivery-select', '--expect-state-sha', fixtures.digest(state_path))

    def precheck_at(self, sample, ok=True):
        return self.cli_at(sample, 'delivery-precheck', '--candidate', 'c1', '--scope', 'cpu',
                           '--expect-selection', '1', ok=ok)

    def test_renewal_refuses_bad_scope_chronology_evidence_and_paused_goal(self):
        self.start_delivery()
        self.ready()
        sample = self.sample()
        cases = [('deliveryIdentitySha256', '0' * 64), ('recordPath', '.warlock-contributor/another.json'),
                 ('owner', 'another'), ('previousExpiresUTC', sample['utc']),
                 ('authorizedUTC', '2000-01-01T00:00:00+00:00'),
                 ('authorizedUTC', '2100-01-01T00:00:00+00:00'),
                 ('authorizationExpiresUTC', self.record()['delivery']['authorizationExpiresUTC'])]
        for index, (field, value) in enumerate(cases):
            with self.subTest(field=field, value=value):
                event, evidence, _, _ = self.renewal(sample, str(index))
                evidence[field] = value
                event['evidence'] = self.ref('bad-renewal-' + str(index), evidence)
                if field == 'authorizationExpiresUTC':
                    event[field] = value
                self.append_at(event, sample, ok=False)
        for status in ('paused', 'complete', 'blocked'):
            with self.subTest(status=status):
                event, evidence, _, goal = self.renewal(sample, status)
                goal['status'] = status
                evidence['goalObservation'] = self.ref('bad-goal-' + status, goal)
                event['evidence'] = self.ref('bad-evidence-' + status, evidence)
                self.append_at(event, sample, ok=False)
        event, evidence, human, _ = self.renewal(sample, 'queued')
        human['kind'] = 'queued-agent-message'
        evidence['humanRequest'] = self.ref('queued-request', human)
        event['evidence'] = self.ref('queued-evidence', evidence)
        self.append_at(event, sample, ok=False)
        event, _, _, _ = self.renewal(sample, 'hash')
        event['evidence']['sha256'] = '0' * 64
        self.append_at(event, sample, ok=False)

    def test_second_renewal_requires_new_human_request_and_prior_effective_deadline(self):
        self.start_delivery()
        sample = self.sample()
        first, _, _, _ = self.renewal(sample)
        self.append_at(first, sample)
        later = self.sample(4)
        stale, _, _, _ = self.renewal(later, '2')
        self.append_at(stale, later, ok=False)
        valid, evidence, _, _ = self.renewal(later, '3', previous=first['authorizationExpiresUTC'])
        first_evidence = json.loads((self.repo / first['evidence']['path']).read_text())
        evidence['authorizedUTC'] = first_evidence['authorizedUTC']
        evidence['humanRequest'] = first_evidence['humanRequest']
        valid['evidence'] = self.ref('reused-human', evidence)
        self.append_at(valid, later, ok=False)
        valid, _, _, _ = self.renewal(later, '4', previous=first['authorizationExpiresUTC'])
        self.append_at(valid, later)
        self.assertEqual(engine().effective_delivery_authorization(self.record()), valid['authorizationExpiresUTC'])

    def test_renewal_does_not_waive_clock_reconciliation(self):
        self.start_delivery()
        sample = dict(self.sample(), bootId='another-boot')
        event, _, _, _ = self.renewal(sample)
        result = self.append_at(event, sample)
        self.assertEqual(result['nextRootAction']['kind'], 'reconcile-clock')
        self.assertFalse(result['nextRootAction']['executionAuthorized'])
        self.assertTrue(result['nextRootAction']['progress']['reconciliationRequired'])

    def test_renewal_never_migrates_legacy_stopped_record(self):
        self.fixture.cli('--record', self.record_path, 'start', '--owner', 'root')
        for _ in range(2):
            self.fixture.cli('--record', self.record_path, 'record', '--outcome', 'qualification', '--summary', 'No observed delivery')
        before = (self.repo / self.record_path).read_bytes()
        self.fixture.write('.warlock-contributor/renewal-event.json', {'eventId': 'renew', 'kind': 'authorization-renewed',
            'authorizationExpiresUTC': '2100-01-01T00:00:00+00:00', 'evidence': {'path': 'foreign.txt', 'sha256': fixtures.digest(self.repo / 'foreign.txt')}})
        self.fixture.cli('--record', self.record_path, 'delivery-event', '--event-file', '.warlock-contributor/renewal-event.json',
                         '--expect-record-sha', fixtures.digest(self.repo / self.record_path), '--expect-selection', '1', ok=False)
        self.assertEqual(before, (self.repo / self.record_path).read_bytes())
        self.assertTrue(engine().progress_status(self.record())['investigationNeedsChange'])

    def test_renewal_preserves_historical_rsi_authorization_binding(self):
        sha, revision = self.integrated_changed()
        self.append(self.rsi_event(sha, revision))
        prior = self.record()['delivery']['events']
        sample = self.sample()
        event, _, _, _ = self.renewal(sample)
        self.append_at(event, sample)
        self.assertEqual(self.record()['delivery']['events'][:-1], prior)
        self.cli_at(sample, 'handoff')

    def test_new_rsi_must_bind_effective_renewed_authorization(self):
        sha, revision = self.integrated_changed()
        sample = self.sample()
        renewal, _, _, _ = self.renewal(sample)
        self.append_at(renewal, sample)
        rsi = self.rsi_event(sha, revision)
        self.append_at(rsi, sample, ok=False)
        evidence = json.loads((self.repo / rsi['evidence']['path']).read_text())
        evidence['authorizationExpiresUTC'] = renewal['authorizationExpiresUTC']
        rsi['evidence'] = self.ref('renewed-rsi', evidence)
        self.append_at(rsi, sample)


if __name__ == '__main__':
    unittest.main()
