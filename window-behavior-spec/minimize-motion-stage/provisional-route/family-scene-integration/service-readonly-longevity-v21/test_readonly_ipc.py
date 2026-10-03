"""Actual Unix kernel peers and lease/fsync files; no native desktop socket."""
from copy import deepcopy
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
import unittest

from native_runtime import NativeSession
from owned_commands import OwnedCommands
from readonly_ipc import ReadonlyIPC, REQUESTS
from service_runtime import RuntimeLease, JournalStore, process_start


class CpuServer:
    def __init__(self,path,handle):
        self.path=path;self.handle=handle;self.requests=[];self.stop=threading.Event();self.children=[]
        self.listener=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.listener.bind(str(path));self.listener.listen(16);self.listener.settimeout(.1)
        self.thread=threading.Thread(target=self.accept,daemon=True);self.thread.start()
    def accept(self):
        while not self.stop.is_set():
            try:connection,_=self.listener.accept()
            except socket.timeout:continue
            except OSError:return
            thread=threading.Thread(target=self.client,args=(connection,),daemon=True)
            self.children.append(thread);thread.start()
    def client(self,connection):
        with connection:
            connection.settimeout(1)
            try:
                data=connection.recv(1024)
                self.requests.append(data)
                self.handle(connection,data)
            except (OSError,TimeoutError):pass
    def close(self):
        self.stop.set();self.listener.close();self.thread.join(timeout=1)
        for thread in self.children:thread.join(timeout=2)
        if self.path.exists():self.path.unlink()


class ReadonlyKernelTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='readonly-cpu-')
        self.runtime=Path(self.temporary.name);self.root=self.runtime/'service';self.root.mkdir(mode=0o700)
        self.session='cpu-readonly';directory=self.runtime/'hypr'/self.session;directory.mkdir(parents=True,mode=0o700)
        self.socket=directory/'.socket.sock';self.handler=lambda c,d:c.sendall(b'[]')
        def control(connection,data):
            if data==b'j/version':connection.sendall(b'{"cpuFixture":true}')
            else:self.handler(connection,data)
        self.control=CpuServer(self.socket,control)
        self.wayland=CpuServer(self.runtime/'cpu-wayland',lambda c,d:None)
        self.env=dict(os.environ,XDG_RUNTIME_DIR=str(self.runtime),HYPRLAND_INSTANCE_SIGNATURE=self.session,WAYLAND_DISPLAY='cpu-wayland')
        self.lease=RuntimeLease(self.root,self.session)
        self.guard=NativeSession(self.session,os.getpid(),process_start(os.getpid()),'cpu-wayland',self.env)
        self.store=JournalStore(self.root,self.session);self.serial=0;self.records=[];self.lock=threading.RLock();self.writer_fault=None
        def write(body):
            if self.writer_fault:self.writer_fault(body)
            self.lease.verify();self.serial+=1
            self.store.write({'version':1,'session':self.session,'snapshot':self.serial,'scenes':[],'pending':[],'readonlyOwnership':deepcopy(body)})
            self.records.append(deepcopy(body))
        self.reader=ReadonlyIPC(self.root,self.guard,self.lease.verify,write,reservation_lock=self.lock)
    def tearDown(self):
        self.control.close();self.wayland.close();self.lease.close();self.temporary.cleanup()
    def query(self,wire=b'j/clients',shape=list,timeout=1):
        return self.reader.query(wire,shape,timeout,1)
    def row(self):return list(self.reader.rows.values())[-1]
    def test_actual_peer_eof_fd_and_durable_history_before_return(self):
        self.assertEqual(self.query(),b'[]')
        row=self.row();self.assertTrue(row['closed']);self.assertTrue(row['published']);self.assertEqual(row['outcome'],'complete')
        self.assertEqual(row['evidence']['peer']['pid'],os.getpid())
        self.assertTrue(row['evidence']['completeServerEOF'])
        self.assertEqual(self.records[-1],self.store.read()['readonlyOwnership'])
        self.assertTrue(any(r['history'] and r['history'][-1]['outcome']=='pending' for r in self.records))
        self.assertTrue(all(r['closed'] for r in self.records[-1]['history']))
    def test_all_exact_fixed_requests_use_original_top_level_shapes(self):
        for wire,shape in REQUESTS.values():
            self.handler=lambda c,d,s=shape:c.sendall(b'{}' if s is dict else b'[]')
            self.assertEqual(json.loads(self.query(wire,shape)),{} if shape is dict else [])
        self.assertEqual(len(self.reader.rows),5)
    def test_direct_path_does_not_touch_keeper_or_execute_helper(self):
        class NoKeeper:
            def register(self,*a,**k):raise AssertionError('read-only data launched a helper')
        commands=OwnedCommands(NoKeeper(),self.env,1,readonly=self.reader)
        self.assertEqual(commands.check_output(['hyprctl','clients','-j'],text=True,timeout=1),'[]')
        before=len(self.reader.rows)
        for option in ('stdout','stderr'):
            with self.assertRaisesRegex(ValueError,'capture output conflicts'):
                commands.run(['hyprctl','clients','-j'],capture_output=True,timeout=1,**{option:subprocess.PIPE})
        self.assertEqual(len(self.reader.rows),before)
    def test_extra_flags_or_effect_or_user_expression_never_enter_direct_path(self):
        for args in [['hyprctl','clients','-j','--all'],['hyprctl','dispatch','closewindow'],['hyprctl','repl','print(hl.plugin.hyprbars.window_atlas())'],['hyprctl','repl','print(hl.plugin.hyprbars.window_families()); error("x")'],['hyprctl','reload']]:
            self.assertIsNone(self.reader.run(args,actor=1,env=self.env,input=None,capture_output=True,timeout=1,check=True,options={'text':True}))
        self.assertEqual(self.reader.rows,{})
    def test_partial_json_even_with_eof_is_terminal_refusal(self):
        self.handler=lambda c,d:c.sendall(b'[{')
        with self.assertRaises(ValueError):self.query()
        row=self.row();self.assertEqual(row['outcome'],'refused');self.assertTrue(row['closed']);self.assertTrue(row['published'])
        with self.assertRaisesRegex(ValueError,'terminal'):self.reader.finish(row['id'],closed=True,outcome='complete',evidence=row['evidence'],error=None)
        self.handler=lambda c,d:c.sendall(b'[]')
        self.assertEqual(self.query(),b'[]')
        self.assertEqual(len(self.reader.rows),2)
    def test_wrong_shape_and_invalid_utf8_refuse(self):
        for reply in [b'{"error":"refused"}',b'{}',b'\xff']:
            self.handler=lambda c,d,r=reply:c.sendall(r)
            with self.assertRaises((ValueError,UnicodeError)):self.query()
            self.assertEqual(self.row()['outcome'],'refused')
    def test_oversized_reply_refuses_and_closes_actual_descriptor(self):
        self.handler=lambda c,d:c.sendall(b' '*1048577)
        with self.assertRaisesRegex(ValueError,'bound'):self.query()
        self.assertTrue(self.row()['closed']);self.assertEqual(self.row()['outcome'],'refused')
    def test_absolute_timeout_is_not_reset_for_chunks(self):
        def chunks(c,d):
            c.sendall(b'[');time.sleep(.07);c.sendall(b' ');time.sleep(.07);c.sendall(b']')
        self.handler=chunks;begin=time.monotonic()
        with self.assertRaises(TimeoutError):self.query(timeout=.1)
        self.assertLess(time.monotonic()-begin,.3)
        self.assertEqual(self.row()['outcome'],'refused')
    def test_registration_fsync_failure_prevents_query_send_and_latches(self):
        def fail(body):
            if body['history']:raise OSError('registration fsync fault')
        self.writer_fault=fail
        with self.assertRaisesRegex(OSError,'fsync'):self.query()
        self.assertNotIn(b'j/clients',self.control.requests)
        self.writer_fault=None
        with self.assertRaisesRegex(ValueError,'revoked'):self.query()
    def test_completion_fsync_failure_never_returns_bytes(self):
        def fail(body):
            if any(r['outcome']=='complete' for r in body['history']):raise OSError('completion fsync fault')
        self.writer_fault=fail
        with self.assertRaisesRegex(OSError,'completion'):self.query()
        self.assertTrue(self.reader.fault)
        self.assertEqual(self.store.read()['readonlyOwnership']['history'][-1]['outcome'],'pending')
    def test_owner_replacement_during_reply_refuses(self):
        original=deepcopy(self.lease.owner)
        def replace(c,d):
            self.lease.owner['nonce']='f'*32;self.lease.publish_owner();c.sendall(b'[]')
        self.handler=replace
        try:
            with self.assertRaises(ValueError):self.query()
            self.assertEqual(self.row()['outcome'],'refused')
        finally:self.lease.owner=original;self.lease.publish_owner()
    def test_changed_socket_identity_during_reply_refuses(self):
        retained=self.socket.with_name('retained.sock')
        def replace(c,d):
            self.socket.rename(retained);self.socket.touch(mode=0o600);c.sendall(b'[]')
        self.handler=replace
        try:
            with self.assertRaises(ValueError):self.query()
            self.assertEqual(self.row()['outcome'],'refused')
        finally:
            if retained.exists():self.socket.unlink();retained.rename(self.socket)
    def test_history_capacity_archives_only_closed_rows_before_connection(self):
        import readonly_ipc
        from readonly_archive import segment_chain
        original=readonly_ipc.MAX_HISTORY;readonly_ipc.MAX_HISTORY=2
        try:
            self.query();self.query();before=self.control.requests.count(b'j/clients')
            self.assertEqual(self.query(),b'[]')
            self.assertEqual(self.control.requests.count(b'j/clients'),before+1)
            self.assertEqual(len(self.reader.rows),1)
            self.assertEqual(self.reader.serial,3)
            archived=segment_chain(self.reader.archive,self.reader.tip,issuer=readonly_ipc.digest(self.reader.issuer),
                epoch=1,validate_rows=lambda rows:None)
            self.assertEqual([r['serial'] for r in archived],[1,2])
            self.assertTrue(all(r['closed'] and r['published'] for r in archived))
        finally:readonly_ipc.MAX_HISTORY=original
    def test_healthy_parallel_rows_do_not_hold_manager_lock_during_io(self):
        waiting=threading.Event();release=threading.Event();errors=[]
        def slow(c,d):
            if d==b'j/clients':waiting.set();release.wait(1)
            c.sendall(b'[]')
        self.handler=slow
        thread=threading.Thread(target=lambda:self.query(),daemon=True);thread.start();self.assertTrue(waiting.wait(1))
        try:
            with self.lock:self.assertEqual(self.query(b'j/monitors'),b'[]')
        finally:release.set();thread.join(timeout=2)
        self.assertFalse(thread.is_alive());self.assertEqual(len(self.reader.rows),2)
        self.assertTrue(all(r['outcome']=='complete' for r in self.reader.rows.values()))

    def test_exact_selected_peer_change_refuses_before_data_request(self):
        original=self.guard.pid;self.guard.pid+=1
        try:
            with self.assertRaises(ValueError):self.query()
            self.assertNotIn(b'j/clients',self.control.requests)
            self.assertEqual(self.reader.rows,{})
        finally:self.guard.pid=original

    def test_source_alias_and_executable_path_replacement_refuse(self):
        import readonly_ipc
        original=readonly_ipc.__file__;copy=self.runtime/'alias.py';copy.write_bytes(Path(original).read_bytes());copy.chmod(0o600)
        readonly_ipc.__file__=str(copy)
        try:
            with self.assertRaises(ValueError):self.query()
        finally:readonly_ipc.__file__=original
        directory=self.runtime/'bin';directory.mkdir(mode=0o700);selected=directory/'hyprctl';selected.write_bytes(Path(self.reader.executable).read_bytes());selected.chmod(0o500)
        path=self.guard.env['PATH'];self.guard.env['PATH']=str(directory)
        try:
            with self.assertRaises(ValueError):self.query()
        finally:self.guard.env['PATH']=path
        self.assertNotIn(b'j/clients',self.control.requests)

    def test_postdisk_owner_replacement_revokes_completed_partial_proof(self):
        original=deepcopy(self.lease.owner);changed=[]
        def replace(body):
            if not changed and any(r['outcome']=='complete' for r in body['history']):
                changed.append(True);self.lease.owner['nonce']='e'*32;self.lease.publish_owner()
        self.writer_fault=replace
        try:
            with self.assertRaisesRegex(ValueError,'lease identity'):self.query()
            self.assertEqual(self.row()['outcome'],'refused')
            self.assertEqual(self.store.read()['readonlyOwnership']['history'][-1]['outcome'],'refused')
        finally:self.writer_fault=None;self.lease.owner=original;self.lease.publish_owner()

    def test_retained_history_schema_does_not_bless_effect_or_partial_return(self):
        from readonly_ipc import checked_retained
        self.query();body=self.reader.snapshot();issuer=body['issuer']
        keeper={'servicePID':issuer['pid'],'serviceStart':issuer['start'],'rootIdentity':issuer['rootIdentity']}
        environment={k:self.env[k] for k in issuer['environment']}
        check=lambda b:checked_retained(b,root=self.root,environment=environment,keeper=keeper,guard=self.guard)
        self.assertEqual(check(body),body)
        for mutation in ['effect','partial','unknownSource','booleanPID']:
            bad=deepcopy(body)
            if mutation=='effect':bad['history'][0]['request']='/dispatch closewindow'
            elif mutation=='partial':bad['history'][0]['evidence']['completeServerEOF']=False
            elif mutation=='unknownSource':bad['issuer']['adapter']['sha256']='f'*64
            else:bad['issuer']['pid']=True
            with self.assertRaises(ValueError):check(bad)

    def test_normal_factory_closure_refuses_actual_pending_connection(self):
        waiting=threading.Event();release=threading.Event();errors=[]
        def slow(c,d):waiting.set();release.wait(1);c.sendall(b'[]')
        self.handler=slow
        def query():
            try:self.query()
            except Exception as error:errors.append(str(error))
        thread=threading.Thread(target=query,daemon=True);thread.start();self.assertTrue(waiting.wait(1))
        try:
            with self.assertRaisesRegex(ValueError,'incomplete'):self.reader.assert_closed()
        finally:release.set();thread.join(timeout=2)
        self.assertFalse(errors);self.reader.assert_closed()


if __name__=='__main__':unittest.main()
