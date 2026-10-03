import copy
import unittest
import test_scene_manager as fixture
from scene_controller import ids

class ReceiptVisualTests(unittest.TestCase):
    setUp=fixture.RegistryTests.setUp
    tearDown=fixture.RegistryTests.tearDown
    request=fixture.RegistryTests.request
    seeded=fixture.RegistryTests.seeded
    ready=fixture.RegistryTests.ready
    wait=fixture.RegistryTests.wait
    def seed(self):
        self.request();c=self.m.actors[0].controller;r=self.seeded(c)
        return c,r,self.boundaries[0][1]
    def reserve(self,op='restore',index=2):
        w=self.d.windows[index];return self.m.reserve(op,w['address'],w['stableId'],w['pid'])
    def test_retained_retarget_is_queued_at_receipt_before_any_context_or_family_query(self):
        c,old,t=self.seed();calls=[]
        self.boundaries[0][0].family=lambda *args:calls.append(args)
        self.reserve();r=c.current
        self.assertNotEqual(r.token,old.token);self.assertEqual(t.sent[-1]['command'],'retarget')
        self.assertEqual(t.sent[-1]['token'],r.token);self.assertEqual(t.sent[-1]['identities'],ids(old.members))
        self.assertEqual(r.sources,old.sources);self.assertFalse(r.validated);self.assertFalse(calls)
        self.assertFalse(self.ready(c,old));self.assertFalse(self.ready(c,r));self.assertFalse(self.d.commits)
    def test_context_acceptance_reuses_reserved_token_without_second_retarget(self):
        c,old,t=self.seed();p=self.reserve();r=c.current;count=len(t.sent)
        result=self.m.activate(p['receipt'],context='trusted-fixture');self.wait(lambda:r.validated)
        self.assertEqual(result['token'],r.token);self.assertIs(c.current,r)
        self.assertEqual([e['command'] for e in t.sent[count:]],['validate']);self.assertEqual(self.d.captures,3)
    def test_third_receipt_reuses_pixels_before_second_context_without_lookup(self):
        c,old,t=self.seed();second=self.reserve();middle=c.current;third=self.reserve('minimize',0);latest=c.current
        self.assertEqual(latest.sources,old.sources);self.assertEqual(self.d.captures,3)
        self.assertEqual([e['operation'] for e in t.sent if e['command']=='retarget'],['restore','minimize'])
        count=len(t.sent);self.assertTrue(self.m.activate(second['receipt'],context='trusted-fixture')['superseded'])
        self.assertEqual(len(t.sent),count);self.assertIs(c.current,latest);self.assertFalse(self.ready(c,middle))
        self.m.activate(third['receipt'],context='trusted-fixture');self.wait(lambda:latest.validated)
    def test_context_change_cancels_new_provisional_token_without_native_effect(self):
        c,old,t=self.seed();p=self.reserve();r=c.current
        with self.assertRaisesRegex(ValueError,'context changed'):self.m.activate(p['receipt'],context='foreign-output-workspace')
        self.assertIsNone(c.current);self.assertEqual(t.sent[-1]['command'],'cancel');self.assertEqual(t.sent[-1]['token'],r.token)
        self.assertFalse(self.d.commits);self.assertFalse(self.d.destinations);self.assertFalse(r.validated)
    def test_context_pending_reduce_watchdog_cannot_commit_inherited_direction(self):
        c,old,t=self.seed();self.reserve();r=c.current;self.d.reduced_flag=True;self.m.watchdog()
        self.assertIs(c.current,r);self.assertFalse(self.d.commits);self.assertFalse(r.validated)
    def test_transport_failure_before_context_has_no_native_settlement(self):
        c,old,t=self.seed();self.reserve();c.transport_failure('pipe gone')
        self.assertIsNone(c.current);self.assertFalse(self.d.commits);self.assertFalse(self.d.destinations)
    def test_cancelled_before_context_does_not_commit_old_accepted_direction(self):
        c,old,t=self.seed();self.reserve();r=c.current
        self.assertTrue(c.event({'event':'cancelled','token':r.token,'identities':ids(r.members)}))
        self.assertIsNone(c.current);self.assertFalse(self.d.commits)
    def test_queue_failure_keeps_receipt_and_later_fresh_latest_settlement(self):
        c,old,t=self.seed();original=t.send
        def fail(m):
            if m['command']=='retarget':raise RuntimeError('queue failed')
            original(m)
        t.send=fail;p=self.reserve('minimize');r=c.current
        self.assertIn('provisionalQueueFailure',r.profile);self.assertFalse(r.validated);self.assertFalse(self.d.commits)
        self.m.activate(p['receipt'],context='trusted-fixture');self.wait(lambda:c.current is None)
        self.assertEqual([op for op,*_ in self.d.commits],['minimize']*3)
        self.assertTrue(r.validated);self.assertFalse(any(e['token']==r.token and e['command']=='validate' for e in t.sent))

if __name__=='__main__':unittest.main()
