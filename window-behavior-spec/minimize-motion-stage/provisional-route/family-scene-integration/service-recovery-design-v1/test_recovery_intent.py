import copy
from pathlib import Path
import sys
import unittest
import threading
from types import SimpleNamespace

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'service-review-v12'))
from recovery_intent import reconstruct,snapshot_intent
from direction import Direction

A = ['0xaa', 'aa', 41]
B = ['0xbb', 'bb', 41]
C = ['0xcc', 'cc', 42]


def constant(operation):
    return {'anchor': operation, 'inverted': False, 'identity': None}


def event(receipt, command, captured=A):
    return {'receipt': receipt, 'command': command, 'captured': captured}


def ledger(events=None, receipt=2):
    return {'anchors': [], 'events': events or [event(1, 'minimize'), event(2, 'toggle')], 'receipts': [[A, receipt], [B, receipt]]}


def window(captured, minimized=False):
    return {'address': captured[0], 'stableId': captured[1], 'pid': captured[2], 'mapped': True,
            'workspace': {'name': 'special:win-minimized' if minimized else '1'}}


class RecoveryIntentTest(unittest.TestCase):
    def test_accepted_reverse_stays_restore_after_partial_minimize(self):
        plan = reconstruct(ledger(), [A, B], 2)
        self.assertEqual(plan.endpoint([window(A, True), window(B)]), 'restore')
        self.assertEqual(plan.receipt, 2)

    def test_constant_minimize_does_not_retoggle_partial_endpoint(self):
        plan = reconstruct(ledger([event(1, 'minimize')], 1), [A, B], 1)
        self.assertEqual(plan.endpoint([window(A, True), window(B)]), 'minimize')

    def test_anchored_toggle_uses_exact_captured_fresh_state(self):
        plan = reconstruct(ledger([event(1, 'toggle')], 1), [A, B], 1)
        self.assertEqual(plan.endpoint([window(A, True), window(B)]), 'restore')
        self.assertEqual(plan.endpoint([window(A), window(B, True)]), 'minimize')

    def test_activate_uses_exact_active_identity(self):
        plan = reconstruct(ledger([event(1, 'activate')], 1), [A, B], 1)
        self.assertEqual(plan.endpoint([window(A), window(B)], A), 'minimize')
        self.assertEqual(plan.endpoint([window(A), window(B)], B), 'restore')
        self.assertEqual(plan.endpoint([window(A), window(B)], None), 'restore')

    def test_unrelated_later_receipt_cannot_override_family_direction(self):
        body = ledger([event(1, 'restore'), event(3, 'minimize', C)], 1)
        body['receipts'].append([C, 3])
        self.assertEqual(reconstruct(body, [A, B], 3).direction.constant, 'restore')

    def test_compressed_anchor_and_later_toggle_replay(self):
        body = ledger([event(2, 'toggle')])
        body['anchors'] = [{'identity': k, 'receipt': 1, 'direction': constant('restore')} for k in (A, B)]
        self.assertEqual(reconstruct(body, [A, B], 2).direction.constant, 'minimize')

    def test_disagreeing_previous_scopes_refuse_merge(self):
        body = ledger()
        body['anchors'] = [{'identity': A, 'receipt': 1, 'direction': constant('restore')}, {'identity': B, 'receipt': 2, 'direction': constant('restore')}]
        with self.assertRaisesRegex(ValueError, 'atomic replacement'):
            reconstruct(body, [A, B], 2)

    def test_same_receipt_conflicting_anchor_refused(self):
        body = ledger()
        body['anchors'] = [{'identity': A, 'receipt': 1, 'direction': constant('restore')}, {'identity': B, 'receipt': 1, 'direction': constant('minimize')}]
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            reconstruct(body, [A, B], 2)

    def test_newer_receipt_without_direction_provenance_refused(self):
        body = ledger([event(1, 'minimize')], 2)
        with self.assertRaisesRegex(ValueError, 'provenance differ'):
            reconstruct(body, [A, B], 2)

    def test_duplicate_or_future_events_refused(self):
        for events in ([event(1, 'restore'), event(1, 'minimize')], [event(3, 'restore')]):
            with self.subTest(events=events), self.assertRaisesRegex(ValueError, 'duplicate/future'):
                reconstruct(ledger(events), [A, B], 2)

    def test_boolean_receipt_pid_and_inversion_refused(self):
        for change in ('receipt', 'pid', 'inversion'):
            body = ledger()
            if change == 'receipt': body['events'][0]['receipt'] = True
            if change == 'pid': body['events'][0]['captured'] = ['0xaa', 'aa', True]
            if change == 'inversion': body['anchors'] = [{'identity': A, 'receipt': 1, 'direction': {'anchor': 'restore', 'inverted': 1, 'identity': None}}]
            with self.subTest(change=change), self.assertRaises(ValueError):
                reconstruct(body, [A, B], 2)

    def test_missing_identity_and_reused_pid_cannot_resolve_plan(self):
        plan = reconstruct(ledger(), [A, B], 2)
        for windows in ([window(A)], [window(['0xaa', 'aa', 99]), window(B)]):
            with self.subTest(windows=windows), self.assertRaisesRegex(ValueError, 'family changed'):
                plan.endpoint(windows)

    def test_duplicate_fresh_family_refused(self):
        with self.assertRaises(ValueError):
            reconstruct(ledger(), [A, A], 2)
        plan = reconstruct(ledger(), [A, B], 2)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            plan.endpoint([window(A), window(A)])

    def test_direction_anchor_outside_fresh_family_refused(self):
        body = ledger([])
        body['events'] = []
        body['anchors'] = [{'identity': A, 'receipt': 2, 'direction': {'anchor': 'activate', 'inverted': False, 'identity': C}}]
        with self.assertRaisesRegex(ValueError, 'another fresh family'):
            reconstruct(body, [A, B], 2)

    def test_unknown_and_incomplete_old_ledger_refused(self):
        for body in ({}, {'events': []}, {'anchors': [], 'events': [], 'receipts': []}):
            with self.subTest(body=body), self.assertRaises(ValueError):
                reconstruct(body, [A, B], 2)

    def test_reconstruction_does_not_modify_journal(self):
        body = ledger()
        before = copy.deepcopy(body)
        reconstruct(body, [A, B], 2)
        self.assertEqual(body, before)
    def test_activation_does_not_focus_reused_active_address(self):
        plan = reconstruct(ledger([event(1, 'activate')], 1), [A, B], 1)
        with self.assertRaisesRegex(ValueError,'reused exact identity'):
            plan.endpoint([window(A),window(B)],['0xaa','aa',99])
    def test_actual_manager_ledger_roundtrip_preserves_constant_reverse(self):
        manager=SimpleNamespace(lock=threading.RLock(),intent_anchors={tuple(k):(1,Direction('minimize')) for k in (A,B)},
            intent_events={2:{'captured':tuple(A),'command':'toggle'}},receipts={tuple(k):2 for k in (A,B)})
        body=snapshot_intent(manager)
        self.assertEqual(reconstruct(body,[A,B],2).endpoint([window(A,True),window(B)]),'restore')
        body['events'][0]['captured'][0]='0xff'
        self.assertEqual(manager.intent_events[2]['captured'],tuple(A))


if __name__ == '__main__':
    unittest.main()
