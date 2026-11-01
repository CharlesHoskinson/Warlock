"""Foreign provenance is reviewed atomically, never source ownership or progress."""
import importlib.util
import hashlib
import json
import unittest
from unittest import mock

import test_warlock as fixtures

spec = importlib.util.spec_from_file_location('foreign_policy', fixtures.CHECKER)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo = self.fixture.repo
        self.cli = self.fixture.cli
        self.names = ['implementation/warlock/qa/foreign_model.qnt',
                      'implementation/warlock/qa/foreign_model_test.qnt']
        for name in self.names:
            self.fixture.write(name, 'original foreign work')
        self.adoption_name = 'implementation/warlock/src/LaterOwned.elm'
        self.fixture.write(self.adoption_name, 'separately owned dependency at capture')
        self.fixture.start()
        self.record_path = '.warlock-contributor/slice.json'
        self.record_file = self.repo / self.record_path
        self.original = self.record_file.read_bytes()
        self.record = json.loads(self.original)
        self.identity = policy.record_identity(self.record, self.record_path)
        self.sidecar = policy.reconciliation_path(self.repo, dict(self.record, _recordPath=self.record_path))
        self.counter = 0
        self.owner_records = {}

    def transition(self, name, reviewer='independent-reviewer', previous=None):
        self.counter += 1
        current = fixtures.digest(self.repo / name)
        source_record_path = self.owner_records.get(name)
        if source_record_path is None:
            source_record_path = '.warlock-contributor/model-owner-%d.json' % self.counter
            self.owner_records[name] = source_record_path
            source_record = {
                'schema': 1, 'owner': 'separate-model-owner',
                'slice': {'id': 'foreign-model', 'requirements': ['ELM-ARC-012'],
                          'scenarios': ['cancel-before-commit'], 'paths': [name]},
                'baseline': self.record['baseline'], 'startedUTC': '2026-01-01T00:00:00+00:00',
                'sourceHashes': {name: current}, 'foreignDirty': {},
                'adoptedDirty': {'paths': []}, 'iterations': []}
        else:
            source_record = json.loads((self.repo/source_record_path).read_text())
            source_record['sourceHashes'][name] = current
        self.fixture.write(source_record_path, source_record)
        index_path = self.repo/'.warlock-contributor/participant-index.json'
        index = json.loads(index_path.read_text())
        index['records'][source_record_path] = policy.participant_entry(
            source_record, fixtures.digest(self.repo/source_record_path))
        payload = {'schema': 1, 'records': dict(sorted(index['records'].items()))}
        index = dict(payload, indexSha256=policy.json_sha256(payload))
        self.fixture.write('.warlock-contributor/participant-index.json', index)
        snap = '.warlock-contributor/evidence/foreign-reconciliation-snapshots/owner-%d.json' % self.counter
        self.fixture.write(snap, source_record)
        review = '.warlock-contributor/evidence/foreign-reconciliations/review-%d.json' % self.counter
        reason = 'Preserve the separate model owner and reconcile reviewed bytes'
        self.fixture.write(review, dict(schema=1, scope='foreign-provenance-only', scenarioAcceptance=False,
            recordIdentitySha256=self.identity, recordPath=self.record_path, path=name,
            previousSha256=previous or self.record['foreignDirty'].get(name), currentSha256=current,
            sourceRecordSnapshot=snap, sourceRecordSnapshotSha256=fixtures.digest(self.repo / snap),
            sourceOwner='separate-model-owner', sourceRecordPath=source_record_path,
            ownerCensusSnapshot='pending', ownerCensusSnapshotSha256='pending',
            reason=reason, reviewer=reviewer, independent=True))
        return dict(path=name, sourceRecordPath=source_record_path, ownerCensusSnapshot='pending',
                    sourceRecordSnapshot=snap, reviewFile=review, reason=reason)

    def prepare_transitions(self, transitions):
        if not transitions or any(not isinstance(entry, dict) or 'sourceRecordPath' not in entry
                                  for entry in transitions):
            return transitions
        census = json.loads(self.cli('--record', self.record_path, 'owner-census').stdout)
        census_path = census['ownerCensusSnapshot']
        for entry in transitions:
            if not isinstance(entry, dict) or 'reviewFile' not in entry:
                continue
            entry['ownerCensusSnapshot'] = census_path
            review = json.loads((self.repo/entry['reviewFile']).read_text())
            review['ownerCensusSnapshot'] = census_path
            review['ownerCensusSnapshotSha256'] = census['ownerCensusSnapshotSha256']
            self.fixture.write(entry['reviewFile'], review)
        return transitions

    def reconcile(self, transitions, ok=True):
        self.prepare_transitions(transitions)
        self.fixture.write('.warlock-contributor/transitions.json', transitions)
        return self.cli('reconcile-foreign', '--transition-file', '.warlock-contributor/transitions.json', ok=ok)

    def change(self, names=None, text='owner updated model'):
        for name in self.names if names is None else names:
            self.fixture.write(name, text)

    def test_atomic_two_paths_preserves_record_files_index_and_progress(self):
        self.change()
        self.cli('check', ok=False)
        sources = {name: (self.repo/name).read_bytes() for name in self.names}
        index = self.fixture.run_git('write-tree')
        packet = json.loads(self.reconcile([self.transition(n) for n in self.names]).stdout)
        self.assertFalse(packet['scenarioAcceptanceInferred'])
        self.assertEqual(self.original, self.record_file.read_bytes())
        self.assertEqual(index, self.fixture.run_git('write-tree'))
        for name, value in sources.items():
            self.assertEqual(value, (self.repo/name).read_bytes())
        self.cli('check')
        resumed = json.loads(self.cli('handoff').stdout)
        self.assertEqual(resumed['protectedForeignPaths'], sorted(self.record['foreignDirty']))
        self.assertEqual(json.loads(self.record_file.read_text())['iterations'], [])
        self.fixture.run_git('add', self.names[0])
        self.assertIn('Staged protected foreign path', self.cli('review', ok=False).stdout)

    def test_reconciliation_keeps_exact_index_digest_for_noncanonical_record_bytes(self):
        # Keep semantically valid whitespace while pinning the exact stored bytes.
        record_bytes = json.dumps(self.record, indent=4, sort_keys=True).encode() + b'\n'
        self.record_file.write_bytes(record_bytes)
        index_path = self.repo/'.warlock-contributor/participant-index.json'
        index = json.loads(index_path.read_text())
        index['records'][self.record_path]['recordSha256'] = hashlib.sha256(record_bytes).hexdigest()
        payload = {'schema': index['schema'], 'records': index['records']}
        index['indexSha256'] = policy.json_sha256(payload)
        index_path.write_text(json.dumps(index, indent=2)+'\n')
        self.change([self.names[0]])
        transitions = self.prepare_transitions([self.transition(self.names[0])])
        before_index = index_path.read_bytes()
        self.reconcile(transitions)
        self.assertEqual(record_bytes, self.record_file.read_bytes())
        self.assertEqual(before_index, index_path.read_bytes())
        self.cli('check')

    def test_second_transition_keeps_old_chain_and_accepts_latest_only(self):
        self.change([self.names[0]])
        self.reconcile([self.transition(self.names[0])])
        first = json.loads(self.sidecar.read_text())['events'][0]
        old = fixtures.digest(self.repo/self.names[0])
        self.change([self.names[0]], 'second reviewed model')
        self.cli('check', ok=False)
        self.reconcile([self.transition(self.names[0], previous=old)])
        events = json.loads(self.sidecar.read_text())['events']
        self.assertEqual(events[0], first)
        self.assertEqual(events[1]['previousEventSha256'], first['eventSha256'])
        self.cli('check')
        self.change([self.names[0]], 'unreviewed third model')
        self.cli('check', ok=False)
        self.assertEqual(self.original, self.record_file.read_bytes())

    def test_replay_rejects_forged_noop_transition(self):
        self.change([self.names[0]])
        self.reconcile([self.transition(self.names[0])])
        data = json.loads(self.sidecar.read_text())
        first = data['events'][0]
        review_path = '.warlock-contributor/evidence/foreign-reconciliations/review-noop.json'
        review = json.loads((self.repo/first['reviewFile']).read_text())
        review['previousSha256'] = first['toSha256']
        review['currentSha256'] = first['toSha256']
        self.fixture.write(review_path, review)
        no_op = dict(first, fromSha256=first['toSha256'],
                     previousEventSha256=first['eventSha256'], reviewFile=review_path,
                     reviewFileSha256=fixtures.digest(self.repo/review_path))
        no_op['eventSha256'] = policy.json_sha256(
            {key: value for key, value in no_op.items() if key != 'eventSha256'})
        data['events'].append(no_op)
        self.fixture.write(str(self.sidecar.relative_to(self.repo)), data)
        output = self.cli('check', ok=False)
        self.assertIn('changed source hash', output.stdout)

    def test_owner_census_refuses_unclassified_scratch_json(self):
        malformed = self.repo/'.warlock-contributor/unclassified-participant.json'
        malformed.write_text('{broken json')
        output = self.cli('owner-census', ok=False)
        self.assertIn('unclassified JSON paths', output.stdout)

    def test_partial_batch_or_unrelated_drift_writes_nothing(self):
        self.change()
        self.reconcile([self.transition(self.names[0])], ok=False)
        self.assertFalse(self.sidecar.exists())
        entries = [self.transition(n) for n in self.names]
        self.fixture.write('implementation/warlock/src/Unrelated.elm', 'unowned change')
        self.reconcile(entries, ok=False)
        self.assertFalse(self.sidecar.exists())

    def test_bad_review_and_snapshot_fail_atomically(self):
        self.change()
        for field, value in [('independent', False), ('reviewer', 'separate-model-owner'),
                             ('reviewer', 'fresh-contributor'), ('recordIdentitySha256', '0'*64),
                             ('currentSha256', '0'*64), ('scenarioAcceptance', True)]:
            with self.subTest(field=field, value=value):
                entries = [self.transition(n) for n in self.names]
                review = self.repo/entries[-1]['reviewFile']
                data = json.loads(review.read_text()); data[field] = value
                self.fixture.write(entries[-1]['reviewFile'], data)
                self.reconcile(entries, ok=False)
                self.assertFalse(self.sidecar.exists())
        entries = [self.transition(n) for n in self.names]
        snapshot = self.repo/entries[0]['sourceRecordSnapshot']
        data = json.loads(snapshot.read_text()); data['sourceHashes'] = {}
        self.fixture.write(entries[0]['sourceRecordSnapshot'], data)
        self.reconcile(entries, ok=False)
        self.assertFalse(self.sidecar.exists())

    def test_selected_new_unsafe_and_nonregular_paths_refused(self):
        for name in ['implementation/warlock/src/Desktop.elm',
                     'implementation/warlock/src/New.elm', '../escape']:
            with self.subTest(name=name):
                self.reconcile([dict(path=name, sourceRecordSnapshot='unused', reviewFile='unused', reason='review')], ok=False)
        self.change([self.names[0]])
        entry = self.transition(self.names[0])
        (self.repo/self.names[0]).unlink()
        (self.repo/self.names[0]).symlink_to(self.repo/self.names[1])
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())

    def test_corrupt_chain_or_evidence_fails_closed(self):
        self.change([self.names[0]])
        entry = self.transition(self.names[0])
        self.reconcile([entry])
        clean = self.sidecar.read_bytes()
        value = json.loads(clean); value['events'][0]['toSha256'] = '0'*64
        self.fixture.write(str(self.sidecar.relative_to(self.repo)), value)
        self.cli('check', ok=False)
        self.sidecar.write_bytes(clean)
        self.fixture.write(entry['reviewFile'], {'tampered': True})
        self.cli('check', ok=False)

    def test_record_and_clean_extension_keep_sidecar_identity(self):
        self.change([self.names[0]])
        self.reconcile([self.transition(self.names[0])])
        sidecar_before = self.sidecar.read_bytes()
        self.cli('record', '--outcome', 'qualification', '--summary', 'No original observation')
        self.cli('extend', '--path', 'src/NewCleanDependency.elm', '--reason', 'Same behavior dependency')
        after = json.loads(self.record_file.read_text())
        for key in ('foreignDirty', 'startedUTC', 'owner', 'sourceRevision', 'sourceHashes'):
            self.assertEqual(after[key], self.record[key])
        self.assertFalse(after['iterations'][0]['meaningfulProgress'])
        self.assertEqual(sidecar_before, self.sidecar.read_bytes())
        self.cli('check')

    def test_duplicate_batch_and_unowned_snapshot_refused(self):
        self.change([self.names[0]])
        entry = self.transition(self.names[0])
        self.reconcile([entry, entry], ok=False)
        snapshot = self.repo/entry['sourceRecordSnapshot']
        data = json.loads(snapshot.read_text()); data['foreignDirty'] = {self.names[0]: None}
        self.fixture.write(entry['sourceRecordSnapshot'], data)
        # Even a freshly matching review hash cannot make a foreign snapshot an owner.
        review = json.loads((self.repo/entry['reviewFile']).read_text())
        review['sourceRecordSnapshotSha256'] = fixtures.digest(snapshot)
        self.fixture.write(entry['reviewFile'], review)
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())

    def test_event_census_must_be_intact_and_bind_unique_nonself_owner(self):
        self.change([self.names[0]])
        entry = self.prepare_transitions([self.transition(self.names[0])])[0]
        census_path = self.repo/entry['ownerCensusSnapshot']
        census_bytes = census_path.read_bytes()
        census = json.loads(census_bytes)
        census['participantIndexSha256'] = '0' * 64
        self.fixture.write(entry['ownerCensusSnapshot'], census)
        self.fixture.write('.warlock-contributor/transitions.json', [entry])
        self.cli('reconcile-foreign', '--transition-file', '.warlock-contributor/transitions.json', ok=False)
        self.assertFalse(self.sidecar.exists())
        census_path.write_bytes(census_bytes)

        entry = self.transition(self.names[0])
        source_record_path = entry['sourceRecordPath']
        source_record = json.loads((self.repo/source_record_path).read_text())
        duplicate = dict(source_record, owner='second-model-owner',
                         startedUTC='2026-01-01T00:00:01+00:00')
        duplicate_path = '.warlock-contributor/model-owner-duplicate.json'
        self.fixture.write(duplicate_path, duplicate)
        index_path = self.repo/'.warlock-contributor/participant-index.json'
        index = json.loads(index_path.read_text())
        index['records'][duplicate_path] = policy.participant_entry(
            duplicate, fixtures.digest(self.repo/duplicate_path))
        payload = {'schema': 1, 'records': dict(sorted(index['records'].items()))}
        self.fixture.write('.warlock-contributor/participant-index.json',
                           dict(payload, indexSha256=policy.json_sha256(payload)))
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())

    def test_source_owner_cannot_alias_target_owner(self):
        self.change([self.names[0]])
        entry = self.transition(self.names[0])
        source_record_path = entry['sourceRecordPath']
        source_record = json.loads((self.repo/source_record_path).read_text())
        source_record['owner'] = self.record['owner']
        self.fixture.write(source_record_path, source_record)
        self.fixture.write(entry['sourceRecordSnapshot'], source_record)
        index_path = self.repo/'.warlock-contributor/participant-index.json'
        index = json.loads(index_path.read_text())
        index['records'][source_record_path] = policy.participant_entry(
            source_record, fixtures.digest(self.repo/source_record_path))
        payload = {'schema': 1, 'records': dict(sorted(index['records'].items()))}
        self.fixture.write('.warlock-contributor/participant-index.json',
                           dict(payload, indexSha256=policy.json_sha256(payload)))
        review = json.loads((self.repo/entry['reviewFile']).read_text())
        review['sourceOwner'] = self.record['owner']
        review['sourceRecordSnapshotSha256'] = fixtures.digest(self.repo/entry['sourceRecordSnapshot'])
        self.fixture.write(entry['reviewFile'], review)
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())

    def test_legacy_event_cannot_follow_schema2_and_boolean_version_is_invalid(self):
        self.change([self.names[0]])
        self.reconcile([self.transition(self.names[0])])
        clean = self.sidecar.read_bytes()
        data = json.loads(clean)
        first = data['events'][0]
        legacy = dict(first)
        for field in ('eventSchema', 'sourceRecordPath', 'ownerCensusSnapshot',
                      'ownerCensusSnapshotSha256', 'eventSha256'):
            legacy.pop(field, None)
        legacy['fromSha256'] = first['toSha256']
        legacy['previousEventSha256'] = first['eventSha256']
        legacy['eventSha256'] = policy.json_sha256(legacy)
        data['events'].append(legacy)
        self.fixture.write(str(self.sidecar.relative_to(self.repo)), data)
        self.cli('check', ok=False)

        data = json.loads(clean)
        data['events'][0]['eventSchema'] = True
        data['events'][0]['eventSha256'] = policy.json_sha256(
            {key: value for key, value in data['events'][0].items() if key != 'eventSha256'})
        self.fixture.write(str(self.sidecar.relative_to(self.repo)), data)
        self.cli('check', ok=False)

    def test_stale_duplicate_and_noncanonical_claimants_fail_closed(self):
        self.change([self.names[0]])
        entry = self.transition(self.names[0])
        source = json.loads((self.repo/entry['sourceRecordPath']).read_text())
        duplicate = dict(source, owner='second-model-owner',
                         startedUTC='2026-01-01T00:00:02+00:00',
                         sourceHashes={self.names[0]: 'f'*64})
        duplicate_path = '.warlock-contributor/model-owner-stale.json'
        self.fixture.write(duplicate_path, duplicate)
        index_path = self.repo/'.warlock-contributor/participant-index.json'
        index = json.loads(index_path.read_text())
        index['records'][duplicate_path] = policy.participant_entry(
            duplicate, fixtures.digest(self.repo/duplicate_path))
        payload = {'schema': 1, 'records': dict(sorted(index['records'].items()))}
        self.fixture.write('.warlock-contributor/participant-index.json',
                           dict(payload, indexSha256=policy.json_sha256(payload)))
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())

    def test_noncanonical_alias_claim_fails_closed(self):
        self.change([self.names[0]])
        entry = self.transition(self.names[0])
        source = json.loads((self.repo/entry['sourceRecordPath']).read_text())
        alternate = self.names[0].replace('/qa/', '//qa/')
        duplicate = dict(source, owner='second-model-owner',
                          startedUTC='2026-01-01T00:00:02+00:00')
        duplicate['slice']['paths'] = [alternate]
        duplicate['sourceHashes'] = {alternate: fixtures.digest(self.repo/self.names[0])}
        duplicate_path = '.warlock-contributor/model-owner-alias.json'
        self.fixture.write(duplicate_path, duplicate)
        index_path = self.repo/'.warlock-contributor/participant-index.json'
        index = json.loads(index_path.read_text())
        index['records'][duplicate_path] = policy.participant_entry(
            duplicate, fixtures.digest(self.repo/duplicate_path))
        payload = {'schema': 1, 'records': dict(sorted(index['records'].items()))}
        self.fixture.write('.warlock-contributor/participant-index.json',
                           dict(payload, indexSha256=policy.json_sha256(payload)))
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())

    def test_review_or_sidecar_symlink_is_never_followed(self):
        self.change([self.names[0]])
        entry = self.transition(self.names[0])
        review = self.repo/entry['reviewFile']
        retained = review.with_suffix('.retained')
        review.rename(retained); review.symlink_to(retained)
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())
        review.unlink(); retained.rename(review)
        self.sidecar.parent.mkdir(parents=True, exist_ok=True)
        target = self.fixture.write('.warlock-contributor/untouched.json', {'untouched': True})
        before = target.read_bytes(); self.sidecar.symlink_to(target)
        self.fixture.write('.warlock-contributor/transitions.json', [entry])
        self.cli('reconcile-foreign', '--transition-file', '.warlock-contributor/transitions.json', ok=False)
        self.assertEqual(before, target.read_bytes())

    def test_unrelated_dirty_adoption_keeps_reconciliation_and_custody_checks(self):
        self.change([self.names[0]])
        self.reconcile([self.transition(self.names[0])])
        sidecar_before = self.sidecar.read_bytes()
        self.cli('extend', '--path', self.adoption_name, '--adopt-dirty', self.adoption_name,
                 '--ownership-note', 'Explicit later ownership transfer', '--reason', 'Same behavior dependency')
        after = json.loads(self.record_file.read_text())
        self.assertNotIn(self.adoption_name, after['foreignDirty'])
        self.assertEqual(after['startedUTC'], self.record['startedUTC'])
        self.assertEqual(after['iterations'], self.record['iterations'])
        self.assertEqual(self.sidecar.read_bytes(), sidecar_before)
        self.cli('check')
        self.cli('handoff')
        # A custody edit without an extension must not be hidden by stable routing.
        after['foreignDirty'].pop(self.names[1])
        self.fixture.write(self.record_path, after)
        self.assertIn('custody', self.cli('check', ok=False).stdout.lower())

    def test_stale_owner_history_does_not_authorize_current_transition(self):
        self.change([self.names[0]])
        entry = self.transition(self.names[0])
        snap = self.repo/entry['sourceRecordSnapshot']
        data = json.loads(snap.read_text())
        data['iterations'] = [{'sourceHashes': {self.names[0]: 'f'*64}}]
        self.fixture.write(entry['sourceRecordSnapshot'], data)
        review = json.loads((self.repo/entry['reviewFile']).read_text())
        review['sourceRecordSnapshotSha256'] = fixtures.digest(snap)
        self.fixture.write(entry['reviewFile'], review)
        self.reconcile([entry], ok=False)
        self.assertFalse(self.sidecar.exists())

    def test_previously_reconciled_adoption_retains_history_not_foreign_overlay(self):
        self.change([self.names[0]])
        self.reconcile([self.transition(self.names[0])])
        before = self.sidecar.read_bytes()
        self.cli('extend', '--path', self.names[0], '--adopt-dirty', self.names[0],
                 '--ownership-note', 'Explicit model dependency transfer', '--reason', 'Same behavior dependency')
        self.assertEqual(self.sidecar.read_bytes(), before)
        self.change([self.names[0]], 'now an explicitly owned change')
        self.cli('check')
        self.assertNotIn(self.names[0], json.loads(self.record_file.read_text())['foreignDirty'])

    def test_later_foreign_review_after_adoption_uses_retained_full_identity(self):
        self.change([self.names[0]])
        self.reconcile([self.transition(self.names[0])])
        self.cli('extend', '--path', self.adoption_name, '--adopt-dirty', self.adoption_name,
                 '--ownership-note', 'Explicit dependency transfer', '--reason', 'Same behavior dependency')
        previous = fixtures.digest(self.repo/self.names[0])
        self.change([self.names[0]], 'later separately reviewed source')
        packet = json.loads(self.cli('handoff', ok=False).stdout)
        self.assertEqual(packet['recordIdentitySha256'], self.identity)
        self.reconcile([self.transition(self.names[0], previous=previous)])
        self.cli('check')

    def test_latest_owner_binding_orders_extensions_and_ignores_old_claims(self):
        name = self.names[0]
        owner = {'sourceHashes': {name: 'base'},
                 'pathExtensions': [{'afterIteration': 0, 'sourceHashes': {name: 'extension-before'}},
                                    {'afterIteration': 1, 'sourceHashes': {name: 'extension-after'}}],
                 'iterations': [{'sourceHashes': {name: 'iteration'},
                                 'claims': [{'sourceHashes': {name: 'historical-claim'}}]}]}
        self.assertEqual(policy.latest_recorded_source_hash(owner, name), 'extension-after')
        owner['iterations'].append({'sourceHashes': {name: None}})
        self.assertIsNone(policy.latest_recorded_source_hash(owner, name))

    def test_transition_file_must_be_ignored_and_untracked(self):
        self.change([self.names[0]])
        entries = [self.transition(self.names[0])]
        for name in ['transitions.json', '.warlock-contributor/tracked-transitions.json']:
            self.fixture.write(name, entries)
            if 'tracked-' in name:
                self.fixture.run_git('add', '-f', name)
            output = self.cli('reconcile-foreign', '--transition-file', name, ok=False)
            self.assertIn('ignored scratch', output.stdout)
            self.assertFalse(self.sidecar.exists())

    def test_selected_overlap_is_rejected_even_when_captured_as_foreign(self):
        name = 'implementation/warlock/src/Desktop.elm'
        self.fixture.write(name, 'owner selected source already dirty at start')
        record_path = '.warlock-contributor/selected-overlap.json'
        self.cli('--record', record_path, 'start', '--owner', 'selected-source-owner')
        record = json.loads((self.repo/record_path).read_text())
        self.assertIn(name, record['foreignDirty'])
        self.fixture.write('.warlock-contributor/transitions.json',
                           [dict(path=name, sourceRecordPath='unused', ownerCensusSnapshot='unused',
                                 sourceRecordSnapshot='unused', reviewFile='unused', reason='review')])
        output = self.cli('--record', record_path, 'reconcile-foreign',
                          '--transition-file', '.warlock-contributor/transitions.json', ok=False)
        self.assertIn('selected or adopted', output.stdout)

    def test_declared_dirty_foreign_source_can_be_explicitly_adopted_without_extension(self):
        name = 'implementation/warlock/src/Desktop.elm'
        self.fixture.write(name, 'known selected dirty source')
        record_path = '.warlock-contributor/selected-adoption.json'
        self.cli('--record', record_path, 'start', '--owner', 'selected-source-owner')
        before = json.loads((self.repo/record_path).read_text())
        self.assertIn(name, before['foreignDirty'])
        self.cli('--record', record_path, 'extend', '--path', name, '--adopt-dirty', name,
                 '--ownership-note', 'Explicit ownership of this already declared source',
                 '--reason', 'Same selected source, no dependency expansion')
        after = json.loads((self.repo/record_path).read_text())
        self.assertIn(name, after['adoptedDirty']['paths'])
        self.assertNotIn(name, after['foreignDirty'])
        for key in ['startedUTC', 'iterations', 'sourceHashes', 'slice']:
            self.assertEqual(before[key], after[key])
        self.cli('--record', record_path, 'check')

    def test_read_refuses_parent_symlink_swapped_after_safe(self):
        parent = self.repo/'read-parent'; parent.mkdir()
        (parent/'value.json').write_text('{"inside":true}')
        outside = self.repo/'outside-read'; outside.mkdir()
        (outside/'value.json').write_text('{"outside":true}')
        checked = policy.safe(self.repo, 'read-parent/value.json')
        parent.rename(self.repo/'read-parent-original'); parent.symlink_to(outside)
        with self.assertRaises((OSError, ValueError)):
            policy.read(checked)

    def test_atomic_replace_uses_held_parent_after_concurrent_symlink_swap(self):
        parent = self.repo/'write-parent'; parent.mkdir()
        target = parent/'sidecar.json'; target.write_text('{"old":true}')
        outside = self.repo/'outside-write'; outside.mkdir()
        foreign = outside/'sidecar.json'; foreign.write_text('must remain untouched')
        replace = policy.os.replace
        def swap(src, dst, **kwargs):
            self.assertIn('src_dir_fd', kwargs)
            self.assertIn('dst_dir_fd', kwargs)
            parent.rename(self.repo/'write-parent-original'); parent.symlink_to(outside)
            return replace(src, dst, **kwargs)
        with mock.patch.object(policy.os, 'replace', side_effect=swap):
            policy.write_record(target, {'owned': True})
        self.assertEqual(foreign.read_text(), 'must remain untouched')
        self.assertEqual(json.loads((self.repo/'write-parent-original/sidecar.json').read_text()), {'owned': True})

    def test_reconciliation_holds_sidecar_directory_across_validation_and_commit(self):
        self.change([self.names[0]])
        entry = self.prepare_transitions([self.transition(self.names[0])])[0]
        self.fixture.write('.warlock-contributor/transitions.json', [entry])
        record = dict(self.record, _recordPath=self.record_path)
        reqs, state = policy.context(self.repo)
        parent = self.sidecar.parent
        outside = self.repo/'outside-sidecar'; outside.mkdir()
        foreign = outside/self.sidecar.name; foreign.write_text('outside remains untouched')
        real_write = policy.write_record
        moved = self.repo/'.warlock-contributor/pinned-sidecar-directory'
        def swap(path, value, **kwargs):
            self.assertIsNotNone(kwargs.get('parent_fd'))
            parent.rename(moved); parent.symlink_to(outside)
            return real_write(path, value, **kwargs)
        args = type('Arguments', (), {'transition_file': '.warlock-contributor/transitions.json'})()
        with mock.patch.object(policy, 'write_record', side_effect=swap):
            packet = policy.reconcile_foreign(self.repo, record, reqs, state, args)
        self.assertEqual(foreign.read_text(), 'outside remains untouched')
        self.assertEqual(fixtures.digest(moved/self.sidecar.name), packet['sidecarSha256'])
        self.cli('check', ok=False)  # Namespace now redirects: no false current admission.

    def test_already_declared_adoption_cannot_hide_changed_foreign_bytes(self):
        name = 'implementation/warlock/src/Desktop.elm'
        self.fixture.write(name, 'selected source captured dirty')
        record_path = '.warlock-contributor/selected-changed.json'
        self.cli('--record', record_path, 'start', '--owner', 'selected-source-owner')
        before = (self.repo/record_path).read_bytes()
        self.fixture.write(name, 'unexplained subsequent source change')
        self.cli('--record', record_path, 'extend', '--path', name, '--adopt-dirty', name,
                 '--ownership-note', 'Cannot override drift', '--reason', 'Same source', ok=False)
        self.assertEqual(before, (self.repo/record_path).read_bytes())

    def test_declared_readme_extension_binding_can_receive_explicit_ownership_assertion(self):
        name = 'implementation/warlock/haskell/native-authority/README.md'
        self.fixture.write(name, 'current separately recorded README bytes')
        self.cli('extend', '--path', name, '--adopt-dirty', name,
                 '--ownership-note', 'Original dependency extension', '--reason', 'Same source work')
        before = json.loads(self.record_file.read_text())
        self.assertIn(name, before['slice']['paths'])
        self.assertNotIn(name, before['foreignDirty'])
        self.assertEqual(before['adoptedDirty']['paths'], [])
        self.assertEqual(before['pathExtensions'][-1]['sourceHashes'][name], fixtures.digest(self.repo/name))
        self.cli('extend', '--path', name, '--adopt-dirty', name,
                 '--ownership-note', 'Assert exact current README ownership', '--reason', 'Explicit selected path ownership')
        after = json.loads(self.record_file.read_text())
        self.assertIn(name, after['adoptedDirty']['paths'])
        for key in ['slice', 'sourceHashes', 'foreignDirty', 'startedUTC', 'iterations', 'pathExtensions']:
            self.assertEqual(before[key], after[key])
        self.cli('check')

    def test_declared_readme_assertion_refuses_bytes_not_in_latest_own_binding(self):
        name = 'implementation/warlock/haskell/native-authority/README.md'
        self.fixture.write(name, 'captured README')
        self.cli('extend', '--path', name, '--adopt-dirty', name,
                 '--ownership-note', 'Original dependency extension', '--reason', 'Same work')
        before = self.record_file.read_bytes()
        self.fixture.write(name, 'unrecorded newer README')
        self.cli('extend', '--path', name, '--adopt-dirty', name,
                 '--ownership-note', 'Cannot silently adopt unrecorded bytes', '--reason', 'Exact source only', ok=False)
        self.assertEqual(before, self.record_file.read_bytes())

    def test_custom_record_routes_same_sidecar_across_commands(self):
        new_path = '.warlock-contributor/custom.json'
        self.record_file.rename(self.repo/new_path)
        self.record_path = new_path
        self.record_file = self.repo/new_path
        self.identity = policy.record_identity(self.record, new_path)
        self.cli('--record', new_path, 'index-participants')
        self.change([self.names[0]])
        transitions = self.prepare_transitions([self.transition(self.names[0])])
        self.fixture.write('.warlock-contributor/transitions.json', transitions)
        self.cli('--record', new_path, 'reconcile-foreign', '--transition-file', '.warlock-contributor/transitions.json')
        self.cli('--record', new_path, 'check')
        self.cli('--record', new_path, 'handoff')
        self.assertEqual(self.original, self.record_file.read_bytes())


if __name__ == '__main__':
    unittest.main()
