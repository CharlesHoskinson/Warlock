"""CPU-only evidence persistence and exact diagnostic source projection."""
import ast,base64,copy,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import continuation_evidence as c
from preservation_projection import project
B=Path(__file__).resolve().parent;OLD=B.with_name('browser-files-flow-v16')
IDENTITY={'address':'0xabcd','stableId':'0123','pid':123}
class Obs:
 def __init__(self):
  self.environment={'HYPRLAND_INSTANCE_SIGNATURE':'private-instance'};self.starts=['456','456'];self.clients=[dict(IDENTITY)]
  self.seat={'keyboardSurfacePresent':True,'keyboardOwner':dict(IDENTITY),'coreNativeFocus':dict(IDENTITY)}
  self.events=[];self.calls=[];self.error=None
 def start(self,pid):return self.starts.pop(0) if len(self.starts)>1 else self.starts[0]
 def data(self,name):self.calls.append(name);return self.clients if name=='clients' else {'keyboards':[]}
 def run(self,*args):
  self.calls.append(args)
  if self.error:raise self.error
  if 'keyboard_events' in args[-1]:return json.dumps(self.events)
  if 'keyboard_state' in args[-1]:return json.dumps(self.seat)
  return json.dumps({'str':'us'})
class Evidence(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'evidence.json';self.obs=Obs();self.native={'nativeFocus':dict(IDENTITY)}
  self.e=c.ContinuationEvidence(self.path,self.obs,lambda:copy.deepcopy(self.native),123,'456',IDENTITY,'exact-cdp-session')
 def saved(self):return json.loads(self.path.read_text())
 def test_private_file_mode_and_no_feature_acceptance(self):
  self.assertEqual(self.path.stat().st_mode&0o7777,0o600);self.assertFalse(self.saved()['originalFeatureAcceptance'])
 def test_actual_dom_saved_before_after_with_exact_identity(self):
  row=self.e.begin_dom();self.e.end_dom(row,{'value':'wrong','selection':[0,0]})
  r=self.saved()['samples'][0];self.assertEqual(r['dom']['value'],'wrong')
  for phase in ('before','after'):self.assertTrue(r[phase]['sameBrowserLifetime']);self.assertTrue(r[phase]['samePrivateSelector'])
 def test_failed_dom_query_error_retained(self):
  row=self.e.begin_dom();self.e.dom_error(row,RuntimeError('raw CDP failure'))
  self.assertEqual(self.saved()['samples'][0]['errors']['dom']['error'],'raw CDP failure')
 def test_missing_keyboard_owner_stays_missing(self):
  self.obs.seat['keyboardOwner']=None;row=self.e.begin_dom();self.assertIsNone(row['before']['seatKeyboard']['keyboardOwner'])
 def test_foreign_keyboard_owner_not_repaired_from_core_focus(self):
  self.obs.seat['keyboardOwner']={**IDENTITY,'pid':124};row=self.e.begin_dom();self.assertEqual(row['before']['seatKeyboard']['keyboardOwner']['pid'],124)
  self.assertEqual(row['before']['native']['nativeFocus']['pid'],123)
 def test_missing_surface_and_resource_saved_separately(self):
  self.obs.seat.update(keyboardSurfacePresent=False,keyboardResourcePresent=False);row=self.e.begin_dom();self.assertFalse(row['before']['seatKeyboard']['keyboardSurfacePresent'])
 def test_changed_browser_start_refuses_after_raw_fields_saved(self):
  self.obs.starts=['456','457']
  with self.assertRaises(AssertionError):self.e.begin_dom()
  row=self.saved()['samples'][0]['before'];self.assertEqual(row['browserProcessStartAfter'],'457');self.assertIn('seatKeyboard',row);self.assertFalse(row['sameBrowserLifetime'])
 def test_reused_native_identity_refuses(self):
  self.obs.clients=[{**IDENTITY,'stableId':'0124'}]
  with self.assertRaises(AssertionError):self.e.begin_dom()
  self.assertEqual(self.saved()['samples'][0]['before']['actualPrivateClients'][0]['stableId'],'0124')
 def test_duplicate_client_refuses(self):
  self.obs.clients*=2
  with self.assertRaises(AssertionError):self.e.begin_dom()
 def test_missing_client_refuses(self):
  self.obs.clients=[]
  with self.assertRaises(AssertionError):self.e.begin_dom()
 def test_changed_private_selector_refuses(self):
  self.obs.environment['HYPRLAND_INSTANCE_SIGNATURE']='another-private'
  with self.assertRaises(AssertionError):self.e.begin_dom()
  self.assertFalse(self.saved()['samples'][0]['before']['samePrivateSelector']);self.assertEqual(self.obs.calls,[])
 def test_read_error_is_saved_before_rethrow(self):
  self.obs.error=PermissionError(13,'private query refused')
  with self.assertRaises(PermissionError):self.e.begin_dom()
  error=self.saved()['samples'][0]['before']['errors']['seatKeyboardRaw'];self.assertEqual(error['errno'],13)
 def test_malformed_keyboard_json_is_not_repaired(self):
  self.obs.run=lambda *a:'{broken'
  with self.assertRaises(json.JSONDecodeError):self.e.begin_dom()
  self.assertEqual(self.saved()['samples'][0]['before']['errors']['seatKeyboard']['type'],'JSONDecodeError');self.assertEqual(self.saved()['samples'][0]['before']['seatKeyboardRaw'],'{broken')
 def test_every_wrong_dom_poll_kept(self):
  for n in range(4):
   row=self.e.begin_dom();self.e.end_dom(row,{'value':str(n)})
  self.assertEqual([r['dom']['value']for r in self.saved()['samples']],['0','1','2','3'])
 def test_prepare_records_only_selected_env_and_original_caption(self):
  self.e.prepare({'active':'draft','selection':[29,29]},'expected','-continued0',{'HOME':'private-home','SECRET':'never-record'})
  saved=self.saved();self.assertNotIn('SECRET',saved['selectedEnvironment']);self.assertEqual(saved['acceptedCaptionDom']['selection'],[29,29]);self.assertEqual(saved['expectedValue'],'expected')
 def test_events_raw_state_not_delivery_acceptance(self):
  self.obs.events=[{'keycode':30,'cancelledAtObservation':False,'seat':{'keyboardOwner':None}}];row=self.e.begin_dom();self.assertEqual(row['before']['keyboardEvents'],self.obs.events);self.assertFalse(self.saved()['originalFeatureAcceptance'])
 def test_actual_harmless_child_kernel_argv_exe_lifetime_normal_exit(self):
  command=['/usr/bin/python3','-c','import time;time.sleep(.2);print("CPU only")']
  result=self.e.run_wtype(command,dict(os.environ));record=self.saved()['commands'][0]
  self.assertEqual(result.returncode,0);self.assertEqual(record['command'],command);self.assertEqual(record['stdout'],'CPU only\n');self.assertTrue(record['originalProcessGoneAfterWait'])
  raw=base64.b64decode(record['actualOwnedProcess']['rawCmdlineBase64']);self.assertEqual(raw.split(b'\0')[:-1],[s.encode()for s in command]);self.assertTrue(record['actualOwnedProcess']['lifetimeBefore']);self.assertTrue(record['actualOwnedProcess']['lifetimeAfter'])
  self.assertIn('python3',record['actualOwnedProcess']['exe'])
 def test_nonzero_child_not_reported_normal(self):
  result=self.e.run_wtype(['/usr/bin/python3','-c','import time;time.sleep(.1);raise SystemExit(7)'],dict(os.environ))
  self.assertEqual(result.returncode,7);self.assertFalse(self.saved()['commands'][0]['normalExit'])
 def test_timeout_preserves_original_kill_policy_and_no_normal_acceptance(self):
  process=unittest.mock.MagicMock();process.pid=os.getpid();process.__enter__.return_value=process
  process.communicate.side_effect=[subprocess.TimeoutExpired(['fixed-wtype'],12),('','')]
  with patch.object(c.subprocess,'Popen',return_value=process):
   with self.assertRaises(subprocess.TimeoutExpired):self.e.run_wtype(['fixed-wtype'],{})
  process.kill.assert_called_once();record=self.saved()['commands'][0];self.assertTrue(record['forcedTimeoutCleanup']);self.assertNotIn('normalExit',record)
class Source(unittest.TestCase):
 def test_exact_inverse_restores_v16_runtime_bytes(self):
  for name in ('private_session.py','run_native.py'):self.assertEqual(project(B/name,(B/name).read_text()),(OLD/name).read_text(),name)
 def test_original15_check_asts_and_continuation_equality_unchanged(self):
  def checks(p):return[ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(p.read_text()))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='check']
  self.assertEqual(checks(B/'private_session.py'),checks(OLD/'private_session.py'))
  exact="final=wait(lambda:dom() if dom()['value']==expected else None,'actual continuation at retained caret')"
  self.assertIn(exact,(B/'private_session.py').read_text())
 def test_all_old_runtime_bytefiles_except_narrow_additions_exact(self):
  for p in [*OLD.glob('*.py'),*OLD.glob('*.qnt')]:
   if p.name not in {'private_session.py','run_native.py','metrics_offline.py','freeze_packet.py'}:self.assertEqual((B/p.name).read_bytes(),p.read_bytes(),p.name)
 def test_all_real_product_and_readonly_protocol_exact(self):
  for p in [*(OLD/'files-app').rglob('*'),OLD/'cdp_readonly.py',OLD/'compose.html',OLD/'nested-qt.lua']:
   if p.is_file():self.assertEqual((B/p.relative_to(OLD)).read_bytes(),p.read_bytes(),str(p))
 def test_dom_is_persisted_before_original_url_check(self):
  s=(B/'private_session.py').read_text();part=s[s.index(' def dom():'):s.index(' def capture_processes')]
  self.assertLess(part.index('continuation_trace.end_dom'),part.index("assert value['url']"));self.assertNotIn('focus(',part)
 def test_same_wtype_text_argv_env_timeout_with_no_new_input_action(self):
  s=(B/'private_session.py').read_text();part=s[s.index(' def type_text'):s.index(' def browser_rect')]
  self.assertIn("continuation_trace.run_wtype(['/usr/bin/wtype','-d','20','--',text],env)",part)
  helper=(B/'continuation_evidence.py').read_text();self.assertIn('process.communicate(timeout=12)',helper);self.assertNotIn('focus',helper);self.assertNotIn('keyboard.send',helper)
 def test_projection_shape_changes_refuse(self):
  with self.assertRaises(AssertionError):project(B/'private_session.py',(B/'private_session.py').read_text().replace('from continuation_evidence import ContinuationEvidence','from continuation_evidence import Different'))
if __name__=='__main__':unittest.main()
