#!/usr/bin/env python3
"""Actual candidate reservation/IPC order and race tests, without compositor."""
import copy,threading,time,unittest,subprocess
import test_controller as base
motion=base.motion
from pathlib import Path

class FreezeControllerTests(unittest.TestCase):
    setUp=base.ControllerTests.setUp
    tearDown=base.ControllerTests.tearDown
    request=base.ControllerTests.request
    def running(self):
        token=self.request('minimize');self.c.ready(token);return token
    def block_metadata(self):
        entered=threading.Event();release=threading.Event();real=self.d.clients
        def clients():
            if threading.current_thread().name=='new-intent':
                entered.set();self.assertTrue(release.wait(2))
            return real()
        self.d.clients=clients
        return entered,release
    def test_freeze_precedes_blocked_clients_and_stale_ready_finish(self):
        old=self.running();entered,release=self.block_metadata();result=[]
        worker=threading.Thread(name='new-intent',target=lambda:result.append(self.request('restore')))
        worker.start();self.assertTrue(entered.wait(1))
        try:
            r=self.c.pending['0x10'];self.assertEqual(r['phase'],'validating')
            freezes=[x for x in self.d.calls if x[0]=='motionFreeze'];self.assertEqual(len(freezes),1)
            self.assertEqual(freezes[0][1]['previousToken'],old)
            self.assertLessEqual(r['profile']['freezeAck'],r['profile'].get('clientsStart',time.monotonic()))
            self.assertFalse(self.c.ready(old)['ok']);self.assertFalse(self.c.settle(old)['ok'])
            self.assertEqual(len(self.d.commits()),1)
        finally:release.set();worker.join(2)
        self.assertFalse(worker.is_alive());self.assertEqual(result,[r['token']])
        self.assertLess(r['profile']['freezeAck'],r['profile']['clientsDone'])
        self.assertLess(r['profile']['freezeAck'],r['profile']['familyStart'])
    def test_latest_reservation_wins_while_earlier_validation_blocks(self):
        old=self.running();entered,release=self.block_metadata();result=[]
        worker=threading.Thread(name='new-intent',target=lambda:result.append(self.request('restore')))
        worker.start();self.assertTrue(entered.wait(1));second=self.c.pending['0x10']['token']
        try:
            third=self.request('minimize');self.assertNotEqual(second,third)
            self.assertFalse(self.c.ready(second)['ok']);self.assertFalse(self.c.settle(old)['ok'])
        finally:release.set();worker.join(2)
        self.assertEqual(self.c.pending['0x10']['token'],third)
        self.assertEqual(result,[second]);self.c.ready(third);self.c.settle(third)
        self.assertTrue(all(x[1]=='minimize' for x in self.d.commits()))
    def test_close_reuse_during_validation_never_commits_replacement(self):
        old=self.running();entered,release=self.block_metadata();errors=[]
        def request():
            try:self.request('restore')
            except ValueError as e:errors.append(str(e))
        worker=threading.Thread(name='new-intent',target=request);worker.start();self.assertTrue(entered.wait(1))
        pending=self.c.pending['0x10'];self.d.windows[0]['stableId']='replacement'
        release.set();worker.join(2)
        self.assertEqual(errors,['window identity changed']);self.assertFalse(self.c.pending)
        self.assertFalse(self.c.settle(old)['ok']);self.assertEqual(len(self.d.commits()),1)
        cancelled=[x[1]['token'] for x in self.d.calls if x[0]=='motionCancel']
        self.assertIn(pending['token'],cancelled)
    def test_invalid_captured_identity_does_not_freeze_pending(self):
        token=self.running()
        with self.assertRaises(ValueError):self.c.request('restore','0x10','wrong','100')
        self.assertFalse(any(x[0]=='motionFreeze' for x in self.d.calls));self.assertEqual(self.c.pending['0x10']['token'],token)
    def test_rejected_freeze_falls_back_without_endpoint_reset_begin(self):
        old=self.running();ipc=self.d.ipc
        def reject(method,payload):return False if method=='motionFreeze' else ipc(method,payload)
        self.d.ipc=reject;new=self.request('restore')
        self.assertFalse(self.c.pending)
        self.assertEqual(self.d.commits()[-1][1],'restore')
        self.assertEqual([x[1]['token'] for x in self.d.calls if x[0]=='motionBegin'],[old])
        self.assertFalse(self.c.settle(new)['ok'])
    def test_recovery_cancels_frozen_latest_token_and_commits_exact_identity(self):
        old=self.running();r,previous=self.c.reserve('restore',self.d.windows[0]);self.c.freeze(r,previous)
        new=motion.Controller(self.d,self.root);new.recover()
        self.assertEqual(self.d.commits()[-1][1],'restore')
        self.assertIn(r['token'],[x[1]['token'] for x in self.d.calls if x[0]=='motionCancel'])
    def test_pending_reuse_deadline_and_reduction_have_no_native_authority(self):
        old=self.running();r,previous=self.c.reserve('restore',self.d.windows[0]);self.c.freeze(r,previous)
        self.d.windows[0]['pid']=101;self.d.is_reduced=True;r['deadline']=0
        self.c.watchdog();self.assertFalse(self.c.pending);self.assertEqual(len(self.d.commits()),1)
    def test_older_family_preparation_cannot_supersede_newer_member(self):
        old=self.running();new=self.request('restore')
        result=self.c.prepare('minimize',self.d.windows[0],profile={'received':0})
        self.assertEqual(result,new);self.assertEqual(self.c.pending['0x10']['operation'],'restore')
    def test_all_validated_family_routes_freeze_before_any_target_query(self):
        self.d.windows.append(base.window('0x20','stable20',200))
        self.d.family=lambda w,ws,single=False:(list(ws),ws[-1])
        initial=self.c.request('minimize','0x10','stable10','100')['tokens']
        for token in initial:self.c.ready(token)
        self.d.calls.clear();target=self.d.target
        def guarded(w):
            freezes=[x for x in self.d.calls if x[0]=='motionFreeze']
            self.assertEqual({x[1]['identity'][0] for x in freezes},{'0x10','0x20'})
            return target(w)
        self.d.target=guarded
        result=self.c.request('restore','0x10','stable10','100')['tokens']
        self.assertEqual(len(result),2)
    def test_validation_refreshes_native_rectangle_before_capture(self):
        old=self.running();real=self.d.clients;changed=False
        def clients():
            nonlocal changed
            if not changed:self.d.windows[0]['at']=[93,104];changed=True
            return real()
        self.d.clients=clients;new=self.request('restore');record=self.c.lookup(new)
        self.assertEqual(record['nativeRect']['x'],93);self.assertEqual(record['nativeRect']['y'],104)

    def test_third_intent_during_blocked_validation_retains_actual_png_pixels(self):
        captures=[]
        def capture(w,token):
            path=self.root/(token+'.png');color='red' if not captures else 'blue'
            subprocess.run(['magick','-size','4x6','xc:gold','-fill',color,'-draw','rectangle 1,3 2,4',str(path)],check=True)
            captures.append(token)
            return {'image':str(path),'rect':{'x':78,'y':85,'width':643,'height':381},'whole':True}
        self.d.capture=capture;old=self.running();old_record=copy.deepcopy(self.c.lookup(old));original=Path(old_record['image']).read_bytes()
        entered,release=self.block_metadata();result=[]
        worker=threading.Thread(name='new-intent',target=lambda:result.append(self.request('restore')))
        worker.start();self.assertTrue(entered.wait(1));second=self.c.pending['0x10']['token']
        try:
            self.assertNotIn('image',self.c.pending['0x10'])
            third=self.request('minimize');record=self.c.lookup(third)
            self.assertEqual(Path(record['image']).read_bytes(),original);self.assertEqual(captures,[old])
            self.assertEqual(record['rect'],old_record['rect']);self.assertEqual(record['nativeRect'],old_record['nativeRect']);self.assertTrue(record['wholeWindow'])
        finally:release.set();worker.join(2)
        self.assertEqual(result,[second]);self.assertFalse(self.c.ready(second)['ok'])
    def test_renderer_snapshot_must_be_owned_and_identity_bound(self):
        old=self.running();record=copy.deepcopy(self.c.lookup(old));ipc=self.d.ipc
        alien=self.root.parent/(self.root.name+'-alien.png');alien.write_bytes(b'wrong pixels')
        def forged(method,payload):
            if method=='motionFreeze':return {'accepted':True,'snapshot':{'image':str(alien),'identity':payload['identity'],
                'nativeRect':record['nativeRect'],'rect':record['rect'],'whole':True}}
            return ipc(method,payload)
        self.d.ipc=forged
        try:
            new=self.request('restore');self.assertEqual(Path(self.c.lookup(new)['image']).read_bytes(),Path(record['image']).read_bytes())
            self.assertNotEqual(self.c.lookup(new)['frozenSnapshot']['image'],str(alien))
        finally:alien.unlink()


if __name__=='__main__':unittest.main()
