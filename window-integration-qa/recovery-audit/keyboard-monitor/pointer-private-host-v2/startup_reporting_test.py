import contextlib,io,json,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import host_acceptance as h
import native_probe_pointer as r
import startup_reporting as s
class StartupTests(unittest.TestCase):
 def good(self):return h.MARKER+'\nOutput WAYLAND-1: configure surface with 3\n'
 def test_live_stdout_succeeds_while_core_file_unflushed(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);stdout=root/'stdout';stdout.write_text(self.good());disk=root/'unflushed';disk.write_bytes(b'');report={};calls=[]
   self.assertTrue(s.live_transport([stdout],lambda:calls.append('guard'),report,seconds=0)['pass_'])
   self.assertEqual(calls,['guard']);self.assertEqual(disk.read_bytes(),b'')
 def test_later_archive_cannot_replace_missing_live_ack(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);live=root/'unflushed';live.write_bytes(b'');(root/'later-archive').write_text(self.good());report={}
   with self.assertRaisesRegex(TimeoutError,'proof unavailable'):s.live_transport([live],lambda:None,report,seconds=0)
   self.assertFalse(report['lastStartupTransport']['configureACKHandlerObserved']);self.assertEqual(report['lastStartupTransport']['files'][0]['bytes'],0)
 def test_real_transport_failure_is_immediate_and_strict(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'stdout';path.write_text(self.good()+'Broken pipe\n')
   with self.assertRaisesRegex(RuntimeError,'transport failure'):s.live_transport([path],lambda:None,{},seconds=100,pause=lambda _:self.fail('must not retry fatal diagnostic'))
 def test_first_error_survives_secondary_cleanup(self):
  report={}
  try:raise TimeoutError('first live ACK failure')
  except Exception as error:s.failure(report,error,'startup')
  first=report['traceback']
  try:raise RuntimeError('secondary cleanup failure')
  except Exception as error:s.failure(report,error,'cleanup')
  self.assertIn('first live ACK failure',report['error']);self.assertEqual(report['traceback'],first);self.assertEqual(len(report['failures']),2)
 def test_no_receiver_cleanup_preserves_failure(self):
  report={'error':'first'}
  with tempfile.TemporaryDirectory() as temp:
   s.archive_terminal(None,Path(temp),report);s.archive_terminal(Path(temp)/'not-created',Path(temp),report)
   self.assertEqual(report['error'],'first');self.assertFalse(report['terminalReceiverBytesAvailable']);self.assertFalse((Path(temp)/'native-terminal.bin').exists())
 def test_summary_never_prints_full_state_maps_or_catalog(self):
  report=dict(result='failed',checks=[],restoration={},error='x'*100000,hostEvidence={'maps':'private-raw-map'*100000},before={'catalogs':'private-catalog'*100000})
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'report.json';path.write_text(json.dumps(report));text=json.dumps(s.summary(report,path))
  self.assertLess(len(text),4096);self.assertNotIn('private-raw-map',text);self.assertNotIn('private-catalog',text)
 def test_private_stdout_logging_enabled_without_environment_mutation(self):
  self.assertIn(b'debug={disable_logs=false,enable_stdout_logs=true}',r.config_bytes())
 def test_actual_execute_early_failure_has_no_clients_and_preserves_primary(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);logs=root/'owned-host';logs.mkdir();archive=logs/'hyprland.log';archive.write_text(self.good());(logs/'weston-renderer.log').write_text('private parent')
   (root/'pointer-frozen-stage-report.json').write_text(json.dumps({'hostAdapter':str(r.HOST_ROOT)}))
   class Session:
    def __init__(self,**kwargs):
     self.env={'XDG_RUNTIME_DIR':temp,**{'XDG_'+name.upper()+'_HOME':str(root/name) for name in ('config','data','cache')}};self.evidence=dict(runtime=temp,compositorPID=123,compositorStart='456',compositorConfig=str(root/'private.lua'),hyprland={'log':str(archive)},signature='private',archivedRuntime=[{'archive':str(archive)}]);(root/'private.lua').write_text('private')
     self.host=SimpleNamespace(processes=[],descendants=lambda:[])
    def __enter__(self):return self
    def __exit__(self,*args):self.evidence['runtimeGone']=True
    def guard(self):pass
   before={'reader':'false','files':{'visible':True}}
   observer=SimpleNamespace(capture=lambda:before,compare=lambda a,b:{'mainExact':True})
   monitor={'width':1280,'height':800,'scale':1.25}
   def data(env,*args):return [monitor] if args[0]=='monitors' else {'bool':False}
   actual_library=r.LIB
   with patch.object(r,'HERE',root),patch.object(r,'REPORT',root/'report.json'),patch.object(r,'LIB',actual_library),patch.object(r.qa,'require_qa_scope'),patch.object(r,'MainObserver',return_value=observer),patch.object(r,'verify_manifest'),patch.object(r,'manifest_unchanged',return_value=True),patch.object(r.HOST,'PrivateHyprSession',Session),patch.object(r.HOST.original,'mapped_files',return_value={'files':{str(r.QA_ROOT/'aquamarine-nested-lifecycle-v1/prefix/lib/libaquamarine.so.0.15.0'):h.AQ_SHA}}),patch.object(r.host_acceptance,'ipc_complete',return_value=True),patch.object(r,'data',side_effect=data),patch.object(r,'ctl',return_value=''),patch.object(r.startup_reporting,'live_transport',side_effect=TimeoutError('genuine early live ACK unavailable')),patch.object(r.subprocess,'Popen',side_effect=AssertionError('client must not start')),contextlib.redirect_stdout(io.StringIO()) as stdout:
    self.assertEqual(r.execute(),1)
   result=json.loads((root/'report.json').read_text());self.assertIn('genuine early live ACK unavailable',result['error']);self.assertEqual(len(result['failures']),1);self.assertFalse(result['terminalReceiverBytesAvailable']);self.assertEqual(result['ownedFixtureProcesses'],[]);self.assertLess(len(stdout.getvalue()),4096)
if __name__=='__main__':unittest.main()
