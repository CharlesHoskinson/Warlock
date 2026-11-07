#!/usr/bin/env python3
"""Pure metadata/profile safety controls. Never runs compiler or fixture executables."""
import argparse
import ast
import hashlib
import importlib.util
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest

ROOT = None
helper = None
qa = None
EXPECTED_LEGACY_PROVIDER_IF_HASHES = ['947e06e5cb87024d98de0ba97283c48c43fd3cc82df4106d291c89e9361fd249', '9f7e4caea2f2788bf952d4a49da4b907d1370d79f28e212c382cd5acf2fb726f', 'e1b53ee61082d9b11cd69812d9d536c56cae5adafc57deef6f8f17649cd0a94a']

class ProfileControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runtime = Path(self.temp.name) / 'runtime'
        self.runtime.mkdir()
        source = ROOT / 'implementation/warlock/haskell/runtime'
        shutil.copyfile(source / 'runtime.cabal', self.runtime / 'runtime.cabal')
        for directory in helper.FIXTURE_HASHES:
            (self.runtime / directory).mkdir()
            shutil.copyfile(source / directory / 'Main.hs', self.runtime / directory / 'Main.hs')

    def test_exact_fixtures_and_only_two_targets(self):
        helper.validate_runtime(self.runtime)
        self.assertEqual(helper.TARGETS, (
            ('webkit-callback-capi-controls', 'warlock-runtime:test:webkit-callback-capi-controls'),
            ('owned-signal-lifecycle-controls', 'warlock-runtime:test:owned-signal-lifecycle-controls')))

    def test_changed_fixture_refused(self):
        p = self.runtime / 'test-owned-signal/Main.hs'
        p.write_bytes(p.read_bytes() + b'-- drift\n')
        with self.assertRaises(RuntimeError): helper.validate_runtime(self.runtime)

    def test_missing_fixture_refused(self):
        (self.runtime / 'test-owned-signal/Main.hs').unlink()
        with self.assertRaises(RuntimeError): helper.validate_runtime(self.runtime)

    def test_extra_home_module_refused(self):
        (self.runtime / 'test-owned-signal/Other.hs').write_text('module Other where\n')
        with self.assertRaises(RuntimeError): helper.validate_runtime(self.runtime)

    def test_symlink_fixture_refused(self):
        p = self.runtime / 'test-owned-signal/Main.hs'; target = self.runtime / 'outside.hs'
        p.rename(target); p.symlink_to(target)
        with self.assertRaises(RuntimeError): helper.validate_runtime(self.runtime)

    def test_symlink_directory_refused(self):
        p = self.runtime / 'test-owned-signal'; target = self.runtime / 'other'
        p.rename(target); p.symlink_to(target, target_is_directory=True)
        with self.assertRaises(RuntimeError): helper.validate_runtime(self.runtime)

    def test_cabal_drift_refused(self):
        p = self.runtime / 'runtime.cabal'; p.write_bytes(p.read_bytes() + b'-- drift\n')
        with self.assertRaises(RuntimeError): helper.validate_runtime(self.runtime)

    def test_cabal_added_cpp_refused(self):
        p = self.runtime / 'runtime.cabal'
        p.write_text(p.read_text().replace('test-suite owned-signal-lifecycle-controls\n',
                                          'test-suite owned-signal-lifecycle-controls\n  cpp-options: -DBYPASS\n'))
        with self.assertRaises(RuntimeError): helper.validate_runtime(self.runtime)

    def test_cabal_dependency_or_flag_change_refused(self):
        p = self.runtime / 'runtime.cabal'
        p.write_text(p.read_text().replace('process ==1.6.19.0', 'process >=1'))
        with self.assertRaises(RuntimeError): helper.validate_runtime(self.runtime)

    def test_original_nineteen_suites_and_bytes_preserved(self):
        text = (self.runtime / 'runtime.cabal').read_text()
        self.assertTrue(text.endswith(helper.ADDED_SUFFIX))
        before = text[:-len(helper.ADDED_SUFFIX)]
        self.assertEqual(hashlib.sha256(before.encode()).hexdigest(), helper.BASE_CABAL_SHA256)
        self.assertEqual(len([line for line in before.splitlines() if line.startswith('test-suite ')]), 19)
        self.assertEqual(len([line for line in text.splitlines() if line.startswith('test-suite ')]), 21)

    def test_command_plan_build_and_list_only(self):
        output = Path('/private/output'); stage = output / 'haskell'
        plan = helper.command_plan({'cabal':'/sdk/cabal', 'ghcPrefix':'/sdk/ghc'}, output, stage)
        self.assertEqual([name for name, _ in plan], ['provider-callback-build',
            'list-webkit-callback-capi-controls', 'list-owned-signal-lifecycle-controls'])
        self.assertEqual([argv[2] for _, argv in plan], ['build', 'list-bin', 'list-bin'])
        self.assertEqual(plan[0][1][-2:], [target for _, target in helper.TARGETS])
        self.assertTrue(all('--offline' in argv for _, argv in plan))
        self.assertFalse(any(arg in ['test', 'run', 'repl', '--allow-newer'] for _, argv in plan for arg in argv))
        self.assertFalse(any('warlock-ui-backend' in arg or 'warlock-ui-owner' in arg or 'application-argv-fixture' in arg
                             for _, argv in plan for arg in argv))
        self.assertTrue(all('--jobs=2' in argv and '--with-hsc2hs=/sdk/ghc/bin/hsc2hs' in argv for _, argv in plan))

    def test_no_fixture_spawn_or_wrapper_api(self):
        tree = ast.parse((ROOT / 'tools/provider_callback_build.py').read_text())
        imported = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertNotIn('subprocess', imported)
        self.assertNotIn('ctypes', imported)
        names = [node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)]
        self.assertNotIn('Popen', names)
        self.assertNotIn('system', names)
        self.assertNotIn('kill', names)
        self.assertNotIn('killpg', names)
        self.assertNotIn('haskell_test_wrapper', (ROOT / 'tools/provider_callback_build.py').read_text())

    def test_narrow_input_closure_excludes_elm_and_native_stage_campaign(self):
        names = qa.arm64_inputs(Path(self.temp.name), provider_callback_build=True)
        self.assertIn('tools/provider_callback_build.py', names)
        self.assertIn('tools/test_provider_callback_build.py', names)
        self.assertNotIn('tools/arm64_native_stage.py', names)
        self.assertNotIn('tools/run_webkit_provider_probe.py', names)
        self.assertNotIn('tools/haskell_test_wrapper.py', names)
        self.assertNotIn('implementation/warlock/elm.json', names)
        self.assertFalse(any(name.endswith('.elm') for name in names))

    def test_fixed_mode_and_source_closure_forwarding(self):
        tree = ast.parse((ROOT / 'tools/check_arm64_cpu.py').read_text())
        self.assertIn('provider-callback-build', [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)])
        main_defs = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main']
        self.assertEqual(len(main_defs), 1)
        calls = [node for node in ast.walk(main_defs[0]) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == 'arm64_inputs']
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(any(k.arg == 'provider_callback_build' and isinstance(k.value, ast.Attribute)
                                and k.value.attr == 'provider_callback_build' for k in call.keywords) for call in calls))
        qa_tree = ast.parse((ROOT / 'tools/qa_cpu.py').read_text())
        self.assertIn('--provider-callback-build', [node.value for node in ast.walk(qa_tree) if isinstance(node, ast.Constant)])

    def test_legacy_provider_mode_branches_unchanged(self):
        tree = ast.parse((ROOT / 'tools/check_arm64_cpu.py').read_text())
        actual = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.If) and isinstance(node.test, ast.Attribute)
                    and isinstance(node.test.value, ast.Name) and node.test.value.id == 'args'
                    and node.test.attr == 'provider_probe_build'):
                actual.append(hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest())
        self.assertEqual(sorted(actual), EXPECTED_LEGACY_PROVIDER_IF_HASHES)

    def image_file(self, machine=183):
        dist = Path(self.temp.name) / 'dist'; dist.mkdir(exist_ok=True)
        p = dist / 'owned-signal-lifecycle-controls'
        data = bytearray(64); data[:4] = b'\x7fELF'; data[4:7] = bytes([2, 1, 1])
        struct.pack_into('<HHI', data, 16, 2, machine, 1)
        p.write_bytes(data); p.chmod(0o700)
        return p, dist

    def test_arm64_elf_metadata_positive_no_execution(self):
        p, dist = self.image_file(); pin = helper.pin_image(p, dist, p.name)
        self.assertEqual(pin['sha256'], hashlib.sha256(p.read_bytes()).hexdigest())
        self.assertFalse(pin['executed'])

    def test_foreign_architecture_refused(self):
        p, dist = self.image_file(62)
        with self.assertRaises(RuntimeError): helper.pin_image(p, dist, p.name)

    def test_symlink_and_foreign_output_image_refused(self):
        p, dist = self.image_file(); other = dist / 'alias'; other.symlink_to(p)
        with self.assertRaises(RuntimeError): helper.pin_image(other, dist, p.name)
        with self.assertRaises(RuntimeError): helper.pin_image(p, dist / 'elsewhere', p.name)

    def test_setid_image_refused(self):
        p, dist = self.image_file(); p.chmod(0o4700)
        with self.assertRaises(RuntimeError): helper.pin_image(p, dist, p.name)


def main():
    global ROOT, helper, qa
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    ROOT = args.root.resolve()
    sys.path.insert(0, str(ROOT / 'tools'))
    spec = importlib.util.spec_from_file_location('provider_callback_build', ROOT / 'tools/provider_callback_build.py')
    if spec is None or spec.loader is None:
        raise RuntimeError('missing fixed helper loader')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    import qa_cpu
    qa = qa_cpu
    unittest.main(argv=[sys.argv[0]], verbosity=0)

if __name__ == '__main__':
    main()
