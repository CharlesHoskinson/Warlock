"""Exact terminal proof faults using actual CPU ELF children, never Wayland."""
from contextlib import contextmanager
from copy import deepcopy
import os
from pathlib import Path
import select
import tempfile
import time
import unittest
from unittest.mock import patch
from helper_supervisor import Keeper
from owned_commands import SealedFile
from recovery_resources import gated_process,renderer_terminal_state,retire_renderer
from recovery_runtime import NativeRecovery
from service_runtime import RuntimeLease,unresolved
import test_recovery_runtime as baseline
import test_recovery_resources as resource_baseline

class RendererTerminalTests(unittest.TestCase):
    @contextmanager
    def legacy(self,executable='/usr/bin/true'):
        with tempfile.TemporaryDirectory() as raw:
            f,s,d,a,b=baseline.RecoveryTests().fixture(raw);owners=[]
            with SealedFile(executable) as selected:
                child=gated_process('/proc/self/fd/'+str(selected.fd),env=f.guard.env,pass_fds=(selected.fd,),record=owners.append,process_factory=__import__('fixture_legacy_ready').ready_process)
            row=owners[0];f.producer_hash=row['producer']['sha256'];b['actorResources'][0].update(phase='launched',renderer=row);s.write(b)
            lease=RuntimeLease(f.root,'offline')
            try:yield f,s,d,a,b,lease,child,row
            finally:
                if lease.fd is not None:lease.close()
                if child.poll() is None:child.terminate()
                child.wait(timeout=3)
                for stream in (child.stdin,child.stdout,child.stderr):stream.close()
    def zombie(self,child):
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            state=Path(f'/proc/{child.pid}/stat').read_text().rsplit(') ',1)[1].split()[0]
            if state=='Z':return
            time.sleep(.002)
        self.fail('actual unreaped child never reached Z')
    def incompatible(self,d):
        d.windows.pop(0);d.family=lambda w,windows,single=False:(deepcopy(windows),deepcopy(windows[-1]))
    def coordinator(self,f,s,d,l,**kw):return NativeRecovery(f,store=s,desktop=d,lease_verify=l.verify,**kw)
    def test_actual_unreaped_legacy_cancel_ack_then_dispose_without_native_write(self):
        with self.legacy() as (f,s,d,a,b,l,child,row):
            self.zombie(child);self.incompatible(d)
            self.coordinator(f,s,d,l).preflight(b)
            witness=renderer_terminal_state(row)
            self.assertEqual((witness['kind'],witness['observed']['state']),('exited','Z'));self.assertTrue(witness['oldLifetimeGone'])
            self.assertEqual(retire_renderer(row,expected_environment=row['environment']),dict(oldLifetimeGone=True,signaled=False,forced=False))
            result=self.coordinator(f,s,d,l).recover(b)
            self.assertFalse(unresolved(result));self.assertFalse(a.exists());self.assertFalse(d.commits)
            proof=result['recovery']['plans'][0]['cancellation'];self.assertTrue(proof['acknowledged']);self.assertEqual(proof['outcome'],'non-settlement')
    def test_same_unreaped_lifetime_restart_refreshes_durable_ack(self):
        with self.legacy() as (f,s,d,a,b,l,child,row):
            self.zombie(child);self.incompatible(d)
            def stop(*args,**kw):
                if kw.get('inspection_only'):return {'directoryGone':False}
                self.assertTrue(s.read()['recovery']['plans'][0]['cancellation']['acknowledged']);self.assertTrue(a.exists());raise OSError('after durable ack')
            with self.assertRaisesRegex(OSError,'after durable ack'):self.coordinator(f,s,d,l,dispose=stop).recover(b)
            previous=s.read();l.close();new=RuntimeLease(f.root,'offline')
            try:result=self.coordinator(f,s,d,new).recover(previous)
            finally:new.close()
            self.assertFalse(unresolved(result));self.assertFalse(a.exists());self.assertFalse(d.commits);self.assertEqual(renderer_terminal_state(row)['observed']['state'],'Z')
    def test_same_live_lifetime_is_not_terminal(self):
        with self.legacy('/usr/bin/cat') as (f,s,d,a,b,l,child,row):
            child.stdin.write('actual live CPU child\n');child.stdin.flush();self.assertEqual(child.stdout.readline(),'actual live CPU child\n')
            self.assertEqual(renderer_terminal_state(row)['kind'],'running');self.assertFalse(renderer_terminal_state(row)['oldLifetimeGone']);self.assertIsNone(child.poll())
    def test_reused_start_never_signals_actual_live_replacement(self):
        with self.legacy('/usr/bin/cat') as (f,s,d,a,b,l,child,row):
            reused=dict(row,start=row['start']+1);w=renderer_terminal_state(reused)
            self.assertEqual(w['kind'],'reused');self.assertTrue(w['oldLifetimeGone']);self.assertIsNone(child.poll())
    def test_reaped_old_pid_is_separately_absent(self):
        with self.legacy() as (f,s,d,a,b,l,child,row):
            child.wait(timeout=3);w=renderer_terminal_state(row);self.assertEqual(w['kind'],'absent');self.assertIsNone(w['observed']);self.assertTrue(w['oldLifetimeGone'])
    def test_modern_zombie_pidfd_does_not_bless_nonempty_keeper_group(self):
        resources=resource_baseline.ResourceTests()
        with tempfile.TemporaryDirectory() as raw:
            keeper,launch,env=resources.launched(Path(raw))
            try:
                launch.process.terminate();self.zombie(launch.process)
                self.assertTrue(renderer_terminal_state(launch.ownership)['oldLifetimeGone'])
                with self.assertRaisesRegex(ValueError,'keeper refused'):keeper.complete(launch.job)
                self.assertIn(launch.job,keeper.jobs)
            finally:
                # The refused command intentionally tears down keeper ingress.
                # Reap this exact direct CPU child before keeper crash cleanup;
                # this is fault cleanup, never normal completion acceptance.
                launch.process.wait(timeout=3);keeper.connection.close();keeper.process.wait(timeout=5)
                self.assertNotEqual(keeper.process.returncode,0)
                # No terminal proof is invented for this rejected fault path.
                keeper.process.stderr.read();keeper.process.stderr.close()
                for stream in (launch.process.stdin,launch.process.stdout,launch.process.stderr):stream.close()
    def test_running_durable_retired_claim_refuses_without_disposal(self):
        with self.legacy('/usr/bin/cat') as (f,s,d,a,b,l,child,row):
            b['actorResources'][0].update(phase='retired',outcome=dict(oldLifetimeGone=True,directoryGone=False,allocationPhase='launched'));s.write(b)
            self.incompatible(d)
            with self.assertRaisesRegex(ValueError,'old live renderer'):self.coordinator(f,s,d,l).recover(b)
            self.assertTrue(a.exists());self.assertFalse(d.commits);self.assertIsNone(child.poll())
    def test_unknown_and_malformed_stat_quarantine(self):
        with self.legacy('/usr/bin/cat') as (f,s,d,a,b,l,child,row):
            raw=Path(f'/proc/{child.pid}/stat').read_text();prefix,tail=raw.rsplit(') ',1);fields=tail.split();fields[0]='?'
            for value in (prefix+') '+' '.join(fields),str(child.pid)+' (cpu) Z 1',str(child.pid+1)+' (cpu) '+tail):
                with patch('recovery_resources.Path.read_text',return_value=value),self.assertRaises(ValueError):renderer_terminal_state(row)
            self.assertIsNone(child.poll())
    def test_unknown_procfs_and_pidfd_errors_are_not_absence(self):
        with self.legacy('/usr/bin/cat') as (f,s,d,a,b,l,child,row):
            with patch('recovery_resources.Path.read_text',side_effect=PermissionError('proc denial')),self.assertRaises(PermissionError):renderer_terminal_state(row)
            with patch('recovery_resources.os.pidfd_open',side_effect=PermissionError('pidfd denial')),self.assertRaises(PermissionError):renderer_terminal_state(row)
    def test_boolean_and_nonpositive_pid_start_never_prove_terminal(self):
        with self.legacy() as (f,s,d,a,b,l,child,row):
            for field in ('pid','start'):
                for value in (True,False,0,-1,'1'):
                    bad=dict(row,**{field:value})
                    with self.assertRaises(ValueError):renderer_terminal_state(bad)
    def test_unexpected_pidfd_error_event_refuses(self):
        with self.legacy('/usr/bin/cat') as (f,s,d,a,b,l,child,row):
            class BadPoll:
                def register(self,fd,event):self.fd=fd
                def poll(self,timeout):return [(self.fd,select.POLLERR)]
            with patch('recovery_resources.select.poll',return_value=BadPoll()),self.assertRaisesRegex(ValueError,'unexpected renderer pidfd'):renderer_terminal_state(row)

if __name__=='__main__':unittest.main()
