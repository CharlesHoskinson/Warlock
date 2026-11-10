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



EXPECTED_OLD_TEST_AST = {'PhysicalBuildControls.test_exact_four_targets_and_no_caller_selected_target': '97d10169b06020d7f96cbad57277250511b2c05a2685857d9bbf697de940c223', 'PhysicalBuildControls.test_command_plan_build_plus_four_list_bin_only': '41c81745013b872b9276e6fe0e0a99b4ec0150e84b383e24f0b606d1bab72f97', 'PhysicalBuildControls.test_existing_fixed_sdk_flags_are_reused_exactly': 'e41c4a18a558ad28d59320a43e4fcacdfdfd7147cc83200b8ddad233b440a395', 'PhysicalBuildControls.test_exact_source_and_cabal_validate': 'd4f7f64aa49c16982f557fdcc3db049c3e47cddbd94ac0a17e40ff2749b6baeb', 'PhysicalBuildControls.test_all_actual_new_home_modules_required': '6e0d6d6ff1362c8ee7b1ced7714df1d23146629e7c89c9b1e68a07d4da8e78ca', 'PhysicalBuildControls.test_changed_source_refused': 'fa7278cec5d1360bd6353594687df609e6caed3f8852fe941feeedc982c4cf94', 'PhysicalBuildControls.test_missing_retirement_cell_refused': '2daa653c6c63e874b7ac4bb1793cb25cf83f2f4701f8b9698223a9c759d790cc', 'PhysicalBuildControls.test_symlink_source_refused': 'b95fbb4c230833be084c4e7f7537aa9f39f713ceb48a5dee8ef79e3d56be7c4d', 'PhysicalBuildControls.test_symlink_source_ancestor_refused': '6c6b3089eb678e35d0814ab0b1d4a1906e55fd4bf13429c553fe8be7375ccbcd', 'PhysicalBuildControls.test_symlink_fixture_directory_refused': '97e2df9978708c9db78bdc897e28c26dd56d12ee1b844d8b93acdfa7a4cbd41d', 'PhysicalBuildControls.test_extra_fixture_home_module_refused': 'e53acc8d96260e88af1ec355dbdf5b735b2cb48417643e03986211105720c5f4', 'PhysicalBuildControls.test_extra_fixture_c_source_refused': '099b407572b6fdddeb4b342ebf7913c5207aa644ce296ae054c015e88903b42f', 'PhysicalBuildControls.test_symlink_cabal_refused': 'edf5b3d4a6f60df27c8ef7fdb9e9f73ff6492d0f3096016d6e281006ab3e4e72', 'PhysicalBuildControls.test_changed_cabal_refused': '26eab4bc131c959551649425bdf17d1678a7d5b75acee1827ac0d32f39a49c93', 'PhysicalBuildControls.test_threaded_flag_cannot_be_added_to_owner': '5043a10b2e9f8bd16fddf3ec464e7b4e48b2b3f138d9f9fbd8b13f873ad214fe', 'PhysicalBuildControls.test_both_fixture_modes_and_original_nonthreaded_consumer': '1052982929739050d1981adc564651ecae2b41403cb66360862ad80d15ffb029', 'PhysicalBuildControls.test_component_field_drift_refused_even_with_changed_whole_pin': 'b8d310a32718bf8a79adbd76c0915e5347228b5f168931dd62eadbaf510dac64', 'PhysicalBuildControls.test_missing_sources_remain_in_required_input_closure': '08fe480f6e849e496240c2ff288c728d38cdce3b77068b5057893f24f6b80a91', 'PhysicalBuildControls.test_old_callback_helper_and_all_29_controls_unchanged': '34ebeb69865ace196c6216b63febbbc6d88a5b876112675c8dd6d1df12609191', 'PhysicalBuildControls.test_closed_mode_and_two_source_closure_forwardings': '3849d03ce0d335683b9632c662f7d869ca1ef931c481e77845a3327ca29357e9', 'PhysicalBuildControls.test_no_spawn_or_fixture_wrapper_in_helper': 'fdde485de42cf5523e223dc83678bbf3173cefd4421bff3221a6e259f17885a3', 'PhysicalBuildControls.test_existing_image_pin_implementation_is_reused': '7fc0e1baa6a8a825a36c3671774f2f78f02c20762684b5d4f102e24be768b0ed', 'BridgeProfileTests.test_bridge_targets_keep_original_four_and_only_two_behaviors': '21d9d9f2aabfda136f2164690f984098b563aa597eb05572c170d247e4441893', 'BridgeProfileTests.test_bridge_missing_or_drifted_owner_and_fixture_refused': '600c9994f4be3fb94f92f02aaf130d8aa80637333c239cff02a23f797a6b02b4', 'BridgeProfileTests.test_bridge_refuses_missing_executor_before_staging': '291eb9530a720fb37e572ce82e579ca398155f7e26f5c9c752457be9684979c3', 'BridgeProfileTests.test_bridge_closure_forces_all_declared_files_when_absent': 'd1a1086250c8e8c314c58d4f90eb134fbbe32d04487e25cc2ca642ea9c067f04'}
EXPECTED_OLD_NOARGS = {'workspace-navigation-controls', 'ui-private-network-controls', 'held-document-controls', 'ui-engine-broker-controls', 'native-cancellation-controls', 'ui-engine-controls', 'webkit-provider-probe-contract-controls', 'ui-engine-exec-controls', 'ui-display-controls', 'ui-engine-protocol-controls', 'elf-cases', 'owner-sequences', 'preview-control', 'desktop-boundary-controls', 'ui-webkit-controls', 'boundary-controls', 'public-controls'}

