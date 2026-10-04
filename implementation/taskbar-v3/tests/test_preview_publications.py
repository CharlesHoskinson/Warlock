"""Finalized preview publication invalidation; real inotify, no GUI actions."""
import os
from pathlib import Path
import select
import tempfile
import unittest
from unittest.mock import patch

from test_taskbar_watch import WatchHarness, wait_for, watch


class PreviewPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.preview = self.root / 'hypr-window-previews'
        self.preview.mkdir()
        self.local = self.root / 'taskbar-settings.json'
        self.harness = None

    def tearDown(self):
        if self.harness:
            self.harness.close()
        self.temp.cleanup()

    def watcher(self):
        return watch.FileChanges([self.local], [self.preview])

    def staging(self, count=1):
        for index in range(count):
            for name in ('.capture.ABCDEF.png', '0xabc-0.png.tmp.png', '0xabc.json.tmp',
                         '.motion-token-0.png', '.motion-token.json.tmp',
                         '0xabc.fail', '0xabc.lock', '.capture-all.lock'):
                path = self.preview / name
                path.write_bytes(('staging-' + str(index)).encode())
                path.unlink()

    def test_existing_helper_staging_burst_is_not_dirty(self):
        observer = self.watcher()
        try:
            self.staging(100)
            self.assertFalse(observer.read())
        finally:
            observer.close()

    def test_existing_helper_final_atomic_publications_and_second_slot(self):
        observer = self.watcher()
        try:
            self.staging()
            raw = self.preview / '.capture.ABCDEF.png'
            raw.write_bytes(b'raw')
            output = self.preview / '0xabc-0.png'
            staging = self.preview / '0xabc-0.png.tmp.png'
            staging.write_bytes(b'pixels')
            self.assertFalse(observer.read(), 'pre-rename capture work must stay silent')
            staging.replace(output)
            self.assertTrue(observer.read())
            (self.preview / '0xabc-1.png').write_bytes(output.read_bytes())
            self.assertTrue(observer.read())
            metadata = self.preview / '0xabc.json.tmp'
            metadata.write_text('{"pid":123,"stableId":"id"}')
            self.assertFalse(observer.read())
            metadata.replace(self.preview / '0xabc.json')
            self.assertTrue(observer.read())
            raw.unlink()
            self.assertFalse(observer.read())
        finally:
            observer.close()

    def test_final_pixel_rewrite_remains_dirty_with_same_ready_identity(self):
        (self.preview / '0xabc-0.png').write_bytes(b'old')
        (self.preview / '0xabc.json').write_text('{"pid":123,"stableId":"same"}')
        observer = self.watcher()
        try:
            (self.preview / '0xabc-0.png').write_bytes(b'new')
            self.assertTrue(observer.read(), 'unchanged metadata does not imply unchanged pixels')
            (self.preview / '0xabc.json').write_text('{"pid":123,"stableId":"same"}')
            self.assertTrue(observer.read(), 'finalized metadata publications remain visible')
        finally:
            observer.close()

    def test_final_delete_and_permission_change_remain_dirty(self):
        final = self.preview / '0xABC-1.png'
        final.write_bytes(b'pixels')
        observer = self.watcher()
        try:
            final.chmod(0o600)
            self.assertTrue(observer.read())
            final.unlink()
            self.assertTrue(observer.read())
            metadata = self.preview / '0xABC.json'
            metadata.write_text('{}')
            observer.read()
            metadata.unlink()
            self.assertTrue(observer.read())
        finally:
            observer.close()

    def test_ignored_burst_does_not_drop_concurrent_settings_change(self):
        observer = self.watcher()
        try:
            self.staging(20)
            self.local.write_text('{"desktopScope":"current"}')
            self.staging(20)
            self.assertTrue(observer.read())
        finally:
            observer.close()

    def test_ignored_burst_does_not_drop_concurrent_final_publication(self):
        observer = self.watcher()
        try:
            self.staging(20)
            (self.preview / '0xf00-0.png').write_bytes(b'pixels')
            self.staging(20)
            self.assertTrue(observer.read())
        finally:
            observer.close()

    def test_directory_replacement_rebuilds_and_keeps_future_updates(self):
        observer = self.watcher()
        try:
            self.preview.rename(self.root / 'previous-previews')
            self.preview.mkdir()
            (self.preview / '0xabc-0.png').write_bytes(b'initial')
            self.assertTrue(observer.read())
            (self.preview / '0xabc-0.png').write_bytes(b'next')
            self.assertTrue(observer.read())
        finally:
            observer.close()

    def test_missing_directory_creation_is_dirty(self):
        self.preview.rmdir()
        observer = self.watcher()
        try:
            self.preview.mkdir()
            self.assertTrue(observer.read())
            (self.preview / '0xabc.json').write_text('{}')
            self.assertTrue(observer.read())
        finally:
            observer.close()

    def test_overflow_forces_reconciliation_regardless_of_filter(self):
        observer = self.watcher()
        raw = watch.struct.pack('iIII', -1, observer.OVERFLOW, 0, 0)
        try:
            with patch.object(watch.os, 'read', side_effect=[raw, BlockingIOError()]):
                with patch.object(observer, 'refresh', wraps=observer.refresh) as refresh:
                    self.assertTrue(observer.read())
                    refresh.assert_called_once()
        finally:
            observer.close()

    def test_only_exact_root_finalized_filenames_match(self):
        observer = self.watcher()
        try:
            for name in ('0xabc-0.png', '0xABC-1.png', '0x1.json'):
                self.assertTrue(observer.relevant(self.preview / name), name)
            for name in ('0xabc-2.png', 'abc-0.png', '0x-0.png', '0xabc.png',
                         '.capture.ABC.png', '.motion-token.png', '0xabc.json.tmp',
                         '0xabc-1.png.tmp.png', '0xabc.fail', '0xabc.lock'):
                self.assertFalse(observer.relevant(self.preview / name), name)
            self.assertFalse(observer.relevant(self.preview / 'nested/0xabc-0.png'))
            self.assertTrue(observer.relevant(self.preview))
            self.assertTrue(observer.relevant(self.preview.parent))
        finally:
            observer.close()

    def test_final_publication_during_snapshot_is_not_swallowed(self):
        self.harness = WatchHarness(self.root, files=([self.local], [self.preview]))
        h = self.harness
        wait_for(lambda: len(h.rows()) == 1)
        def provider():
            result = h.snapshot()
            if len(h.calls) == 2:
                self.staging(10)
                (self.preview / '0xabc-0.png').write_bytes(b'published-during-query')
                self.staging(10)
            return result
        h.provider = provider
        os.write(h.input_write, b'refresh\n')
        wait_for(lambda: len(h.rows()) >= 3)
        self.assertIsNone(h.error)
        self.assertEqual(len(h.rows()), 3)

    def test_observe_ignores_transient_work_and_keeps_final_rewrites(self):
        self.harness = WatchHarness(self.root, files=([self.local], [self.preview]))
        h = self.harness
        wait_for(lambda: len(h.rows()) == 1)
        for _ in range(3):
            self.staging()
            # Wait longer than coalescing so suppression isn't just batching.
            select.select([], [], [], .09)
        self.assertEqual(len(h.rows()), 1)
        final = self.preview / '0xabc-0.png'
        final.write_bytes(b'first')
        wait_for(lambda: len(h.rows()) == 2)
        final.write_bytes(b'second')
        wait_for(lambda: len(h.rows()) == 3)
        self.assertIsNone(h.error)


if __name__ == '__main__':
    unittest.main(verbosity=2)
