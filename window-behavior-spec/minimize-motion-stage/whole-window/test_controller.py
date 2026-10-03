#!/usr/bin/env python3
"""Offline actual-controller tests. No compositor, shell or desktop mutations."""
import copy
import os
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
HELPERS=Path(os.getenv('MOTION_HELPER_DIR',str(HERE)))
loader=importlib.machinery.SourceFileLoader('motion',str(HELPERS/'hypr-window-motion'))
spec=importlib.util.spec_from_loader(loader.name,loader)
motion=importlib.util.module_from_spec(spec)
loader.exec_module(motion)


def window(address='0x10',identity='stable10',pid=100):
    return {'address':address,'stableId':identity,'pid':pid,'mapped':True,
            'at':[79,88],'size':[641,377],'pinned':True,'workspace':{'name':'2'}}


class Desktop:
    def __init__(self,root):
        self.windows=[window()]
        self.calls=[]
        self.root=root
        self.is_reduced=False
        self.visible=True
        self.capture_fails=False
        self.reject_begin=False
        self.capture_hook=None
        self.rectangles={w['address']:copy.deepcopy((w['at'],w['size'])) for w in self.windows}
    def clients(self):return copy.deepcopy(self.windows)
    def active(self):return '0x10'
    def source_screen(self,w,previous=None):return {'name':'DP-1','x':0,'y':0,'width':1920,'height':1080,'scale':1}
    def select_destination(self,w):
        self.calls.append(('select_destination',motion.key(w)))
        return self.source_screen(w)
    def reduced(self):return self.is_reduced
    def family(self,w,windows,single=False):return [w],w
    def target(self,w):return {'visible':self.visible,'screenName':'DP-1','monitorX':0,'monitorY':0,
                              'rect':{'x':951,'y':10,'width':19,'height':19}}
    def capture(self,w,token):
        if self.capture_hook:self.capture_hook()
        if self.capture_fails:raise ValueError('capture failure')
        path=self.root/(token+'.png');path.write_bytes(b'fake-image');return str(path)
    def ipc(self,method,payload):
        self.calls.append((method,copy.deepcopy(payload)))
        return not (self.reject_begin and method=='motionBegin')
    def commit(self,op,w,preview_ready=False):
        current=next((x for x in self.windows if motion.key(x)==motion.key(w)),None)
        if not current:raise ValueError('identity changed')
        self.calls.append(('commit',op,motion.key(w),preview_ready))
        current['workspace']['name']='special:win-minimized' if op=='minimize' else '2'
        # Native geometry and pin are preserved by the core, asserted separately.
    def commits(self):return [c for c in self.calls if c[0]=='commit']


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.d=Desktop(self.root)
        self.c=motion.Controller(self.d,self.root)
    def tearDown(self):self.temp.cleanup()
    def request(self,op):return self.c.request(op,'0x10','stable10','100')['tokens'][0]
    def test_minimize_waits_for_ready_and_restore_waits_for_endpoint(self):
        before=copy.deepcopy(self.d.windows[0])
        first=self.request('minimize')
        self.assertEqual(self.d.commits(),[])
        self.assertTrue(self.c.ready(first)['ok'])
        self.assertEqual(self.d.commits()[-1][1],'minimize')
        self.c.settle(first)
        second=self.request('restore');self.c.ready(second)
        self.assertEqual(self.d.windows[0]['workspace']['name'],'special:win-minimized')
        self.c.settle(second)
        for field in ('at','size','pid','stableId','pinned'):
            self.assertEqual(self.d.windows[0][field],before[field])
        self.assertEqual(self.d.windows[0]['workspace']['name'],'2')
    def test_reverse_and_stale_completion_are_safe(self):
        first=self.request('minimize');self.c.ready(first)
        second=self.request('toggle')
        self.assertEqual(self.c.pending['0x10']['operation'],'restore')
        n=len(self.d.commits())
        self.assertFalse(self.c.settle(first)['ok'])
        self.assertFalse(self.c.ready(first)['ok'])
        self.assertEqual(len(self.d.commits()),n)
        self.c.ready(second);self.c.settle(second)
        self.assertEqual(self.d.commits()[-1][1],'restore')
        self.assertFalse(list(self.root.glob('*.png')))
    def test_latest_request_wins_during_capture(self):
        barrier=threading.Event();release=threading.Event()
        def hook():
            if not barrier.is_set():barrier.set();self.assertTrue(release.wait(2))
        self.d.capture_hook=hook
        result=[]
        thread=threading.Thread(target=lambda:result.append(self.request('minimize')))
        thread.start();self.assertTrue(barrier.wait(2))
        second=self.request('restore')
        release.set();thread.join(2);self.assertFalse(thread.is_alive())
        self.assertEqual(self.c.pending['0x10']['token'],second)
        self.assertFalse(self.c.ready(result[0])['ok'])
        self.c.ready(second);self.c.settle(second)
        self.assertTrue(all(c[1]=='restore' for c in self.d.commits()))
    def test_address_reuse_rejects_old_capture_and_callbacks(self):
        first=self.request('minimize')
        self.d.windows=[window(identity='stable-reuse',pid=200)]
        self.c.ready(first);self.c.settle(first)
        self.assertEqual(self.d.commits(),[])
        with self.assertRaises(ValueError):self.request('restore')
    def test_same_pid_different_stable_identity_cannot_commit(self):
        first=self.request('minimize')
        self.d.windows[0]['stableId']='samepid-reuse'
        self.c.settle(first)
        self.assertEqual(self.d.commits(),[])
    def test_same_identity_different_pid_cannot_commit(self):
        first=self.request('minimize')
        self.d.windows[0]['pid']=101
        self.c.settle(first)
        self.assertEqual(self.d.commits(),[])
    def test_capture_failure_commits_intent_without_overlay(self):
        self.d.capture_fails=True
        self.request('minimize')
        self.assertEqual(self.d.commits()[-1][1],'minimize')
        self.assertFalse(self.c.pending)
        self.assertFalse(any(c[0]=='motionBegin' for c in self.d.calls))
    def test_hidden_target_commits_without_capture_or_overlay(self):
        self.d.visible=False
        self.request('minimize')
        self.assertFalse(self.c.pending)
        self.assertFalse(list(self.root.glob('*.png')))
        self.assertEqual(self.d.commits()[-1][1],'minimize')
    def test_renderer_rejection_cleans_snapshot(self):
        self.d.reject_begin=True
        self.request('minimize')
        self.assertFalse(self.c.pending)
        self.assertFalse(list(self.root.glob('*.png')))
        self.assertEqual(self.d.commits()[-1][1],'minimize')
    def test_reduction_during_restore_commits_latest_intent(self):
        first=self.request('minimize');self.c.ready(first)
        second=self.request('restore');self.c.ready(second)
        self.d.is_reduced=True;self.c.watchdog()
        self.assertEqual(self.d.commits()[-1][1],'restore')
        self.assertFalse(self.c.pending)
        self.assertFalse(self.c.settle(second)['ok'])
    def test_already_reduced_has_no_snapshot(self):
        self.d.is_reduced=True;self.request('minimize')
        self.assertFalse(self.c.pending)
        self.assertFalse(list(self.root.glob('*.png')))
    def test_shell_loss_watchdog_settles_current_request(self):
        first=self.request('minimize');self.c.ready(first)
        second=self.request('restore')
        self.c.pending['0x10']['deadline']=0
        self.c.watchdog()
        self.assertEqual(self.d.commits()[-1][1],'restore')
        self.assertFalse(self.c.pending)
        self.assertFalse(self.c.settle(first)['ok'])
        self.assertFalse(self.c.settle(second)['ok'])
    def test_service_restart_recovers_pending_intent_by_identity(self):
        first=self.request('minimize');self.c.ready(first)
        self.request('restore')
        recovered=motion.Controller(self.d,self.root);recovered.recover()
        self.assertEqual(self.d.commits()[-1][1],'restore')
        self.assertEqual((self.root/'pending.json').read_text(),'[]')
    def test_restart_skips_reused_address(self):
        self.request('minimize')
        self.d.windows=[window(identity='reused',pid=102)]
        motion.Controller(self.d,self.root).recover()
        self.assertEqual(self.d.commits(),[])
    def test_visible_window_focus_does_not_fly_from_taskbar(self):
        self.request('restore')
        self.assertFalse(self.c.pending)
        self.assertEqual(self.d.commits()[-1][1],'restore')
        self.assertFalse(any(c[0]=='motionBegin' for c in self.d.calls))
    def test_two_windows_have_independent_tokens(self):
        other=window('0x20','stable20',200);self.d.windows.append(other)
        first=self.request('minimize')
        second=self.c.request('minimize','0x20','stable20','200')['tokens'][0]
        self.c.ready(first);self.c.ready(second);self.c.settle(first)
        self.assertIn('0x20',self.c.pending)
        self.assertNotIn('0x10',self.c.pending)
        self.c.settle(second)
    def test_rapid_activate_alternates_current_intent_before_native_commit(self):
        one=self.request('activate')
        two=self.request('activate')
        three=self.request('activate')
        self.assertEqual(self.c.pending['0x10']['operation'],'minimize')
        self.assertFalse(self.c.ready(one)['ok']);self.assertFalse(self.c.ready(two)['ok'])
        self.c.ready(three);self.c.settle(three)
        self.assertEqual(self.d.commits()[-1][1],'minimize')
    def test_inactive_visible_activate_only_raises(self):
        self.d.active=lambda:'0xother'
        self.request('activate')
        self.assertFalse(self.c.pending)
        self.assertEqual(self.d.commits()[-1][1],'restore')
    def test_modal_family_out_of_order_endpoints_focus_modal_last(self):
        child=window('0x20','stable20',200)
        self.d.windows.append(child)
        for w in self.d.windows:w['workspace']['name']='special:win-minimized'
        self.d.family=lambda w,windows,single=False:(windows,windows[1])
        tokens=self.c.request('restore','0x10','stable10','100')['tokens']
        for token in tokens:self.c.ready(token)
        self.c.settle(tokens[1]);self.c.settle(tokens[0])
        self.assertEqual(self.d.commits()[-1][2],motion.key(child))
        self.assertTrue(all(w['workspace']['name']=='2' for w in self.d.windows))
    def test_new_minimize_supersedes_old_family_focus(self):
        child=window('0x20','stable20',200)
        self.d.windows.append(child)
        for w in self.d.windows:w['workspace']['name']='special:win-minimized'
        self.d.family=lambda w,windows,single=False:(windows,windows[1])
        tokens=self.c.request('restore','0x10','stable10','100')['tokens']
        for token in tokens:self.c.ready(token)
        self.c.settle(tokens[1])
        latest=self.c.request('minimize','0x10','stable10','100')['tokens']
        for token in latest:self.c.ready(token);self.c.settle(token)
        self.assertFalse(self.c.settle(tokens[0])['ok'])
        self.assertTrue(all(w['workspace']['name']=='special:win-minimized' for w in self.d.windows))
        self.assertEqual(self.d.commits()[-1][1],'minimize')
    def test_permanent_core_failure_clears_pending_and_reports_error(self):
        token=self.request('minimize')
        def fail(*args):raise OSError('permanent native failure')
        self.d.commit=fail
        result=self.c.ready(token)
        self.assertFalse(result['ok']);self.assertIn('permanent native failure',result['error'])
        self.assertFalse(self.c.pending);self.assertIn(token,self.c.results)
        self.c.watchdog();self.assertFalse(self.c.pending)
    def test_restore_core_failure_at_endpoint_clears_pending(self):
        first=self.request('minimize');self.c.ready(first);self.c.settle(first)
        token=self.request('restore');self.c.ready(token)
        def fail(*args):raise OSError('restore failed')
        self.d.commit=fail
        self.assertFalse(self.c.settle(token)['ok']);self.assertFalse(self.c.pending)
    def test_foreign_destination_selected_before_expansion_begin(self):
        first=self.request('minimize');self.c.ready(first);self.c.settle(first)
        self.d.calls=[]
        self.request('restore')
        names=[c[0] for c in self.d.calls]
        self.assertLess(names.index('select_destination'),names.index('motionBegin'))
        self.assertEqual(self.d.windows[0]['workspace']['name'],'special:win-minimized')
    def test_cross_display_route_uses_immediate_safe_fallback(self):
        self.d.target=lambda w:{'visible':True,'screenName':'DP-OTHER','rect':{'x':1990,'y':10,'width':19,'height':19}}
        self.request('minimize')
        self.assertFalse(self.c.pending);self.assertFalse(any(c[0]=='motionBegin' for c in self.d.calls))
        self.assertEqual(self.d.commits()[-1][1],'minimize')
    def test_failed_reversal_cancels_previous_visual(self):
        first=self.request('minimize');self.c.ready(first)
        Path(self.c.pending['0x10']['image']).unlink()
        self.d.capture_fails=True
        second=self.request('restore')
        cancels=[c[1]['token'] for c in self.d.calls if c[0]=='motionCancel']
        self.assertIn(first,cancels)
        self.assertFalse(self.c.pending);self.assertEqual(self.d.commits()[-1][1],'restore')
    def test_min_restore_min_retargets_while_native_stays_minimized(self):
        first=self.request('minimize');self.c.ready(first)
        second=self.request('restore');self.c.ready(second)
        third=self.request('minimize')
        self.assertEqual(self.c.pending['0x10']['token'],third)
        self.assertFalse(self.c.settle(second)['ok'])
        self.c.ready(third);self.c.settle(third)
        self.assertEqual(self.d.windows[0]['workspace']['name'],'special:win-minimized')
    def test_active_reversal_reuses_same_identity_snapshot_without_recapture(self):
        first=self.request('minimize');self.c.ready(first)
        old=self.c.pending['0x10']['image']
        self.d.capture_fails=True
        second=self.request('restore')
        new=self.c.pending['0x10']['image']
        self.assertNotEqual(old,new);self.assertEqual(Path(old).read_bytes(),Path(new).read_bytes())
        self.assertEqual(self.c.pending['0x10']['phase'],'loading')
        self.c.ready(second);self.c.settle(second)
        self.assertEqual(self.d.commits()[-1][1],'restore')
    def test_snapshot_route_targets_actual_icon_and_native_rect(self):
        self.request('minimize')
        record=self.c.pending['0x10']
        self.assertEqual(record['rect'],{'x':79,'y':88,'width':641,'height':377})
        self.assertEqual(record['target']['rect'],{'x':951,'y':10,'width':19,'height':19})


if __name__=='__main__':unittest.main()