class BackingProfileTests(unittest.TestCase):
    def test_backing_exact_seventh_target_third_behavior(self):
        self.assertEqual(helper.BACKING_TARGETS, helper.BRIDGE_TARGETS + (
            ('filter-backing-root-controls', 'warlock-runtime:test:filter-backing-root-controls'),))
        self.assertEqual(helper.BACKING_BEHAVIOR_SUITES, helper.BRIDGE_BEHAVIOR_SUITES +
                         ('filter-backing-root-controls',))
        output = Path('/private/output')
        packet = {'cabal': '/sdk/cabal', 'ghcPrefix': '/sdk/ghc'}
        old = helper.bridge_command_plan(packet, output, output / 'haskell')
        new = helper.backing_command_plan(packet, output, output / 'haskell')
        self.assertEqual([argv[2] for _, argv in new], ['build'] + ['list-bin'] * 7)
        self.assertEqual(new[0][1][:-7], old[0][1][:-6])
        self.assertEqual(new[0][1][-7:], [target for _, target in helper.BACKING_TARGETS])
        self.assertTrue(all(argv[:-1] == old[1][1][:-1] for _, argv in new[1:]))
        self.assertFalse(any(word in ('run', 'test', 'exec', 'repl') for _, argv in new for word in argv))

    def test_backing_requires_protected_bridge_executor(self):
        with self.assertRaises(RuntimeError):
            helper.run_profile('/missing', '/missing', {}, None, backing=True)
        with self.assertRaises(RuntimeError):
            helper.run_profile('/missing', '/missing', {}, None, bridge=True, backing=True)

    def test_backing_missing_drift_symlink_and_extra_home_refused(self):
        with tempfile.TemporaryDirectory(prefix='backing-profile-control-') as directory:
            runtime = Path(directory) / 'runtime'
            for name in {'runtime.cabal', *helper.SOURCE_HASHES, *helper.BRIDGE_SOURCE_HASHES,
                         *helper.BACKING_SOURCE_HASHES}:
                destination = runtime / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'implementation/warlock/haskell/runtime' / name, destination)
            helper.validate_backing_runtime(runtime)
            for name in ['ui/Warlock/Ui/FilterBackingRoot.hsc', 'test-filter-backing-root/Main.hs']:
                file = runtime / name
                original = file.read_bytes()
                file.unlink()
                with self.assertRaises(RuntimeError): helper.validate_backing_runtime(runtime)
                file.write_bytes(original + b'-- drift\n')
                with self.assertRaises(RuntimeError): helper.validate_backing_runtime(runtime)
                file.unlink()
                outside = runtime / ('outside-' + file.name)
                outside.write_bytes(original)
                file.symlink_to(outside)
                with self.assertRaises(RuntimeError): helper.validate_backing_runtime(runtime)
                file.unlink()
                file.write_bytes(original)
            (runtime / 'test-filter-backing-root/Extra.hs').write_text('module Extra where\n')
            with self.assertRaises(RuntimeError): helper.validate_backing_runtime(runtime)

    def test_backing_closure_includes_missing_declared_files(self):
        names = qa.arm64_inputs(Path('/missing'), physical_context_owner_backing=True)
        self.assertEqual(set(helper.BACKING_SOURCE_HASHES),
                         {'ui/Warlock/Ui/FilterBackingRoot.hsc', 'test-filter-backing-root/Main.hs'})
        for name in helper.BACKING_SOURCE_HASHES:
            self.assertIn('implementation/warlock/haskell/runtime/' + name, names)
        self.assertIn('tools/haskell_test_wrapper.py', names)
        self.assertFalse(any(name.endswith('.elm') for name in names))

    def test_backing_noargs_addition_and_original26_ast_preserved(self):
        wrapper = ast.parse((ROOT / 'tools/haskell_test_wrapper.py').read_text())
        noargs = next(ast.literal_eval(node.value) for node in wrapper.body
                      if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'NOARGS'
                                                            for t in node.targets))
        self.assertEqual(noargs, EXPECTED_OLD_NOARGS | {'filter-backing-root-controls'})
        tree = ast.parse((ROOT / 'tools/test_physical_context_build.py').read_text())
        actual = {cls.name + '.' + node.name: hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
                  for cls in tree.body if isinstance(cls, ast.ClassDef) for node in cls.body
                  if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}
        for name, expected in EXPECTED_OLD_TEST_AST.items():
            self.assertEqual(actual[name], expected)



