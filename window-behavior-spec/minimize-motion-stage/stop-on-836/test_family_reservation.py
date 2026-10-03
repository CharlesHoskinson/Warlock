#!/usr/bin/env python3
"""Snapshot-to-reservation callback interleavings on the actual controller."""
import copy,unittest
import test_controller as base
motion=base.motion
class ReservationRace(unittest.TestCase):
 setUp=base.ControllerTests.setUp
 tearDown=base.ControllerTests.tearDown
 def setup_family(self):
  self.d.windows=[base.window('0x10','owner',100),base.window('0x20','child',100),base.window('0x30','nested',100)]
  self.d.family=lambda w,windows,single=False:(windows,windows[-1])
  tokens=self.c.request('minimize','0x30','nested','100')['tokens']
  for token in tokens:self.c.ready(token);self.c.settle(token)
  return self.c.request('restore','0x30','nested','100')['tokens']
 def test_old_owner_restore_between_family_snapshot_and_reservation(self):
  previous=self.setup_family();owner=self.c.pending['0x10']['token']
  def family(w,windows,single=False):
   stale=copy.deepcopy(self.d.windows)
   self.c.settle(owner)
   self.assertEqual(self.d.windows[0]['workspace']['name'],'2')
   return stale,stale[-1]
  self.d.family=family
  result=self.c.request('minimize','0x30','nested','100')
  self.assertIn('0x10',self.c.pending,'owner was skipped using a stale minimized workspace snapshot')
  self.assertEqual(self.c.pending['0x10']['operation'],'minimize')
  for token in result['tokens']:
   if token:self.c.ready(token);self.c.settle(token)
  self.assertTrue(all(w['workspace']['name']=='special:win-minimized' for w in self.d.windows))
 def test_all_peers_reserved_before_first_peer_freeze(self):
  old=self.setup_family();seen=[];ipc=self.d.ipc
  def observe(method,payload):
   if method=='motionFreeze' and payload['identity'][0]!='0x30':
    seen.append({a:r['operation'] for a,r in self.c.pending.items()})
   return ipc(method,payload)
  self.d.ipc=observe
  self.c.request('minimize','0x30','nested','100')
  self.assertTrue(seen)
  self.assertTrue(all(set(states)=={'0x10','0x20','0x30'} and all(op=='minimize' for op in states.values()) for states in seen))
 def test_member_reuse_during_family_query_rejects_entire_new_scope(self):
  self.setup_family();before=len(self.d.commits())
  def family(w,windows,single=False):
   self.d.windows[0]['stableId']='reused';self.d.windows[0]['pid']=101
   return windows,windows[-1]
  self.d.family=family
  with self.assertRaisesRegex(ValueError,'family member identity'):self.c.request('minimize','0x30','nested','100')
  self.assertFalse(any(c[1]=='minimize' and c[2][0]=='0x10' for c in self.d.commits()[before:]))
 def test_current_cancel_first_deduplicated_and_completion_after_cleanup(self):
  token=self.c.request('minimize','0x10','stable10','100')['tokens'][0];self.c.ready(token)
  record=self.c.lookup(token)
  record['frozenVisual']={k:record[k] for k in ('token','identity','target')}
  record['oldVisuals']=[dict(record['frozenVisual'],token='older-1')]
  attempted=[]
  def ipc(method,payload):
   if method=='motionCancel':
    attempted.append(payload['token'])
    self.assertIs(self.c.lookup(token),record)
    self.assertEqual(record['phase'],'cleaning')
   return True
  self.d.ipc=ipc;self.c.settle(token)
  self.assertEqual(attempted,[token,'older-1']);self.assertIsNone(self.c.lookup(token))
  events=self.c.events
  self.assertTrue(any(e['event']=='commitDone' and e['token']==token for e in events))
  done=[e['time'] for e in events if e['event']=='cancelDone']
  cleanup=next(e['time'] for e in events if e['event']=='cleanupDone' and e['token']==token)
  self.assertLessEqual(max(done),cleanup)
 def test_family_plan_and_commit_ledger_preserve_each_exact_member(self):
  self.setup_family()
  result=self.c.request('minimize','0x30','nested','100')
  plan=next(e for e in reversed(self.c.events) if e['event']=='familyPlan')
  self.assertEqual({tuple(m['identity']) for m in plan['members']},{motion.key(w) for w in self.d.windows})
  self.assertEqual({m['token'] for m in plan['members']},set(result['tokens']))
  for token in result['tokens']:self.c.ready(token);self.c.settle(token)
  commits={tuple(e['identity']) for e in self.c.events if e['event']=='commitDone' and e['token'] in result['tokens']}
  self.assertEqual(commits,{motion.key(w) for w in self.d.windows})
 def test_diagnostics_retention_is_bounded(self):
  for i in range(300):self.c.audit('test',index=i)
  self.assertEqual(len(self.c.events),128);self.assertEqual(self.c.events[0]['index'],172)

if __name__=='__main__':unittest.main()
