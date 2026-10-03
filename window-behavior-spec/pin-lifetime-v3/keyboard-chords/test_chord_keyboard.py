"""Actual C/XKB chord plan and isolated CPU protocol shim. No native GUI input."""
import json,os,subprocess,tempfile,threading,socket,unittest
from pathlib import Path
B=Path(__file__).resolve().parent
def start(pid):return(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]
class Chords(unittest.TestCase):
 def plan(self,name):
  p=subprocess.run([str(B/'physical-keyboard'),'--plan','--chord',name],capture_output=True,text=True,timeout=3,env={});self.assertEqual(p.returncode,0,p.stderr);return json.loads(p.stdout)['plan']
 def test_exact_whole_physical_super_p_and_balanced_modifier_masks(self):
  p=self.plan('super-p');self.assertEqual([(x['wire'],x['state'],x['modsDepressed'])for x in p],[(125,1,64),(25,1,64),(25,0,64),(125,0,0)])
 def test_exact_whole_physical_super_ctrl_t(self):
  p=self.plan('super-ctrl-t');self.assertEqual([(x['wire'],x['state'],x['modsDepressed'])for x in p],[(125,1,64),(29,1,68),(20,1,68),(20,0,68),(29,0,64),(125,0,0)])
 def test_actual_canonical_menu_return_escape(self):
  for name,wire,symbol in [('menu',127,65383),('return',28,65293),('escape',1,65307)]:
   with self.subTest(name=name):
    p=self.plan(name);self.assertEqual([(x['wire'],x['state'],x['symbol'])for x in p],[(wire,1,symbol),(wire,0,symbol)]);self.assertTrue(all(x['xkb']==wire+8 and x['modsDepressed']==0 for x in p))
 def test_no_unknown_or_extra_command_before_connection(self):
  for args in [[],['--chord','super'],['--chord','SUPER+P'],['--chord','super-p','retry'],['--chord','p'],['-d','20','--','p']]:
   p=subprocess.run([str(B/'physical-keyboard'),*args],capture_output=True,text=True,timeout=3,env={});self.assertEqual(p.returncode,2,args);self.assertEqual(p.stdout,'')
 def fixture(self,chord='super-p',fault=None,wrong_peer=False,wrong_start=False):
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
   args=['--chord',chord]
   try:p=subprocess.run([str(B/'physical-protocol-cpu'),*args],env=env,capture_output=True,text=True,timeout=3)
   finally:
    thread.join(2);self.assertFalse(thread.is_alive())
    if child:child.stdin.close();child.wait(timeout=2);self.assertEqual(child.returncode,0)
   rows=[json.loads(x)for x in log.read_text().splitlines()];self.assertTrue(all(x==b''for x in received),'CPUshim must send no actual Wayland protocol bytes');return p,rows,connections

 def test_actual_runtime_cpu_protocol_held_chord_and_explicit_modifiers(self):
  for name in ['super-p','super-ctrl-t','menu','return','escape']:
   with self.subTest(name=name):
    p,rows,_=self.fixture(chord=name);self.assertEqual(p.returncode,0,p.stderr);plan=self.plan(name)
    expected=[]
    for key in plan:
     expected.append(('key',key['wire'],key['state']))
     if key['modifierTransition']:expected.append(('modifiers',key['modsDepressed'],0))
    self.assertEqual([(x['kind'],x['a'],x['b'])for x in rows if x['kind']in ('key','modifiers')],expected);self.assertEqual(sum(x['kind']=='keymap'for x in rows),1);self.assertEqual(sum(x['kind']=='create_keyboard'for x in rows),1);self.assertEqual(sum(x['kind']=='destroy_keyboard'for x in rows),1);self.assertEqual(json.loads(p.stdout)['pairCount'],len(plan)//2)
 def test_actual_peer_and_start_mismatch_before_keys(self):
  p,rows,_=self.fixture(wrong_peer=True);self.assertEqual(p.returncode,3);self.assertEqual(rows,[])
  p,rows,connected=self.fixture(wrong_start=True);self.assertEqual(p.returncode,3);self.assertEqual(rows,[]);self.assertFalse(connected)
 def test_error_held_meta_sends_no_modifier_release_or_destroy(self):
  p,rows,_=self.fixture(fault={'CPU_FAIL_AT':'3'});self.assertEqual(p.returncode,3);self.assertEqual([(x['kind'],x['a'],x['b'])for x in rows if x['kind']in ('key','modifiers')],[('key',125,1)]);self.assertFalse(any(x['kind']=='destroy_keyboard'for x in rows));self.assertIn('heldCountAtFailure=1',p.stderr)
 def test_error_after_modifier_sends_no_target(self):
  p,rows,_=self.fixture(fault={'CPU_FAIL_AT':'4'});self.assertEqual(p.returncode,3);self.assertEqual([(x['kind'],x['a'],x['b'])for x in rows if x['kind']in ('key','modifiers')],[('key',125,1),('modifiers',64,0)]);self.assertFalse(any(x['kind']=='destroy_keyboard'for x in rows))
 def test_registry_loss_or_duplicate_refuses_input(self):
  for fault in [{'CPU_REMOVAL_AT':'2'},{'CPU_DUPLICATE_SEAT':'1'}]:
   p,rows,_=self.fixture(fault=fault);self.assertEqual(p.returncode,3);self.assertFalse(any(x['kind']=='key'for x in rows))
if __name__=='__main__':unittest.main(verbosity=2)
