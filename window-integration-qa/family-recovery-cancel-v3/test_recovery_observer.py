"""Actual CPU-only recovery archival and partial/failure evidence faults."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
BASE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-recovery-terminal-v17')
sys.path.insert(0,str(BASE))
import test_recovery_runtime as inherited
from recovery_runtime import NativeRecovery
from service_runtime import RuntimeLease,unresolved
from recovery_observer import RecoveryArchive,retain_regular

class RecoveryArchiveTests(unittest.TestCase):
    def test_durable_cancel_archived_while_exact_sources_still_exist(self):
        with tempfile.TemporaryDirectory() as raw:
            f,s,d,a,b=inherited.RecoveryTests().fixture(raw);d.windows.pop(0);d.family=lambda w,windows,single=False:(deepcopy(windows),deepcopy(windows[-1]))
            lease=RuntimeLease(f.root,'offline')
            try:
                coordinator=NativeRecovery(f,store=s,desktop=d,lease_verify=lease.verify);archive=RecoveryArchive(coordinator,Path(raw)/'evidence');archive.attach();result=coordinator.recover(b)
            finally:lease.close()
            rows=[json.loads(p.read_text()) for p in archive.destination.glob('*/observation.json')]
            acknowledgments=[r for r in rows if any(p.get('cancellation',{}).get('acknowledged') for p in r['body'].get('recovery',{}).get('plans',[])) and any(x['exists'] for x in r['resources'])]
            self.assertTrue(acknowledgments);self.assertTrue(all(r['resources'][0]['files'] for r in acknowledgments));self.assertTrue(any(r['phase']=='before-dispose' for r in rows));self.assertTrue(any(r['phase']=='after-dispose' and not r['resources'][0]['exists'] for r in rows))
            self.assertFalse(unresolved(result));self.assertFalse(d.commits)
    def test_failed_real_persist_never_creates_acknowledgment_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            f,s,d,a,b=inherited.RecoveryTests().fixture(raw);lease=RuntimeLease(f.root,'offline');coordinator=NativeRecovery(f,store=s,desktop=d,lease_verify=lease.verify)
            def refuse():raise OSError('actual fsync refused')
            coordinator.persist=refuse;archive=RecoveryArchive(coordinator,Path(raw)/'evidence');archive.attach()
            try:
                with self.assertRaisesRegex(OSError,'actual fsync'):coordinator.persist()
            finally:lease.close()
            self.assertEqual(list(archive.destination.iterdir()),[]);self.assertTrue(a.exists())
    def test_mismatched_readback_persists_raw_error_before_assertion(self):
        with tempfile.TemporaryDirectory() as raw:
            f,s,d,a,b=inherited.RecoveryTests().fixture(raw);lease=RuntimeLease(f.root,'offline');coordinator=NativeRecovery(f,store=s,desktop=d,lease_verify=lease.verify);coordinator.body=deepcopy(b);coordinator.body['serial']+=1
            archive=RecoveryArchive(coordinator,Path(raw)/'evidence')
            try:
                with self.assertRaisesRegex(ValueError,'durable coordinator'):archive.snapshot('fault')
            finally:lease.close()
            evidence=json.loads(next(archive.destination.glob('*/observation.json')).read_text());self.assertIn('error',evidence);self.assertTrue(Path(evidence['journal']['retained']).is_file());self.assertFalse(evidence['nativeAuthority'])
    def test_unknown_symlink_material_is_never_followed(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);outside=root/'outside';outside.write_bytes(b'secret');outside.chmod(0o600);selected=root/'symlink';selected.symlink_to(outside)
            with self.assertRaises(OSError):retain_regular(selected,root/'retained')
            self.assertFalse((root/'retained').exists())
    def test_descriptor_relative_read_retains_selected_directory_not_rebound_path(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);owned=root/'owned';owned.mkdir(mode=0o700);source=owned/'source';source.write_bytes(b'original');source.chmod(0o600);fd=os.open(owned,os.O_RDONLY|os.O_DIRECTORY)
            try:
                owned.rename(root/'old');owned.mkdir(mode=0o700);source.write_bytes(b'replacement');source.chmod(0o600)
                result=retain_regular(source,root/'retained',dir_fd=fd)
            finally:os.close(fd)
            self.assertEqual((root/'retained').read_bytes(),b'original');self.assertNotEqual(result['inode'],source.stat().st_ino)
    def test_unsafe_mode_or_bound_never_becomes_retained_proof(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);p=root/'source';p.write_bytes(b'123456');p.chmod(0o644)
            with self.assertRaises(ValueError):retain_regular(p,root/'one')
            p.chmod(0o600)
            with self.assertRaises(ValueError):retain_regular(p,root/'two',limit=3)
            self.assertFalse((root/'one').exists());self.assertFalse((root/'two').exists())

if __name__=='__main__':unittest.main()
