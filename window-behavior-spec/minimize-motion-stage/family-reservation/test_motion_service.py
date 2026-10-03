#!/usr/bin/env python3
"""Actual daemon/socket startup in a private fake desktop; subprocess cleanup."""
import hashlib,json,os
from pathlib import Path
import shutil,signal,socket,subprocess,tempfile,time,unittest
HERE=Path(__file__).resolve().parent
HELPERS=Path(os.getenv('MOTION_HELPER_DIR',str(HERE)))
FAKE=r'''#!/usr/bin/env python3
import fcntl,json,os,sys,time
from pathlib import Path
root=Path(os.environ['MOTION_SOCKET_FAKE']);path=root/'state.json'
with (root/'state.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);s=json.loads(path.read_text());name=Path(sys.argv[0]).name
 if name=='hyprctl':
  cmd=sys.argv[1]
  if cmd=='clients':print(json.dumps(s['windows']))
  elif cmd=='activewindow':print(json.dumps({'address':s['active']}))
  elif cmd=='monitors':print(json.dumps([{'id':0,'name':'DP-1','x':0,'y':0,'width':1920,'height':1080,'scale':1,'focused':True,'activeWorkspace':{'name':'1'}}]))
  elif cmd=='repl':
   print(json.dumps([dict(w,parent='' if i==0 else s['windows'][0]['address'],parentStableId='' if i==0 else s['windows'][0]['stableId'],modal=i>0) for i,w in enumerate(s['windows'])]))
  elif cmd=='workspaces':print(json.dumps([{'name':'1','monitorID':0,'monitor':'DP-1'}]))
  elif cmd=='dispatch':print('ok')
  else:sys.exit(2)
 elif name=='omarchy-shell':print('null' if sys.argv[2]=='motionTarget' else 'true')
 elif name=='hypr-window-family':
  windows=json.loads(sys.stdin.read());print(json.dumps({'windows':windows,'focus':windows[-1]}))
 elif name=='fake-core':
  if s.get('fail'):sys.exit(77)
  op,address,identity,pid=sys.argv[1:5]
  w=next((w for w in s['windows'] if w['address']==address and w['stableId']==identity and str(w['pid'])==pid),None)
  if not w:sys.exit(3)
  s['calls'].append([op,address]);w['workspace']['name']='special:win-minimized' if op=='minimize' else '1'
  s['active']=address
  if op=='minimize':
   state=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-windowctl';state.mkdir(parents=True,exist_ok=True)
   (state/address).write_text('1 0 '+identity+'\n')
   (state/(address+'.monitor.json')).write_text(json.dumps({'pid':w['pid'],'stableId':identity,'homeWorkspace':'1','monitorName':'DP-1'}))
  path.write_text(json.dumps(s))
'''

class ServiceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.home=self.root/'home';(self.home/'.local/bin').mkdir(parents=True)
  bin=self.root/'bin';bin.mkdir();runtime=self.root/'runtime';runtime.mkdir()
  for name in ['hyprctl','omarchy-shell','fake-core']:
   p=bin/name;p.write_text(FAKE);p.chmod(0o755)
  p=self.home/'.local/bin/hypr-window-family';p.write_text(FAKE);p.chmod(0o755)
  self.env=dict(os.environ,HOME=str(self.home),PATH=str(bin)+':'+os.environ['PATH'],XDG_RUNTIME_DIR=str(runtime),HYPRLAND_INSTANCE_SIGNATURE='motion-socket-qa',HYPR_WINDOWCTL_CORE=str(bin/'fake-core'),MOTION_SOCKET_FAKE=str(self.root))
  self.service_root=runtime/'hypr-window-motion'/hashlib.sha256(b'motion-socket-qa').hexdigest()[:20]
  self.state={'windows':[{'address':'0x10','stableId':'stable10','pid':100,'mapped':True,'monitor':0,'pinned':False,'workspace':{'name':'1'},'at':[80,90],'size':[640,380]}],'active':'0x10','calls':[]}
  self.save()
 def save(self): (self.root/'state.json').write_text(json.dumps(self.state))
 def read(self):return json.loads((self.root/'state.json').read_text())
 def run_client(self,*args,extra=None):
  env=dict(self.env,**(extra or {}));return subprocess.run([str(HELPERS/'hypr-window-motion'),*args],env=env,capture_output=True,text=True,timeout=15)
 def tearDown(self):
  try:
   if (self.service_root/'control.sock').exists():self.run_client('stop')
   deadline=time.monotonic()+3
   while (self.service_root/'daemon.pid').exists() and time.monotonic()<deadline:time.sleep(.03)
   if (self.service_root/'daemon.pid').exists():os.kill(int((self.service_root/'daemon.pid').read_text()),signal.SIGTERM)
  finally:self.temp.cleanup()
 def test_real_socket_single_flag_does_not_poison_later_family(self):
  child=dict(self.state['windows'][0],address='0x20',stableId='stable20',pid=200)
  self.state['windows'].append(child);self.save()
  first=self.run_client('request','minimize','0x10','stable10','100',extra={'HYPR_WINDOWCTL_FAMILY_SINGLE':'1','HYPR_WINDOWCTL_ASYNC':'1'})
  self.assertEqual(first.returncode,0,first.stderr)
  self.assertEqual(self.read()['calls'],[['minimize','0x10']])
  second=self.run_client('request','restore','0x10','stable10','100')
  self.assertEqual(second.returncode,0,second.stderr)
  calls=self.read()['calls'];self.assertIn(['restore','0x20'],calls);self.assertEqual(calls[-1],['restore','0x20'])
  pid=int((self.service_root/'daemon.pid').read_text())
  environment=Path('/proc')/str(pid)/'environ'
  raw=environment.read_bytes();self.assertNotIn(b'HYPR_WINDOWCTL_FAMILY_SINGLE=',raw);self.assertNotIn(b'HYPR_WINDOWCTL_ASYNC=',raw)
 def test_stale_socket_waits_for_recovery_before_new_intent(self):
  self.state['windows'][0]['workspace']['name']='special:win-minimized';self.save()
  self.service_root.mkdir(parents=True)
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as stale:stale.bind(str(self.service_root/'control.sock'))
  record={'token':'old','identity':['0x10','stable10',100],'operation':'restore','previewReady':True,'phase':'running','deadline':0}
  (self.service_root/'pending.json').write_text(json.dumps([record]))
  result=self.run_client('request','minimize','0x10','stable10','100')
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(self.read()['calls'],[['restore','0x10'],['minimize','0x10']])
 def test_permanent_core_failure_returns_error_and_clears_journal(self):
  self.state['fail']=True;self.save()
  result=self.run_client('request','minimize','0x10','stable10','100')
  self.assertEqual(result.returncode,3);self.assertIn('native window operation failed',result.stderr)
  self.assertEqual(json.loads((self.service_root/'pending.json').read_text()),[])
  self.assertEqual(self.read()['calls'],[])

if __name__=='__main__':unittest.main()
