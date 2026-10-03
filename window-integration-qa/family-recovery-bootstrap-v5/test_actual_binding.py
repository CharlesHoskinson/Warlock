"""Actual loaded source, regular FD, RuntimeLease and Unix-peer CPU evidence."""
from copy import deepcopy
from contextlib import contextmanager
import importlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import module_binding as binding
import service_observer
import native_runtime,scene_manager,scene_controller,pipe_transport,owned_commands,service_runtime
import test_readonly_ipc as cpu
B=Path(__file__).parent

class LoadedSourceTests(unittest.TestCase):
 def test_actual_candidate_and_links(self):
  raw=binding._observe('actual-cpu');self.assertEqual(raw['errors'],[]);self.assertFalse(raw['usable']);self.assertTrue(raw['rawEvidenceOnly']);self.assertEqual(len(raw['modules']),18);self.assertTrue(all(v['matched'] for v in raw['links']))
 def test_stale_preloaded_v17_is_not_repaired_by_outer_path(self):
  old=binding.SERVICE.parent/'service-recovery-terminal-v17'
  code="import sys;sys.path.insert(0,sys.argv[1]);import native_runtime;sys.path.insert(0,sys.argv[2]);import module_binding;sys.path.insert(0,str(module_binding.SERVICE));r=module_binding._observe('stale');assert r['errors'] and not r['usable'];print(native_runtime.__file__)"
  result=subprocess.run([sys.executable,'-B','-c',code,str(old),str(B)],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),text=True,capture_output=True,timeout=5,check=True)
  self.assertIn(str(old/'native_runtime.py'),result.stdout)
 def test_actual_link_replacement_persists_raw_refusal(self):
  with tempfile.TemporaryDirectory() as raw,patch.object(native_runtime,'NativeDesktop',object):
   path=Path(raw)/'capture.json'
   with self.assertRaises(ValueError):binding.capture(path,'wrong-link')
   data=json.loads(path.read_text());self.assertTrue(data['errors']);self.assertFalse(data['usable']);self.assertFalse(data['links'][0]['matched'])
 def test_valid_module_token_replacement_refuses(self):
  old=binding._observe('first');old['moduleToken']='0'*64
  self.assertTrue(binding._observe('fresh',previous=old)['errors'])
 def test_post_disk_link_replacement_refuses(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'capture.json';real=binding.persist_raw;original=native_runtime.NativeDesktop
   def publish(p,r):
    disk=real(p,r)
    if p==path:native_runtime.NativeDesktop=object
    return disk
   try:
    with patch.object(binding,'persist_raw',side_effect=publish),self.assertRaises(ValueError):binding.capture(path,'after-disk')
    self.assertTrue(json.loads(path.with_name('capture-confirmation.json').read_text())['errors'])
   finally:native_runtime.NativeDesktop=original
 def test_actual_source_fd_swap_is_refused(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'source.py';path.write_text('value=1\n');path.chmod(0o600);real=os.read;done=False
   def swap(fd,size):
    nonlocal done
    value=real(fd,size)
    if value and not done:
     done=True;new=path.with_suffix('.replacement');new.write_text('value=1\n');new.chmod(0o600);new.replace(path)
    return value
   with patch.object(binding.os,'read',side_effect=swap):row=binding.read_source(path)
   self.assertTrue(row['error']);self.assertNotEqual(row['before']['inode'],row['namedAfter']['inode'])
 def test_alias_and_unsafe_mode_refuse(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'source.py';path.write_text('x=1\n');path.chmod(0o666);self.assertTrue(binding.read_source(path)['error']);alias=path.with_suffix('.alias');alias.symlink_to(path)
   with self.assertRaises(ValueError):binding.read_source(alias)

class OwnerKernelTests(unittest.TestCase):
 setUp=cpu.ReadonlyKernelTests.setUp
 tearDown=cpu.ReadonlyKernelTests.tearDown
 query=cpu.ReadonlyKernelTests.query
 @contextmanager
 def package(self):
  with tempfile.TemporaryDirectory() as folder:
   package=Path(folder);destination=package/'evidence';destination.mkdir(mode=0o700)
   packet={'inputs':{},'inputModes':{}}
   for p in B.rglob('*.py'):
    if '__pycache__' not in p.parts:packet['inputs'][str(p)]=binding.sha(p.read_bytes());packet['inputModes'][str(p)]=p.stat().st_mode&0o7777
   descriptor=package/'frozen-inputs.json';descriptor.write_text(json.dumps(packet));descriptor.chmod(0o600)
   factory=object.__new__(service_observer.ObservedFactory);factory.root=self.root;factory.guard=self.guard;factory.lease_verify=self.lease.verify;factory.readonly=self.reader;factory.keeper=None;factory.observed_bindings=[]
   initial=binding._observe('initial');factory.binding_bootstrap=initial
   with patch.object(binding,'__file__',str(package/'module_binding.py')):
    yield factory,initial,destination,binding.sha(descriptor.read_bytes())
 def bound(self,factory,initial,destination,digest):
  proof=binding.bind_owner(factory,self.lease.verify,destination/'actual-owner-binding.json',initial,digest);factory.binding_owner=proof;return proof
 def test_actual_held_lease_first_complete_binding(self):
  with self.package() as (factory,initial,destination,digest):
   proof=self.bound(factory,initial,destination,digest);self.assertTrue(proof['usable']);self.assertEqual(proof['owner']['pid'],os.getpid());self.assertEqual(proof['owner']['rootIdentity'],list(self.lease.root_identity));self.assertFalse(initial['usable']);self.assertTrue(json.loads(Path(proof['confirmation']['path']).read_text())['owner']==proof['owner'])
 def test_wrong_collector_digest_persists_no_usable_binding(self):
  with self.package() as (factory,initial,destination,digest):
   with self.assertRaises(ValueError):self.bound(factory,initial,destination,'0'*64)
   row=json.loads((destination/'actual-owner-binding.json').read_text());self.assertTrue(row['errors']);self.assertFalse(row['usable'])
 def test_owner_changed_after_disk_has_raw_confirmation_before_refusal(self):
  with self.package() as (factory,initial,destination,digest):
   real=binding.persist_raw
   def change(path,row):
    result=real(path,row)
    if path==destination/'actual-owner-binding.json':self.lease.owner['nonce']='f'*32;self.lease.publish_owner()
    return result
   with patch.object(binding,'persist_raw',side_effect=change),self.assertRaises(ValueError):self.bound(factory,initial,destination,digest)
   confirm=json.loads((destination/'actual-owner-binding-confirmation.json').read_text());self.assertTrue(confirm['errors']);self.assertFalse(confirm['usable'])
 def test_callback_replacement_after_disk_refuses(self):
  with self.package() as (factory,initial,destination,digest):
   real=binding.persist_raw
   def change(path,row):
    result=real(path,row)
    if path==destination/'actual-owner-binding.json':factory.context=lambda request:None
    return result
   with patch.object(binding,'persist_raw',side_effect=change),self.assertRaises(ValueError):self.bound(factory,initial,destination,digest)
   self.assertTrue(json.loads((destination/'actual-owner-binding-confirmation.json').read_text())['errors'])
 def test_actual_reader_peer_and_journal_equal_binding(self):
  with self.package() as (factory,initial,destination,digest):
   proof=self.bound(factory,initial,destination,digest);self.assertEqual(self.query(),b'[]');ledger=self.reader.snapshot();journal=self.store.read();self.assertTrue(binding.validate_ledger(ledger,proof['owner'],journal));self.assertEqual(ledger['history'][0]['evidence']['peer']['pid'],os.getpid())
 def test_pending_refused_missing_and_replaced_owner_never_admit(self):
  with self.package() as (factory,initial,destination,digest):
   proof=self.bound(factory,initial,destination,digest);self.query();ledger=self.reader.snapshot();journal=self.store.read()
   changes=[lambda l:l['history'].clear(),lambda l:l['history'][0].update(outcome='pending',closed=False),lambda l:l['history'][0].update(outcome='refused'),lambda l:l['issuer'].update(nonce='f'*32),lambda l:l.update(fault=True),lambda l:l['history'].append(deepcopy(l['history'][0])),lambda l:l['history'][0].update(requestSHA256='0'*64)]
   for change in changes:
    bad=deepcopy(ledger);change(bad);j=deepcopy(journal);j['readonlyOwnership']=bad
    with self.assertRaises(ValueError):binding.validate_ledger(bad,proof['owner'],j)
   bad=deepcopy(journal);bad['readonlyOwnership']['history'].clear()
   with self.assertRaises(ValueError):binding.validate_ledger(ledger,proof['owner'],bad)
 def actor(self,factory):
  desktop=object.__new__(native_runtime.PinnedNativeDesktop);desktop.commands=owned_commands.OwnedCommands(None,self.env,1,readonly=self.reader);desktop.production=importlib.import_module('production_motion_6d9');desktop.base=object.__new__(desktop.production.Desktop)
  controller=object.__new__(scene_manager.ManagedController);transport=object.__new__(pipe_transport.PipeTransport);controller.desktop=desktop;controller.transport=transport;transport.callback=controller.event
  import types
  transport.failure=native_runtime.FailureBinding();code=next(v for v in native_runtime.NativeFactory.__call__.__code__.co_consts if isinstance(v,types.CodeType) and v.co_name=='<lambda>');cell=(lambda value:lambda:value)(transport.failure).__closure__[0];transport.qa_original_bind_controller=types.FunctionType(code,native_runtime.__dict__,closure=(cell,))
  factory.resource_writer=object.__new__(service_runtime.RuntimeService).persist
  return desktop,transport,controller
 def test_exact_actual_actor_class_and_callback_chain(self):
  with self.package() as (factory,initial,destination,digest):
   self.bound(factory,initial,destination,digest);desktop,transport,controller=self.actor(factory)
   # Production owns an actual per-actor module with its command facade.
   source=Path(binding.SERVICE/'production_motion_6d9.py');spec=importlib.util.spec_from_file_location('_cpu_actual_actor',source);desktop.production=importlib.util.module_from_spec(spec);spec.loader.exec_module(desktop.production);desktop.production.subprocess=desktop.commands;desktop.base=object.__new__(desktop.production.Desktop)
   proof=binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json');self.assertTrue(proof['usable']);self.assertTrue(all(proof['relations'].values()))
 def test_stale_callback_no_actor_preparation_authority(self):
  with self.package() as (factory,initial,destination,digest):
   self.bound(factory,initial,destination,digest);desktop,transport,controller=self.actor(factory);transport.callback=lambda event:None
   with self.assertRaises(ValueError):binding.linked_actor(factory,1,desktop,transport,controller,destination/'actor.json')
   row=json.loads((destination/'actor.json').read_text());self.assertFalse(row['usable']);self.assertFalse(row['relations']['eventFunction'])
 def test_actual_recovery_coordinator_binding_before_any_effect(self):
  from recovery_runtime import NativeRecovery
  with self.package() as (factory,initial,destination,digest):
   self.bound(factory,initial,destination,digest);coordinator=NativeRecovery(factory,lease_verify=self.lease.verify)
   observed=list(self.control.requests);proof=binding.bind_recovery(factory,coordinator,destination/'recovery.json')
   self.assertTrue(proof['usable']);self.assertIsNone(coordinator.body);self.assertIsNone(coordinator.keeper);self.assertEqual(self.control.requests,observed);self.assertTrue(all(r==b'j/version' for r in observed))
   evidence={'actualRecoveryBinding':proof,'moduleBindingBefore':factory.binding_owner};self.assertTrue(binding.validate_recovery_evidence(evidence)['accepted'])
 def test_wrong_actual_recovery_factory_refuses_before_effect(self):
  from recovery_runtime import NativeRecovery
  with self.package() as (factory,initial,destination,digest):
   self.bound(factory,initial,destination,digest);coordinator=NativeRecovery(factory,lease_verify=self.lease.verify);coordinator.factory=object()
   with self.assertRaises(ValueError):binding.bind_recovery(factory,coordinator,destination/'recovery.json')
   self.assertTrue(json.loads((destination/'recovery.json').read_text())['errors'])
 def test_genuine_owned_data_probe_uses_actual_row_and_no_helper(self):
  with self.package() as (factory,initial,destination,digest):
   self.bound(factory,initial,destination,digest);probe=binding.data_probe(factory,destination/'probe.json')
   self.assertTrue(probe['usable']);self.assertFalse(probe['nativeAuthority']);self.assertIsNone(probe['row']['actor']);self.assertEqual(probe['row']['request'],'j/clients');self.assertEqual(probe['replySHA256'],binding.sha(b'[]'));self.assertEqual(self.store.read()['readonlyOwnership']['history'][-1],probe['row']);self.assertIsNone(factory.keeper)
 def test_probe_wrong_owner_before_bytes_is_persisted_unusable(self):
  with self.package() as (factory,initial,destination,digest):
   self.bound(factory,initial,destination,digest);factory.binding_owner['ownerToken']='0'*64;before=list(self.control.requests)
   with self.assertRaises(ValueError):binding.data_probe(factory,destination/'probe.json')
   row=json.loads((destination/'probe.json').read_text());confirm=json.loads((destination/'probe-confirmation.json').read_text());self.assertFalse(row['usable']);self.assertTrue(row['errors']);self.assertTrue(confirm['errors']);self.assertEqual(self.control.requests,before)
 def test_expected_fault_pending_data_is_retained_without_authority(self):
  with self.package() as (factory,initial,destination,digest):
   self.bound(factory,initial,destination,digest);self.query();pending=next(r for r in self.records if r['history'] and r['history'][-1]['outcome']=='pending')
   journal=self.store.read();journal['readonlyOwnership']=pending;journal['helperOwnership']={'keeper':{'servicePID':os.getpid(),'serviceStart':service_runtime.process_start(os.getpid()),'rootIdentity':list(self.lease.root_identity)}}
   row=binding.archive_fault_binding(destination,journal,deepcopy(self.lease.owner),self.guard,destination/'old-fault.json')
   self.assertFalse(row['usable']);self.assertEqual(row['ledger']['history'][0]['outcome'],'pending');self.assertEqual(row['errors'],[])
   wrong=deepcopy(self.lease.owner);wrong['nonce']='f'*32
   with self.assertRaises(ValueError):binding.archive_fault_binding(destination,journal,wrong,self.guard,destination/'wrong-old-fault.json')
 def test_actual_terminal_closed_lease_and_ledger_then_changed_archive_refuses(self):
  with self.package() as (factory,initial,destination,digest):
   before=self.bound(factory,initial,destination,digest);probe=binding.data_probe(factory,destination/'probe.json');journal=self.store.read();journal['helperOwnership']={'keeper':{'servicePID':os.getpid(),'serviceStart':service_runtime.process_start(os.getpid()),'rootIdentity':list(self.lease.root_identity)}};self.store.write(journal);self.lease.close()
   service=type('CpuTerminal',(),{'lease':self.lease,'store':self.store,'closed':True,'failure':None})()
   modules=binding._observe('terminal',previous=initial);after=binding.archive_final(factory,service,destination/'actual-terminal-binding.json',modules)
   evidence={'moduleBindingBefore':before,'moduleBindingBootstrap':initial,'actualTerminalBinding':after,'actualOwnedDataProbe':probe};self.assertTrue(binding.validate_evidence(evidence)['accepted'])
   candidate=Path(after['confirmation']['path']);candidate.write_text('{}')
   with self.assertRaises(ValueError):binding.validate_evidence(evidence)

if __name__=='__main__':unittest.main()
