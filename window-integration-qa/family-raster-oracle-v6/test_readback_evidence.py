"""Reject stale, wrong-alpha, redirected or incomplete framebuffer evidence."""
import copy
import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from raster_oracle import encode_png
from readback_evidence import verify_readback, record_pixels, all_pixels_accepted


class ReadbackEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.directory.chmod(0o700)
        # Asymmetric premultiplied channels preserve alpha and orientation.
        self.pixels = bytes((12, 20, 40, 64, 1, 2, 3, 8,
                             0, 0, 0, 0, 200, 12, 30, 255))
        self.path = self.directory / 'owned-7-3.png'
        self.path.write_bytes(encode_png(2, 2, self.pixels))
        self.path.chmod(0o600)
        self.frame = {'event': 'presented', 'accepted': True,
                      'token': 'abcdef123456-1', 'digest': 'a'*64,
                      'stableId': 'abc1', 'pid': 42, 'sequence': '7',
                      'output': 'HEADLESS-1', 'generation': 3, 'progress': .35,
                      'bufferWidth': 2, 'bufferHeight': 2,
                      'members': [{'stableId': 'abc1', 'pid': 42, 'digest': 'b'*64,
                                   'rectangle': {'x': 1, 'y': 2, 'width': 2, 'height': 2}}]}
        self.row = {k: v for k, v in self.frame.items() if k not in ('event', 'accepted')}
        self.row.update(event='ownedFramebufferReadback', filename=self.path.name,
                        nativeAuthority=False, presentationProof=False, readError=0,
                        rawSHA256=hashlib.sha256(self.pixels).hexdigest(),
                        encoding='premultiplied-RGBA8-top-left',
                        eglSurface={'width': 2, 'height': 2},
                        eglConfig=dict(red=8, green=8, blue=8, alpha=8, buffer=32,
                                       samples=0, sampleBuffers=0, configId=1,
                                       colorBufferType=12430, nativeVisualId=0),
                        glBuffer=dict(red=8, green=8, blue=8, alpha=8,
                                      readFormat=6408, readType=5121, sampleBuffers=0,
                                      samples=0, framebuffer=0))

    def tearDown(self):
        self.temp.cleanup()

    def test_raw_alpha_and_top_left_orientation_preserved(self):
        actual, _ = verify_readback(self.row, self.frame, self.directory)
        self.assertEqual(actual, self.pixels)

    def test_stale_identity_sequence_geometry_and_output_refused(self):
        changes = dict(token='abcdef123456-2', digest='c'*64, stableId='abc2',
                       pid=43, sequence='8', output='FOREIGN', generation=4,
                       progress=.5, bufferWidth=3, bufferHeight=3, members=[])
        for key, value in changes.items():
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_readback({**self.row, key: value}, self.frame, self.directory)
        row = copy.deepcopy(self.row)
        row['members'][0]['rectangle']['x'] += 1
        with self.assertRaises(ValueError): verify_readback(row, self.frame, self.directory)

    def test_readback_cannot_stand_in_for_actual_presentation(self):
        for change in ({'event': 'swap'}, {'accepted': False}):
            with self.assertRaises(ValueError):
                verify_readback(self.row, {**self.frame, **change}, self.directory)

    def test_missing_gl_egl_fields_authority_or_conversion_refused(self):
        for change in ({'glBuffer': {}}, {'eglConfig': {}}, {'eglSurface': {'width': 3, 'height': 2}},
                       {'nativeAuthority': True}, {'presentationProof': True},
                       {'readError': 1282}, {'encoding': 'straight-alpha'},
                       {'rawSHA256': '0'*64}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_readback({**self.row, **change}, self.frame, self.directory)

    def test_traversal_filename_and_symlink_refused(self):
        for filename in ('../owned-7-3.png', '/tmp/owned-7-3.png', 'owned-8-3.png'):
            with self.assertRaises(ValueError):
                verify_readback({**self.row, 'filename': filename}, self.frame, self.directory)
        saved = self.path.with_name('saved.png')
        self.path.rename(saved); self.path.symlink_to(saved)
        with self.assertRaises(ValueError): verify_readback(self.row, self.frame, self.directory)

    def test_nonprivate_file_or_directory_refused(self):
        self.path.chmod(0o644)
        with self.assertRaises(ValueError): verify_readback(self.row, self.frame, self.directory)
        self.path.chmod(0o600); self.directory.chmod(0o755)
        with self.assertRaises(ValueError): verify_readback(self.row, self.frame, self.directory)

    def test_pixel_failures_retained_without_losing_remaining_samples(self):
        checks = []
        record_pixels(checks, 'first bad image', {'passed': False, 'badPixels': 7})
        for i in range(7): record_pixels(checks, str(i), {'passed': True})
        self.assertEqual(len(checks), 8)
        self.assertFalse(all_pixels_accepted(checks))
        self.assertEqual(checks[0]['comparison']['badPixels'], 7)
        self.assertFalse(all_pixels_accepted(checks[1:]))
        self.assertTrue(all_pixels_accepted([{'comparison': {}, 'passed': True} for _ in range(8)]))


if __name__ == '__main__': unittest.main()