class ExtractedBridgeCallbackControls(unittest.TestCase):
    def extract_callback(self, backing, run, output, pin_image):
        import json
        import os
        from types import SimpleNamespace
        tree = ast.parse((ROOT / 'tools/check_arm64_cpu.py').read_text())
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
        callbacks = [node for node in ast.walk(main) if isinstance(node, ast.FunctionDef)
                     and node.name == 'execute_bridge_cpu']
        self.assertEqual(len(callbacks), 1)
        module = ast.fix_missing_locations(ast.Module(body=[callbacks[0]], type_ignores=[]))
        namespace = {'Path': Path, 'os': os, 'json': json, 'shutil': shutil, 'sys': sys,
                     'ROOT': ROOT, 'output': output, 'run': run, 'pin_image': pin_image,
                     'digest': lambda path: hashlib.sha256(path.read_bytes()).hexdigest(),
                     'env': {}, 'args': SimpleNamespace(physical_context_owner_bridge=not backing,
                                                       physical_context_owner_backing=backing)}
        exec(compile(module, '<extracted-reviewed-callback>', 'exec'), namespace)
        return namespace['execute_bridge_cpu']

    def test_unknown_suite_refused_before_any_effect(self):
        from unittest.mock import Mock
        run, pin = Mock(side_effect=AssertionError('unexpected run')), Mock(side_effect=AssertionError('unexpected pin'))
        for backing in (False, True):
            callback = self.extract_callback(backing, run, Path('/must-not-create'), pin)
            with self.assertRaises(RuntimeError):
                callback('not-a-fixed-suite', {}, Path('/must-not-use'))
        run.assert_not_called()
        pin.assert_not_called()

    def positive_callback(self, backing, suite, sentinel):
        import json
        import os
        with tempfile.TemporaryDirectory(prefix='extracted-bridge-callback-') as directory:
            output = Path(directory)
            (output / 'dist').mkdir()
            source = output / 'dist/source-fixture'
            source.write_bytes(b'not-executed-mock-image')
            def pin(path, root, name):
                stat = path.stat()
                return {'path': str(path), 'device': stat.st_dev, 'inode': stat.st_ino,
                        'size': stat.st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            calls = []
            def run(label, argv, stage, timeout, env):
                calls.append((label, argv, stage, timeout))
                dispatch = json.loads(Path(env['WARLOCK_HASKELL_DISPATCH']).read_text())
                self.assertEqual(len(dispatch['suites']), 1)
                copied, entry = next(iter(dispatch['suites'].items()))
                self.assertEqual(entry['suite'], suite)
                self.assertEqual(entry['test']['path'], copied)
                self.assertEqual(argv[-1], Path(copied))
                self.assertEqual(argv[:3], [sys.executable, '-B', ROOT / 'tools/haskell_test_wrapper.py'])
                runs = Path(entry['runRoot'])
                runs.mkdir(mode=0o700)
                log = runs / 'default.log'
                log.write_text(sentinel)
                (runs / 'results.json').write_text(json.dumps([{'mode': 'default', 'argv': [], 'exit': 0,
                    'timeout': False, 'forcedCleanup': False, 'log': str(log)}]))
            callback = self.extract_callback(backing, run, output, pin)
            result = callback(suite, pin(source, output / 'dist', suite), output / 'stage')
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][0], 'bridge-cpu-' + suite)
            self.assertEqual(calls[0][3], 240)
            self.assertTrue(result['normalExit'])
            self.assertTrue(result['noArguments'])
            self.assertEqual(result['copiedImage']['sha256'], result['originalImage']['sha256'])
            self.assertEqual((output / 'dist/bridge-cpu-images').stat().st_mode & 0o777, 0o700)

    def test_existing_bridge_positive_dispatch_remains(self):
        self.positive_callback(False, 'ui-engine-broker-controls',
            'engine broker socketpair controls passed; mock guard is not owned-process evidence\n')

    def test_backing_positive_dispatch_uses_exact_noargs_receipt(self):
        self.positive_callback(True, 'filter-backing-root-controls', 'filter-backing-root-controls: complete\n')


