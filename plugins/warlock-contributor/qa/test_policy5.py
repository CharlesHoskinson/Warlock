"""Proposed real contributor-engine regressions; root execution required.

Place beside existing qa/test_warlock.py only after root applies/reviews the
candidate checker. Uses its isolated-repository CLI, not a mock classifier.
"""
import json
import unittest
import test_warlock as base

class HaskellPolicy5Tests(unittest.TestCase):
    def setUp(self):
        self.fx = base.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.repo, self.cli = self.fx.repo, self.fx.cli

    def record(self):
        return json.loads((self.repo / '.warlock-contributor/slice.json').read_text())

    def select(self, paths):
        self.fx.slice['paths'] = paths
        self.fx.write('docs/warlock-build-loop/v2/STATE.json', {
            'schema': 1, 'sourceCandidate': 'implementation/warlock',
            'heldParent': 'implementation/warlock-preview-provider-v143',
            'activeSlice': self.fx.slice, 'releaseAccepted': False})
        self.fx.run_git('add', '.')
        if self.fx.run_git('diff', '--cached', '--name-only'):
            self.fx.run_git('commit', '-qm', 'fixture selected clean baseline')
        self.fx.start()

    def test_owned_haskell_and_elm_actual_record(self):
        self.fx.write('implementation/warlock/src/Contract.hs', 'module Contract where\nx = 1\n')
        self.select(['src/Contract.hs', 'src/Desktop.elm'])
        self.fx.write('implementation/warlock/src/Contract.hs', 'module Contract where\nx = 2\n')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'owned Haskell change')
        self.assertEqual(self.record()['iterations'][-1]['progressPolicy'], 5)
        self.assertTrue(self.record()['iterations'][-1]['meaningfulProgress'])
        self.fx.write('implementation/warlock/src/Desktop.elm', 'module Desktop exposing (identity)\nidentity = "new"\n')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'owned Elm change')
        self.assertTrue(self.record()['iterations'][-1]['meaningfulProgress'])
        self.cli('check')

    def test_foreign_untracked_does_not_reset_record(self):
        self.select(['src/Desktop.elm'])
        self.fx.write('implementation/warlock/src/Foreign.hs', 'module Foreign where\n')
        result = json.loads(self.cli('record', '--outcome', 'production-fix', '--summary', 'foreign unowned', ok=False).stdout)
        self.assertFalse(result['ok'])
        self.assertFalse(self.record()['iterations'])

    def test_verify_plan_reports_haskell_as_unmapped_product_without_qualification(self):
        path = 'implementation/warlock/src/Contract.hs'
        self.fx.write(path, 'module Contract where\nx = 1\n')
        self.select(['src/Contract.hs'])
        before = (self.repo / '.warlock-contributor/slice.json').read_bytes()
        packet = json.loads(self.cli('verify-plan', '--selected').stdout)
        self.assertIn(path, packet['unmappedProductPaths'])
        self.assertNotIn(path, packet['supportPaths'])
        self.assertEqual(packet['cpuTargets'], [])
        self.assertFalse(packet['executionPerformed'])
        self.assertFalse(packet['acceptanceInferred'])
        self.assertEqual(before, (self.repo / '.warlock-contributor/slice.json').read_bytes())

    def test_tracked_unselected_haskell_source_cannot_be_accepted_evidence(self):
        path = 'implementation/warlock/src/Unselected.hs'
        self.fx.write(path, 'module Unselected where\nvalue = 1\n')
        self.select(['src/Desktop.elm'])
        self.assertTrue(self.fx.run_git('ls-files', '--error-unmatch', path))
        valid = self.fx.accepted_claim()
        self.fx.record_claim(valid)
        before = (self.repo / '.warlock-contributor/slice.json').read_bytes()
        invalid = dict(valid, evidence=[{'path': path, 'sha256': base.digest(self.repo / path)}])
        packet = json.loads(self.fx.record_claim(invalid, ok=False).stdout)
        self.assertEqual(packet['errors'], ['Accepted evidence cannot be product source or ignored scratch'])
        self.assertEqual(before, (self.repo / '.warlock-contributor/slice.json').read_bytes())

    def test_governed_language_revision_refuses_baseline_manifest_and_oracle_drift(self):
        self.select(['src/Desktop.elm'])
        original_path = self.repo / 'docs/elm-roadmap/baselines/requirements-pre-language-20261030.json'
        revision_path = self.repo / 'docs/elm-roadmap/language-revision.json'
        helper_path = self.repo / 'docs/elm-roadmap/tools/language_revision.py'
        current_path = self.repo / 'docs/elm-roadmap/requirements.json'
        before_record = (self.repo / '.warlock-contributor/slice.json').read_bytes()
        for path in (original_path, revision_path, helper_path):
            with self.subTest(path=str(path)):
                before = path.read_bytes()
                path.write_bytes(before + b'\n')
                packet = json.loads(self.cli('check', ok=False).stdout)
                self.assertTrue(any('Frozen original 242/417 baseline changed' in error for error in packet['errors']))
                path.write_bytes(before)
        before = current_path.read_bytes()
        for field in ('verification', 'scenario'):
            with self.subTest(field=field):
                current = json.loads(before)
                if field == 'verification':
                    current['requirements'][0]['verification'] += ' weakened verification'
                else:
                    current['requirements'][0]['scenarios'][0]['then'] += ' weakened oracle'
                self.fx.write('docs/elm-roadmap/requirements.json', current)
                packet = json.loads(self.cli('check', ok=False).stdout)
                self.assertTrue(any('Frozen original 242/417 baseline changed' in error for error in packet['errors']))
                current_path.write_bytes(before)
        self.assertEqual(before_record, (self.repo / '.warlock-contributor/slice.json').read_bytes())
        self.cli('check')

    def test_legacy_policies_one_through_four_haskell_remain_nonprogress(self):
        self.fx.write('implementation/warlock/src/Contract.hs', 'module Contract where\nx = 1\n')
        self.select(['src/Contract.hs'])
        self.fx.write('implementation/warlock/src/Contract.hs', 'module Contract where\nx = 2\n')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'new behavior')
        rec = self.record()
        for policy in (1, 2, 3, 4):
            rec['iterations'][-1].update(progressPolicy=policy, meaningfulProgress=False)
            self.fx.write('.warlock-contributor/slice.json', rec)
            self.cli('check')
            rec['iterations'][-1]['meaningfulProgress'] = True
            self.fx.write('.warlock-contributor/slice.json', rec)
            packet = json.loads(self.cli('check', ok=False).stdout)
            self.assertIn('Iteration progress assertion differs from source hashes/recorded verdict', packet['errors'])

    def test_excluded_selected_paths_and_qualification_do_not_reset(self):
        paths = ['src/Desktop.elm', 'assets/elm.js', 'qa/example.qnt', 'qa/notes.md', 'adapter/legacy.py']
        for name in paths[1:]:
            self.fx.write('implementation/warlock/' + name, 'baseline\n')
        self.select(paths)
        for name in paths[1:]:
            self.fx.write('implementation/warlock/' + name, 'changed\n')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'excluded only')
        self.assertFalse(self.record()['iterations'][-1]['meaningfulProgress'])
        self.cli('record', '--outcome', 'qualification', '--summary', 'design metadata only')
        self.assertFalse(self.record()['iterations'][-1]['meaningfulProgress'])
        self.assertEqual(json.loads(self.cli('check').stdout)['progress']['iterationsWithoutProgress'], 2)

    def test_stale_source_claim_fails_without_promoting_acceptance(self):
        self.select(['src/Desktop.elm'])
        claim = self.fx.claim()
        claim['sourceHashes']['implementation/warlock/src/Desktop.elm'] = '0' * 64
        self.fx.record_claim(claim, ok=False)
        self.assertFalse(self.record()['iterations'])

    def test_component_partial_claim_is_not_original_acceptance(self):
        self.select(['src/Desktop.elm'])
        claim = self.fx.claim()
        self.fx.record_claim(claim)
        rec = self.record()
        self.assertEqual(rec['iterations'][-1]['claims'][0]['disposition'], 'partial')
        self.assertTrue(rec['iterations'][-1]['claims'][0]['missingObservations'])
        self.assertFalse(json.loads((self.repo / 'docs/warlock-build-loop/v2/STATE.json').read_text())['releaseAccepted'])
