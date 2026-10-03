"""Detect mismatched lifetime/output evidence before any pixel acceptance."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from compare_scene import verify_scene
from raster_oracle import encode_png


class SceneEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'owned.png'
        material = encode_png(2, 1, bytes((200, 12, 100, 255, 1, 2, 3, 128)))
        self.path.write_bytes(material)
        member = {'stableId': 'abcd', 'pid': 42, 'digest': hashlib.sha256(material).hexdigest(),
                  'path': str(self.path), 'pixels': [2, 1]}
        self.fixture = {'token': 'abcdef123456-1', 'progress': 0.375,
                        'diagnosticNoNativeAuthority': True,
                        'screenshotMapping': 'untransformed-output-buffer',
                        'allowedPresentedSequences': ['7'],
                        'output': {'name': 'HEADLESS-1', 'generation': 3, 'transform': 0},
                        'members': [member]}
        self.frame = {'event': 'presented', 'accepted': True, 'token': self.fixture['token'],
                      'progress': 0.375, 'output': 'HEADLESS-1', 'generation': 3,
                      'sequence': '7', 'submittedNs': '100', 'timestampNs': '200',
                      'members': [{k: member[k] for k in ('stableId', 'pid', 'digest')}]}
        self.frame['members'][0]['rectangle'] = {'x': 0, 'y': 0, 'width': 2, 'height': 1}

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_bound_presented_record_accepts(self):
        _, sources = verify_scene(self.fixture, self.frame)
        self.assertEqual(len(sources), 1)

    def test_stale_output_lifetime_token_and_capture_sequence_refused(self):
        for key, value in (('generation', 2), ('output', 'FOREIGN'),
                           ('token', 'abcdef123456-2'), ('sequence', '8'), ('progress', 0.5)):
            changed = copy.deepcopy(self.frame)
            changed[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_scene(self.fixture, changed)

    def test_swapped_source_or_identity_refused_even_with_correct_pixels(self):
        for key, value in (('stableId', 'dcba'), ('pid', 43), ('digest', '0' * 64)):
            changed = copy.deepcopy(self.frame)
            changed['members'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_scene(self.fixture, changed)

    def test_empty_partial_or_extra_coverage_refused(self):
        for members in ([], self.frame['members'] * 2):
            changed = {**self.frame, 'members': members}
            with self.assertRaises(ValueError):
                verify_scene(self.fixture, changed)

    def test_nonpresented_failed_or_temporally_impossible_records_refused(self):
        for key, value in (('event', 'swap'), ('accepted', False), ('timestampNs', '0'),
                           ('submittedNs', '0'), ('timestampNs', '99')):
            changed = {**self.frame, key: value}
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_scene(self.fixture, changed)

    def test_unproved_transform_and_native_authority_fixture_refused(self):
        for change in ({'diagnosticNoNativeAuthority': False},
                       {'screenshotMapping': 'guessed'},
                       {'output': {**self.fixture['output'], 'transform': 1}}):
            with self.assertRaises(ValueError):
                verify_scene({**self.fixture, **change}, self.frame)


if __name__ == '__main__':
    unittest.main()
