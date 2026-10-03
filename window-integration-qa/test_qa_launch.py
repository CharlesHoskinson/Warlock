import os
from pathlib import Path
import resource
import socket
import tempfile
import unittest
from unittest.mock import patch
import qa_launch as qa


class LaunchContract(unittest.TestCase):
    def test_unscoped_execution_rejected(self):
        with patch.object(Path, 'read_text', return_value='0::/user.slice/app.scope\n'):
            with self.assertRaises(RuntimeError): qa.require_qa_scope()

    def test_core_zero_does_not_satisfy_contract(self):
        with patch.object(Path, 'read_text', return_value='0::/user.slice/qa-harness.slice/qa-harness-test.scope\n'), patch.object(resource, 'getrlimit', return_value=(0, 0)), patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError): qa.require_qa_scope()

    def test_exact_one_required(self):
        with patch.object(Path, 'read_text', return_value='0::/user.slice/qa-harness.slice/qa-harness-test.scope\n'), patch.object(resource, 'getrlimit', return_value=(1, 1)), patch.dict(os.environ, {}, clear=True):
            self.assertEqual(qa.require_qa_scope()['coreLimit'], 1)

    def test_infinity_only_explicit_diagnostic(self):
        with patch.object(Path, 'read_text', return_value='0::/user.slice/qa-harness.slice/qa-harness-test.scope\n'), patch.object(resource, 'getrlimit', return_value=(resource.RLIM_INFINITY, resource.RLIM_INFINITY)), patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError): qa.require_qa_scope()
            os.environ['WINDOW_QA_BACKTRACE'] = '1'
            self.assertEqual(qa.require_qa_scope()['coreLimit'], 'infinity')

    def test_live_socket_returns_real_peer(self):
        with tempfile.TemporaryDirectory() as directory, socket.socket(socket.AF_UNIX) as server:
            server.bind(directory + '/wayland-test'); server.listen(1)
            row = qa.verify_parent({'XDG_RUNTIME_DIR': directory, 'WAYLAND_DISPLAY': 'wayland-test'})
            self.assertEqual(row['pid'], os.getpid())
            self.assertEqual(row['uid'], os.getuid())
            self.assertEqual(row['path'], directory + '/wayland-test')

    def test_missing_explicit_parent_rejected(self):
        for env in ({}, {'XDG_RUNTIME_DIR': '/tmp'}, {'WAYLAND_DISPLAY': 'wayland-1'}, {'XDG_RUNTIME_DIR': '/tmp', 'WAYLAND_DISPLAY': 'a', 'WAYLAND_SOCKET': '3'}):
            with self.assertRaises(RuntimeError): qa.verify_parent(env)

    def test_dead_socket_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            server = socket.socket(socket.AF_UNIX);server.bind(directory + '/dead');server.close()
            with self.assertRaises(OSError): qa.verify_parent({'XDG_RUNTIME_DIR': directory, 'WAYLAND_DISPLAY': 'dead'})

    def test_regular_file_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory, socket.socket(socket.AF_UNIX) as server:
            server.bind(directory + '/server');server.listen(1)
            Path(directory + '/regular').touch();Path(directory + '/link').symlink_to('server')
            for name in ('regular','link'):
                with self.assertRaises(RuntimeError): qa.verify_parent({'XDG_RUNTIME_DIR': directory, 'WAYLAND_DISPLAY': name})

    def test_replaced_socket_rejected(self):
        with tempfile.TemporaryDirectory() as directory, socket.socket(socket.AF_UNIX) as server:
            server.bind(directory + '/server');server.listen(1)
            real = Path.lstat;count = 0
            def changed(path):
                nonlocal count
                value = real(path);count += 1
                if count == 2:
                    fields = list(value);fields[1] += 1;return os.stat_result(fields)
                return value
            with patch.object(Path, 'lstat', changed):
                with self.assertRaises(RuntimeError): qa.verify_parent({'XDG_RUNTIME_DIR': directory, 'WAYLAND_DISPLAY': 'server'})

    def test_private_directory_mode_and_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory);qa.check_private_directory(path)
            path.chmod(0o755)
            with self.assertRaises(RuntimeError): qa.check_private_directory(path)
            path.chmod(0o700);link=path/'link';link.symlink_to(path)
            with self.assertRaises(RuntimeError): qa.check_private_directory(link)

    def test_nested_env_explicit_wayland_no_drm(self):
        with tempfile.TemporaryDirectory() as directory, socket.socket(socket.AF_UNIX) as server:
            server.bind(directory + '/parent');server.listen(1)
            env={'XDG_RUNTIME_DIR': directory,'WAYLAND_DISPLAY':'parent','AQ_BACKENDS':'drm','AQ_DRM_DEVICES':'/dev/dri/card0','DISPLAY':':0','HYPRLAND_INSTANCE_SIGNATURE':'main'}
            with patch.object(qa,'require_qa_scope'),patch.object(qa,'verify_runtime',return_value=Path('/private')):
                child,identity=qa.nested_env(env,'/private')
            self.assertEqual(child['AQ_BACKENDS'],'wayland')
            self.assertEqual(child['WAYLAND_DISPLAY'],identity['path'])
            self.assertEqual(child['XDG_RUNTIME_DIR'],'/private')
            for key in ('AQ_DRM_DEVICES','DISPLAY','HYPRLAND_INSTANCE_SIGNATURE'):self.assertNotIn(key,child)

    def test_short_runtime_socket_budget(self):
        signature='efb50993780079460b0cbed1363e2166a2de1d9f_1790777558_556595558'
        path='/run/user/'+str(os.getuid())+'/wqa/abcd/hypr/'+signature+'/.socket2.sock'
        self.assertLessEqual(len(path.encode()),107)

    def test_runtime_allocation_skips_existing_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'aaaa').mkdir(mode=0o700)
            with patch.object(qa,'require_qa_scope'),patch.object(qa,'runtime_base',return_value=base),patch.object(qa.secrets,'token_hex',side_effect=['aaaa','bbbb']):
                result=qa.private_runtime()
            self.assertEqual(result,base/'bbbb')
            self.assertEqual(result.stat().st_mode & 0o777,0o700)


if __name__ == '__main__': unittest.main()
