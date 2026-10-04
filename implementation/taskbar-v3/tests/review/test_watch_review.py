import importlib.util
from pathlib import Path
import select
import tempfile
import unittest

source = Path(__file__).resolve().parents[2] / 'taskbar_watch.py'
spec = importlib.util.spec_from_file_location('watch_review', source)
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)


class RenameReviewTests(unittest.TestCase):
    def test_exact_file_moved_out_marks_dirty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / 'config'
            config.mkdir()
            target = config / 'taskbar-pins.json'
            target.write_text('[]')
            observer = watch.FileChanges([target], [])
            try:
                target.rename(root / 'old-pins.json')
                ready, _, _ = select.select([observer.fd], [], [], .2)
                self.assertTrue(ready, 'rename-out must be observed immediately')
                self.assertTrue(observer.read(), 'rename-out must invalidate snapshot')
            finally:
                observer.close()

    def test_desktop_moved_out_marks_dirty(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            applications = root / 'applications'
            applications.mkdir()
            target = applications / 'app.desktop'
            target.write_text('[Desktop Entry]')
            observer = watch.FileChanges([], [applications])
            try:
                target.rename(root / 'old.desktop')
                ready, _, _ = select.select([observer.fd], [], [], .2)
                self.assertTrue(ready, 'desktop rename-out must be observed immediately')
                self.assertTrue(observer.read(), 'desktop rename-out must invalidate snapshot')
            finally:
                observer.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
