#!/usr/bin/env python3
"""Installed daemon socket tests; this is backend recovery, not desktop hotplug."""
import importlib.machinery
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import unittest

HELPER = Path(os.getenv('ATTENTION_HELPER', str(Path.home() / '.local/bin/hypr-taskbar-attention')))
attention = importlib.machinery.SourceFileLoader('attention_recovery', str(HELPER)).load_module()


def wait(predicate, label, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(.02)
    raise AssertionError(label)


class Recovery(unittest.TestCase):
    def test_installed_daemon_uses_own_socket_and_clears_on_eof(self):
        with tempfile.TemporaryDirectory(prefix='attention-recovery-') as directory:
            root = Path(directory)
            sockets = []
            for name in ('main', 'newer-nested'):
                path = root / 'hypr' / name / '.socket2.sock'
                path.parent.mkdir(parents=True)
                server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                server.bind(str(path)); server.listen(); server.settimeout(5)
                sockets.append(server)
            self.assertEqual(attention.event_socket_path(root, 'main'), root/'hypr/main/.socket2.sock')
            self.assertEqual(attention.event_socket_path(root, 'absent'), root/'hypr/absent/.socket2.sock')
            window = {'address':'0x123', 'pid':42, 'stableId':'window-original'}
            (root/'clients.json').write_text(json.dumps([window]))
            binary = root/'bin'; binary.mkdir()
            ctl = binary/'hyprctl'
            ctl.write_text('#!/usr/bin/env python3\nimport os,pathlib,sys\nr=pathlib.Path(os.environ["XDG_RUNTIME_DIR"])\nprint((r/"clients.json").read_text() if sys.argv[1]=="clients" else "{}")\n')
            ctl.chmod(0o755)
            env = dict(os.environ, XDG_RUNTIME_DIR=str(root), HYPRLAND_INSTANCE_SIGNATURE='main', PATH=str(binary)+':'+os.environ['PATH'])
            process = subprocess.Popen([str(HELPER)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            state_path = root/'hypr-taskbar-attention.json'
            def state():
                try: return json.loads(state_path.read_text())
                except (OSError, ValueError): return None
            try:
                stream, _ = sockets[0].accept()
                stream.sendall(b'urgent>>123\n')
                wait(lambda: state() == {'0x123':{'pid':42,'stableId':'window-original'}}, 'main urgency')
                sockets[1].setblocking(False)
                with self.assertRaises(BlockingIOError): sockets[1].accept()
                stream.close()
                wait(lambda: state() == {}, 'EOF clears old urgency')
                stream, _ = sockets[0].accept()
                window['pid'] = 43; window['stableId'] = 'window-replacement'
                (root/'clients.json').write_text(json.dumps([window]))
                stream.sendall(b'urgent>>123\n')
                wait(lambda: state() == {'0x123':{'pid':43,'stableId':'window-replacement'}}, 'reconnect uses fresh identity')
                stream.sendall(b'activewindowv2>>123\n')
                wait(lambda: state() == {}, 'focus clears recovered urgency')
                stream.close()
            finally:
                process.terminate(); process.wait(timeout=5)
                for server in sockets: server.close()
                error = process.stderr.read()
                process.stdout.close(); process.stderr.close()
                self.assertEqual(error, '')


if __name__ == '__main__':
    unittest.main()
