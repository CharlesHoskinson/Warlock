"""Genuine owned CPU helpers, real pixels and unchanged controller seed guards.

grim is explicitly a file-copy fixture; no native compositor is contacted.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import test_batch_preview as fixtures
import test_scene_controller as scenes
from native_desktop import NativeDesktop
from owned_commands import OwnedCommands,SealedFile
from pipe_transport import PipeTransport
from scene_controller import SceneController,key,rectangle

EVIDENCE=[]

class HiddenFusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build=tempfile.TemporaryDirectory(prefix='fusion-fixtures-');cls.bin=Path(cls.build.name)
        for source,name in (('hidden_grim_cpu_fixture.c','grim'),('renderer_role_cpu_fixture.c','renderer-cpu')):
            subprocess.run(['/usr/bin/gcc','-O2','-Wall','-Wextra','-Werror',str(Path(__file__).with_name(source)),'-o',str(cls.bin/name)],check=True,timeout=10)
        cls.producer_sha=hashlib.sha256((cls.bin/'renderer-cpu').read_bytes()).hexdigest()
    @classmethod
    def tearDownClass(cls):cls.build.cleanup()
    def setUp(self):
        self.f=fixtures.BatchTests();self.f.setUp();self.errors=[];self.controllers=[];self.expected_unknown=False
        self.raw=self.f.root/'raw-clients';self.raw.mkdir(mode=0o700)
        self.f.env.update(PATH=str(self.bin)+':'+os.environ['PATH'],FIXTURE_GRIM_DIRECTORY=str(self.raw),FIXTURE_GRIM_MODE='normal')
        self.f.commands.env=dict(self.f.env)
        self.scene_desktop=scenes.Desktop();self.live=self.scene_desktop.windows
        for index,window in enumerate(self.live):
            window.update(size=[96+index*8,64+index*4],workspace={'name':'special:win-minimized'},pinned=False)
            self.scene_desktop.native[index].update(deepcopy(window))
            (self.raw/(window['stableId']+'.png')).write_bytes(fixtures.patterned_png(*window['size'],alpha=True))
        self.envpatch=patch.dict(os.environ,self.f.env);self.envpatch.start()
        self.actor=NativeDesktop(self.f.root/'hypr-window-motion'/'actor',core='/unused-cpu-core',commands=self.f.commands,
            target=lambda _:dict(visible=True,rect=dict(x=10,y=700,width=28,height=28),screenName='owned-cpu'))
        self.client_observations=[]
        def clients():self.client_observations.append(deepcopy(self.live));return deepcopy(self.live)
        self.actor.base.clients=clients
        self.frames={};self.metadata={}
        for window in self.live:
            width,height=window['size'];left,top,right,bottom=7,31,7,7
            stem=self.actor.root/('full-'+window['stableId']+'-'+str(window['pid']))
            frame=fixtures.patterned_png(width+left+right,height+top+bottom,alpha=True)
            metadata=dict(whole=True,canonical=True,identity=list(key(window)),clientSize=window['size'],
                pixels=[width+left+right,height+top+bottom],insets=dict(left=left,top=top,right=right,bottom=bottom),
                rect=dict(x=window['at'][0]-left,y=window['at'][1]-top,width=width+left+right,height=height+top+bottom))
            stem.with_suffix('.png').write_bytes(frame);stem.with_suffix('.json').write_text(json.dumps(metadata))
            self.frames[window['stableId']]=frame;self.metadata[window['stableId']]=metadata
        with SealedFile(self.bin/'renderer-cpu') as selected:
            self.transport=PipeTransport('/proc/self/fd/'+str(selected.fd),env=self.f.env,failure=self.errors.append,
                pass_fds=(selected.fd,),keeper=self.f.keeper,actor=17)
        deadline=time.monotonic()+2
        while not self.transport.outputs() and time.monotonic()<deadline:time.sleep(.002)
        self.assertTrue(self.transport.outputs());self.actor.preview_batch.bind_renderer(self.transport,self.producer_sha)
        self.assertTrue(self.actor.preview_batch._closed())
    def tearDown(self):
        try:
            for controller in self.controllers:controller.workers.shutdown(wait=True,cancel_futures=True)
            self.assertEqual(self.transport.close(),0);self.assertFalse(self.errors)
            jobs=self.jobs()
            remaining=deepcopy(list(self.f.keeper.jobs.values()))
            if self.expected_unknown:
                terminal=self.f.keeper.abort();self.assertIs(terminal['normalStop'],False)
            else:
                self.assertFalse(self.f.keeper.jobs);self.f.keeper.stop();terminal=self.f.keeper.ownership['terminal']
                self.assertIs(terminal['normalStop'],True)
                self.assertTrue(all(row['normalCompletion'] is True and row['groupEmpty'] is True for row in terminal['jobs']))
                self.assertEqual({row['job']for row in terminal['jobs']},{row['job']for row in jobs})
            EVIDENCE.append({'test':self.id(),'jobs':jobs,'remainingRegistered':remaining,'actualKeeperTerminal':deepcopy(terminal),
                'unknownExpected':self.expected_unknown,'rendererClosed':self.transport.closed,'rendererExit':self.transport.process.returncode,
                'clientObservations':len(self.client_observations),'nativeLaunch':False,'grimIsFixture':True})
            if not self.expected_unknown:self.assertFalse(self.f.keeper.jobs)
        finally:self.envpatch.stop();self.f.tearDown()
    def jobs(self):return list({row['job']:row for packet in self.f.records for row in packet['jobs']}.values())
    def helpers(self):return [row for row in self.jobs() if row['kind']=='helper']
    def capture(self,index=0):return self.actor.capture_source(deepcopy(self.live[index]),'abcdef123456-1',index)
    def assert_no_preview(self):
        preview=self.actor.preview_batch.preview
        self.assertFalse(list(preview.glob('0x*.png')));self.assertFalse(list(preview.glob('0x*.json')))
    def hook(self,callback):
        original=self.f.commands.run
        def run(argv,**options):
            result=original(argv,**options)
            if Path(argv[0]).name=='magick':callback(argv)
            return result
        self.f.commands.run=run
    def assert_pixels(self,source,index=0):
        window=self.live[index];raw=self.raw/(window['stableId']+'.png');frame=self.actor.root/('full-'+window['stableId']+'-'+str(window['pid'])+'.png')
        thumb=self.f.root/'expected-thumb.png';whole=self.f.root/'expected-whole.png'
        subprocess.run(['/usr/bin/magick',str(raw),'-thumbnail','300x180>',str(thumb)],check=True,timeout=1)
        subprocess.run(['/usr/bin/magick',str(frame),'(',str(raw),'-resize',str(window['size'][0])+'x'+str(window['size'][1])+'!',')','-geometry','+7+31','-compose','SrcAtop','-composite',str(whole)],check=True,timeout=1)
        self.assertEqual(self.f.decoded(Path(source['path'])),self.f.decoded(whole))
        for slot in (0,1):self.assertEqual(self.f.decoded(self.actor.production.RUNTIME/'hypr-window-previews'/(window['address']+'-'+str(slot)+'.png')),self.f.decoded(thumb))
    def test_actual_bound_owned_capture_preserves_both_original_pixels_and_six_observations(self):
        source=self.capture();self.assert_pixels(source);self.assertEqual(len(self.client_observations),6)
        helpers=self.helpers();self.assertEqual(len(helpers),2)
        self.assertEqual([Path(h['ownership']['targetArgv'][0]).name for h in helpers],['grim','magick'])
        self.assertTrue(all(h['phase']=='closed' and h['groupEmpty'] for h in helpers))
        self.assertEqual(source['digest'],hashlib.sha256(Path(source['path']).read_bytes()).hexdigest())
    def test_three_members_use_three_real_grim_and_three_real_combined_jobs(self):
        sources=[self.capture(i)for i in range(3)]
        self.actor.finish_capture_previews(sources,deepcopy(self.live),current=lambda:True,reservation_lock=self.f.lock,deadline_ns=time.monotonic_ns()+2000000000)
        self.assertEqual(len(self.helpers()),6)
        for i,source in enumerate(sources):self.assert_pixels(source,i)
        self.assertFalse(self.actor.preview_batch.pending);self.assertTrue(self.actor.preview_batch._closed())
    def test_legacy_standalone_keeps_two_original_real_magick_jobs(self):
        self.actor.preview_batch=None;source=self.capture();self.assert_pixels(source)
        self.assertEqual([Path(h['ownership']['targetArgv'][0]).name for h in self.helpers()],['grim','magick','magick'])
    def test_changed_cached_identity_refuses_before_grim(self):
        window=self.live[0];path=self.actor.root/('full-'+window['stableId']+'-'+str(window['pid'])+'.json');metadata=json.loads(path.read_text());metadata['identity'][2]+=1;path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ValueError,'matching whole-window cache'):self.capture()
        self.assertFalse(self.helpers());self.assert_no_preview()
    def test_changed_cached_client_size_refuses_before_grim(self):
        window=self.live[0];path=self.actor.root/('full-'+window['stableId']+'-'+str(window['pid'])+'.json');metadata=json.loads(path.read_text());metadata['clientSize'][0]+=1;path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ValueError,'matching whole-window cache'):self.capture()
        self.assertFalse(self.helpers());self.assert_no_preview()
    def test_normal_empty_grim_refuses_with_known_closure(self):
        self.f.commands.env['FIXTURE_GRIM_MODE']='empty'
        with self.assertRaisesRegex(ValueError,'empty toplevel'):self.capture()
        self.assert_no_preview();self.assertFalse(self.actor.preview_batch.quarantined)
    def test_actual_magick_nonzero_refuses_and_closes_real_job(self):
        window=self.live[0];(self.actor.root/('full-'+window['stableId']+'-'+str(window['pid'])+'.png')).write_bytes(b'invalid image material')
        with self.assertRaises(subprocess.CalledProcessError):self.capture()
        self.assert_no_preview();self.assertFalse(self.actor.preview_batch.quarantined)
        self.assertTrue(all(h['phase']=='closed' and h['groupEmpty'] for h in self.helpers()))
    def test_normal_magick_missing_thumbnail_refuses_before_publication(self):
        self.hook(lambda argv:Path(argv[argv.index('-write')+1]).unlink())
        with self.assertRaisesRegex(ValueError,'incomplete hidden pixel outputs'):self.capture()
        self.assert_no_preview();self.assertFalse(self.actor.preview_batch.quarantined)
    def test_normal_magick_missing_whole_refuses_before_publication(self):
        self.hook(lambda argv:Path(argv[-1]).unlink())
        with self.assertRaisesRegex(ValueError,'incomplete hidden pixel outputs'):self.capture()
        self.assert_no_preview();self.assertFalse(self.actor.preview_batch.quarantined)
    def test_normal_magick_short_whole_refuses_before_publication(self):
        self.hook(lambda argv:Path(argv[-1]).write_bytes(b'x'*63))
        with self.assertRaisesRegex(ValueError,'incomplete hidden pixel outputs'):self.capture()
        self.assert_no_preview();self.assertFalse(self.actor.preview_batch.quarantined)
    def test_post_helper_actual_lifetime_change_refuses_publication(self):
        self.hook(lambda argv:self.live[0].update(pid=self.live[0]['pid']+1))
        with self.assertRaisesRegex(ValueError,'identity or geometry'):self.capture()
        self.assert_no_preview()
    def test_post_helper_actual_geometry_change_refuses_publication(self):
        self.hook(lambda argv:self.live[0]['at'].__setitem__(0,self.live[0]['at'][0]+1))
        with self.assertRaisesRegex(ValueError,'identity or geometry'):self.capture()
        self.assert_no_preview()
    def test_actual_failed_durable_helper_completion_quarantines_exact_epoch(self):
        original=self.f.keeper.record
        def refused(body):
            if any(row['kind']=='helper' and row['phase']=='closed' and Path(row['ownership']['targetArgv'][0]).name=='magick' for row in body['jobs']):raise OSError('closed helper durable write refused')
            original(body)
        self.f.keeper.record=refused
        try:
            with self.assertRaisesRegex(ValueError,'unfinished'):self.capture()
            self.assertTrue(self.actor.preview_batch.quarantined);self.assertEqual(self.actor.preview_batch.active_epochs,{self.actor.capture_session+'-1'})
            self.assertTrue((self.actor.root/(self.actor.capture_session+'-1.png')).is_file());self.assert_no_preview()
        finally:self.f.keeper.record=original;self.expected_unknown=True
    def test_actual_grim_timeout_retains_unknown_job_and_epoch(self):
        self.f.commands.env['FIXTURE_GRIM_MODE']='timeout'
        with self.assertRaisesRegex(ValueError,'unfinished'):self.capture()
        self.assertTrue(self.actor.preview_batch.quarantined);self.assertTrue(self.f.keeper.jobs);self.assert_no_preview();self.expected_unknown=True
    def controller(self):
        desktop=self.scene_desktop
        desktop.capture_source=self.actor.capture_source
        original=desktop.release_sources
        def release(sources):original(sources);self.actor.release_sources(sources)
        desktop.release_sources=release;desktop.finish_capture_previews=self.actor.finish_capture_previews
        transport=scenes.Transport();controller=SceneController(desktop,transport);self.controllers.append(controller)
        return controller,transport
    def test_cancelled_controller_after_real_pixels_cannot_seed(self):
        controller,transport=self.controller()
        self.hook(lambda argv:setattr(controller,'current',None))
        window=self.live[0];controller.request('restore',*key(window),context=1);controller.workers.shutdown(wait=True)
        self.assertFalse(any(m['command']=='seed'for m in transport.sent));self.assertTrue(self.scene_desktop.released)
        self.assertFalse(self.actor.preview_batch.quarantined)
    def test_real_receipt_deadline_after_pixels_cannot_seed(self):
        controller,transport=self.controller();once=[False]
        def delayed(argv):
            if once[0]:return
            once[0]=True;deadline=controller.current.profile['receivedNs']+2000000000
            gate=threading.Event();timer=threading.Timer(max(0,(deadline-time.monotonic_ns())/1e9)+.015,gate.set);timer.start()
            try:self.assertTrue(gate.wait(2.5))
            finally:timer.join(3)
            self.assertGreaterEqual(time.monotonic_ns(),deadline)
        self.hook(delayed);window=self.live[0];controller.request('restore',*key(window),context=1);controller.workers.shutdown(wait=True)
        self.assertFalse(any(m['command']=='seed'for m in transport.sent));self.assertTrue(self.scene_desktop.released)
        self.assertFalse(self.actor.preview_batch.quarantined)
    def test_shared_immutable_whole_cache_is_preserved_for_reuse(self):
        from snapshot_cache import SnapshotCache
        cache=SnapshotCache(self.f.root/'shared',self.actor.base.validate_snapshot,session='offline');self.actor.shared_cache=cache
        for window in self.live:cache.publish(window,self.metadata[window['stableId']],self.frames[window['stableId']])
        before={str(p):p.read_bytes()for p in cache.root.iterdir()}
        self.capture();after={str(p):p.read_bytes()for p in cache.root.iterdir()}
        self.assertEqual(before,after)
    def test_noncanonical_direct_hidden_helper_refuses_before_material(self):
        original=self.actor.preview_batch;self.actor.preview_batch=None
        try:
            with self.assertRaisesRegex(ValueError,'canonical owned'):self.actor._capture_hidden_fused(deepcopy(self.live[0]),'abcdef123456-1')
        finally:self.actor.preview_batch=original
        self.assertFalse(self.helpers())

if __name__=='__main__':unittest.main()
