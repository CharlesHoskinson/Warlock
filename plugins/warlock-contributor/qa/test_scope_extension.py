"""Generic policy-2 extension/reselection regressions in existing isolated fixtures.

Root executes these against baseline then candidate; no production source is edited.
"""
import copy
import datetime as dt
import json
from types import SimpleNamespace
from unittest.mock import patch

import test_warlock as fixtures
from test_delivery_flow import DeliveryFixture, engine


class ScopeExtensionSelectionTests(DeliveryFixture):
    STATE = 'docs/warlock-build-loop/v2/STATE.json'
    DEPENDENCY = 'implementation/warlock/src/AdditionalDependency.elm'

    def prepare_selected(self, dirty_dependency=False):
        # Reuse the existing fixture's source bytes; these policy tests do not
        # compile or claim acceptance for an invented production implementation.
        self.fixture.write(self.DEPENDENCY, (self.repo / self.source).read_text())
        self.fixture.run_git('add', '--', self.DEPENDENCY)
        self.fixture.run_git('commit', '-qm', 'fixture dependency before participant start')
        if dirty_dependency:
            self.fixture.write(self.DEPENDENCY, (self.repo / self.DEPENDENCY).read_text() + '\n')
        state = json.loads((self.repo / self.STATE).read_text())
        state['unrelatedFixtureField'] = 'retain exactly'
        self.fixture.write(self.STATE, state)
        self.start_delivery()
        self.assertIn(self.STATE, self.record()['foreignDirty'])

    def extend(self, path=None, adopt=False):
        args = ['--record', self.record_path, 'extend', '--path', path or self.DEPENDENCY,
                '--reason', 'same original behavior needs its declared dependency']
        if adopt:
            args += ['--adopt-dirty', path or self.DEPENDENCY,
                     '--ownership-note', 'explicit same-owner fixture dependency adoption']
        return self.fixture.cli(*args)

    def reselect(self):
        return self.fixture.cli('--record', self.record_path, 'delivery-select',
                                '--expect-state-sha', fixtures.digest(self.repo / self.STATE))

    def proof(self, record=None):
        record = copy.deepcopy(record or self.record())
        record['_recordPath'] = self.record_path
        return engine().canonical_selection_state_provenance(self.repo, record)

    def test_extend_then_normal_select_and_event_preserve_custody_and_clocks(self):
        self.prepare_selected()
        before = self.record()
        state_bytes = (self.repo / self.STATE).read_bytes()
        identity = engine().record_identity(before, self.record_path)
        self.extend()  # Baseline must fail here with EXTEND-STATE-INVERSE.
        extended = self.record()
        self.assertEqual((self.repo / self.STATE).read_bytes(), state_bytes)
        for key in ('owner', 'startedUTC', 'foreignDirty', 'adoptedDirty', 'sourceHashes', 'delivery'):
            self.assertEqual(extended[key], before[key], key)
        self.assertEqual(engine().record_identity(extended, self.record_path), identity)
        self.assertEqual(len(extended['pathExtensions']), 1)
        self.assertEqual(self.proof(), {self.STATE: fixtures.digest(self.repo / self.STATE)})
        self.reselect()
        selected = json.loads((self.repo / self.STATE).read_text())
        self.assertEqual(selected['activeSlice'], extended['slice'])
        self.assertEqual(selected['activeSelection']['generation'], 2)
        self.assertEqual(selected['sliceSelectionHistory'][:-1], json.loads(state_bytes)['sliceSelectionHistory'])
        active = dict(extended, _recordPath=self.record_path)
        engine().current_selection(active, selected, 2)
        self.append({'eventId': 'extended-plan', 'kind': 'plan-changed', 'reason': 'dependency declared',
                     'owner': 'root', 'nextAction': 'run the original selected component'}, selection=2)
        self.assertEqual(self.record()['delivery']['events'][-1]['kind'], 'plan-changed')
        self.assertEqual(self.record()['delivery']['clockOrigin'], before['delivery']['clockOrigin'])

    def test_event_still_refuses_until_explicit_normal_reselection(self):
        self.prepare_selected()
        self.extend()
        before = (self.repo / self.record_path).read_bytes()
        result = self.append({'eventId': 'not-selected-yet', 'kind': 'deferred', 'reason': 'fixture',
                              'owner': 'root', 'nextAction': 'select the extended slice'}, ok=False)
        self.assertIn('Canonical delivery selection differs', result.stdout)
        self.assertEqual((self.repo / self.record_path).read_bytes(), before)

    def test_repeated_extend_select_cycles_keep_exact_full_state_inverse(self):
        self.prepare_selected()
        self.extend()
        self.reselect()
        second = 'implementation/warlock/src/AnotherDependency.elm'
        # An absent, explicitly declared future dependency is an existing API case.
        self.extend(second)
        self.reselect()
        self.assertEqual(self.proof(), {self.STATE: fixtures.digest(self.repo / self.STATE)})
        selected = json.loads((self.repo / self.STATE).read_text())
        self.assertEqual(selected['activeSelection']['generation'], 3)
        engine().current_selection(dict(self.record(), _recordPath=self.record_path), selected, 3)

    def test_unrelated_state_edit_cannot_be_laundered_by_extend_or_select(self):
        self.prepare_selected()
        self.extend()
        state = json.loads((self.repo / self.STATE).read_text())
        state['unrelatedFixtureField'] = 'foreign edit'
        self.fixture.write(self.STATE, state)
        before_record = (self.repo / self.record_path).read_bytes()
        before_state = (self.repo / self.STATE).read_bytes()
        self.assertEqual(self.proof(), {})
        self.fixture.cli('--record', self.record_path, 'delivery-select', '--expect-state-sha',
                         fixtures.digest(self.repo / self.STATE), ok=False)
        self.assertEqual((self.repo / self.record_path).read_bytes(), before_record)
        self.assertEqual((self.repo / self.STATE).read_bytes(), before_state)

    def test_tampered_extension_source_order_or_membership_refuses(self):
        self.prepare_selected()
        self.extend()
        for mutate in (lambda r: r['pathExtensions'][-1]['sourceHashes'].update({self.source: 'a' * 64}),
                       lambda r: r['slice']['paths'].reverse(),
                       lambda r: r['pathExtensions'][-1].update(reason=''),
                       lambda r: r['pathExtensions'][-1].update(afterIteration=True)):
            with self.subTest(mutate=mutate):
                record = self.record()
                mutate(record)
                self.assertEqual(self.proof(record), {})

    def test_forged_earlier_extension_timestamp_refuses_old_selected_slice(self):
        self.prepare_selected()
        self.extend()
        record = self.record()
        record['pathExtensions'][0]['atUTC'] = record['startedUTC']
        self.assertEqual(self.proof(record), {})

    def test_failed_final_validation_leaves_record_object_and_files_unchanged(self):
        self.prepare_selected()
        module = engine()
        record = dict(self.record(), _recordPath=self.record_path)
        record['iterations'] = [{'claims': [{'sourceHashes': {self.source: fixtures.digest(self.repo / self.source)}}]}]
        before = copy.deepcopy(record)
        disk_before = {name: (self.repo / name).read_bytes() for name in (self.record_path, self.STATE)}
        reqs, state = module.context(self.repo)
        args = SimpleNamespace(path=[self.DEPENDENCY], reason='explicit dependency', adopt_dirty=[],
                               ownership_note=None, correct_support_ghost=None, record_snapshot=None)
        with module.delivery_edit_lock(self.repo, self.record_path), patch.object(module, 'validate', return_value=(['forced final refusal'], [])):
            with self.assertRaisesRegex(ValueError, 'forced final refusal'):
                module.extend_paths(self.repo, record, reqs, state, args)
        self.assertEqual(record, before)
        for name, raw in disk_before.items():
            self.assertEqual((self.repo / name).read_bytes(), raw)

    def test_dirty_new_dependency_retains_exact_pre_adoption_identity_binding(self):
        self.prepare_selected(dirty_dependency=True)
        before = self.record()
        self.extend(adopt=True)
        extended = self.record()
        self.assertNotIn(self.DEPENDENCY, extended['foreignDirty'])
        self.assertEqual(extended['pathExtensions'][-1]['foreignHashes'],
                         {self.DEPENDENCY: before['foreignDirty'][self.DEPENDENCY]})
        self.assertEqual(self.proof(), {self.STATE: fixtures.digest(self.repo / self.STATE)})
        self.reselect()
        self.assertEqual(self.proof(), {self.STATE: fixtures.digest(self.repo / self.STATE)})

    def test_dirty_extension_foreign_hash_tamper_refuses(self):
        self.prepare_selected(dirty_dependency=True)
        self.extend(adopt=True)
        record = self.record()
        record['pathExtensions'][-1]['foreignHashes'][self.DEPENDENCY] = 'f' * 64
        self.assertEqual(self.proof(record), {})

    def test_selection_history_edit_still_refuses_after_reselection(self):
        self.prepare_selected()
        self.extend()
        self.reselect()
        state = json.loads((self.repo / self.STATE).read_text())
        state['sliceSelectionHistory'][-1]['activeSlice']['after'] = 'unrecorded change'
        self.fixture.write(self.STATE, state)
        self.assertEqual(self.proof(), {})

    def test_legacy_unknown_custody_identity_never_matches_null_selection(self):
        self.prepare_selected(dirty_dependency=True)
        self.extend(adopt=True)
        record = self.record()
        record['pathExtensions'][-1].pop('foreignHashes')
        state = json.loads((self.repo / self.STATE).read_text())
        state['activeSelection']['recordIdentitySha256'] = None
        self.fixture.write(self.STATE, state)
        self.assertEqual(self.proof(record), {})
