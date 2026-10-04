"""Fake Unix peers and real inotify/CLI: no live GUI/compositor access."""
import io
import json
import os
from pathlib import Path
import socket
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import taskbar_watch as watch


def wait_for(predicate, timeout=3):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError('Timed out waiting for observation')


class WatchHarness:
    def __init__(self, root, provider=None, reconcile=10, files=None):
        self.root = root
        self.directory = root / 'hypr/selected'
        self.directory.mkdir(parents=True)
        self.path = self.directory / '.socket2.sock'
        self.server = self.make_server()
        self.input_read, self.input_write = os.pipe()
        self.stopped = threading.Event()
        self.calls = []
        self.output = io.StringIO()
        self.error = None
        self.local = root / 'taskbar-settings.json'
        self.preview = root / 'previews'
        self.preview.mkdir()
        self.provider = provider or self.snapshot
        self.paths = ([self.local], [self.preview]) if files is None else files
        self.reconcile = reconcile
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.server.settimeout(3)
        self.peer, _ = self.server.accept()

    def make_server(self):
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(self.path))
        server.listen()
        return server

    def snapshot(self):
        self.calls.append(time.monotonic())
        return dict(groups=[], snapGroups=[], monitors=[], focusedAddress='',
                    settings={}, reducedMotion=False)

    def run(self):
        try:
            watch.observe(lambda: self.provider(), self.paths, runtime=self.root,
                          instance='selected', input_fd=self.input_read, output=self.output,
                          reconcile=self.reconcile, retry=.05, coalesce=.06,
                          should_stop=self.stopped.is_set)
        except BaseException as error:
            self.error = error

    def rows(self):
        return [json.loads(row) for row in self.output.getvalue().splitlines()]

    def close(self):
        self.stopped.set()
        self.thread.join(3)
        self.peer.close()
        self.server.close()
        os.close(self.input_read)
        os.close(self.input_write)
        if self.thread.is_alive():
            raise AssertionError('Observer failed to stop')


class ObserveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.harness = None

    def tearDown(self):
        if self.harness:
            self.harness.close()
        self.temp.cleanup()

    def start(self, **kwargs):
        self.harness = WatchHarness(self.root, **kwargs)
        wait_for(lambda: len(self.harness.rows()) >= 1 or self.harness.error)
        self.assertIsNone(self.harness.error)
        return self.harness

    def test_initial_and_idle_do_not_query_continuously(self):
        h = self.start()
        time.sleep(.35)
        self.assertEqual(len(h.calls), 1)
        row = h.rows()[0]
        self.assertEqual(row['protocolVersion'], 1)
        self.assertEqual(row['sequence'], 1)
        self.assertRegex(row['epoch'], r'^[0-9a-f]{32}$')
        self.assertEqual(row['groups'], [])

    def test_burst_coalesces_and_fragmented_event_waits_for_newline(self):
        h = self.start()
        h.peer.sendall(b'activewindow>>part')
        time.sleep(.12)
        self.assertEqual(len(h.calls), 1)
        h.peer.sendall(b'ial\n' + b'openwindow>>abc\n' * 50)
        wait_for(lambda: len(h.calls) == 2)
        time.sleep(.12)
        self.assertEqual(len(h.calls), 2)
        self.assertEqual([row['sequence'] for row in h.rows()], [1, 2])

    def test_stdin_refresh_coalesces_and_eof_exits(self):
        h = self.start()
        os.write(h.input_write, b'refresh\n' * 20)
        wait_for(lambda: len(h.calls) == 2)
        os.close(h.input_write)
        h.input_write = os.open('/dev/null', os.O_RDONLY)
        h.thread.join(2)
        self.assertFalse(h.thread.is_alive())
        self.assertIsNone(h.error)

    def test_invalid_control_terminates_and_closes_peer(self):
        h = self.start()
        os.write(h.input_write, b'activate 0xabc\n')
        h.thread.join(2)
        self.assertIsInstance(h.error, ValueError)
        h.peer.settimeout(1)
        self.assertEqual(h.peer.recv(1), b'')
        self.assertEqual(len(h.calls), 1)

    def test_local_files_are_timely_and_session_order_is_ignored(self):
        h = self.start()
        (self.root / 'taskbar-session-order.json').write_text('{}')
        time.sleep(.12)
        self.assertEqual(len(h.calls), 1)
        h.local.write_text('{}')
        wait_for(lambda: len(h.calls) == 2)
        (h.preview / '0xabc-0.png').write_bytes(b'pixels')
        wait_for(lambda: len(h.calls) == 3)

    def test_production_snap_list_selfrewrite_does_not_trigger_refresh_loop(self):
        snap = self.root / 'snap'
        snap.mkdir()
        finalized = snap / 'state.json'
        body = {'version': 1, 'groups': [], 'snapped': {}, 'next_id': 0}
        finalized.write_text(json.dumps(body))
        observations = []

        def provider():
            observations.append(time.monotonic())
            temporary = snap / 'state.tmp'
            temporary.write_text(finalized.read_text())
            temporary.replace(finalized)
            return dict(groups=[], focusedAddress='', snapGroups=[], settings={},
                        monitors=[], reducedMotion=False)

        h = self.start(provider=provider, files=([finalized], [], [finalized]))
        time.sleep(.4)
        self.assertEqual(len(observations), 1)
        external = snap / 'state.tmp'
        body['next_id'] = 1
        external.write_text(json.dumps(body))
        external.replace(finalized)
        wait_for(lambda: len(h.rows()) == 2)
        time.sleep(.3)
        self.assertEqual(len(observations), 2)
        self.assertEqual(len(h.rows()), 2)

    def test_external_snap_change_during_snapshot_is_not_swallowed(self):
        snap = self.root / 'snap'
        snap.mkdir()
        finalized = snap / 'state.json'
        finalized.write_text('{"generation":0}')
        first_started, external_done = threading.Event(), threading.Event()
        observations = []

        def provider():
            observations.append(finalized.read_text())
            temporary = snap / 'state.tmp'
            temporary.write_text(observations[-1])
            temporary.replace(finalized)
            if len(observations) == 1:
                first_started.set()
                if not external_done.wait(2):
                    raise AssertionError('External edit did not arrive')
            return dict(groups=[], focusedAddress='', snapGroups=[], settings={},
                        monitors=[], reducedMotion=False)

        def external():
            if not first_started.wait(2):
                return
            finalized.write_text('{"generation":1}')
            external_done.set()

        editor = threading.Thread(target=external)
        editor.start()
        h = self.start(provider=provider, files=([finalized], [], [finalized]))
        editor.join(2)
        wait_for(lambda: len(h.rows()) == 2)
        self.assertEqual(observations, ['{"generation":0}', '{"generation":1}'])
        time.sleep(.15)
        self.assertEqual(len(h.rows()), 2)

    def test_content_equal_snap_mode_change_is_still_dirty(self):
        snap = self.root / 'state.json'
        snap.write_text('{}')
        h = self.start(files=([snap], [], [snap]))
        snap.chmod(0o600)
        wait_for(lambda: len(h.rows()) == 2)

    def test_temporary_snap_writes_and_lock_files_are_ignored(self):
        snap = self.root / 'state.json'
        snap.write_text('{}')
        h = self.start(files=([snap], [], [snap]))
        (self.root / 'state.tmp').write_text('{"not-final":true}')
        (self.root / 'snap.lock').write_text('lock')
        time.sleep(.2)
        self.assertEqual(len(h.rows()), 1)

    def test_directory_created_after_start_is_discovered(self):
        file = self.root / 'new/deeper/settings.json'
        h = self.start(files=([file], []))
        file.parent.mkdir(parents=True)
        wait_for(lambda: len(h.calls) >= 2)
        before = len(h.calls)
        file.write_text('{}')
        wait_for(lambda: len(h.calls) > before)

    def test_replaced_directory_gets_new_watch(self):
        directory = self.root / 'config'
        directory.mkdir()
        file = directory / 'settings.json'
        h = self.start(files=([file], []))
        directory.rename(self.root / 'old-config')
        directory.mkdir()
        # Observer checks socket lifetime every quarter second; a manual
        # refresh wakes it up and lets it rebuild local directory watches.
        os.write(h.input_write, b'refresh\n')
        wait_for(lambda: len(h.calls) >= 2)
        before = len(h.calls)
        file.write_text('{}')
        wait_for(lambda: len(h.calls) > before)

    def test_moved_out_exact_file_and_catalog_entry_are_dirty(self):
        h = self.start()
        h.local.write_text('{}')
        wait_for(lambda: len(h.calls) == 2)
        h.local.rename(self.root / 'settings-moved-away.json')
        wait_for(lambda: len(h.calls) == 3)
        entry = h.preview / 'example.desktop'
        entry.write_text('[Desktop Entry]')
        wait_for(lambda: len(h.calls) == 4)
        entry.rename(self.root / 'example.desktop')
        wait_for(lambda: len(h.calls) == 5)

    def test_file_permission_changes_are_dirty(self):
        h = self.start()
        h.local.write_text('{}')
        wait_for(lambda: len(h.calls) == 2)
        h.local.chmod(0o600)
        wait_for(lambda: len(h.calls) == 3)

    def test_reconciliation_refreshes_missing_event_fields(self):
        h = self.start(reconcile=.18)
        wait_for(lambda: len(h.calls) >= 3)
        self.assertGreaterEqual(h.calls[1] - h.calls[0], .15)

    def test_disconnect_preserves_epoch_without_stale_output(self):
        h = self.start()
        old = h.rows()[0]['epoch']
        h.peer.close()
        h.server.settimeout(2)
        h.peer, _ = h.server.accept()
        wait_for(lambda: len(h.rows()) == 2)
        self.assertEqual(h.rows()[1]['epoch'], old)
        self.assertEqual(h.rows()[1]['sequence'], 2)

    def test_socket_replacement_reconnects_selected_path(self):
        h = self.start()
        old = h.rows()[0]['epoch']
        h.server.close()
        h.path.unlink()
        h.server = h.make_server()
        h.peer.close()
        h.server.settimeout(2)
        h.peer, _ = h.server.accept()
        wait_for(lambda: len(h.rows()) == 2)
        self.assertEqual(old, h.rows()[1]['epoch'])

    def test_snapshot_rejects_lifetime_replacement_during_query(self):
        h = self.start()
        def replaced():
            h.path.unlink()
            return h.snapshot()
        h.provider = replaced
        os.write(h.input_write, b'refresh\n')
        wait_for(lambda: len(h.calls) == 2)
        time.sleep(.15)
        self.assertEqual(len(h.rows()), 1)

    def test_snapshot_failure_emits_no_partial_json(self):
        h = self.start()
        h.provider = lambda: (_ for _ in ()).throw(ValueError('malformed observation'))
        os.write(h.input_write, b'refresh\n')
        time.sleep(.2)
        self.assertEqual(len(h.rows()), 1)
        self.assertIsInstance(h.error, ValueError)

    def test_snapshot_output_bound_emits_no_partial_json(self):
        h = self.start()
        h.provider = lambda: {'large': 'x' * (watch.MAX_SNAPSHOT_BYTES + 1)}
        os.write(h.input_write, b'refresh\n')
        h.thread.join(2)
        self.assertIsInstance(h.error, ValueError)
        self.assertEqual(len(h.rows()), 1)

    def test_snapshot_nonfinite_json_is_rejected(self):
        h = self.start()
        h.provider = lambda: {'progress': float('nan')}
        os.write(h.input_write, b'refresh\n')
        h.thread.join(2)
        self.assertIsInstance(h.error, ValueError)
        self.assertEqual(len(h.rows()), 1)

    def test_shutdown_closes_event_subscription(self):
        h = self.start()
        h.stopped.set()
        h.thread.join(2)
        h.peer.settimeout(1)
        self.assertEqual(h.peer.recv(1), b'')


