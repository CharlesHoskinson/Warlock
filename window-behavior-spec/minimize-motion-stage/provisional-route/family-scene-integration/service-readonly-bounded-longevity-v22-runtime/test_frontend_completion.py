"""Actual inherited workers expose partial context versus latest cleanup."""
import threading
import unittest
import test_socket_frontend as fixture

class CompletionObservationTests(unittest.TestCase):
    def test_blocked_metadata_reproduces_empty_pending_then_full_inverse(self):
        f=fixture.FrontendTests();f.setUp()
        release=threading.Event()
        try:
            f.d.block=release
            first=f.request();self.assertTrue(f.entered.wait(1));second=f.request(op='restore')
            f.gate.set();self.assertTrue(f.d.started.wait(1))
            f.wait(lambda:not f.m.pending)
            with f.m.lock:
                current=[a.controller.current for a in f.m.actors if a.controller.current]
                self.assertEqual(len(current),1)
                self.assertEqual(current[0].profile['managerReceipt'],second['receipt'])
                self.assertFalse(current[0].validated)
                self.assertFalse(f.d.commits)
                self.assertFalse(any(a.controller.history for a in f.m.actors))
            self.assertFalse(f.latest_completed(second['receipt']))
            release.set();f.wait(lambda:f.latest_completed(second['receipt']))
            self.assertFalse(f.latest_completed(first['receipt']))
            self.assertEqual(len(f.d.commits),3)
            done=f.m.actors[0].controller.history[-1]
            self.assertEqual(done.profile['managerReceipt'],second['receipt'])
            self.assertEqual(done.operation,'restore')
            self.assertTrue(done.profile['nativeEndpointAlreadySatisfied'])
            self.assertFalse(any(t.sent for t in f.transports))
            self.assertTrue(any(h.get('superseded') and h['receipt']==first['receipt'] for h in f.m.ingress_history))
        finally:
            release.set();f.tearDown()
