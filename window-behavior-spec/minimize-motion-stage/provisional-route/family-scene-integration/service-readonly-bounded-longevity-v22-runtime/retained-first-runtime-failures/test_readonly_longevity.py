"""Real kernel Unix peers, immutable FD material, and fsync/journal fault boundaries."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import threading
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

import readonly_ipc
from readonly_archive import ArchiveStore, encoded, segment_chain
from readonly_ipc import ReadonlyIPC, digest, seal_predecessor, validate_storage
from service_runtime import RuntimeLease
import test_readonly_ipc as inherited


class LongevityKernelTests(unittest.TestCase):
    setUp = inherited.ReadonlyKernelTests.setUp
    tearDown = inherited.ReadonlyKernelTests.tearDown
    query = inherited.ReadonlyKernelTests.query
    row = inherited.ReadonlyKernelTests.row

    def seed(self):
        self.assertEqual(self.query(), b'[]')
        self.assertEqual(self.query(), b'[]')
        self.records.clear()

    def capacity(self):
        return patch.object(readonly_ipc, 'MAX_HISTORY', 2)

    def validate(self, value=None):
        return validate_storage(value or self.reader.snapshot(), root=self.root,
                                environment=self.reader.issuer['environment'], guard=self.guard)

    def test_exact_orphan_predecessor_reseal_under_new_actual_lease(self):
        self.seed(); old = self.reader.snapshot()
        first = seal_predecessor(old,root=self.root,environment=old['issuer']['environment'],
                                 guard=self.guard,lease_verify=self.lease.verify)
        self.lease.close(); self.lease = RuntimeLease(self.root,self.session)
        self.assertNotEqual(self.lease.nonce,old['issuer']['nonce'])
        second = seal_predecessor(old,root=self.root,environment=old['issuer']['environment'],
                                  guard=self.guard,lease_verify=self.lease.verify)
        self.assertEqual(first,second)
        self.assertEqual(self.reader.archive.read(second)['ledger'],old)
        self.assertEqual(self.store.read()['readonlyOwnership'],old)

    def test_partial_existing_predecessor_refuses_without_old_journal_replacement(self):
        self.seed(); old = self.reader.snapshot(); before = self.store.read()
        first = seal_predecessor(old,root=self.root,environment=old['issuer']['environment'],
                                 guard=self.guard,lease_verify=self.lease.verify)
        path = self.reader.archive.path / first['name']
        with path.open('r+b') as stream:stream.seek(0);stream.write(b'!');stream.flush();os.fsync(stream.fileno())
        self.lease.close(); self.lease = RuntimeLease(self.root,self.session)
        with self.assertRaises(ValueError):
            seal_predecessor(old,root=self.root,environment=old['issuer']['environment'],
                             guard=self.guard,lease_verify=self.lease.verify)
        self.assertEqual(self.store.read(),before)

    def test_existing_predecessor_fsync_fault_never_authorizes_new_journal(self):
        self.seed(); old = self.reader.snapshot(); before = self.store.read()
        seal_predecessor(old,root=self.root,environment=old['issuer']['environment'],
                         guard=self.guard,lease_verify=self.lease.verify)
        self.lease.close(); self.lease = RuntimeLease(self.root,self.session)
        with patch('readonly_archive.os.fsync',side_effect=OSError('existing predecessor fsync fault')):
            with self.assertRaisesRegex(OSError,'fsync'):
                seal_predecessor(old,root=self.root,environment=old['issuer']['environment'],
                                 guard=self.guard,lease_verify=self.lease.verify)
        self.assertEqual(self.store.read(),before)

    def test_synthetic_predecessor_lease_callback_never_seals(self):
        self.seed(); old = self.reader.snapshot()
        with self.assertRaisesRegex(ValueError,'actual selected'):
            seal_predecessor(old,root=self.root,environment=old['issuer']['environment'],
                             guard=self.guard,lease_verify=lambda:None)
        self.assertEqual(list(self.reader.archive.path.iterdir()),[])

    def test_issuer_changes_during_archive_write_keep_full_old_journal(self):
        self.seed(); before = self.store.read(); original = self.reader.archive.write
        owner = deepcopy(self.lease.owner)
        def replace(body):
            pointer = original(body)
            self.lease.owner['nonce']='b'*32;self.lease.publish_owner()
            return pointer
        self.reader.archive.write = replace
        try:
            with self.capacity():
                with self.assertRaises(ValueError):self.query()
            self.assertEqual(self.reader.tip,None)
            self.assertEqual(len(self.reader.rows),2)
            self.assertEqual(self.store.read(),before)
            self.assertTrue(self.reader.fault)
        finally:self.lease.owner=owner;self.lease.publish_owner()

    def test_still_valid_new_owner_replacement_during_predecessor_seal_refuses(self):
        self.seed(); old = self.reader.snapshot(); before = self.store.read()
        owner = deepcopy(self.lease.owner); nonce = self.lease.nonce
        original = ArchiveStore.write
        def replace(store, body, **options):
            pointer = original(store,body,**options)
            self.lease.nonce='c'*32;self.lease.owner['nonce']=self.lease.nonce;self.lease.publish_owner()
            self.lease.verify()  # Individually valid replacement is insufficient.
            return pointer
        try:
            with patch.object(ArchiveStore,'write',replace):
                with self.assertRaisesRegex(ValueError,'current owner changed'):
                    seal_predecessor(old,root=self.root,environment=old['issuer']['environment'],
                                     guard=self.guard,lease_verify=self.lease.verify)
            self.assertEqual(self.store.read(),before)
        finally:self.lease.nonce=nonce;self.lease.owner=owner;self.lease.publish_owner()

    def test_actual_keeper_first_startup_publication_keeps_lineage_before_reader(self):
        from native_runtime import NativeFactory
        from service_runtime import RuntimeService,JournalStore
        root=self.runtime/'hypr-window-motion'/'startup'
        root.parent.mkdir(mode=0o700);root.mkdir(mode=0o700)
        executable=self.runtime/'owned-cpu-target';executable.write_bytes(Path('/usr/bin/cat').read_bytes());executable.chmod(0o500)
        expected=hashlib.sha256(executable.read_bytes()).hexdigest()
        def factory():
            with patch.dict(os.environ,self.env):
                return NativeFactory(root,self.guard,producer=executable,producer_hash=expected,
                                     core=executable,core_hash=expected)
        snapshots=[];original=JournalStore.write
        def record(store,body):
            original(store,body)
            if store.root==root:snapshots.append(deepcopy(body))
        with patch.object(JournalStore,'write',record):
            first_factory=factory();first=RuntimeService(root,self.session,first_factory,lambda:None)
            try:
                self.assertEqual(first_factory.readonly.query(b'j/clients',list,1,1),b'[]')
            finally:first.close()
            old=first.store.read()['readonlyOwnership'];snapshots.clear()
            second_factory=factory();second=RuntimeService(root,self.session,second_factory,lambda:None)
            try:
                pending=[body for body in snapshots if body['helperOwnership'] is not None and
                         body['readonlyOwnership'] is None]
                self.assertTrue(pending)
                self.assertTrue(all(body['readonlyPredecessor'] is not None for body in pending))
                selected=pending[0]['readonlyPredecessor']
                self.assertEqual(second_factory.readonly.predecessor,selected)
                self.assertEqual(second_factory.readonly.archive.read(selected)['ledger'],old)
                self.assertEqual(second_factory.readonly.rows,{})
            finally:second.close()
        lease=RuntimeLease(root,self.session)
        try:
            third=factory();third.bind_lease(lease.verify)
            third.validate_readonly_previous(pending[0])
            self.assertEqual(third.readonly_predecessor,selected)
            self.assertIsNone(third.readonly_previous)
            path=root/'readonly-ledger'/selected['name']
            with path.open('r+b') as stream:stream.seek(0);stream.write(b'!');stream.flush();os.fsync(stream.fileno())
            fourth=factory();fourth.bind_lease(lease.verify)
            with self.assertRaises(ValueError):fourth.validate_readonly_previous(pending[0])
            self.assertIsNone(fourth.keeper)
            self.assertIsNone(fourth.readonly)
        finally:lease.close()

    def test_hardlink_alias_refuses_without_fault_reset(self):
        self.seed()
        with self.capacity(): self.query()
        path = self.reader.archive.path / self.reader.tip['name']
        os.link(path, path.with_name('hardlink'))
        with self.assertRaisesRegex(ValueError, 'identity'): self.query()
        self.assertTrue(self.reader.fault)

    def test_unpublished_refusal_is_retained_raw_and_not_reclaimed(self):
        self.handler = lambda c,d:c.sendall(b'[{')
        with self.assertRaises(ValueError): self.query()
        retained = self.reader.snapshot()
        retained['history'][0]['published'] = False
        pointer = seal_predecessor(retained, root=self.root, environment=self.reader.issuer['environment'],
                                   guard=self.guard, lease_verify=self.lease.verify)
        self.assertEqual(self.reader.archive.read(pointer)['ledger'], retained)
        self.assertFalse(self.reader.archive.read(pointer)['ledger']['history'][0]['published'])
        self.assertEqual(self.reader.archive.read(pointer)['ledger']['history'][0]['outcome'], 'refused')
        # A segment carrying the identical unpublished row must be rejected.
        row = retained['history'][0]
        bad = self.reader.archive.write({'version':1,'kind':'segment','issuerSHA256':digest(retained['issuer']),
            'epoch':1,'previous':None,'rows':[row],'first':1,'last':1})
        candidate = deepcopy(retained); candidate['history']=[]; candidate['epoch']=1; candidate['archiveTip']=bad
        with self.assertRaisesRegex(ValueError, 'unfinished'): self.validate(candidate)

    def test_real_child_crash_after_durable_tip_restarts_with_exact_new_lifetime(self):
        from service_runtime import JournalStore, process_start
        root = self.runtime / 'restart-service'; root.mkdir(mode=0o700)
        script = r'''import json,os,sys
from pathlib import Path
from copy import deepcopy
import readonly_ipc
from readonly_ipc import ReadonlyIPC
from native_runtime import NativeSession
from service_runtime import RuntimeLease,JournalStore,process_start
root=Path(sys.argv[1]);session=sys.argv[2];pid=int(sys.argv[3]);start=int(sys.argv[4])
env=json.loads(sys.argv[5]);lease=RuntimeLease(root,session)
guard=NativeSession(session,pid,start,'cpu-wayland',env);store=JournalStore(root,session);serial=0
readonly_ipc.MAX_HISTORY=2
def record(body):
 global serial
 lease.verify();serial+=1
 store.write({'version':1,'session':session,'snapshot':serial,'scenes':[],'pending':[],
              'readonlyOwnership':deepcopy(body)})
 if body['archiveTip'] is not None:os._exit(73)
reader=ReadonlyIPC(root,guard,lease.verify,record)
for _ in range(3):reader.query(b'j/clients',list,1,1)
raise AssertionError('crash point not reached')
'''
        run = subprocess.run([sys.executable,'-B','-c',script,str(root),self.session,str(os.getpid()),
                              str(process_start(os.getpid())),json.dumps(self.env)],
                             cwd=Path(__file__).parent, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode,73,run.stdout+run.stderr)
        journal = JournalStore(root,self.session)
        old = journal.read()['readonlyOwnership']
        self.assertIsNone(process_start(old['issuer']['pid']))
        self.assertEqual(old['history'],[])
        self.assertEqual(old['serial'],2)
        lease = RuntimeLease(root,self.session)
        serial = journal.read()['snapshot']
        try:
            self.assertNotEqual(lease.nonce,old['issuer']['nonce'])
            self.assertNotEqual(os.getpid(),old['issuer']['pid'])
            pointer = seal_predecessor(old,root=root,environment=old['issuer']['environment'],
                                       guard=self.guard,lease_verify=lease.verify)
            def record(body):
                nonlocal serial
                lease.verify();serial+=1
                journal.write({'version':1,'session':self.session,'snapshot':serial,'scenes':[],
                               'pending':[],'readonlyOwnership':deepcopy(body)})
            fresh = ReadonlyIPC(root,self.guard,lease.verify,record,predecessor=pointer)
            self.assertEqual(fresh.rows,{})
            self.assertEqual(fresh.archive.read(pointer)['ledger'],old)
            self.assertEqual(fresh.query(b'j/clients',list,1,1),b'[]')
            self.assertEqual(fresh.serial,1)
            self.assertEqual(len(fresh.rows),1)
            fresh.assert_closed()
        finally:lease.close()

    def test_genuine_640_queries_exceed_original_512_without_discard_or_replay(self):
        for serial in range(1, 641):
            self.assertEqual(self.query(), b'[]')
            self.assertEqual(self.reader.serial, serial)
            self.assertLessEqual(len(self.reader.rows), 512)
            self.records.clear()  # Only the test's redundant in-memory recording is dropped.
        self.assertEqual(self.control.requests.count(b'j/clients'), 640)
        self.assertEqual(self.reader.epoch, 1)
        archived = segment_chain(self.reader.archive, self.reader.tip, issuer=digest(self.reader.issuer),
                                 epoch=1, validate_rows=lambda rows: None)
        self.assertEqual(len(archived), 512)
        self.assertEqual([r['serial'] for r in archived], list(range(1, 513)))
        self.assertTrue(all(r['closed'] and r['published'] and r['outcome'] == 'complete' for r in archived))
        self.assertEqual([r['serial'] for r in self.reader.rows.values()], list(range(513, 641)))
        self.assertEqual(self.validate(), self.store.read()['readonlyOwnership'])
        self.reader.assert_closed()

    def test_pending_actual_connection_survives_disjoint_closed_reclamation(self):
        waiting = threading.Event(); release = threading.Event(); errors = []
        def slow(c, d):
            if d == b'j/clients': waiting.set(); release.wait(2)
            c.sendall(b'[]')
        self.handler = slow
        def worker():
            try: self.query(timeout=2)
            except BaseException as e: errors.append(e)
        with self.capacity():
            thread = threading.Thread(target=worker); thread.start()
            self.assertTrue(waiting.wait(1))
            try:
                self.assertEqual(self.query(b'j/monitors'), b'[]')
                pending = deepcopy(self.reader.rows['00000000000000000000000000000001'])
                self.assertEqual(self.query(b'j/workspaces'), b'[]')
                self.assertEqual(self.reader.rows[pending['id']], pending)
                self.assertIn(pending['id'], self.reader.references)
                archived = self.reader.archive.read(self.reader.tip)['rows']
                self.assertEqual([r['serial'] for r in archived], [2])
            finally: release.set(); thread.join(2)
        self.assertEqual(errors, [])
        self.assertFalse(thread.is_alive())
        self.assertEqual(self.reader.references, set())
        self.assertEqual(self.reader.rows[pending['id']]['outcome'], 'complete')

    def test_live_postdisk_confirmation_reference_cannot_be_reclaimed(self):
        reached = threading.Event(); release = threading.Event(); errors = []
        original = self.reader.authority
        def blocked():
            if threading.current_thread().name == 'held-result' and self.reader.rows and self.row()['outcome'] == 'complete':
                reached.set(); release.wait(2)
            return original()
        self.reader.authority = blocked
        def worker():
            try: self.query(timeout=2)
            except BaseException as e: errors.append(e)
        with self.capacity():
            thread = threading.Thread(target=worker, name='held-result'); thread.start()
            self.assertTrue(reached.wait(1))
            try:
                held = next(iter(self.reader.rows))
                with self.assertRaisesRegex(ValueError, 'normal shutdown'):self.reader.assert_closed()
                self.assertEqual(self.query(b'j/monitors'), b'[]')
                self.assertEqual(self.query(b'j/workspaces'), b'[]')
                self.assertIn(held, self.reader.rows)
                self.assertIn(held, self.reader.references)
                self.assertNotIn(held, [r['id'] for r in self.reader.archive.read(self.reader.tip)['rows']])
            finally: release.set(); thread.join(2)
        self.assertEqual(errors, [])
        self.assertEqual(self.reader.references, set())

    def test_all_actual_pending_connections_refuse_capacity_before_new_send(self):
        waiting = threading.Event(); release = threading.Event(); count = []; errors = []
        def slow(c,d):
            count.append(d)
            if len(count) == 2: waiting.set()
            release.wait(2); c.sendall(b'[]')
        self.handler = slow
        def worker(wire):
            try: self.query(wire, timeout=2)
            except BaseException as e: errors.append(e)
        with self.capacity():
            threads = [threading.Thread(target=worker, args=(w,)) for w in (b'j/clients', b'j/monitors')]
            for t in threads: t.start()
            self.assertTrue(waiting.wait(1))
            before = len(count)
            try:
                with self.assertRaisesRegex(ValueError, 'reclaimable'): self.query(b'j/workspaces')
                self.assertEqual(len(count), before)
                self.assertTrue(self.reader.fault)
                self.assertEqual(self.reader.tip, None)
                self.assertEqual(len(self.reader.rows), 2)
            finally:
                release.set()
                for t in threads: t.join(2)
        self.assertEqual(len(errors), 2)  # Latched failure prevents their late data return.
        self.assertTrue(all(r['closed'] and r['outcome'] == 'refused' for r in self.reader.rows.values()))

    def test_archive_io_block_does_not_hold_service_reservation_or_row_lock(self):
        self.seed(); reached = threading.Event(); release = threading.Event(); errors = []
        original = self.reader.archive.write
        def blocked(body): reached.set(); release.wait(2); return original(body)
        self.reader.archive.write = blocked
        def worker():
            try: self.query(timeout=2)
            except BaseException as e: errors.append(e)
        with self.capacity():
            thread = threading.Thread(target=worker); thread.start(); self.assertTrue(reached.wait(1))
            try:
                self.assertTrue(self.lock.acquire(timeout=.2)); self.lock.release()
                self.assertTrue(self.reader.lock.acquire(timeout=.2)); self.reader.lock.release()
            finally: release.set(); thread.join(2)
        self.assertFalse(thread.is_alive()); self.assertEqual(errors, [])

    def test_concurrent_new_row_survives_archive_plan_and_tip_commit(self):
        self.seed(); reached = threading.Event(); release = threading.Event(); errors = []
        original = self.reader.archive.write
        def blocked(body): reached.set(); release.wait(2); return original(body)
        self.reader.archive.write = blocked
        def worker():
            try: self.reader.rotate_closed(lambda: 2)
            except BaseException as e: errors.append(e)
        with patch.object(readonly_ipc, 'MAX_HISTORY', 3):
            # Proactive rotation leaves genuine capacity for a disjoint new query.
            thread = threading.Thread(target=worker); thread.start(); self.assertTrue(reached.wait(1))
            try:
                self.assertEqual(self.query(b'j/monitors'), b'[]')
            finally: release.set(); thread.join(2)
        self.assertEqual(errors, [])
        self.assertEqual([r['serial'] for r in self.reader.rows.values()], [3])
        self.validate()

    def test_closed_refusal_archives_without_becoming_returned_data(self):
        self.handler = lambda c,d:c.sendall(b'[{')
        with self.assertRaises(ValueError): self.query()
        self.handler = lambda c,d:c.sendall(b'[]')
        self.query()
        with self.capacity(): self.query()
        first = self.reader.archive.read(self.reader.tip)['rows'][0]
        self.assertEqual(first['outcome'], 'refused')
        self.assertEqual(first['evidence']['replyBytes'], 2)
        self.assertIsNotNone(first['error'])
        self.validate()

    def test_archive_file_fsync_fault_retains_old_journal_and_prevents_send(self):
        self.seed(); before = self.store.read(); sent = self.control.requests.count(b'j/clients')
        with self.capacity(), patch('readonly_archive.os.fsync', side_effect=OSError('archive fsync fault')):
            with self.assertRaisesRegex(OSError, 'fsync'): self.query()
        self.assertEqual(self.store.read(), before)
        self.assertEqual(self.reader.tip, None)
        self.assertEqual(len(self.reader.rows), 2)
        self.assertEqual(self.control.requests.count(b'j/clients'), sent)
        self.assertTrue(self.reader.fault)

    def test_archive_directory_fsync_fault_keeps_unreferenced_orphan(self):
        self.seed(); before = self.store.read(); actual = os.fsync; count = []
        def fail(fd):
            count.append(fd)
            if len(count) == 2: raise OSError('parent fsync fault')
            return actual(fd)
        with self.capacity(), patch('readonly_archive.os.fsync', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'parent'): self.query()
        self.assertEqual(self.store.read(), before)
        self.assertEqual(len(list(self.reader.archive.path.iterdir())), 1)
        self.assertEqual(self.reader.tip, None)

    def test_archive_readback_fault_never_publishes_tip(self):
        self.seed(); before = self.store.read()
        with self.capacity(), patch.object(self.reader.archive, 'read', side_effect=ValueError('readback fault')):
            with self.assertRaisesRegex(ValueError, 'readback'): self.query()
        self.assertEqual(self.store.read(), before)
        self.assertEqual(self.reader.tip, None)

    def test_failed_tip_publication_preserves_old_memory_and_disk(self):
        self.seed(); before = self.store.read()
        def fail(body):
            if body['archiveTip'] is not None: raise OSError('tip publication fault')
        self.writer_fault = fail
        with self.capacity():
            with self.assertRaisesRegex(OSError, 'tip'): self.query()
        self.assertEqual(self.store.read(), before)
        self.assertEqual(self.reader.tip, None)
        self.assertEqual(len(self.reader.rows), 2)
        self.assertTrue(self.reader.fault)

    def test_journal_published_then_writer_crashes_retains_verifiable_disk_tip(self):
        self.seed(); original = self.reader.record
        def crash(body):
            original(body)
            if body['archiveTip'] is not None: raise OSError('after durable tip crash')
        self.reader.record = crash
        with self.capacity():
            with self.assertRaisesRegex(OSError, 'durable tip'): self.query()
        self.assertEqual(len(self.reader.rows), 2)
        self.assertEqual(self.reader.tip, None)
        disk = self.store.read()['readonlyOwnership']
        self.assertEqual(disk['history'], [])
        self.assertEqual(disk['epoch'], 1)
        self.assertEqual(self.validate(disk), disk)
        self.assertTrue(self.reader.fault)

    def test_tip_published_before_in_memory_reclamation(self):
        self.seed(); original = self.reader.record; observed = []
        def observe(body):
            if body['archiveTip'] is not None and not observed:
                self.assertEqual(len(self.reader.rows), 2)
                self.assertEqual(self.reader.tip, None)
                original(body)
                self.assertEqual(self.store.read()['readonlyOwnership'], body)
                self.assertEqual(len(self.reader.rows), 2)
                observed.append(True)
            else: original(body)
        self.reader.record = observe
        with self.capacity(): self.query()
        self.assertEqual(observed, [True])
        self.assertEqual(len(self.reader.rows), 1)

    def test_actual_valid_file_replacement_and_hardlink_alias_refuse(self):
        self.seed()
        with self.capacity(): self.query()
        path = self.reader.archive.path / self.reader.tip['name']
        saved = path.with_name('held-original')
        data = path.read_bytes(); path.rename(saved); path.write_bytes(data); path.chmod(0o600)
        sent = self.control.requests.count(b'j/clients')
        with self.assertRaisesRegex(ValueError, 'identity'): self.query()
        self.assertEqual(self.control.requests.count(b'j/clients'), sent)
        self.assertTrue(self.reader.fault)

    def test_corrupt_archive_bytes_even_with_stable_inode_refuse(self):
        self.seed()
        with self.capacity(): self.query()
        path = self.reader.archive.path / self.reader.tip['name']
        with path.open('r+b') as file:
            file.seek(0); file.write(b'!'); file.flush(); os.fsync(file.fileno())
        with self.assertRaisesRegex(ValueError, 'bytes'): self.query()
        self.assertTrue(self.reader.fault)

    def test_missing_or_wrong_epoch_digest_tip_refuses(self):
        self.seed()
        with self.capacity(): self.query()
        body = self.reader.snapshot()
        for key, changed in [('epoch', 2), ('serial', 4)]:
            bad = deepcopy(body); bad[key] = changed
            with self.assertRaises(ValueError): self.validate(bad)
        bad = deepcopy(body); bad['archiveTip']['sha256'] = '0' * 64
        with self.assertRaises(ValueError): self.validate(bad)
        (self.reader.archive.path / self.reader.tip['name']).unlink()
        with self.assertRaises(FileNotFoundError): self.query()

    def test_valid_archive_directory_replacement_refuses(self):
        self.seed(); path = self.reader.archive.path; old = path.with_name('old-ledger')
        path.rename(old); path.mkdir(mode=0o700)
        with self.assertRaisesRegex(ValueError, 'directory'): self.query()
        self.assertTrue(self.reader.fault)

    def test_predecessor_preserves_pending_without_publishing_completion_or_replay(self):
        reached = threading.Event(); release = threading.Event(); errors = []
        def slow(c,d): reached.set(); release.wait(2); c.sendall(b'[]')
        self.handler = slow
        def worker():
            try: self.query(timeout=2)
            except BaseException as e: errors.append(e)
        thread = threading.Thread(target=worker); thread.start(); self.assertTrue(reached.wait(1))
        try:
            retained = self.store.read()['readonlyOwnership']
            pointer = seal_predecessor(retained, root=self.root, environment=self.reader.issuer['environment'],
                                       guard=self.guard, lease_verify=self.lease.verify)
            sealed = self.reader.archive.read(pointer)
            self.assertEqual(sealed['ledger'], retained)
            self.assertEqual(sealed['ledger']['history'][0]['outcome'], 'pending')
            self.assertIsNone(sealed['ledger']['history'][0]['evidence'])
        finally: release.set(); thread.join(2)
        self.assertEqual(errors, [])
        self.assertEqual(self.reader.serial, 1)

    def test_new_actual_lease_nonce_empty_current_ledger_keeps_full_predecessor(self):
        self.seed()
        with self.capacity(): self.query()
        old = self.reader.snapshot(); nonce = self.lease.nonce
        self.reader.assert_closed(); self.lease.close(); self.lease = RuntimeLease(self.root, self.session)
        self.assertNotEqual(self.lease.nonce, nonce)
        pointer = seal_predecessor(old, root=self.root, environment=old['issuer']['environment'],
                                   guard=self.guard, lease_verify=self.lease.verify)
        def write(body):
            self.lease.verify(); self.serial += 1
            self.store.write({'version':1,'session':self.session,'snapshot':self.serial,'scenes':[],
                              'pending':[],'readonlyOwnership':deepcopy(body)})
        fresh = ReadonlyIPC(self.root, self.guard, self.lease.verify, write,
                            reservation_lock=self.lock, predecessor=pointer)
        self.assertEqual(fresh.rows, {})
        self.assertEqual(fresh.serial, 0)
        self.assertNotEqual(digest(fresh.issuer), digest(old['issuer']))
        self.assertEqual(fresh.archive.read(pointer)['ledger'], old)
        self.assertEqual(fresh.query(b'j/clients', list, 1, 1), b'[]')
        self.assertEqual(len(fresh.rows), 1)
        self.assertEqual(self.control.requests.count(b'j/clients'), 4)
        fresh.assert_closed()


if __name__ == '__main__': unittest.main()
