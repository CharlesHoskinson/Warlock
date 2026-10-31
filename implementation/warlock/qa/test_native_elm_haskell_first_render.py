"""Development-only controller guards; never imports a native admission or launches GUI."""
import hashlib
import fcntl
import importlib.util
import os
import selectors
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

path = Path(__file__).with_name('native-elm-haskell-first-render.py')
spec = importlib.util.spec_from_file_location('native_first_render_runner', path)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def test_hash_identity_symlink_mode_and_size_refusals(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source'
            source.write_bytes(b'owned source')
            selected = {'path': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
            body, stamp = runner.verified_file(selected, 100)
            self.assertEqual(body, b'owned source')
            self.assertEqual(stamp[4], len(body))
            source.write_bytes(b'changed source')
            with self.assertRaises(runner.Refused):
                runner.verified_file(selected, 100)
            source.write_bytes(body)
            with self.assertRaises(runner.Refused):
                runner.verified_file(selected, 1)
            link = Path(directory) / 'link'
            link.symlink_to(source)
            with self.assertRaises(runner.Refused):
                runner.verified_file({**selected, 'path': str(link)}, 100)
            source.chmod(0o666)
            with self.assertRaises(runner.Refused):
                runner.verified_file(selected, 100)

    def test_null_digest_is_not_an_artifact_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source'
            source.write_bytes(b'not an authority')
            with self.assertRaises(runner.Refused):
                runner.verified_file({'path': str(source), 'sha256': None}, 100)

    def test_metadata_duplicate_nonfinite_and_invalid_utf8(self):
        for body in [b'{"a":1,"a":2}', b'{"a":NaN}', b'\xff']:
            with self.subTest(body=body), self.assertRaises(runner.Refused):
                runner.metadata(body)

    def test_nonzero_process_preserves_both_large_streams(self):
        process = subprocess.Popen([sys.executable, '-B', '-c',
            "import os; os.write(1,b'x'*1500000); os.write(2,b'y'*100000); raise SystemExit(7)"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        buffers = {'stdout': bytearray(), 'stderr': bytearray()}
        try:
            actual = runner.collect_bounded(process, buffers, seconds=5)
            self.assertEqual(process.returncode, 7)
            self.assertEqual(actual, {'stdout': b'x' * 1500000, 'stderr': b'y' * 100000})
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)
            process.stdout.close()
            process.stderr.close()

    def test_timeout_keeps_already_read_evidence(self):
        process = subprocess.Popen([sys.executable, '-B', '-c',
            "import os,time; os.write(1,b'retained-before-timeout'); time.sleep(5)"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        buffers = {'stdout': bytearray(), 'stderr': bytearray()}
        try:
            with self.assertRaises(TimeoutError):
                runner.collect_bounded(process, buffers, seconds=1)
            self.assertEqual(buffers['stdout'], b'retained-before-timeout')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)
            process.stdout.close()
            process.stderr.close()

    def test_output_overflow_is_bounded_and_retained(self):
        process = subprocess.Popen([sys.executable, '-B', '-c',
            "import os; data=b'x'*5000000; offset=0\nwhile offset<len(data): offset+=os.write(1,data[offset:])"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        buffers = {'stdout': bytearray(), 'stderr': bytearray()}
        try:
            with self.assertRaises(runner.Refused):
                runner.collect_bounded(process, buffers, seconds=5)
            self.assertGreater(len(buffers['stdout']), 4194304)
            self.assertLessEqual(len(buffers['stdout']), 4194304 + 65536)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)
            process.stdout.close()
            process.stderr.close()

    def test_lock_file_presence_does_not_prove_a_live_coordinator(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / 'native.lock'
            lock.touch(mode=0o600)
            with self.assertRaises(runner.Refused):
                runner.held_lock_ancestor(lock)

    def test_kernel_lock_owner_must_be_a_live_ancestor(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / 'native.lock'
            fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                code = "import importlib.util,pathlib,sys; p=pathlib.Path(sys.argv[1]); s=importlib.util.spec_from_file_location('runner',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.held_lock_ancestor(pathlib.Path(sys.argv[2])))"
                child = subprocess.run([sys.executable, '-B', '-c', code, str(path), str(lock)],
                                       capture_output=True, timeout=5)
                self.assertEqual(child.returncode, 0, child.stderr.decode(errors='replace'))
                self.assertEqual(child.stdout.strip(), str(os.getpid()).encode())
            finally:
                os.close(fd)

    def test_live_nonancestor_lock_owner_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / 'native.lock'
            code = "import fcntl,os,sys,time; fd=os.open(sys.argv[1],os.O_RDWR|os.O_CREAT,0o600); fcntl.flock(fd,fcntl.LOCK_EX); print('ready',flush=True); time.sleep(5)"
            child = subprocess.Popen([sys.executable, '-B', '-c', code, str(lock)],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(child.stdout, selectors.EVENT_READ)
                    self.assertTrue(selector.select(2), 'lock owner did not become ready')
                    self.assertEqual(child.stdout.readline(), b'ready\n')
                with self.assertRaises(runner.Refused):
                    runner.held_lock_ancestor(lock)
            finally:
                child.terminate()
                child.communicate(timeout=3)

    def test_cgroup_events_require_explicit_unique_known_values(self):
        self.assertFalse(runner.parse_cgroup_events(b'populated 0\nfrozen 0\n')['populated'])
        self.assertTrue(runner.parse_cgroup_events(b'populated 1\nfrozen 0\n')['populated'])
        for raw in [b'', b'frozen 0\n', b'populated 2\nfrozen 0\n',
                    b'populated 0\npopulated 1\nfrozen 0\n',
                    b'populated 0\nfrozen 0\nunknown 0\n', b'\xff', b'x' * 4097]:
            with self.subTest(raw=raw[:30]), self.assertRaises(runner.Refused):
                runner.parse_cgroup_events(raw)

    def test_atomic_report_preserves_baseline_on_replace_failure(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            runner.atomic_report(output, {'passed': False, 'forcedContainment': None})
            original = (output / 'report.json').read_bytes()
            with patch.object(runner.os, 'replace', side_effect=OSError('injected publication failure')):
                with self.assertRaises(OSError):
                    runner.atomic_report(output, {'passed': True})
            self.assertEqual((output / 'report.json').read_bytes(), original)
            runner.atomic_report(output, {'passed': False, 'phase': 'finished'})
            self.assertEqual(runner.metadata((output / 'report.json').read_bytes())['phase'], 'finished')


if __name__ == '__main__':
    unittest.main()
