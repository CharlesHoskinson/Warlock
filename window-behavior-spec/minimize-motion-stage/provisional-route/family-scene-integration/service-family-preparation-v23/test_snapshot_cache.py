import copy
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import types
import unittest
from snapshot_cache import SnapshotCache
import production_motion_6d9 as native
from native_desktop import NativeDesktop
from test_capture_lease import png
from test_scene_controller import Desktop,rectangle,key

class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='sc-');self.root=Path(self.temp.name);self.d=Desktop();self.w=self.d.windows[0]
        self.pixels=png(*self.w['size'])
        self.metadata={'whole':True,'canonical':True,'identity':list(key(self.w)),'clientSize':self.w['size'],'rect':rectangle(self.w),'insets':dict(left=0,top=0,right=0,bottom=0),'pixels':self.w['size']}
        self.cache=SnapshotCache(self.root/'cache',native.Desktop.validate_snapshot)
    def tearDown(self):self.temp.cleanup()
    def test_minimized_exact_identity_cache_survives_new_actor_directory(self):
        self.cache.publish(self.w,self.metadata,self.pixels)
        fresh=SnapshotCache(self.root/'cache',native.Desktop.validate_snapshot)
        minimized=copy.deepcopy(self.w);minimized['workspace']['name']='special:win-minimized'
        metadata,pixels=fresh.restore(minimized)
        self.assertEqual(pixels,self.pixels);self.assertEqual(metadata['cacheDigest'],hashlib.sha256(self.pixels).hexdigest())
        self.assertEqual(metadata['identity'],list(key(self.w)))
    def test_same_address_pid_or_stable_id_reuse_cannot_import_cache(self):
        self.cache.publish(self.w,self.metadata,self.pixels)
        for change in ({'pid':self.w['pid']+1},{'stableId':'ee55'},{'address':'0xee55'}):
            reused=dict(self.w,**change)
            with self.assertRaises((ValueError,FileNotFoundError)):self.cache.restore(reused)
    def test_actual_png_replacement_and_dimension_drift_refuse_restore(self):
        self.cache.publish(self.w,self.metadata,self.pixels);path=self.cache.root/json.loads((self.cache.root/(self.cache.stem(self.w)+'.json')).read_text())['cacheFile']
        path.write_bytes(png(*self.w['size'])+b'changed')
        with self.assertRaisesRegex(ValueError,'digest'):self.cache.restore(self.w)
        path.unlink()
        self.cache.publish(self.w,self.metadata,self.pixels)
        drift=copy.deepcopy(self.w);drift['at'][0]+=1
        with self.assertRaisesRegex(ValueError,'geometry'):self.cache.restore(drift)
    def test_symlink_cache_file_never_reads_foreign_pixels(self):
        self.cache.publish(self.w,self.metadata,self.pixels);path=self.cache.root/json.loads((self.cache.root/(self.cache.stem(self.w)+'.json')).read_text())['cacheFile']
        other=self.root/'other';other.write_bytes(self.pixels);path.unlink();path.symlink_to(other)
        with self.assertRaises(OSError):self.cache.restore(self.w)
    def test_concurrent_pair_publications_always_read_one_complete_exact_digest(self):
        alternate=png(*self.w['size'])+b'valid-trailing-png-data'
        self.cache.publish(self.w,self.metadata,self.pixels);failures=[]
        def writer():
            try:
                for i in range(20):self.cache.publish(self.w,self.metadata,self.pixels if i%2 else alternate)
            except Exception as error:failures.append(error)
        thread=threading.Thread(target=writer);thread.start()
        for i in range(20):
            metadata,pixels=self.cache.restore(self.w)
            self.assertIn(pixels,(self.pixels,alternate));self.assertEqual(metadata['cacheDigest'],hashlib.sha256(pixels).hexdigest())
        thread.join(2);self.assertFalse(thread.is_alive());self.assertFalse(failures)
    def test_metadata_commit_failure_keeps_previous_complete_pair_restorable(self):
        self.cache.publish(self.w,self.metadata,self.pixels)
        prior_pointer=(self.cache.root/(self.cache.stem(self.w)+'.json')).read_bytes()
        original=self.cache.write_atomic
        def fail_pointer(path,data):
            if path.suffix=='.json':raise OSError('injected metadata commit failure')
            return original(path,data)
        self.cache.write_atomic=fail_pointer
        with self.assertRaisesRegex(OSError,'metadata commit'):self.cache.publish(self.w,self.metadata,self.pixels+b'new-png-tail')
        self.assertEqual((self.cache.root/(self.cache.stem(self.w)+'.json')).read_bytes(),prior_pointer)
        self.assertEqual(self.cache.restore(self.w)[1],self.pixels)
        removed=self.cache.prune({key(self.w)},complete=True)
        self.assertEqual(len(removed),1);self.assertEqual(self.cache.restore(self.w)[1],self.pixels)
    def test_same_native_numbers_from_new_compositor_session_cannot_import_cache(self):
        self.cache.publish(self.w,self.metadata,self.pixels)
        later=SnapshotCache(self.root/'cache',native.Desktop.validate_snapshot,session='different-compositor-session')
        with self.assertRaisesRegex(ValueError,'identity/whole'):later.restore(self.w)
    def test_complete_prune_removes_only_closed_pair_retaining_live_minimized_cache(self):
        self.cache.publish(self.w,self.metadata,self.pixels)
        closed=self.d.windows[1]
        metadata=dict(self.metadata,identity=list(key(closed)),clientSize=closed['size'],rect=rectangle(closed),pixels=closed['size'])
        self.cache.publish(closed,metadata,png(*closed['size']))
        unrelated=self.cache.root/'unrelated.png';unrelated.write_bytes(b'keep')
        with self.assertRaisesRegex(ValueError,'complete'):self.cache.prune({key(self.w)},complete=False)
        removed=self.cache.prune({key(self.w)},complete=True)
        self.assertEqual(len(removed),2);self.assertEqual(self.cache.restore(self.w)[1],self.pixels)
        self.assertEqual(unrelated.read_bytes(),b'keep')
        with self.assertRaises(FileNotFoundError):self.cache.restore(closed)
    def test_adapter_failure_after_private_epoch_creation_removes_unreturned_capture(self):
        # Exercise the actual adapter wrapper at the precise pre-return boundary;
        # fake only the compositor capture primitive so no native call occurs.
        actor=NativeDesktop.__new__(NativeDesktop);actor.root=self.root/'actor';actor.root.mkdir(mode=0o700)
        actor.capture_lock=threading.RLock();actor.shared_cache=None;actor.current_capture_epoch=None
        created=[]
        def capture(actor,w,token,index):
            epoch='0123456789ab-1';actor.current_capture_epoch=epoch
            path=actor.root/(epoch+'.png');path.write_bytes(self.pixels);created.append(path)
            raise ValueError('native identity changed after export')
        actor._capture_source_impl=types.MethodType(capture,actor)
        with self.assertRaisesRegex(ValueError,'identity changed'):actor.capture_source(self.w,'0123456789ab-2',0)
        self.assertFalse(created[0].exists());self.assertIsNone(actor.current_capture_epoch)
    def test_adapter_shared_publish_failure_releases_its_returned_but_untransferred_png(self):
        actor=NativeDesktop.__new__(NativeDesktop);actor.root=self.root/'actor';actor.root.mkdir(mode=0o700)
        actor.capture_lock=threading.RLock();actor.shared_cache=self.cache;actor.current_capture_epoch=None
        created=[]
        def capture(actor,w,token,index):
            epoch='0123456789ab-1';actor.current_capture_epoch=epoch
            image=actor.root/(epoch+'.png');image.write_bytes(self.pixels);created.append(image)
            # Deliberately incomplete cache pair after successful image creation.
            return {'path':str(image)}
        actor._capture_source_impl=types.MethodType(capture,actor)
        with self.assertRaises(FileNotFoundError):actor.capture_source(self.w,'0123456789ab-2',0)
        self.assertFalse(created[0].exists())

if __name__=='__main__':unittest.main()
