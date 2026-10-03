"""Real CPU sealed gate; initial readiness never releases target."""
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import fixture_legacy_ready as ready
from owned_commands import SealedFile
from recovery_resources import gated_process,verify_process

class LegacyReadinessTests(unittest.TestCase):
    def launch(self,record):
        with tempfile.TemporaryDirectory() as raw,SealedFile('/usr/bin/cat') as selected:
            env=dict(os.environ,XDG_RUNTIME_DIR=raw,HYPRLAND_INSTANCE_SIGNATURE='cpu-ready',WAYLAND_DISPLAY='never-connect')
            child=gated_process('/proc/self/fd/'+str(selected.fd),env=env,pass_fds=(selected.fd,),record=record,process_factory=ready.ready_process)
            try:
                child.stdin.write('actual sealed CPU target\n');child.stdin.flush();self.assertEqual(child.stdout.readline(),'actual sealed CPU target\n')
            finally:
                child.terminate();child.wait(timeout=2)
                for stream in (child.stdin,child.stdout,child.stderr):stream.close()
    def test_actual_live_initial_source_verified_before_gate_then_target_runs(self):
        seen=[]
        def record(row):
            self.assertTrue(ready.gate_phase(row));self.assertTrue(ready.observe_ready(row));self.assertEqual(verify_process(row),'gated');seen.append(row)
        self.launch(record);self.assertEqual(len(seen),1)
    def test_empty_kernel_observation_is_pending_not_acceptance_and_full_inverse(self):
        def record(row):
            original=Path.read_bytes
            def empty(path,*a,**kw):
                return b'' if str(path)==f'/proc/{row["pid"]}/environ' else original(path,*a,**kw)
            with patch.object(Path,'read_bytes',empty):self.assertFalse(ready.observe_ready(row))
            original_text=Path.read_text
            def startup(path,*a,**kw):return 'running' if str(path)==f'/proc/{row["pid"]}/syscall' else original_text(path,*a,**kw)
            with patch.object(Path,'read_text',startup):self.assertFalse(ready.observe_ready(row))
            def malformed(path,*a,**kw):return 'unknown record' if str(path)==f'/proc/{row["pid"]}/syscall' else original_text(path,*a,**kw)
            with patch.object(Path,'read_text',malformed),self.assertRaises(ValueError):ready.observe_ready(row)
            self.assertTrue(ready.observe_ready(row));self.assertEqual(verify_process(row),'gated')
        self.launch(record)
    def test_nonempty_mismatches_and_replaced_lifetime_source_never_ready(self):
        def record(row):
            original=Path.read_bytes
            for name,value in [('environ',b'XDG_RUNTIME_DIR=/wrong\0'),('cmdline',b'wrong\0')]:
                def mismatch(path,*a,**kw):return value if str(path)==f'/proc/{row["pid"]}/{name}' else original(path,*a,**kw)
                with patch.object(Path,'read_bytes',mismatch),self.assertRaises(ValueError):ready.observe_ready(row)
            bad=deepcopy(row);bad['start']+=1
            with self.assertRaises(ValueError):ready.observe_ready(bad)
            bad=deepcopy(row);bad['producer']['sha256']='0'*64
            with self.assertRaises(ValueError):ready.observe_ready(bad)
            self.assertTrue(ready.observe_ready(row));self.assertEqual(verify_process(row),'gated')
        self.launch(record)
    def test_expired_or_unknown_observation_never_counts_as_ready(self):
        def record(row):
            with self.assertRaises(TimeoutError):ready.wait_ready(row,time.monotonic()-1)
            with patch.object(Path,'read_bytes',side_effect=PermissionError('unknown kernel observation')),self.assertRaises(PermissionError):ready.observe_ready(row)
            self.assertTrue(ready.observe_ready(row));self.assertEqual(verify_process(row),'gated')
        self.launch(record)
