"""Actual CPU/kernel boundary tests; synthetic replies prove no native pin effect."""
import copy,hashlib,importlib.util,json,mmap,os,random,socket,subprocess,tempfile,threading,time,unittest
from pathlib import Path
from unittest.mock import patch
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pin_boundary_candidate',B/'pin_helper.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def captured():
 return dict(address='0x1234',stableId='abcd',pid=123,session='testsession',compositorPid=os.getpid(),compositorStart=h.process(os.getpid())['start'],incarnation='a'*32,epoch='1',generation='1')
def receipt():
 t=captured();projection={k:v for k,v in t.items()if k not in ('compositorPid','compositorStart')}
 before=dict(projection,live=True,normal=True,fullscreen=False,floating=True,pinned=False)
 return dict(ok=True,phase='complete',reason='',actionsInvoked=True,possiblePartialOutcome=False,captured=t,before=before,after=dict(before,pinned=True),desiredPinned=True)

class ParserTests(unittest.TestCase):
 def test_original_malformed_completion_counterexample(self):
  oldspec=importlib.util.spec_from_file_location('old_pin',B/'retained-initial.py');old=importlib.util.module_from_spec(oldspec);oldspec.loader.exec_module(old)
  bad=receipt();bad['captured']={}
  with self.assertRaises(old.Refused)as olderror:old.result(bad,captured())
  self.assertNotIsInstance(olderror.exception,old.Uncertain)
  with self.assertRaises(h.Uncertain):h.result(bad,captured())
 def test_valid_exact_toggle(self):self.assertEqual(h.result(receipt(),captured())['after']['pinned'],True)
 def test_toggle_from_pinned_to_unpinned(self):
  r=receipt();r['before']['pinned']=True;r['desiredPinned']=False;r['after']['pinned']=False
  self.assertEqual(h.result(r,captured())['after']['pinned'],False)
 def test_missing_or_malformed_completed_token_is_uncertain(self):
  for value in (None,{},dict(captured(),pid=True),dict(captured(),epoch='0'),dict(captured(),generation=str(2**64))):
   with self.subTest(value=value),self.assertRaises(h.Uncertain):h.result(dict(receipt(),captured=value),captured())
 def test_foreign_token_is_uncertain(self):
  with self.assertRaises(h.Uncertain):h.result(dict(receipt(),captured=dict(captured(),generation='2')),captured())
 def test_no_action_cannot_claim_complete(self):
  with self.assertRaises(h.Uncertain):h.result(dict(receipt(),actionsInvoked=False),captured())
 def test_before_pin_must_be_boolean_and_toggled(self):
  for value in (None,0,1,True):
   r=receipt();r['before']['pinned']=value
   with self.subTest(value=value),self.assertRaises(h.Uncertain):h.result(r,captured())
 def test_owner_projection_and_state_guards(self):
  for field,value in [('generation','2'),('live',False),('normal',False),('fullscreen',True),('floating',False),('pinned',False)]:
   r=receipt();r['after'][field]=value
   with self.subTest(field=field),self.assertRaises(h.Uncertain):h.result(r,captured())
 def test_explicit_native_validation_refusal(self):
  r=dict(ok=False,phase='validate',reason='Stale or foreign complete pin identity',actionsInvoked=False,possiblePartialOutcome=False)
  self.assertIs(h.result(r,captured()),r)
 def test_explicit_native_partial_failure_stays_visible(self):
  r=dict(ok=False,phase='raise',reason='backend refusal',actionsInvoked=True,possiblePartialOutcome=True)
  self.assertTrue(h.result(r,captured())['possiblePartialOutcome'])
 def test_inconsistent_partial_flag_is_uncertain(self):
  with self.assertRaises(h.Uncertain):h.result(dict(receipt(),possiblePartialOutcome=True),captured())
 def test_inconsistent_native_refusal_phase_is_uncertain(self):
  for phase,action in (('complete',False),('validate',True),('pin',False),('raise',False)):
   r=dict(ok=False,phase=phase,reason='synthetic',actionsInvoked=action,possiblePartialOutcome=action)
   with self.subTest(phase=phase),self.assertRaises(h.Uncertain):h.result(r,captured())
 def test_foreign_native_refusal_token_is_uncertain(self):
  r=dict(ok=False,phase='validate',reason='synthetic',actionsInvoked=False,possiblePartialOutcome=False,captured=dict(captured(),generation='2'))
  with self.assertRaises(h.Uncertain):h.result(r,captured())
 def test_actual_projection_counterexamples_now_uncertain(self):
  for field,bad in (('floating',None),('pid',True)):
   r=receipt();t=captured();t['pid']=1;r['captured']=t;r['before']['pid']=1;r['after']['pid']=1;r['before'][field]=bad
   with self.subTest(field=field),self.assertRaises(h.Uncertain):h.result(r,t)
 def test_seeded_1000_malformed_projection_mutations(self):
  rng=random.Random(20261002)
  for index in range(1000):
   r=receipt();t=captured();t['pid']=1;r['captured']=t;r['before']['pid']=1;r['after']['pid']=1
   name=rng.choice(['before','after']);field=rng.choice(['address','stableId','pid','session','incarnation','epoch','generation','floating','pinned'])
   bad=rng.choice([None,0,1,True,False,1.0,'malformed',[],{}])
   if field in ('floating','pinned')and type(bad)is bool:bad='malformed'
   if field=='pid'and type(bad)is int and bad==1:bad=True
   r[name][field]=bad
   with self.subTest(index=index,name=name,field=field),self.assertRaises(h.Uncertain):h.result(r,t)
 def test_duplicate_and_nonfinite_json_refused(self):
  for raw in ('{"ok":true,"ok":false}','{"x":NaN}','{"x":Infinity}','{"x":-Infinity}','{"x":{"p":1,"p":2}}'):
   with self.subTest(raw=raw),self.assertRaises(ValueError):h.strict_json(raw)
 def test_command_has_only_full_token_and_no_fallback(self):
  request=h.command(captured()).decode();self.assertTrue(request.startswith('repl print(hl.plugin.hyprbars.pin_request({'))
  self.assertNotIn('activewindow',request)
  for key in h.FIELDS:self.assertIn(key+'=',request)
  with self.assertRaises(h.Refused):h.command({'address':'0x1234','pid':123})

