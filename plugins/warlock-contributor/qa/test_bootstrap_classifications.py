"""Exact reviewed bootstrap evidence cannot erase real participant history."""
import hashlib
import importlib.util
import json
import os
import unittest

import test_warlock as fixtures

_spec = importlib.util.spec_from_file_location('bootstrap_classification_policy', fixtures.CHECKER)
_policy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_policy)


class BootstrapClassificationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli

    def genuine_legacy(self, stopped=False):
        self.fixture.start()
        if stopped:
            for _ in range(2):
                self.cli('record', '--outcome', 'qualification', '--summary', 'No scenario observation')
        path = self.repo / '.warlock-contributor/slice.json'
        before = path.read_bytes()
        (self.repo / _policy.PARTICIPANT_INDEX).unlink()
        return path, before

    def entry(self, name):
        path = self.repo / name
        if path.is_symlink():
            fingerprint = 'symlink:' + hashlib.sha256(os.fsencode(os.readlink(path))).hexdigest()
            kind = 'symlink'
        else:
            fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
            kind = 'file'
        return {'kind': kind, 'fingerprint': fingerprint,
                'reason': 'Retained explicit negative fixture, not a participant history.',
                'producer': 'isolated regression fixture'}

    def classify(self, names, review_changes=None, manifest_changes=None, entries_override=None):
        payload = {'schema': 1, 'owner': 'bootstrap-owner', 'reviewer': 'independent-reviewer',
                   'entries': {name: self.entry(name) for name in names} if entries_override is None else entries_override}
        review = {'schema': 1, 'disposition': 'accepted',
                  'scope': 'participant-inventory-bootstrap-only',
                  'scenarioAcceptance': False, 'independent': True,
                  'owner': payload['owner'], 'reviewer': payload['reviewer'],
                  'classificationsSha256': _policy.json_sha256(payload)}
        review.update(review_changes or {})
        review_path = self.fixture.write('.warlock-contributor/evidence/bootstrap-review.json', review)
        manifest = dict(payload, review={
            'path': review_path.relative_to(self.repo).as_posix(),
            'sha256': hashlib.sha256(review_path.read_bytes()).hexdigest()})
        manifest.update(manifest_changes or {})
        return self.fixture.write(_policy.BOOTSTRAP_CLASSIFICATIONS, manifest)

    def assert_blocked(self, fragment):
        result = self.cli('index-participants', ok=False)
        self.assertIn(fragment, result.stdout)
        self.assertFalse((self.repo / _policy.PARTICIPANT_INDEX).exists())

    def test_exact_reviewed_malformed_and_partial_evidence_preserves_real_bytes(self):
        record, original = self.genuine_legacy()
        bad = '.warlock-contributor/store/taskbar.json'
        packet = '.warlock-contributor/worker-handoff.json'
        self.fixture.write(bad, '{ deliberate malformed store fixture')
        self.fixture.write(packet, {'owner': 'worker', 'slice': 'handoff description'})
        manifest = self.classify([bad, packet])
        evidence_before = [(self.repo / name).read_bytes() for name in (bad, packet)]
        result = json.loads(self.cli('index-participants').stdout)
        self.assertEqual(result['participantCount'], 1)
        self.assertEqual(result['recordPaths'], ['.warlock-contributor/slice.json'])
        self.assertEqual(record.read_bytes(), original)
        self.assertEqual(evidence_before, [(self.repo / name).read_bytes() for name in (bad, packet)])
        index = json.loads((self.repo / _policy.PARTICIPANT_INDEX).read_bytes())
        self.assertEqual(index['bootstrapClassifications'], {
            'path': _policy.BOOTSTRAP_CLASSIFICATIONS,
            'sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()})
        self.assertEqual(index['records']['.warlock-contributor/slice.json']['recordSha256'],
                         hashlib.sha256(original).hexdigest())
        self.assertEqual(_policy.participant_inventory(self.repo)['errors'], [])

    def test_no_manifest_keeps_original_index_payload_and_unknown_corruption_fatal(self):
        record, original = self.genuine_legacy()
        self.cli('index-participants')
        index_path = self.repo / _policy.PARTICIPANT_INDEX
        index = json.loads(index_path.read_bytes())
        self.assertEqual(set(index), {'schema', 'records', 'indexSha256'})
        self.assertEqual(index['indexSha256'], _policy.json_sha256({'schema': 1, 'records': index['records']}))
        index_path.unlink()
        self.fixture.write('.warlock-contributor/unknown.json', '{ unreadable possible history')
        self.assert_blocked('cannot classify')
        self.assertEqual(record.read_bytes(), original)

    def test_unlisted_corruption_still_blocks_with_other_reviewed_evidence(self):
        known = '.warlock-contributor/known.json'
        self.fixture.write(known, '{ known')
        self.classify([known])
        self.fixture.write('.warlock-contributor/unknown.json', '{ unknown')
        self.assert_blocked('cannot classify .warlock-contributor/unknown.json')

    def test_changed_and_missing_classified_files_are_fatal(self):
        name = '.warlock-contributor/malformed.json'
        path = self.fixture.write(name, '{ original')
        self.classify([name])
        path.write_text('{ changed')
        self.assert_blocked('artifact fingerprint differs')
        path.unlink()
        self.assert_blocked('classifications are invalid')

    def test_genuine_and_ambiguous_participant_exclusions_are_denied(self):
        record, original = self.genuine_legacy()
        self.classify(['.warlock-contributor/slice.json'])
        self.assert_blocked('cannot exclude participant or possible history')
        self.assertEqual(record.read_bytes(), original)
        for marker in ('startedUTC', 'iterations'):
            with self.subTest(marker=marker):
                packet = '.warlock-contributor/possible.json'
                self.fixture.write(packet, {'owner': 'draft', 'slice': {}, marker: []})
                self.classify([packet])
                self.assert_blocked('cannot exclude participant or possible history')

    def test_indexed_participant_cannot_be_classified_even_if_current_bytes_corrupt(self):
        self.fixture.start()
        path = self.repo / '.warlock-contributor/slice.json'
        path.write_text('{ deliberately corrupt indexed history')
        self.classify(['.warlock-contributor/slice.json'])
        result = self.cli('index-participants', ok=False)
        self.assertIn('cannot exclude indexed/control path', result.stdout)
        self.assertEqual(path.read_text(), '{ deliberately corrupt indexed history')

    def test_raw_symlink_target_is_reviewed_without_following_and_change_is_denied(self):
        record, original = self.genuine_legacy()
        target = self.fixture.write('outside.json', '{ outside target must never be parsed')
        name = '.warlock-contributor/storage-link.json'
        link = self.repo / name
        link.symlink_to('../outside.json')
        self.classify([name])
        self.cli('index-participants')
        self.assertEqual(os.readlink(link), '../outside.json')
        self.assertEqual(target.read_text(), '{ outside target must never be parsed')
        self.assertEqual(record.read_bytes(), original)
        link.unlink()
        link.symlink_to('../different-missing-target.json')
        result = self.cli('index-participants', ok=False)
        self.assertIn('artifact fingerprint differs', result.stdout)
        self.assertEqual(os.readlink(link), '../different-missing-target.json')

    def test_review_hash_payload_and_scope_flags_are_required(self):
        name = '.warlock-contributor/fixture.json'
        self.fixture.write(name, '{ negative')
        mutations = [ {'scope': 'product-acceptance'}, {'scenarioAcceptance': True},
                      {'independent': False}, {'disposition': 'partial'},
                      {'classificationsSha256': '0' * 64} ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.classify([name], review_changes=mutation)
                self.assert_blocked('exact provenance-only payload')
        manifest = self.classify([name])
        review = self.repo / json.loads(manifest.read_bytes())['review']['path']
        review.write_bytes(review.read_bytes() + b' ')
        self.assert_blocked('review artifact bytes changed')

    def test_same_casefold_owner_and_reviewer_is_not_independent(self):
        name = '.warlock-contributor/fixture.json'
        self.fixture.write(name, '{ negative')
        self.classify([name], manifest_changes={'owner': 'INDEPENDENT-REVIEWER'})
        self.assert_blocked('distinct owner and reviewer')

    def test_manifest_drift_or_removal_after_index_is_fatal(self):
        self.genuine_legacy()
        name = '.warlock-contributor/fixture.json'
        self.fixture.write(name, '{ negative')
        manifest = self.classify([name])
        self.cli('index-participants')
        original = manifest.read_bytes()
        manifest.write_bytes(original + b' ')
        result = self.cli('index-participants', ok=False)
        self.assertIn('manifest bytes changed', result.stdout)
        manifest.unlink()
        result = self.cli('index-participants', ok=False)
        self.assertIn('manifest is missing', result.stdout)

    def test_duplicate_manifest_fields_and_unsafe_paths_are_rejected(self):
        name = '.warlock-contributor/fixture.json'
        self.fixture.write(name, '{ negative')
        manifest = self.classify([name])
        manifest.write_text(manifest.read_text().replace('"schema": 1,', '"schema": 1, "schema": 1,', 1))
        self.assert_blocked('Duplicate bootstrap field')
        for excluded in ('../foreign.json', _policy.PARTICIPANT_INDEX,
                         _policy.BOOTSTRAP_CLASSIFICATIONS,
                         '.warlock-contributor/evidence/bootstrap-review.json'):
            with self.subTest(excluded=excluded):
                self.classify([name], entries_override={excluded: self.entry(name)})
                self.assert_blocked('cannot exclude indexed/control path')

    def test_present_but_null_index_binding_is_not_silently_ignored(self):
        self.fixture.start()
        index_path = self.repo / _policy.PARTICIPANT_INDEX
        index = json.loads(index_path.read_bytes())
        index['bootstrapClassifications'] = None
        index_path.write_text(json.dumps(index, indent=2) + '\n')
        result = self.cli('index-participants', ok=False)
        self.assertIn('empty bootstrap classification binding', result.stdout)

    def test_reviewed_evidence_never_resets_stopped_participant_history(self):
        record, original = self.genuine_legacy(stopped=True)
        name = '.warlock-contributor/store-fixture.json'
        self.fixture.write(name, '{ negative')
        self.classify([name])
        self.cli('index-participants')
        index_before = (self.repo / _policy.PARTICIPANT_INDEX).read_bytes()
        result = self.cli('--record', '.warlock-contributor/restart.json', 'start',
                          '--owner', 'another-worker', ok=False)
        self.assertIn('prior stopped record', result.stdout)
        self.assertEqual(record.read_bytes(), original)
        self.assertEqual((self.repo / _policy.PARTICIPANT_INDEX).read_bytes(), index_before)
        self.assertFalse((self.repo / '.warlock-contributor/restart.json').exists())

    def test_seeded_changed_bytes_never_inherit_prior_review(self):
        name = '.warlock-contributor/negative-fixture.json'
        state = 20261101
        for seed in range(16):
            with self.subTest(seed=seed):
                state = (state * 1664525 + 1013904223) % (2 ** 32)
                path = self.fixture.write(name, '{ negative seed ' + str(state))
                self.classify([name])
                path.write_bytes(path.read_bytes() + (' mutation-' + str(seed)).encode())
                self.assert_blocked('artifact fingerprint differs')


if __name__ == '__main__':
    unittest.main()
