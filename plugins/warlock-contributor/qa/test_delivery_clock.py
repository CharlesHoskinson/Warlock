"""Management clocks exclude measured suspend but retain fixed authorization."""
import datetime as dt
import unittest

from test_delivery_flow import engine


class DeliveryClockTests(unittest.TestCase):
    def setUp(self):
        self.module = engine()
        self.origin = {'utc': '2026-11-06T16:00:00+00:00', 'bootId': 'boot-a',
                       'monotonicNs': 1000000000, 'boottimeNs': 1000000000}
        self.record = {'workflowPolicy': 2, 'startedUTC': self.origin['utc'], 'iterations': [],
                       'delivery': {'schema': 1, 'clockOrigin': self.origin,
                                    'authorizationExpiresUTC': '2026-11-06T19:07:31+00:00', 'events': []}}

    def status(self, mono, boot=None, boot_id='boot-a', utc='2026-11-06T18:00:00+00:00'):
        sample = {'utc': utc, 'bootId': boot_id, 'monotonicNs': (1 + mono) * 1000000000,
                  'boottimeNs': (1 + (mono if boot is None else boot)) * 1000000000}
        return self.module.delivery_progress_status(self.record, sample=sample)

    def test_suspend_excluded_but_awake_queue_counts(self):
        self.assertTrue(hasattr(self.module, 'delivery_progress_status'))
        self.assertFalse(self.status(100, 7300)['planChangeRequired'])
        self.assertTrue(self.status(2700, 9900)['planChangeRequired'])
        self.assertEqual(self.status(100, 7300)['suspendedSeconds'], 7200)

    def test_legacy_progress_keys_remain_available(self):
        legacy = self.module.progress_status({'startedUTC': self.origin['utc'], 'iterations': []},
                                             dt.datetime.fromisoformat(self.origin['utc']))
        current = self.status(0)
        self.assertTrue(set(legacy) <= set(current))
        self.assertTrue(set(legacy['limits']) <= set(current['limits']))

    def test_reboot_and_regression_are_unknown(self):
        self.assertTrue(hasattr(self.module, 'delivery_progress_status'))
        self.assertTrue(self.status(100, boot_id='new-boot')['reconciliationRequired'])
        self.assertTrue(self.status(-1)['reconciliationRequired'])

    def test_expiry_during_suspend_still_applies(self):
        self.assertTrue(hasattr(self.module, 'delivery_progress_status'))
        result = self.status(1, 14400, utc='2026-11-06T20:00:00+00:00')
        self.assertTrue(result['authorizationExpired'])
        self.assertFalse(result['investigationNeedsChange'])

    def test_source_hash_progress_does_not_reset_new_clock(self):
        self.assertTrue(hasattr(self.module, 'delivery_progress_status'))
        self.record['iterations'] = [{'meaningfulProgress': True, 'atUTC': '2026-11-06T18:00:00+00:00'}]
        self.assertTrue(self.status(3000)['planChangeRequired'])

    def test_legacy_threshold_remains_utc_and_exact(self):
        record = {'startedUTC': self.origin['utc'], 'iterations': []}
        clock = dt.datetime.fromisoformat(self.origin['utc'])
        self.assertFalse(self.module.progress_status(record, clock + dt.timedelta(seconds=2699))['investigationNeedsChange'])
        self.assertTrue(self.module.progress_status(record, clock + dt.timedelta(seconds=2700))['investigationNeedsChange'])


if __name__ == '__main__':
    unittest.main()
