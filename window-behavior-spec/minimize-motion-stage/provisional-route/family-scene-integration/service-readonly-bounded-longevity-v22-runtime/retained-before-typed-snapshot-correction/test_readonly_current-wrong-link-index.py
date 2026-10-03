"""Real CPU Unix peers, sealed FDs, archive files and original query deadlines."""
from copy import deepcopy
import fcntl
import hashlib
import mmap
import os
from pathlib import Path
import threading
import time
import unittest
from unittest.mock import patch

import test_readonly_ipc as kernel_fixture
from readonly_current import CurrentReadWitness, SealedData
from readonly_ipc import ReadonlyIPC, validate_storage


class BoundedReadTests(unittest.TestCase):
    setUp=kernel_fixture.ReadonlyKernelTests.setUp
    query=kernel_fixture.ReadonlyKernelTests.query
    row=kernel_fixture.ReadonlyKernelTests.row
    def tearDown(self):
        self.reader.current.close(force=True)
        kernel_fixture.ReadonlyKernelTests.tearDown(self)
    def rotate(self):
        deadline=time.monotonic()+1
        def remaining():
            left=deadline-time.monotonic()
            if left<=0:raise TimeoutError('actual maintenance absolute deadline')
            return left
        self.reader.rotate_closed(remaining)
    def segmented(self,count=2):
        for _ in range(count):self.query();self.rotate()
    def test_current_witness_is_distinct_from_full_history_authority(self):
        self.query();proof=self.reader._current_authority()
        self.assertIs(type(proof),CurrentReadWitness)
        self.assertIsInstance(self.reader.authority(),str)
        self.assertFalse(hasattr(proof,'nativeAuthority'))
    def test_older_corruption_may_not_affect_fresh_bytes_but_fails_full_audit(self):
        self.segmented();older=self.reader.current.latest.verify(self.reader.archive,self.reader.current.directory_fd)['previous']
        path=self.reader.archive.path/older['name'];data=path.read_bytes();path.write_bytes(b'x'+data[1:])
        self.assertEqual(self.query(),b'[]')
        with self.assertRaises(ValueError):self.reader.audit_history()
        self.assertTrue(self.reader.fault)
    def test_older_corruption_fails_normal_close(self):
        self.segmented();older=self.reader.current.latest.verify(self.reader.archive,self.reader.current.directory_fd)['previous']
        path=self.reader.archive.path/older['name'];data=path.read_bytes();path.write_bytes(b'x'+data[1:])
        with self.assertRaises(ValueError):self.reader.assert_closed()
        self.assertFalse(self.reader.current.closed)
    def test_older_corruption_fails_fresh_binding_before_any_new_send(self):
        self.segmented();older=self.reader.current.latest.verify(self.reader.archive,self.reader.current.directory_fd)['previous']
        path=self.reader.archive.path/older['name'];data=path.read_bytes();path.write_bytes(b'x'+data[1:])
        with self.assertRaises(ValueError):validate_storage(self.reader.snapshot(),root=self.root,environment=self.reader.issuer['environment'],guard=self.guard)
    def test_latest_corruption_refuses_before_connection(self):
        self.segmented(1);path=self.reader.archive.path/self.reader.tip['name'];data=path.read_bytes();path.write_bytes(b'x'+data[1:])
        before=self.control.requests.count(b'j/clients')
        with self.assertRaises(ValueError):self.query()
        self.assertEqual(self.control.requests.count(b'j/clients'),before)
    def test_valid_same_byte_sealed_owner_fd_replacement_refuses(self):
        anchor=self.reader.current.anchor;clone=SealedData('valid-replacement',anchor.value)
        old=anchor.fd;anchor.fd=clone.fd
        try:
            with self.assertRaises(ValueError):self.query()
            self.assertTrue(self.reader.fault)
        finally:anchor.fd=old;clone.close()
    def test_valid_tip_token_fd_replacement_refuses(self):
        tip=self.reader.current.latest;clone=SealedData('valid-token-replacement',tip.token.value)
        old=tip.token.fd;tip.token.fd=clone.fd
        try:
            with self.assertRaises(ValueError):self.query()
        finally:tip.token.fd=old;clone.close()
    def test_same_file_dup_fd_replacement_refuses_even_when_inodes_match(self):
        self.segmented(1);tip=self.reader.current.latest;old=tip.fd;duplicate=os.dup(old);os.set_inheritable(duplicate,False);tip.fd=duplicate
        try:
            with self.assertRaises(ValueError):self.query()
        finally:tip.fd=old;os.close(duplicate)
    def test_tip_fd_capture_cannot_be_replaced_with_updated_mutable_metadata(self):
        from readonly_current import fd_material
        self.segmented(1);tip=self.reader.current.latest;old=tip.fd;expected=tip.expected
        duplicate=os.dup(old);os.set_inheritable(duplicate,False);tip.fd=duplicate;tip.expected=fd_material(duplicate)
        try:
            with self.assertRaisesRegex(ValueError,'capture changed'):self.query()
        finally:tip.fd=old;tip.expected=expected;os.close(duplicate)
    def test_descriptor_access_flags_changed_refuse(self):
        fd=self.reader.current.anchor.fd;old=fcntl.fcntl(fd,fcntl.F_GETFL);fcntl.fcntl(fd,fcntl.F_SETFL,old|os.O_NONBLOCK)
        try:
            with self.assertRaises(ValueError):self.query()
        finally:fcntl.fcntl(fd,fcntl.F_SETFL,old)
    def test_executable_mapping_alias_refuses_actual_current_fd(self):
        fd=self.reader.current.anchor.fd
        mapping=mmap.mmap(fd,0,flags=mmap.MAP_PRIVATE,prot=mmap.PROT_READ|mmap.PROT_EXEC,trackfd=False)
        try:
            with self.assertRaisesRegex(ValueError,'executable alias'):self.query()
        finally:mapping.close()
    def test_held_query_survives_owned_append_and_old_fd_retires_after_finally(self):
        self.query();waiting=threading.Event();release=threading.Event();result=[];errors=[]
        def hold(c,d):waiting.set();release.wait(1);c.sendall(b'[]')
        self.handler=hold
        def worker():
            try:result.append(self.query())
            except BaseException as e:errors.append(e)
        old=self.reader.current.latest;thread=threading.Thread(target=worker);thread.start();self.assertTrue(waiting.wait(1))
        try:
            self.rotate();self.assertIsNot(self.reader.current.latest,old);self.assertIn(old,self.reader.current.tips)
            self.assertEqual(len(self.reader.rows),1);self.assertGreater(old.references,0)
        finally:release.set();thread.join(2)
        self.assertFalse(thread.is_alive());self.assertEqual(errors,[]);self.assertEqual(result,[b'[]'])
        self.assertNotIn(old,self.reader.current.tips);self.assertEqual(old.token.fd,-1)
    def test_borrowed_old_tip_corruption_refuses_reply_after_owned_append(self):
        self.segmented(1);self.query();waiting=threading.Event();release=threading.Event();errors=[];returns=[]
        self.handler=lambda c,d:(waiting.set(),release.wait(1),c.sendall(b'[]'))
        def worker():
            try:returns.append(self.query())
            except BaseException as e:errors.append(e)
        old=self.reader.current.latest;thread=threading.Thread(target=worker);thread.start();self.assertTrue(waiting.wait(1))
        try:
            self.rotate();path=self.reader.archive.path/old.pointer['name'];data=path.read_bytes();path.write_bytes(b'x'+data[1:])
        finally:release.set();thread.join(2)
        self.assertFalse(thread.is_alive());self.assertTrue(errors);self.assertEqual(returns,[])
        self.assertEqual(self.row()['outcome'],'refused')
    def test_durable_publication_then_adoption_failure_keeps_memory_rows_and_exact_disk_tip(self):
        self.query();snapshot=self.reader.snapshot();original=self.reader.current.adopt
        def fail(*args):raise OSError('adoption fault after durable publication')
        self.reader.current.adopt=fail
        with self.assertRaisesRegex(OSError,'adoption fault'):self.rotate()
        self.assertEqual(self.reader.rows,{r['id']:r for r in snapshot['history']});self.assertIsNone(self.reader.tip)
        disk=self.store.read()['readonlyOwnership'];self.assertEqual(disk['epoch'],1);self.assertEqual(disk['history'],[])
        validate_storage(disk,root=self.root,environment=self.reader.issuer['environment'],guard=self.guard)
        self.assertTrue(self.reader.fault);self.reader.current.adopt=original
    def test_publication_fault_does_not_adopt_or_reclaim_and_releases_prepared_fds(self):
        self.query();before=set(os.listdir('/proc/self/fd'));rows=deepcopy(self.reader.rows)
        self.writer_fault=lambda body:(_ for _ in ()).throw(OSError('publication fault')) if body['archiveTip'] else None
        with self.assertRaisesRegex(OSError,'publication fault'):self.rotate()
        self.assertEqual(self.reader.rows,rows);self.assertIsNone(self.reader.tip)
        self.assertEqual(set(os.listdir('/proc/self/fd')),before)
    def test_repeated_archives_do_not_accumulate_unborrowed_descriptors(self):
        initial=set(os.listdir('/proc/self/fd'))
        for _ in range(16):self.query();self.rotate();self.assertEqual(len(self.reader.current.tips),1)
        after=set(os.listdir('/proc/self/fd'));self.assertLessEqual(len(after),len(initial)+1)
        self.reader.assert_closed();self.assertTrue(self.reader.current.closed)
    def test_new_query_cannot_use_closed_current_proof(self):
        self.query();self.reader.assert_closed();before=self.control.requests.count(b'j/clients')
        with self.assertRaises(ValueError):self.query()
        self.assertEqual(self.control.requests.count(b'j/clients'),before)

    def test_unregistered_borrow_slots_are_bounded_before_new_connection(self):
        import readonly_ipc
        old_capacity=readonly_ipc.MAX_HISTORY;readonly_ipc.MAX_HISTORY=2
        release=threading.Event();events=[threading.Event(),threading.Event()];threads=[];errors=[]
        original=self.reader.ensure_capacity
        def ensure(remaining):
            name=threading.current_thread().name
            if name.startswith('pre-register-'):
                events[int(name.rsplit('-',1)[1])].set();release.wait(remaining())
            return original(remaining)
        def worker():
            try:self.query()
            except BaseException as e:errors.append(e)
        self.reader.ensure_capacity=ensure
        try:
            for i in range(2):
                self.query(b'j/monitors')
                thread=threading.Thread(target=worker,name=f'pre-register-{i}');threads.append(thread);thread.start()
                self.assertTrue(events[i].wait(.3));self.rotate()
            before=self.control.requests.count(b'j/workspaces')
            self.assertEqual(self.reader.current.borrowers,2)
            with self.assertRaisesRegex(ValueError,'reclaimable'):self.query(b'j/workspaces')
            self.assertEqual(self.control.requests.count(b'j/workspaces'),before)
            self.assertEqual(self.reader.current.borrowers,2)
            self.assertLessEqual(len(self.reader.current.tips),3)
            self.assertTrue(self.reader.fault)
        finally:
            release.set()
            for thread in threads:thread.join(2)
            readonly_ipc.MAX_HISTORY=old_capacity
        self.assertEqual(len(errors),2);self.assertEqual(self.reader.current.borrowers,0)
        self.assertTrue(all(not(t.is_alive()) for t in threads))
        self.assertEqual(len(self.reader.current.tips),1)

    def test_normal_close_refuses_archive_operation_until_exact_adoption(self):
        self.query();reached=threading.Event();release=threading.Event();errors=[]
        original=self.reader.archive.write
        def block(body):reached.set();release.wait(1);return original(body)
        self.reader.archive.write=block
        def worker():
            try:self.rotate()
            except BaseException as e:errors.append(e)
        thread=threading.Thread(target=worker);thread.start();self.assertTrue(reached.wait(.3))
        try:
            with self.assertRaisesRegex(ValueError,'append incomplete; normal shutdown'):self.reader.assert_closed()
            self.assertFalse(self.reader.current.closed)
        finally:release.set();thread.join(2)
        self.assertEqual(errors,[]);self.assertFalse(thread.is_alive())
        self.reader.assert_closed();self.assertTrue(self.reader.current.closed)

    def assert_refused_before_send(self):
        before=self.control.requests.count(b'j/clients')
        with self.assertRaises(ValueError):self.query()
        self.assertEqual(self.control.requests.count(b'j/clients'),before)
        self.assertTrue(self.reader.fault)
        self.assertEqual(self.reader.current.borrowers,0)
        self.assertEqual(sum(t.references for t in self.reader.current.tips),0)
    def test_bool_epoch_cannot_alias_integer_zero(self):
        self.reader.epoch=False
        with self.assertRaises(ValueError):validate_storage(self.reader.snapshot(),root=self.root,environment=self.reader.issuer['environment'],guard=self.guard)
        self.assert_refused_before_send()
    def test_bool_serial_cannot_alias_integer_zero(self):
        self.reader.serial=False
        self.assert_refused_before_send()
    def test_false_like_fault_cannot_alias_literal_false(self):
        self.reader.fault=''
        self.assert_refused_before_send()
    def test_float_version_cannot_alias_exact_integer_version(self):
        original=self.reader.snapshot
        def malformed():
            result=original();result['version']=2.0;return result
        self.reader.snapshot=malformed
        self.assert_refused_before_send()
    def test_missing_snapshot_field_refuses_current_proof(self):
        original=self.reader.snapshot
        def malformed():
            result=original();del result['predecessor'];return result
        self.reader.snapshot=malformed
        self.assert_refused_before_send()
    def test_extra_snapshot_field_refuses_current_proof(self):
        original=self.reader.snapshot
        def malformed():
            result=original();result['extra']=True;return result
        self.reader.snapshot=malformed
        self.assert_refused_before_send()
    def test_bool_tip_epoch_cannot_alias_authenticated_integer_one(self):
        self.segmented(1);self.reader.tip['epoch']=True
        self.assert_refused_before_send()
    def test_bool_tip_link_identity_cannot_alias_authenticated_integer_one(self):
        self.segmented(1)
        self.assertEqual(self.reader.tip['identity'][-1],1)
        self.reader.tip['identity'][-1]=True
        self.assert_refused_before_send()
    def test_bool_captured_fd_flag_cannot_alias_integer_one(self):
        self.reader.current.anchor.expected['fdFlags']=True
        self.assert_refused_before_send()
    def test_borrow_without_owned_query_frame_refuses_without_descriptor_reference_leak(self):
        before=self.control.requests.count(b'j/clients')
        with self.assertRaisesRegex(ValueError,'owned live query frame'):
            self.reader._current_authority(borrow=True)
        self.assertEqual(self.control.requests.count(b'j/clients'),before)
        self.assertEqual(self.reader.current.borrowers,0)
        self.assertEqual(sum(t.references for t in self.reader.current.tips),0)
