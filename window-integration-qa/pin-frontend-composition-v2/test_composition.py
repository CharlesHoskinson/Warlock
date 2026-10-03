"""Execute new unprojected CPU decoders/controller; controlled data, no GUI proof."""
import copy,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from popup_authority import NAMES,ENGINE,engine_pair,popup_pair
from layer_episode import episode
from frontend_authority import binding,current,completion_current,FrontendCase
from frontend_cases import FrontendCases

class Composition(unittest.TestCase):
 def setUp(self):
  self.scope=dict(pid=11,start='777',configSHA256='f'*64,engineGeneration=1,engineEpoch=1,providerGeneration=1)
  self.meta=dict(schema='qml-engine-metadata-v1',kind='metadata-only; no widget/input authority',processId=11,processStart='777',configSHA256='f'*64,**{k:1 for k in ENGINE})
  self.popup=dict(schema='qml-popup-lifetime-v1',relationship='lexical-pin-popup-existing-attached-native-content',processId=11,processStart='777',configSHA256='f'*64,**{k:1 for k in ENGINE},nativeWindowBound=True,diagnostics={},allocations=dict(zip(NAMES,range(1,8))),contexts={n:dict(generation=i+11 if i<3 else 0,present=i<3,enginePresent=i<3)for i,n in enumerate(NAMES)})
  self.token=dict(address='0x123',stableId='18000000',pid=7,session='qa_1',compositorPid=9,compositorStart='123',incarnation='a'*32,epoch='1',generation='1')
  self.layer=dict(address='0xabc',pid=11,namespace='hoskinson-pin-window-menu',mapped=True,visible=True,box=[200,300,240,100])
  self.native=dict(layers=[self.layer],pointerSurfacePresent=True,pointerLayerOwner=self.layer,keyboardSurfacePresent=True,keyboardResourcePresent=True,keyboardLayerOwner=self.layer,cursor=[310,315],nativeFocus=None,sessionLocked=False,constrained=False,heldButtons=False,seatGrab=False,captured=False,dnd=False,dragTarget=False,exclusiveLayers=0,clickMode=0)
  self.menu=dict(open=True,status='ready',sent=False,nonce=1,publicIdentity={k:self.token[k]for k in('address','stableId','pid')},captured=self.token,layerNamespace='hoskinson-pin-window-menu',button=dict(x=0,y=0,width=220,height=30,visible=True,enabled=True,label='Toggle pin'),engineBefore=copy.deepcopy(self.meta),engineAfter=copy.deepcopy(self.meta),popupBefore=copy.deepcopy(self.popup),popupAfter=copy.deepcopy(self.popup))
  self.expected=binding(self.menu,self.native,self.scope)
 def rows(self,route='pointer'):
  a=dict(sequence=1,timeMs=0,cancelledAtObservation=False,native=copy.deepcopy(self.native))
  if route=='pointer':a.update(button=272,buttonState=1)
  else:a.update(keycode=28,keyState=1,seatKeySymAvailableAtObservation=True,seatKeySymAtObservation=65293)
  b=copy.deepcopy(a);b.update(sequence=2);b['buttonState'if route=='pointer'else'keyState']=0
  return [a,b]
 def test_full_pair_positive(self):self.assertEqual(popup_pair(self.menu,self.scope),self.popup)
 def test_source_supported_content_root_alias(self):
  for k in('popupBefore','popupAfter'):self.menu[k]['allocations']['nativeRoot']=5
  self.assertEqual(binding(self.menu,self.native,self.scope)['popupWitness']['allocations']['nativeRoot'],5)
 def test_metadata_flags_cannot_supply_tuple(self):
  self.menu['popupBefore']=dict(actualProviderVerified=True,scope=self.scope)
  with self.assertRaises(ValueError):binding(self.menu,self.native,self.scope)
 def test_every_generation_boolean_refused(self):
  for k in ENGINE:
   m=copy.deepcopy(self.menu);m['popupBefore'][k]=True
   with self.assertRaises(ValueError):binding(m,self.native,self.scope)
 def test_allocation_boolean_or_null_refused(self):
  for name in NAMES:
   for value in(True,0,None):
    m=copy.deepcopy(self.menu);m['popupBefore']['allocations'][name]=value
    with self.assertRaises(ValueError):binding(m,self.native,self.scope)
 def test_each_allocation_getter_change_refused(self):
  for name in NAMES:
   m=copy.deepcopy(self.menu);m['popupAfter']['allocations'][name]+=100
   with self.assertRaises(ValueError):binding(m,self.native,self.scope)
 def test_each_context_change_refused(self):
  for name in NAMES:
   m=copy.deepcopy(self.menu);c=m['popupAfter']['contexts'][name];c.update(generation=100,present=True,enginePresent=True)
   with self.assertRaises(ValueError):binding(m,self.native,self.scope)
 def test_native_absent_engine_conflict_refused(self):
  m=copy.deepcopy(self.menu);m['popupBefore']['contexts']['window']['enginePresent']=True
  with self.assertRaises(ValueError):binding(m,self.native,self.scope)
 def test_context_boolean_alias_refused(self):
  for name in NAMES:
   for field in('present','enginePresent','generation'):
    m=copy.deepcopy(self.menu);m['popupBefore']['contexts'][name][field]=1 if field!='generation'else True
    with self.assertRaises(ValueError):binding(m,self.native,self.scope)
 def test_null_window_refused(self):
  self.menu['popupBefore']['nativeWindowBound']=False
  with self.assertRaises(ValueError):binding(self.menu,self.native,self.scope)
 def test_engine_before_after_or_external_change_refused(self):
  self.menu['engineAfter']['engineEpoch']=2
  with self.assertRaises(ValueError):engine_pair(self.menu)
  with self.assertRaises(ValueError):popup_pair(self.menu,self.scope)
 def test_fresh_valid_tuple_not_old_current(self):
  for k in('popupBefore','popupAfter'):self.menu[k]['allocations']['window']=100
  with self.assertRaises(ValueError):current(self.menu,self.native,self.scope,self.expected)
 def test_complete_row_retains_full_popup(self):
  m=dict(self.menu,status='complete',sent=True,button=dict(self.menu['button'],enabled=False))
  self.assertTrue(completion_current(m,self.native,self.scope,self.expected))
  m['popupAfter']=copy.deepcopy(m['popupAfter']);m['popupAfter']['allocations']['attached']=99
  with self.assertRaises(ValueError):completion_current(m,self.native,self.scope,self.expected)
 def test_pointer_episode_positive(self):self.assertTrue(episode([],self.rows(),'pointer',self.expected)['observedPressAndRelease'])
 def test_return_episode_positive(self):self.assertTrue(episode([],self.rows('return'),'return',self.expected)['observedPressAndRelease'])
 def test_pending_same_suffix_not_acceptance(self):
  r=self.rows();self.assertIsNone(episode([],r[:1],'pointer',self.expected,allow_pending=True))
  with self.assertRaises(ValueError):episode([],r[:1],'pointer',self.expected)
 def test_intent_and_normal_exit_cannot_release(self):
  c=FrontendCase(self.expected);c.press(self.menu,self.native,self.scope,'pointer')
  for value in(True,dict(pressSent=True,releaseSent=True),dict(exitCode=0)):
   with self.assertRaises(ValueError):c.release(value)
  self.assertFalse(c.released)
 def test_actual_episode_redecoded_before_release(self):
  c=FrontendCase(self.expected);c.press(self.menu,self.native,self.scope,'pointer');proof=episode([],self.rows(),'pointer',self.expected);c.release(proof);self.assertTrue(c.released)
  proof['after'][1]['buttonState']=1
  with self.assertRaises(ValueError):c.release(proof)
 def test_nonfinite_or_fractional_cursor_refused(self):
  for x in(float('nan'),float('inf'),310.5,True):
   r=self.rows();r[1]['native']['cursor'][0]=x
   with self.assertRaises(ValueError):episode([],r,'pointer',self.expected)
 def test_integral_float_cursor_exactly_admitted(self):
  r=self.rows();r[1]['native']['cursor']=[310.0,315.0]
  self.assertTrue(episode([],r,'pointer',self.expected))
 def test_each_bool_numeric_event_refused(self):
  for route in('pointer','return'):
   fields=('sequence','timeMs','button','buttonState')if route=='pointer'else('sequence','timeMs','keycode','keyState','seatKeySymAtObservation')
   for field in fields:
    r=self.rows(route);r[0][field]=True
    with self.assertRaises(ValueError):episode([],r,route,self.expected)
 def test_prefix_eviction_sequence_replacement_and_extra_refused(self):
  r=self.rows();before=[dict(copy.deepcopy(r[0]),sequence=10)]
  for after in(r,[dict(r[0],sequence=1),dict(r[1],sequence=3)],r+[dict(r[1],sequence=3)]):
   with self.assertRaises(ValueError):episode(before if after is r else [],after,'pointer',self.expected)
 def test_unknown_popup_cancellation_refused(self):
  for route in('pointer','return'):
   r=self.rows(route);r[0]['cancelledAtObservation']=True
   with self.assertRaises(ValueError):episode([],r,route,self.expected)
 def test_wrong_layer_or_surface_refused(self):
  for route in('pointer','return'):
   for field,value in [('pointerLayerOwner'if route=='pointer'else'keyboardLayerOwner',None),('pointerSurfacePresent'if route=='pointer'else'keyboardSurfacePresent',False)]:
    r=self.rows(route);r[1]['native'][field]=value
    with self.assertRaises(ValueError):episode([],r,route,self.expected)
 def test_actual_return_resource_and_symbol_required(self):
  for field,value in [('keyboardResourcePresent',False),('keyboardResourcePresent',1)]:
   r=self.rows('return');r[1]['native'][field]=value
   with self.assertRaises(ValueError):episode([],r,'return',self.expected)
  r=self.rows('return');r[0]['seatKeySymAtObservation']=65307
  with self.assertRaises(ValueError):episode([],r,'return',self.expected)
 def controller(self):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
  route=SimpleNamespace(output=Path(tmp.name),session=SimpleNamespace(guard=Mock(),ctl=Mock(return_value='[]')))
  return FrontendCases(route,SimpleNamespace(pid=11),Mock(return_value={'actualProviderVerified':True}),Mock(return_value=json.dumps(self.menu)),{},Mock())
 def test_controller_scope_uses_actual_fixed_query_not_flags(self):
  c=self.controller();self.assertEqual(c.scope(),self.scope);c.scope_reader.assert_not_called();c.ipc_readonly.assert_called_once_with('hoskinson.windows','pinMenuState')
 def test_controller_missing_raw_engine_refuses_before_input(self):
  c=self.controller();c.ipc_readonly.return_value=json.dumps(dict(actualProviderVerified=True,scope=self.scope))
  with self.assertRaises(ValueError):c.scope()
  self.assertEqual(c.report['inputs'],[])
 def test_controller_event_query_route_is_fixed_readonly(self):
  c=self.controller();c.input_rows('return');c.session.ctl.assert_called_once_with('repl','print(hl.plugin.toolkit_held_probe.keyboard_events())')
  with self.assertRaises(ValueError):c.input_rows('titlebar')

if __name__=='__main__':unittest.main()
