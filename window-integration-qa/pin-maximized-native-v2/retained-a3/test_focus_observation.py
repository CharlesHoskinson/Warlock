"""Exercise actual controller sampling with injected CPU-only readers."""
from pathlib import Path
import tempfile
import unittest
from native_cases import NativeCases


TARGET = {'address': '0x123', 'stableId': '18000001', 'pid': 101}
OTHER = {'address': '0x456', 'stableId': '18000002', 'pid': 101}


class Session:
    def __init__(self): self.guards = 0
    def guard(self): self.guards += 1


class FocusObservation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.session = Session()
        self.case = NativeCases(self.session, Path(self.tmp.name)/'cpu')

    def pair(self, core, seat):
        native = {'nativeFocus': core, 'extraNativeEvidence': ['retained']}
        keyboard = {'keyboardOwner': seat, 'extraSeatEvidence': ['retained']}
        self.case.native = lambda: native
        self.case.seat = lambda: keyboard
        return native, keyboard

    def test_positive_returns_exact_persisted_objects(self):
        native, seat = self.pair(TARGET, TARGET)
        result = self.case.focus_pair('nested', TARGET)
        self.assertIs(result[0], native)
        self.assertIs(result[1], seat)
        self.assertIs(self.case.report['observations'][0]['value'], native)
        self.assertIs(self.case.report['observations'][1]['value'], seat)
        self.assertEqual(self.session.guards, 2)

    def test_core_mismatch_still_records_seat(self):
        native, seat = self.pair(OTHER, TARGET)
        self.assertIsNone(self.case.focus_pair('nested', TARGET))
        self.assertEqual([x['value'] for x in self.case.report['observations']], [native, seat])

    def test_seat_mismatch_retains_both(self):
        native, seat = self.pair(TARGET, OTHER)
        self.assertIsNone(self.case.focus_pair('nested', TARGET))
        self.assertEqual([x['value'] for x in self.case.report['observations']], [native, seat])

    def test_both_mismatches_retained(self):
        native, seat = self.pair(OTHER, OTHER)
        self.assertIsNone(self.case.focus_pair('nested', TARGET))
        self.assertEqual([x['value'] for x in self.case.report['observations']], [native, seat])

    def test_seat_failure_keeps_native_and_actual_error(self):
        native, _ = self.pair(OTHER, TARGET)
        def failed(): raise RuntimeError('injected Seat read error')
        self.case.seat = failed
        with self.assertRaisesRegex(RuntimeError, 'Seat read error'):
            self.case.focus_pair('nested', TARGET)
        rows = self.case.report['observations']
        self.assertIs(rows[0]['value'], native)
        self.assertIn('Seat read error', rows[1]['error'])
        self.assertNotIn('value', rows[1])

    def test_native_failure_does_not_fabricate_seat(self):
        def failed(): raise RuntimeError('injected native read error')
        self.case.native = failed
        def impossible(): self.fail('Seat reader must not run after native failure')
        self.case.seat = impossible
        with self.assertRaisesRegex(RuntimeError, 'native read error'):
            self.case.focus_pair('nested', TARGET)
        rows = self.case.report['observations']
        self.assertEqual(len(rows), 1)
        self.assertIn('native read error', rows[0]['error'])

    def test_original_public_pid_type_guard_retained(self):
        self.pair({**TARGET, 'pid': True}, TARGET)
        self.assertIsNone(self.case.focus_pair('nested', TARGET))

    def test_sampler_does_not_requery_after_predicate(self):
        calls = []
        native, seat = self.pair(TARGET, TARGET)
        def read():
            calls.append('native')
            return native if len(calls)==1 else {'nativeFocus': OTHER}
        self.case.native = read
        result = self.case.focus_pair('nested', TARGET)
        self.assertEqual(calls, ['native'])
        self.assertIs(result[0], native)


if __name__ == '__main__': unittest.main()
