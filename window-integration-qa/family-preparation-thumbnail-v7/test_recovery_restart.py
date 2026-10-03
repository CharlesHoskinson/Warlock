"""Actual headless process/lease API restarts; no compositor/client execution."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
import helper_setup as setup
import helper_observer as observer
from native_integration import SERVICE
from service_recovery_observer import make_recovery_runtime
sys.path.insert(0,str(SERVICE))
import test_recovery_runtime as inherited
from recovery_runtime import NativeRecovery
from service_runtime import JournalStore
from recovery_evidence import validate_baseline,runtime_peer_witness

MEMBERS=[dict(address='0x'+str(i),stableId=str(i),pid=100+i) for i in range(1,4)]

class RestartTests(unittest.TestCase):
    def test_original_actual_baseline_template_requires_all15_and_normal_fixtures(self):
        reference=json.loads(Path('/home/hoskinson/window-integration-qa/family-continuous-reversal-v3/attempt-1/report.json').read_text());expected=reference['sourceManifestSHA256']
        self.assertTrue(validate_baseline(reference,expected))
        for field in ('mainPreservation','clientCleanup'):
            bad=deepcopy(reference);bad[field]={}
            with self.assertRaises(ValueError):validate_baseline(bad,expected)
    def test_partial_source_or_forced_baseline_never_admits_fault_campaign(self):
        reference=json.loads(Path('/home/hoskinson/window-integration-qa/family-continuous-reversal-v3/attempt-1/report.json').read_text());expected=reference['sourceManifestSHA256']
        bad=deepcopy(reference);bad['checks'].pop()
        with self.assertRaises(ValueError):validate_baseline(bad,expected)
        bad=deepcopy(reference);bad['clientCleanup']['family-service']['forcedTermination']=True
        with self.assertRaises(ValueError):validate_baseline(bad,expected)
        with self.assertRaises(ValueError):validate_baseline(reference,'0'*64)
    @contextmanager
    def roots(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);script=root/'source.py';script.write_text('import sys\nsys.stdin.readline()\n');script.chmod(0o600)
            for name in ('initial','restart'):(root/name).mkdir(mode=0o700)
            old_command=[sys.executable,str(script),'--root',str(root/'runtime'),'--session','cpu-test','--evidence',str(root/'initial/evidence.json')]
            first=subprocess.Popen(old_command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            new_command=list(old_command);new_command[-1]=str(root/'restart/evidence.json')
            second=subprocess.Popen(new_command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            env={'WINDOW_QA_HELPER_CONFIG':str(root/'config.json')};config={'queryRoots':{}}
            setup.register_service_root(env,config,observer.process(first.pid),old_command,MEMBERS,SERVICE)
            config['serviceTargetLimitPerMember']=2;config['serviceRefreshLimit']=9;setup.write_json(Path(env['WINDOW_QA_HELPER_CONFIG']),config)
            try:yield root,script,first,second,env,config,new_command
            finally:
                for process in (first,second):
                    if process.poll() is None:process.stdin.write(b'\n');process.stdin.flush()
                    process.wait(timeout=3);process.stdin.close()
    def old_gone(self,first):first.stdin.write(b'\n');first.stdin.flush();first.wait(timeout=3)
    def test_live_exact_old_root_cannot_be_replaced(self):
        with self.roots() as (root,script,first,second,env,config,command):
            before=Path(env['WINDOW_QA_HELPER_CONFIG']).read_bytes()
            with self.assertRaisesRegex(RuntimeError,'remains live'):setup.register_service_restart(env,config,observer.process(second.pid),command,MEMBERS)
            self.assertEqual(Path(env['WINDOW_QA_HELPER_CONFIG']).read_bytes(),before)
    def test_actual_new_gated_root_retains_sources_members_and_accumulated_limits(self):
        with self.roots() as (root,script,first,second,env,config,command):
            old=deepcopy(config['queryRoots']['service']);self.old_gone(first)
            setup.register_service_restart(env,config,observer.process(second.pid),command,MEMBERS)
            actual=json.loads(Path(env['WINDOW_QA_HELPER_CONFIG']).read_text());self.assertEqual(actual['queryRoots']['service']['identity']['pid'],second.pid);self.assertEqual(actual['serviceRootHistory'],[old]);self.assertEqual(actual['queryRoots']['service']['sources'],old['sources']);self.assertEqual(actual['serviceMembers'],MEMBERS);self.assertEqual((actual['serviceTargetLimitPerMember'],actual['serviceRefreshLimit']),(2,9))
    def test_new_root_cannot_change_original_runtime_or_session(self):
        with self.roots() as (root,script,first,second,env,config,command):
            self.old_gone(first)
            for flag in ('--root','--session'):
                bad=list(command);bad[bad.index(flag)+1]+='-changed'
                with self.assertRaisesRegex(RuntimeError,'source/root/session'):setup.register_service_restart(env,config,observer.process(second.pid),bad,MEMBERS)
            self.assertNotIn('serviceRootHistory',config)
    def test_members_and_changed_frozen_source_refuse_before_config_write(self):
        with self.roots() as (root,script,first,second,env,config,command):
            self.old_gone(first);before=Path(env['WINDOW_QA_HELPER_CONFIG']).read_bytes();bad=deepcopy(MEMBERS);bad[0]['pid']+=1
            with self.assertRaisesRegex(RuntimeError,'member guards'):setup.register_service_restart(env,config,observer.process(second.pid),command,bad)
            script.write_text('import sys\nsys.stdin.readline()\n# changed material\n')
            with self.assertRaisesRegex(RuntimeError,'frozen source changed'):setup.register_service_restart(env,config,observer.process(second.pid),command,MEMBERS)
            self.assertEqual(Path(env['WINDOW_QA_HELPER_CONFIG']).read_bytes(),before)
    def test_unknown_new_lifetime_and_used_evidence_destination_refuse(self):
        with self.roots() as (root,script,first,second,env,config,command):
            self.old_gone(first);wrong=dict(observer.process(second.pid),start='1')
            with self.assertRaisesRegex(RuntimeError,'fresh gated'):setup.register_service_restart(env,config,wrong,command,MEMBERS)
            Path(command[-1]).write_text('old evidence')
            with self.assertRaisesRegex(RuntimeError,'fresh sibling'):setup.register_service_restart(env,config,observer.process(second.pid),command,MEMBERS)
    def test_actual_kernel_peer_cannot_confirm_wrong_start_or_released_lease(self):
        from types import SimpleNamespace
        import threading
        from service_runtime import RuntimeLease
        from socket_frontend import SocketFrontend
        with tempfile.TemporaryDirectory() as raw:
            lease=RuntimeLease(raw,'offline');manager=SimpleNamespace(lock=threading.RLock(),pending={},ingress_history=[],state=lambda:[])
            frontend=SocketFrontend(lease.socket,manager,lambda value:{});lease.bound(frontend.socket_identity);frontend.start()
            try:
                identity=observer.process(os.getpid());wrong=dict(identity,start=str(int(identity['start'])+1))
                with self.assertRaisesRegex(ValueError,'typed fresh owner'):runtime_peer_witness(raw,'offline',wrong,{'nonce':'0'*32},list(lease.root_identity),list(lease.lock_identity),Path(raw)/'wrong-start.json')
                root_identity=list(lease.root_identity);lock_identity=list(lease.lock_identity);lease.close()
                with self.assertRaisesRegex(ValueError,'exclusive runtime lease'):runtime_peer_witness(raw,'offline',identity,{'nonce':'0'*32},root_identity,lock_identity,Path(raw)/'released-lock.json')
                for name in ('wrong-start.json','released-lock.json'):
                    evidence=json.loads((Path(raw)/name).read_text());self.assertIn('error',evidence);self.assertNotIn('confirmed',evidence)
            finally:frontend.close(close_manager=False);lease.close()
    def test_documented_runtime_recovery_binding_completes_before_actual_private_api(self):
        with tempfile.TemporaryDirectory() as raw:
            f,s,d,a,b=inherited.RecoveryTests().fixture(raw);d.windows.pop(0);d.family=lambda w,windows,single=False:(deepcopy(windows),deepcopy(windows[-1]))
            class Factory:
                def __init__(self):self.__dict__.update(f.__dict__);self.recovery_calls=0
                def bind_lease(self,verify):self.lease_verify=verify
                def recover(self,previous):
                    self.recovery_calls+=1;return NativeRecovery(self,store=s,desktop=d,lease_verify=self.lease_verify).recover(previous)
                def __call__(self,*args):raise AssertionError('No new actor requested during recovered API setup')
            factory=Factory();runtime=make_recovery_runtime(raw,'offline',factory,lambda value:{})
            try:
                self.assertEqual(factory.recovery_calls,1);self.assertFalse(a.exists());self.assertFalse(d.commits);self.assertTrue((Path(raw)/'api.sock').is_socket())
                live=JournalStore(raw,'offline').read();self.assertEqual(live['recoveryHistory'][-1]['state'],'completed');self.assertEqual(live['recoveryHistory'][-1]['plans'][0]['operation'],'cancel');self.assertNotIn('recovery',live)
                runtime.frontend.start()
                witness=runtime_peer_witness(raw,'offline',observer.process(os.getpid()),{'nonce':'0'*32},list(runtime.lease.root_identity),list(runtime.lease.lock_identity),Path(raw)/'peer-proof.json')
                self.assertTrue(witness['confirmed']);self.assertEqual(witness['peer']['pid'],os.getpid());self.assertEqual(witness['ownerBefore'],witness['ownerAfter']);self.assertTrue(witness['exclusiveLeaseBlocked'])
            finally:runtime.close()

if __name__=='__main__':unittest.main()
