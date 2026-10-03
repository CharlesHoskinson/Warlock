"""Owned Unix kernel peer + protocol-fixture proof tests, no actual D-Bus/browser claim."""
from pathlib import Path
import os,socket,subprocess,tempfile,threading,unittest
from unittest.mock import patch
import bus_authority as b
class BusAuthority(unittest.TestCase):
 def run_proof(self,pid=None,uid=None,refused=False,stale=False,peer_wrong=False,preexec_wrong=False):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);sock.bind(str(root/'bus'));sock.listen();sock.settimeout(.1);stop=threading.Event()
   def accept():
    while not stop.is_set():
     try:c,_=sock.accept();c.close()
     except TimeoutError:continue
     except OSError:break
   thread=threading.Thread(target=accept);thread.start()
   identity={'pid':os.getpid(),'start':Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]};bus={**identity,'pid':os.getpid()+1 if peer_wrong else os.getpid()};address='unix:path='+str(root/'bus');binary=Path('/proc/self/exe').resolve()
   launch={'pid':identity['pid'],'start':identity['start'],'appBusSelectors':{'DBUS_SESSION_BUS_ADDRESS':address,'DBUS_SYSTEM_BUS_ADDRESS':address},'privateGioVfs':'local','binarySHA256':b.sha(binary)}
   if preexec_wrong:launch['appBusSelectors']['DBUS_SYSTEM_BUS_ADDRESS']='unix:path=/foreign/bus'
   commands=[]
   def query(cmd,**kwargs):
    commands.append(cmd);method=cmd[cmd.index('--method')+1].split('.')[-1]
    text={'ListNames':"(['org.freedesktop.DBus', ':1.0'],)",'GetConnectionUnixProcessID':f'(uint32 {os.getpid() if pid is None else pid},)','GetConnectionUnixUser':f'(uint32 {os.getuid() if uid is None else uid},)'}[method]
    return subprocess.CompletedProcess(cmd,1 if refused else 0,text,'fixture refusal' if refused else '')
   try:
    with patch.object(b,'BINARY',binary),patch.object(b.subprocess,'run',side_effect=query):r=b.prove(launch,identity,root,{'DBUS_SESSION_BUS_ADDRESS':address,'DBUS_SYSTEM_BUS_ADDRESS':address},bus,lambda x:not stale,lambda:None)
    return r,commands
   finally:stop.set();sock.close();thread.join(timeout=1)
 def test_actual_owned_kernel_peer_protocol_fixture_positive(self):
  r,cmd=self.run_proof();self.assertEqual(r['result'],'pass',r);self.assertEqual(len(cmd),3);self.assertEqual(r['connection']['pid'],os.getpid());self.assertTrue(r['rootLifetimeAfter'])
 def test_other_client_pid_not_browser(self):
  r,_=self.run_proof(pid=1);self.assertEqual(r['result'],'fail');self.assertIn('No actual exact owned',r['error'])
 def test_other_uid_refused(self):self.assertEqual(self.run_proof(uid=os.getuid()+1)[0]['result'],'fail')
 def test_query_refusal_retained(self):
  r,_=self.run_proof(refused=True);self.assertEqual(r['result'],'fail');self.assertEqual(r['queries'][0]['returncode'],1)
 def test_stale_root_refused(self):
  r,cmd=self.run_proof(stale=True);self.assertEqual(r['result'],'fail');self.assertFalse(cmd)
 def test_wrong_actual_peer_refused(self):
  r,cmd=self.run_proof(peer_wrong=True);self.assertEqual(r['result'],'fail');self.assertFalse(cmd)
 def test_preexec_foreign_selector_refused(self):
  r,cmd=self.run_proof(preexec_wrong=True);self.assertEqual(r['result'],'fail');self.assertFalse(cmd)
 def test_method_mutation_refused(self):
  with self.assertRaises(RuntimeError):b.parse_reply('StartServiceByName','(uint32 1,)')
 def test_malformed_pid_refused(self):
  for value in ['(true,)','(-1,)','(4294967296,)','(1, 2)']:
   with self.assertRaises((RuntimeError,ValueError)):b.parse_reply('GetConnectionUnixProcessID',value)
 def test_duplicate_names_refused(self):
  with self.assertRaises(RuntimeError):b.parse_reply('ListNames',"(['org.freedesktop.DBus', ':1.0', ':1.0'],)")
if __name__=='__main__':unittest.main(verbosity=2)
