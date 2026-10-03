import copy
import json
from pathlib import Path
import subprocess
import threading
import time
import unittest
from unittest.mock import patch
from native_desktop import NativeDesktop
from scene_controller import SceneController,key
from scene_manager import SceneManager
from test_scene_controller import Desktop,Transport,rectangle


class GestureDesktop(Desktop):
    def __init__(self):
        super().__init__();self.retire_calls=[];self.capture_windows=[];self.refuse=False
    def retire_gestures(self,members):
        self.retire_calls.append([key(w) for w in members])
        if self.refuse:raise ValueError('capability/member retirement refused')
        for w in self.windows:
            w['at'][0]+=7;w['at'][1]+=9;w['size'][0]+=3;w['pinned']=not w['pinned']
        return [{'identity':list(key(w)),'retired':i==1} for i,w in enumerate(members)]
    def capture_source(self,w,*args):
        self.capture_windows.append(copy.deepcopy(w))
        return super().capture_source(w,*args)


class RetirementTransaction(unittest.TestCase):
    def setUp(self):self.d=GestureDesktop();self.t=Transport();self.c=SceneController(self.d,self.t)
    def tearDown(self):self.c.close()
    def request(self):
        w=self.d.windows[0];return self.c.request('minimize',w['address'],w['stableId'],w['pid'],context='fixture')
    def test_all_retirement_precedes_actual_capture_with_current_geometry_and_pin(self):
        self.request();self.c.workers.shutdown(wait=True)
        self.assertEqual(len(self.d.retire_calls),1);self.assertEqual(self.d.captures,3)
        self.assertEqual([{k:w[k] for k in ('address','stableId','pid','at','size','pinned','mapped','workspace')} for w in self.d.capture_windows],self.d.windows)
        r=self.c.current
        self.assertEqual([s['nativeRect'] for s in r.sources],[rectangle(w) for w in self.d.windows])
        self.assertEqual([w['pinned'] for w in r.profile['postRetirementFamily']],[w['pinned'] for w in self.d.windows])
        self.assertEqual(len(r.profile['gestureRetirementReply']),3)
    def test_refusal_aborts_every_source_and_no_native_commit(self):
        self.d.refuse=True;self.request();self.c.workers.shutdown(wait=True)
        self.assertFalse(self.d.captures);self.assertFalse(self.d.commits)
        self.assertFalse(any(e['command']=='seed' for e in self.t.sent))
        self.assertIn('retirement refused',self.c.history[-1].profile['gestureRetirementFailure'])
    def test_family_replaced_after_retirement_aborts_capture(self):
        original=self.d.retire_gestures
        def replace(members):
            result=original(members)
            self.d.windows[2]['pid']+=1;self.d.native[2]['pid']+=1
            return result
        self.d.retire_gestures=replace;self.request();self.c.workers.shutdown(wait=True)
        self.assertFalse(self.d.captures);self.assertFalse(self.d.commits)
        self.assertIn('family changed',self.c.history[-1].profile['failure'])
    def test_obsolete_worker_after_family_lookup_cannot_retire_newer_gesture(self):
        entered=threading.Event();release=threading.Event()
        initial_fresh=self.c.fresh
        def barrier(record):
            result=initial_fresh(record)
            if record.operation=='restore':entered.set();release.wait(3)
            return result
        self.c.fresh=barrier
        for w in self.d.windows:w['workspace']['name']='special:win-minimized'
        w=self.d.windows[0];self.c.request('restore',w['address'],w['stableId'],w['pid'],context='fixture')
        self.assertTrue(entered.wait(1))
        self.c.request('minimize',w['address'],w['stableId'],w['pid'],context='fixture')
        deadline=time.monotonic()+2
        while time.monotonic()<deadline and self.c.current:time.sleep(.002)
        try:self.assertEqual(len(self.d.retire_calls),1)
        finally:release.set();self.c.workers.shutdown(wait=True)
        self.assertEqual(len(self.d.retire_calls),1)
    def test_family_claim_blocks_older_unknown_peer_before_retirement(self):
        d=self.d;entered=threading.Event();release=threading.Event();created=[]
        class ActorDesktop:
            def __init__(self,number):self.number=number
            def __getattr__(self,name):return getattr(d,name)
            def family(self,*args):
                result=d.family(*args)
                if self.number==1:entered.set();release.wait(3)
                return result
        def factory(number):
            a=ActorDesktop(number);t=Transport();created.append((a,t));return a,t
        m=SceneManager(factory)
        try:
            for w in d.windows:w['workspace']['name']='special:win-minimized'
            w=d.windows[0];m.request('restore',w['address'],w['stableId'],w['pid'],context='fixture')
            self.assertTrue(entered.wait(1));w=d.windows[2]
            m.request('minimize',w['address'],w['stableId'],w['pid'],context='fixture')
            deadline=time.monotonic()+2
            while time.monotonic()<deadline and len(d.retire_calls)<1:time.sleep(.002)
            self.assertEqual(len(d.retire_calls),1)
            release.set()
            for actor in m.actors:actor.controller.workers.shutdown(wait=True)
            self.assertEqual(len(d.retire_calls),1)
        finally:release.set();m.close()


class ActualLuaBatch(unittest.TestCase):
    def setUp(self):
        self.d=Desktop();self.actor=NativeDesktop.__new__(NativeDesktop)
        self.check_output=subprocess.check_output
    def execute(self,prefix):
        def replacement(command,**options):
            self.assertEqual(command[:2],['hyprctl','repl'])
            return self.check_output(['lua','-'],input=prefix+'\n'+command[2],text=True,timeout=1)
        return patch('native_desktop.subprocess.check_output',side_effect=replacement)
    def test_exact_member_calls_once_and_boolean_reply(self):
        prefix='local count=0; hl={plugin={hyprbars={retire_gesture_current=function(a,s) count=count+1; assert(a=="0x"..s); return true,count==2 end}}}'
        with self.execute(prefix):reply=self.actor.retire_gestures(self.d.windows)
        self.assertEqual([r['identity'] for r in reply],[list(key(w)) for w in self.d.windows])
        self.assertEqual([r['retired'] for r in reply],[False,True,False])
    def test_missing_native_capability_has_no_fallback(self):
        with self.execute('hl={plugin={hyprbars={}}}'):
            with self.assertRaises(ValueError) as error:self.actor.retire_gestures(self.d.windows)
        self.assertEqual(error.exception.evidence['error'],'retirement-capability-absent')
    def test_false_member_stops_batch_and_reports_partial_retirement(self):
        prefix='local count=0; hl={plugin={hyprbars={retire_gesture_current=function(a,s) count=count+1; assert(count<=2); return count~=2,true end}}}'
        with self.execute(prefix):
            with self.assertRaises(ValueError) as error:self.actor.retire_gestures(self.d.windows)
        self.assertEqual(error.exception.evidence,{'ok':False,'retired':[True]})
    def test_nonboolean_native_reply_refuses_not_truthiness(self):
        prefix='hl={plugin={hyprbars={retire_gesture_current=function(a,s) return 1,0 end}}}'
        with self.execute(prefix):self.assertRaises(ValueError,self.actor.retire_gestures,self.d.windows)


if __name__=='__main__':unittest.main()
