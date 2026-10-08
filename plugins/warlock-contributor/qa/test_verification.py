"""Verification planning is read-only and cannot turn suggestions into results."""
import datetime as dt
import importlib.util
import json
import shlex
import unittest

import test_warlock as fixtures


class VerificationPlannerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli
        for name in ('check-feedback.py', 'check-search.py', 'check-focus-core.py',
                     'check-native-authority.py', 'native-window-feedback.py'):
            self.fixture.write('implementation/warlock/qa/' + name,
                               "raise RuntimeError('planner must never execute this runner')\n")
        self.fixture.run_git('add', '.')
        self.fixture.run_git('commit', '-qm', 'runner fixtures')

    def packet(self, *args, ok=True):
        return json.loads(self.cli('verify-plan', *args, ok=ok).stdout)

    def select(self, requirement, scenario, paths):
        state_path = self.repo / 'docs/warlock-build-loop/v2/STATE.json'
        state = json.loads(state_path.read_text())
        state['activeSlice'].update(requirements=[requirement], scenarios=[scenario], paths=paths)
        self.fixture.write(str(state_path.relative_to(self.repo)), state)
        for name in paths:
            path = name if name.startswith('implementation/') else 'implementation/warlock/' + name
            if not (self.repo / path).exists():
                self.fixture.write(path, 'initial source\n')
        self.fixture.run_git('add', '.')
        self.fixture.run_git('commit', '-qm', 'selected original fixture')

    def test_missing_record_fails_and_unchanged_record_does_not_suggest_reruns(self):
        self.packet(ok=False)
        self.fixture.start()
        packet = self.packet()
        self.assertEqual(packet['cpuTargets'], [])
        self.assertEqual(packet['nativeCandidates'], [])
        self.assertEqual(packet['consideredPaths'], [])

    def test_planning_selected_paths_is_read_only_and_preserves_original_obligations(self):
        self.fixture.start()
        paths = ['.warlock-contributor/slice.json', '.git/index',
                 'docs/warlock-build-loop/v2/STATE.json',
                 'docs/warlock-build-loop/v2/requirement-ledger.json']
        before = [(self.repo / name).read_bytes() for name in paths]
        packet = self.packet('--selected')
        target = packet['cpuTargets'][0]
        self.assertEqual(target['runner'], 'implementation/warlock/qa/check-feedback.py')
        self.assertIn('/home/hoskinson/window-integration-qa/qa_run.py', target['argv'])
        self.assertEqual(shlex.split(target['command'])[1:], target['argv'])
        self.assertIsNone(packet['observations'][0]['recordedDisposition'])
        original = next(r for r in self.fixture.original['requirements'] if r['id'] == 'ELM-UI-007')
        self.assertEqual(packet['observations'][0]['verificationScope'], original['verification'])
        self.assertEqual(before, [(self.repo / name).read_bytes() for name in paths])

    def test_only_changed_paths_trigger_suggestions_and_recording_ends_default_rerun(self):
        self.fixture.start()
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'changed behavior\n')
        self.assertEqual(len(self.packet()['cpuTargets']), 1)
        self.cli('record', '--outcome', 'production-fix', '--summary', 'Changed source; actual QA pending')
        self.assertEqual(self.packet()['cpuTargets'], [])
        self.assertFalse(self.packet()['observations'][0]['evidenceMatchesCurrentSources'])

    def test_missing_runner_does_not_offer_unprotected_fallback(self):
        (self.repo / 'implementation/warlock/qa/check-feedback.py').unlink()
        self.fixture.start()
        target = self.packet('--selected')['cpuTargets'][0]
        self.assertFalse(target['runnerAvailable'])
        self.assertIsNone(target['command'])
        self.assertIsNone(target['runnerSha256'])

    def test_unknown_product_and_support_changes_stay_explicit(self):
        self.select('ELM-UI-007', 'restore-pending', ['src/NewFeature.elm', 'qa/helper.py'])
        self.fixture.start()
        for name in ('src/NewFeature.elm', 'qa/helper.py'):
            self.fixture.write('implementation/warlock/' + name, 'changed\n')
        packet = self.packet()
        self.assertEqual(packet['unmappedProductPaths'], ['implementation/warlock/src/NewFeature.elm'])
        self.assertEqual(packet['supportPaths'], ['implementation/warlock/qa/helper.py'])
        self.assertEqual(packet['cpuTargets'], [])

    def test_stale_evidence_fails_planner_and_stays_explicit(self):
        self.fixture.start()
        self.fixture.record_claim(self.fixture.claim())
        self.fixture.write('implementation/warlock/src/Desktop.elm', 'changed after evidence\n')
        packet = self.packet(ok=False)
        self.assertTrue(packet['errors'])
        self.assertFalse(packet['observations'][0]['evidenceMatchesCurrentSources'])

    def test_taskview_plans_actual_positive_and_retired_opener_flags_serially(self):
        self.select('ELM-UI-006', 'overview-cancel', ['src/TaskView.elm'])
        self.fixture.start()
        packet = self.packet('--selected')
        self.assertEqual(packet['cpuTargets'][0]['arguments'], ['--task-view'])
        self.assertEqual([x['arguments'] for x in packet['nativeCandidates']],
                         [['--task-view'], ['--task-view-retired-opener']])
        for item in packet['nativeCandidates']:
            self.assertIn('docs/warlock-build-loop/v2/loop.py', item['argv'])
            self.assertIn('--runner', item['argv'])
            self.assertEqual(shlex.split(item['command']), item['argv'])

    def test_core_change_orders_owning_unit_then_authority_and_never_full_rebuild(self):
        self.select('ELM-UI-006', 'overview-cancel', ['native/core/SeatManager.cpp'])
        self.fixture.start()
        self.fixture.write('implementation/warlock/native/core/SeatManager.cpp', 'changed core\n')
        runners = [x['runner'].split('/')[-1] for x in self.packet()['cpuTargets']]
        self.assertEqual(runners, ['check-focus-core.py', 'check-native-authority.py'])

    def test_surface_header_change_compiles_owning_host_instead_of_authority(self):
        self.select('ELM-UI-007', 'restore-pending', ['native/surface.h'])
        self.fixture.start()
        self.fixture.write('implementation/warlock/native/surface.h', 'changed surface protocol\n')
        packet = self.packet()
        self.assertEqual([p['runner'].split('/')[-1] for p in packet['cpuTargets']], ['check-search.py'])
        self.assertEqual(packet['cpuTargets'][0]['arguments'], ['--native-popup'])
        self.assertEqual(packet['unmappedProductPaths'], [])

    def test_primary_surface_change_uses_primary_campaign_instead_of_group_picker(self):
        self.select('ELM-UI-004', 'taskbar-inactive', ['src/Surface.elm'])
        self.fixture.start()
        self.fixture.write('implementation/warlock/src/Surface.elm', 'changed state cues\n')
        packet = self.packet()
        self.assertEqual(packet['unmappedProductPaths'], [])
        self.assertEqual(packet['cpuTargets'][0]['arguments'], ['--taskbar-primary'])
        self.assertEqual([p['arguments'] for p in packet['nativeCandidates']], [['--taskbar-primary']])

    def test_custom_record_is_preserved_as_one_quoted_argument(self):
        name = '.warlock-contributor/alternate record;touch sentinel.json'
        self.cli('--record', name, 'start', '--owner', 'contributor')
        packet = json.loads(self.cli('--record', name, 'verify-plan', '--selected').stdout)
        argv = shlex.split(packet['nativeCandidates'][0]['command'])
        self.assertEqual(argv[argv.index('--record') + 1], name)
        self.assertFalse((self.repo / 'sentinel.json').exists())

    def test_dense_keyboard_adapter_maps_existing_protected_browser_and_native_modes(self):
        self.select('ELM-UI-008', 'overflow-first-last', ['assets/bar-adapter.js', 'assets/shell.css'])
        self.fixture.start()
        self.fixture.write('implementation/warlock/assets/bar-adapter.js', 'changed keyboard behavior\n')
        packet = self.packet()
        self.assertEqual(packet['supportPaths'], [])
        self.assertEqual(packet['unmappedProductPaths'], [])
        self.assertEqual(packet['cpuTargets'][0]['arguments'], ['--dense-taskbar'])
        self.assertEqual([x['arguments'] for x in packet['nativeCandidates']], [['--dense-taskbar']])
        self.assertFalse(packet['executionPerformed'])
        self.assertFalse(packet['acceptanceInferred'])

    def test_menu_keyboard_adapter_maps_current_menu_campaign(self):
        self.select('ELM-UI-008', 'menu-invocation', ['assets/context.js'])
        self.fixture.start()
        packet = self.packet('--selected')
        self.assertEqual(packet['cpuTargets'][0]['arguments'], ['--pinned-menus'])
        self.assertEqual([x['arguments'] for x in packet['nativeCandidates']], [['--pinned-menus']])

    def test_reflow_maps_controller_renderer_adapter_and_host_to_actual_reflow_mode(self):
        paths = ['src/SurfaceController.elm', 'src/Popup.elm', 'assets/popup-adapter.js',
                 'native/host.c', 'qa/PopupReflowReplay.elm']
        self.select('ELM-UI-008', 'overflow-resize', paths)
        self.fixture.start()
        packet = self.packet('--selected')
        self.assertEqual(packet['unmappedProductPaths'], [])
        self.assertEqual(packet['supportPaths'], ['implementation/warlock/qa/PopupReflowReplay.elm'])
        self.assertEqual(len(packet['cpuTargets']), 1)
        self.assertEqual(packet['cpuTargets'][0]['arguments'], ['--popup-reflow'])
        self.assertEqual(packet['cpuTargets'][0]['triggerPaths'], sorted(
            'implementation/warlock/' + name for name in paths[:-1]))
        self.assertEqual([x['arguments'] for x in packet['nativeCandidates']], [['--popup-reflow']])
        self.assertFalse(packet['executionPerformed'])
        self.assertFalse(packet['acceptanceInferred'])

    def test_reflow_host_header_selects_reflow_without_rebuilding_authority(self):
        self.select('ELM-UI-008', 'overflow-resize', ['native/surface.h'])
        self.fixture.start()
        packet = self.packet('--selected')
        self.assertEqual([x['runner'].split('/')[-1] for x in packet['cpuTargets']], ['check-search.py'])
        self.assertEqual(packet['cpuTargets'][0]['arguments'], ['--popup-reflow'])

    def test_popup_renderer_outside_reflow_uses_existing_selected_menu_mode(self):
        self.select('ELM-UI-008', 'menu-invocation', ['src/Popup.elm'])
        self.fixture.start()
        packet = self.packet('--selected')
        self.assertEqual(packet['unmappedProductPaths'], [])
        self.assertEqual(packet['cpuTargets'][0]['arguments'], ['--pinned-menus'])

    def test_transport_is_unmapped_product_and_generated_js_stays_support(self):
        self.select('ELM-UI-007', 'restore-pending', ['assets/native-preview-proposals.js', 'assets/elm.js'])
        self.fixture.start()
        packet = self.packet('--selected')
        self.assertEqual(packet['unmappedProductPaths'], ['implementation/warlock/assets/native-preview-proposals.js'])
        self.assertEqual(packet['supportPaths'], ['implementation/warlock/assets/elm.js'])
        self.assertEqual(packet['cpuTargets'], [])


class ProgressStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('contributor_progress', fixtures.CHECKER)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def record(self):
        return {'startedUTC': '2026-10-07T00:00:00+00:00', 'iterations': []}

    def test_time_threshold_is_exact_and_has_no_global_block(self):
        record = self.record()
        start = dt.datetime.fromisoformat(record['startedUTC'])
        before = self.module.progress_status(record, start + dt.timedelta(seconds=2699))
        after = self.module.progress_status(record, start + dt.timedelta(seconds=2700))
        self.assertFalse(before['investigationNeedsChange'])
        self.assertEqual(after['reasons'], ['45-minutes-without-recorded-progress'])
        self.assertIn('do not block independent work', after['action'])

    def test_two_nonprogress_iterations_trigger_and_recorded_progress_resets(self):
        record = self.record()
        stamp = '2026-10-07T00:01:00+00:00'
        record['iterations'] = [{'atUTC': stamp, 'meaningfulProgress': False}] * 2
        clock = dt.datetime.fromisoformat(stamp)
        self.assertEqual(self.module.progress_status(record, clock)['reasons'], ['two-iterations-without-progress'])
        record['iterations'].append({'atUTC': stamp, 'meaningfulProgress': True})
        packet = self.module.progress_status(record, clock)
        self.assertFalse(packet['investigationNeedsChange'])
        self.assertEqual(packet['iterationsWithoutProgress'], 0)
        self.assertEqual(packet['secondsSinceRecordedProgress'], 0)

    def test_loop_check_exposes_metrics_without_turning_advisory_into_rejection(self):
        fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.start()
        fixture.cli('record', '--outcome', 'qualification', '--summary', 'Observation missing')
        fixture.cli('record', '--outcome', 'qualification', '--summary', 'Still missing')
        packet = json.loads(fixture.cli('check', '--require-record').stdout)
        self.assertTrue(packet['ok'])
        self.assertTrue(packet['progress']['investigationNeedsChange'])
        self.assertEqual(packet['progress']['iterationsWithoutProgress'], 2)
        self.assertTrue(packet['warnings'])


if __name__ == '__main__':
    unittest.main()
