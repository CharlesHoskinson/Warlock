"""Offline adapter controls; no agents, credentials, product tests or services."""
import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'harness2_adapter.py'
spec = importlib.util.spec_from_file_location('warlock_harness2_adapter', SCRIPT)
assert spec is not None and spec.loader is not None
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class AdapterControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        for name, text in [('task.txt', 'resolve task'), ('source.txt', 'frozen code'), ('plugin.txt', 'baseline workflow plugin'),
                           ('oracle.json', '{"checks":["delivered","oracles-retained"]}'),
                           ('guards.json', '{"native":false}'), ('authorization.json', '{"expires":"unchanged"}')]:
            (self.root / name).write_text(text)
        self.request: dict[str, Any] = {'schema': 1, 'taskId': 'offline-handoff-1',
                        'taskFiles': ['task.txt'], 'sourceFiles': ['source.txt'],
                        'oracleFiles': ['oracle.json'], 'guardFiles': ['guards.json'],
                        'authorizationFiles': ['authorization.json'], 'pluginBaselineFiles': ['plugin.txt'],
                        'checkNames': ['delivered', 'oracles-retained']}
        self.harness: dict[str, Any] = {'prompt': 'Finish the exact task.', 'toolGuidance': 'Use fixed read tools.',
                        'taskDecomposition': ['Read frozen inputs', 'Deliver evidence'],
                        'handoff': 'Name the next owner and observation.'}

    def freeze(self, harness=None):
        return adapter.freeze(self.root, self.request, harness or self.harness)

    def observation(self, snapshot, passed=(False, True), filename='baseline.log'):
        (self.root / filename).write_text('retained supplied observation')
        return {'schema': 1, 'taskId': snapshot['taskId'],
                'snapshotSha256': adapter.canonical_sha(snapshot),
                'checks': [{'name': name, 'passed': value} for name, value in zip(self.request['checkNames'], passed)],
                'reportFiles': [filename], 'regressionFiles': [filename]}

    def test_comparable_handoff_candidate(self):
        baseline = self.freeze()
        harness = dict(self.harness, handoff='Root owns execution; attach exact result.')
        candidate = self.freeze(harness)
        result = adapter.compare(baseline, candidate, self.observation(baseline),
                                 self.observation(candidate, (True, True), 'candidate.log'), 'c' * 64)
        self.assertEqual(result['passedCheckDelta'], 1)
        self.assertFalse(result['acceptanceAuthority'])
        self.assertFalse(result['autoAdopt'])
        self.assertEqual(result['changedHarnessFields'], ['handoff'])
        self.assertEqual(len(result['reportBindings']['baseline']), 1)
        self.assertEqual(result['rsi']['proposedDisposition'], 'deferred-blocker')
        self.assertEqual(len(result['baselinePluginSha256']), 64)
        self.assertFalse(result['rsi']['adoptionVerified'])

    def test_full_candidate_digest_is_explicit_not_source_map_digest(self):
        baseline, candidate = self.freeze(), self.freeze(dict(self.harness, handoff='New handoff'))
        result = adapter.compare(baseline, candidate, self.observation(baseline),
                                 self.observation(candidate, (True, True), 'candidate.log'), 'c' * 64)
        self.assertEqual(result['completedCandidateSha256'], 'c' * 64)
        self.assertNotEqual(result['completedCandidateSha256'], result['sourceSnapshotSha256'])
        self.assertEqual(result['baselinePluginSha256'], adapter.canonical_sha({'plugin.txt': adapter.canonical_file_hash(self.root / 'plugin.txt')}))
        self.assertEqual([row['name'] for row in result['checks']], self.request['checkNames'])
        for bad in ['', 'x' * 64, 'C' * 64]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                adapter.compare(baseline, candidate, {}, {}, bad)

    def test_snapshot_detached_from_input_mutations(self):
        snapshot = self.freeze()
        self.request['checkNames'].append('later')
        self.harness['taskDecomposition'].append('later')
        self.assertEqual(snapshot['checkNames'], ['delivered', 'oracles-retained'])
        self.assertEqual(snapshot['harness']['taskDecomposition'], ['Read frozen inputs', 'Deliver evidence'])

    def test_refuse_changed_fixed_roles(self):
        for role in ['taskFiles', 'sourceFiles', 'oracleFiles', 'guardFiles', 'authorizationFiles', 'pluginBaselineFiles']:
            with self.subTest(role=role):
                baseline = self.freeze()
                path = self.root / self.request[role][0]
                old = path.read_bytes()
                path.write_bytes(old + b' changed')
                candidate = self.freeze()
                with self.assertRaises(ValueError):
                    adapter.compare(baseline, candidate, {}, {}, 'c' * 64)
                path.write_bytes(old)

    def test_refuse_noneditable_harness_fields(self):
        for field in ['guardrails', 'authorization', 'oracle', 'scripts', 'plugins', 'acceptance']:
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.freeze(dict(self.harness, **{field: 'edited'}))

    def test_refuse_unknown_request_and_duplicate_roles(self):
        self.request['sourceFiles'] = ['task.txt']
        with self.assertRaises(ValueError):
            self.freeze()
        self.request['sourceFiles'] = ['source.txt']
        self.request['unexpected'] = True
        with self.assertRaises(ValueError):
            self.freeze()

    def test_refuse_escape_symlink_directory_and_missing(self):
        (self.root / 'link').symlink_to(self.root / 'task.txt')
        (self.root / 'linked-dir').symlink_to(self.root, target_is_directory=True)
        for path in ['../task.txt', '/etc/passwd', 'link', 'linked-dir/task.txt', 'missing', '.']:
            with self.subTest(path=path):
                request = dict(self.request, taskFiles=[path])
                with self.assertRaises(ValueError):
                    adapter.freeze(self.root, request, self.harness)

    def test_fifo_and_oversized_files_are_refused(self):
        fifo = self.root / 'fifo'
        os.mkfifo(fifo)
        with self.assertRaises(ValueError):
            adapter.read_json(fifo)
        large = self.root / 'large'
        large.write_bytes(b'x' * (adapter.MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            adapter.read_json(large)

    def test_refuse_nonprivate_context(self):
        self.root.chmod(0o755)
        with self.assertRaises(ValueError):
            self.freeze()

    def test_refuse_input_changed_after_freeze(self):
        baseline = self.freeze()
        candidate = self.freeze(dict(self.harness, prompt='A candidate'))
        (self.root / 'guards.json').write_text('changed later')
        with self.assertRaises(ValueError):
            adapter.compare(baseline, candidate, {}, {}, 'c' * 64)

    def test_refuse_changed_check_inventory(self):
        baseline = self.freeze()
        self.request['checkNames'].append('injected')
        candidate = self.freeze(dict(self.harness, prompt='A candidate'))
        with self.assertRaises(ValueError):
            adapter.compare(baseline, candidate, {}, {}, 'c' * 64)

    def test_refuse_omitted_duplicate_reordered_and_nonboolean_checks(self):
        baseline = self.freeze()
        candidate = self.freeze(dict(self.harness, prompt='A candidate'))
        good = self.observation(candidate, (True, True), 'candidate.log')
        bad_values = [good['checks'][:1], good['checks'] * 2, list(reversed(good['checks'])),
                      [{'name': 'delivered', 'passed': 1}, good['checks'][1]]]
        for checks in bad_values:
            with self.subTest(checks=checks), self.assertRaises(ValueError):
                adapter.compare(baseline, candidate, self.observation(baseline), dict(good, checks=checks), 'c' * 64)

    def test_refuse_wrong_snapshot_or_task_or_missing_reports(self):
        baseline, candidate = self.freeze(), self.freeze(dict(self.harness, prompt='A candidate'))
        good = self.observation(candidate, (True, True), 'candidate.log')
        for field, value in [('snapshotSha256', '0' * 64), ('taskId', 'foreign'),
                             ('reportFiles', []), ('reportFiles', ['missing']), ('regressionFiles', [])]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                adapter.compare(baseline, candidate, self.observation(baseline), dict(good, **{field: value}), 'c' * 64)

    def test_refuse_forged_snapshot(self):
        snap = self.freeze()
        forged = copy.deepcopy(snap)
        forged['fixedInputs']['guardFiles']['guards.json']['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            adapter.compare(forged, snap, {}, {}, 'c' * 64)

    def test_refuse_duplicate_json_keys(self):
        (self.root / 'ambiguous.json').write_text('{"schema":1,"schema":2}')
        with self.assertRaises(ValueError):
            adapter.read_json(self.root / 'ambiguous.json')

    def test_refuse_upstream_probe_in_core_interpreter(self):
        with self.assertRaises(ValueError):
            adapter.check_probe_interpreter((3, 9))
        with self.assertRaises(ValueError):
            adapter.check_probe_interpreter((3, 14))
        adapter.check_probe_interpreter((3, 12))

    def test_pin_check_detects_assumed_unchanged_source_edit(self):
        (self.root / 'harness2').mkdir()
        (self.root / 'harness2/demo.py').write_text('changed body')
        with patch.object(adapter, '_git', side_effect=[adapter.UPSTREAM_COMMIT, '', 'harness2/demo.py']), \
             patch.object(adapter, '_git_bytes', return_value=b'pinned body'), self.assertRaises(ValueError):
            adapter.verify_upstream(self.root)

    def test_no_change_rsi_disposition_is_valid_without_forced_edit(self):
        baseline, candidate = self.freeze(), self.freeze(dict(self.harness, prompt='Candidate'))
        result = adapter.compare(baseline, candidate, self.observation(baseline, (True, True)),
                                 self.observation(candidate, (True, True), 'candidate.log'), 'c' * 64)
        self.assertEqual(result['rsi']['proposedDisposition'], 'no-change')
        self.assertFalse(result['rsi']['recursiveRsi'])
        self.assertFalse(result['autoAdopt'])

    def test_demo_report_ignores_progress_stdout_and_rejects_failure(self):
        path = self.root / 'demo.json'
        value = {'done': 2, 'failed': 0, 'execution_count': 14, 'editor_calls': 16}
        path.write_text(json.dumps(value))
        self.assertEqual(adapter.demo_report(self.root)['executionCount'], 14)
        value['failed'] = 1
        path.write_text(json.dumps(value))
        with self.assertRaises(ValueError):
            adapter.demo_report(self.root)

    def test_probe_is_fixed_api_not_executor(self):
        self.assertIn('run_domain(', adapter.PROBE_CODE)
        self.assertIn('DemoProposer', adapter.PROBE_CODE)
        self.assertNotIn('CodexSubstrate(', adapter.PROBE_CODE)
        self.assertNotIn('run_sweep', adapter.PROBE_CODE)
        self.assertNotIn('dangerously', adapter.PROBE_CODE)


if __name__ == '__main__':
    unittest.main()
