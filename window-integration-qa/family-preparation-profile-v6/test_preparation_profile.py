import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import threading
import unittest

from preparation_profile import BoundaryProfile


def leaf(value):
    return value


def nested(value):
    return leaf(value)


def raise_exact(error):
    raise error


def held(ready, release):
    ready.set()
    release.wait(2)
    return leaf(19)


class FaultingProfile(BoundaryProfile):
    def _details(self, frame):
        raise OSError('actual observer callback failure')


class ProfileTests(unittest.TestCase):
    def sources(self, symbols=('leaf', 'nested', 'raise_exact', 'held')):
        p = Path(__file__).resolve()
        return {str(p): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                         'mode': stat.S_IMODE(p.stat().st_mode), 'symbols': list(symbols)}}

    def saved(self, profile):
        profile.stop()
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'trace.json'
            result = profile.save(p)
            self.assertEqual(json.loads(p.read_text()), result)
            self.assertEqual(stat.S_IMODE(p.stat().st_mode), 0o600)
            return result

    def test_real_nested_calls_keep_result_and_code_identity(self):
        code = leaf.__code__
        value = object()
        p = BoundaryProfile(self.sources()).install()
        self.assertIs(nested(value), value)
        row = self.saved(p)
        self.assertTrue(row['traceComplete'])
        self.assertIs(leaf.__code__, code)
        self.assertEqual([e['event'] for e in row['events']], ['call', 'call', 'return', 'return'])
        self.assertEqual(row['events'][1]['parent'], row['events'][0]['id'])
        self.assertFalse(row['nativeAuthority'])

    def test_original_exception_identity_preserved_without_success_claim(self):
        error = RuntimeError('same exact exception')
        p = BoundaryProfile(self.sources()).install()
        try:
            raise_exact(error)
        except RuntimeError as actual:
            self.assertIs(actual, error)
        row = self.saved(p)
        self.assertTrue(row['traceComplete'])
        self.assertFalse(row['returnEventProvesSuccess'])
        self.assertFalse(row['events'][-1]['successClaimed'])

    def test_real_concurrent_workers_have_distinct_thread_spans(self):
        p = BoundaryProfile(self.sources()).install()
        ready = [threading.Event(), threading.Event()]
        release = threading.Event()
        workers = [threading.Thread(target=held, args=(r, release)) for r in ready]
        for w in workers: w.start()
        for r in ready: self.assertTrue(r.wait(2))
        release.set()
        for w in workers: w.join(2); self.assertFalse(w.is_alive())
        row = self.saved(p)
        self.assertTrue(row['traceComplete'])
        self.assertEqual(len({e['thread'] for e in row['events']}), 2)

    def test_existing_current_profile_refuses_without_replacement(self):
        hook = lambda *a: None
        sys.setprofile(hook)
        try:
            with self.assertRaises(RuntimeError): BoundaryProfile(self.sources()).install()
            self.assertIs(sys.getprofile(), hook)
        finally:
            sys.setprofile(None)

    def test_existing_global_thread_profile_refuses_without_replacement(self):
        hook = lambda *a: None
        threading.setprofile(hook)
        try:
            with self.assertRaises(RuntimeError): BoundaryProfile(self.sources()).install()
            self.assertIs(threading.getprofile(), hook)
        finally:
            threading.setprofile(None)

    def test_actual_overflow_keeps_result_and_reports_incomplete(self):
        p = BoundaryProfile(self.sources(), max_events=2).install()
        self.assertEqual(leaf(1), 1)
        self.assertEqual(leaf(2), 2)
        row = self.saved(p)
        self.assertFalse(row['traceComplete'])
        self.assertEqual(len(row['events']), 2)
        self.assertIn('capacity', row['errors'][0])

    def test_callback_failure_is_latched_without_changing_return(self):
        p = FaultingProfile(self.sources()).install()
        self.assertEqual(leaf(4), 4)
        row = self.saved(p)
        self.assertFalse(row['traceComplete'])
        self.assertIn('actual observer callback failure', row['errors'][0])

    def test_live_span_at_stop_stays_incomplete_after_late_return(self):
        p = BoundaryProfile(self.sources()).install()
        ready, release = threading.Event(), threading.Event()
        worker = threading.Thread(target=held, args=(ready, release)); worker.start()
        self.assertTrue(ready.wait(2))
        p.stop(); release.set(); worker.join(2)
        with tempfile.TemporaryDirectory() as folder:
            row = p.save(Path(folder) / 'trace.json')
        self.assertFalse(row['traceComplete'])
        self.assertEqual(len(row['openSpans']), 1)

    def test_actual_source_replacement_cannot_claim_complete(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.py'; path.write_text('def fn(): return 3\n'); path.chmod(0o600)
            env = {}; exec(compile(path.read_text(), str(path), 'exec'), env)
            p = BoundaryProfile({str(path): {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'mode': 0o600, 'symbols': ['fn']}}).install()
            self.assertEqual(env['fn'](), 3)
            path.write_text('def fn(): return 7\n')
            row = self.saved(p)
        self.assertFalse(row['sourceStable'])
        self.assertFalse(row['traceComplete'])

    def test_exclusive_evidence_never_overwrites_prior_bytes(self):
        p = BoundaryProfile(self.sources()).install(); leaf(1); p.stop()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'trace.json'; path.write_bytes(b'original')
            with self.assertRaises(FileExistsError): p.save(path)
            self.assertEqual(path.read_bytes(), b'original')


if __name__ == '__main__':
    unittest.main()
