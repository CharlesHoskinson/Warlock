import threading
import unittest
import test_scene_manager as fixture

class IngressTests(unittest.TestCase):
    setUp=fixture.RegistryTests.setUp
    tearDown=fixture.RegistryTests.tearDown
    request=fixture.RegistryTests.request
    wait=fixture.RegistryTests.wait
    ready=fixture.RegistryTests.ready
    seeded=fixture.RegistryTests.seeded
    def reserve(self,index=0,operation='restore'):
        w=self.d.windows[index]
        return self.m.reserve(operation,w['address'],w['stableId'],w['pid'])
    def test_reservation_before_context_blocks_old_native_ready_without_waiting_lookup(self):
        self.request();c=self.m.actors[0].controller;old=self.seeded(c)
        pending=self.reserve(2)
        self.assertTrue(pending['contextPending']);self.assertFalse(self.ready(c,old))
        self.assertFalse(self.d.commits)
        current=self.m.activate(pending['receipt'],context='trusted-fixture')
        self.assertTrue(current['accepted']);self.assertEqual(current['actor'],1)
        self.assertTrue(any(e['command']=='retarget' and e['token']==current['token'] for e in self.boundaries[0][1].sent))
    def test_older_context_reply_cannot_supersede_newer_accepted_intent(self):
        self.request();c=self.m.actors[0].controller;self.seeded(c)
        old=self.reserve(0,'restore');new=self.reserve(2,'minimize')
        result=self.m.activate(new['receipt'],context='trusted-fixture');latest=c.current
        count=len(self.boundaries[0][1].sent)
        rejected=self.m.activate(old['receipt'],context='obsolete-context')
        self.assertTrue(rejected['superseded']);self.assertIs(c.current,latest)
        self.assertEqual(len(self.boundaries[0][1].sent),count)
        self.assertEqual(result['receipt'],new['receipt'])
    def test_context_failure_retires_visual_but_cannot_settle_unvalidated_restore(self):
        self.request();c=self.m.actors[0].controller;old=self.seeded(c);self.ready(c,old)
        before=list(self.d.commits);pending=self.reserve(2,'restore')
        self.assertTrue(self.m.fail_ingress(pending['receipt'],'native output disappeared'))
        self.assertIsNone(c.current);self.assertEqual(self.d.commits,before)
        self.assertEqual(self.boundaries[0][1].sent[-1]['command'],'cancel')
        self.assertEqual(self.boundaries[0][1].sent[-1]['token'],old.token)
        self.assertTrue(self.m.ingress_history[-1]['failed'])
    def test_obsolete_context_failure_cannot_cancel_current_visual(self):
        self.request();c=self.m.actors[0].controller;self.seeded(c)
        old=self.reserve(0,'restore');new=self.reserve(2,'minimize')
        self.m.activate(new['receipt'],context='trusted-fixture');latest=c.current
        count=len(self.boundaries[0][1].sent)
        self.assertFalse(self.m.fail_ingress(old['receipt'],'old query failed'))
        self.assertIs(c.current,latest);self.assertEqual(len(self.boundaries[0][1].sent),count)
    def test_context_deadline_is_failure_never_native_completion(self):
        self.request();c=self.m.actors[0].controller;old=self.seeded(c)
        pending=self.reserve(2)
        self.m.pending[pending['receipt']]['receivedNs']-=3000000000
        self.m.watchdog()
        self.assertIsNone(c.current);self.assertFalse(self.d.commits)
        self.assertTrue(self.m.ingress_history[-1]['failed'])
        self.assertIn(old.token,c.retired)

if __name__=='__main__':unittest.main()
