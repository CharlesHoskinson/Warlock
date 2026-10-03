import fcntl
import json
from pathlib import Path
import tempfile
import unittest
from service_runtime import RuntimeLease,atomic_write

class LeaseTests(unittest.TestCase):
    def release(self,lease):
        if lease.fd is not None:
            import os
            os.close(lease.fd);lease.fd=None
    def test_actual_held_inode_owner_and_exclusion_are_fresh(self):
        with tempfile.TemporaryDirectory() as raw:
            lease=RuntimeLease(raw,'offline')
            try:lease.verify()
            finally:lease.close()
    def test_replaced_lock_refuses_even_with_identical_owner_and_journal(self):
        with tempfile.TemporaryDirectory() as raw:
            lease=RuntimeLease(raw,'offline');lock=Path(raw)/'runtime.lock';lock.rename(lock.with_name('old.lock'));lock.write_bytes(b'');lock.chmod(0o600)
            try:
                with self.assertRaisesRegex(ValueError,'lock inode'):lease.verify()
            finally:self.release(lease)
    def test_copied_owner_in_replacement_root_cannot_restore_authority(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw)/'owned';root.mkdir(mode=0o700);lease=RuntimeLease(root,'offline');owner=(root/'owner.json').read_bytes();root.rename(root.with_name('old'));root.mkdir(mode=0o700)
            (root/'runtime.lock').write_bytes(b'');(root/'runtime.lock').chmod(0o600);(root/'owner.json').write_bytes(owner);(root/'owner.json').chmod(0o600)
            try:
                with self.assertRaisesRegex(ValueError,'root inode'):lease.verify()
            finally:self.release(lease)
    def test_same_inode_explicit_unlock_revokes_exclusion(self):
        with tempfile.TemporaryDirectory() as raw:
            lease=RuntimeLease(raw,'offline');fcntl.flock(lease.fd,fcntl.LOCK_UN)
            try:
                with self.assertRaisesRegex(ValueError,'no longer holds exclusion'):lease.verify()
            finally:self.release(lease)
    def test_changed_owner_nonce_cannot_write_or_recover(self):
        with tempfile.TemporaryDirectory() as raw:
            lease=RuntimeLease(raw,'offline');owner=dict(lease.owner,nonce='changed');atomic_write(lease.owner_path,json.dumps(owner).encode())
            try:
                with self.assertRaisesRegex(ValueError,'owner PID/start/nonce'):lease.verify()
            finally:self.release(lease)

if __name__=='__main__':unittest.main()
