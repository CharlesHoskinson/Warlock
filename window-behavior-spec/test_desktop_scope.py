#!/usr/bin/env python3
"""Installed desktop ownership and MRU candidate contract."""
import os
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path.home()/'.local/share/hypr-window-controls'))
from window_state import desktop_owner, switcher_candidates, monitor_owner


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runtime = Path(self.temp.name)
        (self.runtime/'hypr-windowctl').mkdir()
        self.windows = [dict(address='0x1',stableId='1',mapped=True,workspace={'name':'1'},focusHistoryID=0),
                        dict(address='0x2',stableId='2',mapped=True,workspace={'name':'2'},focusHistoryID=1),
                        dict(address='0x3',stableId='3',mapped=True,workspace={'name':'special:win-minimized'},focusHistoryID=2),
                        dict(address='0x4',stableId='4',mapped=True,pinned=True,workspace={'name':'2'},focusHistoryID=3),
                        dict(address='0x5',stableId='5',mapped=True,workspace={'name':'special:scratchpad'},focusHistoryID=4)]
        self.saved = self.runtime/'hypr-windowctl/0x3'
        self.saved.write_text('1 0 3\n')

    def addresses(self,scope):
        return [w['address'] for w in switcher_candidates(self.windows,'1',scope,self.runtime)]

    def test_current_all_minimized_and_pinned(self):
        self.assertEqual(self.addresses('current'),['0x1','0x3','0x4'])
        self.assertEqual(self.addresses('all'),['0x1','0x2','0x3','0x4'])

    def test_minimized_identity_reuse_is_excluded(self):
        self.windows[2]['stableId']='reused'
        self.assertEqual(self.addresses('all'),['0x1','0x2','0x4'])
        self.assertEqual(desktop_owner(self.windows[2],self.runtime),('',False))

    def test_minimized_pinned_and_legacy_metadata(self):
        self.saved.write_text('2 1 3\n')
        self.assertIn('0x3',self.addresses('current'))
        self.saved.write_text('1 0\n')
        self.assertEqual(desktop_owner(self.windows[2],self.runtime),('1',False))

    def test_missing_malformed_and_unmapped(self):
        self.saved.write_text('special:evil 0 3\n')
        self.assertNotIn('0x3',self.addresses('all'))
        self.saved.unlink()
        self.assertNotIn('0x3',self.addresses('all'))
        self.windows[0]['mapped']=False
        self.assertNotIn('0x1',self.addresses('current'))

    def test_minimized_monitor_uses_home_workspace(self):
        window=dict(self.windows[2],monitor=0,pid=42)
        monitors=[dict(id=0,name='physical',focused=True),dict(id=7,name='virtual')]
        self.assertEqual(monitor_owner(window,monitors,[dict(name='1',monitorID=7)],self.runtime),7)

    def test_inactive_home_monitor_identity_and_disconnect(self):
        window=dict(self.windows[2],monitor=0,pid=42)
        metadata=self.saved.with_name('0x3.monitor.json')
        metadata.write_text(json.dumps(dict(pid=42,stableId='3',homeWorkspace='1',monitorName='virtual')))
        monitors=[dict(id=0,name='physical',focused=True),dict(id=7,name='virtual')]
        self.assertEqual(monitor_owner(window,monitors,[],self.runtime),7)
        self.assertEqual(monitor_owner(dict(window,pid=43),monitors,[],self.runtime),0)
        self.assertEqual(monitor_owner(window,monitors[:1],[],self.runtime),0)
        # A re-used numeric monitor ID cannot impersonate a named output.
        monitors[1]['name']='different-output'
        self.assertEqual(monitor_owner(window,monitors,[],self.runtime),0)

    def test_workspace_move_overrides_saved_monitor(self):
        window=dict(self.windows[2],monitor=0,pid=42)
        self.saved.with_name('0x3.monitor.json').write_text(json.dumps(dict(pid=42,stableId='3',homeWorkspace='1',monitorName='virtual')))
        monitors=[dict(id=0,name='physical'),dict(id=7,name='virtual')]
        self.assertEqual(monitor_owner(window,monitors,[dict(name='1',monitorID=0)],self.runtime),0)


if __name__=='__main__':unittest.main()
