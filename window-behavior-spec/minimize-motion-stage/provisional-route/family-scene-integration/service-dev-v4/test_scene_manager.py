import copy
import threading
import time
import unittest
from scene_manager import SceneManager
from scene_controller import ids,key
from test_scene_controller import Desktop,Transport

class ActorDesktop:
    def __init__(self,shared):self.shared=shared;self.gate=None;self.started=threading.Event()
    def __getattr__(self,name):return getattr(self.shared,name)
    def family(self,*args):
        result=self.shared.family(*args)
        if self.gate:self.started.set();self.gate.wait(3)
        return result

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.d=Desktop();self.boundaries=[]
        def factory(number):
            desktop=ActorDesktop(self.d);transport=Transport();self.boundaries.append((desktop,transport));return desktop,transport
        self.m=SceneManager(factory)
    def tearDown(self):
        for d,t in self.boundaries:
            if d.gate:d.gate.set()
        if self.d.commit_block:self.d.commit_block.set()
        for a in self.m.actors:a.controller.workers.shutdown(wait=True,cancel_futures=True)
    def request(self,index=0,operation='minimize'):
        w=self.d.windows[index]
        return self.m.request(operation,w['address'],w['stableId'],w['pid'],context='trusted-fixture')
    def wait(self,p):
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            if p():return
            time.sleep(.002)
        self.fail('registry worker boundary not reached')
    def ready(self,c,r):
        return c.event({'event':'ready','token':r.token,'identities':ids(r.members),'servicePromoted':True,'sourceDigests':[{k:s[k] for k in ('stableId','pid','digest')} for s in r.sources]})
    def seeded(self,c):self.wait(lambda:c.current and c.current.visual and c.current.validated);return c.current
    def test_known_modal_peer_routes_to_same_actor_and_retires_old_callback(self):
        first=self.request();a=self.m.actors[0].controller
        self.seeded(a)
        self.assertEqual(len(a.current.members),3)
        old=a.current
        result=self.request(2,'restore')
        self.assertEqual(result['actor'],first['actor']);self.assertEqual(len(self.m.actors),1)
        self.assertFalse(self.ready(a,old));self.assertFalse(self.d.commits)
    def test_two_initial_unknown_peers_latest_whole_scope_wins_no_old_destination(self):
        for w in self.d.windows:w['workspace']['name']='special:win-minimized'
        def factory(number):
            desktop=ActorDesktop(self.d);desktop.gate=threading.Event() if number==1 else None
            transport=Transport();self.boundaries.append((desktop,transport));return desktop,transport
        self.m=SceneManager(factory)
        self.request(0,'restore');old=self.m.actors[0].controller;self.assertTrue(self.boundaries[0][0].started.wait(1))
        newest=self.request(2,'minimize');new=self.m.actors[1].controller;r=self.seeded(new)
        self.assertEqual(newest['actor'],2);self.assertEqual(len(r.members),3)
        self.boundaries[0][0].gate.set();self.wait(lambda:old.current is None)
        self.assertFalse(self.d.destinations);self.assertFalse(self.d.commits)
        self.assertTrue(self.ready(new,r));self.assertEqual(len(self.d.commits),3)
        self.assertEqual({member for _,member,_ in self.d.commits},{key(w) for w in self.d.windows})
    def test_newer_still_unvalidated_peer_blocks_old_observed_restore(self):
        for w in self.d.windows:w['workspace']['name']='special:win-minimized'
        def factory(number):
            desktop=ActorDesktop(self.d);desktop.gate=threading.Event()
            transport=Transport();self.boundaries.append((desktop,transport));return desktop,transport
        self.m=SceneManager(factory)
        self.request(0,'restore');old=self.m.actors[0].controller
        self.assertTrue(self.boundaries[0][0].started.wait(1))
        self.request(2,'minimize');new=self.m.actors[1].controller
        self.assertTrue(self.boundaries[1][0].started.wait(1))
        self.boundaries[0][0].gate.set();self.wait(lambda:old.current is None)
        self.assertFalse(self.d.destinations);self.assertFalse(self.d.commits)
        self.assertFalse(self.boundaries[0][1].sent)
        self.boundaries[1][0].gate.set();r=self.seeded(new)
        self.assertTrue(self.ready(new,r));self.assertEqual(len(self.d.commits),3)
    def test_slow_ready_observation_does_not_hold_manager_reservation(self):
        self.request();c=self.m.actors[0].controller;r=self.seeded(c)
        original=c.fresh;blocked=threading.Event();release=threading.Event()
        def fresh(record):
            observation=original(record)
            if record is r:blocked.set();release.wait(3)
            return observation
        c.fresh=fresh
        callback=threading.Thread(target=lambda:self.ready(c,r));callback.start()
        self.assertTrue(blocked.wait(1))
        accepted=[];request=threading.Thread(target=lambda:accepted.append(self.request(2,'restore')));request.start()
        try:
            request.join(.3);self.assertEqual(len(accepted),1)
            self.assertEqual(self.boundaries[0][1].sent[-1]['command'],'retarget')
        finally:release.set();callback.join(1);request.join(1)
        self.assertFalse(self.d.commits)
    def test_unrelated_same_pid_families_have_independent_actors(self):
        foreign=copy.deepcopy(self.d.windows[0]);foreign.update(address='0xdddd',stableId='dddd')
        self.d.windows.append(foreign);self.d.native.append(dict(foreign,parent='',parentStableId='',modal=False))
        first=self.request();a=self.m.actors[0].controller;old=self.seeded(a)
        second=self.request(3);b=self.m.actors[1].controller;new=self.seeded(b)
        self.assertNotEqual(first['actor'],second['actor']);self.assertEqual(len(new.members),1)
        self.assertTrue(self.ready(a,old));self.assertTrue(self.ready(b,new))
        self.assertEqual(len(self.d.commits),4)
    def test_request_receipt_cannot_interleave_native_family_peer_commit(self):
        self.request();a=self.m.actors[0].controller;old=self.seeded(a)
        self.d.commit_block=threading.Event();self.d.started.clear()
        callback=threading.Thread(target=lambda:self.ready(a,old));callback.start();self.assertTrue(self.d.started.wait(1))
        accepted=[];next_request=threading.Thread(target=lambda:accepted.append(self.request(2,'restore')));next_request.start()
        time.sleep(.02);self.assertFalse(accepted)
        self.d.commit_block.set();callback.join(1);next_request.join(1)
        self.assertEqual(len(self.d.commits),3);self.assertEqual(len(accepted),1)
        self.assertEqual(accepted[0]['actor'],1)
    def test_invalid_input_never_constructs_actor_and_shutdown_refuses_requests(self):
        with self.assertRaises(ValueError):self.m.request('minimize','bad','aa01',41,context=1)
        self.assertFalse(self.boundaries);self.m.close()
        with self.assertRaises(RuntimeError):self.request()
    def test_manager_retains_actor_cache_routing_after_native_cleanup(self):
        self.request();a=self.m.actors[0].controller;r=self.seeded(a);self.ready(a,r)
        a.event({'event':'endpoint','token':r.token,'identities':ids(r.members),'sourceDigests':[{k:s[k] for k in ('stableId','pid','digest')} for s in r.sources],'servicePromoted':True})
        a.event({'event':'cancelled','token':r.token,'identities':ids(r.members)})
        self.assertIsNone(a.current)
        result=self.request(2,'restore');self.assertEqual(result['actor'],1);self.assertEqual(len(self.m.actors),1)

if __name__=='__main__':unittest.main()
