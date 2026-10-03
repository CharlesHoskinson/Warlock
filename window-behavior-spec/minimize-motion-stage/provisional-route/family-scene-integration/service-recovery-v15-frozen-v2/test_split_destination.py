import copy
import json
from pathlib import Path
import tempfile
import threading
import types
import unittest
from unittest.mock import patch
from native_desktop import NativeDesktop
from native_runtime import PinnedNativeDesktop
from scene_controller import key

class SplitDestination(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        (self.root/'hypr-windowctl').mkdir()
        self.window={'address':'0xabc','stableId':'a1','pid':23}
        self.monitors=[{'name':'owned','id':2,'focused':True}]
        self.workspaces=[{'name':'3','monitorID':2}]
        self.effects=[];self.refreshes=[]
        self.desktop=NativeDesktop.__new__(NativeDesktop)
        self.desktop.production=types.SimpleNamespace(RUNTIME=self.root)
        self.desktop.base=types.SimpleNamespace(monitors=lambda:copy.deepcopy(self.monitors),clients=lambda:[copy.deepcopy(self.window)],ipc=lambda *v:self.refreshes.append(v))
        self.state=self.root/'hypr-windowctl/0xabc';self.state.write_text('3 0 a1\n')
        self.metadata=self.state.with_name('0xabc.monitor.json')
        self.metadata.write_text(json.dumps({'pid':23,'stableId':'a1','homeWorkspace':3,'monitorName':'owned'}))
    def tearDown(self):self.temp.cleanup()
    def plan(self):
        with patch('native_desktop.subprocess.check_output',return_value=json.dumps(self.workspaces)):
            return self.desktop.plan_destination(self.window)
    def apply(self,plan):
        with patch('native_desktop.subprocess.run',side_effect=lambda args,**kwargs:self.effects.append(args)):
            return self.desktop.apply_destination(self.window,plan)
    def test_actual_plan_is_readonly_and_exact_member_bound(self):
        with patch('native_desktop.subprocess.run',side_effect=AssertionError('plan must not focus')):
            plan=self.plan()
        self.assertEqual(plan['identity'],list(key(self.window)));self.assertEqual(plan['destination'],'3')
        self.assertFalse(self.effects or self.refreshes)
    def test_actual_apply_has_identical_focus_commands_without_shell_refresh(self):
        plan=self.plan();self.apply(plan)
        self.assertEqual(self.effects,[['hyprctl','dispatch','hl.dsp.focus({ monitor = "owned" })'],['hyprctl','dispatch','hl.dsp.focus({ workspace = "3" })']])
        self.assertFalse(self.refreshes)
        self.desktop.refresh_destination(self.window,plan);self.assertEqual(self.refreshes,[('motionRefresh',{})])
    def test_destination_fields_replacement_refuses_before_focus(self):
        plan=self.plan();self.state.write_text('4 0 a1\n')
        with self.assertRaisesRegex(ValueError,'destination changed'):self.apply(plan)
        self.assertFalse(self.effects)
    def test_destination_metadata_replacement_refuses_before_focus(self):
        plan=self.plan();self.metadata.write_text('{}')
        with self.assertRaisesRegex(ValueError,'destination changed'):self.apply(plan)
        self.assertFalse(self.effects)
    def test_native_identity_reuse_refuses_before_focus(self):
        plan=self.plan();self.window['pid']+=1
        with self.assertRaisesRegex(ValueError,'identity differs'):self.apply(plan)
        self.assertFalse(self.effects)
    def test_closed_identity_refuses_before_focus(self):
        plan=self.plan();self.desktop.base.clients=lambda:[]
        with self.assertRaisesRegex(ValueError,'identity changed'):self.apply(plan)
        self.assertFalse(self.effects)
    def test_exact_output_fallback_matches_original_planner(self):
        self.workspaces=[];self.metadata.write_text(json.dumps({'pid':23,'stableId':'a1','homeWorkspace':3,'monitorName':'gone'}))
        self.assertEqual(self.plan()['monitor']['name'],'owned')
        self.monitors=[]
        with self.assertRaisesRegex(ValueError,'output unavailable'):self.plan()
    def test_each_pinned_native_phase_checks_selected_session_before_and_after(self):
        self.desktop.__class__=PinnedNativeDesktop
        count=[];self.desktop.session_guard=types.SimpleNamespace(verify=lambda:count.append(True))
        plan=self.plan();self.assertEqual(len(count),2)
        self.apply(plan);self.assertEqual(len(count),4)
        self.desktop.refresh_destination(self.window,plan);self.assertEqual(len(count),6)
    def test_actual_worker_family_witness_cannot_be_overwritten_by_another_worker(self):
        d=NativeDesktop.__new__(NativeDesktop);d.family_query_lock=threading.RLock();d.family_query_local=threading.local()
        d.base=types.SimpleNamespace(family=lambda window,windows,single:([window],window),family_trace=types.SimpleNamespace(evidence=None))
        first={'address':'0xabc','stableId':'a1','pid':23};second={'address':'0xdef','stableId':'b2','pid':24}
        first_sampled=threading.Event();second_sampled=threading.Event();results=[]
        def one():
            d.family(first,[first],True);first_sampled.set();second_sampled.wait(1);results.append(d.family_evidence())
        def two():
            first_sampled.wait(1);d.family(second,[second],True);second_sampled.set()
        a=threading.Thread(target=one);b=threading.Thread(target=two);a.start();b.start();a.join(2);b.join(2)
        self.assertFalse(a.is_alive() or b.is_alive());self.assertEqual(results[0]['members'],[list(key(first))])

if __name__=='__main__':unittest.main()
