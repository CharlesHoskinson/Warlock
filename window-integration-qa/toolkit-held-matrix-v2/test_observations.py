import copy,unittest
from observations import captured,retired,released,positive_group_drop
TARGET={'address':'0xabc','stableId':'1','pid':123};PEER={'address':'0xdef','stableId':'2','pid':123}
def base():return dict(coreDragTarget=TARGET,coreDragMode=0,signalDownButtonIds=[272],heldButtons=False,nativeFocus=PEER,groups=[],sessionLocked=False,exclusiveLayers=0,constrained=False,seatGrab=False,captured=False,dnd=False)
class Oracle(unittest.TestCase):
 def test_core_captured_exact(self):self.assertTrue(captured(base(),TARGET,0,272))
 def test_lifetime_mismatch_refused(self):
  s=base();s['coreDragTarget']={**TARGET,'stableId':'3'}
  with self.assertRaisesRegex(ValueError,'lifetime'):captured(s,TARGET,0,272)
 def test_wrong_mode_refused(self):
  with self.assertRaisesRegex(ValueError,'mode'):captured(base(),TARGET,1,272)
 def test_wrong_held_button_refused(self):
  with self.assertRaisesRegex(ValueError,'button'):captured(base(),TARGET,0,273)
 def test_competing_grab_refused(self):
  s=base();s['seatGrab']=True
  with self.assertRaisesRegex(ValueError,'authority'):captured(s,TARGET,0,272)
 def test_retire_held_signal_preserved(self):
  a=base();b={**a,'coreDragTarget':None};self.assertTrue(retired(a,b,PEER))
 def test_retire_target_not_clear_refused(self):
  with self.assertRaisesRegex(ValueError,'retired'):retired(base(),base(),PEER)
 def test_nonrelease_group_mutation_refused(self):
  a=base();b={**a,'coreDragTarget':None,'groups':[dict(head=PEER,current=PEER,members=[PEER,TARGET],locked=False,denied=False)]}
  with self.assertRaisesRegex(ValueError,'group'):retired(a,b,PEER)
 def test_nonrelease_focus_theft_refused(self):
  a=base();b={**a,'coreDragTarget':None,'nativeFocus':TARGET}
  with self.assertRaisesRegex(ValueError,'focus'):retired(a,b,PEER)
 def test_fake_retirement_release_refused(self):
  a=base();b={**a,'coreDragTarget':None,'signalDownButtonIds':[]}
  with self.assertRaisesRegex(ValueError,'fabricated'):retired(a,b,PEER)
 def test_genuine_release_quiescent(self):self.assertTrue(released({**base(),'coreDragTarget':None,'signalDownButtonIds':[]}))
 def test_core_held_blocks_release(self):
  with self.assertRaisesRegex(ValueError,'quiesce'):released({**base(),'coreDragTarget':None,'signalDownButtonIds':[],'heldButtons':True})
 def test_signal_held_blocks_release(self):
  with self.assertRaisesRegex(ValueError,'quiesce'):released({**base(),'coreDragTarget':None})
 def test_actual_group_insert_positive(self):
  s=base();s['groups']=[dict(head=PEER,current=TARGET,members=[PEER,TARGET],locked=False,denied=False)];self.assertTrue(positive_group_drop(s,TARGET,PEER))
 def test_no_group_insert_refused(self):
  with self.assertRaisesRegex(ValueError,'insert'):positive_group_drop(base(),TARGET,PEER)
 def test_wrong_lifetime_group_insert_refused(self):
  s=base();s['groups']=[dict(head=PEER,current=PEER,members=[PEER,{**TARGET,'stableId':'3'}],locked=False,denied=False)]
  with self.assertRaisesRegex(ValueError,'insert'):positive_group_drop(s,TARGET,PEER)
if __name__=='__main__':unittest.main(verbosity=2)
