import copy
import unittest
from verify_sampling import verify, POLICY


class SamplerConfiguration(unittest.TestCase):
    def setUp(self):
        self.sources = [{'digest': 'a'*64, 'pixels': [64,48]},
                        {'digest': 'b'*64, 'pixels': [23,17]},
                        {'digest': 'c'*64, 'pixels': [7,9]}]
        self.events = [{'event': 'samplingExperiment', 'policy': POLICY,
            'fragmentSHA256': 'd'*64, 'rasterDiagnostic': True,
            'nativeAuthority': False, 'pixelProof': False}]
        for i, s in enumerate(self.sources + [dict(digest='', pixels=[1,1])]*3):
            self.events.append({'event': 'samplingConfigured', 'policy': POLICY,
                'textureId': i+1, 'sourceDigest': s['digest'], 'pixels': s['pixels'][:],
                'controlIndex': -1 if i<3 else i-3, 'extentUniform': s['pixels'][:],
                'minFilter': 9728, 'magFilter': 9728, 'wrapS': 33071, 'wrapT': 33071,
                'inspectionError': 0, 'nativeAuthority': False, 'pixelProof': False})

    def accepts(self):
        return verify(self.events, self.sources, 'd'*64)

    def test_complete_exact_observation(self):
        self.assertEqual(self.accepts()['familyTextureCount'], 3)

    def test_one_pixel_control_never_substitutes_family(self):
        self.events[1]['controlIndex'] = 0
        self.assertRaises(ValueError, self.accepts)

    def test_stale_source_digest(self):
        self.events[2]['sourceDigest'] = 'e'*64
        self.assertRaises(ValueError, self.accepts)

    def test_native_window_extent_is_not_source_extent(self):
        self.events[2]['pixels'] = self.events[2]['extentUniform'] = [230,170]
        self.assertRaises(ValueError, self.accepts)

    def test_sticky_control_uniform(self):
        self.events[3]['extentUniform'] = [1,1]
        self.assertRaises(ValueError, self.accepts)

    def test_queried_state_and_errors(self):
        for field, bad in [('minFilter',9729), ('magFilter',9729), ('wrapS',10497),
                           ('wrapT',10497), ('inspectionError',1282)]:
            with self.subTest(field=field):
                saved = copy.deepcopy(self.events)
                self.events[1][field] = bad
                self.assertRaises(ValueError, self.accepts)
                self.events = saved

    def test_missing_family_and_control_records(self):
        for n in (1,5):
            with self.subTest(record=n):
                saved = self.events[:]
                self.events.pop(n)
                self.assertRaises(ValueError, self.accepts)
                self.events = saved

    def test_duplicate_texture_cannot_attest_two_sources(self):
        self.events[2]['textureId'] = self.events[1]['textureId']
        self.assertRaises(ValueError, self.accepts)

    def test_numeric_booleans_are_invalid_getters(self):
        self.events[1]['inspectionError'] = False
        self.assertRaises(ValueError, self.accepts)

    def test_wrong_fragment_is_not_experiment(self):
        self.events[0]['fragmentSHA256'] = 'f'*64
        self.assertRaises(ValueError, self.accepts)

    def test_pixels_and_presentation_are_separate(self):
        self.events[2]['pixelProof'] = True
        self.assertRaises(ValueError, self.accepts)


if __name__ == '__main__':
    unittest.main()
