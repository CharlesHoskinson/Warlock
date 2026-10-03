import copy
import importlib.util
from pathlib import Path
import threading
import time
import types
import unittest
from scene_manager import SceneManager
from scene_controller import ids,key
from test_scene_controller import Desktop,Transport

OLD=Path(__file__).resolve().parent.parent/'service-review-v12'

class SplitDesktop(Desktop):
    def __init__(self):
        super().__init__();self.gate_name=None;self.entered=threading.Event();self.release=threading.Event()
        self.phase_calls=[];self.focus_effects=[];self.refreshes=[];self.retirements=[]
    def phase(self,name):
        self.phase_calls.append(name)
        if name==self.gate_name:
            self.entered.set()
            if not self.release.wait(3):raise TimeoutError('test observation gate')
    def retire_gestures(self,members):
        self.retirements.append([key(w) for w in members])
        return [{'identity':list(key(w)),'retired':False} for w in members]
    def active(self):self.phase('active');return super().active()
    def reduced(self):self.phase('reduced');return super().reduced()
    def plan_destination(self,w):self.phase('plan');return {'identity':key(w)}
    def apply_destination(self,w,plan):
        if plan['identity']!=key(w):raise ValueError('exact destination changed')
        self.focus_effects.append(key(w))
    def refresh_destination(self,w,plan):self.phase('refresh');self.refreshes.append(key(w))
    def select_destination(self,w):
        plan=self.plan_destination(w);self.apply_destination(w,plan);self.refresh_destination(w,plan)

