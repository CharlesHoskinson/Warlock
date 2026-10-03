import copy
from pathlib import Path
import sys
import unittest

P = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/producer-production-default-v10')
sys.path.insert(0, str(P))
from test_quantized_gate import Gate
from verify_quantized_over import copy_state
from verify_causal_target import verify_target


class TargetBinding(unittest.TestCase):
    def setUp(self):
        fixture = Gate()
        fixture.setUp()
        self.frame = fixture.frame
        self.record = dict(fixture.readback, kind='member-prefix', prefixCount=3, controls=[],
                           readFramebuffer=0, prefixTexture=102, observedPrefixCount=3,
                           readTargetCopy=fixture.copy_state(0, 102), nativeAuthority=False, presentationProof=False)

    def verify(self):
        return verify_target(self.record, self.frame, 20, copy_state)

    def test_all_family_prefixes_and_control_vectors(self):
        for count, texture in ((1, 102), (2, 101), (3, 102)):
            self.record.update(prefixCount=count, observedPrefixCount=count, prefixTexture=texture)
            self.record['readTargetCopy']['texture'] = texture
            self.assertTrue(self.verify()['actualCausalTargetBound'])
        for vector, texture in (((1,), 102), ((0, 1), 101), ((0, 1, 2), 102)):
            self.record.update(kind='constant-control', prefixCount=0, controls=[{'index': i} for i in vector],
                               observedPrefixCount=len(vector), prefixTexture=texture)
            self.record['readTargetCopy']['texture'] = texture
            self.assertFalse(self.verify()['nativeAuthority'])

    def test_substituted_target_prefix_extent_and_program_refused(self):
        original = copy.deepcopy(self.record)
        for field, value in (('readFramebuffer', 202), ('readFramebuffer', False), ('prefixTexture', 101),
                             ('observedPrefixCount', 2), ('generation', 8), ('sequence', '16'), ('output', 'other')):
            with self.subTest(field=field):
                self.record = copy.deepcopy(original)
                self.record[field] = value
                self.assertRaises(ValueError, self.verify)
        for field, value in (('framebuffer', 202), ('texture', 101), ('program', 8), ('blend', True),
                             ('extentUniform', [480, 240]), ('minFilter', 9729)):
            with self.subTest(copyField=field):
                self.record = copy.deepcopy(original)
                self.record['readTargetCopy'][field] = value
                self.assertRaises(ValueError, self.verify)

    def test_reordered_control_vector_refused(self):
        self.record.update(kind='constant-control', prefixCount=0, controls=[{'index': 1}, {'index': 0}], observedPrefixCount=2)
        self.assertRaises(ValueError, self.verify)

    def test_repeated_or_missing_pass_refused(self):
        self.frame['passes'][-1]['prefixCount'] = 2
        self.assertRaises(ValueError, self.verify)

    def test_missing_observation_cannot_claim_target(self):
        del self.record['readTargetCopy']
        self.assertRaises(ValueError, self.verify)


if __name__ == '__main__':
    unittest.main()
