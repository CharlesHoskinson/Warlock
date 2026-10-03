"""Unprojected B19 collector CPU + owned Unix-socket observations, no GUI."""
import ast,base64,json,os,socket,subprocess,sys,tempfile,threading,unittest
from pathlib import Path
from types import SimpleNamespace
import output_readiness as o
B=Path(__file__).resolve().parent;OLD=B.with_name('toolkit-held-matrix-v12')
EXACT=[dict(o.FIELDS,name='WAYLAND-1')]
class Clock:
 def __init__(self):self.now=0.
 def __call__(self):return self.now
 def sleep(self,d):self.now+=d
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.out=Path(self.tmp.name)/'proof.json';self.clock=Clock();self.guard_count=0
  def guard():self.guard_count+=1
  self.s=SimpleNamespace(evidence={'browserStartupBudget':{'launchReturnedMonotonic':0.,'deadlineMonotonic':15.,'pid':os.getpid()},'compositorPID':os.getpid()},guard=guard)
 def tearDown(self):self.tmp.cleanup()
 def run_rows(self,rows,change=None):
  queue=list(rows)
  def reader(s,d,row,persist,clock):
   value=queue.pop(0);row['completeServerEOF']=True
   if change:change(s,row)
   return value if isinstance(value,bytes) else json.dumps(value).encode()
  return o.collect(self.s,self.out,self.clock,self.clock.sleep,reader)
 def failure(self,rows,pattern=None,change=None):
  with self.assertRaisesRegex((RuntimeError,ValueError,UnicodeError),pattern or'.'):self.run_rows(rows,change)
  r=json.loads(self.out.read_text());self.assertFalse(r['accepted']);self.assertFalse(r['originalFeatureAcceptance']);return r
 def test_exact_no_original_credit(self):
  r=self.run_rows([EXACT]);self.assertTrue(r['accepted']);self.assertFalse(r['originalFeatureAcceptance']);self.assertEqual(self.guard_count,1);self.assertEqual(self.out.stat().st_mode&0o777,0o600)
 def test_empty_to_exact_keeps_deadline(self):
  r=self.run_rows([[],EXACT]);self.assertEqual(len(r['observations']),2);self.assertEqual(r['startupBudget']['deadlineMonotonic'],15.);self.assertGreater(self.clock.now,0)
 def test_wrong_monitor_terminal_raw_before_assert(self):
  r=self.failure([[dict(o.FIELDS,width=1920)]]);self.assertEqual(r['observations'][0]['actualOutputs'][0]['width'],1920);self.assertEqual(json.loads(base64.b64decode(r['observations'][0]['rawReplyBase64']))[0]['width'],1920)
 def test_extra_monitor_refused(self):self.failure([EXACT+EXACT])
 def test_nonlist_refused_and_retained(self):self.assertEqual(self.failure([{}])['observations'][0]['actualOutputs'],{})
 def test_malformed_reply_raw_retained(self):self.assertEqual(base64.b64decode(self.failure([b'{bad'])['observations'][0]['rawReplyBase64']),b'{bad')
 def test_invalid_utf8_retained(self):self.failure([b'\xff'])
 def test_bool_not_numeric_output_authority(self):
  for key in o.FIELDS:
   value=dict(o.FIELDS);value[key]=True;self.assertFalse(o.exact_outputs([value]))
 def test_empty_deadline_expires_no_reset(self):
  self.clock.now=14.99;r=self.failure([[]],'deadline');self.assertEqual(r['startupBudget']['deadlineMonotonic'],15.)
 def test_exact_after_deadline_refused(self):self.failure([EXACT],'deadline',lambda s,r:setattr(self.clock,'now',15.))
 def test_expired_before_any_query(self):
  self.clock.now=15.;r=self.failure([],'deadline');self.assertEqual(r['observations'],[])
 def test_missing_eof_refused(self):self.failure([EXACT],'Complete bounded',lambda s,r:r.update(completeServerEOF=False))
 def test_oversize_refused_raw_retained(self):self.assertEqual(self.failure([b' '*65537])['observations'][0]['replyBytes'],65537)
 def test_bad_budget_refused(self):
  for value in (True,float('nan'),-1.,None):
   self.s.evidence['browserStartupBudget']['launchReturnedMonotonic']=value;self.failure([],'budget')
 def test_changed_final_guard_refuses(self):
  self.s.guard=lambda:(_ for _ in ()).throw(RuntimeError('changed lifetime'));self.failure([EXACT],'changed lifetime')
 def test_source_inverse_original_runner_exact(self):
  from source_conservation import reconstructed_runner
  self.assertEqual(reconstructed_runner(),(OLD/'run_native.py').read_bytes())
  with self.assertRaises(RuntimeError):reconstructed_runner((B/'run_native.py').read_bytes()+b'\n#extra')
 def test_all_original_runtime_exact(self):
  for n in ('helper_observer.py','helper_setup.py','evaluation_setup.py','qs_lifecycle.py','delegate_diagnostics.py','held_route.py','held_controller.py','observations.py','frontend_route.py','scroll_route.py','input_control.py','private_shell.py','service_observer.py','matrix.json'):
   self.assertEqual((B/n).read_bytes(),(OLD/n).read_bytes(),n)
 def test_original_backend_gate_and_order_exact(self):
  source=(B/'run_native.py').read_text();before=(OLD/'run_native.py').read_text()
  line=next(line for line in before.splitlines() if 'Actual private output/backend mismatch' in line)
  self.assertIn(line,source);self.assertLess(source.index('output_readiness.collect('),source.index(line));self.assertLess(source.index(line),source.index("session.ctl('plugin','load'"))
 def test_formal_before_runtime(self):
  r=json.loads((B/'output-formal-before-runtime.json').read_text());self.assertEqual(r['result'],'pass');self.assertFalse(r['nativeLaunch'])
 def test_real_fixed_ipc_peer_eof_raw(self):self.real_socket()
 def test_real_wrong_kernel_peer_refused_before_request(self):self.real_socket(wrong_pid=True)
 def test_real_changed_after_guard_refused(self):self.real_socket(change_after=True)
 def real_socket(self,wrong_pid=False,change_after=False):
  from private_output_host import original as host
  runtime=Path(self.tmp.name);p=runtime/'hypr'/'private'/'.socket.sock';p.parent.mkdir(parents=True)
  server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(str(p));server.listen(1);server.settimeout(3);requests=[]
  child=subprocess.Popen([sys.executable,'-c','import sys;sys.stdin.read()'],stdin=subprocess.PIPE)if wrong_pid else None
  def serve():
   with server:
    conn,_=server.accept()
    with conn:
     raw=conn.recv(64);requests.append(raw)
     if raw:conn.sendall(json.dumps(EXACT).encode())
  thread=threading.Thread(target=serve);thread.start();count=0
  def guard():
   nonlocal count
   count+=1
   if change_after and count>=3:raise RuntimeError('changed actual owned lifetime')
  self.s=SimpleNamespace(host=SimpleNamespace(runtime=runtime),env={'HYPRLAND_INSTANCE_SIGNATURE':'private','WAYLAND_DISPLAY':'wayland-1','XDG_RUNTIME_DIR':str(runtime),'DBUS_SESSION_BUS_ADDRESS':'unix:path='+str(runtime/'bus')},evidence={'compositorPID':child.pid if child else os.getpid(),'signature':'private','ipcReadiness':[{'path':str(p)}],'browserStartupBudget':{'launchReturnedMonotonic':0.,'deadlineMonotonic':15.}},sockets=[host.socket_identity(p,runtime)],child_identity=host.process(os.getpid()),guard=guard)
  row={};persist=lambda:None
  try:
   if wrong_pid or change_after:
    with self.assertRaisesRegex(RuntimeError,'peer|lifetime'):o.query(self.s,15.,row,persist,self.clock)
    self.assertIn('queryError',row)
   else:
    raw=o.query(self.s,15.,row,persist,self.clock);self.assertEqual(json.loads(raw),EXACT);self.assertTrue(row['completeServerEOF']);self.assertEqual(row['peer']['pid'],os.getpid());self.assertEqual(base64.b64decode(row['rawReplyBase64']),raw)
  finally:
   thread.join(4);self.assertFalse(thread.is_alive())
   if child:child.stdin.close();child.wait(timeout=3);self.assertEqual(child.returncode,0)
  self.assertEqual(requests,[b''if wrong_pid else b'j/monitors'])
if __name__=='__main__':unittest.main()
