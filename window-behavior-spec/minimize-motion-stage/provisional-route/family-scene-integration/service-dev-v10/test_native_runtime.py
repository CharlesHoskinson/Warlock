import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
from native_runtime import PinnedExecutable,NativeSession,FailureBinding,sanitize_environment,request_runtime,UncertainAcceptance
from service_runtime import process_start

class NativeCompositionTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='ns-');self.root=Path(self.tmp.name);self.root.chmod(0o700)
    def tearDown(self):self.tmp.cleanup()
    def script(self,text='original'):
        p=self.root/'exec';p.write_text('#!/bin/sh\nprintf '+text+'\n');p.chmod(0o700);return p,hashlib.sha256(p.read_bytes()).hexdigest()
    def test_pinned_exec_runs_original_inode_after_path_replacement(self):
        path,digest=self.script()
        with PinnedExecutable(path,digest) as executable:
            replacement=self.root/'new';replacement.write_text('#!/bin/sh\nprintf replaced\n');replacement.chmod(0o700);replacement.replace(path)
            self.assertEqual(subprocess.check_output([executable.path],pass_fds=(executable.fd,)),b'original')
    def test_in_place_edit_cannot_change_sealed_executable(self):
        path,digest=self.script()
        with PinnedExecutable(path,digest) as executable:
            path.write_text('#!/bin/sh\nprintf replaced\n')
            self.assertEqual(subprocess.check_output([executable.path],pass_fds=(executable.fd,)),b'original')
            with self.assertRaises(OSError):os.write(executable.fd,b'changed')
    def test_wrong_digest_refuses_before_execution(self):
        p,_=self.script()
        with self.assertRaisesRegex(ValueError,'digest'):PinnedExecutable(p,'0'*64)
    def test_symlink_and_writable_exec_refuse(self):
        p,h=self.script();link=self.root/'link';link.symlink_to(p)
        with self.assertRaises(OSError):PinnedExecutable(link,h)
        p.chmod(0o722)
        with self.assertRaisesRegex(ValueError,'unsafe'):PinnedExecutable(p,h)
    def test_request_flags_are_removed_but_exact_session_preserved(self):
        env={'HYPR_WINDOWCTL_FAMILY_SINGLE':'1','HYPR_WINDOWCTL_ASYNC':'1','HYPR_WINDOWCTL_FRONTEND':'foreign','HYPRLAND_INSTANCE_SIGNATURE':'exact','WAYLAND_DISPLAY':'chosen','PATH':'/usr/bin'}
        self.assertEqual(sanitize_environment(env),{'HYPRLAND_INSTANCE_SIGNATURE':'exact','WAYLAND_DISPLAY':'chosen','PATH':'/usr/bin'})
    def listeners(self):
        d=self.root/'hypr'/'chosen';d.mkdir(parents=True);paths=(d/'.socket.sock',self.root/'wayland-test');sockets=[]
        for path in paths:
            s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);s.bind(str(path));s.listen(10);self.addCleanup(s.close);sockets.append(s)
        return paths,sockets
    def env(self):return {'XDG_RUNTIME_DIR':str(self.root),'HYPRLAND_INSTANCE_SIGNATURE':'chosen','WAYLAND_DISPLAY':'wayland-test'}
    def test_actual_two_socket_peers_match_selected_pid_start(self):
        self.listeners();s=NativeSession('chosen',os.getpid(),process_start(os.getpid()),'wayland-test',self.env());self.assertEqual(s.pid,os.getpid())
    def test_environment_mismatch_refuses_before_connect(self):
        self.listeners()
        with self.assertRaisesRegex(ValueError,'environment'):NativeSession('foreign',os.getpid(),process_start(os.getpid()),'wayland-test',self.env())
    def test_pid_start_reuse_refuses_before_connect(self):
        self.listeners()
        with self.assertRaisesRegex(ValueError,'reused'):NativeSession('chosen',os.getpid(),process_start(os.getpid())+1,'wayland-test',self.env())
    def test_socket_replacement_is_not_selected_compositor(self):
        paths,_=self.listeners();paths[1].unlink();paths[1].write_text('not a socket')
        with self.assertRaisesRegex(ValueError,'socket identity'):NativeSession('chosen',os.getpid(),process_start(os.getpid()),'wayland-test',self.env())
    def test_early_failure_delivered_once_after_controller_binding(self):
        b=FailureBinding();calls=[];done=threading.Event();b('first');b('second');self.assertFalse(calls)
        b.bind(lambda reason:(calls.append(reason),done.set()));self.assertTrue(done.wait(1));b('third');self.assertEqual(calls,['first'])
    def api(self,response):
        path=self.root/'api.sock';s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);s.bind(str(path));path.chmod(0o600);s.listen(1);self.addCleanup(s.close)
        st=path.stat();owner={'pid':os.getpid(),'start':process_start(os.getpid()),'session':'chosen','socket':[st.st_dev,st.st_ino]};p=self.root/'owner.json';p.write_text(json.dumps(owner));p.chmod(0o600)
        received=[]
        def serve():
            c,_=s.accept()
            with c:received.append(c.recv(8192));c.sendall(response)
        t=threading.Thread(target=serve);t.start();self.addCleanup(lambda:t.join(1));return received
    def test_actual_api_acceptance_is_receipt_not_completion(self):
        received=self.api(b'{"ok":true,"accepted":true,"completed":false,"receipt":9}\n')
        r=request_runtime(self.root,'chosen',{'command':'request','operation':'minimize','address':'0xab','stableId':'ab','pid':2});self.assertTrue(r['accepted']);self.assertFalse(r['completed']);self.assertEqual(len(received),1)
    def test_lost_response_is_uncertain_and_single_send_without_fallback(self):
        received=self.api(b'')
        with self.assertRaises(UncertainAcceptance):request_runtime(self.root,'chosen',{'command':'state'})
        self.assertEqual(len(received),1)
    def test_missing_service_never_creates_or_autostarts(self):
        missing=self.root/'absent'
        with self.assertRaises(FileNotFoundError):request_runtime(missing,'chosen',{'command':'state'})
        self.assertFalse(missing.exists())

if __name__=='__main__':unittest.main()