class EvidenceTests(unittest.TestCase):
 def test_full_short_writes_and_fsync(self):
  with tempfile.TemporaryFile()as f:
   write=os.write;fsync=os.fsync;calls=[]
   def short(fd,data):return write(fd,data[:3])
   def synced(fd):calls.append(fd);return fsync(fd)
   with patch.object(h.os,'write',short),patch.object(h.os,'fsync',synced):h.publish(f.fileno(),{'evidence':'long original record'})
   f.seek(0);self.assertEqual(json.loads(f.read()),{'evidence':'long original record'});self.assertEqual(calls,[f.fileno()])
 def test_zero_write_refused(self):
  with tempfile.TemporaryFile()as f,patch.object(h.os,'write',return_value=0),self.assertRaises(OSError):h.publish(f.fileno(),{'x':1})
 def test_fsync_failure_propagates(self):
  with tempfile.TemporaryFile()as f,patch.object(h.os,'fsync',side_effect=OSError('actual publication failed')),self.assertRaises(OSError):h.publish(f.fileno(),{'x':1})

class TransportTests(unittest.TestCase):
 def fixture(self,reply,drip=False):
  temp=tempfile.TemporaryDirectory();runtime=Path(temp.name);runtime.chmod(0o700)
  (runtime/'hypr').mkdir(mode=0o700);folder=runtime/'hypr'/'testsession';folder.mkdir(mode=0o700)
  path=folder/'.socket.sock';server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(str(path));server.listen();server.settimeout(3)
  config={'runtime':str(runtime),'selectors':{'HYPRLAND_INSTANCE_SIGNATURE':'testsession'},'socket':{'path':str(path),'identity':[path.stat().st_dev,path.stat().st_ino]},'compositor':{'identity':{'pid':os.getpid()}}}
  received=[]
  def serve():
   try:
    with server.accept()[0]as conn:
     received.append(conn.recv(8192))
     if drip:
      for part in reply:
       time.sleep(.35);conn.sendall(bytes([part]))
     else:conn.sendall(reply)
   except (TimeoutError,BrokenPipeError,ConnectionResetError):pass
   finally:server.close()
  thread=threading.Thread(target=serve);thread.start()
  self.addCleanup(temp.cleanup);self.addCleanup(thread.join,4)
  return config,received
 def test_actual_peer_full_eof_raw_before_parse(self):
  config,received=self.fixture(b'{"receipt":true}');evidence={};publications=[]
  value=h.exchange(config,b'fixed request',evidence,lambda:publications.append(copy.deepcopy(evidence)),lambda:None)
  self.assertEqual(value,{'receipt':True});self.assertEqual(received,[b'fixed request'])
  self.assertEqual(evidence['transport']['peer']['pid'],os.getpid());self.assertTrue(evidence['transport']['completeServerEOF'])
  self.assertTrue(publications[-1]['transport']['rawReplyBase64']);self.assertTrue(publications[-1]['transport']['completeServerEOF'])
 def test_wrong_actual_peer_before_send(self):
  config,received=self.fixture(b'{}');config['compositor']['identity']['pid']+=1;evidence={}
  with self.assertRaises(h.Refused)as error:h.exchange(config,b'fixed request',evidence,lambda:None,lambda:None)
  self.assertNotIsInstance(error.exception,h.Uncertain);self.assertFalse(evidence['transport']['sendStarted'])
 def test_actual_drip_cannot_reset_deadline(self):
  config,received=self.fixture(b'{"valid":true}',drip=True);evidence={};start=time.monotonic()
  with self.assertRaises(h.Uncertain):h.exchange(config,b'fixed request',evidence,lambda:None,lambda:None)
  elapsed=time.monotonic()-start;self.assertGreater(elapsed,1.8);self.assertLess(elapsed,2.5);self.assertFalse(evidence['transport']['completeServerEOF'])
 def test_malformed_after_send_uncertain(self):
  for reply in (b'{',b'{"x":1,"x":2}',b'{"x":NaN}',b'\xff'):
   with self.subTest(reply=reply):
    config,received=self.fixture(reply);evidence={}
    with self.assertRaises(h.Uncertain):h.exchange(config,b'fixed request',evidence,lambda:None,lambda:None)
    self.assertTrue(evidence['transport']['sendStarted']);self.assertTrue(evidence['transport']['rawReplyBase64'])
 def test_post_send_publication_failure_cannot_reclassify(self):
  config,received=self.fixture(b'{}');evidence={}
  def persist():
   if evidence['transport']['sendStarted']:raise OSError('disk refuses publication')
  with self.assertRaises(h.Uncertain):h.exchange(config,b'fixed request',evidence,persist,lambda:None)
  self.assertTrue(evidence['transport']['sendStarted']);self.assertIn('errorPublicationFailure',evidence['transport'])
 def test_pre_send_guard_uses_original_deadline(self):
  config,received=self.fixture(b'{}');evidence={}
  with self.assertRaises(TimeoutError):h.exchange(config,b'fixed request',evidence,lambda:None,lambda:time.sleep(2.05))
  self.assertFalse(evidence['transport']['sendStarted'])
 def test_socket_replacement_after_send_uncertain(self):
  config,received=self.fixture(b'{}');evidence={};replacement=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.addCleanup(replacement.close);replaced=False
  def persist():
   nonlocal replaced
   if evidence['transport']['completeServerEOF']and not replaced:
    path=Path(config['socket']['path']);path.unlink();replacement.bind(str(path));replaced=True
  with self.assertRaises(h.Uncertain):h.exchange(config,b'fixed request',evidence,persist,lambda:None)
  self.assertTrue(evidence['transport']['completeServerEOF'])

