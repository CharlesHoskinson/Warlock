"""Actual service/lease/journal and confined CPU groups; no native GUI effects.

The CPU guard deliberately skips compositor verification. These tests prove the
new journal callback and quarantine boundaries, not current-window authority.
"""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from native_runtime import NativeFactory, PinnedNativeDesktop
from owned_commands import SealedFile, OwnedCommands
from owned_launch import OwnedLaunch
from service_runtime import RuntimeService, JournalStore, actor_unresolved, process_start


class ActorServiceBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='actor-service-cpu-')
        self.runtime=Path(self.temp.name)
        parent=self.runtime/'hypr-window-motion';parent.mkdir(mode=0o700)
        self.root=parent/'cpu';self.root.mkdir(mode=0o700)
        executable=self.runtime/'inert-executable'
        executable.write_bytes(Path('/usr/bin/cat').read_bytes());executable.chmod(0o700)
        digest=hashlib.sha256(executable.read_bytes()).hexdigest()
        self.env=dict(os.environ,XDG_RUNTIME_DIR=str(self.runtime),
            HYPRLAND_INSTANCE_SIGNATURE='actor-service-cpu',WAYLAND_DISPLAY='never-connect')
        self.environment=patch.dict(os.environ,self.env);self.environment.start()
        guard=SimpleNamespace(env=self.env,session='actor-service-cpu',verify=lambda:None)
        self.factory=NativeFactory(self.root,guard,producer=executable,
            producer_hash=digest,core=executable,core_hash=digest)
        self.service=RuntimeService(self.root,guard.session,self.factory,lambda _:None)
        self.launches=[]

    def tearDown(self):
        for launch in self.launches:
            if launch.process.poll() is None:launch.process.communicate('',timeout=2)
            if not launch.closed:
                try:launch.complete()
                except Exception:pass
            for stream in (launch.process.stdin,launch.process.stdout,launch.process.stderr):
                if stream:stream.close()
        keeper=self.factory.keeper
        if not keeper.closed:
            try:keeper.abort()
            except RuntimeError:
                # An injected service durability fault also refuses publishing
                # crash cleanup. Verify its physical outcome without upgrading
                # that refused publication to successful service completion.
                self.assertTrue(self.service.manager.persistence_failed)
                self.assertTrue(keeper.closed)
                self.assertEqual(keeper.process.returncode,0)
                self.assertFalse(keeper.read_terminal()['normalStop'])
            finally:
                if keeper.process.poll() is None:keeper.detach();keeper.process.wait(timeout=5)
                if not keeper.process.stderr.closed:keeper.process.stderr.close()
        try:self.service.frontend.close(close_manager=False)
        finally:
            self.service.lease.close();self.environment.stop();self.temp.cleanup()

    def launch(self,kind='helper',actor=1):
        with SealedFile('/usr/bin/cat') as executable:
            launch=OwnedLaunch(['/usr/bin/cat'],env=self.env,
                keeper=self.factory.keeper,actor=actor,kind=kind,
                executable_fd=executable.fd,stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.launches.append(launch);return launch

    def finish(self,launch):
        output,error=launch.process.communicate('actual CPU return\n',timeout=2)
        self.assertEqual((output,launch.process.returncode),('actual CPU return\n',0),error)
        launch.complete()

    def test_actual_service_publishes_initial_actor_ledger(self):
        body=self.service.store.read()
        self.assertEqual(body['actorOwnership'],{'jobs':{},'freezes':{},'revisions':{},'fault':False})
        self.assertEqual(body['helperOwnership'],self.factory.keeper.snapshot())
        self.assertIsNone(body['readonlyOwnership'])
        self.assertIs(self.factory.keeper.reservation_lock,self.service.manager.lock)

    def test_initial_actor_publication_failure_closes_exact_keeper_without_success(self):
        self.service.close()
        old=self.factory
        self.factory=NativeFactory(self.root,old.guard,producer=old.producer,
            producer_hash=old.producer_hash,core=old.core,core_hash=old.core_hash)
        original=JournalStore.write
        def refuse_actor(store,body):
            if body.get('actorOwnership') is not None:
                raise OSError('injected initial actor journal durability failure')
            return original(store,body)
        with patch.object(JournalStore,'write',refuse_actor):
            with self.assertRaisesRegex(RuntimeError,'initial actor journal'):
                RuntimeService(self.root,old.guard.session,self.factory,lambda _:None)
        keeper=self.factory.keeper
        self.assertTrue(keeper.actor_fault);self.assertTrue(keeper.closed)
        self.assertEqual(keeper.process.returncode,0)
        self.assertFalse(keeper.read_terminal()['normalStop'])
        self.assertFalse((self.root/'owner.json').exists())

    def test_closed_gate_history_is_durable_before_actual_release(self):
        writes=[];original=self.service.store.write
        def observe(body):
            original(body);writes.append(self.service.store.read())
        with patch.object(self.service.store,'write',side_effect=observe):launch=self.launch()
        rows=[b['actorOwnership']['jobs'].get(launch.job) for b in writes]
        self.assertEqual(next(r for r in rows if r)['phase'],'gated')
        self.assertTrue(any(r and r['phase']=='released' for r in rows))
        current=self.service.store.read()['actorOwnership']['jobs'][launch.job]
        self.assertEqual((current['pid'],current['start']),(launch.process.pid,process_start(launch.process.pid)))
        self.assertIsNone(launch.process.poll());self.finish(launch)
        body=self.service.store.read()
        self.assertEqual(body['helperOwnership']['jobs'],[])
        self.assertEqual(body['actorOwnership']['jobs'][launch.job]['phase'],'closed')
        self.assertEqual(body['actorOwnership'],self.factory.keeper.actor_snapshot())
        self.service.close()
        self.assertEqual(self.service.store.read()['actorOwnership']['jobs'][launch.job]['phase'],'closed')

    def test_service_publication_failure_retains_inventory_and_actual_fault(self):
        original=self.service.store.write
        def fail_at_registration(body):
            if body['actorOwnership'] and body['actorOwnership']['jobs']:
                raise OSError('injected actual service journal fsync failure')
            original(body)
        with patch.object(self.service.store,'write',side_effect=fail_at_registration):
            with self.assertRaises(RuntimeError):self.launch()
        snapshot=self.factory.actor_snapshot()
        self.assertTrue(snapshot['fault']);self.assertEqual(len(snapshot['jobs']),1)
        self.assertTrue(self.service.manager.persistence_failed)
        self.assertTrue(actor_unresolved(snapshot))
        self.assertEqual(snapshot,self.service.snapshot()['actorOwnership'])
        with self.assertRaisesRegex(ValueError,'durability failed'):self.launch()

    def test_native_zero_exit_retains_semantic_gap_in_both_ledgers(self):
        launch=self.launch(kind='native-effect');self.finish(launch)
        body=self.service.store.read();row=body['actorOwnership']['jobs'][launch.job]
        self.assertEqual(row['phase'],'closed');self.assertIsNone(row['returned'])
        self.assertEqual(body['helperOwnership']['jobs'][0]['phase'],'released')
        self.assertTrue(body['helperOwnership']['jobs'][0]['groupEmpty'])
        self.assertTrue(actor_unresolved(body['actorOwnership']))
        with self.assertRaisesRegex(RuntimeError,'actor ledger'):self.factory.close()
        self.assertFalse(self.factory.keeper.read_terminal()['normalStop'])
        self.assertIsNone(self.service.store.read()['actorOwnership']['jobs'][launch.job]['returned'])

    def test_service_quarantine_precedes_manager_capture_disposal(self):
        launch=self.launch(kind='native-export');self.finish(launch)
        with patch.object(self.service.manager,'close') as disposal:
            with self.assertRaisesRegex(RuntimeError,'actor ledger'):self.service.close()
        disposal.assert_not_called()
        self.assertIsNotNone(self.service.lease.fd)
        self.assertTrue((self.root/'owner.json').exists())
        self.assertFalse(self.factory.keeper.closed)

    def test_service_fault_quarantine_precedes_manager_capture_disposal(self):
        self.factory.keeper.actor_fault=True
        with patch.object(self.service.manager,'close') as disposal:
            with self.assertRaisesRegex(RuntimeError,'actor ledger'):self.service.close()
        disposal.assert_not_called();self.assertIsNotNone(self.service.lease.fd)

    def test_healthy_helper_can_drain_before_normal_service_close(self):
        launch=self.launch();self.factory.assert_actor_authority()
        self.finish(launch);self.service.close()
        self.assertTrue(self.factory.keeper.read_terminal()['normalStop'])
        self.assertIsNone(self.service.lease.fd)

    def test_missing_service_actor_inventory_cannot_claim_normal_closure(self):
        launch=self.launch();row=self.factory.keeper.actor_jobs.pop(launch.job)
        try:
            with self.assertRaisesRegex(RuntimeError,'actor ledger'):self.factory.assert_actor_authority()
        finally:self.factory.keeper.actor_jobs[launch.job]=row
        self.finish(launch)

    def test_snapshot_mutation_cannot_change_owned_actor_history(self):
        launch=self.launch();snapshot=self.factory.actor_snapshot()
        snapshot['jobs'].clear();snapshot['fault']=True
        self.assertIn(launch.job,self.factory.keeper.actor_jobs)
        self.assertFalse(self.factory.keeper.actor_fault);self.finish(launch)

    def desktop(self,actor=1):
        directory=self.root/'actors';directory.mkdir(mode=0o700,exist_ok=True)
        desktop=PinnedNativeDesktop(directory/('actor-cpu-'+str(actor)),core=self.factory.core,
            session_guard=self.factory.guard,core_hash=self.factory.core_hash,
            commands=OwnedCommands(self.factory.keeper,self.env,actor),
            retirement_guard=lambda:self.factory.assert_actor_authority(actor),
            retirement_lock=self.service.manager.lock)
        # Janitor runs its real private-file cleanup using an explicit CPU-only
        # client-list fixture. No compositor query/observation is claimed.
        desktop.base.clients=lambda:[]
        return desktop

    def capture(self,desktop):
        source=desktop.root/'0123456789ab-1.png'
        source.write_bytes(b'owned CPU capture fixture');source.chmod(0o600)
        return source

    def test_late_native_return_gap_preserves_actual_owned_capture(self):
        desktop=self.desktop();capture=self.capture(desktop)
        self.factory.assert_actor_authority(1)
        launch=self.launch(kind='native-export');self.finish(launch)
        with self.assertRaisesRegex(RuntimeError,'actor ledger'):
            desktop.release_sources([{'path':str(capture)}])
        with self.assertRaisesRegex(RuntimeError,'actor ledger'):desktop.dispose()
        self.assertEqual(capture.read_bytes(),b'owned CPU capture fixture')
        self.assertTrue(desktop.root.exists())

    def test_other_actors_native_gap_does_not_block_selected_capture_disposal(self):
        desktop=self.desktop();capture=self.capture(desktop)
        launch=self.launch(kind='native-effect',actor=2);self.finish(launch)
        desktop.release_sources([{'path':str(capture)}]);self.assertFalse(capture.exists())
        desktop.dispose();self.assertFalse(desktop.root.exists())
        self.assertIsNone(self.service.store.read()['actorOwnership']['jobs'][launch.job]['returned'])

    def test_actor_fault_preserves_actual_owned_capture_and_directory(self):
        desktop=self.desktop();capture=self.capture(desktop)
        self.factory.keeper.actor_fault=True
        with self.assertRaisesRegex(RuntimeError,'actor ledger'):desktop.dispose()
        self.assertTrue(capture.exists());self.assertTrue(desktop.root.exists())


if __name__=='__main__':unittest.main()
