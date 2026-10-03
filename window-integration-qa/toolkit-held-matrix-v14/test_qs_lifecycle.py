"""Source-backed CLI refusals and real owned nongraphical process authority tests."""
from pathlib import Path
import copy,json,os,subprocess,tempfile,time,unittest
from unittest.mock import patch
import helper_observer as h
import qs_lifecycle as q
ROW=dict(id='abc123',pid=123,shell_id='a'*32,config_path='/owned/shell.qml',launch_time='2026-10-01T17:08:51')
def result(stdout='',stderr='',code=0):return subprocess.CompletedProcess(['owned-read-only-fixture'],code,stdout,stderr)
class QS(unittest.TestCase):
 def test_genuine_source_empty_text_distinct_from_json_rows(self):
  self.assertEqual(q.parse_instances(result('No running instances.\n')),[])
  self.assertEqual(q.parse_instances(result(json.dumps([ROW]))),[ROW])
 def test_unknown_empty_malformed_duplicate_keys_and_fields_refused(self):
  for stdout in ('','[]','warning\n','{}',json.dumps([dict(ROW,pid=True)]),json.dumps([dict(ROW,extra=1)]),json.dumps([ROW,ROW]),json.dumps([ROW]).replace('"pid": 123','"pid": 123, "pid": 124')):
   with self.assertRaises(q.Refused,msg=stdout):q.parse_instances(result(stdout))
  with self.assertRaises(q.Refused):q.parse_instances(result('No running instances.\n',stderr='foreign warning\n'))
 def test_only_exact_installed_launcher_startup_replies_pending(self):
  self.assertEqual(q.ping_state(result('ok\n')),'ready')
  for text in ('omarchy-shell is not running\n','omarchy-shell is not ready\n'):self.assertEqual(q.ping_state(result(stderr=text,code=1)),'pending')
  for reply in (result('Target not found.\n'),result(stderr='omarchy-shell is not responding\n',code=1),result(stderr='unknown\n',code=1),result('ok'),result('ok\n',stderr='warning\n')):
   with self.assertRaises(q.Refused):q.ping_state(reply)
 def owned(self,folder):
  root=Path(folder);script=root/'owned.py';script.write_text('import sys\nprint("owned CPU fixture ready",flush=True)\nfor line in sys.stdin:\n if line.strip()=="quit":break\n');config=root/'shell.qml';config.write_text('owned nongraphical authority test, never loaded\n')
  env=dict(os.environ,HOME=folder,XDG_RUNTIME_DIR=folder,HYPRLAND_INSTANCE_SIGNATURE='owned',WAYLAND_DISPLAY='owned',OMARCHY_PATH=folder,WINDOW_QA_HELPER_CONFIG=str(root/'helper.json'),WINDOW_MOTION_NATIVE_CONFIG=str(root/'frontend.json'),DBUS_SESSION_BUS_ADDRESS='unix:path='+folder+'/bus')
  command=['/usr/bin/python3',str(script)];process=subprocess.Popen(command,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
  # Test fixture body receipt only; actual QS lifecycle/deadlines are unchanged.
  import select
  ready,_,_=select.select([process.stdout],[],[],3)
  if not ready or process.stdout.readline()!='owned CPU fixture ready\n':
   self.dispose(process);raise AssertionError('Actual nongraphical fixture ready receipt missing')
  authority=q.Lifecycle(process,h.process(process.pid),command,env,lambda:None,config)
  return process,authority
 def dispose(self,p):
  if p.poll() is None:p.stdin.write('quit\n');p.stdin.flush();p.wait(timeout=3)
  for stream in (p.stdin,p.stdout,p.stderr):stream.close()
 def test_actual_owned_process_pinning_allows_only_bounded_known_startup(self):
  with tempfile.TemporaryDirectory() as folder:
   p,authority=self.owned(folder)
   try:
    authority.guard();replies=[result(stderr='omarchy-shell is not running\n',code=1),result(stderr='omarchy-shell is not ready\n',code=1),result('ok\n')]
    with patch.object(authority,'invoke',side_effect=replies):self.assertTrue(authority.await_ready(seconds=1)['exactReady'])
    with patch.object(authority,'invoke',return_value=result(stderr='unknown\n',code=1)):
     with self.assertRaises(q.Refused):authority.await_ready(seconds=1)
   finally:self.dispose(p)
 def test_actual_source_and_environment_mutation_refused_before_probe(self):
  with tempfile.TemporaryDirectory() as folder:
   p,authority=self.owned(folder)
   try:
    authority.guard();authority.env=dict(authority.env,HOME='/different')
    with self.assertRaisesRegex(q.Refused,'environment'):authority.guard()
    authority.env['HOME']=folder;authority.config.write_text('changed')
    with self.assertRaisesRegex(q.Refused,'source'):authority.guard()
   finally:self.dispose(p)
 def test_dead_original_startup_is_terminal_no_fabricated_ready(self):
  with tempfile.TemporaryDirectory() as folder:
   p,authority=self.owned(folder)
   try:
    self.dispose(p)
    with self.assertRaisesRegex(q.Refused,'exited'):authority.await_ready(seconds=1)
    answer=authority.close();self.assertFalse(answer['normalQuit']);self.assertFalse(answer['ready']);self.assertTrue(answer['naturallyExitedBeforeClose'])
   finally:
    if p.poll() is None:self.dispose(p)
 def test_exact_selected_row_required_before_any_kill(self):
  with tempfile.TemporaryDirectory() as folder:
   p,authority=self.owned(folder)
   try:
    with patch.object(authority,'invoke',return_value=result('No running instances.\n')):self.assertIsNone(authority.selected())
    bad=dict(ROW,pid=p.pid,config_path='/different/shell.qml')
    with patch.object(authority,'invoke',return_value=result(json.dumps([bad]))):
     with self.assertRaisesRegex(q.Refused,'different config'):authority.selected()
    self.assertFalse(authority.kill_sent)
   finally:self.dispose(p)

 def test_real_passed_pipe_exec_gate_keeps_exact_pid_start_before_any_probe(self):
  import sys
  sys.path.insert(0,str(q.B.parent));import qa_launch
  try:qa_launch.require_qa_scope()
  except RuntimeError:self.skipTest('Exact real exec gate requires actual QA scope/core1')
  with qa_launch.owned_runtime() as folder:
   previous,authority=self.owned(folder);command=authority.command;env=authority.env;config=authority.config;self.dispose(previous)
   read_fd,write_fd=os.pipe2(os.O_CLOEXEC);gate=['/usr/bin/python3',str(q.B/'exec_gate.py'),str(read_fd),'--',*command]
   p=subprocess.Popen(gate,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,pass_fds=(read_fd,),start_new_session=True);os.close(read_fd)
   try:
    captured=h.process(p.pid);authority=q.Lifecycle(p,captured,command,env,lambda:None,config,gate_command=gate)
    with self.assertRaises(q.Pending):authority.guard(allow_gate=True)
    os.write(write_fd,b'1');os.close(write_fd);write_fd=-1
    deadline=time.monotonic()+2
    while time.monotonic()<deadline:
     try:authority.guard(allow_gate=True);break
     except q.Pending:time.sleep(.01)
    self.assertTrue(authority.final);self.assertEqual(h.process(p.pid)['start'],captured['start'])
   finally:
    if write_fd!=-1:os.close(write_fd)
    self.dispose(p)
 def test_known_startup_has_a_real_deadline(self):
  with tempfile.TemporaryDirectory() as folder:
   p,authority=self.owned(folder)
   try:
    start=time.monotonic()
    with patch.object(authority,'invoke',return_value=result(stderr='omarchy-shell is not ready\n',code=1)):
     with self.assertRaisesRegex(q.Refused,'deadline'):authority.await_ready(seconds=.06)
    self.assertLess(time.monotonic()-start,.5)
   finally:self.dispose(p)

if __name__=='__main__':unittest.main(verbosity=2)
