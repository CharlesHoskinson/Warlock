"""Accepted source tuples identify the tested committed bytes, without checkout."""
import json
import unittest

import test_warlock as fixtures


class AcceptedRevisionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli
        self.source = 'implementation/warlock/src/Desktop.elm'
        self.fixture.start()

    def test_changed_source_cannot_be_accepted_against_an_older_commit(self):
        self.fixture.write(self.source, 'new visible behavior\n')
        claim = self.fixture.accepted_claim()
        before = (self.repo / '.warlock-contributor/slice.json').read_bytes()
        result = json.loads(self.fixture.record_claim(claim, ok=False).stdout)
        self.assertTrue(any('bytes differ' in error for error in result['errors']))
        self.assertEqual(before, (self.repo / '.warlock-contributor/slice.json').read_bytes())
        # Staging alone is still not a reproducible accepted revision.
        self.fixture.run_git('add', self.source)
        self.fixture.record_claim(claim, ok=False)
        self.fixture.run_git('commit', '-qm', 'actual implementation')
        claim['sourceTuple']['sourceRevision'] = self.fixture.run_git('rev-parse', 'HEAD')
        self.fixture.record_claim(claim)
        self.cli('check')

    def test_mutable_refs_abbreviations_tags_and_options_are_refused(self):
        claim = self.fixture.accepted_claim()
        self.fixture.run_git('branch', 'accepted-source')
        self.fixture.run_git('tag', 'accepted-tag')
        for revision in ('HEAD', 'accepted-source', 'accepted-tag',
                         claim['sourceTuple']['sourceRevision'][:12], '--help'):
            with self.subTest(revision=revision):
                candidate = dict(claim, sourceTuple=dict(claim['sourceTuple'], sourceRevision=revision))
                self.fixture.record_claim(candidate, ok=False)
        self.fixture.record_claim(claim)

    def test_commit_without_selected_source_cannot_support_acceptance(self):
        claim = self.fixture.accepted_claim()
        self.fixture.run_git('rm', self.source)
        self.fixture.run_git('commit', '-qm', 'source absent in named revision')
        self.fixture.write(self.source, 'original Elm source\n')
        # The hash follows the working file; the named commit still has no file.
        claim['sourceHashes'][self.source] = fixtures.digest(self.repo / self.source)
        claim['sourceTuple']['sourceRevision'] = self.fixture.run_git('rev-parse', 'HEAD')
        result = json.loads(self.fixture.record_claim(claim, ok=False).stdout)
        self.assertTrue(any('lacks a regular source file' in error for error in result['errors']))

    def test_committed_symlink_is_not_a_regular_tested_source(self):
        claim = self.fixture.accepted_claim()
        source = self.repo / self.source
        source.unlink()
        source.symlink_to('different-source.elm')
        self.fixture.run_git('add', self.source)
        self.fixture.run_git('commit', '-qm', 'symlink source fixture')
        source.unlink()
        source.write_text('different-source.elm')
        claim['sourceHashes'][self.source] = fixtures.digest(source)
        claim['sourceTuple']['sourceRevision'] = self.fixture.run_git('rev-parse', 'HEAD')
        result = json.loads(self.fixture.record_claim(claim, ok=False).stdout)
        self.assertTrue(any('lacks a regular source file' in error for error in result['errors']))

    def test_every_declared_source_must_match_its_committed_bytes(self):
        # A second declaration with a space exercises literal Git path lookup.
        self.fixture.write('implementation/warlock/assets/menu view.css', 'old CSS\n')
        self.fixture.run_git('add', 'implementation/warlock/assets/menu view.css')
        self.fixture.run_git('commit', '-qm', 'second source fixture')
        self.cli('extend', '--path', 'assets/menu view.css', '--reason', 'Selected feedback styling')
        claim = self.fixture.accepted_claim()
        other = 'implementation/warlock/assets/menu view.css'
        self.fixture.write(other, 'new CSS\n')
        claim['sourceHashes'][other] = fixtures.digest(self.repo / other)
        self.fixture.record_claim(claim, ok=False)
        self.fixture.run_git('add', other)
        self.fixture.run_git('commit', '-qm', 'tested second source')
        claim['sourceTuple']['sourceRevision'] = self.fixture.run_git('rev-parse', 'HEAD')
        self.fixture.record_claim(claim)

    def test_historical_accepted_observation_keeps_its_original_commit(self):
        claim = self.fixture.accepted_claim()
        self.fixture.record_claim(claim)
        original_revision = claim['sourceTuple']['sourceRevision']
        self.fixture.write(self.source, 'later source behavior\n')
        self.fixture.run_git('add', self.source)
        self.fixture.run_git('commit', '-qm', 'later change')
        self.cli('record', '--outcome', 'production-fix', '--summary', 'Later change; original observation historical')
        packet = json.loads(self.cli('handoff').stdout)
        self.assertFalse(packet['observations'][0]['evidenceMatchesCurrentSources'])
        record = json.loads((self.repo / '.warlock-contributor/slice.json').read_text())
        self.assertEqual(record['iterations'][0]['claims'][0]['sourceTuple']['sourceRevision'], original_revision)

    def test_reviewer_requesting_changes_cannot_support_accepted_claim(self):
        claim = self.fixture.accepted_claim()
        for disposition in ('failed', 'partial', 'needs-changes', ''):
            claim['reviewer']['disposition'] = disposition
            self.fixture.record_claim(claim, ok=False)
        claim['reviewer']['disposition'] = 'accepted'
        self.fixture.record_claim(claim)

    def test_check_catches_edited_record_with_empty_accepted_evidence(self):
        self.fixture.record_claim(self.fixture.accepted_claim())
        path = self.repo / '.warlock-contributor/slice.json'
        record = json.loads(path.read_text())
        record['iterations'][0]['claims'][0]['evidence'] = []
        path.write_text(json.dumps(record))
        result = json.loads(self.cli('check', ok=False).stdout)
        self.assertIn('Accepted claim needs retained evidence', result['errors'])

    def test_validation_leaves_index_ledger_foreign_drafts_and_head_untouched(self):
        self.fixture.record_claim(self.fixture.accepted_claim())
        protected = ['.git/index', '.warlock-contributor/slice.json', 'foreign.txt',
                     'docs/warlock-build-loop/v2/requirement-ledger.json']
        before = [(self.repo / name).read_bytes() for name in protected]
        head = self.fixture.run_git('rev-parse', 'HEAD')
        self.cli('check')
        self.cli('review')
        self.assertEqual(before, [(self.repo / name).read_bytes() for name in protected])
        self.assertEqual(head, self.fixture.run_git('rev-parse', 'HEAD'))


if __name__ == '__main__':
    unittest.main()
