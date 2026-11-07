#!/usr/bin/env python3
"""Pure controls for the fixed QA pointer builder; never invoke build tools."""
import argparse
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = None
helper = None
BASE = 'implementation/warlock/qa/native-runtime-helpers/'
ELF = '''ELF Header:
  Class:                             ELF64
  Data:                              2's complement, little endian
  Machine:                           AArch64
Program Headers:
      [Requesting program interpreter: /lib/ld-linux-aarch64.so.1]
Dynamic section:
 0x0000000000000001 (NEEDED) Shared library: [libwayland-client.so.0]
 0x0000000000000001 (NEEDED) Shared library: [libc.so.6]
'''


class PointerBuildTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for name in helper.SOURCE_PINS:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def test_actual_sources_and_protocol_are_accepted(self):
        helper.validate_sources(self.root)

    def test_drifted_pointer_source_refused(self):
        file = self.root / (BASE + 'virtual_pointer.c')
        file.write_bytes(file.read_bytes() + b'/* drift */\n')
        with self.assertRaises(RuntimeError):
            helper.validate_sources(self.root)

    def test_missing_xml_refused(self):
        (self.root / (BASE + 'wlr-virtual-pointer-unstable-v1.xml')).unlink()
        with self.assertRaises(RuntimeError):
            helper.validate_sources(self.root)

    def test_symlink_input_refused(self):
        file = self.root / (BASE + 'wlr-virtual-pointer-unstable-v1.xml')
        other = self.root / 'elsewhere.xml'
        file.rename(other)
        file.symlink_to(other)
        with self.assertRaises(RuntimeError):
            helper.validate_sources(self.root)

    def test_fixed_plan_is_two_generators_two_objects_and_link_only(self):
        plan = helper.command_plan(Path('/source'), Path('/private/output'))
        self.assertEqual([label for label, _ in plan], ['pointer-header', 'pointer-code', 'pointer-object', 'pointer-protocol-object', 'pointer-link'])
        self.assertEqual([argv[0] for _, argv in plan], ['/usr/bin/wayland-scanner', '/usr/bin/wayland-scanner', '/usr/bin/cc', '/usr/bin/cc', '/usr/bin/cc'])
        self.assertEqual(plan[0][1][1], 'client-header')
        self.assertEqual(plan[1][1][1], 'private-code')
        self.assertEqual(plan[0][1][2], plan[1][1][2])
        compile_argv = plan[2][1]
        self.assertEqual(plan[4][1][-2:], ['-lwayland-client', '-lm'])
        self.assertIn('-c', compile_argv)
        self.assertIn('/source/' + BASE + 'virtual_pointer.c', compile_argv)
        self.assertNotIn('ldd', ' '.join(compile_argv))

    def test_literal_arm_elf_metadata_accepts_exact_needed(self):
        self.assertEqual(helper.parse_elf(ELF), (['libwayland-client.so.0', 'libc.so.6'], '/lib/ld-linux-aarch64.so.1'))

    def test_exact_glibc_loader_needed_is_supported(self):
        text = ELF.replace('libwayland-client.so.0', 'ld-linux-aarch64.so.1')
        self.assertEqual(helper.parse_elf(text)[0], ['ld-linux-aarch64.so.1', 'libc.so.6'])

    def test_foreign_arch_and_endianness_refused(self):
        for old, new in [('AArch64', 'Advanced Micro Devices X86-64'), ('little endian', 'big endian'), ('ELF64', 'ELF32')]:
            with self.subTest(value=new):
                with self.assertRaises(RuntimeError):
                    helper.parse_elf(ELF.replace(old, new))

    def test_rpath_runpath_and_loader_injection_refused(self):
        for tag in ['RPATH', 'RUNPATH', 'AUDIT', 'DEPAUDIT', 'FILTER', 'AUXILIARY']:
            with self.subTest(tag=tag):
                with self.assertRaises(RuntimeError):
                    helper.parse_elf(ELF + ' 0x0 (' + tag + ') value\n')

    def test_foreign_loader_or_needed_path_refused(self):
        for text in [ELF.replace('/lib/ld-linux-aarch64.so.1', '/tmp/loader'), ELF.replace('libc.so.6', '../libc.so.6'), ELF.replace('libc.so.6', '/usr/lib/libc.so.6')]:
            with self.assertRaises(RuntimeError):
                helper.parse_elf(text)

    def test_duplicate_needed_or_interpreter_refused(self):
        for extra in [' 0x1 (NEEDED) Shared library: [libc.so.6]\n', ' [Requesting program interpreter: /usr/lib/ld-linux-aarch64.so.1]\n']:
            with self.assertRaises(RuntimeError):
                helper.parse_elf(ELF + extra)

    def test_make_dependencies_parse_actual_escaped_line_format(self):
        self.assertEqual(helper.dependency_names('pointer.o: /source/a.c \\\n /usr/include/stdint.h\n'), ['/source/a.c', '/usr/include/stdint.h'])
        with self.assertRaises(RuntimeError):
            helper.dependency_names('not-a-dependency-rule')

    def test_seeded_literal_mutations_never_admit_foreign_needed(self):
        import random
        generator = random.Random(20261107)
        for _ in range(24):
            name = generator.choice(['../', '/tmp/', '$ORIGIN/', 'bad name/']) + str(generator.randrange(1000))
            with self.subTest(name=name):
                with self.assertRaises(RuntimeError):
                    helper.parse_elf(ELF.replace('libc.so.6', name))


def main():
    global ROOT, helper
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    ROOT = args.root.resolve()
    sys.path.insert(0, str(ROOT / 'tools'))
    spec = importlib.util.spec_from_file_location('virtual_pointer_build', ROOT / 'tools/virtual_pointer_build.py')
    if spec is None or spec.loader is None:
        raise RuntimeError('missing fixed pointer helper')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    unittest.main(argv=[sys.argv[0]], verbosity=0)


if __name__ == '__main__':
    main()
