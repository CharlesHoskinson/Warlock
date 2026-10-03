"""Actual pure setup/command guards plus exact predecessor source preservation."""
import ast,copy
from pathlib import Path
import unittest
import focus_setup as f
B=Path(__file__).resolve().parent;OLD=B.with_name('browser-files-flow-v14')
IDENTITY={'address':'0xabcd','stableId':'18000000','pid':123,'start':'456'}
SESSION='private-attached-session'
PEER={**{k:IDENTITY[k]for k in ('address','stableId','pid')},'mapped':True,'hidden':False,'acceptsInput':True,'surfaceBox':[140,100,930,700]}
NATIVE={**{k:False for k in ('sessionLocked','exclusiveLayers','constrained','heldButtons','seatGrab','captured','dnd','dragTarget')},'clickMode':0,'pointerSurfacePresent':True,'nativeFocus':PEER,'pointerOwner':PEER,'cursor':[605,450]}

class FocusSetup(unittest.TestCase):
 def test_exact_observed_focus_and_pointer_owner(self):self.assertEqual(f.observed(NATIVE,IDENTITY,SESSION),PEER)
 def test_wrong_focus_or_pointer_lifetime_refused(self):
  for role in ('nativeFocus','pointerOwner'):
   for key,value in [('address','0xbeef'),('stableId','18000001'),('pid',124)]:
    n=copy.deepcopy(NATIVE);n[role][key]=value
    with self.assertRaises(ValueError):f.observed(n,IDENTITY,SESSION)
 def test_ineligible_focus_or_pointer_refused(self):
  for role in ('nativeFocus','pointerOwner'):
   for key,value in [('mapped',False),('hidden',True),('acceptsInput',False)]:
    n=copy.deepcopy(NATIVE);n[role][key]=value
    with self.assertRaises(ValueError):f.observed(n,IDENTITY,SESSION)
 def test_all_input_capture_flags_refuse(self):
  for k in ('sessionLocked','exclusiveLayers','constrained','heldButtons','seatGrab','captured','dnd','dragTarget','clickMode'):
   n=copy.deepcopy(NATIVE);n[k]=True if k!='clickMode'else 1
   with self.assertRaises(ValueError):f.observed(n,IDENTITY,SESSION)
 def test_missing_pointer_surface_refused(self):
  n={**NATIVE,'pointerSurfacePresent':False}
  with self.assertRaises(ValueError):f.observed(n,IDENTITY,SESSION)
 def test_exact_focus_snapshot_change_refused(self):
  expected={**PEER,'surfaceBox':[141,100,930,700]}
  with self.assertRaises(ValueError):f.observed(NATIVE,IDENTITY,SESSION,expected)
 def test_identity_and_selector_injection_refused(self):
  for key,value in [('address','0xabcd"; hl.dispatch()'),('address','abcd'),('stableId','18000000\n'),('pid',True),('pid',0),('start','0'),('start','456x')]:
   with self.assertRaises(ValueError):f.command({**IDENTITY,key:value},SESSION)
  with self.assertRaises(ValueError):f.command({**IDENTITY,'extra':1},SESSION)
  with self.assertRaises(ValueError):f.command(IDENTITY,'')
 def test_guarded_synchronous_dispatch_order(self):
  command,ack=f.command(IDENTITY,SESSION)
  self.assertLess(command.index('assert(a=='),command.index('hl.dispatch('))
  self.assertLess(command.index('hl.dispatch('),command.index('assert(aa=='))
  self.assertLess(command.index('assert(aa=='),command.index('print("'+ack+'")'))
  self.assertNotIn('timer',command);self.assertNotIn('get_active_window',command)
  self.assertIn('hl.dsp.focus({window="address:0xabcd"})',command)
 def test_complete_raw_ack_separate_from_authority(self):
  _,ack=f.command(IDENTITY,SESSION);raw='qa-browser-focus-setup-result:table:diagnostic=unknown\n'+ack
  f.validate_ack(raw,ack)
  with self.assertRaises(ValueError):f.observed({**NATIVE,'nativeFocus':None},IDENTITY,SESSION)
 def test_missing_malformed_or_stale_ack_refused(self):
  _,ack=f.command(IDENTITY,SESSION)
  for raw in ['',ack,'ok','qa-browser-focus-setup-result:table:\nwrong', 'qa-browser-focus-setup-result:table:\n'+ack+'\nextra']:
   with self.assertRaises(ValueError):f.validate_ack(raw,ack)
 def test_warped_center_swaps_actual_candidate_order(self):
  self.assertEqual(f.ordered_points([605,450],[682,508],[605.0,450.0]),[[682,508],[605,450]])
 def test_other_cursor_preserves_candidate_order(self):self.assertEqual(f.ordered_points([605,450],[682,508],[1110,495]),[[605,450],[682,508]])
 def test_zero_displacement_refused_before_write(self):
  with self.assertRaises(ValueError):f.require_displacement([605,450],[605.0,450.0])
  f.require_displacement([682,508],[605,450])
 def test_noninteger_incomplete_outside_candidates_refused(self):
  for point in ([605.0,450],[605],[True,450],[1600,450],[-1,450]):
   with self.assertRaises(ValueError):f.ordered_points(point,[682,508],[0,0])
 def test_one_axis_duplicate_candidates_refused(self):
  with self.assertRaises(ValueError):f.ordered_points([605,450],[605,508],[0,0])
 def test_v14_runtime_exact_outside_setup_and_browser_rect(self):
  old=(OLD/'private_session.py').read_text();new=(B/'private_session.py').read_text()
  new=new.replace('from focus_setup import command as focus_command,validate_ack as validate_focus_ack,observed as observed_focus,ordered_points,require_displacement\n','',1)
  begin=new.index(' def browser_rect():');end=new.index(' def files_point():',begin)
  new=new[:begin]+old[old.index(' def browser_rect():'):old.index(' def files_point():')]+new[end:]
  self.assertEqual(new,old)
 def test_v14_all_models_and_other_runtime_exact(self):
  exceptions={'private_session.py','freeze_packet.py','metrics_offline.py','test_geometry_source.py'}
  for p in [*OLD.glob('*.py'),*OLD.glob('*.qnt')]:
   if p.name not in exceptions:self.assertEqual((B/p.name).read_bytes(),p.read_bytes(),p.name)
 def test_original15_checks_still_exact(self):
  def checks(p):return[ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(p.read_text()))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='check']
  self.assertEqual(checks(B/'private_session.py'),checks(OLD/'private_session.py'))
 def test_current_follow_mouse_and_readonly_cdp_exact(self):
  for name in ('nested-qt.lua','cdp_readonly.py','compose.html','viewport_witness.py'):
   self.assertEqual((B/name).read_bytes(),(OLD/name).read_bytes(),name)
  self.assertIn('follow_mouse=0',(B/'nested-qt.lua').read_text())
 def test_setup_never_counted_as_original_feature(self):
  text=(B/'private_session.py').read_text();start=text.index("setup={'accepted':False");end=text.index("initial,s,expected=wait(paired",start)
  self.assertNotIn('check(',text[start:end]);self.assertIn("'originalFeatureAcceptance':False",text[start:end])

if __name__=='__main__':unittest.main()
