"""Static ELF manifest refusal controls. No native image is executed."""
import unittest
import json
from arm64_native_stage import elf_header, readelf_dependencies, approved_runpath, library_recipe


def header(machine=183):
    data = bytearray(64)
    data[:7] = b'\x7fELF\x02\x01\x01'
    data[16:18] = (3).to_bytes(2, 'little')
    data[18:20] = machine.to_bytes(2, 'little')
    return bytes(data)


class NativeStageContractTests(unittest.TestCase):
    def test_elf64_little_aarch64_is_explicit(self):
        self.assertEqual(elf_header(header()), {'class': 'ELF64', 'byteOrder': 'little', 'machine': 'AArch64', 'type': 3})

    def test_wrong_architecture_or_truncated_image_refuses(self):
        for data in (header(62), header()[:20], b'#!/bin/sh\n'):
            with self.assertRaises(ValueError):
                elf_header(data)

    def test_literal_needed_and_loader_are_retained(self):
        text = (' 0x0000000000000001 (NEEDED) Shared library: [libc.so.6]\n'
                ' 0x0000000000000001 (NEEDED) Shared library: [libgtk-4.so.1]\n'
                ' [Requesting program interpreter: /lib/ld-linux-aarch64.so.1]\n')
        self.assertEqual(readelf_dependencies(text), (['libc.so.6', 'libgtk-4.so.1'], '/lib/ld-linux-aarch64.so.1'))

    def test_literal_usr_lib_interpreter_is_retained(self):
        text = ' [Requesting program interpreter: /usr/lib/ld-linux-aarch64.so.1]\n'
        self.assertEqual(readelf_dependencies(text), ([], '/usr/lib/ld-linux-aarch64.so.1'))

    def test_cross_alias_duplicate_interpreters_remain_ambiguous(self):
        for first, second in (('/lib/ld-linux-aarch64.so.1', '/usr/lib/ld-linux-aarch64.so.1'),
                              ('/usr/lib/ld-linux-aarch64.so.1', '/lib/ld-linux-aarch64.so.1')):
            with self.subTest(first=first), self.assertRaises(ValueError):
                readelf_dependencies('[Requesting program interpreter: ' + first + ']\n'
                                     '[Requesting program interpreter: ' + second + ']\n')

    def test_dynamic_library_without_interpreter_is_not_fabricated(self):
        self.assertEqual(readelf_dependencies('Dynamic section: no NEEDED entries\n'), ([], None))

    def test_duplicate_or_path_qualified_needed_refuses(self):
        for text in ('(NEEDED) Shared library: [libc.so.6]\n(NEEDED) Shared library: [libc.so.6]\n',
                     '(NEEDED) Shared library: [/tmp/libc.so.6]\n',
                     '(NEEDED) Shared library: [../libc.so.6]\n'):
            with self.assertRaises(ValueError):
                readelf_dependencies(text)

    def test_rpath_and_foreign_loader_are_not_implicitly_qualified(self):
        for text in ('(RUNPATH) Library runpath: [$ORIGIN]\n', '(RPATH) Library rpath: [/tmp]\n',
                     '[Requesting program interpreter: /tmp/loader]\n'):
            with self.assertRaises(ValueError):
                readelf_dependencies(text)

    def test_multiple_interpreters_are_ambiguous(self):
        with self.assertRaises(ValueError):
            readelf_dependencies('[Requesting program interpreter: /lib/ld-linux-aarch64.so.1]\n' * 2)


