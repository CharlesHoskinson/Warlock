"""Synthetic trace faults and actual frozen CPU driver plans; no GUI acceptance."""
from copy import deepcopy
import json,subprocess,unittest
from input_episode import episode,PLANS
from native_cases import KEYBOARD
T={'address':'0xabc','stableId':'18000000','pid':123,'session':'qa_session','compositorPid':456,'compositorStart':'1234','incarnation':'a'*32,'epoch':'1','generation':'1'}
OWNER={k:T[k] for k in ('address','stableId','pid')}
def mouse():return [{'button':272,'buttonState':s,'timeMs':10+i,'cancelledAtObservation':True,'native':{'cursor':[100,100],'hitOwner':dict(OWNER)}} for i,s in enumerate([1,0])]
def keys(route):return [{'sequence':i+1,'keycode':code,'keyState':state,'timeMs':0,'cancelledAtObservation':False,'seatKeySymAvailableAtObservation':True,'seatKeySymAtObservation':0,'seat':{'keyboardOwner':dict(OWNER),'coreNativeFocus':dict(OWNER),'keyboardSurfacePresent':True,'keyboardResourcePresent':True}} for i,(code,state) in enumerate(PLANS[route])]
class EpisodeTests(unittest.TestCase):
 def refuse(self,rows,before=None,route='titlebar'):
  with self.assertRaises((ValueError,TypeError)):episode(before or [],rows,route,T,[100,100])
 def test_consumed_reserved_button_pair_is_actual_delivery(self):
  r=episode([],mouse(),'titlebar',T,[100,100]);self.assertTrue(r['observedPressAndRelease']);self.assertFalse(r['nativeAcceptance'])
 def test_driver_intent_and_no_actual_events_cannot_pass(self):self.refuse([])
 def test_missing_release_refuses(self):self.refuse(mouse()[:1])
 def test_reordered_pair_refuses(self):self.refuse(list(reversed(mouse())))
 def test_duplicate_down_refuses(self):r=mouse();r[1]['buttonState']=1;self.refuse(r)
 def test_extra_button_refuses(self):self.refuse(mouse()+mouse()[:1])
 def test_wrong_member_down_or_up_refuses(self):
  for i in range(2):
   r=mouse();r[i]['native']['hitOwner']['stableId']='18000001';self.refuse(r)
 def test_wrong_cursor_refuses(self):r=mouse();r[1]['native']['cursor']=[101,100];self.refuse(r)
 def test_numeric_bool_and_float_aliases_refuse(self):
  for field,value in [('buttonState',True),('buttonState',1.0),('timeMs',False),('cancelledAtObservation',0)]:
   r=mouse();r[0][field]=value;self.refuse(r)
 def test_prefix_replacement_refuses(self):
  old=mouse();new=deepcopy(old);new[0]['timeMs']=99;self.refuse(new+mouse(),old)
 def test_prefix_bool_alias_refuses(self):
  old=mouse();new=deepcopy(old);new[0]['buttonState']=True;self.refuse(new+mouse(),old)
 def test_valid_retained_prefix_accepts(self):
  before=mouse();r=episode(before,before+mouse(),'titlebar',T,[100,100]);self.assertEqual(r['eventCount'],2)
 def test_exact_keyboard_episodes_accept(self):
  for route in ['super-p','super-ctrl-t']:self.assertTrue(episode([],keys(route),route,T)['observedPressAndRelease'])
 def test_keyboard_sequence_gap_refuses(self):
  r=keys('super-p');r[2]['sequence']+=1;self.refuse(r,route='super-p')
 def test_keyboard_wrong_seat_or_core_refuses(self):
  for field in ['keyboardOwner','coreNativeFocus']:
   r=keys('super-p');r[1]['seat'][field]['pid']=999;self.refuse(r,route='super-p')
 def test_keyboard_release_missing_refuses(self):self.refuse(keys('super-ctrl-t')[:-1],route='super-ctrl-t')
 def test_keyboard_numeric_alias_refuses(self):
  r=keys('super-p');r[0]['keyState']=True;self.refuse(r,route='super-p')
 def test_valid_partial_episode_is_pending_only_when_explicit(self):
  self.assertIsNone(episode([],mouse()[:1],'titlebar',T,[100,100],allow_pending=True))
  with self.assertRaises(ValueError):episode([],mouse()[:1],'titlebar',T,[100,100])
  self.assertTrue(episode([],mouse(),'titlebar',T,[100,100],allow_pending=True)['observedPressAndRelease'])
 def test_conflicting_partial_episode_is_immediate_refusal(self):
  r=mouse()[:1];r[0]['buttonState']=0
  with self.assertRaises(ValueError):episode([],r,'titlebar',T,[100,100],allow_pending=True)
 def test_actual_cpu_driver_plans_match_exact_episode_routes(self):
  for route in ['super-p','super-ctrl-t']:
   r=subprocess.run([str(KEYBOARD),'--plan','--chord',route],capture_output=True,text=True,check=True,timeout=3);p=json.loads(r.stdout)
   self.assertIs(p['cpuOnly'],True);self.assertEqual(p['keymapSHA256'],'bac3cf32ec492636e40269802a13285515e138069fa0405284397404599b11ee');self.assertEqual([(k['wire'],k['state']) for k in p['plan']],PLANS[route])
if __name__=='__main__':unittest.main()
