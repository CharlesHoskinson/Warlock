"""Same-owner SUPPORT custody, separate from foreign ownership or progress.

Network-free tests exercise real temporary Git repos, actual validation and
sidecar writes. Only the external live authenticated-CLI observation is mocked.
Root executes these after reviewing/applying the patch; no worker execution.
"""
import copy
import datetime as dt
import hashlib
import importlib.util
import json
from types import SimpleNamespace
import unittest
from unittest import mock

import test_warlock as fixtures

spec = importlib.util.spec_from_file_location('support_policy', fixtures.CHECKER)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class SupportCustodyTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        self.names = sorted(policy.SUPPORT_CUSTODY_PATHS)
        # Real canonical support docs are tracked before their owner changes
        # them. The base fixture only tracks STATE; untracked docs elsewhere
        # are intentionally outside dirty_names' product/plugin census.
        support_baseline = [name for name in self.names if name != policy.STATE]
        for name in support_baseline:
            self.fixture.write(name, 'tracked support baseline\n')
        self.fixture.run_git('add', '--', *support_baseline)
        self.fixture.run_git('commit', '-qm', 'track canonical support fixture')
        state = json.loads((self.repo / policy.STATE).read_text())
        state['supportNote'] = 'captured owner work'
        self.fixture.write(policy.STATE, state)
        for name in self.names:
            if name != policy.STATE:
                self.fixture.write(name, 'captured owner work\n')
        self.fixture.write('implementation/warlock/src/Unowned.elm', 'captured genuine foreign draft\n')
        self.fixture.start()
        self.path = '.warlock-contributor/slice.json'
        self.original = (self.repo / self.path).read_bytes()
        self.record = json.loads(self.original)
        self.record['_recordPath'] = self.path
        self.counter = 0
        self.live = []
        for name in self.names:
            if name == policy.STATE:
                state['supportNote'] = 'current canonical owner work'
                self.fixture.write(name, state)
            else:
                self.fixture.write(name, 'current canonical owner work\n')
        self.reqs, self.state = policy.context(self.repo)

    def prepare(self, names=None, reviewer='independent-reviewer', disposition='accepted'):
        self.counter += 1
        prefix = policy.SUPPORT_EVIDENCE + str(self.counter) + '-'
        snap = prefix + 'record.json'
        self.fixture.write(snap, json.loads(self.original))
        at = dt.datetime.now(dt.timezone.utc)
        self.live = [dict(resource='file:' + str(self.repo / n),
            holder=self.record['owner'], holder_did='did:key:z6Mkh123456789ABCDEFGH',
            lease_end=(at + dt.timedelta(hours=1)).isoformat(), queue=[])
            for n in (self.names if names is None else names)]
        proof = prefix + 'claim-proof.json'
        self.fixture.write(proof, dict(schema=1, owner=self.record['owner'], run='fixture-run',
            observedUTC=at.isoformat(), claims=self.live))
        existing, errors, data = policy.support_reconciliations(self.repo, self.record,
                                                               check_current=False)
        self.assertEqual(errors, [])
        identity = data['recordIdentitySha256'] if data else policy.record_identity(self.record, self.path)
        entries = []
        for index, name in enumerate(self.names if names is None else names):
            current = prefix + str(index) + '-current.bin'
            p = self.repo / current
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes((self.repo / name).read_bytes())
            review = prefix + str(index) + '-review.json'
            reason = 'Same owner canonical support update; preserve captured participant history'
            evidence = dict(recordSnapshot=snap, currentSnapshot=current, claimProof=proof)
            expected = dict(schema=1, disposition=disposition, scope='same-owner-support-provenance-only',
                scenarioAcceptance=False, independent=True, reviewer=reviewer,
                recordIdentitySha256=identity, recordPath=self.path, path=name,
                previousSha256=existing.get(name, self.record['foreignDirty'][name]),
                currentSha256=fixtures.digest(self.repo / name), sourceOwner=self.record['owner'], reason=reason,
                **evidence)
            expected.update({k + 'Sha256': fixtures.digest(self.repo / v) for k, v in evidence.items()})
            self.fixture.write(review, expected)
            entries.append(dict(path=name, reviewFile=review, reason=reason, **evidence))
        transition = prefix + 'transitions.json'
        self.fixture.write(transition, entries)
        return entries, SimpleNamespace(transition_file=transition)

    def apply(self, args):
        with mock.patch.object(policy, 'support_live_claims', return_value=self.live):
            return policy.reconcile_support(self.repo, self.record, self.reqs, self.state, args)

    def assert_unchanged(self):
        self.assertEqual((self.repo / self.path).read_bytes(), self.original)

    def test_all_four_support_transitions_preserve_record_source_timer_and_foreign_pins(self):
        _, args = self.prepare()
        packet = self.apply(args)
        self.assertTrue(packet['participantBytesUnchanged'])
        self.assert_unchanged()
        self.fixture.cli('check')
        overlay, errors, data = policy.support_reconciliations(self.repo, self.record)
        self.assertEqual(errors, [])
        self.assertEqual(set(overlay), set(self.names))
        self.assertEqual(data['custodyBaseline']['foreignDirty'], self.record['foreignDirty'])
        self.assertEqual(len(data['events']), 4)
        self.assertEqual(self.record['iterations'], [])

    def test_stale_foreign_source_drift_still_blocks_without_writing(self):
        _, args = self.prepare()
        self.fixture.write('implementation/warlock/src/Unowned.elm', 'unrelated changed worker\n')
        with self.assertRaises(ValueError):
            self.apply(args)
        self.assertFalse(policy.support_sidecar(self.repo, self.record).exists())
        self.assert_unchanged()

    def test_same_owner_reviewer_refused(self):
        _, args = self.prepare(reviewer=self.record['owner'])
        with self.assertRaises(ValueError):
            self.apply(args)
        self.assert_unchanged()

    def test_wrong_holder_missing_claim_duplicate_and_expired_live_rows_refused(self):
        _, args = self.prepare()
        good = copy.deepcopy(self.live)
        variants = [[], good + [good[0]],
                    [dict(x, holder='different-owner') for x in good],
                    [dict(x, holder_did='did:key:zDifferent') for x in good],
                    [dict(x, lease_end='2000-01-01T00:00:00+00:00') for x in good]]
        for rows in variants:
            with self.subTest(rows=rows):
                self.live = rows
                with self.assertRaises(ValueError):
                    self.apply(args)
                self.assertFalse(policy.support_sidecar(self.repo, self.record).exists())
                self.assert_unchanged()

    def test_forged_review_snapshot_and_proof_cannot_pass_exact_hashes(self):
        for key in ('recordSnapshot', 'currentSnapshot', 'claimProof', 'reviewFile'):
            entries, args = self.prepare()
            p = self.repo / entries[0][key]
            p.write_bytes(p.read_bytes() + b' changed')
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.apply(args)
            self.assertFalse(policy.support_sidecar(self.repo, self.record).exists())
            self.assert_unchanged()

    def test_any_unsupported_or_product_path_is_refused_before_cli(self):
        entries, args = self.prepare()
        rejected = ['implementation/warlock/src/Desktop.elm', 'tools/check_auth_cpu.py',
                    'tools/check_tea_cpu.py', 'docs/arbitrary.md', '../STATE.json']
        for name in rejected:
            # Path spellings only; never read forbidden support files.
            entries[0]['path'] = name
            self.fixture.write(args.transition_file, entries)
            with mock.patch.object(policy, 'support_live_claims') as live:
                with self.assertRaises(ValueError):
                    policy.reconcile_support(self.repo, self.record, self.reqs, self.state, args)
                live.assert_not_called()
            self.assert_unchanged()

    def test_partial_batch_cannot_hide_other_changed_support_paths(self):
        _, args = self.prepare([self.names[0]])
        with self.assertRaises(ValueError):
            self.apply(args)
        self.assertFalse(policy.support_sidecar(self.repo, self.record).exists())
        self.assert_unchanged()

    def test_later_drift_requires_new_review_and_keeps_old_history(self):
        _, args = self.prepare()
        self.apply(args)
        sidecar = policy.support_sidecar(self.repo, self.record)
        prior = json.loads(sidecar.read_text())
        self.fixture.write('docs/HANDOFF.md', 'later canonical owner update\n')
        self.fixture.cli('check', ok=False)
        _, later = self.prepare(['docs/HANDOFF.md'])
        self.apply(later)
        self.assertEqual(json.loads(sidecar.read_text())['events'][:4], prior['events'])
        self.fixture.cli('check')
        self.assert_unchanged()

    def test_cli_unreviewed_transition_refuses_without_writes(self):
        _, args = self.prepare()
        entries = json.loads((self.repo / args.transition_file).read_text())
        entries[0]['reason'] = 'different unreviewed reason'
        self.fixture.write(args.transition_file, entries)
        self.fixture.cli('reconcile-support', '--transition-file', args.transition_file, ok=False)
        self.assertFalse(policy.support_sidecar(self.repo, self.record).exists())
        self.assert_unchanged()

    def test_ordinary_check_is_offline_after_valid_transition(self):
        _, args = self.prepare()
        self.apply(args)
        with mock.patch.object(policy, 'support_live_claims', side_effect=AssertionError('must stay offline')):
            errors, _ = policy.validate(self.repo, self.record, self.reqs, self.state)
        self.assertEqual(errors, [])
        self.assert_unchanged()

    def test_assigned_run_required_before_cli_execution(self):
        with mock.patch.dict('os.environ', {'AGENTBUS_RUN': 'assigned'}):
            with mock.patch.object(policy.subprocess, 'run') as execute:
                with self.assertRaises(ValueError):
                    policy.support_live_claims(self.record['owner'], 'other-run')
                execute.assert_not_called()



    def test_rejected_partial_missing_review_and_bool_schema_or_flags_refused(self):
        for field, value in [('disposition', 'rejected'), ('disposition', 'partial'),
                             ('disposition', None), ('schema', True),
                             ('independent', 1), ('scenarioAcceptance', 0)]:
            entries, args = self.prepare()
            path = self.repo / entries[0]['reviewFile']
            review = json.loads(path.read_text())
            if value is None:
                del review[field]
            else:
                review[field] = value
            self.fixture.write(entries[0]['reviewFile'], review)
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.apply(args)
            self.assertFalse(policy.support_sidecar(self.repo, self.record).exists())
            self.assert_unchanged()

    def test_expired_frozen_claim_refused_despite_new_live_claim(self):
        entries, args = self.prepare()
        name = entries[0]['claimProof']
        proof = json.loads((self.repo / name).read_text())
        at = dt.datetime.now(dt.timezone.utc)
        proof['observedUTC'] = (at - dt.timedelta(hours=2)).isoformat()
        for row in proof['claims']:
            row['lease_end'] = (at - dt.timedelta(hours=1)).isoformat()
        self.fixture.write(name, proof)
        # Keep the fixture self-consistent: the independently authored review
        # binds these exact expired proof bytes; live rows remain future-valid.
        for entry in entries:
            review = json.loads((self.repo / entry['reviewFile']).read_text())
            review['claimProofSha256'] = fixtures.digest(self.repo / name)
            self.fixture.write(entry['reviewFile'], review)
        with self.assertRaises(ValueError):
            self.apply(args)
        self.assertFalse(policy.support_sidecar(self.repo, self.record).exists())
        self.assert_unchanged()

    def test_mutating_any_frozen_artifact_during_live_probe_refuses_before_cas(self):
        for key in ('recordSnapshot', 'currentSnapshot', 'claimProof', 'reviewFile'):
            entries, args = self.prepare()
            def observe(*_):
                path = self.repo / entries[0][key]
                path.write_bytes(path.read_bytes() + b'\n')
                return self.live
            with self.subTest(key=key), mock.patch.object(policy, 'support_live_claims', side_effect=observe):
                with self.assertRaises(ValueError):
                    policy.reconcile_support(self.repo, self.record, self.reqs, self.state, args)
            self.assertFalse(policy.support_sidecar(self.repo, self.record).exists())
            self.assert_unchanged()

    def test_staged_support_requires_explicit_include_and_exact_approved_current_bytes(self):
        _, args = self.prepare()
        self.apply(args)
        name = 'docs/HANDOFF.md'
        self.fixture.run_git('add', '--', name)
        self.fixture.cli('review', ok=False)
        self.fixture.cli('review', '--include', name)
        self.assert_unchanged()
        self.fixture.write(name, 'unreviewed later support bytes\n')
        self.fixture.run_git('add', '--', name)
        self.fixture.cli('review', '--include', name, ok=False)
        self.assert_unchanged()

    def test_explicit_include_never_allows_genuine_foreign_source(self):
        _, args = self.prepare()
        self.apply(args)
        name = 'implementation/warlock/src/Unowned.elm'
        self.fixture.run_git('add', '--', name)
        self.fixture.cli('review', '--include', name, ok=False)
        self.assert_unchanged()


if __name__ == '__main__':
    unittest.main()