class ResponsivePreparation(unittest.TestCase):
    def setUp(self):
        self.d=SplitDesktop();self.t=Transport();self.snapshots=[]
        self.m=SceneManager(lambda n:(self.d,self.t),persist=lambda:self.snapshots.append(self.m.serial))
        self.c=None
    def tearDown(self):
        self.d.release.set()
        for a in self.m.actors:a.controller.workers.shutdown(wait=True,cancel_futures=True)
    def wait(self,p):
        end=time.monotonic()+2
        while time.monotonic()<end:
            if p():return
            time.sleep(.001)
        self.fail('actual worker phase missing')
    def reserve(self,op):
        w=self.d.windows[0];return self.m.reserve(op,w['address'],w['stableId'],w['pid'])
    def seed(self):
        first=self.reserve('minimize');self.m.activate(first['receipt'],context='fixed')
        self.c=self.m.actors[0].controller
        self.wait(lambda:self.c.current and self.c.current.validated and self.c.current.visual)
        previous=self.c.current
        self.c.event({'event':'ready','token':previous.token,'identities':ids(previous.members),
            'servicePromoted':True,'sourceDigests':[{k:s[k] for k in ('stableId','pid','digest')} for s in previous.sources]})
        return previous
    def exercise(self,phase,*,old_source=False,initial=False,post_active=False):
        previous=None if initial else self.seed()
        if initial:
            result=self.reserve('activate');self.c=self.m.actors[0].controller
        else:result=self.reserve('restore')
        if old_source:
            spec=importlib.util.spec_from_file_location('frozen_v12_controller_counterexample',OLD/'scene_controller.py')
            module=importlib.util.module_from_spec(spec);__import__('sys').modules[spec.name]=module;spec.loader.exec_module(module)
            self.c.prepare=types.MethodType(module.SceneController.prepare,self.c)
        calls=0;fresh=self.c.fresh
        if phase=='post-fresh':
            def gated(record):
                nonlocal calls
                observed=fresh(record);calls+=1
                if calls==2:self.d.phase('post-fresh')
                return observed
            self.c.fresh=gated
        if post_active:
            active=self.d.active;active_calls=0
            def gated_active():
                nonlocal active_calls
                active_calls+=1
                if active_calls==1:return Desktop.active(self.d)
                return active()
            self.d.active=gated_active
        self.d.gate_name=phase
        self.m.activate(result['receipt'],context='fixed');blocked_record=self.c.current
        self.assertTrue(self.d.entered.wait(1))
        before_effects=len(self.d.focus_effects);before_captures=self.d.captures
        answers=[];errors=[];completed=threading.Event()
        def request():
            try:answers.append(self.reserve('minimize'))
            except Exception as e:errors.append(e)
            finally:completed.set()
        thread=threading.Thread(target=request);thread.start()
        try:
            if old_source:self.assertFalse(completed.wait(.15),'frozen shared-lock counterexample unexpectedly did not block')
            else:
                self.assertTrue(completed.wait(.15),'new reservation waited for blocked slow observation')
                self.assertFalse(errors);self.assertEqual(len(answers),1)
                self.assertEqual(self.snapshots[-1],answers[0]['receipt'])
                if previous is not None:
                    self.assertEqual(self.t.sent[-1]['command'],'retarget')
                    self.assertEqual(self.t.sent[-1]['token'],self.c.current.token)
                    self.assertEqual(self.c.current.sources,previous.sources)
                self.assertFalse(self.c.current.validated)
        finally:self.d.release.set();thread.join(2);self.c.workers.shutdown(wait=True,cancel_futures=False)
        self.assertFalse(thread.is_alive());self.assertFalse(errors)
        if not old_source:
            self.assertFalse(any(e['command']=='validate' and e['token']==blocked_record.token for e in self.t.sent))
            self.assertEqual(len(self.d.focus_effects),before_effects)
            self.assertEqual(self.d.captures,before_captures)
            self.assertFalse(blocked_record.validated)
    def test_blocked_post_retirement_fresh_does_not_block_retained_retarget(self):self.exercise('post-fresh')
    def test_blocked_destination_plan_does_not_block_retained_retarget(self):self.exercise('plan')
    def test_blocked_destination_refresh_does_not_block_retained_retarget(self):self.exercise('refresh')
    def test_blocked_reduced_observation_does_not_block_retained_retarget(self):self.exercise('reduced')
    def test_blocked_initial_active_observation_does_not_block_reservation(self):self.exercise('active',initial=True)
    def test_blocked_post_retirement_active_does_not_block_reservation(self):self.exercise('active',initial=True,post_active=True)
    def test_frozen_v12_post_retirement_fresh_actual_method_blocks_receipt(self):self.exercise('post-fresh',old_source=True)
    def test_frozen_v12_destination_refresh_actual_method_blocks_receipt(self):self.exercise('refresh',old_source=True)
    def test_frozen_v12_reduced_actual_method_blocks_receipt(self):self.exercise('reduced',old_source=True)
    def test_frozen_v12_post_retirement_active_actual_method_blocks_receipt(self):self.exercise('active',old_source=True,initial=True,post_active=True)
    def test_native_family_commit_still_excludes_receipt_replacement(self):
        self.seed();record=self.c.current
        self.d.commit_block=threading.Event();self.d.started.clear()
        done=threading.Event();answers=[]
        def commit_batch():
            with self.c.lock:self.c.commit_members(record,'minimize','atomic fixture')
        commit=threading.Thread(target=commit_batch)
        commit.start();self.assertTrue(self.d.started.wait(1))
        def reserve():answers.append(self.reserve('restore'));done.set()
        request=threading.Thread(target=reserve);request.start()
        try:self.assertFalse(done.wait(.05));self.assertIs(self.c.current,record)
        finally:self.d.commit_block.set();commit.join(2);request.join(2)
        self.assertTrue(done.is_set());self.assertEqual(len(answers),1)
    def test_current_complete_split_destination_preserves_each_member_refresh(self):
        self.seed();result=self.reserve('restore');self.m.activate(result['receipt'],context='fixed')
        self.wait(lambda:self.c.current.validated)
        self.assertEqual(self.d.focus_effects,[key(w) for w in self.d.windows])
        self.assertEqual(self.d.refreshes,[key(w) for w in self.d.windows]);self.assertEqual(self.d.captures,3)
        self.assertTrue(any(e['command']=='validate' and e['token']==self.c.current.token for e in self.t.sent))
    def test_old_error_after_blocked_read_cannot_reject_latest_record(self):
        self.seed();result=self.reserve('restore');original=self.d.plan_destination
        def error(w):original(w);raise ValueError('old read failed')
        self.d.plan_destination=error;self.d.gate_name='plan';self.m.activate(result['receipt'],context='fixed')
        self.assertTrue(self.d.entered.wait(1));new=self.reserve('minimize');record=self.c.current
        self.d.release.set();self.c.workers.shutdown(wait=True)
        self.assertEqual(record.profile['managerReceipt'],new['receipt']);self.assertNotIn('failure',record.profile)
        self.assertIs(self.c.current,record);self.assertFalse(record.validated)

if __name__=='__main__':unittest.main()
