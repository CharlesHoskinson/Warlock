#!/usr/bin/env python3
"""Pure fixed-profile controls; no compiler, GTK, fixture or native execution."""
import argparse
import ast
import hashlib
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = None
helper = None
qa = None
EXPECTED_TARGETS = (
    ('warlock-ui-owner', 'warlock-runtime:exe:warlock-ui-owner'),
    ('ui-webkit-controls', 'warlock-runtime:test:ui-webkit-controls'),
    ('physical-context-owner-controls', 'warlock-runtime:test:physical-context-owner-controls'),
    ('physical-context-owner-threaded-controls', 'warlock-runtime:test:physical-context-owner-threaded-controls'),
)
EXPECTED_NEW_PATHS = {
    'ui/Warlock/Ui/DefaultContextOwner.hs',
    'ui/Warlock/Ui/CallbackRetirement.hs',
    'ui/Warlock/Ui/ProcessSignalOwner.hs',
    'test-ui-webkit/Main.hs',
    'test-default-context-owner/Main.hs',
}
EXPECTED_LEGACY = {
    'tools/provider_callback_build.py': 'd2b3021866b0f6ce8403358df9fa41dc6a0a59e7d7e597a34262aada6450d7e5',
    'tools/test_provider_callback_build.py': '4e11c1f3a561bcb291eff0d0d0522b8e0001daf60f5193d60f865df7a6e68c8a',
}
NONTHREADED_FLAGS = '-Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0'


class PhysicalBuildControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runtime = Path(self.temp.name) / 'runtime'
        self.runtime.mkdir()
        source = ROOT / 'implementation/warlock/haskell/runtime'
        for name in {'runtime.cabal', *helper.SOURCE_HASHES}:
            destination = self.runtime / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, destination)

    def test_exact_four_targets_and_no_caller_selected_target(self):
        self.assertEqual(helper.TARGETS, EXPECTED_TARGETS)
        self.assertEqual(list(__import__('inspect').signature(helper.command_plan).parameters),
                         ['packet', 'output', 'stage'])

    def test_command_plan_build_plus_four_list_bin_only(self):
        plan = helper.command_plan({'cabal': '/sdk/cabal', 'ghcPrefix': '/sdk/ghc'},
                                   Path('/private/output'), Path('/private/output/haskell'))
        self.assertEqual([name for name, _ in plan],
                         ['physical-context-owner-build'] + ['list-' + name for name, _ in EXPECTED_TARGETS])
        self.assertEqual([argv[2] for _, argv in plan], ['build'] + ['list-bin'] * 4)
        self.assertEqual(plan[0][1][-4:], [target for _, target in EXPECTED_TARGETS])
        self.assertEqual([argv[-1] for _, argv in plan[1:]], [target for _, target in EXPECTED_TARGETS])
        for _, argv in plan:
            for flag in ['--offline', '--jobs=2', '--with-hsc2hs=/sdk/ghc/bin/hsc2hs',
                         '--with-gcc=/usr/bin/gcc', '--with-ar=/usr/bin/ar', '--with-ld=/usr/bin/ld']:
                self.assertIn(flag, argv)
            self.assertFalse(any(value in ('test', 'run', 'exec', 'repl', '--allow-newer') for value in argv))

    def test_existing_fixed_sdk_flags_are_reused_exactly(self):
        from provider_callback_build import command_plan as legacy_plan
        packet = {'cabal': '/sdk/cabal', 'ghcPrefix': '/sdk/ghc'}
        output = Path('/private/output')
        old = legacy_plan(packet, output, output / 'haskell')
        new = helper.command_plan(packet, output, output / 'haskell')
        self.assertEqual(old[0][1][:-2], new[0][1][:-4])
        self.assertTrue(all(argv[:-1] == old[1][1][:-1] for _, argv in new[1:]))

    def test_exact_source_and_cabal_validate(self):
        helper.validate_runtime(self.runtime)

    def test_all_actual_new_home_modules_required(self):
        self.assertTrue(EXPECTED_NEW_PATHS.issubset(helper.SOURCE_HASHES))
        self.assertEqual(set(helper.SOURCE_HASHES), EXPECTED_NEW_PATHS | {
            'ui/Warlock/Ui/WebKit.hs', 'ui/Warlock/Ui/Mvp.hsc'})

    def test_changed_source_refused(self):
        file = self.runtime / 'ui/Warlock/Ui/DefaultContextOwner.hs'
        file.write_bytes(file.read_bytes() + b'-- drift\n')
        with self.assertRaises(RuntimeError):
            helper.validate_runtime(self.runtime)

    def test_missing_retirement_cell_refused(self):
        (self.runtime / 'ui/Warlock/Ui/CallbackRetirement.hs').unlink()
        with self.assertRaises(RuntimeError):
            helper.validate_runtime(self.runtime)

    def test_symlink_source_refused(self):
        file = self.runtime / 'ui/Warlock/Ui/DefaultContextOwner.hs'
        other = self.runtime / 'outside.hs'
        file.rename(other)
        file.symlink_to(other)
        with self.assertRaises(RuntimeError):
            helper.validate_runtime(self.runtime)

    def test_symlink_source_ancestor_refused(self):
        directory = self.runtime / 'ui/Warlock/Ui'
        other = self.runtime / 'other-ui'
        directory.rename(other)
        directory.symlink_to(other, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            helper.validate_runtime(self.runtime)

    def test_symlink_fixture_directory_refused(self):
        directory = self.runtime / 'test-default-context-owner'
        other = self.runtime / 'other-fixture'
        directory.rename(other)
        directory.symlink_to(other, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            helper.validate_runtime(self.runtime)

    def test_extra_fixture_home_module_refused(self):
        (self.runtime / 'test-default-context-owner/Extra.hs').write_text('module Extra where\n')
        with self.assertRaises(RuntimeError):
            helper.validate_runtime(self.runtime)

    def test_extra_fixture_c_source_refused(self):
        (self.runtime / 'test-default-context-owner/extra.c').write_text('/* not selected */\n')
        with self.assertRaises(RuntimeError):
            helper.validate_runtime(self.runtime)

    def test_symlink_cabal_refused(self):
        file = self.runtime / 'runtime.cabal'
        other = self.runtime / 'other.cabal'
        file.rename(other)
        file.symlink_to(other)
        with self.assertRaises(RuntimeError):
            helper.validate_runtime(self.runtime)

    def test_changed_cabal_refused(self):
        file = self.runtime / 'runtime.cabal'
        file.write_bytes(file.read_bytes() + b'-- drift\n')
        with self.assertRaises(RuntimeError):
            helper.validate_runtime(self.runtime)

    def test_threaded_flag_cannot_be_added_to_owner(self):
        self.assertIn('  ghc-options: ' + NONTHREADED_FLAGS + '\n',
                      helper.COMPONENT_STANZAS['executable warlock-ui-owner'])
        file = self.runtime / 'runtime.cabal'
        original = file.read_text()
        stanza = helper.COMPONENT_STANZAS['executable warlock-ui-owner']
        altered = stanza.replace('  ghc-options: ', '  ghc-options: -threaded ')
        file.write_text(original.replace(stanza, altered))
        with patch.object(helper, 'CABAL_SHA256', hashlib.sha256(file.read_bytes()).hexdigest()):
            with self.assertRaises(RuntimeError):
                helper.validate_runtime(self.runtime)

    def test_both_fixture_modes_and_original_nonthreaded_consumer(self):
        for key in ['executable warlock-ui-owner', 'test-suite ui-webkit-controls',
                    'test-suite physical-context-owner-controls']:
            flags = [line for line in helper.COMPONENT_STANZAS[key].splitlines()
                     if line.startswith('  ghc-options:')]
            self.assertEqual(flags, ['  ghc-options: ' + NONTHREADED_FLAGS])
        flags = [line for line in helper.COMPONENT_STANZAS['test-suite physical-context-owner-threaded-controls'].splitlines()
                 if line.startswith('  ghc-options:')]
        self.assertEqual(len(flags), 1)
        self.assertIn('-threaded', flags[0].split())

    def test_component_field_drift_refused_even_with_changed_whole_pin(self):
        file = self.runtime / 'runtime.cabal'
        original = file.read_text()
        stanza = helper.COMPONENT_STANZAS['test-suite physical-context-owner-controls']
        altered = stanza.replace('  main-is: Main.hs', '  main-is: Other.hs')
        self.assertNotEqual(stanza, altered)
        file.write_text(original.replace(stanza, altered))
        with patch.object(helper, 'CABAL_SHA256', hashlib.sha256(file.read_bytes()).hexdigest()):
            with self.assertRaises(RuntimeError):
                helper.validate_runtime(self.runtime)

    def test_missing_sources_remain_in_required_input_closure(self):
        names = qa.arm64_inputs(Path(self.temp.name) / 'missing', physical_context_owner_build=True)
        for name in EXPECTED_NEW_PATHS:
            self.assertIn('implementation/warlock/haskell/runtime/' + name, names)
        for name in ['tools/physical_context_build.py', 'tools/test_physical_context_build.py',
                     'tools/provider_callback_build.py']:
            self.assertIn(name, names)
        self.assertFalse(any(name.endswith('.elm') for name in names))
        self.assertNotIn('tools/arm64_native_stage.py', names)

    def test_old_callback_helper_and_all_29_controls_unchanged(self):
        for name, expected in EXPECTED_LEGACY.items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)
        tree = ast.parse((ROOT / 'tools/test_provider_callback_build.py').read_text())
        self.assertEqual(sum(isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
                             for node in ast.walk(tree)), 29)

    def test_closed_mode_and_two_source_closure_forwardings(self):
        check = ast.parse((ROOT / 'tools/check_arm64_cpu.py').read_text())
        main = [node for node in check.body if isinstance(node, ast.FunctionDef) and node.name == 'main']
        self.assertEqual(len(main), 1)
        calls = [node for node in ast.walk(main[0]) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == 'arm64_inputs']
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(any(key.arg == 'physical_context_owner_build'
                                and isinstance(key.value, ast.Attribute)
                                and key.value.attr == 'physical_context_owner_build'
                                for key in call.keywords) for call in calls))
        self.assertIn('physical-context-owner-build', [node.value for node in ast.walk(check)
                                                     if isinstance(node, ast.Constant)])
        qa_tree = ast.parse((ROOT / 'tools/qa_cpu.py').read_text())
        self.assertIn('--physical-context-owner-build', [node.value for node in ast.walk(qa_tree)
                                                       if isinstance(node, ast.Constant)])

    def test_no_spawn_or_fixture_wrapper_in_helper(self):
        text = (ROOT / 'tools/physical_context_build.py').read_text()
        tree = ast.parse(text)
        imports = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
        self.assertNotIn('subprocess', imports)
        self.assertNotIn('ctypes', imports)
        attributes = [node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)]
        for name in ['Popen', 'system', 'kill', 'killpg']:
            self.assertNotIn(name, attributes)
        self.assertNotIn('haskell_test_wrapper', text)

    def test_existing_image_pin_implementation_is_reused(self):
        from provider_callback_build import pin_image
        self.assertIs(helper.pin_image, pin_image)


