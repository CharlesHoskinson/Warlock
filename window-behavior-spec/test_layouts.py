#!/usr/bin/env python3
"""Test installed menu host behind mocked compositor and Quickshell transport."""
import importlib.machinery
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

menu = importlib.machinery.SourceFileLoader('qa_menu', str(Path.home() / '.local/bin/hypr-window-menu')).load_module()

class MenuTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.windows = [{'address':'0x111','monitor':0,'title':'Owner','pinned':False,'fullscreen':0},
                        {'address':'0x222','monitor':0,'title':'Later focus','pinned':False,'fullscreen':0}]
        self.monitor = {'id':0,'name':'TEST','x':-1000,'y':100,'width':1280,'height':1000,'scale':1}
        self.cursor = {'x':-500,'y':300}
        self.pick = ''
        self.calls = []
        def ctl(*args):
            self.calls.append(('ctl', args))
            if args[0] == 'clients': return json.dumps(self.windows)
            if args[0] == 'monitors': return json.dumps([self.monitor])
            if args[0] == 'cursorpos': return json.dumps(self.cursor)
            if args[0] == 'activewindow': return json.dumps(self.windows[1])
            return ''
        def run(argv, **kwargs):
            self.calls.append(('run', argv))
            return SimpleNamespace(returncode=0, stdout=self.pick)
        for name, value in [('HOME',Path(self.tmp.name)),('ctl',ctl),
                            ('subprocess',SimpleNamespace(run=run, DEVNULL=-3))]:
            handle=patch.object(menu,name,value); handle.start(); self.addCleanup(handle.stop)

    def invoke(self, *args):
        with patch.object(sys, 'argv', ['hypr-window-menu', *args]): menu.main()

    def request(self):
        return json.loads(next(args[-1] for kind,args in self.calls if kind=='run' and 'open' in args))

    def test_width_threshold_in_logical_units(self):
        for physical, scale, extended in [(1279,1,False),(1280,1,True),(2558,2,False),(2560,2,True),(1920,1.5,True)]:
            self.calls.clear(); self.monitor.update(width=physical,scale=scale)
            self.invoke('layouts','0x111')
            self.assertEqual(self.request()['extendedLayouts'], extended)
            self.assertEqual(self.request()['address'], '0x111')
            self.assertFalse(any(kind=='ctl' and args[0]=='activewindow' for kind,args in self.calls))

    def test_third_and_asymmetric_actions_keep_owner(self):
        for zone in ['third_left','third_center','third_right','two_thirds_left','two_thirds_right']:
            self.calls.clear(); self.invoke('act','0x111','zone:'+zone)
            self.assertIn(('ctl',('eval',f'hypr_snap_zone("{zone}", "0x111")')),self.calls)
            self.assertFalse(any(kind=='ctl' and args[0]=='activewindow' for kind,args in self.calls))

    def test_snapbar_pick_and_release_keep_owner(self):
        self.pick='third_center\n'; self.invoke('snapbar-release','0x111')
        self.assertIn(('ctl',('eval','hypr_snap_zone("third_center","0x111")')), self.calls)
        picked=next(args for kind,args in self.calls if kind=='run' and 'pick' in args)
        self.assertEqual(picked[-2:], ['500','200'])
        self.assertTrue(any(kind=='run' and 'hide' in args for kind,args in self.calls))

    def test_snapbar_blank_pick_only_snaps_at_edge(self):
        self.invoke('snapbar-release','0x111')
        self.assertIn(('ctl',('eval','hypr_snap_discard_release("0x111")')),self.calls)
        self.assertFalse(any(kind=='ctl' and args[0]=='eval' and 'hypr_snap_zone' in args[1] for kind,args in self.calls))
        self.calls.clear(); self.cursor={'x':-1000,'y':110}
        self.invoke('snapbar-release','0x111')
        self.assertIn(('ctl',('eval','hypr_snap_zone("top_left","0x111")')), self.calls)

    def test_switcher_click_passes_captured_identity(self):
        self.invoke('switcher-restore',json.dumps({'address':'0x111','pid':123,'stableId':'original'}))
        call=next(args for kind,args in self.calls if kind=='run')
        self.assertEqual(call[-4:],['restore','0x111','original','123'])

if __name__=='__main__': unittest.main()
