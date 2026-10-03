"""Real PNG descriptors and owned adapter cleanup across reserved staging scans."""
from contextlib import contextmanager
from copy import deepcopy
import os
import threading
import unittest
from unittest.mock import patch
import batch_preview
import test_batch_preview as base
from native_desktop import NativeDesktop

class StagingTests(unittest.TestCase):
    setUp=base.BatchTests.setUp
    tearDown=base.BatchTests.tearDown
    native_actor=base.BatchTests.native_actor
    def material(self,index=1):
        window=deepcopy(base.Desktop().windows[0]);window.update(address=hex(0x1000+index),stableId=index,pid=10000+index,size=[2,2],at=[0,0])
        epoch='abcdef123456-'+str(index);image=self.actor/(epoch+'.png')
        image.write_bytes(base.patterned_png(2,2));image.chmod(0o600)
        metadata=dict(rect=dict(x=0,y=0,width=2,height=2),pixels=[2,2],insets=dict(left=0,top=0,right=0,bottom=0))
        return window,epoch,image,metadata
    def adapter(self):
        actor=NativeDesktop.__new__(NativeDesktop);actor.root=self.actor;actor.preview_batch=self.batch;actor.janitor=lambda:None
        return actor
    @contextmanager
    def scan(self,args=None,invoke=None):
        args=args or self.material();entered=threading.Event();permit=threading.Event();errors=[];fds=[];original=os.pread
        def gated(fd,size,offset):
            if threading.current_thread().name=='reserved-material-scan' and not entered.is_set():
                fds.append(fd);entered.set()
                if not permit.wait(3):raise TimeoutError('test scan gate')
            return original(fd,size,offset)
        def run():
            try:(invoke or (lambda:self.batch.stage(*args)))()
            except BaseException as error:errors.append(error)
        worker=threading.Thread(target=run,name='reserved-material-scan')
        with patch.object(batch_preview.os,'pread',gated):
            worker.start()
            try:
                self.assertTrue(entered.wait(1));yield args,errors,fds
            finally:
                permit.set();worker.join(3);self.assertFalse(worker.is_alive())
        for fd in fds:
            with self.assertRaises(OSError):os.fstat(fd)
    def test_unrelated_actual_cleanup_and_new_receipt_complete_during_png_read(self):
        old=self.material(99)[2];actor=self.adapter();receipt=threading.RLock();cleaned=threading.Event();reserved=threading.Event();errors=[]
        def cleanup():
            try:
                with receipt:actor.release_sources([dict(path=str(old))]);cleaned.set()
            except BaseException as error:errors.append(error)
        def request():
            with receipt:reserved.set()
        threads=[]
        with self.scan() as (_,scan_errors,_):
            threads=[threading.Thread(target=cleanup),threading.Thread(target=request)]
            for t in threads:t.start()
            try:self.assertTrue(cleaned.wait(.5));self.assertTrue(reserved.wait(.5));self.assertFalse(old.exists())
            finally:
                for t in threads:t.join(1)
        self.assertFalse(scan_errors);self.assertFalse(errors);self.assertTrue(all(not t.is_alive() for t in threads));self.assertEqual(len(self.batch.pending),1)
    def test_exact_scanning_epoch_release_discard_dispose_and_helper_launch_refuse(self):
        actor=self.adapter()
        with self.scan() as (args,errors,_):
            epoch=args[1]
            for action in (lambda:actor.release_sources([dict(path=str(args[2]))]),lambda:self.batch.discard(epoch),self.batch.require_disposable,lambda:self.batch._reserve([],[])):
                with self.assertRaisesRegex(ValueError,'staging'):action()
            self.assertTrue(args[2].exists());self.assertEqual(set(self.batch.staging),{epoch});self.assertFalse(self.keeper.jobs)
        self.assertFalse(errors);actor.release_sources([dict(path=str(args[2]))]);self.batch.require_disposable()
    def test_pending_and_scanning_combined_capacity64_refuses65_before_open(self):
        for index in range(1,64):self.batch.stage(*self.material(index))
        with self.scan(self.material(64)) as (_,errors,_):
            with patch.object(batch_preview,'PinnedPNG',side_effect=AssertionError('capacity must refuse before material open')):
                with self.assertRaisesRegex(ValueError,'lifecycle unavailable'):self.batch.stage(*self.material(65))
            self.assertEqual(len(self.batch.pending)+len(self.batch.staging),64)
        self.assertFalse(errors);self.assertEqual(len(self.batch.pending),64);self.assertFalse(self.batch.staging)
    def test_duplicate_epoch_cannot_borrow_live_scan_reservation(self):
        with self.scan() as (args,errors,_):
            reservation=self.batch.staging[args[1]]
            with self.assertRaisesRegex(ValueError,'lifecycle unavailable'):self.batch.stage(*args)
            self.assertIs(self.batch.staging[args[1]],reservation)
        self.assertFalse(errors);self.assertEqual(len(self.batch.pending),1)
    def test_actual_failed_adapter_read_closes_fd_before_unreturned_epoch_cleanup(self):
        actor,window=self.native_actor();fds=[]
        def fail(fd,*args):fds.append(fd);raise OSError('actual gated material read failure')
        with patch.object(batch_preview.os,'pread',fail):
            with self.assertRaisesRegex(OSError,'material read failure'):actor.capture_source(window,'fedcba987654-1',0)
        self.assertEqual(len(fds),1)
        with self.assertRaises(OSError):os.fstat(fds[0])
        self.assertFalse(actor.preview_batch.staging);self.assertFalse(actor.preview_batch.pending)
        self.assertFalse(list(actor.root.glob('fedcba987654-*.png')));self.assertFalse(actor.preview_batch.quarantined)
    def test_changed_reservation_quarantines_exact_epoch_without_erasing_replacement(self):
        actor=self.adapter();old=self.material(99)[2]
        with self.scan() as (args,errors,_):
            with self.batch.lock:
                foreign=dict(serial=999,snapshot={'untrusted':True});self.batch.staging[args[1]]=foreign
        self.assertEqual(len(errors),1);self.assertRegex(str(errors[0]),'reservation changed')
        self.assertIs(self.batch.staging[args[1]],foreign);self.assertTrue(self.batch.quarantined);self.assertIn(args[1],self.batch.active_epochs)
        for action in (lambda:actor.release_sources([dict(path=str(args[2]))]),self.batch.require_disposable):
            with self.assertRaises(ValueError):action()
        actor.release_sources([dict(path=str(old))]);self.assertFalse(old.exists());self.assertTrue(args[2].exists())
    def test_unknown_lifecycle_during_scan_cannot_publish_material_or_clear_quarantine(self):
        with self.scan() as (args,errors,_):
            with self.batch.lock:self.batch.quarantined=True;self.batch.active_epochs.add(args[1])
        self.assertEqual(len(errors),1);self.assertRegex(str(errors[0]),'publication lifecycle unavailable')
        self.assertFalse(self.batch.staging);self.assertFalse(self.batch.pending);self.assertTrue(self.batch.quarantined)
        with self.assertRaises(ValueError):self.batch.discard(args[1])
    def test_png_identity_replacement_during_read_unwinds_only_owned_reservation(self):
        with self.scan() as (args,errors,_):
            original=args[2];renamed=original.with_suffix('.prior');original.rename(renamed);original.write_bytes(renamed.read_bytes());original.chmod(0o600)
        self.assertEqual(len(errors),1);self.assertRegex(str(errors[0]),'inode changed');self.assertFalse(self.batch.staging);self.assertFalse(self.batch.pending);self.assertFalse(self.batch.quarantined)
    def test_close_occurs_outside_lifecycle_before_epoch_becomes_releasable(self):
        args=self.material();observed=[];original=batch_preview.PinnedPNG.close
        def close(pin):
            if pin.fd is not None:
                acquired=threading.Event()
                def take():
                    with self.batch.lock:acquired.set()
                t=threading.Thread(target=take);t.start();ok=acquired.wait(.5);t.join(1)
                self.assertTrue(ok,'PNG close held lifecycle lock');self.assertIn(args[1],self.batch.staging)
                with self.assertRaisesRegex(ValueError,'staging'):self.batch.discard(args[1])
                observed.append(True)
            original(pin)
        with patch.object(batch_preview.PinnedPNG,'close',close):self.batch.stage(*args)
        self.assertEqual(observed,[True]);self.assertFalse(self.batch.staging);self.assertIn(args[1],self.batch.pending)

if __name__=='__main__':unittest.main()
