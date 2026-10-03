import unittest
from unittest.mock import patch
import qa_nested_backend as b

class BackendSelection(unittest.TestCase):
    def test_unscoped_refuses_before_inputs(self):
        with patch.object(b,'require_qa_scope',side_effect=RuntimeError('unscoped')),patch.object(b,'verify_library',side_effect=AssertionError('late')):
            with self.assertRaises(RuntimeError):b.command([], {})
    def test_bad_selection_and_drm_device_refused(self):
        for env in ({}, {'AQ_BACKENDS':'drm'}, {'AQ_BACKENDS':'wayland','AQ_DRM_DEVICES':'/dev/dri/card0'}):
            with patch.object(b,'require_qa_scope'),patch.object(b,'verify_library',side_effect=AssertionError('late')):
                with self.assertRaises(RuntimeError):b.command([],env)
    def test_loader_injection_refused(self):
        for key in ('LD_PRELOAD','LD_AUDIT'):
            with patch.object(b,'require_qa_scope'),patch.object(b,'verify_library',side_effect=AssertionError('late')):
                with self.assertRaises(RuntimeError):b.command([],{'AQ_BACKENDS':'wayland',key:'/unknown.so'})
    def test_dead_parent_refused(self):
        with patch.object(b,'require_qa_scope'),patch.object(b,'verify_runtime'),patch.object(b,'verify_parent',side_effect=RuntimeError('dead')),patch.object(b,'verify_library',side_effect=AssertionError('late')):
            with self.assertRaises(RuntimeError):b.command([],{'AQ_BACKENDS':'wayland','XDG_RUNTIME_DIR':'/private'})
    def test_compositor_only_child_exec_keeps_caller_env(self):
        env={'AQ_BACKENDS':'wayland','XDG_RUNTIME_DIR':'/private','LD_LIBRARY_PATH':'/graphics'};before=dict(env)
        with patch.object(b,'require_qa_scope'),patch.object(b,'verify_runtime'),patch.object(b,'verify_parent'),patch.object(b,'verify_library',return_value='/reviewed'):
            self.assertEqual(b.command(['--config','/private/a.lua'],env),['/usr/bin/env','LD_LIBRARY_PATH=/reviewed:/graphics','/usr/bin/Hyprland','--config','/private/a.lua'])
        self.assertEqual(env,before)
    def test_actual_read_only_backing_mapping_and_changed_hash(self):
        from pathlib import Path
        import hashlib
        import mmap
        library=b.STAGE/'prefix/lib/libaquamarine.so.0.15.0'
        expected=hashlib.sha256(library.read_bytes()).hexdigest()
        with library.open('rb') as source, mmap.mmap(source.fileno(),4096,access=mmap.ACCESS_READ):
            self.assertTrue(b.actual_mapping_matches(Path('/proc/self'),library,expected))
        with self.assertRaises(RuntimeError):b.actual_mapping_matches(Path('/proc/self'),library,'bad')
    def test_actual_frozen_private_library_verified(self):
        self.assertEqual(b.verify_library(),str(b.STAGE/'prefix/lib'))

if __name__=='__main__':unittest.main()
