"""Network-free original-record recovery contract for the protected QA runner.

Fixtures use the real contributor checker and temporary Git repository. The
only mocked external observation is the live authenticated claim query. Tests
patch the three fixed identity/archive constants solely to use synthetic bytes;
production constants must name the one original record and published archive.
"""
import copy
import datetime as dt
import hashlib
import importlib.util
import io
import tarfile
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import test_warlock as fixtures

spec = importlib.util.spec_from_file_location('record_recovery_policy', fixtures.CHECKER)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

CACHES = ('plugins/warlock-contributor/scripts/__pycache__/warlock.cpython-314.pyc',
          'window-integration-qa/__pycache__/qa_launch.cpython-314.pyc')
TOOL = 'tools/check_tea_cpu.py'
NAMES = (*CACHES, TOOL)
SOURCES = ('plugins/warlock-contributor/scripts/warlock.py', 'window-integration-qa/qa_launch.py')
PREFIX = '.warlock-contributor/evidence/tea004-recovery/'


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        if not callable(getattr(policy, 'reconcile_tea004_recovery', None)):
            self.fail('specific atomic TEA004 recovery is not implemented')
        self.f = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.repo = self.f.repo
        for name in (*NAMES, SOURCES[1]):
            self.f.write(name, 'tracked original ' + name + '\n')
        self.f.run_git('add', '--', *NAMES, SOURCES[1])
        self.f.run_git('commit', '-qm', 'fixture tracked inputs')
        for name in NAMES:
            self.f.write(name, 'captured dirty ' + name + '\n')
        self.f.cli('start', '--owner', 'lead')
        self.record_path = '.warlock-contributor/slice.json'
        self.original = (self.repo / self.record_path).read_bytes()
        self.index = (self.repo / '.warlock-contributor/participant-index.json').read_bytes()
        self.record = json.loads(self.original)
        self.record['_recordPath'] = self.record_path
        self.reqs, self.state = policy.context(self.repo)
        self.identity = policy.record_identity(self.record, self.record_path)
        (self.repo / CACHES[0]).unlink()
        self.f.write(CACHES[1], 'new tracked cache bytes\n')
        self.f.write(TOOL, 'current reviewed tooling source\n')
        archive_name = PREFIX + 'archive.tar.gz'
        self.archive = self.repo / archive_name
        self.archive.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(self.archive, 'w:gz') as archive:
            member = tarfile.TarInfo(self.record_path)
            member.size = len(self.original)
            archive.addfile(member, io.BytesIO(self.original))
        self.census_path = '.warlock-contributor/evidence/foreign-owner-censuses/fixture.json'
        self.census = self.f.write(self.census_path, policy.owner_census_bytes(self.repo))
        self.snapshot = self.f.write(PREFIX + 'record.json', json.loads(self.original))
        self.snapshot.write_bytes(self.original)
        at = dt.datetime.now(dt.timezone.utc)
        self.live = [dict(resource='file:' + str(self.repo / TOOL), holder='lead',
                          holder_did='did:key:z6Mkh123456789ABCDEFGH',
                          lease_end=(at + dt.timedelta(hours=1)).isoformat(), queue=[])]
        self.proof = self.f.write(PREFIX + 'claim.json', dict(schema=1, owner='lead', run='fixture-run',
                                  observedUTC=at.isoformat(), claims=self.live))
        self.entries = []
        for i, name in enumerate(NAMES):
            current = policy.fingerprint(self.repo, name)
            snap = None
            if current is not None:
                snap = PREFIX + str(i) + '-current.bin'
                path = self.repo / snap
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((self.repo / name).read_bytes())
            source = SOURCES[i] if i < 2 else None
            entry = dict(path=name, kind='cache' if i < 2 else 'same-owner-tool',
                         fromSha256=self.record['foreignDirty'][name], toSha256=current,
                         currentSnapshot=snap, currentSnapshotSha256=current,
                         sourcePath=source, sourceSha256=fixtures.digest(self.repo / source) if source else None,
                         reason='preserve historical custody during remote recovery')
            self.entries.append(entry)
        self.payload = dict(schema=1, recordPath=self.record_path, recordIdentitySha256=self.identity,
                            recordSnapshot=PREFIX + 'record.json', recordSnapshotSha256=fixtures.digest(self.snapshot),
                            archive=PREFIX + 'archive.tar.gz', archiveSha256=fixtures.digest(self.archive),
                            ownerCensusSnapshot=self.census_path, ownerCensusSnapshotSha256=fixtures.digest(self.census),
                            claimProof=PREFIX + 'claim.json', claimProofSha256=fixtures.digest(self.proof),
                            entries=self.entries, reviewFile=PREFIX + 'review.json')
        self.review = dict(schema=1, disposition='accepted', scope='tea004-recovery-provenance-only',
                           independent=True, scenarioAcceptance=False, reviewer='independent-reviewer',
                           payloadSha256=self.payload_hash(), sourceOwner='lead')
        self.write_payload()
        # Fixed constants are explicit injection points only in isolated fixtures.
        constants = {'TEA004_RECOVERY_RECORD': self.record_path,
                     'TEA004_RECOVERY_IDENTITY': self.identity,
                     'TEA004_RECOVERY_ARCHIVE_SHA256': fixtures.digest(self.archive)}
        self.patches = [mock.patch.object(policy, key, value) for key, value in constants.items()]
        for patch in self.patches:
            patch.start()
            self.addCleanup(patch.stop)

    def payload_hash(self):
        # Avoid a circular digest: review path is included, review bytes are not.
        raw = json.dumps(self.payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
        return hashlib.sha256(raw).hexdigest()

    def write_payload(self):
        self.f.write(PREFIX + 'review.json', self.review)
        self.f.write(PREFIX + 'batch.json', self.payload)

    def apply(self):
        args = SimpleNamespace(transition_file=PREFIX + 'batch.json')
        with mock.patch.object(policy, 'support_live_claims', return_value=self.live):
            return policy.reconcile_tea004_recovery(self.repo, self.record, self.reqs, self.state, args)

    def assert_unchanged(self):
        self.assertEqual((self.repo / self.record_path).read_bytes(), self.original)
        self.assertEqual((self.repo / '.warlock-contributor/participant-index.json').read_bytes(), self.index)

    def test_atomic_exact_batch_preserves_record_and_detects_later_drift(self):
        result = self.apply()
        self.assertTrue(result['participantBytesUnchanged'])
        self.assertFalse(result['scenarioAcceptanceInferred'])
        self.assert_unchanged()
        overlay, errors, _ = policy.protected_reconciliations(self.repo, self.record)
        self.assertEqual(errors, [])
        self.assertEqual({n: overlay[n] for n in NAMES},
                         {entry['path']: entry['toSha256'] for entry in self.entries})
        self.f.write(TOOL, 'subsequent unreviewed change')
        self.assertTrue(policy.protected_reconciliations(self.repo, self.record)[1])

    def test_rejects_partial_duplicate_unknown_and_selected_paths_atomically(self):
        for entries in (self.entries[:2], self.entries + self.entries[:1],
                        self.entries[:2] + [dict(self.entries[2], path='tools/other.py')],
                        self.entries[:2] + [dict(self.entries[2], path='implementation/warlock/src/Desktop.elm')]):
            with self.subTest(entries=entries):
                self.payload['entries'] = entries
                self.review['payloadSha256'] = self.payload_hash()
                self.write_payload()
                with self.assertRaises(ValueError):
                    self.apply()
                self.assert_unchanged()
                self.assertFalse(policy.tea004_recovery_sidecar(self.repo, self.record).exists())

    def test_rejects_unreviewed_bytes_identity_and_evidence(self):
        originals = copy.deepcopy(self.payload), copy.deepcopy(self.review)
        for key, value in (('recordIdentitySha256', '0' * 64), ('archiveSha256', '0' * 64),
                           ('recordSnapshotSha256', '0' * 64), ('claimProofSha256', '0' * 64)):
            with self.subTest(key=key):
                self.payload, self.review = copy.deepcopy(originals)
                self.payload[key] = value
                self.review['payloadSha256'] = self.payload_hash()
                self.write_payload()
                with self.assertRaises(ValueError): self.apply()
                self.assert_unchanged()
                self.assertFalse(policy.tea004_recovery_sidecar(self.repo, self.record).exists())
        self.payload, self.review = copy.deepcopy(originals)
        self.review['reviewer'] = 'lead'
        self.write_payload()
        with self.assertRaises(ValueError): self.apply()
        self.assert_unchanged()

    def test_rejects_missing_duplicate_wrong_or_expired_live_claim(self):
        row = self.live[0]
        for live in ([], [row, row], [dict(row, holder='other')],
                     [dict(row, holder_did='did:key:zDifferent')],
                     [dict(row, lease_end='2000-01-01T00:00:00+00:00')]):
            with self.subTest(live=live):
                self.live = live
                with self.assertRaises(ValueError): self.apply()
                self.assert_unchanged()
                self.assertFalse(policy.tea004_recovery_sidecar(self.repo, self.record).exists())

    def test_rejects_cache_symlink_and_mutation_after_review(self):
        self.f.write(CACHES[1], 'different from reviewed snapshot')
        with self.assertRaises(ValueError): self.apply()
        self.assert_unchanged()
        p = self.repo / CACHES[1]
        p.unlink()
        p.symlink_to(self.repo / TOOL)
        with self.assertRaises(ValueError): self.apply()
        self.assert_unchanged()

    def test_rejects_archive_or_census_mutation(self):
        self.archive.write_bytes(self.archive.read_bytes() + b'unreviewed change')
        with self.assertRaises(ValueError): self.apply()
        self.assert_unchanged()
        self.assertFalse(policy.tea004_recovery_sidecar(self.repo, self.record).exists())

    def test_rechecks_current_state_after_live_claim(self):
        def drift(*args):
            self.f.write(TOOL, 'changed while live claim was checked')
            return self.live
        args = SimpleNamespace(transition_file=PREFIX + 'batch.json')
        with mock.patch.object(policy, 'support_live_claims', side_effect=drift):
            with self.assertRaises(ValueError):
                policy.reconcile_tea004_recovery(self.repo, self.record, self.reqs, self.state, args)
        self.assert_unchanged()
        self.assertFalse(policy.tea004_recovery_sidecar(self.repo, self.record).exists())

    def test_rejects_sidecar_tampering(self):
        self.apply()
        sidecar = policy.tea004_recovery_sidecar(self.repo, self.record)
        data = json.loads(sidecar.read_text())
        data['events'][0]['toSha256'] = '0' * 64
        sidecar.write_text(json.dumps(data))
        self.assertTrue(policy.protected_reconciliations(self.repo, self.record)[1])
        self.assert_unchanged()

    def test_rejects_cache_member_in_pinned_archive(self):
        with tarfile.open(self.archive, 'w:gz') as archive:
            member = tarfile.TarInfo(self.record_path)
            member.size = len(self.original)
            archive.addfile(member, io.BytesIO(self.original))
            member = tarfile.TarInfo(CACHES[0])
            member.size = 1
            archive.addfile(member, io.BytesIO(b'x'))
        archive_sha = fixtures.digest(self.archive)
        self.payload['archiveSha256'] = archive_sha
        self.review['payloadSha256'] = self.payload_hash()
        self.write_payload()
        with mock.patch.object(policy, 'TEA004_RECOVERY_ARCHIVE_SHA256', archive_sha):
            with self.assertRaises(ValueError): self.apply()
        self.assert_unchanged()
        self.assertFalse(policy.tea004_recovery_sidecar(self.repo, self.record).exists())

    def test_rejects_evidence_mutation_during_claim_probe(self):
        def tamper(*args):
            self.proof.write_bytes(self.proof.read_bytes() + b' ')
            return self.live
        args = SimpleNamespace(transition_file=PREFIX + 'batch.json')
        with mock.patch.object(policy, 'support_live_claims', side_effect=tamper):
            with self.assertRaises(ValueError):
                policy.reconcile_tea004_recovery(self.repo, self.record, self.reqs, self.state, args)
        self.assert_unchanged()
        self.assertFalse(policy.tea004_recovery_sidecar(self.repo, self.record).exists())

    def test_rejects_stale_census_even_with_refreshed_payload_hash(self):
        census = json.loads(self.census.read_text())
        census['participantIndexSha256'] = '0' * 64
        self.f.write(self.census_path, census)
        self.payload['ownerCensusSnapshotSha256'] = fixtures.digest(self.census)
        self.review['payloadSha256'] = self.payload_hash()
        self.write_payload()
        with self.assertRaises(ValueError): self.apply()
        self.assert_unchanged()
        self.assertFalse(policy.tea004_recovery_sidecar(self.repo, self.record).exists())

    def test_recovery_never_allows_staging_protected_tool_or_cache(self):
        self.apply()
        self.f.run_git('add', '--', TOOL, CACHES[1])
        packet = policy.review(self.repo, self.record, self.reqs, self.state, [TOOL, CACHES[1]])
        for name in (TOOL, CACHES[1]):
            self.assertIn('Staged protected foreign path: ' + name, packet['errors'])
        self.assert_unchanged()

    def test_recreated_absent_cache_is_drift_and_cannot_be_staged(self):
        self.apply()
        self.f.write(CACHES[0], 'recreated unreviewed generated bytes')
        self.assertTrue(policy.protected_reconciliations(self.repo, self.record)[1])
        self.f.run_git('add', '--', CACHES[0])
        packet = policy.review(self.repo, self.record, self.reqs, self.state, [CACHES[0]])
        self.assertIn('Staged protected foreign path: ' + CACHES[0], packet['errors'])
        self.assert_unchanged()

    def test_rejects_archive_noncanonical_cache_alias(self):
        with tarfile.open(self.archive, 'w:gz') as archive:
            member = tarfile.TarInfo(self.record_path)
            member.size = len(self.original)
            archive.addfile(member, io.BytesIO(self.original))
            member = tarfile.TarInfo('./' + CACHES[0])
            member.size = 1
            archive.addfile(member, io.BytesIO(b'x'))
        archive_sha = fixtures.digest(self.archive)
        self.payload['archiveSha256'] = archive_sha
        self.review['payloadSha256'] = self.payload_hash()
        self.write_payload()
        with mock.patch.object(policy, 'TEA004_RECOVERY_ARCHIVE_SHA256', archive_sha):
            with self.assertRaises(ValueError): self.apply()
        self.assert_unchanged()
        self.assertFalse(policy.tea004_recovery_sidecar(self.repo, self.record).exists())