class BridgeProfileTests(unittest.TestCase):
    def test_bridge_targets_keep_original_four_and_only_two_behaviors(self):
        expected = EXPECTED_TARGETS + (
            ('ui-engine-protocol-controls', 'warlock-runtime:test:ui-engine-protocol-controls'),
            ('ui-engine-broker-controls', 'warlock-runtime:test:ui-engine-broker-controls'))
        self.assertEqual(helper.BRIDGE_TARGETS, expected)
        self.assertEqual(helper.BRIDGE_BEHAVIOR_SUITES,
                         ('ui-engine-protocol-controls', 'ui-engine-broker-controls'))
        packet = {'cabal': '/sdk/cabal', 'ghcPrefix': '/sdk/ghc'}
        output = Path('/private/output')
        old = helper.command_plan(packet, output, output / 'haskell')
        new = helper.bridge_command_plan(packet, output, output / 'haskell')
        self.assertEqual([argv[2] for _, argv in new], ['build'] + ['list-bin'] * 6)
        self.assertEqual(new[0][1][:-6], old[0][1][:-4])
        self.assertEqual(new[0][1][-6:], [target for _, target in expected])
        self.assertTrue(all(argv[:-1] == old[1][1][:-1] for _, argv in new[1:]))

    def test_bridge_missing_or_drifted_owner_and_fixture_refused(self):
        with tempfile.TemporaryDirectory(prefix='bridge-profile-control-') as directory:
            runtime = Path(directory) / 'runtime'
            for name in {'runtime.cabal', *helper.SOURCE_HASHES, *helper.BRIDGE_SOURCE_HASHES}:
                destination = runtime / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'implementation/warlock/haskell/runtime' / name, destination)
            helper.validate_bridge_runtime(runtime)
            for name in ['ui/Main.hs', 'ui/Warlock/Ui/EngineCustody.hsc',
                         'test-ui-engine-protocol/Main.hs', 'test-ui-engine-broker/Main.hs']:
                with self.subTest(source=name):
                    file = runtime / name
                    original = file.read_bytes()
                    file.unlink()
                    with self.assertRaises(RuntimeError):
                        helper.validate_bridge_runtime(runtime)
                    file.write_bytes(original + b'-- drift\n')
                    with self.assertRaises(RuntimeError):
                        helper.validate_bridge_runtime(runtime)
                    file.write_bytes(original)

    def test_bridge_refuses_missing_executor_before_staging(self):
        with self.assertRaises(RuntimeError):
            helper.run_profile('/missing', '/missing', {}, None, bridge=True)

    def test_bridge_closure_forces_all_declared_files_when_absent(self):
        names = qa.arm64_inputs(Path('/missing'), physical_context_owner_bridge=True)
        for name in helper.BRIDGE_SOURCE_HASHES:
            self.assertIn('implementation/warlock/haskell/runtime/' + name, names)
        self.assertIn('tools/haskell_test_wrapper.py', names)
        self.assertFalse(any(name.endswith('.elm') for name in names))


def main():
    global ROOT, helper, qa
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    ROOT = args.root.resolve()
    sys.path.insert(0, str(ROOT / 'tools'))
    spec = importlib.util.spec_from_file_location('physical_context_build', ROOT / 'tools/physical_context_build.py')
    if spec is None or spec.loader is None:
        raise RuntimeError('missing fixed physical helper loader')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    import qa_cpu
    qa = qa_cpu
    unittest.main(argv=[sys.argv[0]], verbosity=0)


if __name__ == '__main__':
    main()
