"""Dependency extension preserves custody, history and progress in isolated repos."""
import json
from concurrent.futures import ThreadPoolExecutor
import unittest

import test_warlock as fixtures


class ExtensionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        self.cli = self.fixture.cli
        self.record = self.repo / '.warlock-contributor/slice.json'

    def extend(self, path='src/Dependency.elm', *extra, ok=True):
        return self.cli('extend', '--path', path, '--reason', 'Same behavior needs the event reducer', *extra, ok=ok)

    def test_clean_dependency_preserves_history_and_does_not_count_as_source_fix(self):
        dependency = self.fixture.write('implementation/warlock/src/Dependency.elm', 'existing reducer')
        self.fixture.run_git('add', str(dependency.relative_to(self.repo)))
        self.fixture.run_git('commit', '-qm', 'existing dependency')
        self.fixture.start()
        for _ in range(2):
            self.cli('record', '--outcome', 'qualification', '--summary', 'observation unavailable')
        before = json.loads(self.record.read_text())
        state = (self.repo / 'docs/warlock-build-loop/v2/STATE.json').read_bytes()
        index = self.fixture.run_git('write-tree')
        self.extend()
        after = json.loads(self.record.read_text())
        for key in ('startedUTC', 'sourceRevision', 'sourceHashes', 'owner', 'iterations', 'foreignDirty'):
            self.assertEqual(before[key], after[key])
        self.assertEqual(state, (self.repo / 'docs/warlock-build-loop/v2/STATE.json').read_bytes())
        self.assertEqual(index, self.fixture.run_git('write-tree'))
        packet = json.loads(self.cli('handoff').stdout)
        self.assertEqual(packet['changedSinceLastRecord'], [])
        self.assertTrue(packet['progress']['investigationNeedsChange'])
        self.assertEqual(packet['progress']['iterationsWithoutProgress'], 2)
        self.cli('record', '--outcome', 'production-fix', '--summary', 'dependency declaration only')
        self.assertFalse(json.loads(self.record.read_text())['iterations'][-1]['meaningfulProgress'])
        dependency.write_text('actual new reducer behavior')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'implemented reducer')
        self.assertTrue(json.loads(self.record.read_text())['iterations'][-1]['meaningfulProgress'])
        self.cli('check')

    def test_retains_old_claim_hashes_but_requires_fresh_claim_for_expanded_tuple(self):
        self.fixture.start()
        self.fixture.record_claim(self.fixture.claim())
        before = json.loads(self.record.read_text())['iterations'][0]['claims'][0]
        self.extend()
        after = json.loads(self.record.read_text())['iterations'][0]['claims'][0]
        self.assertTrue(after.pop('historicalAfterSliceExtension'))
        self.assertEqual(before, after)
        packet = json.loads(self.cli('handoff').stdout)
        self.assertFalse(packet['observations'][0]['evidenceMatchesCurrentSources'])
        self.assertTrue(any('added dependencies' in w for w in packet['warnings']))
        self.fixture.write('implementation/warlock/src/Dependency.elm', 'new dependency')
        self.fixture.record_claim(self.fixture.claim(), ok=False)  # Incomplete current source tuple.
        claim = self.fixture.claim()
        claim['sourceHashes']['implementation/warlock/src/Dependency.elm'] = fixtures.digest(self.repo / 'implementation/warlock/src/Dependency.elm')
        self.fixture.record_claim(claim)
        self.cli('check')
        self.assertTrue(json.loads(self.cli('handoff').stdout)['observations'][0]['evidenceMatchesCurrentSources'])

    def test_missing_dependency_creation_is_real_source_progress(self):
        self.fixture.start()
        self.extend()
        self.cli('record', '--outcome', 'production-fix', '--summary', 'declaration only')
        self.assertFalse(json.loads(self.record.read_text())['iterations'][-1]['meaningfulProgress'])
        self.fixture.write('implementation/warlock/src/Dependency.elm', 'new source')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'source created')
        self.assertTrue(json.loads(self.record.read_text())['iterations'][-1]['meaningfulProgress'])
        self.cli('check')

    def test_dirty_dependency_requires_explicit_adoption_and_preserves_other_foreign_files(self):
        self.fixture.write('implementation/warlock/src/Dependency.elm', 'own resumed source')
        self.fixture.write('foreign.txt', 'another worker')
        self.fixture.start()
        before = self.record.read_bytes()
        self.extend(ok=False)
        self.assertEqual(before, self.record.read_bytes())
        self.extend('src/Dependency.elm', '--adopt-dirty', 'implementation/warlock/src/Dependency.elm', '--ownership-note', 'Authored by this participant before declaration')
        record = json.loads(self.record.read_text())
        self.assertNotIn('implementation/warlock/src/Dependency.elm', record['foreignDirty'])
        self.assertIn('foreign.txt', record['foreignDirty'])
        self.cli('check')
        self.fixture.write('foreign.txt', 'overwritten')
        self.cli('check', ok=False)

    def test_changed_foreign_draft_cannot_be_adopted_to_hide_overwrite(self):
        self.fixture.write('implementation/warlock/src/Dependency.elm', 'foreign source')
        self.fixture.start()
        self.fixture.write('implementation/warlock/src/Dependency.elm', 'overwritten source')
        before = self.record.read_bytes()
        self.extend('src/Dependency.elm', '--adopt-dirty', 'implementation/warlock/src/Dependency.elm', '--ownership-note', 'claimed ownership', ok=False)
        self.assertEqual(before, self.record.read_bytes())

    def test_new_untracked_dependency_after_start_also_needs_adoption(self):
        self.fixture.start()
        self.fixture.write('implementation/warlock/src/Dependency.elm', 'own new source')
        self.extend(ok=False)
        self.extend('src/Dependency.elm', '--adopt-dirty', 'implementation/warlock/src/Dependency.elm', '--ownership-note', 'This participant created it')
        self.cli('check')

    def test_rejects_missing_record_duplicate_archive_symlink_and_empty_reason(self):
        self.extend(ok=False)
        self.fixture.start()
        before = self.record.read_bytes()
        for path in ('src/Desktop.elm', 'src/./Desktop.elm', 'src//Desktop.elm', '../warlock-preview-provider-v143/frozen.txt', '/tmp/escape'):
            self.extend(path, ok=False)
        linked = self.repo / 'implementation/warlock/src/linked'
        linked.symlink_to('/tmp')
        self.extend('src/linked/file', ok=False)
        linked.unlink()
        self.extend('src/Dependency.elm', '--reason', ' ', ok=False)
        self.extend('src/Dependency.elm', '--adopt-dirty', 'implementation/warlock/src/Desktop.elm', '--ownership-note', 'wrong path', ok=False)
        self.assertEqual(before, self.record.read_bytes())

    def test_concurrent_extensions_retain_both_dependencies_and_history(self):
        self.fixture.start()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.extend, ['src/One.elm', 'src/Two.elm']))
        self.assertEqual([r.returncode for r in results], [0, 0])
        record = json.loads(self.record.read_text())
        self.assertEqual(len(record['pathExtensions']), 2)
        self.assertEqual(len(record['slice']['paths']), 3)
        self.assertEqual(record['iterations'], [])
        self.cli('check')

    def test_tampered_extension_position_or_current_claim_marker_rejected(self):
        self.fixture.start()
        self.extend()
        record = json.loads(self.record.read_text())
        record['pathExtensions'][0]['afterIteration'] = True
        self.fixture.write('.warlock-contributor/slice.json', record)
        self.cli('check', ok=False)
        record['pathExtensions'][0]['afterIteration'] = 0
        self.fixture.write('.warlock-contributor/slice.json', record)
        self.fixture.write('implementation/warlock/src/Dependency.elm', 'real source')
        claim = self.fixture.claim()
        claim['historicalAfterSliceExtension'] = True
        self.fixture.record_claim(claim, ok=False)


if __name__ == '__main__':
    unittest.main()
