#!/usr/bin/env python3
"""Actual source family planning, failed enrichment and per-token cancellation."""
import copy,json,threading,unittest
from unittest.mock import patch
import test_controller as base
motion=base.motion

def fixture():
 windows=[base.window('0x10','owner',100),base.window('0x20','child',100),base.window('0x30','nested',100),base.window('0x40','foreign',100)]
 native=[]
 for index,w in enumerate(windows):
  parent=windows[index-1] if index in (1,2) else None
  native.append(dict(w,parent=parent['address'] if parent else '',parentStableId=parent['stableId'] if parent else '',modal=index in (1,2)))
 return windows,native
class NativeFamilies(unittest.TestCase):
 def test_partial_minimized_workspace_does_not_split_fresh_native_family(self):
  windows,native=fixture();windows[0]['workspace']['name']='special:win-minimized';windows[1]['workspace']['name']='7'
  members,focus=motion.native_family_plan(windows[2],windows,native)
  self.assertEqual([w['address'] for w in members],['0x10','0x20','0x30']);self.assertEqual(focus['address'],'0x30')
 def test_same_pid_foreign_toplevel_is_excluded(self):
  windows,native=fixture();members,focus=motion.native_family_plan(windows[0],windows,native)
  self.assertNotIn('0x40',[w['address'] for w in members])
 def test_reused_target_pid_and_stable_id_cannot_use_old_relation(self):
  for field,new in [('pid',101),('stableId','reuse')]:
   windows,native=fixture();windows[2][field]=new
   with self.subTest(field=field),self.assertRaisesRegex(ValueError,'coverage|target identity'):motion.native_family_plan(windows[2],windows,native)
 def test_reused_parent_pid_cannot_attach_cached_children(self):
  windows,native=fixture();windows[1]['pid']=101
  with self.assertRaisesRegex(ValueError,'coverage|parent identity'):motion.native_family_plan(windows[2],windows,native)
 def test_changed_parent_stable_id_and_missing_parent_are_rejected(self):
  for missing in (False,True):
   windows,native=fixture()
   if missing:windows.pop(1)
   else:native[2]['parentStableId']='wrong'
   with self.subTest(missing=missing),self.assertRaisesRegex(ValueError,'coverage|parent identity'):motion.native_family_plan(next(w for w in windows if w['address']=='0x30'),windows,native)
 def test_genuine_fresh_detachment_does_not_restore_old_scope(self):
  windows,native=fixture();native[2].update(parent='',parentStableId='')
  members,focus=motion.native_family_plan(windows[2],windows,native);self.assertEqual([w['address'] for w in members],['0x30'])
 def test_duplicate_relation_and_cycle_are_rejected(self):
  windows,native=fixture()
  with self.assertRaisesRegex(ValueError,'duplicate'):motion.native_family_plan(windows[2],windows,native+[native[0]])
  native[0].update(parent='0x30',parentStableId='nested')
  with self.assertRaisesRegex(ValueError,'cycle'):motion.native_family_plan(windows[2],windows,native)
 def test_native_ipc_retry_is_distinct_from_successful_singleton(self):
  windows,native=fixture();desktop=motion.BasicDesktop();desktop.family_trace=threading.local()
  with patch.object(desktop,'clients',return_value=windows),patch.object(motion.subprocess,'check_output',side_effect=['bad JSON',json.dumps(native)]),patch.object(motion.time,'sleep'):
   members,focus=desktop.family(windows[2],windows)
  self.assertEqual(len(members),3);self.assertEqual(desktop.family_trace.evidence['attempts'],2)
 def test_permanent_native_query_failure_rejects_entire_action(self):
  windows,native=fixture();desktop=motion.BasicDesktop()
  with patch.object(desktop,'clients',return_value=windows),patch.object(motion.subprocess,'check_output',return_value='bad JSON'),patch.object(motion.time,'sleep'),self.assertRaisesRegex(ValueError,'entire request rejected'):
   desktop.family(windows[2],windows)
 def test_single_member_backend_optout_requires_no_native_query(self):
  windows,native=fixture()
  with patch.object(motion.subprocess,'check_output',side_effect=AssertionError('unexpected query')):
   members,focus=motion.BasicDesktop().family(windows[2],windows,True)
  self.assertEqual(members,[windows[2]])

 def test_missing_or_mismatched_descendant_is_not_silently_truncated(self):
  for missing in (True,False):
   windows,native=fixture()
   if missing:native.pop(2)
   else:native[2]['pid']=101
   with self.subTest(missing=missing),self.assertRaisesRegex(ValueError,'coverage'):motion.native_family_plan(windows[0],windows,native)
 def test_unrelated_cycle_or_dangling_parent_does_not_break_selected_family(self):
  for parent in ('0x40','0x999'):
   windows,native=fixture();native[3].update(parent=parent,parentStableId='foreign')
   members,focus=motion.native_family_plan(windows[0],windows,native);self.assertEqual(len(members),3)
 def test_client_change_around_query_retries_with_new_complete_snapshot(self):
  windows,native=fixture();desktop=motion.BasicDesktop();desktop.family_trace=threading.local()
  after=windows[:-1];native_after=native[:-1]
  with patch.object(desktop,'clients',side_effect=[windows,after,after,after]),patch.object(motion.subprocess,'check_output',side_effect=[json.dumps(native),json.dumps(native_after)]),patch.object(motion.time,'sleep'):
   members,focus=desktop.family(windows[2],windows)
  self.assertEqual(len(members),3);self.assertEqual(desktop.family_trace.evidence['attempts'],2)

class ControllerFamilies(unittest.TestCase):
 setUp=base.ControllerTests.setUp
 tearDown=base.ControllerTests.tearDown
 def test_rejected_family_reversal_finishes_previous_accepted_primary_intent(self):
  self.d.windows=[base.window('0x10','stable10',100),base.window('0x20','child',100)]
  self.d.family=lambda w,windows,single=False:(windows,windows[-1])
  tokens=self.c.request('minimize','0x10','stable10','100')['tokens']
  for token in tokens:self.c.ready(token);self.c.settle(token)
  tokens=self.c.request('restore','0x10','stable10','100')['tokens']
  def failed(*args):raise ValueError('native family query unavailable')
  self.d.family=failed
  with self.assertRaisesRegex(ValueError,'unavailable'):self.c.request('minimize','0x10','stable10','100')
  self.assertEqual(self.d.windows[0]['workspace']['name'],'2')
  self.assertEqual(self.c.pending['0x20']['operation'],'restore')
  self.c.ready(tokens[1]);self.c.settle(tokens[1]);self.assertFalse(self.c.pending)
  self.assertTrue(all(w['workspace']['name']=='2' for w in self.d.windows))
 def test_each_cancel_is_attempted_after_an_earlier_ipc_failure(self):
  old=self.c.request('minimize','0x10','stable10','100')['tokens'][0];self.c.ready(old)
  new=self.c.request('restore','0x10','stable10','100')['tokens'][0];record=self.c.lookup(new);attempts=[]
  def ipc(method,payload):
   if method=='motionCancel':
    attempts.append(payload['token'])
    if len(attempts)==1:raise OSError('failed stale cancellation')
   return True
  self.d.ipc=ipc;self.c.drop(record)
  self.assertIn(old,attempts);self.assertIn(new,attempts);self.assertGreaterEqual(len(attempts),2);self.assertFalse(self.c.pending)

if __name__=='__main__':unittest.main()
