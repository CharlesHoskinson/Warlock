"""Later foreign-owner edits require explicit exact provenance, never adoption."""
import hashlib
import json
import unittest

import test_warlock as fixtures
import test_foreign_reconciliation as foreign_fixture
import test_bootstrap_classifications as bootstrap_fixture

policy = foreign_fixture.policy


class ForeignIntroductionTests(unittest.TestCase):
    transition = foreign_fixture.ReconciliationTests.transition
    prepare_transitions = foreign_fixture.ReconciliationTests.prepare_transitions
    reconcile = foreign_fixture.ReconciliationTests.reconcile
    entry = bootstrap_fixture.BootstrapClassificationTests.entry
    classify = bootstrap_fixture.BootstrapClassificationTests.classify

    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli
        self.name = 'implementation/warlock/src/SeparateLater.elm'
        self.absent = 'implementation/warlock/src/NewSeparate.elm'
        self.fixture.write(self.name, 'module SeparateLater exposing (value)\nvalue = 1\n')
        self.baseline_link = 'implementation/warlock/src/OriginalSymlink.elm'
        (self.repo / self.baseline_link).symlink_to('SeparateLater.elm')
        self.fixture.run_git('add', self.name, self.baseline_link)
        self.fixture.run_git('commit', '-qm', 'clean separate input before target participant')
        self.initial = fixtures.digest(self.repo / self.name)
        self.fixture.start()
        self.record_path = '.warlock-contributor/slice.json'
        self.record_file = self.repo / self.record_path
        self.original = self.record_file.read_bytes()
        self.record = json.loads(self.original)
        self.identity = policy.record_identity(self.record, self.record_path)
        self.sidecar = policy.reconciliation_path(self.repo, dict(self.record, _recordPath=self.record_path))
        self.counter, self.owner_records = 0, {}

    def introduce(self, name=None):
        name = name or self.name
        baseline = self.initial if name == self.name else None
        entry = self.transition(name, previous=baseline)
        entry['introduceForeign'] = True
        review = json.loads((self.repo / entry['reviewFile']).read_bytes())
        review.update(disposition='accepted', introducedForeign=True,
                      baselineRevision=self.record['sourceRevision'])
        self.fixture.write(entry['reviewFile'], review)
        return entry

    def changed(self, name=None, value='independent owner changed bytes'):
        self.fixture.write(name or self.name, value)

    def assert_original(self):
        self.assertEqual(self.original, self.record_file.read_bytes())

    def test_atomic_clean_and_absent_introduction_preserves_custody_and_staging(self):
        self.changed(); self.changed(self.absent)
        self.cli('check', ok=False)
        entries = [self.introduce(), self.introduce(self.absent)]
        packet = json.loads(self.reconcile(entries).stdout)
        self.assertFalse(packet['scenarioAcceptanceInferred'])
        self.assert_original()
        events = json.loads(self.sidecar.read_bytes())['events']
        self.assertEqual([e['eventSchema'] for e in events], [3, 3])
        self.assertEqual([e['fromSha256'] for e in events], [self.initial, None])
        self.cli('check')
        self.assertEqual(json.loads(self.cli('handoff').stdout)['protectedForeignPaths'], sorted([self.name, self.absent]))
        self.fixture.run_git('add', self.name)
        result = self.cli('review', '--include', self.name, ok=False)
        self.assertIn('Staged protected foreign path', result.stdout)
        self.assert_original()

    def test_missing_explicit_flag_and_false_or_numeric_flags_refused(self):
        self.changed()
        for value in [None, False, 1]:
            entry = self.introduce()
            if value is None: entry.pop('introduceForeign')
            else: entry['introduceForeign'] = value
            self.reconcile([entry], ok=False)
            self.assertFalse(self.sidecar.exists())
        self.assert_original()

    def test_review_requires_accepted_exact_typed_independent_provenance(self):
        self.changed()
        for field, value in [('disposition', 'partial'), ('disposition', 'rejected'),
                             ('schema', True), ('scenarioAcceptance', 0),
                             ('introducedForeign', 1), ('independent', False),
                             ('reviewer', 'separate-model-owner'),
                             ('baselineRevision', '0' * 40), ('previousSha256', None)]:
            with self.subTest(field=field, value=value):
                entry = self.introduce()
                review = json.loads((self.repo / entry['reviewFile']).read_bytes())
                review[field] = value
                self.fixture.write(entry['reviewFile'], review)
                self.reconcile([entry], ok=False)
                self.assertFalse(self.sidecar.exists())
        self.assert_original()

    def test_owner_current_hash_and_unique_owner_census_are_required(self):
        self.changed()
        entry = self.introduce()
        self.changed(value='unrecorded newer owner bytes')
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())
        entry = self.introduce()
        other = json.loads((self.repo / entry['sourceRecordSnapshot']).read_bytes())
        self.fixture.write('.warlock-contributor/competing-owner.json', other)
        self.cli('index-participants')
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())
        self.assert_original()

    def test_current_unowned_selected_unsafe_nonregular_and_unrelated_drift_refused(self):
        self.changed()
        entry = self.introduce()
        self.changed('implementation/warlock/src/UnrelatedLater.elm')
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())
        (self.repo / 'implementation/warlock/src/UnrelatedLater.elm').unlink()
        for name in ['implementation/warlock/src/Desktop.elm', '../escape', 'docs/new.md']:
            bad = dict(entry, path=name)
            self.reconcile([bad], ok=False)
            self.assertFalse(self.sidecar.exists())
        (self.repo / self.name).unlink()
        (self.repo / self.name).symlink_to(self.repo / 'foreign.txt')
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())
        self.assert_original()

    def test_later_transition_keeps_intro_and_never_permits_adoption(self):
        self.changed()
        self.reconcile([self.introduce()])
        first = json.loads(self.sidecar.read_bytes())['events'][0]
        previous = fixtures.digest(self.repo / self.name)
        self.changed(value='next independent owner bytes')
        entry = self.transition(self.name, previous=previous)
        review = json.loads((self.repo / entry['reviewFile']).read_bytes())
        review['disposition'] = 'accepted'
        self.fixture.write(entry['reviewFile'], review)
        self.reconcile([entry])
        events = json.loads(self.sidecar.read_bytes())['events']
        self.assertEqual(events[0], first)
        self.assertEqual(events[1]['eventSchema'], 2)
        self.cli('check')
        result = self.cli('extend', '--path', 'src/SeparateLater.elm',
                          '--reason', 'must not adopt another owner',
                          '--adopt-dirty', self.name, '--ownership-note', 'not authority', ok=False)
        self.assertIn('Introduced foreign custody', result.stdout)
        self.assert_original()
        self.changed(value='unreviewed third source')
        self.assertIn('Reconciled foreign path changed', self.cli('check', ok=False).stdout)

    def test_changed_baseline_and_stale_census_refuse_without_write(self):
        self.changed()
        entry = self.introduce()
        transitions = self.prepare_transitions([entry])
        self.fixture.write('.warlock-contributor/owner-new.json', json.loads((self.repo / entry['sourceRecordSnapshot']).read_bytes()))
        self.cli('index-participants')
        self.fixture.write('.warlock-contributor/transitions.json', transitions)
        self.cli('reconcile-foreign', '--transition-file', '.warlock-contributor/transitions.json', ok=False)
        self.assertFalse(self.sidecar.exists())
        self.assert_original()

    def test_original_symlink_baseline_is_not_a_regular_clean_input(self):
        (self.repo / self.baseline_link).unlink()
        self.changed(self.baseline_link)
        self.reconcile([self.introduce(self.baseline_link)], ok=False)
        self.assertFalse(self.sidecar.exists())
        self.assert_original()

    def test_unowned_or_self_owned_source_record_never_authorizes_introduction(self):
        self.changed()
        for own, paths in [(self.record['owner'], [self.name]), ('separate-model-owner', [])]:
            entry = self.introduce()
            source = json.loads((self.repo / entry['sourceRecordPath']).read_bytes())
            source['owner'], source['slice']['paths'] = own, paths
            self.fixture.write(entry['sourceRecordPath'], source)
            self.fixture.write(entry['sourceRecordSnapshot'], source)
            self.fixture.refresh_fixture_participant_index(entry['sourceRecordPath'])
            review = json.loads((self.repo / entry['reviewFile']).read_bytes())
            review.update(sourceOwner=own, sourceRecordSnapshotSha256=fixtures.digest(self.repo / entry['sourceRecordSnapshot']))
            self.fixture.write(entry['reviewFile'], review)
            self.reconcile([entry], ok=False)
            self.assertFalse(self.sidecar.exists())
        self.assert_original()

    def test_bootstrap_bound_owner_census_and_introduction_use_exact_index_payload(self):
        self.changed()
        entry = self.introduce()
        retained = '.warlock-contributor/retained-generator.json'
        self.fixture.write(retained, '{ retained malformed nonparticipant evidence')
        self.classify([retained])
        index = self.repo / policy.PARTICIPANT_INDEX
        index.unlink()  # Deliberate isolated legacy/bootstrap fixture only.
        self.cli('index-participants')
        index_before = index.read_bytes()
        self.assertIn('bootstrapClassifications', json.loads(index_before))
        self.reconcile([entry])
        self.assertEqual(index_before, index.read_bytes())
        self.cli('check')
        self.assert_original()
        self.fixture.write(retained, '{ changed retained artifact')
        # Census creation validates the indexed bootstrap artifact bindings.
        # Ordinary check validates this participant, not the complete inventory.
        result = self.cli('owner-census', ok=False)
        self.assertIn('Bootstrap classification artifact fingerprint differs', result.stdout)
        self.assertEqual(index_before, index.read_bytes())
        self.assert_original()

    def test_replay_rejects_forged_baseline_and_rejected_review(self):
        self.changed()
        entry = self.introduce()
        self.reconcile([entry])
        original = self.sidecar.read_bytes()
        data = json.loads(original)
        data['events'][0]['baselineRevision'] = '0' * 40
        event = data['events'][0]
        event['eventSha256'] = policy.json_sha256({k: v for k, v in event.items() if k != 'eventSha256'})
        self.fixture.write(str(self.sidecar.relative_to(self.repo)), data)
        self.cli('check', ok=False)
        self.sidecar.write_bytes(original)
        review = json.loads((self.repo / entry['reviewFile']).read_bytes())
        review['disposition'] = 'rejected'
        self.fixture.write(entry['reviewFile'], review)
        self.cli('check', ok=False)
        self.assert_original()


if __name__ == '__main__':
    unittest.main()
