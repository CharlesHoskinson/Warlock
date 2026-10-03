"""Actual locks, sealed helper jobs, writer and PNGs; no native desktop."""
from copy import deepcopy
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import batch_preview as batch
import test_batch_preview as fixtures
from helper_supervisor import Keeper
from owned_commands import OwnedCommands, SealedFile
from owned_launch import OwnedLaunch
from pipe_transport import PipeTransport
from native_runtime import FailureBinding

B=Path(__file__).parent
WRITER=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v9/payload/home/.local/bin/hypr-window-preview')
WRITER_SHA='123206521803a61fbcef58abb25922b9d53bbdae0a90e1d408e9d6d58f31d177'

class AdmissionKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build=tempfile.TemporaryDirectory();cls.executable=Path(cls.build.name)/'renderer-cpu'
        subprocess.run(['/usr/bin/gcc','-O2','-Wall','-Wextra','-Werror',str(B/'renderer_role_cpu_fixture.c'),'-o',str(cls.executable)],check=True,timeout=10)
    @classmethod
    def tearDownClass(cls):cls.build.cleanup()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.actor=self.root/'actor';self.actor.mkdir(mode=0o700)
        home=self.root/'home';home.mkdir(mode=0o700)
        self.preview=self.root/'hypr-window-previews';self.records=[]
        self.env=dict(os.environ,HOME=str(home),XDG_RUNTIME_DIR=str(self.root),HYPRLAND_INSTANCE_SIGNATURE='offline',WAYLAND_DISPLAY='never-connect')
        self.keeper=Keeper(self.root,self.env,lambda row:self.records.append(deepcopy(row)))
        self.commands=OwnedCommands(self.keeper,self.env,17)
        self.batch=batch.BatchPreviews(self.actor,self.preview,self.commands)
        self.members=[];self.sources=[];self.metadata=[];self.lock=threading.RLock();self.transports=[]
        self.current=True;self.errors=[];self.workers=[];self.external=[]
    def tearDown(self):
        for worker in self.workers:worker.join(timeout=3);self.assertFalse(worker.is_alive())
        for process in self.external:
            if process.poll()is None:process.kill();process.communicate(timeout=2)
        for transport in self.transports:
            if not transport.closed:self.assertEqual(transport.close(),0)
        if not self.keeper.closed:
            if self.keeper.jobs:self.keeper.abort()
            else:self.keeper.stop()
        self.tmp.cleanup()
    stage=fixtures.BatchTests.stage
    assert_no_publication=fixtures.BatchTests.assert_no_publication
    def small(self):self.stage([(80,50,3,4,False,1)]*3)
    def finish(self,deadline_ns=None):
        self.batch.finish(self.sources,self.members,clients=lambda:deepcopy(self.members),current=lambda:self.current,reservation_lock=self.lock,deadline_ns=deadline_ns)
    def deadline(self,seconds=2):return time.monotonic_ns()+int(seconds*1000000000)
    def background(self,deadline):
        def work():
            try:self.finish(deadline)
            except BaseException as e:self.errors.append(e)
        worker=threading.Thread(target=work);self.workers.append(worker);worker.start();return worker
    def hold(self,index=1):
        self.preview.mkdir(mode=0o700,exist_ok=True)
        path=self.preview/(self.members[index]['address']+'.lock')
        stream=path.open('w');fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        return stream
    def observe_busy(self,event):
        original=fcntl.flock
        def observe(fd,flags):
            try:return original(fd,flags)
            except BlockingIOError:
                event.set();raise
        return patch.object(batch.fcntl,'flock',observe)
    def renderer(self):
        with SealedFile(self.executable)as sealed:
            transport=PipeTransport('/proc/self/fd/'+str(sealed.fd),env=self.env,failure=FailureBinding(),pass_fds=(sealed.fd,),keeper=self.keeper,actor=17)
        self.transports.append(transport)
        self.batch.bind_renderer(transport,hashlib.sha256(self.executable.read_bytes()).hexdigest())
        limit=time.monotonic()+2
        while not transport.outputs()and time.monotonic()<limit:time.sleep(.002)
        self.assertTrue(transport.outputs());self.assertTrue(self.batch._closed())
        return transport
    def test_actual_unchanged_writer_busy_then_release_genuine_renderer_and_six_pixels(self):
        self.assertEqual(hashlib.sha256(WRITER.read_bytes()).hexdigest(),WRITER_SHA)
        transport=self.renderer();self.small()
        directory=self.root/'fixture-bin';directory.mkdir(mode=0o700)
        marker=self.root/'writer-owns-lock';permit=self.root/'writer-permit'
        target=dict(self.members[1],mapped=True,hidden=False,workspace={'name':'1'},size=[80,50])
        query='#!/usr/bin/python3\nimport pathlib,time\np=pathlib.Path('+repr(str(marker))+')\np.touch()\nd=time.monotonic()+1.8\nwhile not pathlib.Path('+repr(str(permit))+').exists():\n if time.monotonic()>d:raise TimeoutError("CPU fixture permit")\n time.sleep(.002)\nprint('+repr(json.dumps([target]))+')\n'
        export='#!/usr/bin/python3\nimport shutil,sys\nshutil.copyfile('+repr(self.sources[1]['path'])+',sys.argv[-1])\n'
        for name,source in [('hyprctl',query),('grim',export)]:
            path=directory/name;path.write_text(source);path.chmod(0o700)
        env=dict(self.env,PATH=str(directory)+':/usr/bin')
        writer=subprocess.Popen(['/usr/bin/bash',str(WRITER),'capture-both',target['address'],'0'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);self.external.append(writer)
        try:
            limit=time.monotonic()+2
            while not marker.exists()and time.monotonic()<limit:time.sleep(.002)
            self.assertTrue(marker.exists());self.assertIsNone(writer.poll())
            live=deepcopy(next(iter(self.keeper.jobs.values())))
            self.assertEqual(live['phase'],'released');self.assertEqual(live['kind'],'renderer')
            busy=threading.Event()
            with self.observe_busy(busy):
                worker=self.background(self.deadline());self.assertTrue(busy.wait(1))
                # A second unchanged writer truncates the SAME inode before its
                # nonblocking flock skips. Metadata changes must remain legal.
                skipped=subprocess.run(['/usr/bin/bash',str(WRITER),'capture-both',target['address'],'0'],env=env,capture_output=True,timeout=1)
                self.assertEqual(skipped.returncode,0)
                permit.touch();stdout,stderr=writer.communicate(timeout=2)
                self.assertEqual((writer.returncode,stdout,stderr),(0,'',''))
                worker.join(timeout=2);self.assertFalse(worker.is_alive())
            self.assertEqual(self.errors,[]);self.assertEqual(len(list(self.preview.glob('0x*.png'))),6)
            self.assertFalse(self.batch.pending);self.assertIsNone(transport.process.poll())
            for path in self.preview.glob('0x*.png'):self.assertEqual(batch.png_dimensions(path.read_bytes(),complete=True),(80,50))
            self.assertTrue(self.batch._closed())
        finally:permit.touch()
    def test_partial_flocks_release_before_retry_and_new_receipt_remains_available(self):
        self.small();busy=threading.Event()
        with self.hold()as held,self.observe_busy(busy):
            worker=self.background(self.deadline());self.assertTrue(busy.wait(1))
            first=self.preview/(self.members[0]['address']+'.lock')
            with first.open('w')as independent:
                limit=time.monotonic()+.3
                while True:
                    try:fcntl.flock(independent,fcntl.LOCK_EX|fcntl.LOCK_NB);break
                    except BlockingIOError:
                        if time.monotonic()>limit:raise
                        time.sleep(.001)
                self.assertTrue(self.lock.acquire(timeout=.1));self.lock.release()
                fcntl.flock(independent,fcntl.LOCK_UN)
            fcntl.flock(held,fcntl.LOCK_UN);worker.join(timeout=2)
        self.assertEqual(self.errors,[]);self.assertFalse(self.batch.pending)
    def test_original_absolute_deadline_expires_during_busy_retry(self):
        self.small()
        with self.hold():
            began=time.monotonic()
            with self.assertRaisesRegex(TimeoutError,'original preview receipt deadline'):self.finish(self.deadline(.06))
        self.assertLess(time.monotonic()-began,.4);self.assert_no_publication();self.assertFalse(self.keeper.jobs)
    def test_already_expired_deadline_refuses_without_launch(self):
        self.small()
        with self.assertRaises(TimeoutError):self.finish(time.monotonic_ns()-1)
        self.assertFalse(self.keeper.jobs);self.assertEqual(len(self.batch.pending),3)
    def test_typed_deadline_rejects_bool_float_and_negative(self):
        self.small()
        for value in (True,1.5,-1):
            with self.subTest(value=value),self.assertRaises(ValueError):self.finish(value)
        self.assertFalse(self.keeper.jobs)
    def test_standalone_without_deadline_preserves_immediate_busy_refusal(self):
        self.small()
        with self.hold(),self.assertRaises(BlockingIOError):self.finish()
        self.assert_no_publication();self.assertFalse(self.keeper.jobs)
    def test_superseded_current_receipt_while_busy_never_launches(self):
        self.small();busy=threading.Event()
        with self.hold()as held,self.observe_busy(busy):
            worker=self.background(self.deadline());self.assertTrue(busy.wait(1))
            with self.lock:self.current=False
            fcntl.flock(held,fcntl.LOCK_UN);worker.join(timeout=2)
        self.assertEqual(len(self.errors),1);self.assertIsInstance(self.errors[0],ValueError)
        self.assert_no_publication();self.assertFalse(self.keeper.jobs)
    def test_replaced_busy_lock_inode_refuses_even_owned_regular_replacement(self):
        self.small();busy=threading.Event()
        with self.hold()as held,self.observe_busy(busy):
            worker=self.background(self.deadline());self.assertTrue(busy.wait(1))
            path=Path(held.name);path.rename(path.with_suffix('.old'));path.touch(mode=0o600)
            worker.join(timeout=2)
        self.assertEqual(len(self.errors),1);self.assertRegex(str(self.errors[0]),'inode changed')
        self.assert_no_publication();self.assertFalse(self.keeper.jobs)
    def test_symlink_lock_is_actual_kernel_refusal(self):
        self.small();self.preview.mkdir(mode=0o700)
        backing=self.root/'foreign';backing.touch(mode=0o600)
        (self.preview/(self.members[0]['address']+'.lock')).symlink_to(backing)
        with self.assertRaises(OSError)as error:self.finish(self.deadline())
        self.assertEqual(error.exception.errno,errno.ELOOP);self.assertFalse(self.keeper.jobs)
    def test_hardlink_lock_alias_refuses_before_helper(self):
        self.small();self.preview.mkdir(mode=0o700)
        first=self.preview/(self.members[0]['address']+'.lock');first.touch(mode=0o600)
        os.link(first,self.preview/(self.members[1]['address']+'.lock'))
        with self.assertRaisesRegex(ValueError,'aliases another address'):self.finish(self.deadline())
        self.assertFalse(self.keeper.jobs);self.assert_no_publication()
    def test_actual_kernel_unknown_flock_errno_does_not_retry(self):
        self.small();original=fcntl.flock;calls=[]
        def invalid(fd,flags):calls.append(fd);return original(fd,flags|128)
        with patch.object(batch.fcntl,'flock',invalid),self.assertRaises(OSError)as error:self.finish(self.deadline())
        self.assertEqual(error.exception.errno,errno.EINVAL);self.assertEqual(len(calls),1)
        self.assertFalse(self.keeper.jobs);self.assert_no_publication()
    def test_non_flock_eagain_does_not_enter_retry(self):
        self.small()
        with patch.object(self.batch,'_preview_lock_identity',side_effect=BlockingIOError(errno.EAGAIN,'injected metadata fault'))as injected,self.assertRaises(BlockingIOError):self.finish(self.deadline())
        self.assertEqual(injected.call_count,1);self.assertFalse(self.keeper.jobs)
    def test_receipt_lock_wait_uses_remaining_deadline_and_releases(self):
        self.small()
        with self.lock:
            worker=self.background(self.deadline(.06));worker.join(timeout=.3);self.assertFalse(worker.is_alive())
        self.assertEqual(len(self.errors),1);self.assertIsInstance(self.errors[0],TimeoutError)
        self.assertFalse(self.keeper.jobs);self.assert_no_publication()
    def test_actual_normal_helper_closure_after_expiry_does_not_publish(self):
        self.small();original=self.commands.run;deadline=self.deadline(.4)
        def late(argv,**options):
            self.assertEqual(options['timeout'],1)
            result=original(argv,**options)
            time.sleep(max(0,(deadline-time.monotonic_ns())/1000000000)+.01)
            return result
        with patch.object(self.commands,'run',late),self.assertRaises(TimeoutError):self.finish(deadline)
        self.assertTrue(any(any(r['phase']=='closed'and r['groupEmpty']for r in s['jobs'])for s in self.records))
        self.assertFalse(self.keeper.jobs);self.assertFalse(self.batch.quarantined);self.assert_no_publication()
    def test_actual_normal_helper_then_supersession_does_not_publish(self):
        self.small();original=self.commands.run
        def supersede(argv,**options):
            result=original(argv,**options)
            with self.lock:self.current=False
            return result
        with patch.object(self.commands,'run',supersede),self.assertRaisesRegex(ValueError,'superseded before preview publication'):self.finish(self.deadline())
        self.assertFalse(self.keeper.jobs);self.assert_no_publication()
    def test_deadline_between_actual_replacements_never_commits_pending(self):
        self.small();deadline=self.deadline(.4);original=Path.replace;replaced=[]
        def delayed(path,target):
            result=original(path,target)
            if Path(target).parent==self.preview and str(target).endswith('.png'):
                replaced.append(str(target))
                time.sleep(max(0,(deadline-time.monotonic_ns())/1000000000)+.01)
            return result
        with patch.object(Path,'replace',delayed),self.assertRaises(TimeoutError):self.finish(deadline)
        self.assertEqual(len(replaced),1);self.assertEqual(len(self.batch.pending),3)
        self.assertFalse(self.keeper.jobs);self.assertFalse(self.batch.quarantined)
    def test_actual_outstanding_same_actor_helper_quarantines_outputs_and_sources(self):
        self.small();original=self.commands.run;extra=[]
        def run(argv,**options):
            with SealedFile(self.executable)as sealed:
                launch=OwnedLaunch(['/proc/self/fd/'+str(sealed.fd)],env=self.env,keeper=self.keeper,kind='helper',actor=17,executable_fd=sealed.fd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,pass_fds=(sealed.fd,))
            extra.append(launch)
            self.assertEqual(json.loads(launch.process.stdout.readline())['event'],'outputs')
            return original(argv,**options)
        try:
            with patch.object(self.commands,'run',run),self.assertRaisesRegex(ValueError,'group closure unavailable'):self.finish(self.deadline())
            self.assertTrue(self.batch.quarantined);self.assertTrue(self.batch.retained_folder.is_dir())
            self.assertTrue(all(Path(s['path']).exists()for s in self.sources));self.assertTrue(self.keeper.jobs)
            with self.assertRaises(ValueError):self.batch.require_disposable()
        finally:
            for launch in extra:
                launch.process.stdin.write('{"command":"stop"}\n');launch.process.stdin.flush()
                self.assertEqual(launch.process.wait(timeout=2),0);launch.complete()
                for stream in (launch.process.stdin,launch.process.stdout,launch.process.stderr):stream.close()

class FirstSceneSeedDeadlineTests(unittest.TestCase):
    def test_actual_controller_expiry_after_finisher_before_seed(self):
        from scene_controller import SceneController
        from test_capture_lease import FileDesktop
        from test_scene_controller import Transport
        with tempfile.TemporaryDirectory()as root:
            desktop=FileDesktop(Path(root));transport=Transport();controller=SceneController(desktop,transport)
            original=transport.ensure_outputs
            def late(*args,**options):
                record=controller.current
                time.sleep(max(0,(record.profile['receivedNs']+2000000000-time.monotonic_ns())/1000000000)+.01)
                return original(*args,**options)
            transport.ensure_outputs=late
            desktop.finish_capture_previews=lambda *a,**kw:None
            try:
                window=desktop.windows[0];controller.request('minimize',window['address'],window['stableId'],window['pid'],context=1)
                limit=time.monotonic()+3
                while not(controller.history and len(desktop.removed)==3) and time.monotonic()<limit:time.sleep(.002)
                self.assertTrue(controller.history)
                self.assertEqual(controller.history[0].profile['failure'],'original scene receipt deadline before seed')
                self.assertFalse(any(row['command']=='seed'for row in transport.sent))
                self.assertEqual(len(desktop.removed),3)
            finally:controller.workers.shutdown(wait=True,cancel_futures=True)

if __name__=='__main__':unittest.main()
