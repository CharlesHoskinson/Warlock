#!/usr/bin/env python3
import copy,unittest
from native_motion_fixture import verify_owner_pin,verify_family
class Policy(unittest.TestCase):
 def setUp(self):self.members=[{'address':'0x1','stableId':'a','pid':10,'pinned':False},{'address':'0x2','stableId':'b','pid':10,'pinned':False},{'address':'0x3','stableId':'c','pid':10,'pinned':False}]
 def test_owner_only_pin_mixed_modal_family_is_correct(self):
  after=copy.deepcopy(self.members);after[0]['pinned']=True;verify_owner_pin(self.members[0],self.members,after)
 def test_owner_not_pinned_is_rejected(self):
  with self.assertRaisesRegex(AssertionError,'owner'):verify_owner_pin(self.members[0],self.members,self.members)
 def test_other_independently_pinned_member_remains_pinned(self):
  self.members[2]['pinned']=True;after=copy.deepcopy(self.members);after[0]['pinned']=True;verify_owner_pin(self.members[0],self.members,after)
 def test_unrequested_child_pin_change_is_rejected(self):
  after=copy.deepcopy(self.members);after[0]['pinned']=True;after[1]['pinned']=True
  with self.assertRaisesRegex(AssertionError,'wrong'):verify_owner_pin(self.members[0],self.members,after)
 def test_stale_identity_or_missing_member_is_rejected(self):
  after=copy.deepcopy(self.members);after[0]['pinned']=True;after[1]['stableId']='reused'
  with self.assertRaisesRegex(AssertionError,'identity'):verify_owner_pin(self.members[0],self.members,after)
  with self.assertRaisesRegex(AssertionError,'identity'):verify_owner_pin(self.members[0],self.members,after[:1])
 def test_backend_exact_family_and_deepest_focus(self):verify_family(self.members,{'windows':list(reversed(self.members)),'focus':self.members[0]})
 def test_same_process_foreign_peer_or_reused_member_rejected(self):
  foreign=dict(self.members[1],address='0x9');reused=dict(self.members[1],stableId='reuse')
  for substitute in (foreign,reused):
   with self.subTest(substitute=substitute),self.assertRaisesRegex(AssertionError,'family'):verify_family(self.members,{'windows':[self.members[0],substitute,self.members[2]],'focus':self.members[0]})
 def test_wrong_modal_focus_rejected(self):
  with self.assertRaisesRegex(AssertionError,'focus'):verify_family(self.members,{'windows':self.members,'focus':self.members[-1]})
if __name__=='__main__':unittest.main()
