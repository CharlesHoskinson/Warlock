import ast
import configparser
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'native/taskbar_catalog.py'
spec = importlib.util.spec_from_file_location('taskbar_catalog', MODULE)
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.user, self.system = self.base / 'user', self.base / 'system'
        self.cache = self.base / 'cache'
        for root in (self.user, self.system):
            (root / 'applications').mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def desktop(self, name='app.desktop', body=None, root=None):
        path = (root or self.user) / 'applications' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body or '[Desktop Entry]\nType=Application\nName=Demo\nExec=demo %U\n')
        return path

    def load(self, **kwargs):
        return catalog.load_catalog(kwargs.get('data_home', self.user), kwargs.get('data_dirs', [self.system]), kwargs.get('cache_dir', self.cache))

    def test_preserves_entries_actions_and_literal_exec(self):
        self.desktop('nested/app.desktop', '[Desktop Entry]\nType=Application\nName=Example\nExec=example --arg "$HOME" %U\nStartupWMClass=Example\nTerminal=TRUE\nMimeType=text/plain;\nActions=new;missing;empty;\n[Desktop Action new]\nName=New\nExec=example --new %F\n[Desktop Action empty]\nName=Empty\n')
        value = self.load()['nested-app']
        self.assertEqual(value['exec'], 'example --arg "$HOME" %U')
        self.assertEqual(value['actions'], [{'id': 'new', 'name': 'New', 'exec': 'example --new %F'}])
        self.assertTrue(value['terminal'])
        self.assertEqual(value['mime'], ['text/plain', ''])
        self.assertEqual(value['wmclass'], 'Example')
        self.assertEqual(value['icon'], 'application-x-executable')

    def test_original_entries_equivalence(self):
        self.desktop('nested/app.desktop')
        self.desktop('hidden.desktop', '[Desktop Entry]\nHidden=true\n')
        self.desktop('hidden.desktop', root=self.system)
        self.desktop('app.desktop', root=self.system)
        self.desktop('fallback.desktop', '[Desktop Entry]\nType=Link\n')
        self.desktop('fallback.desktop', root=self.system)
        original_path = Path('/home/hoskinson/omarchy-windows-parity/installed/home/.local/bin/hypr-taskbar')
        tree = ast.parse(original_path.read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'entries')
        namespace = {'DATA': self.user, 'Path': Path, 'os': os, 'configparser': configparser}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(original_path), 'exec'), namespace)
        with patch.dict(os.environ, {'XDG_DATA_DIRS': str(self.system)}):
            self.assertEqual(self.load(), namespace['entries']())

    def test_nonregular_desktop_skips_without_blocking(self):
        os.mkfifo(self.user / 'applications/fifo.desktop')
        self.assertEqual(self.load(), {})
        self.assertFalse((self.cache / 'catalog.json').exists())

    def test_user_precedence(self):
        self.desktop(root=self.system)
        self.desktop(body='[Desktop Entry]\nType=Application\nName=User\nExec=user\n')
        self.assertEqual(self.load()['app']['name'], 'User')

    def test_hidden_user_masks_system(self):
        self.desktop(root=self.system)
        self.desktop(body='[Desktop Entry]\nHidden=true\n')
        self.assertEqual(self.load(), {})

    def test_invalid_user_does_not_mask_system_or_cache_partial(self):
        self.desktop(root=self.system)
        self.desktop(body='[broken')
        self.assertEqual(self.load()['app']['name'], 'Demo')
        self.assertFalse((self.cache / 'catalog.json').exists())

    def test_nonapplication_user_does_not_mask_system(self):
        self.desktop(root=self.system)
        self.desktop(body='[Desktop Entry]\nType=Link\nExec=other\n')
        self.assertEqual(self.load()['app']['name'], 'Demo')

    def test_warm_load_eliminates_parse(self):
        self.desktop()
        expected = self.load()
        with patch.object(catalog, '_parse', side_effect=AssertionError('warm parse')):
            for _ in range(20):
                self.assertEqual(self.load(), expected)

    def test_edit_same_size_invalidate(self):
        path = self.desktop()
        self.load()
        old = path.stat()
        path.write_text(path.read_text().replace('Demo', 'Edit'))
        os.utime(path, ns=(old.st_atime_ns, old.st_mtime_ns))
        self.assertEqual(self.load()['app']['name'], 'Edit')

    def test_nested_add_remove(self):
        self.desktop()
        self.load()
        path = self.desktop('new/deep/app.desktop')
        self.assertIn('new-deep-app', self.load())
        path.unlink()
        self.assertNotIn('new-deep-app', self.load())

    def test_missing_root_appears(self):
        root = self.base / 'new-root'
        self.assertEqual(self.load(data_home=root), {})
        self.desktop(root=root)
        self.assertIn('app', self.load(data_home=root))

    def test_root_key_invalidation(self):
        self.desktop()
        self.load()
        self.assertEqual(self.load(data_home=self.base / 'empty', data_dirs=[]), {})

    def test_corrupt_cache_falls_back(self):
        self.desktop()
        self.load()
        (self.cache / 'catalog.json').write_text('{broken')
        self.assertIn('app', self.load())
        self.assertEqual(json.loads((self.cache / 'catalog.json').read_text())['schema'], catalog.SCHEMA)

    def test_schema_and_shape_invalidation(self):
        self.desktop()
        self.load()
        path = self.cache / 'catalog.json'
        for mutation in ('schema', 'catalog'):
            data = json.loads(path.read_text())
            data[mutation] = 999 if mutation == 'schema' else {'app': {'id': 'app'}}
            path.write_text(json.dumps(data))
            self.assertEqual(self.load()['app']['name'], 'Demo')

    def test_unreadable_file_does_not_replace_success_cache(self):
        path = self.desktop()
        self.load()
        previous = (self.cache / 'catalog.json').read_bytes()
        path.write_text('[Desktop Entry]\nType=Application\nName=Edit\nExec=edit\n')
        original = Path.open
        def reject(instance, *args, **kwargs):
            if instance == path:
                raise PermissionError('fixture')
            return original(instance, *args, **kwargs)
        with patch.object(Path, 'open', reject):
            self.assertEqual(self.load(), {})
        self.assertEqual((self.cache / 'catalog.json').read_bytes(), previous)
        self.assertEqual(self.load()['app']['name'], 'Edit')

    def test_change_during_parse_not_cached(self):
        path = self.desktop()
        original = catalog._parse
        def changed(groups):
            result = original(groups)
            path.write_text('[Desktop Entry]\nType=Application\nName=Next\nExec=next\n')
            return result
        with patch.object(catalog, '_parse', changed):
            self.assertEqual(self.load()['app']['name'], 'Demo')
        self.assertFalse((self.cache / 'catalog.json').exists())
        self.assertEqual(self.load()['app']['name'], 'Next')

    def test_inventory_failure_fresh_fallback(self):
        self.desktop()
        with patch.object(catalog, '_inventory', side_effect=PermissionError('inventory')):
            self.assertIn('app', self.load())
        self.assertFalse(self.cache.exists())

    def test_file_symlink_target_edit(self):
        target = self.base / 'outside.desktop'
        target.write_text('[Desktop Entry]\nType=Application\nName=One\nExec=one\n')
        (self.user / 'applications/app.desktop').symlink_to(target)
        self.assertEqual(self.load()['app']['name'], 'One')
        target.write_text('[Desktop Entry]\nType=Application\nName=Two\nExec=two\n')
        self.assertEqual(self.load()['app']['name'], 'Two')

    def test_directory_symlink_not_traversed(self):
        self.desktop(root=self.system)
        (self.user / 'applications/linked').symlink_to(self.system / 'applications', target_is_directory=True)
        self.assertNotIn('linked-app', self.load())

    def test_cache_permissions(self):
        self.desktop()
        self.load()
        self.assertEqual(self.cache.stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.cache / 'catalog.json').stat().st_mode & 0o777, 0o600)

    def test_symlink_cache_directory_refused(self):
        self.desktop()
        destination = self.base / 'destination'
        destination.mkdir(mode=0o700)
        self.cache.symlink_to(destination, target_is_directory=True)
        self.assertIn('app', self.load())
        self.assertEqual(list(destination.iterdir()), [])

    def test_symlink_cache_file_not_read(self):
        self.desktop()
        self.cache.mkdir(mode=0o700)
        external = self.base / 'external.json'
        external.write_text('unchanged')
        (self.cache / 'catalog.json').symlink_to(external)
        self.assertIn('app', self.load())
        self.assertEqual(external.read_text(), 'unchanged')
        self.assertFalse((self.cache / 'catalog.json').is_symlink())

    def test_shared_cache_directory_refused(self):
        self.desktop()
        self.cache.mkdir(mode=0o755)
        self.assertIn('app', self.load())
        self.assertFalse((self.cache / 'catalog.json').exists())

    def test_unicode_malformed_is_not_cached(self):
        path = self.desktop()
        path.write_bytes(b'\xff')
        self.assertEqual(self.load(), {})
        self.assertFalse((self.cache / 'catalog.json').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
