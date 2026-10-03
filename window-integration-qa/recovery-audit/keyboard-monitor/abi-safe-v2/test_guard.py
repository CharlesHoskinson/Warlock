#!/usr/bin/env python3
"""Offline/subprocess refusal tests. No D-Bus, compositor, X or AT-SPI factory."""
from pathlib import Path
import hashlib,json,os,socket,subprocess,sys,tempfile,threading,time,unittest
from abi_guard import BackendGuard,private_bus_socket
B=Path(__file__).resolve().parent
class Connection:
 closed=False
 def is_closed(self):return self.closed
class Device:
 def __init__(self,name):self.__gtype__=type('GType',(),{'name':name})();self.calls=[]
 def map_keysym_modifier(self,key):self.calls.append(key);return 1<<15
class GuardTests(unittest.TestCase):
 def setUp(self):self.bus=Connection();self.owner=':1.5';self.guard=BackendGuard(self.bus,self.owner,lambda:self.owner)
 def test_manager_pure_wayland_permitted(self):
  device=Device('AtspiDeviceA11yManager');self.guard.attach(device)
  self.assertEqual(self.guard.invoke('map_keysym_modifier',65509),1<<15);self.assertEqual(device.calls,[65509])
 def test_legacy_x11_and_unknown_refused_before_keys(self):
  for backend in ['AtspiDeviceLegacy','AtspiDeviceX11','unexpected']:
   device=Device(backend)
   with self.assertRaises(RuntimeError):self.guard.attach(device)
   self.assertEqual(device.calls,[])
 def test_owner_loss_refuses_before_keys(self):
  device=Device('AtspiDeviceA11yManager');self.guard.attach(device);self.owner=':1.9'
  with self.assertRaises(RuntimeError):self.guard.invoke('map_keysym_modifier',65509)
  self.assertEqual(device.calls,[])
 def test_disconnected_bus_refuses_before_keys(self):
  device=Device('AtspiDeviceA11yManager');self.guard.attach(device);self.bus.closed=True
  with self.assertRaises(RuntimeError):self.guard.invoke('map_keysym_modifier',65509)
  self.assertEqual(device.calls,[])
 def test_owned_live_private_unix_transport(self):
  with tempfile.TemporaryDirectory(prefix='abi-transport-') as directory:
   root=Path(directory);path=root/'bus'
   with socket.socket(socket.AF_UNIX) as server:
    server.bind(str(path));server.listen(1)
    evidence=private_bus_socket('unix:path='+str(path),root);self.assertEqual(evidence['serverPID'],os.getpid())
 def test_foreign_abstract_and_missing_transport_refusal(self):
  with tempfile.TemporaryDirectory(prefix='abi-transport-') as directory:
   for address in ['unix:path=/run/user/1000/bus','unix:abstract=main','unix:path='+directory+'/missing','']:
    with self.assertRaises((RuntimeError,FileNotFoundError)):private_bus_socket(address,Path(directory))
 def test_cli_offscope_refuses_before_bus_or_atspi(self):
  env=dict(os.environ);env.pop('KEYBOARD_ABI_RUNTIME',None)
  result=subprocess.run([sys.executable,str(B/'abi_client.py'),'org.gnome.Orca','orca'],env=env,capture_output=True,text=True,timeout=4)
  self.assertEqual(result.returncode,2);self.assertIn('qa-harness.slice',result.stderr);self.assertNotIn('Traceback',result.stderr)
 def test_owned_cleanup_refuses_reused_start_identity(self):
  from owned_cleanup import capture,stop_owned
  process=subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)'],start_new_session=True)
  try:
   record=capture(process,'client');record['start']='incorrect'
   result=stop_owned(record,seconds=.2);self.assertIn('refused',result['error']);self.assertIsNone(process.poll())
  finally:process.terminate();process.wait(timeout=2)
 def test_subprocess_clients_cleanup_precedes_service(self):
  from owned_cleanup import capture,stop_owned
  with tempfile.TemporaryDirectory(prefix='abi-cleanup-') as directory:
   log=Path(directory)/'order';children=[];records=[];reapers=[]
   code="import signal,sys,time;signal.signal(signal.SIGTERM,lambda a,b:(open(sys.argv[1],'a').write(sys.argv[2]+'\\n'),sys.exit(0)));print('ready',flush=True);time.sleep(20)"
   try:
    for role in ['service','client-a','client-b']:
     child=subprocess.Popen([sys.executable,'-c',code,str(log),role],stdout=subprocess.PIPE,text=True,start_new_session=True);children.append(child);self.assertEqual(child.stdout.readline().strip(),'ready');records.append(capture(child,role))
     reaper=threading.Thread(target=child.wait);reaper.start();reapers.append(reaper)
    for record in sorted(records,key=lambda r:r['role']=='service'):self.assertTrue(stop_owned(record,seconds=1)['gone'])
    self.assertEqual(log.read_text().splitlines(),['client-a','client-b','service'])
   finally:
    for child in children:
     if child.poll() is None:child.terminate()
     child.wait(timeout=2);child.stdout.close()
    for reaper in reapers:reaper.join(timeout=2)
 def test_original_sources_unchanged(self):
  for name,expected in json.loads((B/'original-inputs.json').read_text()).items():self.assertEqual(hashlib.sha256((B.parent/name).read_bytes()).hexdigest(),expected)

if __name__=='__main__':unittest.main()
