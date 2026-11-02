"""Narrow declaration correction regressions; Root alone executes these."""
import copy
import hashlib
import importlib.util
import json
from types import SimpleNamespace
import unittest

import test_warlock as fixtures

spec = importlib.util.spec_from_file_location('ghost_policy', fixtures.CHECKER)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class DeclarationGhostCorrectionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        for name in policy.SUPPORT_GHOSTS.values():
            self.fixture.write(name, '# isolated tracked support tool\n')
        self.fixture.run_git('add', 'tools')
        self.fixture.run_git('commit', '-qm', 'tracked support counterparts')
        self.foreign = 'implementation/warlock/src/Other.elm'
        self.fixture.write(self.foreign, 'unrelated worker source\n')
        self.fixture.start()
        self.ghosts = sorted(policy.SUPPORT_GHOSTS)
        self.fixture.cli('extend', *sum((['--path', n] for n in self.ghosts), []),
                         '--reason', 'Fixture reproduces the historical fully normalized mistake')
        self.fixture.cli('record', '--outcome', 'qualification', '--summary', 'No source progress; ghosts never created')
        self.path = '.warlock-contributor/slice.json'
        self.original = (self.repo / self.path).read_bytes()
        self.record = json.loads(self.original)
        self.record['_recordPath'] = self.path
        self.snapshot = policy.CORRECTION_EVIDENCE + 'before-record.json'
        self.reqs, self.state = policy.context(self.repo)

    def archive(self, record=None):
        record = self.record if record is None else record
        self.fixture.write(self.path, {k: v for k, v in record.items() if k != '_recordPath'})
        target = self.repo / self.snapshot
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((self.repo / self.path).read_bytes())
        return SimpleNamespace(correct_support_ghost=list(self.ghosts), adopt_dirty=[],
            reason='Correct observed root-tool prefixing error without dropping source',
            ownership_note='Root separately owns actual tracked support tools; this correction grants no ownership',
            record_snapshot=self.snapshot)

    def assert_refused_without_write(self, record, args):
        before = (self.repo / self.path).read_bytes()
        with self.assertRaises(ValueError):
            policy.correct_support_ghosts(self.repo, record, self.reqs, self.state, args)
        self.assertEqual((self.repo / self.path).read_bytes(), before)

    def test_actual_cli_preserves_history_foreign_and_all_non_ghost_sources(self):
        args = self.archive()
        custody = policy.reconciliation_path(self.repo, self.record)
        self.fixture.write(str(custody.relative_to(self.repo)), policy.empty_reconciliation(self.record))
        custody_before = custody.read_bytes()
        result = json.loads(self.fixture.cli('extend', *sum((['--correct-support-ghost', n] for n in self.ghosts), []),
            '--reason', args.reason, '--ownership-note', args.ownership_note,
            '--record-snapshot', self.snapshot).stdout)
        self.assertFalse(result['rootSupportOwnershipGranted'])
        self.assertEqual(custody.read_bytes(), custody_before)
        after = json.loads((self.repo / self.path).read_bytes())
        for key in ('owner', 'startedUTC', 'sourceRevision', 'sourceHashes', 'baseline',
                    'iterations', 'pathExtensions', 'foreignDirty', 'adoptedDirty'):
            self.assertEqual(after[key], self.record[key])
        self.assertEqual(after['slice']['paths'], [n for n in self.record['slice']['paths'] if n not in self.ghosts])
        self.assertEqual(json.loads((self.repo / self.snapshot).read_text()),
                         {k: v for k, v in self.record.items() if k != '_recordPath'})
        self.assertEqual(after['declarationCorrections'][0]['recordSnapshotSha256'],
                         hashlib.sha256((self.repo / self.snapshot).read_bytes()).hexdigest())
        self.fixture.cli('check')
        fresh = self.fixture.claim()
        self.assertFalse(set(self.ghosts).intersection(fresh['sourceHashes']))

    def test_existing_leaf_and_symlink_are_never_correctable(self):
        for symbolic in (False, True):
            record = copy.deepcopy(self.record)
            args = self.archive(record)
            leaf = self.repo / self.ghosts[0]
            leaf.parent.mkdir(parents=True, exist_ok=True)
            if symbolic:
                leaf.symlink_to('/missing-ghost-target')
            else:
                leaf.write_text('real bytes must be retained')
            try:
                self.assert_refused_without_write(record, args)
            finally:
                leaf.unlink()

    def test_initial_hashed_claimed_foreign_or_adopted_ghosts_are_refused(self):
        for variant in ('initial', 'extensionHash', 'iterationHash', 'claim', 'foreign', 'adopted'):
            record = copy.deepcopy(self.record)
            ghost = self.ghosts[0]
            if variant == 'initial': record['sourceHashes'][ghost] = None
            if variant == 'extensionHash': record['pathExtensions'][-1]['sourceHashes'][ghost] = 'a' * 64
            if variant == 'iterationHash': record['iterations'][-1]['sourceHashes'][ghost] = 'a' * 64
            if variant == 'claim': record['iterations'][-1]['claims'].append({'sourceHashes': {ghost: None}})
            if variant == 'foreign': record['foreignDirty'][ghost] = None
            if variant == 'adopted': record['adoptedDirty']['paths'].append(ghost)
            args = self.archive(record)
            with self.subTest(variant=variant): self.assert_refused_without_write(record, args)

    def test_real_production_and_arbitrary_paths_cannot_be_dropped(self):
        for name in ('implementation/warlock/src/Desktop.elm', 'implementation/warlock/qa/New.elm',
                     'implementation/warlock/tools/arbitrary.py', 'tools/qa_cpu.py'):
            record = copy.deepcopy(self.record)
            args = self.archive(record)
            args.correct_support_ghost = [name]
            with self.subTest(path=name): self.assert_refused_without_write(record, args)

    def test_tracked_or_historically_tracked_ghost_is_not_missing_source(self):
        record = copy.deepcopy(self.record)
        ghost = self.ghosts[0]
        self.fixture.write(ghost, 'historically real source')
        self.fixture.run_git('add', ghost)
        self.fixture.run_git('commit', '-qm', 'once real ghost source')
        (self.repo / ghost).unlink()
        args = self.archive(record)
        self.assert_refused_without_write(record, args)
        self.fixture.run_git('add', '-u', '--', ghost)
        self.fixture.run_git('commit', '-qm', 'remove source, retain history')
        self.assert_refused_without_write(record, args)

    def test_untracked_root_counterpart_refused(self):
        self.fixture.run_git('rm', '--cached', '--', policy.SUPPORT_GHOSTS[self.ghosts[0]])
        self.assert_refused_without_write(self.record, self.archive())

    def test_unrelated_foreign_drift_still_refuses(self):
        args = self.archive()
        self.fixture.write(self.foreign, 'changed unrelated worker source')
        self.assert_refused_without_write(self.record, args)

    def test_correction_does_not_change_no_progress_clock(self):
        record = copy.deepcopy(self.record)
        record['startedUTC'] = '2000-01-01T00:00:00+00:00'
        args = self.archive(record)
        before = policy.progress_status(record)
        packet = policy.correct_support_ghosts(self.repo, record, self.reqs, self.state, args)
        after = packet['progress']
        for key in ('lastRecordedProgressUTC', 'iterationsWithoutProgress', 'investigationNeedsChange', 'reasons'):
            self.assertEqual(after[key], before[key])
        self.assertTrue(after['investigationNeedsChange'])
        self.assertEqual(record['iterations'], json.loads((self.repo / self.snapshot).read_text())['iterations'])

    def test_snapshot_drift_and_later_history_rewrite_are_detected(self):
        args = self.archive()
        policy.correct_support_ghosts(self.repo, self.record, self.reqs, self.state, args)
        self.assertEqual(policy.declaration_corrections(self.repo, self.record), set(self.ghosts))
        altered = copy.deepcopy(self.record)
        altered['iterations'][0]['summary'] = 'rewritten history'
        with self.assertRaises(ValueError): policy.declaration_corrections(self.repo, altered)
        snapshot = self.repo / self.snapshot
        snapshot.write_bytes(snapshot.read_bytes() + b'\n')
        with self.assertRaises(ValueError): policy.declaration_corrections(self.repo, self.record)

    def test_history_json_type_substitutions_are_not_exact_history(self):
        previous = copy.deepcopy(self.record['iterations'])
        for field, replacement in (('meaningfulProgress', 0), ('progressPolicy', 6.0)):
            current = copy.deepcopy(previous)
            current[-1][field] = replacement
            with self.subTest(field=field):
                self.assertFalse(policy.correction_history_extends(previous, current))
        previous[-1]['claims'] = [self.fixture.claim()]
        previous[-1]['claims'][0]['historicalAfterSourceChange'] = True
        current = copy.deepcopy(previous)
        current[-1]['claims'][0]['historicalAfterSourceChange'] = 1
        self.assertFalse(policy.correction_history_extends(previous, current))

    def test_history_only_allows_true_metadata_additions_without_mutation(self):
        previous = copy.deepcopy(self.record['iterations'])
        previous[-1]['claims'] = [self.fixture.claim()]
        untouched = copy.deepcopy(previous)
        current = copy.deepcopy(previous)
        for flag in ('historicalAfterSourceChange', 'historicalAfterSliceExtension'):
            current[-1]['claims'][0][flag] = True
        self.assertTrue(policy.correction_history_extends(previous, current))
        self.assertEqual(previous, untouched)
        for bad in (False, 1, 0, 'true'):
            altered = copy.deepcopy(current)
            altered[-1]['claims'][0]['historicalAfterSourceChange'] = bad
            with self.subTest(value=bad):
                self.assertFalse(policy.correction_history_extends(previous, altered))
        shortened = copy.deepcopy(previous)
        shortened[-1]['claims'] = []
        self.assertFalse(policy.correction_history_extends(previous, shortened))
        expanded = copy.deepcopy(previous)
        expanded[-1]['claims'].append(copy.deepcopy(previous[-1]['claims'][0]))
        self.assertFalse(policy.correction_history_extends(previous, expanded))

    def test_new_raw_root_tool_inputs_fail_with_explicit_support_guidance(self):
        before = (self.repo / self.path).read_bytes()
        result = self.fixture.cli('extend', '--path', 'tools/qa_cpu.py',
                                  '--reason', 'Must not silently create another ghost', ok=False)
        self.assertIn('Root tools are support files', result.stdout)
        self.assertIn('review --include', result.stdout)
        self.assertEqual((self.repo / self.path).read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