class ExactRunpathRecipeTests(unittest.TestCase):
    SQLITE = ('/usr/lib/libsqlite3.so.3.54.1', '3009375a8361a58b6f7e75cd66ab706d218aeff37d30c26501170f29154ef6e2')
    JPEG = ('/usr/lib/libjpeg.so.8.3.2', '2d500d82dd923ed8c91ab6029aa7b733f7bcda7e46160f7e53fd19e16dbbefab')
    TINY = ('/usr/lib/libtinysparql-3.0.so.0.1200.0', '4794555fcee7375ad8c75e7bb31c9afff001b227190cd1c6d62d02cdbb6571d7')

    def test_exact_three_reviewed_image_hash_runpaths(self):
        for image, digest in (self.SQLITE, self.JPEG):
            self.assertEqual(approved_runpath('(RUNPATH) Library runpath: [/usr/lib]\n', image, digest), ('/usr/lib',))
            self.assertEqual(readelf_dependencies('(NEEDED) Shared library: [libc.so.6]\n(RUNPATH) Library runpath: [/usr/lib]\n', image, digest), (['libc.so.6'], None))
        self.assertEqual(approved_runpath('(RUNPATH) Library runpath: [/usr/lib/tinysparql-3.0]\n', *self.TINY), ('/usr/lib/tinysparql-3.0',))
        self.assertEqual(readelf_dependencies('(NEEDED) Shared library: [libc.so.6]\n(RUNPATH) Library runpath: [/usr/lib/tinysparql-3.0]\n', *self.TINY), (['libc.so.6'], None))

    def test_same_path_changed_hash_refuses(self):
        with self.assertRaises(ValueError):
            approved_runpath('(RUNPATH) Library runpath: [/usr/lib]\n', self.SQLITE[0], '0' * 64)

    def test_same_hash_foreign_path_refuses(self):
        with self.assertRaises(ValueError):
            approved_runpath('(RUNPATH) Library runpath: [/usr/lib]\n', '/tmp/libsqlite3.so', self.SQLITE[1])

    def test_changed_empty_or_additional_runpath_refuses(self):
        for paths in ('', '/tmp', '/usr/lib:', '/usr/lib:/tmp', '$ORIGIN'):
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                approved_runpath('(RUNPATH) Library runpath: [' + paths + ']\n', *self.SQLITE)

    def test_duplicate_or_malformed_runpath_refuses(self):
        for text in ('(RUNPATH) Library runpath: [/usr/lib]\n' * 2, '(RUNPATH) malformed\n'):
            with self.assertRaises(ValueError):
                approved_runpath(text, *self.SQLITE)

    def test_rpath_still_refused_even_for_reviewed_hash(self):
        with self.assertRaises(ValueError):
            approved_runpath('(RPATH) Library rpath: [/usr/lib]\n', *self.SQLITE)

    def test_private_runpath_requires_specific_absence_before_default(self):
        self.assertEqual(library_recipe('libc.so.6', ('/usr/lib/tinysparql-3.0',)),
                         ('/usr/lib/libc.so.6', ['/usr/lib/tinysparql-3.0/libc.so.6']))
        self.assertEqual(library_recipe('libc.so.6', ('/usr/lib',)), ('/usr/lib/libc.so.6', []))

    def test_unknown_runpath_or_nonbasename_needed_has_no_recipe(self):
        for name, paths in (('libc.so.6', ('/tmp',)), ('../libc.so.6', ())):
            with self.assertRaises(ValueError):
                library_recipe(name, paths)


class SeededStaticRefusalContracts(unittest.TestCase):
    def test_seed20261107_foreign_arch_and_invalid_needed_paths(self):
        state = 20261107
        invalid = ('../libc.so.6', '/usr/lib/libc.so.6', 'a/b.so', 'libc.so.6:', 'libc\n.so', 'libc\x00.so')
        for index in range(32):
            state = (1664525 * state + 1013904223) & 0xffffffff
            machine = state % 65536
            if machine == 183:
                machine = 184
            bad_name = invalid[(state >> 16) % len(invalid)]
            with self.subTest(seed=20261107, index=index, state=state, machine=machine):
                with self.assertRaises(ValueError):
                    elf_header(header(machine))
                with self.assertRaises(ValueError):
                    library_recipe(bad_name, ())
        print(json.dumps({'kind': 'native-static-refusal-contracts', 'seed': 20261107,
                          'cases': 32, 'foreignArchitectureRefusals': 32,
                          'invalidNeededPathRefusals': 32, 'imageExecuted': False}, sort_keys=True))


if __name__ == '__main__':
    unittest.main()
