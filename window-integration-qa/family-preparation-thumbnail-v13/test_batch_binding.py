"""Actual candidate class/callback/actor binding, with kernel lease fixtures."""
import importlib.util
import json
from pathlib import Path
import types
import unittest
from unittest.mock import patch

import module_binding as binding
import test_actual_binding as inherited
from batch_preview import BatchPreviews
from owned_commands import OwnedCommands


class ModuleCoverageTests(unittest.TestCase):
    def test_missing_batch_or_extra_source_never_yields_complete_observation(self):
        for selected in (tuple(n for n in binding.MODULES if n!='batch_preview'),binding.MODULES+('service_main',),binding.MODULES[:-1]+(binding.MODULES[0],)):
            with self.subTest(selected=selected),patch.object(binding,'MODULES',selected):
                raw=binding._observe('invalid-module-coverage')
                self.assertTrue(raw['errors']);self.assertFalse(raw['usable'])


class BatchBindingKernelTests(unittest.TestCase):
    setUp=inherited.OwnerKernelTests.setUp
    tearDown=inherited.OwnerKernelTests.tearDown
    query=inherited.OwnerKernelTests.query
    package=inherited.OwnerKernelTests.package
    bound=inherited.OwnerKernelTests.bound
    actor=inherited.OwnerKernelTests.actor

    def genuine_actor(self,factory):
        desktop,transport,controller=self.actor(factory)
        source=binding.SERVICE/'production_motion_6d9.py'
        spec=importlib.util.spec_from_file_location('_cpu_batch_binding_actor',source)
        desktop.production=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(desktop.production)
        desktop.production.subprocess=desktop.commands
        desktop.production.RUNTIME=Path(self.env['XDG_RUNTIME_DIR'])
        desktop.base=object.__new__(desktop.production.Desktop)
        return desktop,transport,controller

    def test_actual_batch_callback_objects_and_roots_captured(self):
        with self.package() as (factory,initial,destination,digest):
            self.bound(factory,initial,destination,digest)
            desktop,transport,controller=self.genuine_actor(factory)
            proof=binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json')
            self.assertTrue(proof['usable'])
            self.assertEqual(proof['batch']['instanceID'],id(desktop.preview_batch))
            self.assertEqual(proof['batch']['commandsID'],id(desktop.commands))
            for name in ('desktop.finish_capture_previews','batch.stage','batch.finish','batch.discard','batch.require_releasable','batch.require_disposable'):
                self.assertIn(name,proof['callbacks'])
            confirm=json.loads(Path(proof['confirmation']['path']).read_text())
            self.assertEqual(confirm['batch'],proof['batch'])
            self.assertTrue(all(confirm['batchRelations'].values()))

    def test_individually_valid_foreign_commands_root_preview_or_actor_refuse(self):
        for field in ('commands','root','preview','actor','class','finisher'):
            with self.subTest(field=field),self.package() as (factory,initial,destination,digest):
                self.bound(factory,initial,destination,digest)
                desktop,transport,controller=self.genuine_actor(factory)
                if field=='commands':desktop.preview_batch.commands=OwnedCommands(None,self.env,1,readonly=self.reader)
                elif field=='root':desktop.preview_batch.root=desktop.root.with_name('other-actor')
                elif field=='preview':desktop.preview_batch.preview=desktop.preview_batch.preview.with_name('other-previews')
                elif field=='actor':desktop.commands.actor=True
                elif field=='class':desktop.preview_batch=types.SimpleNamespace(**desktop.preview_batch.__dict__)
                else:desktop.finish_capture_previews=desktop.preview_batch.finish
                with self.assertRaises(ValueError):binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json')
                raw=json.loads((destination/'actor.json').read_text())
                self.assertTrue(raw['errors']);self.assertFalse(raw['usable'])
                self.assertFalse(all(raw['relations'].values()))

    def test_individually_valid_batch_replacement_after_disk_refuses(self):
        with self.package() as (factory,initial,destination,digest):
            self.bound(factory,initial,destination,digest)
            desktop,transport,controller=self.genuine_actor(factory)
            path=destination/'actor.json';real=binding.persist_raw
            def replace_after_disk(p,row):
                result=real(p,row)
                if p==path:desktop.preview_batch=BatchPreviews(desktop.root,Path(self.env['XDG_RUNTIME_DIR'])/'hypr-window-previews',desktop.commands)
                return result
            with patch.object(binding,'persist_raw',side_effect=replace_after_disk),self.assertRaises(ValueError):
                binding.linked_actor(factory,1,desktop,transport,controller,path)
            confirm=json.loads((destination/'actor-confirmation.json').read_text())
            self.assertTrue(confirm['errors'])

    def test_initial_genuine_wrong_batch_method_role_refuses(self):
        substitutions={'stage':'finish','finish':'stage','discard':'require_releasable','require_releasable':'discard','require_disposable':'require_idle'}
        for name,wrong in substitutions.items():
            with self.subTest(role=name),self.package() as (factory,initial,destination,digest):
                self.bound(factory,initial,destination,digest);desktop,transport,controller=self.genuine_actor(factory)
                method=getattr(desktop.preview_batch,wrong)
                self.assertIs(method.__self__,desktop.preview_batch)
                setattr(desktop.preview_batch,name,method)
                with self.assertRaises(ValueError):binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json')
                raw=json.loads((destination/'actor.json').read_text())
                self.assertFalse(raw['usable']);self.assertTrue(raw['errors']);self.assertFalse(raw['relations']['batchCallback.'+name])

    def test_initial_genuine_expected_function_bound_to_foreign_owner_refuses(self):
        from native_desktop import NativeDesktop
        for name in ('stage','finish','discard','require_releasable','require_disposable','finisher'):
            with self.subTest(role=name),self.package() as (factory,initial,destination,digest):
                self.bound(factory,initial,destination,digest);desktop,transport,controller=self.genuine_actor(factory)
                if name=='finisher':
                    foreign=object.__new__(NativeDesktop)
                    desktop.finish_capture_previews=foreign.finish_capture_previews
                    self.assertIs(desktop.finish_capture_previews.__func__,NativeDesktop.finish_capture_previews)
                    relation='finisherOwner'
                else:
                    foreign=BatchPreviews(desktop.root,desktop.preview_batch.preview,desktop.commands)
                    setattr(desktop.preview_batch,name,getattr(foreign,name))
                    self.assertIs(getattr(desktop.preview_batch,name).__func__,getattr(BatchPreviews,name))
                    relation='batchCallback.'+name
                with self.assertRaises(ValueError):binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json')
                raw=json.loads((destination/'actor.json').read_text())
                self.assertFalse(raw['usable']);self.assertTrue(raw['errors']);self.assertFalse(raw['relations'][relation])

    def terminal(self,factory,initial,destination):
        import renderer_binding_fixture as fixture
        fixture.normal_close(factory)
        self.query()
        journal=self.store.read()
        import os,service_runtime
        journal['helperOwnership']={'keeper':{'servicePID':os.getpid(),'serviceStart':service_runtime.process_start(os.getpid()),'rootIdentity':list(self.lease.root_identity)}}
        self.store.write(journal);self.lease.close()
        service=types.SimpleNamespace(lease=self.lease,store=self.store,closed=True,failure=None)
        modules=binding._observe('terminal',previous=initial)
        return binding.archive_final(factory,service,destination/'terminal.json',modules)

    def install_actor(self,factory,destination):
        desktop,transport,controller=self.genuine_actor(factory)
        proof=binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json')
        factory.observed_bindings=[proof];factory.observed_controllers=[(1,controller)]
        return desktop

    def test_exact_actual_terminal_batch_and_postdisk_callbacks(self):
        with self.package() as (factory,initial,destination,digest):
            self.bound(factory,initial,destination,digest);desktop=self.install_actor(factory,destination)
            result=self.terminal(factory,initial,destination)
            self.assertTrue(result['usable'])
            self.assertEqual(result['terminalBatchConfirmation'][0]['batch']['instanceID'],id(desktop.preview_batch))
            confirmation=json.loads(Path(result['confirmation']['path']).read_text())
            self.assertEqual(confirmation['terminalBatchConfirmation'],result['terminalBatchConfirmation'])

    def terminal_replacement(self,field):
        with self.package() as (factory,initial,destination,digest):
            self.bound(factory,initial,destination,digest);desktop=self.install_actor(factory,destination)
            if field=='batch':desktop.preview_batch=BatchPreviews(desktop.root,Path(self.env['XDG_RUNTIME_DIR'])/'hypr-window-previews',desktop.commands)
            else:desktop.preview_batch.stage=desktop.preview_batch.finish
            with self.assertRaises(ValueError):self.terminal(factory,initial,destination)
            raw=json.loads((destination/'terminal.json').read_text());self.assertTrue(raw['errors']);self.assertFalse(raw['usable'])

    def test_terminal_still_valid_replaced_batch_refuses(self):
        self.terminal_replacement('batch')

    def test_terminal_replaced_callback_refuses(self):
        self.terminal_replacement('callback')

    def test_terminal_postdisk_replacement_has_raw_refusal(self):
        with self.package() as (factory,initial,destination,digest):
            self.bound(factory,initial,destination,digest);desktop=self.install_actor(factory,destination)
            path=destination/'terminal.json';real=binding.persist_raw
            def replace_after_disk(p,row):
                result=real(p,row)
                if p==path:desktop.preview_batch=BatchPreviews(desktop.root,Path(self.env['XDG_RUNTIME_DIR'])/'hypr-window-previews',desktop.commands)
                return result
            with patch.object(binding,'persist_raw',side_effect=replace_after_disk),self.assertRaises(ValueError):self.terminal(factory,initial,destination)
            confirmation=json.loads((destination/'actual-terminal-binding-confirmation.json').read_text());self.assertTrue(confirmation['errors'])


if __name__=='__main__':unittest.main()
