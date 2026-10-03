from copy import deepcopy
from dataclasses import asdict
import hashlib
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from helper_supervisor import Keeper
from recovery_runtime import NativeRecovery
from service_runtime import JournalStore,unresolved
from direction import Direction
from recovery_intent import reconstruct
from test_scene_controller import Desktop

class FreshDesktop(Desktop):
    def monitors(self):return [dict(name='offline',id=1,x=0,y=0,width=1000,height=800,scale=1,transform=0,activeWorkspace=dict(id=1,name='1'))]

class RecoveryTests(unittest.TestCase):
    def fixture(self,raw,operation='toggle'):
        root=Path(raw);actors=root/'actors';actors.mkdir(mode=0o700);actor=actors/('actor-1-'+'a'*32);actor.mkdir(mode=0o700)
        capture=actor/'0123456789ab-1.png';capture.write_bytes(b'exact retained capture');capture.chmod(0o600)
        env=dict(os.environ,XDG_RUNTIME_DIR=str(root),HYPRLAND_INSTANCE_SIGNATURE='offline',WAYLAND_DISPLAY='never-connect')
        keeper=Keeper(root,env,lambda value:None);keeper.stop();helper=keeper.snapshot()
        d=FreshDesktop();a=d.windows[0];captured=[a['address'],a['stableId'],a['pid']]
        scope=[[w['address'],w['stableId'],w['pid']] for w in d.windows]
        ledger=dict(anchors=[],events=[dict(receipt=1,captured=captured,command=operation)],receipts=[[v,1] for v in scope])
        inode=actor.stat();parent=actors.stat()
        body=dict(version=1,session='offline',snapshot=1,serial=1,actorSerial=1,recoveryVersion=1,recoveryIntent=ledger,receipts=ledger['receipts'],
            pending=[dict(actor=1,receipt=1,captured=captured,scope=scope,operation=operation,single=False,direction=asdict(Direction(operation,identity=tuple(captured) if operation in ('toggle','activate') else None)))],scenes=[],
            actorResources=[dict(actor=1,phase='directory',renderer=None,directory=dict(path=str(actor),parentIdentity=[parent.st_dev,parent.st_ino],identity=[inode.st_dev,inode.st_ino]))],liveActors=[1],retiringActors=[],helperOwnership=helper)
        guard=SimpleNamespace(session='offline',env=env,verify=lambda:None);factory=SimpleNamespace(root=root,guard=guard,producer_hash='e'*64,core='unused',core_hash='f'*64)
        store=JournalStore(root,'offline');store.write(body)
        return factory,store,d,actor,store.read()
    def test_actual_private_journal_and_owned_capture_settle_complete_family(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw)
            result=NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertEqual(result,store.read());self.assertFalse(unresolved(result));self.assertFalse(actor.exists())
            self.assertEqual([v[0] for v in d.commits],['minimize']*3)
            self.assertEqual(result['recovery']['state'],'completed');self.assertTrue(result['recovery']['plans'][0]['endpointObserved'])
    def test_crash_after_member_write_keeps_original_toggle_resolution(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw)
            original=store.write
            def fault(value):
                if value.get('recovery',{}).get('plans') and len(value['recovery']['plans'][0]['results'])==1:raise OSError('after actual member write before durable result')
                original(value)
            store.write=fault
            with self.assertRaisesRegex(OSError,'actual member write'):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertEqual(d.windows[0]['workspace']['name'],'special:win-minimized')
            archived=store.read();self.assertEqual(archived['recovery']['plans'][0]['operation'],'minimize');self.assertFalse(archived['recovery']['plans'][0]['results'])
            store.write=original
            result=NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(archived)
            self.assertFalse(unresolved(result));self.assertTrue(all(w['workspace']['name']=='special:win-minimized' for w in d.windows));self.assertEqual([v[0] for v in d.commits],['minimize']*4)
    def test_malformed_unrelated_anchor_refuses_before_resource_or_journal_change(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);body['recoveryIntent']['anchors'].append(dict(identity=['0xdd','dd',44],receipt=True,direction=asdict(Direction('restore'))));store.write(body)
            before=(factory.root/'journal.json').read_bytes()
            with self.assertRaises(ValueError):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertEqual((factory.root/'journal.json').read_bytes(),before);self.assertTrue(actor.exists());self.assertFalse(d.commits)
    def test_missing_helper_ownership_refuses_before_source_disposal(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);body.pop('helperOwnership');store.write(body)
            with self.assertRaisesRegex(ValueError,'helper keeper ownership'):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertTrue(actor.exists());self.assertFalse(d.commits)
    def test_unfinished_native_export_refuses_even_with_empty_old_groups(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw)
            from owned_commands import SealedFile
            from owned_launch import OwnedLaunch
            keeper=Keeper(factory.root,factory.guard.env,lambda value:None)
            with SealedFile('/usr/bin/true') as selected:
                launch=OwnedLaunch(['/usr/bin/true'],env=factory.guard.env,keeper=keeper,kind='native-export',actor=1,executable_fd=selected.fd)
            launch.process.wait(timeout=2);keeper.detach();keeper.process.wait(timeout=5);keeper.process.stderr.close()
            body['helperOwnership']=keeper.snapshot();store.write(body)
            with self.assertRaisesRegex(ValueError,'unfinished native export'):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertTrue(actor.exists());self.assertFalse(d.commits)
    def test_old_keeper_nonce_swap_refuses_before_disposal(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);body['helperOwnership']['keeper']['nonce']='b'*32;store.write(body)
            with self.assertRaisesRegex(ValueError,'invocation differs'):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertTrue(actor.exists());self.assertFalse(d.commits)
    def test_completed_callback_is_idempotent(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);first=NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            result=NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(first)
            self.assertFalse(unresolved(result));self.assertEqual(len(d.commits),3)
    def test_each_fresh_member_must_have_latest_exact_owner(self):
        with tempfile.TemporaryDirectory() as raw:
            _,_,_,_,body=self.fixture(raw);ledger=body['recoveryIntent'];ledger['receipts'][1][1]=2
            with self.assertRaises(ValueError):reconstruct(ledger,[v[0] for v in ledger['receipts']],2)
    def test_prepared_endpoint_swap_refuses_before_native_resume(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);original=store.write
            def fault(value):
                if value.get('recovery',{}).get('state')=='settling':raise OSError('before native')
                original(value)
            store.write=fault
            with self.assertRaises(OSError):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            archived=store.read();archived['recovery']['plans'][0]['operation']='restore';store.write=original;store.write(archived)
            with self.assertRaisesRegex(ValueError,'constant endpoint changed'):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(archived)
            self.assertFalse(d.commits)

    def test_duplicate_fresh_clients_quarantine_without_native_effect(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);original=d.clients
            d.clients=lambda:original()+[original()[0]]
            with self.assertRaisesRegex(ValueError,'duplicate address'):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertFalse(d.commits);self.assertTrue(store.read()['pending'])
    def test_output_change_during_observation_quarantines_endpoint(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);count=[0];original=d.monitors
            def changing():
                count[0]+=1;values=original();values[0]['x']=count[0];return values
            d.monitors=changing
            with self.assertRaisesRegex(ValueError,'changed during recovery observation'):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertFalse(d.commits);self.assertTrue(store.read()['pending'])
    def test_fresh_reused_member_cannot_receive_old_endpoint(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);d.windows[1]['pid']+=1
            with self.assertRaises(ValueError):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertFalse(d.commits);self.assertTrue(store.read()['pending'])
    def test_mid_settlement_family_change_preserves_first_result_and_refuses_rest(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw,operation='minimize');original=d.commit
            def changing(*args):
                original(*args)
                if len(d.commits)==1:d.windows[1]['pid']+=1
            d.commit=changing
            with self.assertRaises(ValueError):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            archived=store.read();self.assertEqual(len(d.commits),1);self.assertEqual(len(archived['recovery']['plans'][0]['results']),1);self.assertTrue(archived['pending'])
    def test_captured_known_focus_is_retained_when_pending_overlays_same_receipt(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw,operation='restore');pending=body['pending'][0]
            body['scenes']=[dict(actor=1,requested=pending['captured'],single=False,members=pending['scope'],focus=pending['scope'][0],profile={'managerReceipt':1},direction=pending['direction'])];store.write(body)
            with self.assertRaisesRegex(ValueError,'captured recovery focus differs'):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertFalse(d.commits)
    def test_unknown_actor_material_preserves_all_files_and_pending(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);unknown=actor/'foreign';unknown.write_bytes(b'exact');unknown.chmod(0o600)
            with self.assertRaisesRegex(ValueError,'unexpected actor material'):NativeRecovery(factory,store=store,desktop=d,lease_verify=lambda:None).recover(body)
            self.assertEqual(unknown.read_bytes(),b'exact');self.assertTrue((actor/'0123456789ab-1.png').exists());self.assertFalse(d.commits);self.assertTrue(store.read()['pending'])

    def test_missing_actual_lease_binding_refuses_before_old_resource_mutation(self):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw);before=(factory.root/'journal.json').read_bytes()
            with self.assertRaisesRegex(ValueError,'actual acquired runtime lease binding'):NativeRecovery(factory,store=store,desktop=d).recover(body)
            self.assertEqual((factory.root/'journal.json').read_bytes(),before);self.assertTrue(actor.exists());self.assertFalse(d.commits)

if __name__=='__main__':unittest.main()
