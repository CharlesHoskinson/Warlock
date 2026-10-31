"""Prospective real-engine progress regressions. Root applies candidate and runs; unexecuted."""
import copy
import json
import unittest
import test_warlock as base

class HaskellPackagePolicy6Tests(unittest.TestCase):
    def setUp(self):
        self.fx = base.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.repo, self.cli = self.fx.repo, self.fx.cli

    def record(self):
        return json.loads((self.repo / '.warlock-contributor/slice.json').read_text())

    def select(self, paths):
        for name in paths:
            self.fx.write('implementation/warlock/' + name, 'module Example where\nvalue = 1\n')
        self.fx.slice['paths'] = paths
        self.fx.write('docs/warlock-build-loop/v2/STATE.json', {
            'schema': 1, 'sourceCandidate': 'implementation/warlock',
            'heldParent': 'implementation/warlock-preview-provider-v143',
            'activeSlice': self.fx.slice, 'releaseAccepted': False})
        self.fx.run_git('add', '.')
        self.fx.run_git('commit', '-qm', 'selected clean package fixture')
        self.fx.start()

    def change(self, path):
        self.fx.write('implementation/warlock/' + path, 'module Example where\nvalue = 2\n')

    def fix(self):
        return self.cli('record', '--outcome', 'production-fix', '--summary', 'actual selected source delta')

    def test_actual_package_hs_and_hsc_each_count_then_unchanged_does_not(self):
        hs = 'haskell/protocol/src/Warlock/Transport/Channel.hs'
        hsc = 'haskell/held-document/src/Warlock/Platform/Resolver/Internal.hsc'
        self.select([hs, hsc])
        for path in (hs, hsc):
            self.change(path)
            self.fix()
            last = self.record()['iterations'][-1]
            self.assertEqual(last['progressPolicy'], 6)
            self.assertTrue(last['meaningfulProgress'])
        before = copy.deepcopy(self.record()['iterations'])
        self.fix()
        self.assertFalse(self.record()['iterations'][-1]['meaningfulProgress'])
        self.assertEqual(before, self.record()['iterations'][:-1])
        self.cli('check')

    def test_production_module_names_are_not_support_directories(self):
        # Capitalized Haskell module namespaces are product source, even when
        # their English names resemble lower-case support directory names.
        paths = ['haskell/protocol/src/Warlock/Model/Domain.hs',
                 'haskell/protocol/src/Warlock/Build/Plan.hs']
        self.select(paths)
        for path in paths:
            self.change(path)
            self.fix()
            self.assertTrue(self.record()['iterations'][-1]['meaningfulProgress'])
        self.cli('check')

    def test_support_layouts_do_not_count_and_timer_stays_original(self):
        paths = ['haskell/protocol/test/Main.hs', 'haskell/protocol/tests/Main.hsc',
                 'haskell/protocol/formal/model.qnt', 'haskell/protocol/formal/Model.hs',
                 'haskell/protocol/README.md', 'haskell/protocol/protocol.cabal',
                 'haskell/protocol/dist-newstyle/build/Generated.hs',
                 'haskell/protocol/build/Main.hs', 'haskell/protocol/app/Main.hs',
                 'haskell/protocol/qa/Main.hs', 'haskell/protocol/src/formal/Model.hs',
                 'haskell/protocol/src/generated/Binding.hsc',
                 'haskell/protocol/src/README.md', 'haskell/arbitrary.hs',
                 'haskell/protocol/other/src/NotRoot.hs', 'qa/Example.hs']
        self.select(paths)
        started = self.record()['startedUTC']
        for path in paths:
            self.change(path)
        self.fix()
        self.assertFalse(self.record()['iterations'][-1]['meaningfulProgress'])
        packet = json.loads(self.cli('check').stdout)
        self.assertEqual(packet['progress']['lastRecordedProgressUTC'], started)
        self.assertEqual(packet['progress']['iterationsWithoutProgress'], 1)

    def test_qualification_with_real_source_delta_does_not_count(self):
        path = 'haskell/process-custody/src/Warlock/Capture/Process/Internal.hsc'
        self.select([path]); self.change(path)
        self.cli('record', '--outcome', 'qualification', '--summary', 'qualification only')
        self.assertFalse(self.record()['iterations'][-1]['meaningfulProgress'])
        self.cli('check')

    def test_policy5_false_history_stays_false_and_unmodified_then_new_delta_counts(self):
        path = 'haskell/protocol/src/Warlock/Transport/Channel.hs'
        self.select([path]); self.change(path); self.fix()
        rec = self.record()
        rec['iterations'][-1].update(progressPolicy=5, meaningfulProgress=False)
        self.fx.write('.warlock-contributor/slice.json', rec)
        self.cli('check')
        historical = copy.deepcopy(rec['iterations'][0])
        rec['iterations'][0]['meaningfulProgress'] = True
        self.fx.write('.warlock-contributor/slice.json', rec)
        result = json.loads(self.cli('check', ok=False).stdout)
        self.assertIn('Iteration progress assertion differs from source hashes/recorded verdict', result['errors'])
        rec['iterations'][0] = historical
        self.fx.write('.warlock-contributor/slice.json', rec)
        self.fx.write('implementation/warlock/' + path, 'module Example where\nvalue = 3\n')
        self.fix()
        self.assertEqual(self.record()['iterations'][0], historical)
        self.assertTrue(self.record()['iterations'][-1]['meaningfulProgress'])
        self.assertEqual(self.record()['iterations'][-1]['progressPolicy'], 6)
        self.cli('check')

    def test_foreign_package_edit_refused_without_record_mutation(self):
        self.select(['src/Desktop.elm'])
        before = (self.repo / '.warlock-contributor/slice.json').read_bytes()
        self.change('haskell/protocol/src/Foreign.hs')
        result = json.loads(self.cli('record', '--outcome', 'production-fix', '--summary', 'foreign', ok=False).stdout)
        self.assertTrue(any('Unowned or archival implementation change' in x for x in result['errors']))
        self.assertEqual(before, (self.repo / '.warlock-contributor/slice.json').read_bytes())

    def test_declaring_existing_dependency_is_not_new_source_progress(self):
        extra = 'implementation/warlock/haskell/protocol/src/Existing.hs'
        self.fx.write(extra, 'module Existing where\nvalue = 1\n')
        self.select(['src/Desktop.elm'])
        self.cli('extend', '--path', extra, '--reason', 'actual existing API dependency')
        self.fix()
        self.assertFalse(self.record()['iterations'][-1]['meaningfulProgress'])
        self.cli('check')

    def test_unmapped_package_source_is_product_not_automatic_native_evidence(self):
        path = 'haskell/protocol/src/Warlock/Transport/Channel.hs'
        self.select([path])
        before = (self.repo / '.warlock-contributor/slice.json').read_bytes()
        packet = json.loads(self.cli('verify-plan', '--selected').stdout)
        full = 'implementation/warlock/' + path
        self.assertIn(full, packet['unmappedProductPaths'])
        self.assertNotIn(full, packet['supportPaths'])
        self.assertFalse(packet['executionPerformed'])
        self.assertFalse(packet['acceptanceInferred'])
        self.assertEqual(before, (self.repo / '.warlock-contributor/slice.json').read_bytes())

    def test_policy5_legacy_src_hs_true_remains_true(self):
        path = 'src/Contract.hs'
        self.select([path]); self.change(path); self.fix()
        rec = self.record()
        rec['iterations'][-1].update(progressPolicy=5, meaningfulProgress=True)
        self.fx.write('.warlock-contributor/slice.json', rec)
        before = (self.repo / '.warlock-contributor/slice.json').read_bytes()
        self.cli('check')
        self.assertEqual(before, (self.repo / '.warlock-contributor/slice.json').read_bytes())

    def test_unselected_package_product_cannot_be_independent_accepted_evidence(self):
        path = 'implementation/warlock/haskell/protocol/src/Unselected.hs'
        self.fx.write(path, 'module Unselected where\nvalue = 1\n')
        self.select(['src/Desktop.elm'])
        valid = self.fx.accepted_claim()
        self.fx.record_claim(valid)
        before = (self.repo / '.warlock-contributor/slice.json').read_bytes()
        invalid = dict(valid, evidence=[{'path': path, 'sha256': base.digest(self.repo / path)}])
        packet = json.loads(self.fx.record_claim(invalid, ok=False).stdout)
        self.assertIn('Accepted evidence cannot be product source or ignored scratch', packet['errors'])
        self.assertEqual(before, (self.repo / '.warlock-contributor/slice.json').read_bytes())

if __name__ == '__main__':
    unittest.main()
