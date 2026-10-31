"""CPU fixture checks for the development-only capture receiver."""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from elm_haskell_frame_receiver import FrameError, MAX_STDOUT, archive_frame, decode_frame, _owned_fd


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def noisy_png():
    noise = random.Random(20261031).randbytes(800 * 600 * 3)
    rows = b''.join(b'\0' + noise[i:i + 2400] for i in range(0, len(noise), 2400))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 800, 600, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


def envelope(png):
    return {'schema': 1, 'receipt': {'result': 'UNATTRIBUTED', 'renderObserved': False,
            'receiptFinalDeadlineChecked': False, 'toolIssuerBindingExternallyQualified': False,
            'image': {'name': '../../do-not-use.png', 'bytes': len(png), 'sha256': hashlib.sha256(png).hexdigest()}},
            'pngBase64': base64.b64encode(png).decode('ascii')}


def encode(value):
    return json.dumps(value, separators=(',', ':')).encode() + b'\n'


class ReceiverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.png = noisy_png()
        cls.frame = envelope(cls.png)

    def test_large_exact_payload_and_conservative_facts(self):
        encoded = encode(self.frame)
        self.assertGreater(len(encoded), 1024 * 1024)
        receipt, payload, facts = decode_frame(encoded)
        self.assertEqual(payload, self.png)
        self.assertEqual(receipt['image']['sha256'], hashlib.sha256(payload).hexdigest())
        self.assertTrue(facts['payloadSHA256Verified'])
        self.assertTrue(facts['containerCRCVerified'])
        self.assertFalse(facts['pixelsDecoded'])
        self.assertFalse(facts['nativeAccepted'])

    def test_framing_duplicates_and_schema(self):
        raw = encode(self.frame)
        for broken in [raw[:-1], raw + raw, raw + b'junk', raw.replace(b'"schema":1', b'"schema":1,"schema":1'),
                       raw.replace(b'"schema":1', b'"schema":true'), b'\xff\n', b'[' * 1100 + b'0' + b']' * 1100 + b'\n',
                       b' ' * MAX_STDOUT + b'\n']:
            with self.subTest(length=len(broken)), self.assertRaises(FrameError):
                decode_frame(broken)

    def test_receipt_and_payload_corruption(self):
        for key, value in [('renderObserved', True), ('receiptFinalDeadlineChecked', True),
                           ('toolIssuerBindingExternallyQualified', True), ('result', 'ACCEPTED')]:
            frame = copy.deepcopy(self.frame)
            frame['receipt'][key] = value
            with self.subTest(key=key), self.assertRaises(FrameError):
                decode_frame(encode(frame))
        for mutate in [lambda x: x['receipt']['image'].update(bytes=True),
                       lambda x: x['receipt']['image'].update(sha256='0' * 64),
                       lambda x: x.update(pngBase64=x['pngBase64'] + '='),
                       lambda x: x.update(pngBase64='!'),
                       lambda x: x['receipt'].update(image=None),
                       lambda x: x['receipt'].update(note='\ud800')]:
            frame = copy.deepcopy(self.frame)
            mutate(frame)
            with self.assertRaises(FrameError):
                decode_frame(encode(frame))
        for raw in [b'{"schema":NaN}\n', b'{"schema":1e999}\n']:
            with self.assertRaises(FrameError):
                decode_frame(raw)

    def test_hash_matching_bad_png_retained_without_validity_claim(self):
        bad = self.png[:-1] + bytes([self.png[-1] ^ 1])
        _, payload, facts = decode_frame(encode(envelope(bad)))
        self.assertEqual(payload, bad)
        self.assertTrue(facts['payloadSHA256Verified'])
        self.assertFalse(facts['containerCRCVerified'])
        self.assertFalse(facts['nativeAccepted'])

    def test_absent_image(self):
        frame = copy.deepcopy(self.frame)
        frame['receipt']['image'], frame['pngBase64'] = None, ''
        _, payload, facts = decode_frame(encode(frame))
        self.assertEqual(payload, b'')
        self.assertFalse(facts['payloadSHA256Verified'])

    def test_archive_fixed_names_modes_replay_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            archive_frame(encode(self.frame), parent, 'capture-1')
            files = set(p.name for p in (parent / 'capture-1').iterdir())
            self.assertEqual(files, {'frame.stdout', 'frame.png', 'receipt.json', 'observation.json'})
            self.assertEqual((parent / 'capture-1/frame.png').read_bytes(), self.png)
            for p in (parent / 'capture-1').iterdir():
                self.assertEqual(p.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                archive_frame(encode(self.frame), parent, 'capture-1')
            (parent / 'symlink').symlink_to(parent / 'capture-1', target_is_directory=True)
            with self.assertRaises(FileExistsError):
                archive_frame(encode(self.frame), parent, 'symlink')
            with self.assertRaises(FrameError):
                archive_frame(encode(self.frame), parent, '../escape')
            parent.chmod(0o755)
            with self.assertRaises(FrameError):
                archive_frame(encode(self.frame), parent, 'unsafe-parent')
            self.assertFalse((parent / 'unsafe-parent').exists())
            parent.chmod(0o700)

    def test_close_fault_attempts_parent_and_retains_original(self):
        parent = os.open('/dev/null', os.O_RDONLY)
        child = os.open('/dev/null', os.O_RDONLY)
        close = os.close
        calls = []
        def closing(fd):
            calls.append(fd)
            close(fd)
            if fd == child:
                raise OSError('injected uncertain close')
        with patch('elm_haskell_frame_receiver.os.close', side_effect=closing):
            with self.assertRaises(BaseExceptionGroup) as caught:
                with _owned_fd(parent), _owned_fd(child):
                    raise ValueError('original operation failure')
        self.assertEqual(calls, [child, parent])
        errors = caught.exception.exceptions
        self.assertTrue(any(isinstance(e, ValueError) for e in errors))
        self.assertTrue(any(isinstance(e, OSError) for e in errors))

    def test_short_writes_complete_exact_archive(self):
        write = os.write
        with tempfile.TemporaryDirectory() as directory:
            with patch('elm_haskell_frame_receiver.os.write', side_effect=lambda fd, data: write(fd, data[:65536])) as mocked:
                archive_frame(encode(self.frame), Path(directory), 'short-writes')
            self.assertGreater(mocked.call_count, 4)
            self.assertEqual((Path(directory) / 'short-writes/frame.png').read_bytes(), self.png)


if __name__ == '__main__':
    unittest.main()
