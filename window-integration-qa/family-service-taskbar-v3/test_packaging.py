"""Actual production source/isolation checks; no GUI or native service."""
from pathlib import Path
import json
import os
import unittest
from unittest.mock import patch
import private_shell as p


class Packaging(unittest.TestCase):
    def test_actual_all_copied_sources_and_absolute_imports_match(self):
        row = p.verify_payload()
        self.assertEqual(len(row['copies']), 203)
        self.assertFalse(row['widgetModified'])

    def test_all_implicitly_enabled_production_services_are_disabled(self):
        row = p.verify_payload()
        disabled = set(row['config']['disabledPlugins'])
        manifests = [json.loads(x.read_text()) for x in
                     (p.B / 'payload/omarchy/shell/plugins').rglob('*.json')
                     if x.name == 'manifest.json' or x.name.endswith('.manifest.json')]
        for manifest in manifests:
            if 'service' in manifest.get('kinds', []):
                self.assertIn(manifest['id'], disabled)
        self.assertNotIn('omarchy.bar', disabled)

    def test_only_actual_window_widget_is_on_left_bar(self):
        row = p.verify_payload()['config']
        self.assertEqual(row['bar']['layout'], {
            'left': [{'id': 'hoskinson.windows'}], 'center': [], 'right': []})
        self.assertEqual(row['plugins'], [])

    def test_payload_has_no_links_into_main_catalogs(self):
        self.assertFalse(any(x.is_symlink() for x in (p.B / 'payload').rglob('*')))
        self.assertFalse((p.B / 'payload/home/.config/omarchy/virtual-desktops.json').exists())
        self.assertEqual(json.loads((p.B / 'payload/home/.config/omarchy/taskbar-pins.json').read_text()), [])

    def test_retained_absolute_import_is_explicit_and_unmodified(self):
        source = p.B / 'payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml'
        self.assertIn('import "file://' + str(p.ACCESSIBILITY) + '"', source.read_text())
        self.assertEqual(source.read_bytes(), (p.PLUGIN / 'widget_v65/Windows.qml').read_bytes())

    def test_offscope_home_materialization_refuses_before_any_copy(self):
        with patch.object(p.shutil, 'copytree', side_effect=AssertionError('must not copy')):
            with self.assertRaisesRegex(RuntimeError, 'qa-harness.slice'):
                p.prepare_home({})

    def test_changed_source_is_not_accepted_from_unchanged_copy(self):
        real = p.sha
        altered = str(p.OWNER / '.local/bin/hypr-windowctl-core')
        def changed(path):
            return '0' * 64 if str(path) == altered else real(path)
        with patch.object(p, 'sha', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'Frozen production shell input changed'):
                p.verify_payload()


if __name__ == '__main__':
    unittest.main()