class JourneyBuildProfileControls(unittest.TestCase):
    def test_fixed_observer_and_affected_fixture_compile_only(self):
        self.assertEqual(helper.JOURNEY_TARGETS, helper.BACKING_TARGETS + (
            ('ux003-native-observer', 'warlock-runtime:exe:ux003-native-observer'),
            ('application-owner-route-controls', 'warlock-runtime:test:application-owner-route-controls')))
        output = Path('/private/compile-only')
        packet = {'cabal': '/sdk/cabal', 'ghcPrefix': '/sdk/ghc'}
        old = helper.backing_command_plan(packet, output, output / 'haskell')
        new = helper.journey_command_plan(packet, output, output / 'haskell')
        self.assertEqual([argv[2] for _, argv in new], ['build'] + ['list-bin'] * 9)
        self.assertEqual(new[0][1][:-9], old[0][1][:-7])
        self.assertEqual(new[0][1][-9:], [target for _, target in helper.JOURNEY_TARGETS])
        self.assertTrue(all(argv[:-1] == old[1][1][:-1] for _, argv in new[1:]))
        self.assertFalse(any(word in ('run', 'test', 'exec', 'repl') for _, argv in new for word in argv))
        self.assertEqual(helper.BACKING_BEHAVIOR_SUITES,
            ('ui-engine-protocol-controls', 'ui-engine-broker-controls', 'filter-backing-root-controls'))

    def test_journey_requires_same_protected_backing_callback(self):
        with self.assertRaises(RuntimeError):
            helper.run_profile('/missing', '/missing', {}, None, journey=True)
        with self.assertRaises(RuntimeError):
            helper.run_profile('/missing', '/missing', {}, None, bridge=True, journey=True)
        with self.assertRaises(RuntimeError):
            helper.run_profile('/missing', '/missing', {}, None, bridge=True, backing=True, journey=True)

    def test_journey_required_source_and_ordinary_component_drift_refused(self):
        with tempfile.TemporaryDirectory(prefix='journey-build-control-') as directory:
            runtime = Path(directory) / 'runtime'
            for name in {'runtime.cabal', *helper.SOURCE_HASHES, *helper.BRIDGE_SOURCE_HASHES,
                         *helper.BACKING_SOURCE_HASHES, *helper.JOURNEY_SOURCE_HASHES}:
                target = runtime / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'implementation/warlock/haskell/runtime' / name, target)
            helper.validate_journey_runtime(runtime)
            for name in helper.JOURNEY_SOURCE_HASHES:
                file = runtime / name
                original = file.read_bytes()
                file.unlink()
                with self.assertRaises(RuntimeError): helper.validate_journey_runtime(runtime)
                file.write_bytes(original + b'-- changed\n')
                with self.assertRaises(RuntimeError): helper.validate_journey_runtime(runtime)
                file.unlink()
                outside = runtime / ('outside-' + file.parent.name + '-' + file.name)
                outside.write_bytes(original)
                file.symlink_to(outside)
                with self.assertRaises(RuntimeError): helper.validate_journey_runtime(runtime)
                file.unlink(); file.write_bytes(original)
            extra = runtime / 'fixture-ux003-native-observer/Foreign.hs'
            extra.write_text('module Foreign where\n')
            with self.assertRaises(RuntimeError): helper.validate_journey_runtime(runtime)

    def test_journey_owning_closure_keeps_fixed_missing_source_names(self):
        names = qa.arm64_inputs(Path('/missing'), ux003_journey_build=True)
        for name in helper.JOURNEY_SOURCE_HASHES:
            self.assertIn('implementation/warlock/haskell/runtime/' + name, names)
        self.assertIn('tools/run_ux003_native_journey.py', names)
        self.assertIn('tools/test_ux003_native_journey.py', names)
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
