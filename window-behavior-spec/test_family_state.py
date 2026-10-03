#!/usr/bin/env python3
"""Identity and family topology QA for installed shared state functions."""
import json, sys, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path.home()/'.local/share/hypr-window-controls'))
from window_state import enrich_families, family_root, family_members, family_focus, switcher_candidates

def window(address, parent='', parent_id='', modal=False, identity=None, rank=0):
    return dict(address=address,stableId=identity or address,pid=10,parent=parent,parentStableId=parent_id,modal=modal,focusHistoryID=rank,mapped=True,workspace={'name':'1'})

class FamilyTests(unittest.TestCase):
    def setUp(self):
        self.owner=window('0xa');self.child=window('0xb','0xa','0xa',True,rank=1);self.peer=window('0xc');self.windows=[self.owner,self.child,self.peer]
    def test_independent_same_process_not_family(self):
        self.assertEqual([w['address'] for w in family_members(self.child,self.windows)],['0xa','0xb'])
    def test_modal_nested_focus(self):
        nested=window('0xd','0xb','0xb',True)
        self.assertEqual(family_focus(self.owner,self.windows+[nested])['address'],'0xd')
    def test_nonmodal_transient_keeps_focus(self):
        self.child['modal']=False
        self.assertIs(family_focus(self.owner,self.windows),self.owner)
        self.assertEqual(len(family_members(self.owner,self.windows)),2)
    def test_reused_parent_not_attached(self):
        self.owner['stableId']='new'
        self.assertIs(family_root(self.child,self.windows),self.child)
        self.assertIs(family_focus(self.owner,self.windows),self.owner)
    def test_snapshot_identity_guard(self):
        records=[dict(self.child,parent='0xc',parentStableId='0xc',stableId='reused')]
        with patch('window_state.subprocess.check_output',return_value=json.dumps(records)):
            enrich_families(self.windows)
        self.assertEqual(self.child['parent'],'0xa')
    def test_switcher_skips_blocked_owner(self):
        with patch('window_state.subprocess.check_output',return_value=json.dumps(self.windows)):
            self.assertEqual([w['address'] for w in switcher_candidates(self.windows,'1')],['0xc','0xb'])

if __name__=='__main__':unittest.main()
