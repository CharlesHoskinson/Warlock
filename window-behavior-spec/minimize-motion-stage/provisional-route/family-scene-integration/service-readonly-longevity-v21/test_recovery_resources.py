import hashlib
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import unittest
from recovery_resources import dispose_directory,retire_renderer,verify_process,checked_renderer
from helper_supervisor import Keeper
from owned_launch import OwnedLaunch
from native_runtime import PinnedExecutable

class ResourceTests(unittest.TestCase):
    def directory(self,raw):
        parent=Path(raw)/'actors';parent.mkdir(mode=0o700);actor=parent/('actor-1-'+'a'*32);actor.mkdir(mode=0o700)
        png=actor/'0123456789ab-1.png';png.write_bytes(b'exact');png.chmod(0o600)
        p=parent.stat();s=actor.stat();row=dict(path=str(actor),parentIdentity=[p.st_dev,p.st_ino],identity=[s.st_dev,s.st_ino]);return actor,row
    def test_no_disposal_until_old_lifetime_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            actor,row=self.directory(raw)
            for value in (False,1,None):
                with self.assertRaises(ValueError):dispose_directory(row,renderer_gone=value)
            self.assertTrue(actor.exists())
    def test_exact_complete_private_capture_namespace_can_dispose(self):
        with tempfile.TemporaryDirectory() as raw:
            actor,row=self.directory(raw);scratch=actor/'full-ab-17-0123456789ab-1.json.tmp';scratch.write_bytes(b'partial owned metadata');scratch.chmod(0o600)
            result=dispose_directory(row,renderer_gone=True);self.assertTrue(result['directoryGone']);self.assertEqual(result['captureFilesDeleted'],2)
    def test_replaced_directory_preserves_new_and_old_files(self):
        with tempfile.TemporaryDirectory() as raw:
            actor,row=self.directory(raw);old=actor.with_name('old');actor.rename(old);actor.mkdir(mode=0o700);(actor/'foreign').write_bytes(b'untouched')
            with self.assertRaisesRegex(ValueError,'identity'):dispose_directory(row,renderer_gone=True)
            self.assertEqual((actor/'foreign').read_bytes(),b'untouched');self.assertTrue((old/'0123456789ab-1.png').exists())
    def test_unknown_file_refuses_before_any_known_source_is_deleted(self):
        with tempfile.TemporaryDirectory() as raw:
            actor,row=self.directory(raw);unknown=actor/'arbitrary.png';unknown.write_bytes(b'foreign');unknown.chmod(0o600)
            with self.assertRaisesRegex(ValueError,'unexpected actor material'):dispose_directory(row,renderer_gone=True)
            self.assertEqual(unknown.read_bytes(),b'foreign');self.assertTrue((actor/'0123456789ab-1.png').exists())
    def test_allocation_gap_never_infers_ownership_from_name(self):
        with tempfile.TemporaryDirectory() as raw:
            actor,row=self.directory(raw);row['identity']=None
            with self.assertRaisesRegex(ValueError,'allocation gap'):dispose_directory(row,renderer_gone=True)
            self.assertTrue(actor.exists())
    def test_symlink_capture_is_never_followed_or_deleted(self):
        with tempfile.TemporaryDirectory() as raw:
            actor,row=self.directory(raw);outside=Path(raw)/'foreign';outside.write_bytes(b'untouched');(actor/'full-ab-17.png').symlink_to(outside)
            with self.assertRaises(ValueError):dispose_directory(row,renderer_gone=True)
            self.assertEqual(outside.read_bytes(),b'untouched');self.assertTrue((actor/'0123456789ab-1.png').exists())
    def test_boolean_inode_refuses(self):
        with tempfile.TemporaryDirectory() as raw:
            actor,row=self.directory(raw);row['identity'][1]=True
            with self.assertRaises(ValueError):dispose_directory(row,renderer_gone=True)
            self.assertTrue(actor.exists())
    def launched(self,root):
        env=dict(os.environ,XDG_RUNTIME_DIR=str(root),HYPRLAND_INSTANCE_SIGNATURE='offline',WAYLAND_DISPLAY='never-connect');keeper=Keeper(root,env,lambda body:None)
        executable=root/'cat';shutil.copyfile('/usr/bin/cat',executable);executable.chmod(0o500)
        with PinnedExecutable(executable,hashlib.sha256(executable.read_bytes()).hexdigest()) as selected:
            launch=OwnedLaunch([selected.path],env=env,keeper=keeper,kind='renderer',actor=1,executable_fd=selected.fd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        return keeper,launch,env
    def cleanup(self,keeper,launch):
        if launch.process.poll() is None:launch.process.terminate();launch.process.wait(timeout=2)
        if launch.job in keeper.jobs:launch.complete()
        keeper.stop()
        for stream in (launch.process.stdin,launch.process.stdout,launch.process.stderr):stream.close()
    def test_actual_live_renderer_material_and_typed_roles(self):
        with tempfile.TemporaryDirectory() as raw:
            keeper,launch,env=self.launched(Path(raw))
            try:
                launch.process.stdin.write('actual CPU producer\n');launch.process.stdin.flush();self.assertEqual(launch.process.stdout.readline(),'actual CPU producer\n')
                self.assertEqual(verify_process(launch.ownership),'executed');checked_renderer(launch.ownership)
                row=dict(launch.ownership,pid=True)
                with self.assertRaises(ValueError):checked_renderer(row)
            finally:self.cleanup(keeper,launch)
    def test_exact_pidfd_retirement_never_signals_reused_identity(self):
        with tempfile.TemporaryDirectory() as raw:
            keeper,launch,env=self.launched(Path(raw))
            try:
                reused=dict(launch.ownership,start=launch.ownership['start']+1)
                result=retire_renderer(reused,expected_environment=launch.ownership['environment']);self.assertTrue(result['oldLifetimeGone']);self.assertFalse(result['signaled']);self.assertIsNone(launch.process.poll())
            finally:self.cleanup(keeper,launch)
    def test_exited_unreaped_direct_lifetime_is_gone_without_material_read(self):
        with tempfile.TemporaryDirectory() as raw:
            keeper,launch,env=self.launched(Path(raw))
            try:
                launch.process.terminate()
                import select
                fd=os.pidfd_open(launch.process.pid)
                try:poll=select.poll();poll.register(fd,select.POLLIN);self.assertTrue(poll.poll(2000))
                finally:os.close(fd)
                result=retire_renderer(launch.ownership,expected_environment=launch.ownership['environment']);self.assertTrue(result['oldLifetimeGone']);self.assertFalse(result['signaled'])
            finally:self.cleanup(keeper,launch)

if __name__=='__main__':unittest.main()
