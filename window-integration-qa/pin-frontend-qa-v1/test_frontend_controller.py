"""CPU controlled observations for the unprojected controller; no GUI authority."""
import copy,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
from frontend_cases import FrontendCases
from frontend_authority import binding,completion_current,focus_projection,one_native_event,shell_requester
import test_frontend_authority as fixtures

class Controller(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.fixture=fixtures.Tests();self.fixture.setUp();self.f=self.fixture
  self.route=SimpleNamespace(output=Path(self.tmp.name),session=SimpleNamespace(guard=Mock()),pointer=None,report={})
  self.c=FrontendCases(self.route,SimpleNamespace(pid=11),Mock(),Mock(),{},Mock())
 def test_registered_shell_not_first_root(self):
  config=dict(requestRoots=[dict(role='harness',identity=dict(self.f.requester,pid=20)),dict(role='shell',identity=self.f.requester)])
  self.assertEqual(shell_requester(config,11),self.f.requester)
 def test_ambiguous_or_different_shell_refuses(self):
  r=dict(role='shell',identity=self.f.requester)
  for roots in([r,r],[dict(r,identity=dict(self.f.requester,pid=12))],[]):
   with self.assertRaises(ValueError):shell_requester(dict(requestRoots=roots),11)
 def done(self):return dict(self.f.menu,status='complete',sent=True,button=dict(self.f.menu['button'],enabled=False))
 def test_same_completed_row_disabled_expected(self):self.assertTrue(completion_current(self.done(),self.f.native,self.f.scope,self.f.expected))
 def test_completed_row_layout_label_replacement_refuses(self):
  for k,v in [('width',219),('label','Pin to taskbar'),('visible',False),('enabled',True)]:
   d=self.done();d['button'][k]=v
   with self.assertRaises(ValueError):completion_current(d,self.f.native,self.f.scope,self.f.expected)
 def test_completed_sent_bool_or_nonce_bool_refuses(self):
  for k,v in [('sent',1),('nonce',True)]:
   d=self.done();d[k]=v
   with self.assertRaises(ValueError):completion_current(d,self.f.native,self.f.scope,self.f.expected)
 def scene(self):return dict(native=dict(nativeFocus=self.f.native['nativeFocus']),seat=dict(keyboardOwner=None,coreNativeFocus=self.f.native['nativeFocus'],keyboardSurfacePresent=True,keyboardResourcePresent=True,activeLayout=0,keymapOverridden=False))
 def test_actual_keyboard_diagnostics_not_focus_authority(self):
  before=self.scene();after=copy.deepcopy(before);after['seat'].update(activeLayout=1,keymapOverridden=True)
  self.assertEqual(focus_projection(before),focus_projection(after))
 def test_actual_seat_owner_or_surface_change_refuses_preservation(self):
  before=self.scene();after=copy.deepcopy(before);after['seat']['keyboardOwner']=self.f.token
  self.assertNotEqual(focus_projection(before),focus_projection(after))
  after['seat']['keyboardSurfacePresent']=1
  with self.assertRaises(ValueError):focus_projection(after)
 def test_exact_one_native_event(self):
  r=self.f.receipt['rawNativeResult'];self.assertEqual(one_native_event([], [r],r),r)
  for rows in([],[r,r],[dict(r,desiredPinned=False)]):
   with self.assertRaises(ValueError):one_native_event([],rows,r)
 def test_bounded_observation_persists_actual_exception_before_refusal(self):
  def refuse():raise RuntimeError('raw failure')
  with self.assertRaises(RuntimeError):self.c.observe('actual raw phase',refuse)
  row=json.loads((self.c.output/'report.json').read_text())['observations'][0]
  self.assertEqual(row['label'],'actual raw phase');self.assertIn('raw failure',row['error'])
 def test_missing_provider_refuses_without_native_or_input(self):
  self.c.scope_reader=Mock(return_value=dict(processId=11,scope=self.f.scope))
  with self.assertRaises(RuntimeError):self.c.scope()
  self.assertFalse(self.c.report['engineAuthorityProvided']);self.assertEqual(self.c.report['inputs'],[])
 def test_invalid_opener_and_route_refuse_before_any_input(self):
  for opener,route in [('ipc','pointer'),('right','native')]:
   with self.assertRaises(ValueError):self.c.toggle('owner',opener,route)
  self.assertEqual(self.c.report['inputs'],[]);self.assertEqual(self.c.report['setupInputs'],[])
 def test_pointer_missing_refuses_before_button_bytes(self):
  f=Mock()
  with self.assertRaises(RuntimeError):self.c.buttons(272,False,f)
  f.assert_not_called();self.assertEqual(self.c.report['inputs'],[])
 def test_press_revalidation_refusal_prevents_actual_write(self):
  process=SimpleNamespace(stdin=Mock());self.c.pointer_live=Mock(return_value=process)
  with self.assertRaises(ValueError):self.c.buttons(272,False,lambda:(_ for _ in()).throw(ValueError('changed')))
  process.stdin.write.assert_not_called();self.assertEqual(self.c.report['inputs'],[])
 def test_integer_button_tokens_and_balanced_actual_writes(self):
  process=SimpleNamespace(stdin=Mock());self.c.pointer_live=Mock(return_value=process);self.c.native=Mock(return_value=self.f.native)
  row=self.c.buttons(272,False,Mock());self.assertEqual([x.args[0]for x in process.stdin.write.call_args_list],['button 272 1\n','button 272 0\n']);self.assertTrue(row['releaseSent']);self.assertFalse(self.route.held)
 def test_readonly_queries_no_menu_opener_or_action(self):
  for q in('cycle','pin','open','toggle'):
   with self.assertRaises(ValueError):self.c.query(q)
  self.c.ipc_readonly.assert_not_called()
if __name__=='__main__':unittest.main()
