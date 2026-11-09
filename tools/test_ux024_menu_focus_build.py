"""Source-first mocked fixed build contracts; never a compiler or GUI test."""
import argparse
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

class Controls(unittest.TestCase):
    def test_only_two_closed_build_targets_and_no_cabal_execution(self):
        rows=b.command_plan({'cabal':'/sdk/cabal','ghcPrefix':'/sdk/ghc'},Path('/private/out'),Path('/private/out/haskell'))
        self.assertEqual(rows[0][1][-2:],[target for _,target in b.TARGETS])
        self.assertEqual([row[1][2] for row in rows],['build']+['list-bin']*2)
        self.assertTrue(all('--offline' in row[1] and '--jobs=2' in row[1] for row in rows))
        self.assertFalse(any(word in ('test','run','repl','install','--allow-newer') for _,argv in rows for word in argv))
    def test_only_fixed_pure_allocation_branch_executes(self):
        images={name:{'path':'/images/'+name,'device':'1','inode':'2','size':'3','sha256':'a'*64} for name,_ in b.TARGETS}
        self.assertEqual(b.BEHAVIOR,('ui-webkit-controls',))
        self.assertEqual(b.behavior_command('ui-webkit-controls',images),['/images/ui-webkit-controls','--allocation-only'])
        self.assertEqual([target for _,target in b.TARGETS],['warlock-runtime:exe:warlock-ui-owner','warlock-runtime:test:ui-webkit-controls'])
        for name in ('warlock-ui-owner','ux003-native-observer','ui-engine-protocol-controls','ui-mvp-controls','unknown'):
            with self.assertRaises(ValueError):b.behavior_command(name,images)
    def test_source_tree_rejects_symlink_and_extra_membership(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);(root/'a.hs').write_text('a')
            expected=b.source_tree(root)
            (root/'new.hs').write_text('extra')
            with self.assertRaises(ValueError):b.require_source_tree(root,expected)
            (root/'new.hs').unlink();(root/'alias.hs').symlink_to(root/'a.hs')
            with self.assertRaises(ValueError):b.source_tree(root)
    def test_source_tree_rejects_actual_changed_body(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);(root/'a.hs').write_text('a');expected=b.source_tree(root)
            (root/'a.hs').write_text('b')
            with self.assertRaises(ValueError):b.require_source_tree(root,expected)
    def test_sandbox_hides_host_run_and_binds_source_readonly(self):
        argv=b.sandbox_command({'trees':{},'files':{},'systemInputs':'/sdk/system-build-inputs.json'},Path('/private/out'),'a'*64)
        self.assertIn(['--tmpfs','/run'],[argv[i:i+2] for i in range(len(argv)-1)])
        self.assertIn(['--dir','/run/user'],[argv[i:i+2] for i in range(len(argv)-1)])
        self.assertIn(['--ro-bind',str(b.ROOT),str(b.ROOT)],[argv[i:i+3] for i in range(len(argv)-2)])
        self.assertNotIn(['--ro-bind','/run','/run'],[argv[i:i+3] for i in range(len(argv)-2)])
        self.assertIn('--unshare-net',argv);self.assertIn('--unshare-pid',argv)
    def test_external_system_inventory_is_mounted_readonly(self):
        path='/home/hoskinson/.local/share/warlock-toolchain/system-build-inputs.json'
        argv=b.sandbox_command({'trees':{},'files':{},'systemInputs':path},Path('/private/out'),'a'*64)
        self.assertIn(['--ro-bind',path,path],[argv[i:i+3] for i in range(len(argv)-2)])
    def test_pinned_standard_inventory_alias_precedes_callback_import(self):
        import ast
        tree=ast.parse(Path(b.__file__).read_text())
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        alias=next(n.lineno for n in ast.walk(main) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Subscript) and isinstance(t.slice,ast.Constant) and t.slice.value=='arm64_toolchain' for t in n.targets))
        callback=next(n.lineno for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='load_module' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='fixed_build_elf_pin')
        self.assertLess(alias,callback)
    def test_reaped_leader_is_never_signalled(self):
        child=Mock();child.poll.return_value=0
        with patch.object(b.os,'killpg') as kill:b.stop_unreaped(child)
        kill.assert_not_called()
    def test_live_leader_timeout_is_explicit_forced_failure(self):
        child=Mock();child.poll.return_value=None;child.pid=123
        with patch.object(b.os,'killpg') as kill:
            self.assertTrue(b.stop_unreaped(child))
        kill.assert_called_once();child.wait.assert_called_once()
    def test_deadline_clips_to_authorization_and_never_extends(self):
        with patch.object(b.time,'monotonic_ns',return_value=100),patch.object(b.time,'time_ns',return_value=1000):
            self.assertEqual(b.left(200,1050),50/1e9)
            with self.assertRaises(TimeoutError):b.left(100,2000)
            with self.assertRaises(TimeoutError):b.left(200,1000)

    def test_retained_group_after_leader_reap_refuses_without_signalling(self):
        child=Mock();child.pid=123
        with patch.object(b.os,'killpg',return_value=None) as probe:
            with self.assertRaises(ValueError):b.require_group_absent(child)
        probe.assert_called_once_with(123,0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--module',required=True);a,rest=p.parse_known_args()
    spec=importlib.util.spec_from_file_location('fixed_display_build',a.module);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
    unittest.main(argv=[__file__,*rest])
