"""Real confined CPU renderer/keeper; no GPU, compositor or native operations."""
from contextlib import contextmanager
from copy import deepcopy
import json
import select
import subprocess
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import module_binding as binding
import renderer_binding_fixture as fixture
import test_batch_binding as inherited
from batch_preview import BatchPreviews
from owned_commands import SealedFile
from owned_launch import OwnedLaunch
from pipe_transport import PipeTransport


class RendererBindingKernelTests(unittest.TestCase):
    setUp=inherited.BatchBindingKernelTests.setUp
    tearDown=inherited.BatchBindingKernelTests.tearDown
    package=inherited.BatchBindingKernelTests.package
    bound=inherited.BatchBindingKernelTests.bound
    actor=inherited.BatchBindingKernelTests.actor
    genuine_actor=inherited.BatchBindingKernelTests.genuine_actor
    query=inherited.BatchBindingKernelTests.query
    terminal=inherited.BatchBindingKernelTests.terminal

    def prepare(self,factory,initial,destination,digest):
        self.bound(factory,initial,destination,digest)
        return self.genuine_actor(factory)

    def link(self,factory,desktop,transport,controller,destination):
        proof=binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json')
        factory.observed_bindings=[proof];factory.observed_controllers=[(1,controller)]
        return proof

    def refusal(self,factory,desktop,transport,controller,destination,relation=None):
        with self.assertRaises(ValueError):self.link(factory,desktop,transport,controller,destination)
        raw=json.loads((destination/'actor.json').read_text())
        self.assertFalse(raw['usable']);self.assertTrue(raw['errors'])
        self.assertTrue(raw['renderer']['errors'])
        if relation:self.assertFalse(raw['renderer']['relations'][relation])
        return raw

    @contextmanager
    def foreign(self,factory):
        errors=[]
        with SealedFile(factory._fixture_executable)as executable:
            transport=PipeTransport('/proc/self/fd/'+str(executable.fd),env=self.env,
                failure=errors.append,pass_fds=(executable.fd,),keeper=factory.keeper,actor=2)
        try:
            deadline=time.monotonic()+2
            while not transport.outputs()and time.monotonic()<deadline:time.sleep(.002)
            self.assertTrue(transport.outputs());self.assertFalse(errors)
            yield transport
        finally:
            self.assertEqual(transport.close(),0);self.assertFalse(errors)

    @contextmanager
    def helper(self,factory,actor):
        with SealedFile(factory._fixture_executable)as executable:
            launch=OwnedLaunch(['/proc/self/fd/'+str(executable.fd)],env=self.env,
                keeper=factory.keeper,kind='helper',actor=actor,executable_fd=executable.fd,
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                text=True,bufsize=1,pass_fds=(executable.fd,))
        try:
            self.assertTrue(select.select([launch.process.stdout],[],[],2)[0])
            self.assertEqual(json.loads(launch.process.stdout.readline())['event'],'outputs')
            yield launch
        finally:
            launch.process.stdin.write('{"command":"stop"}\n');launch.process.stdin.flush()
            self.assertEqual(launch.process.wait(timeout=2),0);launch.complete()
            for stream in (launch.process.stdin,launch.process.stdout,launch.process.stderr):stream.close()

    def test_genuine_sealed_exec_live_and_actual_normal_terminal(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            self.assertTrue(desktop.preview_batch._closed())
            self.assertIsNone(transport.process.poll())
            proof=self.link(factory,desktop,transport,controller,destination)
            self.assertTrue(proof['usable']);self.assertTrue(all(proof['renderer']['relations'].values()))
            for name in ('bind_renderer','_closed','_renderer_matches','_typed_equal','_renderer_witness'):
                self.assertIn('batch.'+name,proof['callbacks'])
            result=self.terminal(factory,initial,destination)
            self.assertTrue(result['usable'])
            observed=result['terminalBatchConfirmation'][0]['renderer']
            self.assertEqual(binding.typed_json(observed['stable']),binding.typed_json(proof['renderer']['stable']))
            self.assertIs(observed['lifecycle']['keeperTerminal']['normalStop'],True)
            self.assertIs(type(observed['lifecycle']['keeperReturncode']),int)
            self.assertEqual(observed['lifecycle']['keeperReturncode'],0)
            self.assertFalse(factory.keeper.jobs);self.assertFalse(factory.keeper.children)
            from recovery_resources import process_start
            self.assertNotEqual(process_start(transport.process.pid),transport.owned_launch.ownership['start'])

    def test_live_link_does_not_call_product_exec_verifier_or_poll(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            with patch.object(BatchPreviews,'_closed',side_effect=AssertionError('exec verifier at link')),
                    patch.object(transport.process,'poll',side_effect=AssertionError('poll at link')):
                # Class replacement invalidates the source-role witness, so the
                # direct memory helper must refuse without calling either stub.
                row=binding.renderer_observation(factory,1,desktop,transport,binding.source_packet())
                self.assertTrue(row['errors']);self.assertFalse(row['relations']['rendererGuard._closed'])

    def test_missing_binding_refuses_before_usable(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            desktop.preview_batch.renderer_binding=None
            self.refusal(factory,desktop,transport,controller,destination,'bindingShape')

    def test_foreign_real_transport_launch_keeper_or_process_binding_refuses(self):
        for field in ('transport','launch','process','keeper'):
            with self.subTest(field=field),self.package()as(factory,initial,destination,digest):
                desktop,transport,controller=self.prepare(factory,initial,destination,digest)
                with self.foreign(factory)as foreign:
                    values={'transport':foreign,'launch':foreign.owned_launch,'process':foreign.process,'keeper':object()}
                    captured=desktop.preview_batch.renderer_binding;original=captured[field]
                    try:
                        captured[field]=values[field]
                        self.refusal(factory,desktop,transport,controller,destination,'rendererObjectChain')
                    finally:captured[field]=original

    def test_coherent_foreign_genuine_popen_swap_refuses_actual_pid(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            with self.foreign(factory)as foreign:
                captured=desktop.preview_batch.renderer_binding;launch=transport.owned_launch;original=transport.process
                try:
                    transport.process=launch.process=captured['process']=foreign.process
                    factory.keeper.children[launch.job]=foreign.process
                    self.refusal(factory,desktop,transport,controller,destination,'rendererPopenPID')
                finally:
                    transport.process=launch.process=captured['process']=original
                    factory.keeper.children[launch.job]=original

    def test_noncanonical_process_wrapper_refuses(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            captured=desktop.preview_batch.renderer_binding;launch=transport.owned_launch;original=transport.process
            try:
                transport.process=launch.process=captured['process']=types.SimpleNamespace(pid=original.pid,args=original.args,returncode=None)
                factory.keeper.children[launch.job]=transport.process
                self.refusal(factory,desktop,transport,controller,destination,'rendererClasses')
            finally:
                transport.process=launch.process=captured['process']=original
                factory.keeper.children[launch.job]=original

    def test_nested_bool_float_and_subclass_metadata_refuse(self):
        class Alias(int):pass
        for value in (True,1.0,Alias(1)):
            with self.subTest(type=type(value).__name__),self.package()as(factory,initial,destination,digest):
                desktop,transport,controller=self.prepare(factory,initial,destination,digest)
                owner=desktop.preview_batch.renderer_binding['ownership'];previous=owner['producer']['device']
                try:
                    owner['producer']['device']=value
                    self.refusal(factory,desktop,transport,controller,destination)
                finally:owner['producer']['device']=previous

    def test_coherent_registered_and_launch_float_alias_refuses(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            launch=transport.owned_launch;row=factory.keeper.jobs[launch.job]
            original=launch.ownership['producer']['device'];old=deepcopy(row)
            try:
                launch.ownership['producer']['device']=float(original)
                row['ownership']['producer']['device']=float(original)
                self.refusal(factory,desktop,transport,controller,destination)
            finally:
                launch.ownership['producer']['device']=original;factory.keeper.jobs[launch.job]=old

    def test_selected_producer_digest_refuses(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            desktop.preview_batch.renderer_binding['producerSHA256']='0'*64
            self.refusal(factory,desktop,transport,controller,destination,'rendererSelectedMaterial')

    def test_genuine_outstanding_same_actor_helper_refuses(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            with self.helper(factory,1):
                self.assertFalse(desktop.preview_batch._closed())
                self.refusal(factory,desktop,transport,controller,destination,'rendererRegisteredOwner')

    def test_unrelated_actor_helper_retains_original_live_policy(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            with self.helper(factory,2):
                self.assertTrue(desktop.preview_batch._closed())
                proof=self.link(factory,desktop,transport,controller,destination)
                self.assertTrue(proof['usable'])

    def test_same_kind_second_genuine_renderer_refuses(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            with self.foreign(factory)as foreign:
                row=factory.keeper.jobs[foreign.owned_launch.job];original=row['actor']
                try:
                    row['actor']=1
                    self.refusal(factory,desktop,transport,controller,destination,'rendererRegisteredOwner')
                finally:row['actor']=original

    def test_new_bound_guard_wrong_genuine_function_or_foreign_owner_refuses(self):
        for name in ('bind_renderer','_closed','_renderer_matches'):
            for mutation in ('function','owner'):
                with self.subTest(role=name,mutation=mutation),self.package()as(factory,initial,destination,digest):
                    desktop,transport,controller=self.prepare(factory,initial,destination,digest)
                    batch=desktop.preview_batch
                    foreign=BatchPreviews(batch.root,batch.preview,batch.commands)
                    wrong=batch.stage if mutation=='function'else getattr(foreign,name)
                    setattr(batch,name,wrong)
                    self.refusal(factory,desktop,transport,controller,destination,'rendererGuard.'+name)

    def test_new_static_guard_wrong_function_or_bound_owner_refuses(self):
        for name in ('_typed_equal','_renderer_witness'):
            for mutation in ('function','owner'):
                with self.subTest(role=name,mutation=mutation),self.package()as(factory,initial,destination,digest):
                    desktop,transport,controller=self.prepare(factory,initial,destination,digest)
                    batch=desktop.preview_batch
                    wrong=getattr(batch,'_renderer_witness'if name=='_typed_equal'else'_typed_equal')if mutation=='function'else types.MethodType(getattr(BatchPreviews,name),batch)
                    setattr(batch,name,wrong)
                    self.refusal(factory,desktop,transport,controller,destination,'rendererGuard.'+name)

    def test_binding_replacement_after_raw_disk_is_retained_refusal(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            original=binding.persist_raw;path=destination/'actor.json'
            def replace(p,row):
                observed=original(p,row)
                if p==path:desktop.preview_batch.renderer_binding=dict(desktop.preview_batch.renderer_binding)
                return observed
            with patch.object(binding,'persist_raw',side_effect=replace),self.assertRaises(ValueError):
                self.link(factory,desktop,transport,controller,destination)
            confirm=json.loads((destination/'actor-confirmation.json').read_text())
            self.assertTrue(confirm['errors'])

    def test_real_keeper_abort_zero_exit_refuses_terminal(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            self.link(factory,desktop,transport,controller,destination)
            self.assertEqual(transport.close(),0);factory.keeper.abort()
            self.assertTrue(factory.keeper.closed);self.assertEqual(factory.keeper.process.returncode,0)
            self.assertIs(factory.keeper.ownership['terminal']['normalStop'],False)
            with self.assertRaises(ValueError):self.terminal(factory,initial,destination)
            raw=json.loads((destination/'terminal.json').read_text());self.assertFalse(raw['usable']);self.assertTrue(raw['errors'])

    def test_numeric_keeper_normalstop_alias_refuses_terminal(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            self.link(factory,desktop,transport,controller,destination);fixture.normal_close(factory)
            factory.keeper.ownership['terminal']['normalStop']=1
            with self.assertRaises(ValueError):self.terminal(factory,initial,destination)
            self.assertTrue(json.loads((destination/'terminal.json').read_text())['errors'])

    def test_noninteger_renderer_returncode_refuses_terminal(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            self.link(factory,desktop,transport,controller,destination);fixture.normal_close(factory)
            original=transport.process.returncode
            try:
                transport.process.returncode=0.0
                with self.assertRaises(ValueError):self.terminal(factory,initial,destination)
                self.assertTrue(json.loads((destination/'terminal.json').read_text())['errors'])
            finally:transport.process.returncode=original

    def test_stopped_renderer_cannot_be_linked_as_live(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            self.assertEqual(transport.close(),0)
            self.refusal(factory,desktop,transport,controller,destination,'rendererLiveRegistration')

    def test_terminal_postdisk_binding_replacement_retains_raw_failure(self):
        with self.package()as(factory,initial,destination,digest):
            desktop,transport,controller=self.prepare(factory,initial,destination,digest)
            self.link(factory,desktop,transport,controller,destination)
            path=destination/'terminal.json';original=binding.persist_raw
            def replace(p,row):
                observed=original(p,row)
                if p==path:desktop.preview_batch.renderer_binding=dict(desktop.preview_batch.renderer_binding)
                return observed
            with patch.object(binding,'persist_raw',side_effect=replace),self.assertRaises(ValueError):
                self.terminal(factory,initial,destination)
            self.assertTrue(json.loads((destination/'actual-terminal-binding-confirmation.json').read_text())['errors'])


if __name__=='__main__':unittest.main()
