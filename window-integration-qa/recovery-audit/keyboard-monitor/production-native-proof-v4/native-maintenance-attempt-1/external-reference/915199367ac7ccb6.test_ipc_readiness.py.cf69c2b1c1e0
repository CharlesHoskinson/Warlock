"""Real bounded Unix IPC exchange in owned QA runtime; no compositor or GUI."""
from pathlib import Path
from unittest.mock import patch
import json,os,shutil,socket,threading,unittest
import weston_host as h

class FakeOwnedProcess:
 def poll(self):return None

class Readiness(unittest.TestCase):
 def setUp(self):
  h.original.qa.require_qa_scope();self.runtime=h.original.qa.private_runtime();self.host=h.ReviewedWestonHost(Path('/unused'),{},320,240);self.host.runtime=self.runtime
  self.proc=FakeOwnedProcess();self.row=h.original.process(os.getpid());self.row.update(name='hyprland',command=['/usr/bin/Hyprland']);self.host.processes=[(self.proc,self.row)]
  self.name='hypr/test_signature/.socket.sock';self.path=self.runtime/self.name;self.path.parent.mkdir(parents=True,mode=0o700);self.threads=[];self.servers=[];self.requests=[];self.errors=[]
 def tearDown(self):
  for t in self.threads:t.join(3);self.assertFalse(t.is_alive())
  for server in self.servers:server.close()
  shutil.rmtree(self.runtime)
 def server(self,payload=b'{"version":"fixture-only"}',after=None,fragment=False):
  server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);server.bind(str(self.path));server.listen(1);server.settimeout(2);self.servers.append(server)
  def work():
   try:
    connection,_=server.accept()
    with connection:
     connection.settimeout(2);self.requests.append(connection.recv(4096))
     if fragment:
      for byte in payload:connection.sendall(bytes([byte]))
     else:connection.sendall(payload)
     if after:after()
   except (BrokenPipeError,ConnectionResetError):pass
   except Exception as error:self.errors.append(repr(error))
  t=threading.Thread(target=work);t.start();self.threads.append(t)
 def test_complete_real_exchange_and_own_credentials(self):
  self.server();before=dict(os.environ);self.host.wait_socket(self.name,self.proc)
  self.assertEqual(self.requests,[b'j/version']);row=self.host.evidence['ipcReadiness'][0];self.assertEqual(row['peer']['pid'],os.getpid());self.assertEqual(row['peer']['uid'],os.getuid());self.assertTrue(row['completeServerEOF']);self.assertEqual(row['version'],{'version':'fixture-only'});self.assertEqual(dict(os.environ),before)
 def test_fragmented_json_reply(self):
  self.server(b'{"version":"fixture","data":[1,2,3]}',fragment=True);self.host.wait_socket(self.name,self.proc);self.assertEqual(self.requests,[b'j/version'])
 def test_invalid_json_refused(self):
  self.server(b'unknown request')
  with self.assertRaises(json.JSONDecodeError):self.host.wait_socket(self.name,self.proc)
 def test_truncated_json_refused(self):
  self.server(b'{"version":')
  with self.assertRaises(json.JSONDecodeError):self.host.wait_socket(self.name,self.proc)
 def test_empty_and_nonobject_refused(self):
  self.server(b'[]')
  with self.assertRaises(RuntimeError):self.host.wait_socket(self.name,self.proc)
 def test_oversize_refused(self):
  self.server(b'{"version":"'+b'x'*70000+b'"}')
  with self.assertRaises(RuntimeError):self.host.wait_socket(self.name,self.proc)
 def test_exact_peer_pid_required(self):
  self.server();self.row['pid']+=99999
  with patch.object(h.original,'same_process',return_value=True),self.assertRaisesRegex(RuntimeError,'peer identity'):self.host.wait_socket(self.name,self.proc)
 def test_changed_inode_after_reply_refused(self):
  def replace():
   self.path.unlink();replacement=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);replacement.bind(str(self.path));self.servers.append(replacement)
  self.server(after=replace)
  with self.assertRaisesRegex(RuntimeError,'replaced after reply'):self.host.wait_socket(self.name,self.proc)
 def test_changed_process_before_connection_refused(self):
  with patch.object(h.original,'same_process',return_value=False),self.assertRaisesRegex(RuntimeError,'changed identity'):self.host.wait_socket(self.name,self.proc)
 def test_unregistered_child_refused(self):
  self.host.processes=[]
  with self.assertRaisesRegex(RuntimeError,'registered child'):self.host.wait_socket(self.name,self.proc)
 def test_foreign_peer_uid_refused(self):
  self.server()
  with patch.object(h.struct,'unpack',return_value=(os.getpid(),os.getuid()+1,os.getgid())),self.assertRaisesRegex(RuntimeError,'peer identity'):self.host.wait_socket(self.name,self.proc)
 def test_nonreviewed_child_command_refused(self):
  self.row['command']=['/other/Hyprland']
  with self.assertRaisesRegex(RuntimeError,'registered child'):self.host.wait_socket(self.name,self.proc)
 def test_empty_object_refused(self):
  self.server(b'{}')
  with self.assertRaises(RuntimeError):self.host.wait_socket(self.name,self.proc)
 def test_foreign_absolute_and_malformed_path_refused(self):
  for name in ['/run/user/1000/hypr/main/.socket.sock','hypr/../.socket.sock','other/test/.socket.sock','hypr/test/nested/.socket.sock']:
   with self.subTest(name=name),self.assertRaises(RuntimeError):self.host.wait_socket(name,self.proc)
 def test_original_wayland_parent_and_socket2_readiness_kept(self):
  for name in ['weston-host','wayland-1','hypr/test/.socket2.sock','bus']:
   with patch.object(h.original.PrivateWestonHost,'wait_socket',return_value='original') as method:
    self.assertEqual(self.host.wait_socket(name,self.proc),'original');method.assert_called_once_with(name,self.proc)
 def test_qa_scope_checked_before_ipc(self):
  with patch.object(h.original.qa,'require_qa_scope',side_effect=RuntimeError('outside scope')),self.assertRaisesRegex(RuntimeError,'outside scope'):self.host.wait_socket(self.name,self.proc)

if __name__=='__main__':unittest.main()
