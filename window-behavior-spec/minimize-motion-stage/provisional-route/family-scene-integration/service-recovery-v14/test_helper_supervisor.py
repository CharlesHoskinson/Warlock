from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import unittest
from helper_supervisor import Keeper,read_terminal
from owned_launch import OwnedLaunch
from native_runtime import PinnedExecutable

class SupervisorTests(unittest.TestCase):
    def env(self,root):return dict(os.environ,XDG_RUNTIME_DIR=str(root),HYPRLAND_INSTANCE_SIGNATURE='offline',WAYLAND_DISPLAY='never-connect')
    def pinned(self,root):
        path=root/'cat';shutil.copyfile('/usr/bin/cat',path);path.chmod(0o500)
        return PinnedExecutable(path,hashlib.sha256(path.read_bytes()).hexdigest())
    def test_durable_registration_precedes_exec_and_normal_completion(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);snapshots=[];keeper=Keeper(root,self.env(root),lambda body:snapshots.append(deepcopy(body)))
            try:
                with self.pinned(root) as selected:
                    launch=OwnedLaunch(['cat'],env=self.env(root),keeper=keeper,kind='cpu-test',executable_fd=selected.fd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                    out,err=launch.process.communicate('actual CPU\n',timeout=2);self.assertEqual(out,'actual CPU\n');self.assertEqual(launch.process.returncode,0,err)
                    launch.complete()
                self.assertTrue(any(any(j['phase']=='gated' for j in row['jobs']) for row in snapshots))
                self.assertTrue(any(any(j['phase']=='released' for j in row['jobs']) for row in snapshots))
                keeper.stop();terminal=keeper.read_terminal();self.assertTrue(terminal['normalStop']);self.assertTrue(terminal['jobs'][0]['normalCompletion'])
            finally:
                if not keeper.closed:
                    keeper.detach();keeper.process.wait(timeout=5);keeper.process.stderr.close()
    def test_gate_refuses_exec_when_durable_job_write_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw)
            def writer(body):
                if body['jobs']:raise OSError('actual journal fsync fault')
            keeper=Keeper(root,self.env(root),writer)
            try:
                with self.pinned(root) as selected:
                    with self.assertRaisesRegex(OSError,'fsync fault'):OwnedLaunch(['cat'],env=self.env(root),keeper=keeper,kind='cpu-test',executable_fd=selected.fd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                keeper.detach();keeper.process.wait(timeout=5)
                self.assertEqual(keeper.process.returncode,0,keeper.process.stderr.read());terminal=read_terminal(keeper.ownership)
                self.assertTrue(terminal['allGroupsEmpty']);self.assertFalse(terminal['normalStop'])
            finally:
                if keeper.process.poll() is None:keeper.detach();keeper.process.wait(timeout=5)
                keeper.process.stderr.close()
    def test_control_eof_retires_exact_running_job(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);keeper=Keeper(root,self.env(root),lambda body:None)
            with self.pinned(root) as selected:
                launch=OwnedLaunch(['cat'],env=self.env(root),keeper=keeper,kind='cpu-test',executable_fd=selected.fd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                keeper.detach();launch.process.wait(timeout=3);keeper.process.wait(timeout=5)
                self.assertEqual(launch.process.returncode,-signal.SIGTERM)
                self.assertEqual(keeper.process.returncode,0,keeper.process.stderr.read());terminal=read_terminal(keeper.ownership)
                self.assertFalse(terminal['normalStop']);self.assertTrue(terminal['allGroupsEmpty']);self.assertEqual(terminal['jobs'][0]['job'],launch.job)
            finally:
                if launch.process.poll() is None:launch.process.kill();launch.process.wait()
                if keeper.process.poll() is None:keeper.process.kill();keeper.process.wait()
                for stream in (launch.process.stdin,launch.process.stdout,launch.process.stderr,keeper.process.stderr):stream.close()
    def test_replaced_terminal_root_refuses(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw)/'owned';root.mkdir(mode=0o700);keeper=Keeper(root,self.env(root),lambda body:None);keeper.stop()
            root.rename(root.with_name('old'));root.mkdir(mode=0o700)
            with self.assertRaisesRegex(ValueError,'root changed'):read_terminal(keeper.ownership)

if __name__=='__main__':unittest.main()
