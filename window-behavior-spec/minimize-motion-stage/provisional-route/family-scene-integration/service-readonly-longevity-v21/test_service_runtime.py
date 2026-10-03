import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import select
import tempfile
import threading
import time
import unittest
from service_runtime import RuntimeService,RuntimeLease,JournalStore,stop_runtime,process_start,atomic_write
from test_scene_controller import Desktop,Transport

class ClosingTransport(Transport):
    def __init__(self):super().__init__();self.closed=False
    def close(self):self.closed=True;return 0

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='mr-');self.root=Path(self.temp.name)/'r';self.root.mkdir(mode=0o700)
        self.d=Desktop();self.boundaries=[];self.services=[];self.gate=threading.Event();self.entered=threading.Event()
        self.threads=[];self.thread_errors=[]
    def tearDown(self):
        self.gate.set()
        for r in self.services:
            try:r.close()
            except RuntimeError:pass
        for t in self.threads:t.join(3)
        self.temp.cleanup()
    def factory(self,number):
        t=ClosingTransport();self.boundaries.append(t);return self.d,t
    def context(self,request):self.entered.set();self.gate.wait(3);return 'trusted-fixture'
    def create(self,**kw):
        r=RuntimeService(self.root,'private-session',self.factory,self.context,**kw);self.services.append(r);return r
    def call(self,row,path=None):
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
            s.settimeout(2);s.connect(str(path or self.root/'api.sock'));s.sendall(json.dumps(row).encode()+b'\n')
            data=bytearray()
            while b'\n' not in data:data.extend(s.recv(8192))
            return json.loads(data)
    def request(self):
        w=self.d.windows[0];return self.call({'command':'request','operation':'minimize','address':w['address'],'stableId':w['stableId'],'pid':w['pid']})
    def run_service(self,r):
        def execute():
            try:r.run()
            except Exception as error:self.thread_errors.append(str(error))
        t=threading.Thread(target=execute);self.threads.append(t);t.start()
        self.wait(lambda:r.frontend.accept_thread is not None)
    def wait(self,p):
        end=time.monotonic()+3
        while time.monotonic()<end:
            if p():return
            time.sleep(.002)
        self.fail('runtime boundary timeout')
    def test_real_socket_ack_contains_already_fsynced_pending_identity(self):
        r=self.create();r.start();reply=self.request();self.assertTrue(reply['accepted']);self.assertTrue(self.entered.wait(1))
        body=JournalStore(self.root,'private-session').read();self.assertEqual(body['pending'][0]['receipt'],reply['receipt'])
        self.assertEqual(body['pending'][0]['captured'],['0xaa01','aa01',41]);self.assertEqual(body['receipts'][0][1],reply['receipt'])
        self.assertFalse(self.d.commits);self.assertFalse(self.boundaries[0].sent)
    def test_duplicate_lease_cannot_bind_or_replace_existing_socket(self):
        r=self.create();before=(self.root/'api.sock').stat().st_ino
        with self.assertRaises(BlockingIOError):self.create()
        self.assertEqual((self.root/'api.sock').stat().st_ino,before);self.assertFalse(self.boundaries)
    def test_public_or_symlink_runtime_is_refused_before_factory(self):
        self.root.chmod(0o755)
        with self.assertRaises(ValueError):self.create()
        self.root.chmod(0o700);alias=Path(self.temp.name)/'alias';alias.symlink_to(self.root)
        with self.assertRaises(ValueError):RuntimeService(alias,'private-session',self.factory,self.context)
        self.assertFalse(self.boundaries)
    def test_idle_stop_absence_never_creates_runtime_or_factory(self):
        missing=Path(self.temp.name)/'absent';self.assertTrue(stop_runtime(missing,'private-session')['alreadyStopped'])
        self.assertFalse(missing.exists());before=list(self.root.iterdir());self.assertTrue(stop_runtime(self.root,'private-session')['alreadyStopped'])
        self.assertEqual(list(self.root.iterdir()),before);self.assertFalse(self.boundaries)
    def test_real_stop_closes_idle_listener_and_owned_pid_but_retains_lock_inode(self):
        r=self.create();self.run_service(r);lock_inode=(self.root/'runtime.lock').stat().st_ino
        reply=stop_runtime(self.root,'private-session');self.assertTrue(reply['stopping'])
        self.threads[-1].join(3);self.assertFalse(self.threads[-1].is_alive());self.assertFalse(self.thread_errors)
        self.assertFalse((self.root/'api.sock').exists());self.assertFalse((self.root/'owner.json').exists())
        self.assertEqual((self.root/'runtime.lock').stat().st_ino,lock_inode)
        self.assertTrue(stop_runtime(self.root,'private-session')['alreadyStopped'])
    def test_stop_ack_refuses_following_request_before_runtime_cleanup(self):
        r=self.create();r.start();reply=self.call({'command':'stop'});self.assertTrue(reply['stopping'])
        w=self.d.windows[0]
        with self.assertRaisesRegex(RuntimeError,'queue unavailable'):
            r.frontend.dispatch({'command':'request','operation':'minimize','address':w['address'],'stableId':w['stableId'],'pid':w['pid']})
        self.assertFalse(self.boundaries);self.assertFalse(self.d.commits)
    def test_stop_unknown_socket_never_sends_any_request(self):
        foreign=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);foreign.bind(str(self.root/'api.sock'));foreign.listen(1);foreign.settimeout(.05)
        try:
            with self.assertRaises(ValueError):stop_runtime(self.root,'private-session')
            with self.assertRaises(socket.timeout):foreign.accept()
        finally:foreign.close();(self.root/'api.sock').unlink()
    def test_journal_write_failure_refuses_acceptance_and_all_old_native_authority(self):
        r=self.create();r.start()
        r.store.write=lambda value:(_ for _ in ()).throw(OSError('injected durable write failure'))
        reply=self.request();self.assertFalse(reply['accepted']);self.assertIn('durable journal',reply['error'])
        self.assertTrue(r.manager.persistence_failed);self.assertTrue(r.manager.closed);self.assertTrue(r.stop_requested.is_set())
        self.assertFalse(self.d.commits);self.assertFalse(self.entered.is_set())
        with self.assertRaises(RuntimeError):r.close()
        self.assertTrue(all(t.closed for t in self.boundaries));self.assertFalse((self.root/'api.sock').exists())
    def test_nonempty_unresolved_restart_refuses_before_actor_or_listener(self):
        JournalStore(self.root,'private-session').write({'version':1,'session':'private-session','snapshot':2,'pending':[{'receipt':1}],'scenes':[]})
        with self.assertRaisesRegex(RuntimeError,'fresh-native recovery'):self.create()
        self.assertFalse(self.boundaries);self.assertFalse((self.root/'api.sock').exists())
        with self.assertRaisesRegex(RuntimeError,'unresolved'):stop_runtime(self.root,'private-session')
    def test_wrong_session_or_corrupt_journal_cannot_start_actor(self):
        store=JournalStore(self.root,'other');store.write({'version':1,'session':'other','snapshot':2,'pending':[],'scenes':[]})
        with self.assertRaises(ValueError):self.create()
        (self.root/'journal.json').write_text('{"body":{},"sha256":"fake"}');(self.root/'journal.json').chmod(0o600)
        with self.assertRaises(ValueError):self.create()
        self.assertFalse(self.boundaries)
    def test_stale_exact_owner_socket_is_recovered_but_replacement_socket_refused(self):
        old=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);old.bind(str(self.root/'api.sock'));s=(self.root/'api.sock').stat();old.close()
        atomic_write(self.root/'owner.json',json.dumps({'session':'private-session','pid':2147483647,'start':99,'nonce':'dead','socket':[s.st_dev,s.st_ino]}).encode())
        r=self.create();self.assertFalse(self.boundaries);r.close()
        another=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);another.bind(str(self.root/'api.sock'));another.close()
        atomic_write(self.root/'owner.json',json.dumps({'session':'private-session','pid':2147483647,'start':99,'nonce':'dead','socket':[0,0]}).encode())
        with self.assertRaisesRegex(ValueError,'replaced'):self.create()
    def test_dead_archived_pid_never_authorizes_removing_still_live_listener(self):
        listener=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);listener.bind(str(self.root/'api.sock'));listener.listen(1)
        state=(self.root/'api.sock').stat()
        atomic_write(self.root/'owner.json',json.dumps({'session':'private-session','pid':2147483647,'start':99,'nonce':'dead','socket':[state.st_dev,state.st_ino]}).encode())
        try:
            with self.assertRaisesRegex(ValueError,'live socket listener'):self.create()
            self.assertEqual((self.root/'api.sock').stat().st_ino,state.st_ino);self.assertFalse(self.boundaries)
        finally:listener.close()
    def test_durable_failure_after_existing_scene_prevents_old_ready_core_callback(self):
        r=self.create();r.start();self.gate.set();self.request()
        self.wait(lambda:r.manager.actors[0].controller.current and r.manager.actors[0].controller.current.validated)
        c=r.manager.actors[0].controller;old=c.current
        r.store.write=lambda value:(_ for _ in ()).throw(OSError('later fsync failure'))
        reply=self.request();self.assertFalse(reply['accepted'])
        from scene_controller import ids
        self.assertFalse(c.event({'event':'ready','token':old.token,'identities':ids(old.members),'servicePromoted':True,'sourceDigests':[{k:s[k] for k in ('stableId','pid','digest')} for s in old.sources]}))
        self.assertFalse(self.d.commits)
        with self.assertRaises(RuntimeError):r.close()
        self.assertTrue(all(t.closed for t in self.boundaries))
    def test_empty_restart_preserves_monotonic_snapshot_number(self):
        first=self.create();before=first.store.read()['snapshot'];first.close();before=JournalStore(self.root,'private-session').read()['snapshot']
        second=self.create();self.assertGreater(second.store.read()['snapshot'],before);self.assertFalse(self.boundaries)
    def test_actual_idle_daemon_pid_peer_and_duplicate_process_lease(self):
        command=[sys.executable,str(Path(__file__).with_name('runtime_fixture.py')),'--root',str(self.root)]
        child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            self.assertTrue(select.select([child.stdout],[],[],3)[0],'idle daemon did not report readiness')
            ready=json.loads(child.stdout.readline());self.assertTrue(ready['ready']);self.assertEqual(ready['pid'],child.pid);self.assertEqual(ready['actors'],[])
            owner=json.loads((self.root/'owner.json').read_text());self.assertEqual(owner['pid'],child.pid);self.assertEqual(owner['start'],process_start(child.pid))
            inode=(self.root/'api.sock').stat().st_ino
            duplicate=subprocess.run(command,text=True,capture_output=True,timeout=3)
            self.assertEqual(duplicate.returncode,2);self.assertFalse(json.loads(duplicate.stdout)['ready'])
            self.assertEqual((self.root/'api.sock').stat().st_ino,inode)
            state=self.call({'command':'state'});self.assertEqual(state['actors'],[]);self.assertEqual(state['pendingReceipts'],[])
            self.assertTrue(stop_runtime(self.root,'private-session')['stopping']);self.assertEqual(child.wait(timeout=3),0)
            self.assertFalse((self.root/'api.sock').exists());self.assertFalse((self.root/'owner.json').exists())
            self.assertTrue(stop_runtime(self.root,'private-session')['alreadyStopped'])
        finally:
            if child.poll() is None:child.terminate();child.wait(timeout=3)
            child.stdout.close();child.stderr.close()
    def test_lease_owner_loss_refuses_normal_cleanup_and_preserves_foreign_record(self):
        r=self.create();foreign={'pid':os.getpid(),'start':process_start(os.getpid()),'session':'private-session','nonce':'foreign','socket':None}
        atomic_write(self.root/'owner.json',json.dumps(foreign).encode())
        with self.assertRaisesRegex(RuntimeError,'owner PID/start/nonce'):r.close()
        self.assertTrue(r.manager.persistence_failed)
        os.close(r.lease.fd);r.lease.fd=None
        self.assertEqual(json.loads((self.root/'owner.json').read_text()),foreign)

if __name__=='__main__':unittest.main()
