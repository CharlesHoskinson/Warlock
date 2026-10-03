import copy
import json
from pathlib import Path
import threading
import types
import unittest
from family_order import order_family,needs_active_witness
from native_desktop import NativeDesktop
from scene_controller import SceneController,ids,key
from test_scene_controller import Desktop,Transport


def fixture():
    d=Desktop()
    for w in d.windows:w.update(floating=True,fullscreen=0,pinned=False)
    members=[dict(w,**{k:n[k] for k in ('parent','parentStableId','modal')})
             for w,n in zip(d.windows,d.native,strict=True)]
    return members,copy.deepcopy(d.native)


class DrawOrder(unittest.TestCase):
    def test_nested_mru_never_draws_below_its_parent(self):
        members,native=fixture();members=[members[0],members[2],members[1]]
        self.assertEqual([w['stableId'] for w in order_family(members,native)],['aa01','bb02','cc03'])
    def test_retained_native_baseline_counterexample_ancestry(self):
        p=Path('/home/hoskinson/window-integration-qa/family-service-taskbar-v4/attempt-1/service-evidence.json')
        record=json.loads(p.read_text())['records'][0]['history'][0]
        members=record['members'];self.assertEqual([w['stableId'] for w in members],['18000000','18000003','18000002'])
        # The retained exact parent chain alone constrains every pair. No sibling
        # paint order is inferred from this observer's historical member array.
        self.assertEqual([w['stableId'] for w in order_family(members,members)],['18000000','18000002','18000003'])
    def siblings(self):
        members,native=fixture()
        members[2].update(parent=members[0]['address'],parentStableId=members[0]['stableId'])
        native[2].update(parent=members[0]['address'],parentStableId=members[0]['stableId'])
        return members,native
    def test_native_vector_for_siblings_not_focus_history(self):
        m,n=self.siblings();m[1]['focusHistoryID']=0;m[2]['focusHistoryID']=9
        self.assertEqual([key(w) for w in order_family(m,[n[0],n[2],n[1]])],[key(m[0]),key(m[2]),key(m[1])])
    def test_pinned_ancestor_precedes_unpinned_descendant(self):
        m,n=fixture();m[0]['pinned']=True
        self.assertEqual([key(w) for w in order_family(m,n)],[key(w) for w in m])
    def test_independent_pinned_sibling_above_ordinary_floating(self):
        m,n=self.siblings();m[1]['pinned']=True
        self.assertEqual([key(w) for w in order_family(m,n)],[key(m[0]),key(m[2]),key(m[1])])
    def test_tiled_before_floating_and_active_tiled_last(self):
        m,n=self.siblings();m[1]['floating']=False
        self.assertEqual([key(w) for w in order_family(m,[n[0],n[2],n[1]])],[key(w) for w in m])
        m[2]['floating']=False
        self.assertTrue(needs_active_witness(m));self.assertRaisesRegex(ValueError,'active',order_family,m,n)
        result=order_family(m,n,active=key(m[1]),active_observed=True)
        self.assertEqual([key(w) for w in result],[key(m[0]),key(m[2]),key(m[1])])
    def test_incomplete_reused_or_duplicate_native_vector_refuses(self):
        m,n=fixture();self.assertRaises(ValueError,order_family,m,n[:-1])
        reused=copy.deepcopy(n);reused[1]['pid']+=1;self.assertRaises(ValueError,order_family,m,reused)
        self.assertRaises(ValueError,order_family,m,n+[n[1]])
    def test_missing_selected_parent_stable_or_cycle_refuses(self):
        for change in ({'parentStableId':'ee55'},{'parent':'0xee55','parentStableId':'ee55'},
                       {'parent':'0xcc03','parentStableId':'cc03'}):
            with self.subTest(change=change):
                m,n=fixture();m[1].update(change);n[1].update(change)
                self.assertRaises(ValueError,order_family,m,n)
    def test_unrelated_malformed_parent_does_not_poison_selected_order(self):
        m,n=fixture();n.append(dict(n[0],address='0xee55',stableId='ee55',parent='0xee55',parentStableId='ee55'))
        self.assertEqual([key(w) for w in order_family(m,n)],[key(w) for w in m])
    def test_independent_fullscreen_sibling_refuses_missing_pass_proof(self):
        m,n=self.siblings();m[2]['fullscreen']=2
        self.assertRaisesRegex(ValueError,'fullscreen',order_family,m,n)
    def test_native_adapter_keeps_deepest_focus_separate_from_draw_order(self):
        m,n=fixture();m=[m[0],m[2],m[1]]
        class Base:
            family_trace=types.SimpleNamespace()
            def family(self,*args):
                self.family_trace.evidence={'native':copy.deepcopy(n)}
                return copy.deepcopy(m),copy.deepcopy(m[1])
        actor=NativeDesktop.__new__(NativeDesktop);actor.base=Base()
        ordered,focus=actor.family(m[0],m)
        self.assertEqual([w['stableId'] for w in ordered],['aa01','bb02','cc03'])
        self.assertEqual(focus['stableId'],'cc03')
        self.assertEqual(actor.base.family_trace.evidence['drawOrder'],[list(key(w)) for w in ordered])
    def test_changed_sibling_order_during_capture_rejects_even_equal_geometry_and_releases_all_sources(self):
        d=Desktop();m,n=self.siblings()
        for w in m:w['at']=[100,100];w['size']=[300,200]
        class Adapter:
            def __init__(self):self.changed=False;self.evidence=None
            def __getattr__(self,name):return getattr(d,name)
            def family(self,*args):
                ordered=order_family(m,[n[0],n[2],n[1]] if self.changed else n)
                self.evidence={'drawOrder':[list(key(w)) for w in ordered]}
                return ordered,m[2]
            def family_evidence(self):return copy.deepcopy(self.evidence)
            def capture_source(self,*args):
                source=d.capture_source(*args);self.changed=True;return source
        adapter=Adapter();t=Transport();c=SceneController(adapter,t)
        try:
            w=d.windows[0];c.request('minimize',w['address'],w['stableId'],w['pid'],context='fixture')
            c.workers.shutdown(wait=True)
            self.assertFalse(any(e['command']=='seed' for e in t.sent))
            self.assertEqual(d.captures,3)
            self.assertTrue(any(len(sources)==3 for sources in d.released))
            self.assertIn('draw order changed',c.history[-1].profile['failure'])
        finally:c.close()
    def test_actual_controller_seed_upload_vector_uses_topological_order(self):
        d=Desktop();m,n=fixture()
        class Adapter:
            def __getattr__(self,name):return getattr(d,name)
            def family(self,*args):return order_family([m[0],m[2],m[1]],n),m[2]
        t=Transport();c=SceneController(Adapter(),t)
        try:
            w=d.windows[0];c.request('minimize',w['address'],w['stableId'],w['pid'],context='fixture')
            c.workers.shutdown(wait=True)
            seed=next(e for e in t.sent if e['command']=='seed')
            self.assertEqual([s['stableId'] for s in seed['members']],['aa01','bb02','cc03'])
            self.assertEqual(ids(c.current.members),[{'stableId':s['stableId'],'pid':s['pid']} for s in seed['members']])
            self.assertEqual(c.current.focus,key(m[2]))
        finally:c.close()


if __name__=='__main__':unittest.main()
