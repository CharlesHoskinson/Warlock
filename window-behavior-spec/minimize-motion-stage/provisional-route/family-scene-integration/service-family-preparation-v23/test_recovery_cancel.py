"""CPU/kernel cancellation faults: real lease, journal fsync and keeper lifetime."""
from contextlib import contextmanager
from copy import deepcopy
import fcntl
import json
import os
from pathlib import Path
import tempfile
import unittest
from recovery_runtime import NativeRecovery
from service_runtime import RuntimeLease,unresolved,atomic_write
from scene_controller import key
import test_recovery_runtime as baseline

class CancellationTests(unittest.TestCase):
    fixture=baseline.RecoveryTests.fixture
    @contextmanager
    def case(self,operation='toggle'):
        with tempfile.TemporaryDirectory() as raw:
            factory,store,d,actor,body=self.fixture(raw,operation)
            # A deterministic read-only native family fixture for CPU tests.
            # It reports all currently mapped clients with exact core focus.
            def family(window,windows,single=False):
                members=[row for row in windows if row.get('mapped',True)]
                return ([window],window) if single else (deepcopy(members),deepcopy(members[-1]))
            d.family=family
            lease=RuntimeLease(factory.root,'offline')
            try:yield factory,store,d,actor,body,lease
            finally:
                if lease.fd is not None:
                    try:lease.close()
                    except ValueError:os.close(lease.fd);lease.fd=None
    def coordinator(self,factory,store,d,lease,**extras):
        return NativeRecovery(factory,store=store,desktop=d,lease_verify=lease.verify,**extras)
    def assert_cancel(self,result,store,d,actor,reason):
        self.assertEqual(result,store.read());self.assertFalse(unresolved(result));self.assertFalse(actor.exists());self.assertFalse(d.commits)
        plan=result['recovery']['plans'][0];proof=plan['cancellation']
        self.assertEqual(plan['operation'],'cancel');self.assertEqual(proof['reason'],reason);self.assertEqual(proof['outcome'],'non-settlement')
        self.assertTrue(proof['acknowledged']);self.assertNotIn('endpointObserved',plan)
        self.assertEqual(len(proof['observations']),2);self.assertEqual(proof['observations'][0],proof['observations'][1]);self.assertTrue(proof['helperClosures']);self.assertTrue(proof['refreshes'])
        self.assertTrue(all(row['outcome']['oldLifetimeGone'] for row in proof['resources']))
    def test_closed_captured_lifetime_cancels_without_writing_survivors(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);before=deepcopy(d.windows)
            result=self.coordinator(f,s,d,l).recover(b);self.assert_cancel(result,s,d,a,'member-absent');self.assertEqual(d.windows,before)
            self.assertEqual(result['recovery']['plans'][0]['cancellation']['original']['symbolic']['identity'],b['pending'][0]['captured'])
    def test_closed_peer_remains_classified_with_all_old_member_states(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(1);result=self.coordinator(f,s,d,l).recover(b);self.assert_cancel(result,s,d,a,'member-absent')
            states=result['recovery']['plans'][0]['cancellation']['observations'][0]['members'];self.assertEqual([r['state'] for r in states],['present','absent','present'])
            self.assertEqual(states[0]['current']['pinned'],True);self.assertEqual(states[0]['current']['workspace'],{'name':'1'})
    def test_reused_address_records_replacement_without_writing_it(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows[1]['pid']+=10;before=deepcopy(d.windows)
            result=self.coordinator(f,s,d,l).recover(b);self.assert_cancel(result,s,d,a,'member-reused');self.assertEqual(d.windows,before)
            row=result['recovery']['plans'][0]['cancellation']['observations'][0]['members'][1];self.assertNotEqual(row['identity'][2],row['current']['pid'])
    def test_unmapped_old_member_is_not_dropped_from_scope(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows[2]['mapped']=False;result=self.coordinator(f,s,d,l).recover(b);self.assert_cancel(result,s,d,a,'member-unmapped')
            self.assertEqual(len(result['recovery']['plans'][0]['members']),3)
    def test_changed_observed_whole_family_cancels_as_nonsettlement(self):
        with self.case() as (f,s,d,a,b,l):
            p=b['pending'][0];b['scenes']=[dict(actor=1,requested=p['captured'],single=False,members=p['scope'],focus=p['scope'][-1],profile={'managerReceipt':1},direction=p['direction'])]
            foreign=deepcopy(d.windows[0]);foreign.update(address='0xdddd',stableId='dddd',pid=999);d.windows.append(foreign);s.write(b)
            result=self.coordinator(f,s,d,l).recover(b);self.assert_cancel(result,s,d,a,'family-membership-changed')
    def test_known_restore_focus_change_has_explicit_nonsuccess_outcome(self):
        with self.case('restore') as (f,s,d,a,b,l):
            p=b['pending'][0];b['scenes']=[dict(actor=1,requested=p['captured'],single=False,members=p['scope'],focus=p['scope'][0],profile={'managerReceipt':1},direction=p['direction'])];s.write(b)
            result=self.coordinator(f,s,d,l).recover(b);self.assert_cancel(result,s,d,a,'family-focus-changed')
    def test_compatible_family_still_settles_original_toggle(self):
        with self.case() as (f,s,d,a,b,l):
            result=self.coordinator(f,s,d,l).recover(b);self.assertFalse(unresolved(result));self.assertEqual([r[0] for r in d.commits],['minimize']*3)
            self.assertNotIn('cancellation',result['recovery']['plans'][0])
    def test_failed_retired_journal_fsync_keeps_sources_and_no_ack(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);original=s.write
            def fault(value):
                if any(row['phase']=='retired' for row in value['actorResources']):raise OSError('retired fsync fault')
                original(value)
            s.write=fault
            with self.assertRaisesRegex(OSError,'retired fsync'):self.coordinator(f,s,d,l).recover(b)
            archived=s.read();self.assertTrue(a.exists());self.assertEqual(archived['actorResources'][0]['phase'],'directory');self.assertFalse(archived['recovery']['plans']);self.assertFalse(d.commits)
    def test_failed_cancellation_ack_fsync_keeps_sources(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);original=s.write
            def fault(value):
                if value.get('recovery',{}).get('plans'):raise OSError('cancel ack fsync fault')
                original(value)
            s.write=fault
            with self.assertRaisesRegex(OSError,'cancel ack fsync'):self.coordinator(f,s,d,l).recover(b)
            archived=s.read();self.assertTrue(a.exists());self.assertEqual(archived['actorResources'][0]['phase'],'retired');self.assertFalse(archived['recovery']['plans']);self.assertFalse(d.commits)
    def stop_before_disposal(self,f,s,d,a,b,l):
        def fault(*args,**kwargs):
            on_disk=s.read()['recovery']['plans'][0]['cancellation'];self.assertTrue(on_disk['acknowledged']);self.assertTrue(a.exists())
            raise OSError('after durable ack before source disposal')
        with self.assertRaisesRegex(OSError,'after durable ack'):self.coordinator(f,s,d,l,dispose=fault).recover(b)
        return s.read()
    def test_restart_new_owner_refreshes_cancel_then_disposes_sources(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);archived=self.stop_before_disposal(f,s,d,a,b,l);old_nonce=l.nonce
            l.close();new=RuntimeLease(f.root,'offline')
            try:
                result=self.coordinator(f,s,d,new).recover(archived);self.assert_cancel(result,s,d,a,'member-absent')
                proof=result['recovery']['plans'][0]['cancellation'];self.assertEqual(proof['lease']['owner']['nonce'],old_nonce);self.assertNotEqual(proof['refreshes'][-1]['lease']['owner']['nonce'],old_nonce)
            finally:new.close()
    def test_acknowledged_cancellation_does_not_settle_if_closed_member_returns(self):
        with self.case() as (f,s,d,a,b,l):
            saved=d.windows.pop(0);archived=self.stop_before_disposal(f,s,d,a,b,l);d.windows.insert(0,saved)
            result=self.coordinator(f,s,d,l).recover(archived);self.assert_cancel(result,s,d,a,'member-absent')
            self.assertEqual(result['recovery']['plans'][0]['cancellation']['refreshes'][-1]['observations'][0]['members'][0]['state'],'present')
    def test_unstable_fresh_cancel_refresh_preserves_ack_and_sources(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);archived=self.stop_before_disposal(f,s,d,a,b,l);original=d.clients;count=[0]
            def changing():
                count[0]+=1;rows=original();rows[0]['at'][0]+=count[0];return rows
            d.clients=changing
            with self.assertRaisesRegex(ValueError,'changed during cancellation observation'):self.coordinator(f,s,d,l).recover(archived)
            self.assertTrue(a.exists());self.assertTrue(s.read()['pending']);self.assertFalse(d.commits)
    def test_actual_unlock_cannot_acknowledge_or_dispose(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);fcntl.flock(l.fd,fcntl.LOCK_UN);before=s.read()
            with self.assertRaisesRegex(ValueError,'no longer holds exclusion'):self.coordinator(f,s,d,l).recover(b)
            self.assertEqual(s.read(),before);self.assertTrue(a.exists());self.assertFalse(d.commits)
    def test_actual_owner_nonce_replacement_cannot_cancel(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);atomic_write(l.owner_path,json.dumps(dict(l.owner,nonce='c'*32)).encode());before=s.read()
            with self.assertRaisesRegex(ValueError,'owner PID/start/nonce'):self.coordinator(f,s,d,l).recover(b)
            self.assertEqual(s.read(),before);self.assertTrue(a.exists());self.assertFalse(d.commits)
    def test_fake_lease_dict_is_not_cancellation_authority(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0)
            with self.assertRaisesRegex(ValueError,'actual bound RuntimeLease'):NativeRecovery(f,store=s,desktop=d,lease_verify=lambda:dict(l.owner)).recover(b)
            self.assertTrue(a.exists());self.assertFalse(d.commits)
    def test_unknown_source_material_preserves_nonsettlement_and_quarantines_api(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);foreign=a/'unknown';foreign.write_bytes(b'owned but unsupported');foreign.chmod(0o600)
            with self.assertRaisesRegex(ValueError,'unexpected actor material'):self.coordinator(f,s,d,l).recover(b)
            self.assertTrue(a.exists());self.assertEqual(foreign.read_bytes(),b'owned but unsupported');self.assertTrue(unresolved(s.read()));self.assertFalse(d.commits)
    def test_replaced_source_directory_cannot_be_deleted_after_cancel_ack(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);archived=self.stop_before_disposal(f,s,d,a,b,l);old=a.with_name(a.name+'-retained');a.rename(old);a.mkdir(mode=0o700)
            with self.assertRaisesRegex(ValueError,'identity/private mode changed'):self.coordinator(f,s,d,l).recover(archived)
            self.assertTrue(a.exists());self.assertTrue(old.exists());self.assertTrue(unresolved(s.read()));self.assertFalse(d.commits)
    def test_newer_exact_receipt_cannot_be_cancelled_by_old_scope(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(1);b['serial']=2;b['recoveryIntent']['receipts'][1][1]=2;b['receipts']=deepcopy(b['recoveryIntent']['receipts']);s.write(b)
            with self.assertRaisesRegex(ValueError,'receipt and direction provenance differ'):self.coordinator(f,s,d,l).recover(b)
            self.assertTrue(a.exists());self.assertFalse(d.commits)
    def test_partial_returned_result_preserved_when_next_member_is_reused(self):
        with self.case('minimize') as (f,s,d,a,b,l):
            original=d.commit
            def changing(*args):
                original(*args)
                if len(d.commits)==1:d.windows[1]['pid']+=10
            d.commit=changing
            original_write=s.write;ack_seen=[]
            def observe_ack(value):
                plans=value.get('recovery',{}).get('plans',[])
                if plans and plans[0]['operation']=='cancel' and not ack_seen:
                    self.assertTrue(a.exists());self.assertTrue((a/'0123456789ab-1.png').exists());ack_seen.append(True)
                original_write(value)
            s.write=observe_ack
            result=self.coordinator(f,s,d,l).recover(b);plan=result['recovery']['plans'][0];self.assertTrue(ack_seen)
            self.assertFalse(unresolved(result));self.assertEqual(len(d.commits),1);self.assertEqual(plan['operation'],'cancel');self.assertEqual(plan['results'],plan['priorResults']);self.assertEqual(len(plan['results']),1);self.assertEqual(plan['cancellation']['prepared']['operation'],'minimize');self.assertNotIn('endpointObserved',plan)
    def test_acknowledgment_false_refuses_before_disposal(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);archived=self.stop_before_disposal(f,s,d,a,b,l);archived['recovery']['plans'][0]['cancellation']['acknowledged']=False;s.write(archived)
            with self.assertRaisesRegex(ValueError,'explicit non-settlement'):self.coordinator(f,s,d,l).recover(archived)
            self.assertTrue(a.exists());self.assertFalse(d.commits)
    def test_forged_prior_native_result_refuses_resume(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);archived=self.stop_before_disposal(f,s,d,a,b,l);plan=archived['recovery']['plans'][0];forged=dict(identity=plan['scope'][1],operation='minimize',receipt=1,guardedCoreReturned=True);plan['results']=[forged];plan['priorResults']=[forged];s.write(archived)
            with self.assertRaisesRegex(ValueError,'prior returned native results'):self.coordinator(f,s,d,l).recover(archived)
            self.assertTrue(a.exists());self.assertFalse(d.commits)

    def test_completed_cancellation_callback_is_idempotent(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);first=self.coordinator(f,s,d,l).recover(b)
            result=self.coordinator(f,s,d,l).recover(first)
            self.assertFalse(unresolved(result));self.assertFalse(d.commits);self.assertEqual(len(result['recoveryHistory']),1)
    def test_forged_observation_status_refuses_before_disposal(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);archived=self.stop_before_disposal(f,s,d,a,b,l)
            for observation in archived['recovery']['plans'][0]['cancellation']['observations']:observation['members'][1]['state']='absent'
            s.write(archived)
            with self.assertRaisesRegex(ValueError,'status differs'):self.coordinator(f,s,d,l).recover(archived)
            self.assertTrue(a.exists());self.assertFalse(d.commits)
    def test_missing_retained_old_helper_proof_refuses_before_disposal(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);archived=self.stop_before_disposal(f,s,d,a,b,l);archived['recovery']['plans'][0]['cancellation']['helperClosures']=[];s.write(archived)
            with self.assertRaisesRegex(ValueError,'retain exact old helper'):self.coordinator(f,s,d,l).recover(archived)
            self.assertTrue(a.exists());self.assertFalse(d.commits)
    def test_prepared_original_endpoint_cannot_be_changed_in_cancelled_history(self):
        with self.case('minimize') as (f,s,d,a,b,l):
            original=d.commit
            def changing(*args):
                original(*args)
                if len(d.commits)==1:d.windows[1]['pid']+=10
            d.commit=changing;completed=self.coordinator(f,s,d,l).recover(b)
            completed['recovery']['plans'][0]['cancellation']['prepared']['operation']='restore';s.write(completed)
            with self.assertRaisesRegex(ValueError,'constant endpoint changed'):self.coordinator(f,s,d,l).recover(completed)
            self.assertEqual(len(d.commits),1)
    def test_unfinished_actual_native_effect_cannot_cancel_even_after_keeper_empty(self):
        with self.case() as (f,s,d,a,b,l):
            from helper_supervisor import Keeper
            from owned_commands import SealedFile
            from owned_launch import OwnedLaunch
            keeper=Keeper(f.root,f.guard.env,lambda body:None)
            with SealedFile('/usr/bin/true') as selected:
                launch=OwnedLaunch(['/usr/bin/true'],env=f.guard.env,keeper=keeper,kind='native-effect',actor=1,executable_fd=selected.fd)
            launch.process.wait(timeout=2);keeper.detach();keeper.process.wait(timeout=5);keeper.process.stderr.close()
            b['helperOwnership']=keeper.snapshot();s.write(b);d.windows.pop(0);before=s.read()
            with self.assertRaisesRegex(ValueError,'unfinished native export/effect'):self.coordinator(f,s,d,l).recover(b)
            self.assertEqual(s.read(),before);self.assertTrue(a.exists());self.assertFalse(d.commits)
    def test_real_startup_lease_with_bound_socket_is_not_cancel_authority(self):
        with self.case() as (f,s,d,a,b,l):
            d.windows.pop(0);l.bound((1,2))
            with self.assertRaisesRegex(ValueError,'startup runtime/session'):self.coordinator(f,s,d,l).recover(b)
            self.assertTrue(a.exists());self.assertFalse(d.commits)
    def test_reserved_absent_source_restarts_after_durable_cancel_without_inference(self):
        with self.case() as (f,s,d,a,b,l):
            (a/'0123456789ab-1.png').unlink();a.rmdir();b['actorResources'][0]['phase']='reserved';b['actorResources'][0]['directory']['identity']=None;s.write(b);d.windows.pop(0)
            def fault(*args,**kwargs):raise OSError('reserved disposal crash')
            with self.assertRaisesRegex(OSError,'reserved disposal'):self.coordinator(f,s,d,l,dispose=fault).recover(b)
            archived=s.read();self.assertEqual(archived['actorResources'][0]['phase'],'retired')
            result=self.coordinator(f,s,d,l).recover(archived);self.assert_cancel(result,s,d,a,'member-absent')

    def test_unplanned_empty_scene_uses_exact_pending_scope_for_recovery(self):
        with self.case() as (f,s,d,a,b,l):
            p=b['pending'][0];b['scenes']=[dict(actor=1,requested=p['captured'],single=False,members=[],focus=None,profile={'managerReceipt':1},direction=p['direction'])];s.write(b)
            result=self.coordinator(f,s,d,l).recover(b)
            self.assertFalse(unresolved(result));self.assertEqual([r[0] for r in d.commits],['minimize']*3);self.assertEqual(len(result['recovery']['plans'][0]['scope']),3)

if __name__=='__main__':unittest.main()
