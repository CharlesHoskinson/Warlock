"""Unprojected actual C/XKB plans and CPU-only protocol shim; no native/GUI input."""
import json,os,subprocess,tempfile,threading,socket,unittest,stat,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent
WIRE={45:12,48:11,49:2,50:3,51:4,52:5,53:6,54:7,55:8,56:9,57:10,97:30,98:48,99:46,100:32,101:18,102:33,103:34,104:35,105:23,106:36,107:37,108:38,109:50,110:49,111:24,112:25,113:16,114:19,115:31,116:20,117:22,118:47,119:17,120:45,121:21,122:44,65361:105}
def start(pid):return(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]
class Physical(unittest.TestCase):
 def plan(self,args):return subprocess.run([str(B/'physical-keyboard'),'--plan',*args],capture_output=True,text=True,timeout=3,env={})
 def test_actual_whole_alphabet_numeric_physical_and_symbols(self):
  text='-0123456789abcdefghijklmnopqrstuvwxyz';p=self.plan(['-d','20','--',text]);self.assertEqual(p.returncode,0,p.stderr);r=json.loads(p.stdout);self.assertTrue(r['cpuOnly']);self.assertEqual([x['symbol']for x in r['plan']],list(map(ord,text)));self.assertEqual(len(r['plan']),37)
  for row in r['plan']:self.assertEqual(row['wire'],WIRE[row['symbol']]);self.assertEqual(row['xkb'],row['wire']+8)
 def test_exact_original_continuation_not_escape(self):
  p=self.plan(['-d','20','--','-continued0']);self.assertEqual(p.returncode,0,p.stderr);r=json.loads(p.stdout);self.assertEqual(r['plan'][0],{'symbol':45,'wire':12,'xkb':20,'name':'AE11'});self.assertEqual(len(r['plan']),11)
 def test_exact_original_draft_plan(self):
  text='private-draft-attempt-1-3511b01d';r=json.loads(self.plan(['-d','20','--',text]).stdout);self.assertEqual([x['symbol']for x in r['plan']],list(map(ord,text)))
 def test_exact_three_physical_left(self):
  p=self.plan(['-d','20','-k','Left','-k','Left','-k','Left']);self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(json.loads(p.stdout)['plan'],[{'symbol':65361,'wire':105,'xkb':113,'name':'LEFT'}]*3)
 def test_plan_no_environment_handles_or_wayland_connection(self):
  p=subprocess.run([str(B/'physical-keyboard'),'--plan','-d','20','--','-continued0'],env={'WAYLAND_DISPLAY':'/unowned/main','WAYLAND_SOCKET':'99','DISPLAY':':0'},capture_output=True,text=True,timeout=3);self.assertEqual(p.returncode,0);self.assertTrue(json.loads(p.stdout)['cpuOnly'])
 def test_all_unsupported_text_refused_before_connection(self):
  for text in ('','A',' ','\n','é','\t','_','a"b','a/b','a'*257):
   p=self.plan(['-d','20','--',text]);self.assertEqual(p.returncode,2,text);self.assertEqual(p.stdout,'')
 def test_all_wrong_argv_refused_before_connection(self):
  for args in ([],['-d','20'],['-d','20.0','--','a'],['-d','-20','--','a'],['-d','19','--','a'],['-d','20','--','a','b'],['-d','20','-k','Escape'],['-d','20','-k','Left'],['-d','20','-k','Left','-k','Left','-k','Right']):self.assertEqual(self.plan(args).returncode,2,args)
 def test_256_character_bound_complete_plan(self):self.assertEqual(len(json.loads(self.plan(['-d','20','--','a'*256]).stdout)['plan']),256)
 def fixture(self,text='-continued0',fault=None,wrong_peer=False,wrong_start=False,left=False):
  with tempfile.TemporaryDirectory()as temporary:
   root=Path(temporary);root.chmod(0o700);path=root/'wayland-1';log=root/'events';log.touch(mode=0o600);endpoint=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);endpoint.bind(str(path));endpoint.listen(1);endpoint.settimeout(.8);connections=[];received=[]
   def serve():
    try:
     connection,_=endpoint.accept();connections.append(True)
     with connection:received.append(connection.recv(32))
    except TimeoutError:pass
    finally:endpoint.close()
   thread=threading.Thread(target=serve);thread.start();child=subprocess.Popen(['/usr/bin/python3','-c','import sys;sys.stdin.read()'],stdin=subprocess.PIPE)if wrong_peer else None;pid=child.pid if child else os.getpid()
   env={'XDG_RUNTIME_DIR':str(root),'WAYLAND_DISPLAY':'wayland-1','HYPRLAND_INSTANCE_SIGNATURE':'qa_test','WINDOW_QA_COMPOSITOR_PID':str(pid),'WINDOW_QA_COMPOSITOR_START':start(pid)if not wrong_start else'1','CPU_KEYBOARD_EVENT_LOG':str(log)}
   if fault:env.update(fault)
   args=['-d','20','-k','Left','-k','Left','-k','Left']if left else['-d','20','--',text]
   try:p=subprocess.run([str(B/'physical-protocol-cpu'),*args],env=env,capture_output=True,text=True,timeout=3)
   finally:
    thread.join(2);self.assertFalse(thread.is_alive())
    if child:child.stdin.close();child.wait(timeout=2);self.assertEqual(child.returncode,0)
   rows=[json.loads(x)for x in log.read_text().splitlines()];self.assertTrue(all(x==b''for x in received),'CPUshim must send no actual Wayland protocol bytes');return p,rows,connections
 def test_actual_runtime_source_against_cpu_protocol_minus_correct_pairs(self):
  p,rows,connections=self.fixture();self.assertEqual(p.returncode,0,p.stderr);r=json.loads(p.stdout);self.assertEqual(r['pairCount'],11);self.assertTrue(r['normalDestroyed']);keys=[(x['a'],x['b'])for x in rows if x['kind']=='key'];expected=[(WIRE[ord(c)],state)for c in '-continued0'for state in (1,0)];self.assertEqual(keys,expected);self.assertEqual(sum(x['kind']=='destroy_keyboard'for x in rows),1);self.assertEqual(sum(x['kind']=='create_keyboard'for x in rows),1);self.assertTrue(connections)
  self.assertLess(next(i for i,x in enumerate(rows)if x['kind']=='keymap'),next(i for i,x in enumerate(rows)if x['kind']=='key'))
 def test_actual_runtime_source_three_left_cpu_protocol(self):
  p,rows,_=self.fixture(left=True);self.assertEqual(p.returncode,0,p.stderr);self.assertEqual([(x['a'],x['b'])for x in rows if x['kind']=='key'],[(105,1),(105,0)]*3)
 def test_actual_kernel_peer_mismatch_no_virtual_creation(self):
  p,rows,connections=self.fixture(wrong_peer=True);self.assertEqual(p.returncode,3);self.assertEqual(rows,[]);self.assertTrue(connections)
 def test_actual_process_start_mismatch_no_connect(self):
  p,rows,connections=self.fixture(wrong_start=True);self.assertEqual(p.returncode,3);self.assertEqual(rows,[]);self.assertFalse(connections)
 def test_duplicate_seat_refused_before_create(self):
  p,rows,_=self.fixture(fault={'CPU_DUPLICATE_SEAT':'1'});self.assertEqual(p.returncode,3);self.assertFalse(any(x['kind']in ('create_keyboard','key')for x in rows))
 def test_missing_map_roundtrip_no_press(self):
  p,rows,_=self.fixture(fault={'CPU_FAIL_AT':'2'});self.assertEqual(p.returncode,3);self.assertTrue(any(x['kind']=='keymap'for x in rows));self.assertFalse(any(x['kind']=='key'for x in rows))
 def test_registry_removal_refuses_before_press(self):
  p,rows,_=self.fixture(fault={'CPU_REMOVAL_AT':'2'});self.assertEqual(p.returncode,3);self.assertFalse(any(x['kind']=='key'for x in rows))
 def test_partial_press_error_no_retry_or_extra_character(self):
  p,rows,_=self.fixture(fault={'CPU_FAIL_AT':'3'});self.assertEqual(p.returncode,3);self.assertEqual([(x['a'],x['b'])for x in rows if x['kind']=='key'],[(12,1)]);self.assertFalse(any(x['kind']=='destroy_keyboard'for x in rows));self.assertIn('heldAtFailure=true',p.stderr)
 def test_complete_pair_then_error_no_plan_restart(self):
  p,rows,_=self.fixture(fault={'CPU_FAIL_AT':'4'});self.assertEqual(p.returncode,3);self.assertEqual([(x['a'],x['b'])for x in rows if x['kind']=='key'],[(12,1),(12,0)]);self.assertEqual(sum(x['kind']=='create_keyboard'for x in rows),1)
 def test_formal_numeric_sequence_before_driver(self):
  for n in ('physical-keyboard-formal-before-implementation.json','physical-keyboard-positive-formal-before-implementation.json'):
   r=json.loads((B/n).read_text());self.assertEqual(r['result'],'pass');self.assertFalse(r['nativeExecuted'])
 def test_cpu_protocol_hooks_absent_from_real_driver_source(self):
  s=(B/'physical_keyboard.c').read_text();self.assertNotIn('CPU_',s);self.assertIn('SO_PEERCRED',s);self.assertIn('sync_private()',s);self.assertEqual(s.count('usleep(2000)'),2);self.assertIn('usleep(20000)',s)
 def test_materialized_map_runtime_no_source_includes(self):
  s=(B/'physical_plan.c').read_text();self.assertIn('xkb_keymap_new_from_string',s);self.assertNotIn('xkb_keymap_new_from_names',s);self.assertNotIn('XKB_CONFIG_ROOT',s)
if __name__=='__main__':unittest.main()
