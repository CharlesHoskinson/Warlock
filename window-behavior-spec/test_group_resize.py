#!/usr/bin/env python3
"""Geometry checks for installed shared-boundary resize planning and custom recall."""
import importlib.machinery
import json
from pathlib import Path
import random
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

snap = importlib.machinery.SourceFileLoader('qa_resize', str(Path.home() / '.local/bin/hypr-snap-groups')).load_module()


def overlap(a,b):
    return min(a[0]+a[2],b[0]+b[2]) > max(a[0],b[0]) and min(a[1]+a[3],b[1]+b[3]) > max(a[1],b[1])

class ResizeTests(unittest.TestCase):
    def test_random_horizontal_boundaries_preserve_outside_edges(self):
        rng=random.Random(20260930)
        for _ in range(1000):
            width,height=rng.randint(900,3000),rng.randint(450,1800)
            boundary=width//2
            members={'0x1':[0,0,boundary,height], '0x2':[boundary+10,0,width-boundary-10,height]}
            change=rng.randint(-150,150)
            owner=rng.choice(['0x1','0x2']);old=members[owner]
            new=[0,0,boundary+change,height] if owner=='0x1' else [boundary+10+change,0,width-boundary-10-change,height]
            plan=snap.resize_plan(owner,old,new,members)
            result={**members,**plan};a,b=result['0x1'],result['0x2']
            self.assertEqual(a[0],0);self.assertEqual(b[0]+b[2],width)
            self.assertEqual(a[0]+a[2]+10,b[0]);self.assertFalse(overlap(a,b))
            self.assertTrue(all(r[2]>=200 and r[3]>=100 for r in result.values()))

    def test_middle_third_resizes_both_neighbours(self):
        members={'0x1':[0,0,500,500],'0x2':[510,0,500,500],'0x3':[1020,0,500,500]}
        result={**members,**snap.resize_plan('0x2',members['0x2'],[550,0,430,500],members)}
        self.assertEqual(result['0x1'],[0,0,540,500])
        self.assertEqual(result['0x3'],[990,0,530,500])
        self.assertEqual(result['0x1'][0]+result['0x1'][2]+10,result['0x2'][0])
        self.assertEqual(result['0x2'][0]+result['0x2'][2]+10,result['0x3'][0])
        for a,ra in result.items():
            for b,rb in result.items():
                if a!=b:self.assertFalse(overlap(ra,rb))

    def test_vertical_boundary_retains_titlebar_and_outer_edges(self):
        members={'0x1':[0,0,800,400], '0x2':[0,434,800,400]}
        result={**members,**snap.resize_plan('0x1',members['0x1'],[0,0,800,450],members)}
        self.assertEqual(result['0x2'],[0,484,800,350])
        self.assertEqual(result['0x1'][1]+result['0x1'][3]+34,result['0x2'][1])

    def test_minimum_violation_reverts_owner_without_changing_neighbours(self):
        members={'0x1':[0,0,500,500],'0x2':[510,0,500,500]}
        self.assertEqual(snap.resize_plan('0x1',members['0x1'],[0,0,900,500],members),{'0x1':members['0x1']})

    def test_corner_resize_keeps_four_quarters_disjoint(self):
        members={'0x1':[0,0,800,400],'0x2':[810,0,800,400],
                 '0x3':[0,434,800,400],'0x4':[810,434,800,400]}
        result={**members,**snap.resize_plan('0x1',members['0x1'],[0,0,900,500],members)}
        for a,ra in result.items():
            for b,rb in result.items():
                if a!=b:self.assertFalse(overlap(ra,rb),(a,b,result))

    def test_actual_resize_and_custom_ratio_recall_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            windows=[{'address':'0x1','pid':1,'class':'App','workspace':{'name':'1'},'monitor':0,'at':[0,0],'size':[700,500]},
                     {'address':'0x2','pid':2,'class':'App','workspace':{'name':'1'},'monitor':0,'at':[810,0],'size':[800,500]}]
            state={'version':1,'next_id':1,'groups':[{'id':'snap-1','addresses':['0x1','0x2']}],
                   'snapped':{w['address']:{'identity':snap.identity(w),'workspace':'1','monitor':0,'zone':'left' if w['address']=='0x1' else 'right','rect':[0,0,800,500] if w['address']=='0x1' else [810,0,800,500]} for w in windows}}
            (root/'state.json').write_text(json.dumps(state));calls=[]
            transport=SimpleNamespace(run=lambda argv,**kw:calls.append(('restore',argv)))
            with patch.object(snap,'ROOT',root),patch.object(snap,'clients',lambda:windows),patch.object(snap,'ctl',lambda *argv:calls.append(('eval',argv))),patch.object(snap,'subprocess',transport):
                with patch.object(sys,'argv',['hypr-snap-groups','resize','0x1','0','0','800','500']):snap.main()
                changed=json.loads((root/'state.json').read_text())
                self.assertEqual(changed['snapped']['0x2']['rect'],[710,0,900,500])
                self.assertTrue(all(m['custom'] for m in changed['snapped'].values()))
                self.assertIn(('eval',('eval','hypr_snap_set_geometry("0x2",710,0,900,500)')),calls)
                calls.clear()
                for w in windows:w['workspace']['name']='special:win-minimized'
                with patch.object(sys,'argv',['hypr-snap-groups','recall','snap-1']):snap.main()
                self.assertEqual([argv[-1] for kind,argv in calls if kind=='restore'],['0x1','0x2'])
                self.assertIn(('eval',('eval','hypr_snap_set_geometry("0x1",0,0,700,500)')),calls)
                self.assertIn(('eval',('eval','hypr_snap_set_geometry("0x2",710,0,900,500)')),calls)
                self.assertFalse(any('hypr_snap_zone' in argv[-1] for kind,argv in calls if kind=='eval'))

    def test_actual_hydration_rejects_stable_identity_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            w={'address':'0x1','pid':1,'class':'App','stableId':'100','workspace':{'name':'1'},'monitor':0,'at':[0,0],'size':[800,500]}
            state={'version':1,'next_id':0,'groups':[],'snapped':{}}
            snap.record(state,[w],'0x1','left',normal_size=[420,320],normal_position=[55,65])
            (root/'state.json').write_text(json.dumps(state));calls=[]
            with patch.object(snap,'ROOT',root),patch.object(snap,'clients',lambda:[w]),patch.object(snap,'ctl',lambda *a:calls.append(a)):
                with patch.object(sys,'argv',['hypr-snap-groups','hydrate']):snap.main()
                self.assertEqual(calls,[('eval','hypr_snap_hydrate("0x1",420,320,55,65,"left")')])
                calls.clear();w['stableId']='101'
                with patch.object(sys,'argv',['hypr-snap-groups','hydrate']):snap.main()
                self.assertEqual(calls,[])
                self.assertEqual(json.loads((root/'state.json').read_text())['snapped'],{})

if __name__=='__main__':unittest.main()
