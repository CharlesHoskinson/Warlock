"""Exact publication omissions do not erase possible participant history.

Protected runner only. Synthetic pinned manifests exercise the real inventory
validator in a temporary Git repository; no external network or CLI is mocked.
"""
import copy
import hashlib
import importlib.util
import json
from unittest import mock
import unittest

import test_warlock as fixtures

spec = importlib.util.spec_from_file_location('published_omission_policy', fixtures.CHECKER)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

NAME = '.warlock-contributor/auth-source-staged-review.json'
OTHER = '.warlock-contributor/not-published-omitted.json'
REASON = 'non-JSON runtime output; retained locally'
PUB = 'docs/warlock-build-loop/v2/remote-handoff-20261102/manifest.json'
BODY = b'non-json retained original fixture\n'
HASH = hashlib.sha256(BODY).hexdigest()


class PublishedOmissionTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.repo = self.f.repo
        self.entry = dict(kind='file', fingerprint=HASH,
                          reason='Retained independently audited nonparticipant evidence.',
                          producer='prefixed-cli-output')
        self.published = {'excluded': [{'path': NAME, 'reason': REASON}]}
        self.allowed = {NAME: dict(fingerprint=HASH, producer='prefixed-cli-output')}
        self.classifications = {NAME: copy.deepcopy(self.entry)}
        self.setup_files()

    def setup_files(self):
        payload = dict(schema=1, owner='original-owner', reviewer='independent-reviewer',
                       entries=self.classifications)
        review = dict(schema=1, disposition='accepted', scope='participant-inventory-bootstrap-only',
                      scenarioAcceptance=False, independent=True,
                      owner=payload['owner'], reviewer=payload['reviewer'],
                      classificationsSha256=policy.json_sha256(payload))
        review_path = self.f.write('.warlock-contributor/evidence/bootstrap-review.json', review)
        manifest = dict(payload, review=dict(path=review_path.relative_to(self.repo).as_posix(),
                         sha256=fixtures.digest(review_path)))
        self.class_file = self.f.write(policy.BOOTSTRAP_CLASSIFICATIONS, manifest)
        self.pub_file = self.f.write(PUB, self.published)
        self.bound = dict(path=policy.BOOTSTRAP_CLASSIFICATIONS, sha256=fixtures.digest(self.class_file))
        self.before = (self.class_file.read_bytes(), review_path.read_bytes(), self.pub_file.read_bytes())
        self.review_path = review_path

    def load(self, indexed=None, pinned_class=None, pinned_pub=None, allowed=None):
        overrides = dict(PUBLISHED_BOOTSTRAP_CLASSIFICATION_SHA256=pinned_class or fixtures.digest(self.class_file),
                         PUBLISHED_BOOTSTRAP_MANIFEST_SHA256=pinned_pub or fixtures.digest(self.pub_file),
                         PUBLISHED_BOOTSTRAP_MANIFEST=PUB,
                         PUBLISHED_BOOTSTRAP_OMISSIONS=self.allowed if allowed is None else allowed)
        # create=True lets the old implementation reach its real failing path;
        # production constants must be literal pins, not caller-controlled data.
        with mock.patch.multiple(policy, create=True, **overrides):
            return policy.bootstrap_classifications(self.repo, indexed or {}, self.bound)

    def test_pinned_exact_omission_is_recognized_without_writing_evidence(self):
        entries, bound = self.load()
        self.assertEqual(entries, self.classifications)
        self.assertEqual(bound, self.bound)
        self.assertFalse((self.repo / NAME).exists())
        self.assertEqual(self.before, (self.class_file.read_bytes(), self.review_path.read_bytes(), self.pub_file.read_bytes()))

    def test_present_original_bytes_are_verified_and_changed_file_rejected(self):
        p = self.repo / NAME
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(BODY)
        self.load()
        p.write_bytes(b'changed')
        with self.assertRaises((ValueError, OSError)): self.load()

    def test_missing_unlisted_or_nonmatching_exclusion_is_rejected(self):
        for change in ('unknown', 'wrong-reason', 'no-exclusion', 'wrong-fingerprint', 'wrong-producer', 'symlink-kind'):
            with self.subTest(change=change):
                self.classifications = {NAME: copy.deepcopy(self.entry)}
                self.published = {'excluded': [{'path': NAME, 'reason': REASON}]}
                if change == 'unknown':
                    self.classifications[OTHER] = dict(self.entry)
                if change == 'wrong-reason': self.published['excluded'][0]['reason'] = 'other'
                if change == 'no-exclusion': self.published['excluded'] = []
                if change == 'wrong-fingerprint': self.classifications[NAME]['fingerprint'] = '0' * 64
                if change == 'wrong-producer': self.classifications[NAME]['producer'] = 'unknown'
                if change == 'symlink-kind': self.classifications[NAME]['kind'] = 'symlink'
                self.setup_files()
                with self.assertRaises((ValueError, OSError)): self.load()

    def test_wrong_or_missing_pins_and_changed_review_are_rejected(self):
        for args in ({'pinned_class': '0' * 64}, {'pinned_pub': '0' * 64}):
            with self.subTest(args=args), self.assertRaises((ValueError, OSError)): self.load(**args)
        self.pub_file.unlink()
        with self.assertRaises((ValueError, OSError)): self.load(pinned_pub='0' * 64)
        self.setup_files()
        self.review_path.write_bytes(self.review_path.read_bytes() + b' ')
        with self.assertRaises((ValueError, OSError)): self.load()

    def test_indexed_and_control_paths_never_allowed_as_omissions(self):
        with self.assertRaises((ValueError, OSError)): self.load(indexed={NAME: {}})
        self.classifications = {policy.BOOTSTRAP_CLASSIFICATIONS: dict(self.entry)}
        self.published = {'excluded': [{'path': policy.BOOTSTRAP_CLASSIFICATIONS, 'reason': REASON}]}
        self.allowed = {policy.BOOTSTRAP_CLASSIFICATIONS: dict(fingerprint=HASH, producer='prefixed-cli-output')}
        self.setup_files()
        with self.assertRaises((ValueError, OSError)): self.load()

    def test_missing_parent_and_existing_broken_symlink_are_not_absence(self):
        p = self.repo / NAME
        p.parent.mkdir(parents=True, exist_ok=True)
        p.symlink_to('absent-target')
        with self.assertRaises((ValueError, OSError)): self.load()
        p.unlink()
        # An exact leaf omission may be absent, but a symlinked directory is unsafe.
        parent = self.repo / '.warlock-contributor' / 'haskell-root-research'
        parent.symlink_to('/tmp', target_is_directory=True)
        name = '.warlock-contributor/haskell-root-research/pkg.json'
        self.classifications = {name: dict(self.entry, producer='research-capture')}
        self.allowed = {name: dict(fingerprint=HASH, producer='research-capture')}
        self.published = {'excluded': [{'path': name, 'reason': REASON}]}
        self.setup_files()
        with self.assertRaises((ValueError, OSError)): self.load()

    def test_inventory_and_census_keep_exact_index_and_block_unlisted_omission(self):
        # Bootstrap a real fixture participant before installing synthetic
        # reviewed classification/index binding; this is fixture setup only.
        self.class_file.unlink()
        self.f.start()
        self.setup_files()
        index_path = self.repo / policy.PARTICIPANT_INDEX
        index = json.loads(index_path.read_bytes())
        index['bootstrapClassifications'] = self.bound
        index['indexSha256'] = policy.json_sha256(policy.participant_index_payload(index['records'], self.bound))
        self.f.write(policy.PARTICIPANT_INDEX, index)
        record_path = self.repo / '.warlock-contributor/slice.json'
        original_record = record_path.read_bytes()
        index_before = index_path.read_bytes()
        overrides = dict(PUBLISHED_BOOTSTRAP_CLASSIFICATION_SHA256=fixtures.digest(self.class_file),
                         PUBLISHED_BOOTSTRAP_MANIFEST_SHA256=fixtures.digest(self.pub_file),
                         PUBLISHED_BOOTSTRAP_MANIFEST=PUB, PUBLISHED_BOOTSTRAP_OMISSIONS=self.allowed)
        with mock.patch.multiple(policy, create=True, **overrides):
            inventory = policy.participant_inventory(self.repo)
            self.assertEqual(inventory['errors'], [])
            census = policy.owner_census_bytes(self.repo)
            policy.verify_current_owner_census(self.repo, census)
        self.assertEqual(index_path.read_bytes(), index_before)
        self.assertEqual(record_path.read_bytes(), original_record)

        # A second missing classification absent from the publication remains
        # fatal, even when fixture classification/review/index pins agree.
        self.classifications[OTHER] = dict(self.entry)
        self.setup_files()
        index['bootstrapClassifications'] = self.bound
        index['indexSha256'] = policy.json_sha256(policy.participant_index_payload(index['records'], self.bound))
        self.f.write(policy.PARTICIPANT_INDEX, index)
        changed_fixture_index = index_path.read_bytes()
        overrides['PUBLISHED_BOOTSTRAP_CLASSIFICATION_SHA256'] = fixtures.digest(self.class_file)
        with mock.patch.multiple(policy, create=True, **overrides):
            self.assertTrue(policy.participant_inventory(self.repo)['errors'])
            with self.assertRaises(ValueError): policy.verify_current_owner_census(self.repo, policy.owner_census_bytes(self.repo))
        self.assertEqual(index_path.read_bytes(), changed_fixture_index)
        self.assertEqual(record_path.read_bytes(), original_record)
