"""Source-bound delivery transitions use the existing participant, never a ledger."""
import datetime as dt
import importlib.util
import json
import unittest
from unittest.mock import patch

import test_warlock as fixtures


def engine():
    spec = importlib.util.spec_from_file_location('delivery_engine', fixtures.CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeliveryFixture(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        self.record_path = '.warlock-contributor/delivery.json'
        self.source = 'implementation/warlock/src/Desktop.elm'
        self.plan = {'schema': 1,
                     'authorizationExpiresUTC': (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=2)).isoformat(),
                     'journey': {'userOutcome': 'Visible feedback',
                                 'originalPairs': [{'requirement': 'ELM-UI-007', 'scenario': 'restore-pending'}],
                                 'inputSteps': ['Request restore'], 'expectedObservation': 'Pending is visible'}}
        self.fixture.write('.warlock-contributor/delivery-plan.json', self.plan)

    def start_delivery(self):
        result = self.fixture.cli('--record', self.record_path, 'start', '--owner', 'root',
                                  '--workflow-policy', '2', '--delivery-plan-file', '.warlock-contributor/delivery-plan.json')
        self.fixture.cli('--record', self.record_path, 'delivery-select', '--expect-state-sha',
                         fixtures.digest(self.repo / 'docs/warlock-build-loop/v2/STATE.json'))
        return result

    def record(self):
        return json.loads((self.repo / self.record_path).read_text())

    def append(self, event, ok=True, **kwargs):
        self.fixture.write('.warlock-contributor/delivery-event.json', event)
        expected = kwargs.get('expected', fixtures.digest(self.repo / self.record_path))
        return self.fixture.cli('--record', self.record_path, 'delivery-event',
                                '--event-file', '.warlock-contributor/delivery-event.json',
                                '--expect-record-sha', expected, '--expect-selection', str(kwargs.get('selection', 1)), ok=ok)

    def candidate(self, identity='c1', scope='cpu', baseline=None):
        for name in ('fixture.txt', 'runner.py', 'profile.json'):
            self.fixture.write('.warlock-contributor/' + name, 'bounded fixture\n')
        manifest = {kind: {path: fixtures.digest(self.repo / path)} for kind, path in (
            ('sources', self.source), ('fixtures', '.warlock-contributor/fixture.txt'),
            ('runners', '.warlock-contributor/runner.py'), ('profiles', '.warlock-contributor/profile.json'))}
        candidate = {'id': identity, 'manifest': manifest, 'scope': scope,
                     'argv': ['python3', '-B', '.warlock-contributor/runner.py'],
                     'expectedObservation': 'Pending is visible', 'nativePrerequisites': []}
        candidate['manifest']['sources'] = {name: fixtures.digest(self.repo / name) if (self.repo / name).exists() else None
                                            for name in self.record()['slice']['paths']}
        if baseline is not None:
            candidate['baselineCandidateSha256'] = baseline
        self.append({'eventId': 'candidate-' + identity, 'kind': 'candidate', 'candidate': candidate})
        return self.record()['delivery']['events'][-1]['candidateSha256']

    def review(self, candidate_sha, reviewer='reviewer', scope='cpu'):
        path = '.warlock-contributor/review-' + candidate_sha + '.json'
        self.fixture.write(path, {
            'candidateSha256': candidate_sha, 'reviewer': reviewer,
            'disposition': 'accepted', 'scope': scope})
        return {'eventId': 'review-' + candidate_sha[:8], 'kind': 'review',
                'candidateSha256': candidate_sha,
                'review': {'path': path, 'sha256': fixtures.digest(self.repo / path)}}

    def ready(self):
        sha = self.candidate()
        self.append(self.review(sha))
        return sha

    def precheck(self, ok=True, scope='cpu'):
        return self.fixture.cli('--record', self.record_path, 'delivery-precheck',
                                '--candidate', 'c1', '--scope', scope, '--expect-selection', '1', ok=ok)

    def started(self, sha, job='j1'):
        return {'eventId': 'start-' + job, 'kind': 'execution-started',
                'candidateSha256': sha, 'jobId': job, 'outerHandle': 'handle-' + job}

    def terminal(self, sha, consumed=True, job='j1', classification='pass', exit_code=0):
        candidate = next(e['candidate'] for e in self.record()['delivery']['events']
                         if e['kind'] == 'candidate' and e['candidateSha256'] == sha)
        report = {'terminal': True, 'jobId': job, 'candidateSha256': sha, 'scope': 'cpu',
                  'manifestSha256': engine().json_sha256(candidate['manifest']),
                  'fixtureSha256': engine().json_sha256(candidate['manifest']['fixtures']),
                  'exit': exit_code, 'classification': classification}
        path = '.warlock-contributor/terminal-' + job + '.json'
        self.fixture.write(path, report)
        return {'eventId': 'finish-' + job, 'kind': 'execution-finished', 'candidateSha256': sha,
                'jobId': job, 'outerHandleConsumed': consumed,
                'report': {'path': path, 'sha256': fixtures.digest(self.repo / path)}}


class DeliveryFlowTests(DeliveryFixture):
    def test_extension_preserves_integrated_rsi_history_but_requires_new_selection_and_manifest(self):
        sha, revision = self.integrated_changed()
        self.append(self.rsi_event(sha, revision))
        history = self.record()['delivery']['events']
        extra = 'implementation/warlock/src/Additional.elm'
        self.fixture.cli('--record', self.record_path, 'extend', '--path', extra,
                         '--reason', 'Same journey needs an additional product module')
        self.assertEqual(self.record()['delivery']['events'], history)
        packet = json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)
        self.assertEqual(packet['errors'], [])
        candidate = json.loads(json.dumps(history[0]['candidate']))
        candidate['id'] = 'c2'
        event = {'eventId': 'candidate-c2', 'kind': 'candidate', 'candidate': candidate}
        stale = self.append(event, ok=False)
        self.assertIn('Canonical delivery selection differs', stale.stdout + stale.stderr)
        state_path = self.repo / 'docs/warlock-build-loop/v2/STATE.json'
        self.fixture.cli('--record', self.record_path, 'delivery-select',
                         '--expect-state-sha', fixtures.digest(state_path))
        self.assertEqual(json.loads(state_path.read_text())['activeSelection']['generation'], 2)
        incomplete = self.append(event, selection=2, ok=False)
        self.assertIn('every declared source', incomplete.stdout + incomplete.stderr)
        candidate['manifest']['sources'][extra] = None
        self.append(event, selection=2)
        self.assertEqual(self.record()['delivery']['events'][:-1], history)

    def test_extension_keeps_ready_history_but_refuses_incomplete_execution_precheck(self):
        self.start_delivery()
        self.ready()
        self.fixture.cli('--record', self.record_path, 'extend', '--path',
                         'implementation/warlock/src/Additional.elm', '--reason', 'Additional dependency')
        state_path = self.repo / 'docs/warlock-build-loop/v2/STATE.json'
        self.fixture.cli('--record', self.record_path, 'delivery-select',
                         '--expect-state-sha', fixtures.digest(state_path))
        result = self.fixture.cli('--record', self.record_path, 'delivery-precheck',
                                  '--candidate', 'c1', '--scope', 'cpu', '--expect-selection', '2', ok=False)
        self.assertIn('every declared source', result.stdout + result.stderr)
        candidate = self.record()['delivery']['events'][0]['candidate']
        candidate['manifest']['sources']['implementation/warlock/src/Foreign.elm'] = None
        with self.assertRaisesRegex(ValueError, 'owned'):
            engine().validate_delivery_candidate(self.repo, self.record(), candidate)

    def test_absent_future_product_file_red_then_same_fixture_green(self):
        new_source = 'implementation/warlock/haskell/runtime/src/Warlock/New.hs'
        state_path = 'docs/warlock-build-loop/v2/STATE.json'
        state = json.loads((self.repo / state_path).read_text())
        state['activeSlice']['paths'].append(new_source)
        self.fixture.write(state_path, state)
        self.fixture.run_git('add', state_path)
        self.fixture.run_git('commit', '-qm', 'declare future product path')
        self.start_delivery()
        baseline = self.ready()
        self.append(self.started(baseline))
        self.append(self.terminal(baseline, classification='expected-red', exit_code=1))
        self.assertNotIn('deliveryAdvance', self.record()['delivery']['events'][-1])
        self.fixture.write(new_source, 'module Warlock.New where\nnew = 1\n')
        green = self.candidate('c2', baseline=baseline)
        self.append(self.review(green))
        self.append(self.started(green, 'j2'))
        self.append(self.terminal(green, job='j2'))
        self.assertEqual(json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)['nextRootAction']['kind'], 'integrate')

    def test_ready_queue_after_45_minutes_keeps_root_execution_action(self):
        self.start_delivery()
        self.ready()
        module = engine()
        record = self.record()
        record['_recordPath'] = self.record_path
        reqs, state = module.context(self.repo)
        sample = dict(record['delivery']['clockOrigin'])
        sample['monotonicNs'] += 2800 * 1000000000
        sample['boottimeNs'] += 2800 * 1000000000
        sample['utc'] = (dt.datetime.fromisoformat(sample['utc']) + dt.timedelta(seconds=2800)).isoformat()
        with patch.object(module, 'clock_sample', return_value=sample):
            self.assertTrue(module.progress_status(record)['planChangeRequired'])
            self.assertFalse(module.progress_status(record)['investigationNeedsChange'])
            self.assertEqual(module.delivery_next_action(self.repo, record, reqs)['kind'], 'execute')
            record['delivery']['events'].append({'eventId': 'revised-plan', 'kind': 'plan-changed',
                'sequence': len(record['delivery']['events']) + 1, 'clockSample': sample, 'atUTC': sample['utc'],
                'reason': 'Root queue delay', 'owner': 'Root', 'nextAction': 'Execute ready candidate'})
            self.assertEqual(module.validate(self.repo, record, reqs, state)[0], [])
            self.assertEqual(module.contribution_report(self.repo, record, reqs, state)['errors'], [])
            self.assertEqual(module.delivery_next_action(self.repo, record, reqs)['kind'], 'execute')

    def test_unchanged_integration_is_not_delivery_progress(self):
        self.start_delivery()
        sha = self.ready()
        self.append(self.started(sha))
        self.append(self.terminal(sha))
        self.append({'eventId': 'integration', 'kind': 'integrated', 'candidateSha256': sha,
                     'revision': self.fixture.run_git('rev-parse', 'HEAD')})
        self.assertNotIn('deliveryAdvance', self.record()['delivery']['events'][-1])
        self.assertTrue(self.record()['delivery']['events'][-1].get('sliceCompleted'))
        packet = json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)
        self.assertEqual(packet['nextRootAction']['kind'], 'rsi')
        self.assertEqual(packet['progress']['lastRecordedProgressUTC'], self.record()['delivery']['clockOrigin']['utc'])
        with self.assertRaises(AssertionError):
            self.candidate('unchanged-next')

    def test_changed_tested_integration_and_real_journey_observation(self):
        self.start_delivery()
        self.fixture.write(self.source, 'module Desktop exposing (identity)\nidentity = "new"\n')
        sha = self.ready()
        self.append(self.started(sha))
        self.append(self.terminal(sha))
        self.fixture.run_git('add', self.source)
        self.fixture.run_git('commit', '-qm', 'owned product change')
        revision = self.fixture.run_git('rev-parse', 'HEAD')
        self.append({'eventId': 'integration', 'kind': 'integrated', 'candidateSha256': sha, 'revision': revision})
        self.assertIn('deliveryAdvance', self.record()['delivery']['events'][-1])
        observation = {'candidateSha256': sha, 'revision': revision, 'outcome': 'partial',
                       'inputRoute': 'Real isolated keyboard', 'observedBehavior': 'Pending visible',
                       'missingObligations': ['Actual AT observation']}
        self.fixture.write('.warlock-contributor/observation.json', observation)
        self.append({'eventId': 'journey', 'kind': 'journey-observed', 'candidateSha256': sha,
                     'observation': {'path': '.warlock-contributor/observation.json',
                                     'sha256': fixtures.digest(self.repo / '.warlock-contributor/observation.json')}})
        self.assertEqual(json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)['nextRootAction']['kind'], 'rsi')

    def integrated_changed(self):
        self.start_delivery()
        self.fixture.write(self.source, 'module Desktop exposing (identity)\nidentity = "RSI"\n')
        sha = self.ready()
        self.append(self.started(sha))
        self.append(self.terminal(sha))
        self.fixture.run_git('add', self.source)
        self.fixture.run_git('commit', '-qm', 'tested owned change')
        revision = self.fixture.run_git('rev-parse', 'HEAD')
        self.append({'eventId': 'integration', 'kind': 'integrated', 'candidateSha256': sha, 'revision': revision})
        return sha, revision

    def passing_journey(self):
        self.plan['journey']['inputSteps'] = ['Request restore', 'Inspect pending response']
        self.fixture.write('.warlock-contributor/delivery-plan.json', self.plan)
        sha, revision = self.integrated_changed()
        plan_sha = engine().json_sha256(self.record()['delivery']['journey'])
        steps = []
        for index, step in enumerate(self.plan['journey']['inputSteps']):
            path = '.warlock-contributor/journey-step-' + str(index) + '.txt'
            self.fixture.write(path, 'Observed input and response for ' + step + '\n')
            steps.append({'stepIndex': index, 'inputStep': step, 'outcome': 'pass',
                          'evidence': {'path': path, 'sha256': fixtures.digest(self.repo / path)}})
        cleanup = {'candidateSha256': sha, 'revision': revision, 'terminal': True,
                   'classification': 'normal', 'exit': 0, 'timedOut': False, 'forcedCleanup': False}
        path = '.warlock-contributor/journey-cleanup.json'
        self.fixture.write(path, cleanup)
        observation = {'candidateSha256': sha, 'revision': revision, 'outcome': 'pass',
                       'inputRoute': 'Real isolated keyboard', 'observedBehavior': 'Pending visible',
                       'missingObligations': [], 'journeyPlanSha256': plan_sha, 'steps': steps,
                       'cleanup': {'path': path, 'sha256': fixtures.digest(self.repo / path)}}
        return observation, cleanup

    def observe_journey(self, observation, ok=True):
        path = '.warlock-contributor/journey-observation.json'
        self.fixture.write(path, observation)
        before = (self.repo / self.record_path).read_bytes()
        result = self.append({'eventId': 'journey', 'kind': 'journey-observed',
                              'candidateSha256': observation['candidateSha256'],
                              'observation': {'path': path, 'sha256': fixtures.digest(self.repo / path)}}, ok=ok)
        if not ok:
            self.assertEqual((self.repo / self.record_path).read_bytes(), before)
        return result

    def test_journey_pass_binds_all_planned_steps_and_normal_cleanup(self):
        observation, _ = self.passing_journey()
        self.observe_journey(observation)
        packet = json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)
        self.assertEqual(packet['nextRootAction']['kind'], 'rsi')
        self.assertFalse(packet['nextRootAction']['acceptanceInferred'])

    def test_journey_pass_refuses_missing_reordered_unproven_steps_and_fake_cleanup(self):
        observation, cleanup = self.passing_journey()
        cases = []
        for field in ('journeyPlanSha256', 'steps', 'cleanup'):
            value = json.loads(json.dumps(observation))
            value.pop(field)
            cases.append((field + '-missing', value))
        for name, field, value in (
                ('wrong-plan', 'journeyPlanSha256', '0' * 64),
                ('missing-step', 'steps', observation['steps'][:1]),
                ('reordered-step', 'steps', list(reversed(observation['steps']))),
                ('duplicate-step', 'steps', [observation['steps'][0]] * 2),
                ('remaining-obligation', 'missingObligations', ['real host not observed'])):
            modified = json.loads(json.dumps(observation))
            modified[field] = value
            cases.append((name, modified))
        unproven = json.loads(json.dumps(observation))
        unproven['steps'][0]['evidence']['sha256'] = '0' * 64
        cases.append(('unproven-step', unproven))
        failed = json.loads(json.dumps(observation))
        failed['steps'][0]['outcome'] = 'failed'
        cases.append(('failed-step', failed))
        for name, value in cases:
            with self.subTest(name=name):
                self.observe_journey(value, ok=False)
        for field, value in (('candidateSha256', '0' * 64), ('revision', '0' * 40),
                             ('terminal', False), ('classification', 'timeout'), ('exit', 1),
                             ('exit', False), ('timedOut', True), ('forcedCleanup', True)):
            with self.subTest(cleanupField=field):
                modified = dict(cleanup, **{field: value})
                path = observation['cleanup']['path']
                self.fixture.write(path, modified)
                observation['cleanup']['sha256'] = fixtures.digest(self.repo / path)
                self.observe_journey(observation, ok=False)
        self.fixture.write(observation['cleanup']['path'], cleanup)
        observation['cleanup']['sha256'] = fixtures.digest(self.repo / observation['cleanup']['path'])
        self.observe_journey(observation)

    def rsi_event(self, sha, revision, disposition='no-change'):
        def ref(name, value):
            path = '.warlock-contributor/' + name
            self.fixture.write(path, value)
            return {'path': path, 'sha256': fixtures.digest(self.repo / path)}
        plugin_data = engine().plugin_snapshot(self.repo)
        plugin = ref('baseline-plugin.json', plugin_data)
        candidate = next(e['candidate'] for e in self.record()['delivery']['events'] if e['kind'] == 'candidate')
        guards = {name: value for name, value in self.record()['delivery']['guardHashes'].items() if value is not None}
        maps = {'sourceFiles': candidate['manifest']['sources'], 'pluginBaselineFiles': plugin_data['files'],
                'oracleFiles': guards, 'guardFiles': {}, 'taskFiles': candidate['manifest']['fixtures'], 'authorizationFiles': {}}
        snapshot = {'checkNames': ['stale-fixture-refuses'],
                    'fixedInputs': {role: {name: {'sha256': value, 'bytes': (self.repo / name).stat().st_size}
                                          for name, value in files.items()} for role, files in maps.items()}}
        harness = ref('baseline-harness.json', snapshot)
        regression = ref('regression.json', {'schema': 1, 'pluginSha256': plugin_data['sha256'],
            'terminal': True, 'exit': 0, 'testsRun': 25, 'failures': 0})
        comparison = ref('comparison.json', {'schema': 1, 'kind': 'same-task-harness-comparison',
            'completedCandidateSha256': sha, 'baselinePluginSha256': plugin_data['sha256'],
            'baselineSnapshotSha256': engine().snapshot_sha256(snapshot),
            'candidateSnapshotSha256': engine().snapshot_sha256(snapshot),
            'immutableHashes': {role: engine().snapshot_sha256(files) for role, files in maps.items()},
            'checks': [{'name': 'stale-fixture-refuses', 'baselinePassed': True, 'candidatePassed': True}],
            'regression': regression})
        evidence = ref('rsi.json', {'schema': 1, 'candidateSha256': sha, 'integrationRevision': revision,
            'disposition': disposition, 'baselinePlugin': plugin, 'baselineHarness': harness, 'candidateHarness': harness,
            'authorizationExpiresUTC': self.record()['delivery']['authorizationExpiresUTC'],
            'resultPlugin': plugin, 'proposedChange': 'Preserve existing fixture hash refusal',
            'refutationCase': 'A stale fixture must refuse without mutation',
            'comparison': comparison, 'regression': regression,
            'reason': 'Both probes refuse the same stale fixture and unchanged valid controls pass.'})
        return {'eventId': 'rsi', 'kind': 'rsi', 'candidateSha256': sha,
                'integrationRevision': revision, 'disposition': disposition, 'evidence': evidence}

    def test_rsi_required_before_new_candidate_or_selection(self):
        sha, revision = self.integrated_changed()
        action = json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)['nextRootAction']
        self.assertEqual(action['kind'], 'rsi')
        with self.assertRaises(AssertionError):
            self.candidate('c2')
        self.fixture.cli('--record', self.record_path, 'delivery-select', '--expect-state-sha',
                         fixtures.digest(self.repo / 'docs/warlock-build-loop/v2/STATE.json'), ok=False)
        self.append(self.rsi_event(sha, revision))
        self.assertEqual(json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)['nextRootAction']['kind'], 'exercise-journey')

    def test_rsi_wrong_candidate_and_untested_adoption_refuse(self):
        sha, revision = self.integrated_changed()
        event = self.rsi_event(sha, revision)
        event['candidateSha256'] = '0' * 64
        self.append(event, ok=False)
        self.append(self.rsi_event(sha, revision, 'adopted'), ok=False)

    def test_rsi_changed_immutable_guard_refuses(self):
        sha, revision = self.integrated_changed()
        event = self.rsi_event(sha, revision)
        self.fixture.write('window-integration-qa/qa_run.py', 'changed protected launcher')
        self.append(event, ok=False)

    def test_selection_cannot_hide_running_slot(self):
        self.start_delivery()
        sha = self.ready()
        self.append(self.started(sha))
        self.fixture.cli('--record', self.record_path, 'delivery-select', '--expect-state-sha',
                         fixtures.digest(self.repo / 'docs/warlock-build-loop/v2/STATE.json'), ok=False)

    def test_injected_clock_or_progress_fields_are_refused(self):
        self.start_delivery()
        for field, value in (('activeSeconds', 0), ('deliveryAdvance', 'fake'), ('clockSample', {})):
            with self.subTest(field=field):
                event = {'eventId': 'injected-' + field, 'kind': 'deferred',
                         'reason': 'specific dependency', 'owner': 'root', 'nextAction': 'repair dependency', field: value}
                self.append(event, ok=False)

    def test_native_prerequisite_is_scoped_to_native_candidate(self):
        self.start_delivery()
        with self.assertRaises(AssertionError):
            self.candidate(scope='native')
        self.ready()
        self.precheck()

    def test_production_source_drift_refuses(self):
        self.start_delivery()
        self.ready()
        self.fixture.write(self.source, 'changed after source review\n')
        self.precheck(ok=False)

    def test_bad_original_plan_does_not_create_record(self):
        self.plan['journey']['originalPairs'][0]['scenario'] = 'invented-scenario'
        self.fixture.write('.warlock-contributor/delivery-plan.json', self.plan)
        self.fixture.cli('--record', self.record_path, 'start', '--owner', 'root',
                         '--workflow-policy', '2', '--delivery-plan-file', '.warlock-contributor/delivery-plan.json', ok=False)
        self.assertFalse((self.repo / self.record_path).exists())

    def test_explicit_opt_in_and_same_record_events(self):
        self.start_delivery()
        before = self.record()
        ledger = (self.repo / 'docs/warlock-build-loop/v2/requirement-ledger.json').read_bytes()
        self.candidate()
        after = self.record()
        self.assertEqual(after['workflowPolicy'], 2)
        self.assertEqual(before['iterations'], after['iterations'])
        self.assertEqual(before['startedUTC'], after['startedUTC'])
        self.assertEqual(ledger, (self.repo / 'docs/warlock-build-loop/v2/requirement-ledger.json').read_bytes())
        self.assertEqual(len(after['delivery']['events']), 1)

    def test_ready_precheck_and_terminal_consumption(self):
        self.start_delivery()
        sha = self.ready()
        packet = json.loads(self.precheck().stdout)
        self.assertFalse(packet['executionAuthorized'])
        self.assertEqual(packet['nextRootAction']['kind'], 'execute')
        self.append(self.started(sha))
        self.precheck(ok=False)
        self.append(self.terminal(sha, consumed=False))
        handoff = json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)
        self.assertEqual(handoff['nextRootAction']['kind'], 'consume')
        self.precheck(ok=False)
        self.append({'eventId': 'consume-j1', 'kind': 'execution-consumed', 'jobId': 'j1', 'outerHandle': 'handle-j1'})
        handoff = json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)
        self.assertEqual(handoff['nextRootAction']['kind'], 'integrate')

    def test_stale_hash_duplicate_and_self_review_refuse_without_write(self):
        self.start_delivery()
        sha = self.candidate()
        before = (self.repo / self.record_path).read_bytes()
        self.append(self.review(sha, reviewer='root'), ok=False)
        self.assertEqual(before, (self.repo / self.record_path).read_bytes())
        self.append(self.review(sha), ok=False, expected='0' * 64)
        self.assertEqual(before, (self.repo / self.record_path).read_bytes())
        event = self.review(sha)
        self.append(event)
        before = (self.repo / self.record_path).read_bytes()
        self.append(event, ok=False)
        self.assertEqual(before, (self.repo / self.record_path).read_bytes())

    def test_fixture_drift_and_wrong_scope_block_execution(self):
        self.start_delivery()
        self.ready()
        self.precheck(ok=False, scope='native')
        self.fixture.write('.warlock-contributor/fixture.txt', 'changed expectations\n')
        self.precheck(ok=False)

    def test_second_job_and_wrong_job_terminal_refuse(self):
        self.start_delivery()
        sha = self.ready()
        self.append(self.started(sha))
        self.append(self.started(sha, 'j2'), ok=False)
        self.append(self.terminal(sha, job='old'), ok=False)

    def test_terminal_fixture_identity_must_match(self):
        self.start_delivery()
        sha = self.ready()
        self.append(self.started(sha))
        event = self.terminal(sha)
        path = self.repo / event['report']['path']
        data = json.loads(path.read_text())
        data['fixtureSha256'] = '0' * 64
        path.write_text(json.dumps(data))
        event['report']['sha256'] = fixtures.digest(path)
        self.append(event, ok=False)

    def test_legacy_record_cannot_receive_delivery_events(self):
        self.fixture.cli('--record', self.record_path, 'start', '--owner', 'root')
        before = (self.repo / self.record_path).read_bytes()
        self.append({'eventId': 'illegal', 'kind': 'deferred', 'reason': 'upgrade'}, ok=False)
        self.assertEqual(before, (self.repo / self.record_path).read_bytes())

    def test_new_same_pair_cannot_reset_delivery_history(self):
        self.start_delivery()
        self.fixture.cli('--record', '.warlock-contributor/other.json', 'start', '--owner', 'other',
                         '--workflow-policy', '2', '--delivery-plan-file', '.warlock-contributor/delivery-plan.json', ok=False)

    def test_expected_red_never_enables_integration(self):
        self.start_delivery()
        sha = self.ready()
        self.append(self.started(sha))
        self.append(self.terminal(sha, classification='expected-red', exit_code=1))
        packet = json.loads(self.fixture.cli('--record', self.record_path, 'handoff').stdout)
        self.assertEqual(packet['nextRootAction']['kind'], 'correct')


if __name__ == '__main__':
    unittest.main()
