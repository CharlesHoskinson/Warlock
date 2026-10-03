"""Actual subprocess EOF and malformed event checks, without any GUI."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
from producer_observer import Observer


class DrainTests(unittest.TestCase):
    def test_complete_valid_eof(self):
        with tempfile.TemporaryDirectory() as directory:
            observer = Observer([sys.executable, '-c', 'print(\'{"event":"stopped"}\')'],
                                dict(os.environ), Path(directory))
            observer.process.wait(timeout=3)
            self.assertEqual(observer.close(), 0)
            self.assertTrue(observer.stdout_eof)
            self.assertEqual(observer.rows, [{'event': 'stopped'}])
            self.assertFalse(observer.thread.is_alive())

    def test_process_zero_does_not_hide_malformed_event(self):
        with tempfile.TemporaryDirectory() as directory:
            observer = Observer([sys.executable, '-c', 'print("malformed")'],
                                dict(os.environ), Path(directory))
            observer.process.wait(timeout=3)
            with self.assertRaisesRegex(RuntimeError, 'complete valid stdout EOF'):
                observer.close()
            self.assertEqual(observer.process.returncode, 0)
            self.assertTrue(observer.read_failure)
            self.assertFalse(observer.stdout_eof)