class BoundsTests(unittest.TestCase):
    def test_production_paths_watch_finalized_snap_state_only(self):
        home = Path('/test-home')
        with patch.dict(os.environ, {'XDG_RUNTIME_DIR': '/test-runtime', 'HYPR_SNAP_STATE_DIR': '/test-snap'}):
            files, trees, filtered = watch.watched_paths(home, home / 'config', home / 'data')
        self.assertIn(Path('/test-snap/state.json'), files)
        self.assertEqual(filtered, [Path('/test-snap/state.json')])
        self.assertNotIn(Path('/test-snap'), trees)
        self.assertNotIn(Path('/test-snap/state.tmp'), files)

    def test_oversize_and_invalid_json_use_inode_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'state.json'
            for raw in (b'not-json', b'x' * (watch.MAX_SNAPSHOT_BYTES + 1)):
                file.write_bytes(raw)
                first = watch.FileChanges.content_signature(file)
                self.assertEqual(first[0], 'metadata')
                temporary = file.with_suffix('.tmp')
                temporary.write_bytes(raw)
                temporary.replace(file)
                self.assertNotEqual(first, watch.FileChanges.content_signature(file))

    def test_unreadable_content_falls_back_without_hiding_metadata_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'state.json'
            file.write_text('{}')
            with patch.object(watch.os, 'open', side_effect=PermissionError('denied')):
                first = watch.FileChanges.content_signature(file)
                self.assertEqual(first[0], 'metadata')
                file.chmod(0o600)
                self.assertNotEqual(first, watch.FileChanges.content_signature(file))

    def test_control_bound_and_unknown_commands(self):
        for value in (b'x' * 65, b'launch\n', b'refresh\r\n'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    watch.ControlLines().feed(value)

    def test_control_fragmentation(self):
        parser = watch.ControlLines()
        self.assertFalse(parser.feed(b'refre'))
        self.assertTrue(parser.feed(b'sh\nrefresh\n'))

    def test_signature_cannot_escape_selected_runtime(self):
        for value in ('', '../other', 'one/two', None):
            with self.assertRaises(ValueError):
                watch.EventConnection('/tmp', value)

    def test_endpoint_rejects_regular_file_and_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            directory = root / 'hypr/selected'
            directory.mkdir(parents=True)
            path = directory / '.socket2.sock'
            path.write_text('not a socket')
            conn = watch.EventConnection(root, 'selected')
            with self.assertRaises(ValueError):
                conn.connect()
            path.unlink()
            server = socket.socket(socket.AF_UNIX)
            try:
                target = root / 'real.sock'
                server.bind(str(target))
                path.symlink_to(target)
                with self.assertRaises(ValueError):
                    conn.connect()
            finally:
                server.close()

    def test_event_buffer_bound(self):
        conn = watch.EventConnection('/tmp', 'selected')
        a, b = socket.socketpair()
        try:
            conn.sock = a
            conn.buffer = b'x' * watch.MAX_EVENT_BUFFER
            b.sendall(b'x')
            with self.assertRaises(ValueError):
                conn.read()
        finally:
            conn.close()
            b.close()

    def test_new_peer_lifetime_is_not_adopted(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            directory = root / 'hypr/selected'
            directory.mkdir(parents=True)
            server = socket.socket(socket.AF_UNIX)
            server.bind(str(directory / '.socket2.sock'))
            server.listen()
            conn = watch.EventConnection(root, 'selected')
            conn.selected_peer = (os.getpid(), 'wrong-start-time')
            try:
                with self.assertRaises(watch.SessionEnded):
                    conn.connect()
                self.assertIsNone(conn.sock)
            finally:
                conn.close()
                server.close()

    def test_missing_endpoint_has_bounded_retry(self):
        with tempfile.TemporaryDirectory() as folder:
            read, write = os.pipe()
            try:
                start = time.monotonic()
                with self.assertRaises(watch.SessionEnded):
                    watch.observe(lambda: {}, ([], []), runtime=folder, instance='selected',
                                  input_fd=read, output=io.StringIO(), retry=.02,
                                  reconnect_timeout=.08, should_stop=lambda: False)
                self.assertLess(time.monotonic() - start, .5)
            finally:
                os.close(read)
                os.close(write)


class LegacyCliTests(unittest.TestCase):
    def test_sigterm_during_readonly_query_reaps_child_and_exits(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            stub = home / '.local/share/hypr-window-controls'
            stub.mkdir(parents=True)
            (stub / 'window_state.py').write_text('def desktop_owner(w): return (1, False)\ndef monitor_owner(w,m,s): return 0\n')
            bindir = home / 'bin'
            bindir.mkdir()
            ctl = bindir / 'hyprctl'
            marker = home / 'query-pid'
            ctl.write_text('#!/usr/bin/python3\nimport os,time\nfrom pathlib import Path\nPath(os.environ["QUERY_PID"]).write_text(str(os.getpid()))\ntime.sleep(30)\nprint("[]")\n')
            ctl.chmod(0o755)
            directory = home / 'runtime/hypr/selected'
            directory.mkdir(parents=True)
            server = socket.socket(socket.AF_UNIX)
            server.bind(str(directory / '.socket2.sock'))
            server.listen()
            server.settimeout(3)
            env = dict(os.environ, HOME=str(home), XDG_DATA_HOME=str(home / '.local/share'),
                       XDG_DATA_DIRS=str(home / 'system'), XDG_CACHE_HOME=str(home / '.cache'),
                       XDG_RUNTIME_DIR=str(home / 'runtime'), HYPRLAND_INSTANCE_SIGNATURE='selected',
                       QUERY_PID=str(marker), PATH=str(bindir) + ':' + os.environ['PATH'])
            child = subprocess.Popen([sys.executable, str(BASE / 'hypr-taskbar'), 'observe'],
                                     env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            peer = None
            try:
                peer, _ = server.accept()
                wait_for(marker.exists)
                pid = int(marker.read_text())
                child.send_signal(signal.SIGTERM)
                stdout, stderr = child.communicate(timeout=2)
                self.assertEqual(child.returncode, 0, stderr.decode())
                self.assertEqual(stdout, b'')
                wait_for(lambda: not Path('/proc', str(pid)).exists())
            finally:
                if child.poll() is None:
                    child.kill()
                    child.communicate()
                if peer:
                    peer.close()
                server.close()

    def test_one_shot_snapshot_keeps_legacy_shape_and_fresh_queries(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            stub = home / '.local/share/hypr-window-controls'
            stub.mkdir(parents=True)
            (stub / 'window_state.py').write_text('def desktop_owner(w): return (1, False)\ndef monitor_owner(w,m,s): return 0\n')
            bindir = home / 'bin'
            bindir.mkdir()
            ctl = bindir / 'hyprctl'
            ctl.write_text('#!/usr/bin/python3\nimport sys\nprint("[]")\n')
            ctl.chmod(0o755)
            env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'),
                       XDG_DATA_HOME=str(home / '.local/share'), XDG_DATA_DIRS=str(home / 'system'),
                       XDG_CACHE_HOME=str(home / '.cache'), XDG_RUNTIME_DIR=str(home / 'runtime'),
                       PATH=str(bindir) + ':' + os.environ['PATH'])
            result = subprocess.run([sys.executable, str(BASE / 'hypr-taskbar'), 'snapshot'],
                                    env=env, capture_output=True, text=True, check=True, timeout=5)
            row = json.loads(result.stdout)
            self.assertEqual(set(row), {'groups', 'focusedAddress', 'snapGroups', 'settings', 'monitors', 'reducedMotion'})
            self.assertEqual(row['groups'], [])


if __name__ == '__main__':
    unittest.main()
