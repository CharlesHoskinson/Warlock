"""Actual isolated Unix transport/product CLI tests; no compositor/toolkit proof."""
from pathlib import Path
import hashlib,json,os,shutil,socket,stat,subprocess,sys,tempfile,threading,time,unittest
import native_frontend as n
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-review-v12')
TARGET={'address':'0xabc','stableId':'1','pid':123,'mapped':True}
class Endpoint:
 def __init__(self,path,response,delay=0):
  self.path=path;self.response=response;self.delay=delay;self.requests=[];self.socket=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.socket.bind(str(path));path.chmod(0o600);self.socket.listen();self.socket.settimeout(5);self.thread=threading.Thread(target=self.run);self.thread.start()
 def run(self):
  try:
   c,_=self.socket.accept()
   with c:
    c.settimeout(2);data=c.recv(8192);self.requests.append(data)
    if self.response is not None:c.sendall(self.response)
    if self.delay:time.sleep(self.delay)
  except (OSError,TimeoutError):pass
  finally:self.socket.close()
 def close(self):self.thread.join(timeout=5);self.socket.close()
class Frontend(unittest.TestCase):
 def test_explicit_cli(self):self.assertEqual(n.parse_cli(['restore','0xabc','1','123'])['pid'],123)
 def test_no_inferred_target(self):
  with self.assertRaises(n.Refused):n.parse_cli(['minimize'])
 def test_noncanonical_identity(self):
  for args in [['restore','ABC','1','123'],['restore','0xabc','1','0'],['restore','0xabc','G','123']]:
   with self.assertRaises(n.Refused):n.parse_cli(args)
 def setup_cli(self,answer=b'{"ok":true,"accepted":true,"completed":false,"receipt":1}\n',delay=0,stale=False):
  temp=tempfile.TemporaryDirectory();base=Path(temp.name);home=base/'home';home.mkdir(mode=0o700);service=base/'service';service.mkdir(mode=0o700)
  entry=home/'hypr-windowctl';shutil.copyfile(Path(n.__file__),entry);entry.chmod(0o700)
  compositor=Endpoint(base/'compositor.sock',json.dumps([{**TARGET,'stableId':'2'}] if stale else [TARGET]).encode())
  api=Endpoint(service/'api.sock',answer,delay);owner=n.process(os.getpid());s=(service/'api.sock').stat()
  (service/'owner.json').write_text(json.dumps({'session':'owned','pid':owner['pid'],'start':int(owner['start']),'socket':[s.st_dev,s.st_ino]}));(service/'owner.json').chmod(0o600)
  env={k:v for k,v in os.environ.items() if k not in ('AT_SPI_BUS_ADDRESS','WAYLAND_SOCKET','SESSION_MANAGER','DISPLAY','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS','LD_PRELOAD','LD_AUDIT','PYTHONPATH','PYTHONHOME')}
  env.update(HOME=str(home),XDG_RUNTIME_DIR=str(base),HYPRLAND_INSTANCE_SIGNATURE='owned',WAYLAND_DISPLAY='owned-wayland',PYTHONDONTWRITEBYTECODE='1')
  selectors={k:env[k] for k in ('HOME','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')}
  argv=[v.decode() for v in Path('/proc/self/cmdline').read_bytes().rstrip(b'\0').split(b'\0')];exe=Path('/proc/self/exe').resolve();cs=(base/'compositor.sock').stat()
  log=home/'log.jsonl';log.touch(mode=0o600)
  inputs={str(p):{'sha256':n.digest(p),'mode':stat.S_IMODE(p.stat().st_mode)} for p in SERVICE.glob('*.py')}
  cfg=dict(version=1,runtime=str(base),selectors=selectors,entry=str(entry),entrySHA256=n.digest(entry),requestRoots=[dict(role='isolated-test-root',identity=owner,argv=argv,executable=str(exe),executableSHA256=n.digest(exe))],delegateInputs=inputs,delegateDirectory=str(SERVICE),serviceRoot=str(service),session='owned',service=owner,serviceSocketIdentity=[s.st_dev,s.st_ino],compositor=owner,compositorSocket=str(base/'compositor.sock'),compositorSocketIdentity=[cs.st_dev,cs.st_ino],log=str(log))
  config=home/'config.json';config.write_text(json.dumps(cfg));config.chmod(0o600);env['WINDOW_MOTION_NATIVE_CONFIG']=str(config)
  return temp,entry,env,compositor,api,log
 def run_cli(self,answer=b'{"ok":true,"accepted":true,"completed":false,"receipt":1}\n',delay=0,stale=False):
  temp,entry,env,compositor,api,log=self.setup_cli(answer,delay,stale)
  try:
   result=subprocess.run(['/usr/bin/python3',str(entry),'restore','0xabc','1','123'],env=env,capture_output=True,text=True,timeout=8)
   events=[json.loads(x) for x in log.read_text().splitlines()];return result,list(api.requests),events
  finally:compositor.close();api.close();temp.cleanup()
 def test_actual_cli_delegates_v12_once_with_eof(self):
  r,requests,events=self.run_cli();self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(len(requests),1);self.assertEqual(json.loads(requests[0]),n.parse_cli(['restore','0xabc','1','123']));self.assertTrue(events[0]['transport']['completeServerEOF']);self.assertFalse(events[0]['nativeCompletionClaimed'])
 def test_stale_lifetime_refused_before_api_send(self):
  r,requests,events=self.run_cli(stale=True);self.assertEqual(r.returncode,125);self.assertFalse(requests);self.assertEqual(events[0]['result'],'refused')
 def test_missing_eof_uncertain_no_second_send(self):
  r,requests,events=self.run_cli(delay=2.3);self.assertEqual(r.returncode,75,r.stderr);self.assertEqual(len(requests),1);self.assertEqual(events[0]['result'],'unknown-acceptance')
 def test_extra_frame_uncertain_no_second_send(self):
  r,requests,events=self.run_cli(b'{"ok":true,"accepted":true}\n{}\n');self.assertEqual(r.returncode,75);self.assertEqual(len(requests),1)
 def test_missing_frame_uncertain_no_second_send(self):
  r,requests,events=self.run_cli(b'{"ok":true,"accepted":true}');self.assertEqual(r.returncode,75);self.assertEqual(len(requests),1)
 def test_explicit_server_refusal_retained(self):
  r,requests,events=self.run_cli(b'{"ok":false,"accepted":false,"error":"full"}\n');self.assertEqual(r.returncode,125);self.assertEqual(len(requests),1);self.assertEqual(events[0]['result'],'refused')
 def test_ambiguous_acceptance_retained(self):
  r,requests,events=self.run_cli(b'{"ok":true,"accepted":true,"completed":false,"receipt":false}\n');self.assertEqual(r.returncode,75);self.assertEqual(len(requests),1)
if __name__=='__main__':unittest.main(verbosity=2)
