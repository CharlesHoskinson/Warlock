#!/usr/bin/env python3
"""Pure fixed-build refusal controls; never execute a compiler."""
import argparse
import importlib.util
from pathlib import Path
import tempfile
import unittest

class Controls(unittest.TestCase):
    def test_fixed_target(self):
        plan=M.command_plan(Path('/repo/prefix'),Path('/out'))
        self.assertEqual(plan[1][1][-4:],['--target','aquamarine','--parallel','1'])
    def test_no_install_or_test_target(self):
        self.assertEqual(len(M.command_plan(Path('/prefix'),Path('/out'))),2)
        self.assertNotIn('install',M.command_plan(Path('/prefix'),Path('/out'))[1][1])
    def test_no_user_options(self):
        with self.assertRaises(TypeError):M.command_plan(Path('/p'),Path('/o'),['-DOVERRIDE=1'])
    def test_parent_path(self):
        with self.assertRaises(RuntimeError):M.safe_relative('../outside')
    def test_absolute_path(self):
        with self.assertRaises(RuntimeError):M.safe_relative('/usr/bin/cc')
    def test_empty_path(self):
        with self.assertRaises(RuntimeError):M.safe_relative('')
    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'real').write_text('x');(p/'alias').symlink_to('real')
            with self.assertRaises(RuntimeError):M.plain(p,'alias')
    def test_plain_regular(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'real').write_text('x');self.assertEqual(M.plain(p,'real'),p/'real')
    def test_wrong_hash(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x';p.write_text('actual')
            with self.assertRaises(RuntimeError):M.check_entry(p,{'sha256':'0'*64,'mode':0o644})
    def test_changed_mode(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x';p.write_text('actual');p.chmod(0o600)
            with self.assertRaises(RuntimeError):M.check_entry(p,{'sha256':M.digest(p),'mode':0o644})
    def test_alias_exact(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x';p.symlink_to('one')
            M.check_entry(p,{'link':'one'})
            with self.assertRaises(RuntimeError):M.check_entry(p,{'link':'two'})
    def test_closed_tree_rejects_new_input(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'one').write_text('x')
            M.closed_tree(p,{str(p/'one')})
            (p/'two').write_text('new')
            with self.assertRaises(RuntimeError):M.closed_tree(p,{str(p/'one')})
    def test_closed_empty_search_prefix(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);M.closed_tree(p,set())
            (p/'injected.h').write_text('new')
            with self.assertRaises(RuntimeError):M.closed_tree(p,set())
    def test_unknown_entry(self):
        with self.assertRaises(RuntimeError):M.check_entry(Path('/no'),{'unknown':True})

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True,type=Path);args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('aquamarine_build',args.root/'tools/aquamarine_build.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
    unittest.main(argv=['controls'])