SERVER='''import json,mmap,os,socket,sys,time
from pathlib import Path
socket_path,module,ready,reply,stop=sys.argv[1:]
fd=os.open(module,os.O_RDONLY)
mapping=mmap.mmap(fd,4096,flags=mmap.MAP_PRIVATE,prot=mmap.PROT_READ|mmap.PROT_EXEC)
server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(socket_path);server.listen(1);server.settimeout(.05)
Path(ready).write_text(str(os.getpid()))
connection=None;deadline=time.monotonic()+5
while connection is None and not Path(stop).exists()and time.monotonic()<deadline:
 try:connection=server.accept()[0]
 except TimeoutError:pass
if connection is not None:
 with connection as conn:
  request=conn.recv(8192);Path(reply+'.request').write_bytes(request)
  conn.sendall(Path(reply).read_bytes())
server.close()
deadline=time.monotonic()+5
while not Path(stop).exists()and time.monotonic()<deadline:time.sleep(.01)
mapping.close();os.close(fd)
'''

class ExecutableTests(unittest.TestCase):
 def source(self,pid,role=None):
  p=Path('/proc')/str(pid)
  row={'identity':h.process(pid),'argv':[x.decode()for x in(p/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')],'executable':str((p/'exe').resolve()),'executableSHA256':h.digest(p/'exe'),'cgroup':(p/'cgroup').read_text(),'environment':{'PATH':os.environ.get('PATH')}}
  if role:row['role']=role
  return row
 def fixture(self,mode='valid'):
  temp=tempfile.TemporaryDirectory();runtime=Path(temp.name);runtime.chmod(0o700);home=runtime/'home';home.mkdir(mode=0o700)
  for path in (runtime/'hypr',runtime/'hypr'/'testsession',home/'evidence'):path.mkdir(mode=0o700)
  entry=home/'pin_helper.py';entry.write_bytes((B/'pin_helper.py').read_bytes());entry.chmod(0o700)
  module=home/'inert-mapped-cpu-fixture.bin';module.write_bytes(bytes(4096));module.chmod(0o600)
  script=home/'server.py';script.write_text(SERVER);script.chmod(0o600)
  socket_path=runtime/'hypr'/'testsession'/'.socket.sock';ready=home/'ready';reply=home/'reply.json';stop=home/'stop'
  server=subprocess.Popen(['/usr/bin/python3','-I','-S',str(script),str(socket_path),str(module),str(ready),str(reply),str(stop)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  def cleanup():
   stop.touch();stdout,stderr=server.communicate(timeout=6);self.assertEqual(server.returncode,0,stderr.decode());temp.cleanup()
  self.addCleanup(cleanup)
  deadline=time.monotonic()+3
  while not ready.exists()and server.poll()is None and time.monotonic()<deadline:time.sleep(.01)
  self.assertTrue(ready.exists(),'Actual CPU server readiness missing')
  t=captured();t['compositorPid']=server.pid;t['compositorStart']=h.process(server.pid)['start']
  r=receipt();r['captured']=t
  if mode=='malformed':r['captured']={}
  elif mode=='native-refused':r=dict(ok=False,phase='validate',reason='Synthetic stale owner refusal',actionsInvoked=False,possiblePartialOutcome=False)
  reply.write_text(json.dumps(r));reply.chmod(0o600)
  config_path=home/'pin-config.json';selectors={'HOME':str(home),'XDG_RUNTIME_DIR':str(runtime),'HYPRLAND_INSTANCE_SIGNATURE':'testsession','WAYLAND_DISPLAY':'cpu-no-wayland','DBUS_SESSION_BUS_ADDRESS':'unix:path='+str(runtime/'bus'),'WINDOW_PIN_NATIVE_CONFIG':str(config_path)}
  config={'version':1,'runtime':str(runtime),'selectors':selectors,'entry':{'path':str(entry),'sha256':h.digest(entry)},'interpreter':{'path':str(Path('/proc/self/exe').resolve()),'sha256':h.digest('/proc/self/exe')},'requestRoots':[self.source(os.getpid(),'harness')],'compositor':self.source(server.pid),'socket':{'path':str(socket_path),'identity':[socket_path.stat().st_dev,socket_path.stat().st_ino]},'module':{'path':str(module),'sha256':h.digest(module),'mode':0o600},'evidenceDirectory':str(home/'evidence')}
  config_path.write_text(json.dumps(config));config_path.chmod(0o600)
  return entry,dict(selectors,PATH='/usr/bin'),t,config,config_path,reply
 def invoke(self,mode='valid',mutate=None):
  entry,env,t,config,path,reply=self.fixture(mode)
  if mutate:mutate(config);path.write_text(json.dumps(config));path.chmod(0o600)
  result=subprocess.run([str(entry),'toggle',json.dumps(t)],env=env,capture_output=True,text=True,timeout=4)
  stream=result.stdout if result.returncode in (0,2)else result.stderr
  return result,json.loads(stream),config,reply
 def test_actual_direct_shebang_exact_executable_argv_and_durable_evidence(self):
  result,evidence,config,reply=self.invoke();self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(evidence['nativeCompletionClaimed'])
  records=list(Path(config['evidenceDirectory']).glob('*.json'));self.assertEqual(len(records),1);self.assertEqual(json.loads(records[0].read_text()),evidence)
  self.assertEqual(reply.with_suffix(reply.suffix+'.request').read_bytes(),h.command(evidence['captured']))
  self.assertEqual(evidence['automaticRetries'],0)
 def test_actual_malformed_completed_token_is_exit3_without_completion(self):
  result,evidence,config,reply=self.invoke('malformed');self.assertEqual(result.returncode,3,result.stderr);self.assertEqual(evidence['result'],'uncertain');self.assertFalse(evidence['nativeCompletionClaimed'])
 def test_actual_native_refusal_is_exit2(self):
  result,evidence,config,reply=self.invoke('native-refused');self.assertEqual(result.returncode,2,result.stderr);self.assertEqual(evidence['result'],'native-refused')
 def test_actual_wrong_interpreter_refuses_before_any_send(self):
  result,evidence,config,reply=self.invoke(mutate=lambda config:config['interpreter'].update(sha256='0'*64));self.assertEqual(result.returncode,1,result.stderr);self.assertNotIn('transport',evidence);self.assertFalse(Path(str(reply)+'.request').exists())
 def test_actual_wrong_argv_refuses_before_any_send(self):
  entry,env,t,config,path,reply=self.fixture()
  result=subprocess.run(['/usr/bin/python3','-I','-S','-B',str(entry),'toggle',json.dumps(t)],env=env,capture_output=True,text=True,timeout=4)
  self.assertEqual(result.returncode,1,result.stderr);self.assertIn('final kernel argv differs',result.stderr);self.assertFalse(Path(str(reply)+'.request').exists())

if __name__=='__main__':unittest.main(verbosity=2)
