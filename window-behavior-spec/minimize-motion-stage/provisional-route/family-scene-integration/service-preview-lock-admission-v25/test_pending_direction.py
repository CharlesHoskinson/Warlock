import copy
import threading
import unittest
from scene_controller import ids,key
import test_scene_manager as fixture

class PendingDirectionTests(unittest.TestCase):
    setUp=fixture.RegistryTests.setUp
    tearDown=fixture.RegistryTests.tearDown
    wait=fixture.RegistryTests.wait
    seeded=fixture.RegistryTests.seeded
    def reserve(self,op,index=0):
        w=self.d.windows[index]
        return self.m.reserve(op,w['address'],w['stableId'],w['pid'])
    def activate(self,r):return self.m.activate(r['receipt'],context='trusted-fixture')
    def done(self,receipt,op):
        self.wait(lambda:any(r.profile.get('managerReceipt')==receipt for a in self.m.actors for r in a.controller.history))
        record=next(r for a in self.m.actors for r in a.controller.history if r.profile.get('managerReceipt')==receipt)
        self.assertEqual(record.operation,op);self.assertTrue(record.profile['nativeEndpointAlreadySatisfied'])
        self.assertFalse(record.visual);self.assertFalse(self.d.captures)
        self.assertEqual([o for o,*_ in self.d.commits],[op]*3)
        self.assertFalse(any(t.sent for _,t in self.boundaries))
        return record
    def test_explicit_pending_minimize_then_toggle_restores_without_first_context(self):
        first=self.reserve('minimize');second=self.reserve('toggle')
        self.activate(second);self.done(second['receipt'],'restore')
        count=len(self.d.commits);self.assertTrue(self.activate(first)['superseded']);self.assertEqual(len(self.d.commits),count)
    def test_two_initial_toggles_return_to_visible_endpoint(self):
        self.reserve('toggle');latest=self.reserve('toggle');self.activate(latest);self.done(latest['receipt'],'restore')
    def test_two_initial_toggles_return_to_minimized_endpoint(self):
        for w in self.d.windows:w['workspace']['name']='special:win-minimized'
        self.reserve('toggle');latest=self.reserve('toggle');self.activate(latest);self.done(latest['receipt'],'minimize')
    def test_initial_inactive_activate_then_toggle_minimizes(self):
        self.d.active=lambda:'0xdead'
        self.reserve('activate');latest=self.reserve('toggle');self.activate(latest)
        c=self.m.actors[0].controller;r=self.seeded(c)
        self.assertEqual(r.operation,'minimize');self.assertEqual(len(r.sources),3);self.assertFalse(self.d.commits)
    def test_initial_active_activate_then_toggle_restores(self):
        self.reserve('activate');latest=self.reserve('toggle');self.activate(latest);self.done(latest['receipt'],'restore')
    def test_fresh_unknown_peer_family_receipts_compose_in_original_order(self):
        first=self.reserve('minimize',0);second=self.reserve('toggle',2);latest=self.reserve('toggle',0)
        self.activate(latest);c=self.m.actors[0].controller;r=self.seeded(c)
        self.assertEqual(r.operation,'minimize');self.assertEqual(len(r.members),3)
        self.assertFalse(self.d.commits);self.assertTrue(self.activate(first)['superseded']);self.assertTrue(self.activate(second)['superseded'])
        self.assertEqual(self.m.intent_events,{})
    def test_unknown_peer_toggle_preserves_original_active_anchor_identity(self):
        first=self.reserve('activate',0);latest=self.reserve('toggle',2)
        self.activate(latest);self.done(latest['receipt'],'restore')
        self.assertTrue(self.activate(first)['superseded'])
    def test_pending_commands_from_foreign_same_pid_are_not_family_direction(self):
        foreign=copy.deepcopy(self.d.windows[0]);foreign.update(address='0xdddd',stableId='dddd')
        self.d.windows.append(foreign);self.d.native.append(dict(foreign,parent='',parentStableId='',modal=False))
        self.reserve('minimize',0);latest=self.reserve('toggle',3);self.activate(latest)
        r=self.seeded(self.m.actors[1].controller)
        self.assertEqual(r.operation,'minimize');self.assertEqual([key(m) for m in r.members],[key(foreign)])
        self.assertFalse(self.d.commits)
    def test_failed_latest_context_drops_symbolic_direction_before_next_toggle(self):
        failed=self.reserve('restore');self.assertTrue(self.m.fail_ingress(failed['receipt'],'output removed'))
        latest=self.reserve('toggle');self.activate(latest);r=self.seeded(self.m.actors[0].controller)
        self.assertEqual(r.operation,'minimize');self.assertFalse(self.d.commits)
    def test_first_visible_restore_keeps_exact_pin_bits_and_never_publishes_image(self):
        latest=self.reserve('restore');self.activate(latest);r=self.done(latest['receipt'],'restore')
        self.assertEqual([pin for *_,pin in self.d.commits],[True,False,False])
        self.assertEqual([key(m) for m in r.members],[key(m) for m in self.d.windows])
    def test_first_already_minimized_request_is_native_idempotent_without_image(self):
        for w in self.d.windows:w['workspace']['name']='special:win-minimized'
        latest=self.reserve('minimize');self.activate(latest);self.done(latest['receipt'],'minimize')
    def test_native_matching_endpoint_does_not_skip_retained_displayed_reversal(self):
        first=self.reserve('minimize');self.activate(first);c=self.m.actors[0].controller;old=self.seeded(c)
        self.d.block=threading.Event();self.d.started.clear()
        latest=self.reserve('restore');result=self.activate(latest)
        self.assertTrue(self.d.started.wait(1));self.assertTrue(c.current.visual);self.assertTrue(c.current.running)
        command=next(e for e in self.boundaries[0][1].sent if e['token']==result['token'] and e['command']=='retarget')
        self.assertEqual(command['operation'],'restore');self.assertEqual(command['identities'],ids(old.members))
        self.assertEqual(c.current.sources,old.sources);self.assertEqual(self.d.captures,3);self.assertFalse(self.d.commits)
        self.d.block.set();self.wait(lambda:c.current.validated)
        self.assertNotIn('nativeEndpointAlreadySatisfied',c.current.profile)
    def test_unresolved_ledger_exhaustion_refuses_before_ownership_or_factory_change(self):
        self.m.max_direction_events=2
        self.reserve('toggle');self.reserve('toggle')
        before=(self.m.serial,dict(self.m.receipts),dict(self.m.owners),dict(self.m.intent_events),len(self.boundaries))
        with self.assertRaisesRegex(RuntimeError,'queue full'):self.reserve('restore',2)
        after=(self.m.serial,dict(self.m.receipts),dict(self.m.owners),dict(self.m.intent_events),len(self.boundaries))
        self.assertEqual(before,after);self.assertFalse(self.d.commits)

if __name__=='__main__':unittest.main()
