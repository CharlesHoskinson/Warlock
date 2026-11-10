"""Candidate regressions; Root runs these in the protected plugin test context.

Only live AgentBus observation is mocked. Reconciliation uses real temporary
Git evidence and the ordinary append-only support sidecar.
"""
import copy
import os
import unittest
from unittest import mock

import test_support_custody as support
from test_delivery_flow import DeliveryFixture

policy = support.policy


class GenericSupportActorBindingTests(unittest.TestCase):
    def setUp(self):
        self.case = support.SupportCustodyTests(
            'test_all_four_support_transitions_preserve_record_source_timer_and_foreign_pins')
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.actor = 'assigned-worker'
        self.did = 'did:key:z6Mkh123456789ABCDEFGH'

    def prepare(self, reviewer='independent-reviewer'):
        entries, args = self.case.prepare(reviewer=reviewer)
        path = self.case.repo / entries[0]['claimProof']
        proof = policy.read(path)
        proof['claimOwner'] = self.actor
        for row in proof['claims']:
            row['holder'] = self.actor
        proof['actorBinding'] = dict(schema=1, recordPath=self.case.path,
            recordIdentitySha256=policy.record_identity(self.case.record, self.case.path),
            logicalOwner=self.case.record['owner'], actor=self.actor,
            run=proof['run'], did=self.did,
            resources=sorted(row['resource'] for row in proof['claims']))
        self.case.fixture.write(entries[0]['claimProof'], proof)
        for entry in entries:
            review = policy.read(self.case.repo / entry['reviewFile'])
            review.update(claimOwner=self.actor, claimHolderDid=self.did,
                actorBindingSha256=policy.json_sha256(proof['actorBinding']),
                claimProofSha256=support.fixtures.digest(path))
            self.case.fixture.write(entry['reviewFile'], review)
        self.case.live = copy.deepcopy(proof['claims'])
        return entries, args, proof

    def apply(self, args):
        with mock.patch.dict(os.environ, AGENTBUS_AGENT=self.actor, AGENTBUS_RUN='fixture-run'):
            return self.case.apply(args)

    def test_generic_binding_keeps_record_identity_and_actual_actor(self):
        entries, args, proof = self.prepare()
        identity = policy.record_identity(self.case.record, self.case.path)
        with mock.patch.dict(os.environ, AGENTBUS_AGENT=self.actor, AGENTBUS_RUN='fixture-run'), \
                mock.patch.object(policy, 'support_live_claims', return_value=self.case.live) as live:
            result = policy.reconcile_support(self.case.repo, self.case.record,
                self.case.reqs, self.case.state, args)
        live.assert_called_once_with(self.actor, 'fixture-run')
        self.assertTrue(result['participantBytesUnchanged'])
        self.case.assert_unchanged()
        self.assertEqual(policy.record_identity(self.case.record, self.case.path), identity)
        self.assertNotEqual(self.actor, self.case.record['owner'])
        with mock.patch.object(policy, 'support_live_claims', side_effect=AssertionError('offline replay')):
            overlay, errors, data = policy.support_reconciliations(self.case.repo, self.case.record)
        self.assertEqual(errors, [])
        self.assertEqual(set(overlay), set(self.case.names))
        self.assertEqual(len(data['events']), len(entries))

    def test_forged_binding_fields_rejected(self):
        _, _, good = self.prepare()
        for field, value in [('schema', True), ('recordPath', '.warlock-contributor/other.json'),
                ('recordIdentitySha256', '0' * 64), ('logicalOwner', 'other'),
                ('actor', 'invented-alias'), ('run', 'other-run'),
                ('did', 'a' * 64), ('did', 'did:key:zOtherActor'),
                ('resources', []), ('resources', [good['claims'][0]['resource']])]:
            bad = copy.deepcopy(good)
            bad['actorBinding'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                policy.support_claim_owner(self.case.repo, self.case.record, bad)
        self.case.assert_unchanged()

    def test_missing_binding_and_extra_privileges_rejected(self):
        _, _, proof = self.prepare()
        proof.pop('actorBinding')
        with self.assertRaises(ValueError):
            policy.support_claim_owner(self.case.repo, self.case.record, proof)
        _, _, proof = self.prepare()
        proof['claims'][0]['resource'] = 'file:' + str(self.case.repo / 'plugins/warlock-contributor/scripts/warlock.py')
        proof['actorBinding']['resources'] = sorted(x['resource'] for x in proof['claims'])
        with self.assertRaises(ValueError):
            policy.support_claim_owner(self.case.repo, self.case.record, proof)

    def test_wrong_assigned_actor_or_run_rejected_before_live_probe(self):
        _, args, _ = self.prepare()
        for actor, run in [('other', 'fixture-run'), (self.actor, 'other-run'), ('', '')]:
            with mock.patch.dict(os.environ, AGENTBUS_AGENT=actor, AGENTBUS_RUN=run), \
                    mock.patch.object(policy, 'support_live_claims') as live, self.assertRaises(ValueError):
                policy.reconcile_support(self.case.repo, self.case.record, self.case.reqs, self.case.state, args)
            live.assert_not_called()
        self.case.assert_unchanged()

    def test_wrong_live_did_missing_expired_and_duplicate_claims_rejected(self):
        _, args, _ = self.prepare()
        good = copy.deepcopy(self.case.live)
        for rows in [[], good[1:], good + [good[0]],
                [dict(x, holder_did='did:key:zOtherActor') for x in good],
                [dict(x, lease_end='2000-01-01T00:00:00+00:00') for x in good]]:
            self.case.live = rows
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.apply(args)
        self.case.assert_unchanged()

    def test_frozen_missing_lease_rejected(self):
        _, _, proof = self.prepare()
        proof['claims'][0].pop('lease_end')
        with mock.patch.dict(os.environ, AGENTBUS_AGENT=self.actor, AGENTBUS_RUN='fixture-run'), \
                mock.patch.object(policy, 'support_live_claims') as live, self.assertRaises((ValueError, KeyError)):
            policy.confirm_support_claims(self.case.repo, self.case.record, proof, self.case.names)
        live.assert_not_called()

    def test_self_review_and_missing_binding_review_rejected(self):
        for reviewer in [self.actor, self.did, self.case.record['owner']]:
            _, args, _ = self.prepare(reviewer=reviewer)
            with self.subTest(reviewer=reviewer), self.assertRaises(ValueError):
                self.apply(args)
        entries, args, _ = self.prepare()
        review = policy.read(self.case.repo / entries[0]['reviewFile'])
        review.pop('actorBindingSha256')
        self.case.fixture.write(entries[0]['reviewFile'], review)
        with self.assertRaises(ValueError):
            self.apply(args)
        self.case.assert_unchanged()

    def test_exact_batch_rejects_omitted_transition_path(self):
        _, _, proof = self.prepare()
        with mock.patch.dict(os.environ, AGENTBUS_AGENT=self.actor, AGENTBUS_RUN='fixture-run'), \
                mock.patch.object(policy, 'support_live_claims') as live, self.assertRaises(ValueError):
            policy.confirm_support_claims(self.case.repo, self.case.record, proof, self.case.names[:-1])
        live.assert_not_called()

    def test_binding_replay_uses_frozen_event_participant(self):
        _, args, _ = self.prepare()
        self.apply(args)
        # Existing provenance supports later lawful ownership adoption. Exercise
        # that replay shape without rewriting the real participant fixture.
        current = copy.deepcopy(self.case.record)
        foreign = 'implementation/warlock/src/Unowned.elm'
        current['foreignDirty'].pop(foreign)
        current['slice']['paths'].append(foreign)
        current.setdefault('pathExtensions', []).append(dict(afterIteration=0,
            reason='owned dependency extension', sourceHashes={foreign: support.fixtures.digest(self.case.repo / foreign)},
            adoptedDirty={'paths': [foreign], 'ownershipNote': 'fixture owned adoption'}))
        with mock.patch.object(policy, 'support_live_claims', side_effect=AssertionError('offline replay')):
            _, errors, _ = policy.support_reconciliations(self.case.repo, current)
        self.assertEqual(errors, [])
        self.case.assert_unchanged()

    def test_later_binding_keeps_old_sidecar_prefix(self):
        _, args, _ = self.prepare()
        self.apply(args)
        sidecar = policy.support_sidecar(self.case.repo, self.case.record)
        before = policy.read(sidecar)
        for name in self.case.names:
            if name != policy.STATE:
                self.case.fixture.write(name, 'later independently reviewed support bytes\n')
        # Exact later batch excludes unchanged STATE; its old binding remains valid offline.
        old_names = self.case.names
        self.case.names = [n for n in old_names if n != policy.STATE]
        _, args, _ = self.prepare()
        self.apply(args)
        self.assertEqual(policy.read(sidecar)['events'][:len(before['events'])], before['events'])
        self.case.assert_unchanged()


class NewDeliveryOwnerTests(DeliveryFixture):
    def test_new_policy2_mismatched_actor_refused_without_record_or_index(self):
        self.fixture.env.update(AGENTBUS_AGENT='assigned-other', AGENTBUS_RUN='fixture-run')
        result = self.fixture.cli('--record', self.record_path, 'start', '--owner', 'root',
            '--workflow-policy', '2', '--delivery-plan-file', '.warlock-contributor/delivery-plan.json', ok=False)
        self.assertIn('assigned AgentBus actor', result.stdout + result.stderr)
        self.assertFalse((self.repo / self.record_path).exists())
        self.assertFalse((self.repo / '.warlock-contributor/participant-index.json').exists())

    def test_new_policy2_missing_actor_refused(self):
        self.fixture.env.pop('AGENTBUS_AGENT', None)
        self.fixture.env.pop('AGENTBUS_RUN', None)
        self.fixture.cli('--record', self.record_path, 'start', '--owner', 'root',
            '--workflow-policy', '2', '--delivery-plan-file', '.warlock-contributor/delivery-plan.json', ok=False)
        self.assertFalse((self.repo / self.record_path).exists())

    def test_matching_policy2_start_uses_explicit_fixture_assignment(self):
        self.fixture.env.update(AGENTBUS_AGENT='root', AGENTBUS_RUN='fixture-run')
        self.start_delivery()
        self.assertEqual(self.record()['owner'], 'root')
