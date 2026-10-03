"""Real ImageMagick pixels, sealed Keeper jobs, files and controller boundaries."""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import threading
import time
import unittest
import zlib
from batch_preview import BatchPreviews,PinnedPNG,png_dimensions
from helper_supervisor import Keeper
from owned_commands import OwnedCommands
from scene_controller import SceneController,rectangle
from test_capture_lease import FileDesktop
from test_scene_controller import Desktop,Transport

def patterned_png(width,height,alpha=True):
    def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    scanlines=bytearray()
    for y in range(height):
        scanlines.append(0)
        for x in range(width):
            scanlines.extend(((x*13+y*7)%256,(x*3+y*19)%256,(x*17+y*11)%256))
            if alpha:scanlines.append((x*23+y*29)%256)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',width,height,8,6 if alpha else 2,0,0,0))+chunk(b'IDAT',zlib.compress(scanlines))+chunk(b'IEND',b'')

class BatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.actor=self.root/'actor';self.actor.mkdir(mode=0o700)
        self.preview=self.root/'preview';self.records=[]
        self.env=dict(os.environ,XDG_RUNTIME_DIR=str(self.root),HYPRLAND_INSTANCE_SIGNATURE='offline',WAYLAND_DISPLAY='never-connect')
        self.keeper=Keeper(self.root,self.env,lambda body:self.records.append(deepcopy(body)))
        self.commands=OwnedCommands(self.keeper,self.env,17)
        self.batch=BatchPreviews(self.actor,self.preview,self.commands);self.members=[];self.sources=[];self.metadata=[]
        self.lock=threading.RLock()
    def tearDown(self):
        if self.keeper.process.poll() is None:
            if self.keeper.jobs:self.keeper.abort()
            else:self.keeper.stop()
        self.tmp.cleanup()
    def stage(self,cases=None):
        cases=cases or [(640,400,6,10,True,1),(80,50,3,4,False,1),(240,500,8,9,True,1)]
        for index,(width,height,left,top,alpha,scale) in enumerate(cases):
            window=deepcopy(Desktop().windows[index]);window['size']=[width/scale,height/scale]
            window['at']=[100+index*20,110+index*20]
            epoch='abcdef123456-'+str(index+1);image=self.actor/(epoch+'.png')
            image.write_bytes(patterned_png(width+left+2,height+top+3,alpha));image.chmod(0o600)
            metadata={'rect':{'x':window['at'][0]-left/scale,'y':window['at'][1]-top/scale,
                'width':(width+left+2)/scale,'height':(height+top+3)/scale},
                'pixels':[width+left+2,height+top+3],'insets':{'left':left/scale,'top':top/scale,'right':2/scale,'bottom':3/scale}}
            self.batch.stage(window,epoch,image,metadata)
            self.members.append(window);self.metadata.append(metadata)
            self.sources.append({'stableId':window['stableId'],'pid':window['pid'],'nativeRect':rectangle(window),
                'path':str(image),'digest':hashlib.sha256(image.read_bytes()).hexdigest(),'captureEpoch':epoch})
    def finish(self,current=lambda:True,clients=None):
        self.batch.finish(self.sources,self.members,clients=clients or (lambda:deepcopy(self.members)),current=current,reservation_lock=self.lock)
    def decoded(self,path):
        return subprocess.check_output(['/usr/bin/magick',str(path),'-alpha','on','-depth','8','RGBA:-'],timeout=2)
    def assert_no_publication(self):
        self.assertFalse(list(self.preview.glob('0x*.png')));self.assertFalse(list(self.preview.glob('0x*.json')))
    def test_real_batch_matches_original_rgb_alpha_and_tall_crops_one_owned_launch(self):
        self.stage();self.finish()
        for member,source,metadata in zip(self.members,self.sources,self.metadata,strict=True):
            old=self.root/(member['address']+'.png');scale=metadata['pixels'][0]/metadata['rect']['width']
            crop=f"{round(member['size'][0]*scale)}x{round(member['size'][1]*scale)}+{round(metadata['insets']['left']*scale)}+{round(metadata['insets']['top']*scale)}"
            subprocess.run(['/usr/bin/magick',source['path'],'-crop',crop,'+repage','-thumbnail','300x180>',str(old)],check=True,timeout=1)
            for slot in (0,1):
                actual=self.preview/(member['address']+'-'+str(slot)+'.png')
                self.assertEqual(png_dimensions(actual.read_bytes()),png_dimensions(old.read_bytes()))
                self.assertEqual(self.decoded(actual),self.decoded(old))
            self.assertEqual(json.loads((self.preview/(member['address']+'.json')).read_text()),{'stableId':member['stableId'],'pid':member['pid']})
        launches={row['job']:row for snapshot in self.records for row in snapshot['jobs']}
        self.assertEqual(len(launches),1);row=next(iter(launches.values()))
        self.assertEqual(row['kind'],'helper');self.assertEqual(row['actor'],17);self.assertEqual(row['phase'],'closed');self.assertTrue(row['groupEmpty'])
        self.assertEqual(row['ownership']['targetArgv'][0],'/usr/bin/magick')
        self.assertEqual(row['ownership']['producer']['sha256'],hashlib.sha256(Path('/usr/bin/magick').read_bytes()).hexdigest())
        self.assertFalse(self.keeper.jobs);self.assertFalse(self.batch.pending);self.assertFalse(list(self.preview.glob('.motion-batch-*')))
    def test_real_scaled_exact_bound_and_no_upscale_crops_match(self):
        self.stage([(300,180,4,6,False,1.5),(50,30,5,3,True,2),(602,402,7,8,True,1.25)]);self.finish()
        for window,source,metadata in zip(self.members,self.sources,self.metadata,strict=True):
            crop=self.batch_crop(window,metadata);old=self.root/(window['address']+'.png')
            subprocess.run(['/usr/bin/magick',source['path'],'-crop',crop,'+repage','-thumbnail','300x180>',str(old)],check=True,timeout=1)
            self.assertEqual(self.decoded(old),self.decoded(self.preview/(window['address']+'-0.png')))
    @staticmethod
    def batch_crop(window,metadata):
        scale=metadata['pixels'][0]/metadata['rect']['width']
        return f"{round(window['size'][0]*scale)}x{round(window['size'][1]*scale)}+{round(metadata['insets']['left']*scale)}+{round(metadata['insets']['top']*scale)}"
    def test_replaced_source_refuses_before_helper(self):
        self.stage();path=Path(self.sources[1]['path']);old=path.with_suffix('.old');path.rename(old);path.write_bytes(old.read_bytes())
        with self.assertRaisesRegex(ValueError,'inode changed'):self.finish()
        self.assert_no_publication();self.assertFalse(any(s['jobs'] for s in self.records))
    def test_changed_source_bytes_refuse_before_helper(self):
        self.stage();path=Path(self.sources[1]['path']);path.write_bytes(patterned_png(85,57))
        with self.assertRaises(ValueError):self.finish()
        self.assert_no_publication();self.assertFalse(any(s['jobs'] for s in self.records))
    def test_missing_source_refuses_before_helper(self):
        self.stage();Path(self.sources[1]['path']).unlink()
        with self.assertRaises(FileNotFoundError):self.finish()
        self.assert_no_publication();self.assertFalse(any(s['jobs'] for s in self.records))
    def test_missing_output_despite_real_normal_helper_refuses_whole_publication(self):
        self.stage();original=self.commands.run
        def remove_output(argv,**options):
            result=original(argv,**options);Path(argv[-1]).unlink();return result
        self.commands.run=remove_output
        with self.assertRaises(FileNotFoundError):self.finish()
        self.assert_no_publication();self.assertFalse(self.keeper.jobs);self.assertEqual(len(self.batch.pending),3)
    def test_wrong_output_dimensions_despite_normal_helper_refuse(self):
        self.stage();original=self.commands.run
        def corrupt(argv,**options):
            result=original(argv,**options);Path(argv[-1]).write_bytes(patterned_png(2,2));return result
        self.commands.run=corrupt
        with self.assertRaisesRegex(ValueError,'dimensions differ'):self.finish()
        self.assert_no_publication();self.assertFalse(self.keeper.jobs)
    def test_corrupt_crc_despite_normal_helper_refuses(self):
        self.stage();original=self.commands.run
        def corrupt(argv,**options):
            result=original(argv,**options);path=Path(argv[-1]);data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data);return result
        self.commands.run=corrupt
        with self.assertRaisesRegex(ValueError,'CRC'):self.finish()
        self.assert_no_publication()
    def test_supersession_during_actual_helper_cannot_publish(self):
        self.stage();current=[True];original=self.commands.run
        def supersede(argv,**options):
            result=original(argv,**options);current[0]=False;return result
        self.commands.run=supersede
        with self.assertRaisesRegex(ValueError,'superseded'):self.finish(current=lambda:current[0])
        self.assert_no_publication();self.assertEqual(len(self.batch.pending),3)
    def test_post_helper_geometry_change_refuses_all_previews(self):
        self.stage();live=deepcopy(self.members);original=self.commands.run
        def mutate(argv,**options):
            result=original(argv,**options);live[2]['at'][0]+=1;return result
        self.commands.run=mutate
        with self.assertRaisesRegex(ValueError,'geometry'):self.finish(clients=lambda:deepcopy(live))
        self.assert_no_publication()
    def test_actual_closed_helper_publication_fault_quarantines_material(self):
        self.stage();original=self.keeper.record
        def fail_closed(body):
            if any(row['phase']=='closed' for row in body['jobs']):raise OSError('actual durable completion publication failed')
            original(body)
        self.keeper.record=fail_closed
        with self.assertRaisesRegex(OSError,'publication failed'):self.finish()
        self.assertTrue(self.batch.quarantined);self.assertTrue(self.batch.retained_folder.is_dir())
        self.assertTrue(all(Path(source['path']).exists() for source in self.sources));self.assertEqual(len(self.batch.pending),3)
        for action in (lambda:self.batch.discard(self.sources[0]['captureEpoch']),self.batch.require_disposable):
            with self.assertRaisesRegex(ValueError,'unfinished'):action()
        self.keeper.record=original
    def test_pending_source_prevents_normal_disposal_and_exact_discard_releases(self):
        self.stage()
        with self.assertRaisesRegex(ValueError,'pending'):self.batch.require_disposable()
        self.batch.discard(self.sources[1]['captureEpoch']);self.assertEqual(set(self.batch.pending),{self.sources[0]['captureEpoch'],self.sources[2]['captureEpoch']})
        for source in self.sources:self.batch.discard(source['captureEpoch'])
        self.batch.require_disposable()
    def test_busy_real_flock_refuses_without_launch_or_deadlock(self):
        import fcntl
        self.stage();self.preview.mkdir(mode=0o700)
        with (self.preview/(self.members[1]['address']+'.lock')).open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):self.finish()
        self.assert_no_publication();self.assertFalse(any(s['jobs'] for s in self.records))
    def test_actual_adapter_cleanup_under_receipt_does_not_wait_for_capture_worker(self):
        from native_desktop import NativeDesktop
        actor=NativeDesktop.__new__(NativeDesktop);actor.root=self.actor;actor.capture_lock=threading.RLock()
        actor.preview_batch=self.batch;actor.clients=lambda:deepcopy(self.members);actor.janitor=lambda:None
        self.stage();old=self.actor/'abcdef123456-99.png';old.write_bytes(patterned_png(2,2));old.chmod(0o600)
        receipt=threading.RLock();self.keeper.reservation_lock=receipt
        entered=threading.Event();permit=threading.Event();cleaned=threading.Event();errors=[];original=self.commands.run
        def paused(argv,**options):
            entered.set()
            if not permit.wait(2):raise TimeoutError('cleanup held receipt while waiting for capture')
            return original(argv,**options)
        self.commands.run=paused
        def preparation():
            try:actor.finish_capture_previews(self.sources,self.members,current=lambda:True,reservation_lock=receipt)
            except BaseException as error:errors.append(error)
        def cleanup():
            with receipt:
                actor.release_sources([{'path':str(old)}]);cleaned.set();permit.set()
        prep=threading.Thread(target=preparation);clean=threading.Thread(target=cleanup)
        prep.start();self.assertTrue(entered.wait(1));clean.start()
        try:self.assertTrue(cleaned.wait(.5),'cleanup waited for capture lock')
        finally:permit.set();prep.join(3);clean.join(3)
        self.assertFalse(prep.is_alive());self.assertFalse(clean.is_alive());self.assertFalse(errors)
        self.assertFalse(old.exists());self.assertFalse(self.batch.pending);self.assertFalse(self.keeper.jobs)
    def test_active_exact_source_refuses_adapter_cleanup_without_waiting(self):
        from native_desktop import NativeDesktop
        self.stage();actor=NativeDesktop.__new__(NativeDesktop);actor.root=self.actor;actor.preview_batch=self.batch;actor.janitor=lambda:None
        original=self.commands.run;observed=[]
        def attempt_release(argv,**options):
            with self.lock:
                with self.assertRaisesRegex(ValueError,'unfinished'):actor.release_sources(self.sources)
            observed.append(True);return original(argv,**options)
        self.commands.run=attempt_release;self.finish();self.assertEqual(observed,[True])
        self.assertTrue(all(Path(s['path']).exists() for s in self.sources));self.assertFalse(self.batch.pending)
    def test_partial_slot_publication_failure_retains_pending_and_refuses_success(self):
        from unittest.mock import patch
        self.stage();original=Path.replace;count=[0]
        def fail_second(path,destination):
            count[0]+=1
            if count[0]==2:raise OSError('actual preview slot rename failure')
            return original(path,destination)
        with patch.object(Path,'replace',fail_second):
            with self.assertRaisesRegex(OSError,'slot rename'):self.finish()
        self.assertEqual(len(self.batch.pending),3);self.assertFalse(self.keeper.jobs);self.assertFalse(self.batch.quarantined)
        self.assertFalse(list(self.preview.glob('.motion-batch-*')))
    def test_superseded_before_launch_clears_active_reservation_but_retains_local_lease(self):
        self.stage()
        with self.assertRaisesRegex(ValueError,'superseded'):self.finish(current=lambda:False)
        self.assertFalse(self.batch.active);self.assertFalse(self.batch.active_epochs);self.assertEqual(len(self.batch.pending),3)
        self.assertFalse(any(s['jobs'] for s in self.records))
    def native_actor(self):
        from native_desktop import NativeDesktop
        from unittest.mock import patch
        parent=self.root/'hypr-window-motion'/'actors';parent.mkdir(parents=True,mode=0o700)
        window=deepcopy(Desktop().windows[0])
        with patch.dict(os.environ,self.env):
            actor=NativeDesktop(parent/'actor-2',core=self.root/'unused-core',commands=self.commands,
                target=lambda _:dict(visible=True,rect=dict(x=1,y=1,width=20,height=20),screenName='offline'))
        actor.base.clients=lambda:[deepcopy(window)]
        def export(args,**options):
            # Only the compositor export primitive is replaced. Capture wrapper,
            # permission/cache/pending lifecycle and owned magick are real.
            self.assertEqual(args[:2],['hyprctl','repl']);self.assertIn('window_atlas(',args[2])
            epoch=actor.current_capture_epoch;image=actor.root/(epoch+'.png');image.write_bytes(patterned_png(*window['size']))
            return json.dumps(dict(ok=True,whole=True,canonical=True,captureEpoch=epoch,stableId=window['stableId'],pid=window['pid'],
                rect=rectangle(window),pixels=window['size'],insets=dict(left=0,top=0,right=0,bottom=0)))
        self.commands.check_output=export
        return actor,window
    def test_actual_capture_adapter_finalizes_permissions_before_staging_and_real_batch(self):
        actor,window=self.native_actor();source=actor.capture_source(window,'fedcba987654-1',0)
        row=actor.preview_batch.pending[source['captureEpoch']]
        self.assertEqual(row['inode'][4],Path(source['path']).stat().st_ctime_ns)
        self.assertEqual(row['digest'],source['digest'])
        actor.finish_capture_previews([source],[window],current=lambda:True,reservation_lock=self.lock)
        self.assertFalse(actor.preview_batch.pending);self.assertFalse(self.keeper.jobs)
        preview=actor.preview_batch.preview/(window['address']+'-0.png')
        self.assertEqual(png_dimensions(preview.read_bytes(),complete=True),(270,180))
        actor.release_sources([source]);self.assertFalse(Path(source['path']).exists())
    def test_actual_shared_cache_failure_discards_staged_unreturned_epoch(self):
        from types import SimpleNamespace
        actor,window=self.native_actor()
        def fail_publish(*args):raise OSError('actual wrapper shared cache publication failed')
        actor.shared_cache=SimpleNamespace(stem=lambda _:f"full-{window['stableId']}-{window['pid']}",publish=fail_publish)
        with self.assertRaisesRegex(OSError,'shared cache publication'):actor.capture_source(window,'fedcba987654-1',0)
        self.assertFalse(actor.preview_batch.pending);self.assertFalse(list(actor.root.glob(actor.capture_session+'-*.png')))
        self.assertIsNone(actor.current_capture_epoch)

class FinishControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.d=FileDesktop(Path(self.tmp.name));self.t=Transport();self.c=SceneController(self.d,self.t)
    def tearDown(self):self.c.workers.shutdown(wait=True,cancel_futures=True);self.tmp.cleanup()
    def request(self):
        w=self.d.windows[0];return self.c.request('minimize',w['address'],w['stableId'],w['pid'],context=1)
    def wait(self,p):
        end=time.monotonic()+3
        while time.monotonic()<end:
            if p():return
            time.sleep(.002)
        self.fail('controller boundary timeout')
    def test_complete_family_finish_precedes_outputs_and_seed(self):
        seen=[]
        def finish(sources,members,*,current,reservation_lock,deadline_ns=None):
            self.assertEqual(len(sources),3);self.assertEqual(len(members),3);self.assertTrue(current());self.assertFalse(self.t.sent);self.assertFalse(self.t.preparations);seen.append(True)
        self.d.finish_capture_previews=finish;self.request();self.wait(lambda:any(m['command']=='seed' for m in self.t.sent));self.assertEqual(seen,[True])
    def test_failed_finisher_releases_entire_actual_capture_lease_and_never_seeds(self):
        def fail(*args,**options):raise ValueError('batch image validation failed')
        self.d.finish_capture_previews=fail;self.request();self.wait(lambda:len(self.d.removed)==3)
        self.assertFalse(any(m['command']=='seed' for m in self.t.sent));self.assertFalse(any(p.exists() for p in self.d.created));self.assertFalse(self.t.preparations)
    def test_blocked_finisher_does_not_hold_receipt_lock_and_old_lease_cannot_seed(self):
        entered=threading.Event();release=threading.Event();calls=[]
        def finish(sources,members,*,current,reservation_lock,deadline_ns=None):
            calls.append(sources)
            if len(calls)==1:
                entered.set();release.wait(3)
                with reservation_lock:
                    if not current():raise ValueError('superseded batch')
        self.d.finish_capture_previews=finish;first=self.request();self.assertTrue(entered.wait(1));second=self.request()
        self.wait(lambda:any(m['command']=='seed' and m['token']==second['token'] for m in self.t.sent));release.set();self.wait(lambda:len(self.d.removed)==3)
        self.assertFalse(any(m['command']=='seed' and m['token']==first['token'] for m in self.t.sent));self.assertTrue(all(Path(s['path']).exists() for s in calls[1]))

if __name__=='__main__':unittest.main()
