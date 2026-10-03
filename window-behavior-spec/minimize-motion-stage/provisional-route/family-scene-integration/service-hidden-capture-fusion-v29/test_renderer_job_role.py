"""Nongraphical actual OwnedLaunch/PipeTransport/Keeper role boundaries."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import batch_preview
import test_batch_preview as fixtures
from owned_commands import SealedFile
from pipe_transport import PipeTransport


class RendererRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build=tempfile.TemporaryDirectory()
        cls.executable=Path(cls.build.name)/'renderer-cpu'
        subprocess.run(['/usr/bin/gcc','-O2','-Wall','-Wextra','-Werror',
            str(Path(__file__).with_name('renderer_role_cpu_fixture.c')),'-o',str(cls.executable)],check=True,timeout=10)
        cls.producer_sha=hashlib.sha256(cls.executable.read_bytes()).hexdigest()
    @classmethod
    def tearDownClass(cls):cls.build.cleanup()
    def setUp(self):
        self.f=fixtures.BatchTests();self.f.setUp();self.transports=[];self.errors=[];self.expected_quarantine=False
    def tearDown(self):
        try:
            for transport in reversed(self.transports):
                if not transport.closed:self.assertEqual(transport.close(),0)
                self.assertTrue(all(not thread.is_alive() for thread in transport.threads))
            self.assertFalse(self.errors)
            if self.expected_quarantine:
                self.assertTrue(self.f.keeper.jobs)
                self.assertTrue(all(row['kind']=='helper' and row['phase']=='closed' and row['groupEmpty']
                    for row in self.f.keeper.jobs.values()))
                # Durable closure was deliberately faulted. Fixture cleanup uses
                # inherited Keeper.abort; it is never reported as normal stop.
            else:self.assertFalse(self.f.keeper.jobs)
        finally:self.f.tearDown()
    def renderer(self,actor=17):
        with SealedFile(self.executable) as selected:
            transport=PipeTransport('/proc/self/fd/'+str(selected.fd),env=self.f.env,
                failure=self.errors.append,pass_fds=(selected.fd,),keeper=self.f.keeper,actor=actor)
        self.transports.append(transport)
        deadline=time.monotonic()+2
        while not transport.outputs() and time.monotonic()<deadline:time.sleep(.002)
        self.assertTrue(transport.outputs());self.assertFalse(self.errors)
        return transport
    def bound(self):
        transport=self.renderer();self.f.batch.bind_renderer(transport,self.producer_sha)
        self.assertTrue(self.f.batch._closed());return transport
    def test_live_exact_renderer_all_original_real_pixels_publish_without_closing_renderer(self):
        transport=self.bound()
        self.f.stage();self.f.finish()
        for member,source,metadata in zip(self.f.members,self.f.sources,self.f.metadata,strict=True):
            expected=self.f.root/(member['address']+'.png')
            subprocess.run(['/usr/bin/magick',source['path'],'-crop',self.f.batch_crop(member,metadata),
                '+repage','-thumbnail','300x180>',str(expected)],check=True,timeout=1)
            for slot in (0,1):
                actual=self.f.preview/(member['address']+'-'+str(slot)+'.png')
                self.assertEqual(self.f.decoded(actual),self.f.decoded(expected))
            self.assertEqual(json.loads((self.f.preview/(member['address']+'.json')).read_text()),
                {'stableId':member['stableId'],'pid':member['pid']})
        self.assertIsNone(transport.process.poll());self.assertFalse(transport.closed)
        self.assertEqual(set(self.f.keeper.jobs),{transport.owned_launch.job})
        self.assertFalse(self.f.batch.pending);self.assertTrue(self.f.batch._closed())
    def test_prebind_live_renderer_refuses(self):
        self.renderer();self.assertFalse(self.f.batch._closed())
    def test_rebinding_refuses_preserving_original_object(self):
        transport=self.bound();binding=self.f.batch.renderer_binding
        with self.assertRaisesRegex(ValueError,'exactly once'):self.f.batch.bind_renderer(transport,self.producer_sha)
        self.assertIs(self.f.batch.renderer_binding,binding);self.assertTrue(self.f.batch._closed())
    def test_foreign_genuine_transport_actor_refuses_bind(self):
        transport=self.renderer(18)
        with self.assertRaisesRegex(ValueError,'registered ownership'):self.f.batch.bind_renderer(transport,self.producer_sha)
        self.assertIsNone(self.f.batch.renderer_binding)
    def test_wrong_selected_producer_refuses_bind(self):
        transport=self.renderer()
        with self.assertRaisesRegex(ValueError,'producer/session'):self.f.batch.bind_renderer(transport,'0'*64)
    def test_bind_under_receipt_is_memory_only(self):
        transport=self.renderer()
        with self.f.lock,patch.object(batch_preview,'checked_renderer',side_effect=AssertionError('material I/O in bind')),\
                patch.object(batch_preview,'verify_process',side_effect=AssertionError('kernel I/O in bind')),\
                patch.object(self.f.keeper,'verify',side_effect=AssertionError('keeper I/O in bind')):
            self.f.batch.bind_renderer(transport,self.producer_sha)
        self.assertTrue(self.f.batch._closed())
    def test_coherent_foreign_real_popen_swap_refuses_actual_pid(self):
        transport=self.bound();foreign=self.renderer(18);launch=transport.owned_launch
        binding=self.f.batch.renderer_binding;original=transport.process
        try:
            transport.process=launch.process=binding['process']=foreign.process
            self.f.keeper.children[launch.job]=foreign.process
            self.assertFalse(self.f.batch._closed())
        finally:
            transport.process=launch.process=binding['process']=original
            self.f.keeper.children[launch.job]=original
        self.assertTrue(self.f.batch._closed())
    def test_noncanonical_popen_wrapper_refuses_before_kernel_check(self):
        from types import SimpleNamespace
        transport=self.bound();launch=transport.owned_launch;binding=self.f.batch.renderer_binding;original=transport.process
        surrogate=SimpleNamespace(pid=original.pid,returncode=None)
        try:
            transport.process=launch.process=binding['process']=surrogate;self.f.keeper.children[launch.job]=surrogate
            with patch.object(batch_preview,'verify_process',side_effect=AssertionError('invalid wrapper reached kernel')):
                self.assertFalse(self.f.batch._closed())
        finally:
            transport.process=launch.process=binding['process']=original;self.f.keeper.children[launch.job]=original
    def test_nested_registry_and_launch_bool_float_aliases_refuse(self):
        transport=self.bound();launch=transport.owned_launch;row=self.f.keeper.jobs[launch.job]
        for field in ('device','inode','size'):
            original=launch.ownership['producer'][field]
            for value in (float(original),True):
                with self.subTest(field=field,type=type(value).__name__):
                    try:
                        launch.ownership['producer'][field]=value;row['ownership']['producer'][field]=value
                        self.assertFalse(self.f.batch._closed())
                    finally:
                        launch.ownership['producer'][field]=original;row['ownership']['producer'][field]=original
        self.assertTrue(self.f.batch._closed())
    def test_registry_only_launch_only_aliases_refuse(self):
        transport=self.bound();launch=transport.owned_launch;row=self.f.keeper.jobs[launch.job]
        for owner in (launch.ownership,row['ownership']):
            for field in ('pid','start','uid'):
                original=owner[field]
                try:owner[field]=float(original);self.assertFalse(self.f.batch._closed())
                finally:owner[field]=original
        self.assertTrue(self.f.batch._closed())
    def test_nested_typed_decoder_refuses_non_json_and_alias_values(self):
        equal=self.f.batch._typed_equal
        self.assertTrue(equal({'a':[None,False,1,'x']},{'a':[None,False,1,'x']}))
        for left,right in ((1,True),(1,1.0),({'a':[1]},{'a':[True]}),({'a':None},{'a':float('nan')}),([1],(1,))):
            self.assertFalse(equal(left,right))
        class ForeignString(str):pass
        self.assertFalse(equal({'a':1},{ForeignString('a'):1}))
    def test_same_actor_renderer_kind_and_every_outstanding_role_refuse(self):
        transport=self.bound();row=self.f.keeper.jobs[transport.owned_launch.job]
        for kind in ('helper','native-export','native-effect','unknown'):
            try:row['kind']=kind;self.assertFalse(self.f.batch._closed())
            finally:row['kind']='renderer'
        for kind in ('renderer','helper','native-export','native-effect','unknown'):
            extra=deepcopy(row);extra['job']='duplicate-'+kind;extra['kind']=kind
            try:self.f.keeper.jobs[extra['job']]=extra;self.assertFalse(self.f.batch._closed())
            finally:del self.f.keeper.jobs[extra['job']]
    def test_genuine_other_actor_work_follows_original_filter(self):
        self.bound();self.renderer(18);self.assertTrue(self.f.batch._closed())
    def test_exited_bound_renderer_cannot_claim_live_exemption(self):
        transport=self.bound();self.assertEqual(transport.close(),0);self.assertFalse(self.f.batch._closed())
    def test_exact_start_and_session_changes_refuse(self):
        transport=self.bound();launch=transport.owned_launch;row=self.f.keeper.jobs[launch.job]
        for field,changed in (('start',launch.ownership['start']+1),('environment',dict(launch.ownership['environment'],WAYLAND_DISPLAY='foreign'))):
            original=deepcopy(row['ownership'][field])
            try:row['ownership'][field]=changed;self.assertFalse(self.f.batch._closed())
            finally:row['ownership'][field]=original
    def test_material_io_does_not_hold_receipt_or_keeper_and_final_snapshot_refuses_mutation(self):
        transport=self.bound();entered=threading.Event();release=threading.Event();acquired=threading.Event()
        errors=[];result=[];original=batch_preview.verify_process;row=self.f.keeper.jobs[transport.owned_launch.job]
        def gated(ownership):
            entered.set()
            if not release.wait(2):raise TimeoutError('material observation gate')
            return original(ownership)
        def observe():
            try:result.append(self.f.batch._closed())
            except BaseException as error:errors.append(error)
        def receipt_and_registry():
            with self.f.lock,self.f.keeper.lock:
                row['kind']='unknown';acquired.set()
            release.set()
        worker=threading.Thread(target=observe);other=threading.Thread(target=receipt_and_registry)
        try:
            with patch.object(batch_preview,'verify_process',gated):
                worker.start();self.assertTrue(entered.wait(1));other.start()
                try:self.assertTrue(acquired.wait(.5),'new material I/O held receipt/keeper lock')
                finally:release.set();worker.join(3);other.join(3)
            self.assertFalse(worker.is_alive());self.assertFalse(other.is_alive());self.assertFalse(errors);self.assertEqual(result,[False])
        finally:
            release.set();row['kind']='renderer'
            if worker.is_alive():worker.join(3)
            if other.is_alive():other.join(3)
        self.assertTrue(self.f.batch._closed())
    def test_actual_failed_durable_helper_closure_still_quarantines_with_live_renderer(self):
        self.bound();self.f.stage();original=self.f.keeper.record
        def refuse(body):
            if any(row['kind']=='helper' and row['phase']=='closed' for row in body['jobs']):raise OSError('actual helper closure write refused')
            original(body)
        try:
            self.f.keeper.record=refuse
            with self.assertRaisesRegex(OSError,'closure write refused'):self.f.finish()
            self.assertTrue(self.f.batch.quarantined);self.assertTrue(self.f.batch.retained_folder.is_dir())
            self.assertTrue(all(Path(source['path']).exists() for source in self.f.sources))
            with self.assertRaisesRegex(ValueError,'unfinished'):self.f.batch.require_disposable()
        finally:self.f.keeper.record=original;self.expected_quarantine=True
    def test_exact_binding_mutation_during_unlocked_io_refuses(self):
        self.bound();binding=self.f.batch.renderer_binding;selected=binding['producerSHA256']
        original=batch_preview.verify_process
        def changed(ownership):
            outcome=original(ownership);binding['producerSHA256']='0'*64;return outcome
        try:
            with patch.object(batch_preview,'verify_process',changed):self.assertFalse(self.f.batch._closed())
        finally:binding['producerSHA256']=selected
        self.assertTrue(self.f.batch._closed())


if __name__=='__main__':unittest.main()
