import importlib.util
import json
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch
from native_runtime import NativeSession
from service_runtime import process_start

class CompleteIPCProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ip-');self.root=Path(self.tmp.name);self.root.chmod(0o700)
        d=self.root/'hypr'/'chosen';d.mkdir(parents=True);self.ipc=d/'.socket.sock';self.wayland=self.root/'wayland-test'
        self.servers=[];self.stop=threading.Event();self.rows=[]
        self.env={'XDG_RUNTIME_DIR':str(self.root),'HYPRLAND_INSTANCE_SIGNATURE':'chosen','WAYLAND_DISPLAY':'wayland-test'}
    def tearDown(self):
        self.stop.set()
        for s,t in self.servers:s.close();t.join(1)
        self.tmp.cleanup()
    def server(self,reply=b'{"tag":"complete-fixture"}',*,stall=False,chunks=False,replace=False):
        wl=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);wl.bind(str(self.wayland));wl.listen(4)
        ipc=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);ipc.bind(str(self.ipc));ipc.listen(4);ipc.settimeout(.1)
        def run():
            while not self.stop.is_set():
                try:c,_=ipc.accept()
                except socket.timeout:continue
                except OSError:return
                with c:
                    request=c.recv(1024);row={'request':request.decode(),'replyBytes':0};self.rows.append(row)
                    try:
                        if not request:c.sendall(b'error: empty request');row['unexpectedZeroReplySucceeded']=True
                        else:
                            if replace:
                                self.ipc.unlink();self.ipc.write_text('replaced socket')
                            if chunks:
                                for p in (reply[:3],reply[3:11],reply[11:]):c.sendall(p);row['replyBytes']+=len(p)
                            else:c.sendall(reply);row['replyBytes']=len(reply)
                            if stall:self.stop.wait(2)
                    except OSError as e:row['serverError']=type(e).__name__
        t=threading.Thread(target=run,daemon=True);t.start();dummy=threading.Thread(target=lambda:None);dummy.start()
        self.servers.extend([(ipc,t),(wl,dummy)])
    def verify(self):return NativeSession('chosen',os.getpid(),process_start(os.getpid()),'wayland-test',self.env)
    def test_retained_v10_zero_request_closes_before_server_error_reply(self):
        self.server();path=Path(__file__).parent.parent/'service-review-v10/native_runtime.py'
        spec=importlib.util.spec_from_file_location('retained_v10_runtime',path);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
        old.NativeSession('chosen',os.getpid(),process_start(os.getpid()),'wayland-test',self.env)
        for _ in range(100):
            if self.rows and ('serverError' in self.rows[0] or 'unexpectedZeroReplySucceeded' in self.rows[0]):break
            self.stop.wait(.002)
        self.assertEqual(self.rows[0]['request'],'');self.assertEqual(self.rows[0].get('serverError'),'BrokenPipeError')
    def test_actual_nonempty_request_complete_multichunk_json_eof(self):
        self.server(chunks=True);guard=self.verify()
        self.assertEqual(self.rows[0]['request'],'j/version');self.assertNotIn('serverError',self.rows[0])
        self.assertTrue(guard.ipc_observation['completeServerEOF']);self.assertGreater(guard.ipc_observation['replyBytes'],0)
        self.assertEqual(guard.ipc_observation['version'],{'tag':'complete-fixture'})
    def test_empty_reply_refuses(self):
        self.server(b'')
        with self.assertRaises(json.JSONDecodeError):self.verify()
    def test_partial_json_refuses_after_server_eof(self):
        self.server(b'{"tag":')
        with self.assertRaises(json.JSONDecodeError):self.verify()
    def test_server_error_reply_refuses(self):
        self.server(b'{"error":"unsupported"}')
        with self.assertRaisesRegex(ValueError,'invalid/error'):self.verify()
    def test_oversized_reply_refuses(self):
        self.server(b'{"tag":"'+b'x'*65536+b'"}')
        with self.assertRaisesRegex(ValueError,'exceeds bound'):self.verify()
    def test_complete_json_without_eof_times_out(self):
        self.server(stall=True)
        with self.assertRaises(TimeoutError):self.verify()
    def test_socket_replacement_after_reply_refuses(self):
        self.server(replace=True)
        with self.assertRaisesRegex(ValueError,'identity changed'):self.verify()
    def test_wrong_peer_refuses_before_any_readonly_command(self):
        self.server()
        with patch('native_runtime.process_start',return_value=1):
            # Expected live identity differs from actual socket peer. No command
            # is sent to the foreign socket, including j/version.
            with self.assertRaisesRegex(ValueError,'not selected'):NativeSession('chosen',os.getpid()+100000,1,'wayland-test',self.env)
        for _ in range(100):
            if self.rows:break
            self.stop.wait(.002)
        self.assertEqual(self.rows[0]['request'],'')

if __name__=='__main__':unittest.main()
