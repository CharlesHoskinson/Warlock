"""Retained readiness references survive normal job closure; no native effects."""
import copy
import hashlib
import unittest

import test_delivery as existing


class RetainedReadinessEditTests(unittest.TestCase):
    launch = existing.DeliveryEditPrecheckTests.launch
    check = existing.DeliveryEditPrecheckTests.check
    close = existing.DeliveryEditPrecheckTests.close

    def setUp(self):
        existing.DeliveryEditPrecheckTests.setUp(self)
        self.readiness = '.warlock-contributor/evidence/native-v1/readiness.json'
        path = self.root / self.readiness
        path.parent.mkdir(parents=True)
        path.write_text('{"review":"original immutable readiness"}\n')
        self.reference = {'path': self.readiness,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        self.candidate['nativePrerequisites'] = [self.reference]
        self.candidate['scope'] = 'native'
        # This fixture's launch helper records cpu; use no journal for this native
        # candidate. Canonical job states below exercise the same precheck path.

    def consumed(self):
        self.close(True)
        self.view['job'] = {'jobId': 'pid123-start77', 'consumed': True}
        self.view['terminal'] = {'classification': 'pass'}

    def test_consumed_native_readiness_remains_immutable_without_history_changes(self):
        self.consumed()
        before = copy.deepcopy(self.record)
        identity = self.m.record_identity(self.record, self.record['_recordPath'])
        raw = (self.root / self.readiness).read_bytes()
        with self.assertRaisesRegex(ValueError, 'Retained native prerequisite edit refused'):
            self.check([self.readiness])
        self.assertEqual(self.record, before)
        self.assertEqual(self.m.record_identity(self.record, self.record['_recordPath']), identity)
        self.assertEqual((self.root / self.readiness).read_bytes(), raw)

    def test_running_job_readiness_outside_manifest_is_immutable(self):
        self.view['job'] = {'jobId': 'running', 'consumed': False}
        with self.assertRaisesRegex(ValueError, 'Retained native prerequisite edit refused'):
            self.check([self.readiness])

    def test_older_candidate_readiness_stays_immutable_after_replacement(self):
        self.consumed()
        later = copy.deepcopy(self.candidate)
        later['nativePrerequisites'] = []
        later['scope'] = 'cpu'
        self.record['delivery']['events'].append({'kind': 'candidate', 'candidateSha256': 'c'*64, 'candidate': later})
        self.view.update(candidate=later, candidateSha256='c'*64, job=None, terminal=None)
        with self.assertRaisesRegex(ValueError, 'Retained native prerequisite edit refused'):
            self.check([str(self.root / self.readiness)])

    def test_ready_unlaunched_candidate_reference_is_already_retained(self):
        with self.assertRaisesRegex(ValueError, 'Retained native prerequisite edit refused'):
            self.check([self.readiness])

    def test_ordinary_post_consumed_source_edit_remains_allowed(self):
        self.consumed()
        self.assertTrue(self.check([self.runner])['structuralPrecheckPassed'])

    def test_new_namespace_and_no_byte_change_remain_allowed_while_running(self):
        self.view['job'] = {'jobId': 'running', 'consumed': False}
        before = copy.deepcopy(self.record)
        new_path = '.warlock-contributor/evidence/native-v2/readiness.json'
        self.assertTrue(self.check([new_path])['structuralPrecheckPassed'])
        self.assertTrue(self.check([])['structuralPrecheckPassed'])
        self.assertEqual(self.record, before)
        self.assertFalse((self.root / new_path).exists())


if __name__ == '__main__':
    unittest.main()
