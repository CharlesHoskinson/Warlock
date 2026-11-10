#!/usr/bin/env python3
"""Pure fixed map-diagnostic controls; no process observation or native effect."""
import argparse
import ast
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

p = argparse.ArgumentParser()
p.add_argument('--module', required=True)
args, rest = p.parse_known_args()
spec = importlib.util.spec_from_file_location('fixed_mapping_diagnostics', args.module)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


class Controls(unittest.TestCase):
    def test_all_missing_names_sorted_deduplicated_without_inventory_change(self):
        rows = [{'pathname': n} for n in ['/z', '/a', '/z', '/known', '/dev/dri/card0', '[heap]', None]]
        inventory = {'/known': 'a'*64}
        before = copy.deepcopy(inventory)
        actual = m.missing_named_mappings(rows, inventory, {'/dev/dri/card0': {}})
        self.assertEqual(actual, {'missingNamedPathCount': 2, 'missingNamedPaths': ['/a', '/z'], 'allMissingNamesRetained': True, 'inventoryChanged': False})
        self.assertEqual(inventory, before)

    def test_deleted_named_mapping_stays_missing_even_if_listed(self):
        path = '/fixed/object (deleted)'
        result = m.missing_named_mappings([{'pathname': path}], {path: 'a'*64}, {})
        self.assertEqual(result['missingNamedPaths'], [path])

    def test_bounded_name_count_retains_actual_count_and_marks_truncation(self):
        rows = [{'pathname': '/fixed/'+str(i)} for i in range(300)]
        result = m.missing_named_mappings(rows, {}, {})
        self.assertEqual(result['missingNamedPathCount'], 300)
        self.assertEqual(len(result['missingNamedPaths']), 256)
        self.assertFalse(result['allMissingNamesRetained'])

    def test_bounded_name_bytes_mark_incomplete_evidence(self):
        result = m.missing_named_mappings([{'pathname': '/'+('x'*9000)}], {}, {})
        self.assertEqual(len(result['missingNamedPaths'][0]), 8192)
        self.assertFalse(result['allMissingNamesRetained'])

    def test_32_seeded_missing_vs_known_paths_never_added_to_inventory(self):
        for seed in range(32):
            value = (seed*1664525+1013904223) & 0xffffffff
            path = '/fixed/'+str(value)
            inventory = {path: 'a'*64} if seed % 2 == 0 else {}
            before = copy.deepcopy(inventory)
            result = m.missing_named_mappings([{'pathname': path}], inventory, {})
            self.assertEqual(result['missingNamedPaths'], [] if seed % 2 == 0 else [path])
            self.assertEqual(inventory, before)

    def test_actual_route_records_snapshot_then_uses_unchanged_strict_checker(self):
        tree = ast.parse(Path(args.module).read_text())
        function = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'process_maps')
        calls = [n for n in ast.walk(function) if isinstance(n, ast.Call)]
        strict = [n for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == 'strict_snapshot_files']
        self.assertEqual(len(strict), 1)
        expected = ast.parse("boot_correspondence.strict_snapshot_files(context['current'],context['base'],context['foundation']['graphics'],rows,packet['processInventory'],required,None,clock)", mode='eval').body
        self.assertEqual(ast.dump(strict[0]), ast.dump(expected))
        snapshots = [n for n in calls if isinstance(n.func, ast.Name) and n.func.id == 'write_json']
        diagnostic = [n for n in calls if isinstance(n.func, ast.Name) and n.func.id == 'missing_named_mappings']
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(len(diagnostic), 1)
        self.assertLess(snapshots[0].lineno, strict[0].lineno)
        self.assertLess(diagnostic[0].lineno, strict[0].lineno)
        self.assertFalse(any(isinstance(n, (ast.Try, ast.ExceptHandler)) for n in ast.walk(function)))

    def test_append_only_v6_packet_namespace(self):
        tree = ast.parse(Path(args.module).read_text())
        packet = next(n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PACKET' for t in n.targets))
        self.assertIn('ux024-connected-foreign-toplevel-observer-v6/packet.json', ast.unparse(packet))


if __name__ == '__main__':
    unittest.main(argv=[__file__, *rest])
