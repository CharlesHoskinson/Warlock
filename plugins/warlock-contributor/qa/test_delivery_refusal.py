"""Pre-spawn refusals retain evidence without manufacturing an execution job."""
import copy
import datetime as dt
import json
from unittest.mock import patch

import test_delivery_flow as flow
import test_warlock as fixtures


class DeliveryRefusalTests(flow.DeliveryFixture):
    def setUp(self):
        super().setUp()
        self.start_delivery()
        self.sha = self.ready()

    def refusal(self, handle='outer-refused-1', changes=None, review_changes=None):
        candidate = self.record()['delivery']['events'][0]['candidate']
        raw = '.warlock-contributor/pre-spawn-raw.txt'
        self.fixture.write(raw, 'Protected command differs\n')
        report = {
            'schema': 1, 'classification': 'pre-spawn-refused',
            'candidateSha256': self.sha, 'scope': candidate['scope'],
            'manifestSha256': flow.engine().json_sha256(candidate['manifest']),
            'fixtureSha256': flow.engine().json_sha256(candidate['manifest']['fixtures']),
            'outerHandle': handle, 'outerHandleConsumed': True, 'exit': 2,
            'actualLaunch': None, 'jobId': None,
            'observedUTC': dt.datetime.now(dt.timezone.utc).isoformat(),
            'rawEvidence': {'path': raw, 'sha256': fixtures.digest(self.repo / raw)}}
        report.update(changes or {})
        path = '.warlock-contributor/pre-spawn-report.json'
        self.fixture.write(path, report)
        reference = {'path': path, 'sha256': fixtures.digest(self.repo / path)}
        review = {
            'schema': 1, 'reviewer': 'independent-reviewer', 'disposition': 'accepted',
            'candidateSha256': self.sha, 'scope': candidate['scope'], 'report': reference,
            'conclusion': 'no-process-started',
            'observedUTC': dt.datetime.now(dt.timezone.utc).isoformat()}
        review.update(review_changes or {})
        rp = '.warlock-contributor/pre-spawn-review.json'
        self.fixture.write(rp, review)
        return {'kind': 'execution-refused', 'eventId': 'refused-' + handle,
                'candidateSha256': self.sha, 'outerHandle': handle,
                'report': reference,
                'review': {'path': rp, 'sha256': fixtures.digest(self.repo / rp)}}

    def test_refusal_retains_accepted_review_without_job_and_allows_new_identity(self):
        before = self.record()
        self.append(self.refusal())
        record = self.record()
        self.assertEqual(record['delivery']['events'][:-1], before['delivery']['events'])
        self.assertEqual(record['delivery']['clockOrigin'], before['delivery']['clockOrigin'])
        self.assertEqual(record['delivery']['authorizationExpiresUTC'], before['delivery']['authorizationExpiresUTC'])
        module = flow.engine()
        reqs, _ = module.context(self.repo)
        state = module.delivery_state(self.repo, record, reqs)
        self.assertIsNone(state['job'])
        self.assertIsNone(state['terminal'])
        self.assertEqual(state['review']['disposition'], 'accepted')
        self.assertEqual(state['refusal']['classification'], 'pre-spawn-refused')
        self.assertEqual(module.delivery_next_action(self.repo, record, reqs)['kind'], 'correct')
        self.assertNotIn('deliveryAdvance', record['delivery']['events'][-1])
        self.assertEqual(module.progress_status(record)['lastRecordedProgressUTC'], before['delivery']['clockOrigin']['utc'])
        self.candidate('corrected-new-id')

    def test_old_core_ready_slot_reproducer(self):
        self.append(self.refusal())
        candidate = copy.deepcopy(self.record()['delivery']['events'][0]['candidate'])
        candidate['id'] = 'corrected-ready'
        self.append({'kind': 'candidate', 'eventId': 'corrected', 'candidate': candidate})
        self.assertEqual(self.record()['delivery']['events'][-1]['candidate']['id'], 'corrected-ready')

    def test_refused_candidate_cannot_start_or_integrate(self):
        self.append(self.refusal())
        self.append(self.started(self.sha), ok=False)
        self.append({'kind': 'integrated', 'eventId': 'fake-integration',
                     'candidateSha256': self.sha,
                     'revision': self.fixture.run_git('rev-parse', 'HEAD')}, ok=False)
        self.precheck(ok=False)

    def test_started_or_terminal_unconsumed_job_refuses(self):
        self.append(self.started(self.sha))
        self.append(self.refusal(), ok=False)
        self.append(self.terminal(self.sha, consumed=False, classification='failed', exit_code=1), ok=False)
        # A real terminal report needs its existing failure signature.
        event = self.terminal(self.sha, consumed=False, classification='unknown', exit_code=1)
        rp = self.repo / event['report']['path']
        report = json.loads(rp.read_text())
        report['failureSignature'] = 'actual-started-job'
        self.fixture.write(event['report']['path'], report)
        event['report']['sha256'] = fixtures.digest(rp)
        self.append(event)
        self.append(self.refusal(), ok=False)

    def test_consumed_real_job_is_not_a_pre_spawn_refusal(self):
        self.append(self.started(self.sha))
        self.append(self.terminal(self.sha))
        self.append(self.refusal(), ok=False)

    def test_wrong_candidate_event_or_report_refuses(self):
        event = self.refusal()
        event['candidateSha256'] = '0' * 64
        self.append(event, ok=False)
        self.append(self.refusal(changes={'candidateSha256': '0' * 64}), ok=False)

    def test_pass_launch_job_unconsumed_or_wrong_bindings_refuse(self):
        for changes in ({'exit': 0}, {'exit': True}, {'classification': 'pass'},
                        {'actualLaunch': {'pid': 123}}, {'jobId': 'fake-job'},
                        {'outerHandleConsumed': False}, {'outerHandle': 'other'},
                        {'scope': 'native'}, {'manifestSha256': '0' * 64},
                        {'fixtureSha256': '0' * 64}, {'schema': True}):
            with self.subTest(changes=changes):
                self.append(self.refusal(changes=changes), ok=False)

    def test_missing_changed_or_empty_raw_evidence_refuses(self):
        for mode in ('missing', 'changed', 'empty'):
            event = self.refusal()
            raw = self.repo / '.warlock-contributor/pre-spawn-raw.txt'
            if mode == 'missing':
                raw.unlink()
            else:
                self.fixture.write(str(raw.relative_to(self.repo)), '' if mode == 'empty' else 'changed')
            with self.subTest(mode=mode):
                self.append(event, ok=False)

    def test_independent_review_required_and_bound_to_report(self):
        for changes in ({'reviewer': 'root'}, {'disposition': 'changes-required'},
                        {'candidateSha256': '0' * 64}, {'scope': 'native'},
                        {'conclusion': 'passed'}, {'report': {'path': 'other', 'sha256': '0' * 64}}):
            with self.subTest(changes=changes):
                self.append(self.refusal(review_changes=changes), ok=False)
        event = self.refusal()
        del event['review']
        self.append(event, ok=False)

    def test_duplicate_refusal_and_candidate_id_refuse(self):
        event = self.refusal()
        self.append(event)
        event['eventId'] = 'duplicate-refusal'
        self.append(event, ok=False)
        candidate = self.record()['delivery']['events'][0]['candidate']
        self.append({'kind': 'candidate', 'eventId': 'duplicate-candidate', 'candidate': candidate}, ok=False)

    def test_consumed_refusal_handle_cannot_be_used_for_real_job(self):
        self.append(self.refusal())
        new = self.candidate('c2')
        self.append(self.review(new))
        event = self.started(new, 'j2')
        event['outerHandle'] = 'outer-refused-1'
        self.append(event, ok=False)

    def test_refusal_cannot_reuse_previous_real_job_handle(self):
        self.append(self.started(self.sha))
        self.append(self.terminal(self.sha, classification='expected-red', exit_code=1))
        self.sha = self.candidate('c2')
        self.append(self.review(self.sha))
        self.append(self.refusal(handle='handle-j1'), ok=False)

    def test_refusal_does_not_clear_defer_or_plan_change(self):
        self.append({'eventId': 'defer', 'kind': 'deferred', 'reason': 'paused work',
                     'owner': 'Root', 'nextAction': 'Wait for Root'})
        self.append(self.refusal())
        module = flow.engine()
        record = self.record()
        reqs, _ = module.context(self.repo)
        sample = dict(record['delivery']['events'][-1]['clockSample'])
        sample['monotonicNs'] += 2800 * 1000000000
        sample['boottimeNs'] += 2800 * 1000000000
        sample['utc'] = (dt.datetime.fromisoformat(sample['utc']) + dt.timedelta(seconds=2800)).isoformat()
        with patch.object(module, 'clock_sample', return_value=sample):
            self.assertTrue(module.progress_status(record)['planChangeRequired'])
            self.assertEqual(module.delivery_next_action(self.repo, record, reqs)['kind'], 'deferred')

    def test_refusal_replay_rejects_progress_injection_and_changed_evidence(self):
        self.append(self.refusal())
        module = flow.engine()
        reqs, _ = module.context(self.repo)
        record = self.record()
        record['delivery']['events'][-1]['deliveryAdvance'] = '0' * 64
        with self.assertRaises(ValueError):
            module.delivery_state(self.repo, record, reqs)
        self.fixture.write('.warlock-contributor/pre-spawn-raw.txt', 'changed retained bytes')
        with self.assertRaises(ValueError):
            module.delivery_state(self.repo, self.record(), reqs)

    def test_report_and_review_cannot_predate_reviewed_candidate_or_be_future(self):
        for field in ('report', 'review'):
            for timestamp in ('2000-01-01T00:00:00+00:00', '2100-01-01T00:00:00+00:00'):
                kwargs = {'changes' if field == 'report' else 'review_changes': {'observedUTC': timestamp}}
                with self.subTest(field=field, timestamp=timestamp):
                    self.append(self.refusal(**kwargs), ok=False)
