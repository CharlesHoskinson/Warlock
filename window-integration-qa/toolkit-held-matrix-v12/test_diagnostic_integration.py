"""Exact integration refusal and raw archival tests; no desktop process launch."""
import copy,hashlib,json,os
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
import helper_observer as observer
import helper_setup as setup
B=Path(__file__).resolve().parent
class Integration(unittest.TestCase):
 def fixture(self):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);home=Path(temp.name);home.chmod(0o700);(home/'.local/bin').mkdir(parents=True,mode=0o700);(home/'.local').chmod(0o700)
  source=home/'.local/bin/delegate_diagnostics.py';source.write_bytes((B/'delegate_diagnostics.py').read_bytes());source.chmod(0o700);directory=home/'delegate-diagnostics';directory.mkdir(mode=0o700)
  actual=home/'.local/bin/hypr-snap-groups.actual';actual.write_text('#!/usr/bin/env python3\n');actual.chmod(0o700)
  parent=observer.process(os.getpid());qs=dict(parent,pid=parent['parent']);config=dict(log=str(home/'helper-events.jsonl'),actual=str(actual),delegateDiagnostic=dict(source=str(source),sourceSHA256=observer.digest(source),directory=str(directory)),queryRoots=dict(qs=dict(identity=qs)))
  wrapper=dict(parent,parent=parent['pid']);return home,config,wrapper,[parent,qs]
 def test_source_loader_uses_exact_complete_bytes_and_registered_lineage(self):
  home,cfg,wrapper,anc=self.fixture();module,journal,parent,qs,chain=observer.load_delegate_diagnostic(cfg,wrapper,anc)
  try:self.assertEqual(parent,anc[0]);self.assertEqual(qs,anc[1]);self.assertEqual(len(chain),2);self.assertTrue(callable(module.child_bootstrap));self.assertEqual(journal.path.parent,home/'delegate-diagnostics')
  finally:journal.close()
 def test_changed_source_mode_hash_path_or_lineage_refuse(self):
  for fault in ('mode','hash','path','lineage','shebang'):
   with self.subTest(fault=fault):
    home,cfg,wrapper,anc=self.fixture();source=Path(cfg['delegateDiagnostic']['source'])
    if fault=='mode':source.chmod(0o755)
    if fault=='hash':cfg['delegateDiagnostic']['sourceSHA256']='0'*64
    if fault=='path':cfg['delegateDiagnostic']['source']=str(home/'elsewhere')
    if fault=='lineage':cfg['queryRoots']['qs']['identity']=dict(anc[1],start='0')
    if fault=='shebang':Path(cfg['actual']).write_text('#!/usr/bin/python3\n')
    with self.assertRaises(RuntimeError):observer.load_delegate_diagnostic(cfg,wrapper,anc)
    self.assertEqual(list((home/'delegate-diagnostics').iterdir()),[])
 def test_source_replacement_between_witness_reads_refuses(self):
  home,cfg,wrapper,anc=self.fixture();source=Path(cfg['delegateDiagnostic']['source']);real=observer.material_witness;count=0
  def witness(*args):
   nonlocal count
   value=real(*args);count+=1
   if count==1:source.write_bytes(source.read_bytes()+b'\n')
   return value
  with patch.object(observer,'material_witness',side_effect=witness),self.assertRaises(RuntimeError):observer.load_delegate_diagnostic(cfg,wrapper,anc)
 def test_truncated_raw_diagnostic_is_archived_without_acceptance(self):
  home,cfg,wrapper,anc=self.fixture();path=home/'delegate-diagnostics/23-99.jsonl';raw=b'{"index":0,"event":"stdio-write-entry"';path.write_bytes(raw);path.chmod(0o600)
  result=setup.archive_diagnostics(cfg,[],home/'archive');self.assertEqual((home/'archive'/path.name).read_bytes(),raw);self.assertIn('error',result[0]);self.assertFalse(result[0]['expected']);self.assertTrue(result[0]['completeEOF'])
  with self.assertRaises(RuntimeError):setup.diagnostic_records(path)
 def test_missing_expected_log_and_extra_invocation_stay_failures(self):
  home,cfg,wrapper,anc=self.fixture();start=dict(event='started',operation='test',queryRoot='qs',helper='snap',wrapper=wrapper,delegate=wrapper,diagnosticLog=str(home/'delegate-diagnostics'/f"{wrapper['pid']}-{wrapper['start']}.jsonl"))
  result=setup.archive_diagnostics(cfg,[start],home/'archive');self.assertIn('error',result[0]);self.assertTrue(result[0]['expected'])
  with self.assertRaises(RuntimeError):setup.diagnostic_completeness(cfg,[start])
 def test_diagnostic_additions_never_skip_original_nonzero_helper_gate(self):
  cfg=dict(allowed=['exact'],log='unused');events=[dict(event='started',operation='exact',wrapper={'pid':1},delegate={'pid':2}),dict(event='terminal',operation='exact',wrapper={'pid':1},delegate={'pid':2},exitCode=120)]
  import io
  class Log(io.StringIO):
   def __enter__(self):return self
   def __exit__(self,*args):return False
  with patch.object(observer,'locked_log',return_value=Log()),patch.object(observer,'rows',return_value=events),patch.object(observer,'still_live',return_value=False),patch.object(setup,'diagnostic_completeness') as diagnostics:
   with self.assertRaisesRegex(RuntimeError,'normal completion mismatch'):setup.wait_and_archive(cfg,None)
   diagnostics.assert_not_called()
 def replay_fixture(self):
  home,cfg,wrapper,anc=self.fixture();proof=B/'observer-kernel-proof/shebang-chain'
  rows=[json.loads(line) for line in (proof/'trace.jsonl').read_text().splitlines()];summary=json.loads((proof/'summary.json').read_text())['summary'];bound=rows[0]
  path=home/'delegate-diagnostics'/f"{wrapper['pid']}-{wrapper['start']}.jsonl";actual=next(row['argv'][2] for row in rows if row['event']=='backend-exec')
  # Reference fixture changes only the helper envelope, leaving actual kernel writes intact.
  bound['metadata'].update(operation='reference-query',actualSHA256='a'*64,observerSHA256=cfg['delegateDiagnostic']['sourceSHA256'])
  start=dict(event='started',operation='reference-query',wrapper=wrapper,delegate=bound['delegate'],ancestry=[bound['parent'],bound['qs']],actual=actual,actualSHA256='a'*64,diagnosticLog=str(path),queryRoot='qs',helper='snap')
  summary['path']=str(path);terminal=dict(event='terminal',operation=start['operation'],wrapper=wrapper,delegate=start['delegate'],exitCode=0,diagnostic=summary)
  def save():path.write_text(''.join(json.dumps(row)+'\n' for row in rows));path.chmod(0o600)
  save();return cfg,start,terminal,rows,save
 def test_actual_kernel_write_replay_and_extra_missing_log_refusals(self):
  cfg,start,terminal,rows,save=self.replay_fixture();proof=setup.verify_diagnostic(cfg,start,terminal);self.assertTrue(proof['completeEOF']);self.assertEqual(proof['stdioSyscalls'],1)
  with patch.object(observer,'still_live',return_value=False):self.assertTrue(setup.diagnostic_completeness(cfg,[start,terminal])['complete'])
  extra=Path(cfg['delegateDiagnostic']['directory'])/'99-99.jsonl';extra.write_text('');extra.chmod(0o600)
  with patch.object(observer,'still_live',return_value=False),self.assertRaises(RuntimeError):setup.diagnostic_completeness(cfg,[start,terminal])
 def test_exact_kernel_replay_rejects_lifetime_exec_payload_wait_and_completeness_faults(self):
  for fault in ('lifetime','exec','payload','return','errno','wait','summary','missing-return','source'):
   with self.subTest(fault=fault):
    cfg,start,terminal,rows,save=self.replay_fixture()
    if fault=='lifetime':rows[-1]['identity']=dict(start['delegate'],start='0')
    if fault=='exec':next(row for row in rows if row['event']=='backend-exec')['argv']=['wrong']
    if fault=='payload':next(row for row in rows if row['event']=='stdio-write-entry')['offeredBytesHex']='00'
    if fault=='return':next(row for row in rows if row['event']=='stdio-write-return')['kernelReturn']=999999
    if fault=='errno':next(row for row in rows if row['event']=='stdio-write-return')['errno']=32
    if fault=='wait':rows[-1]['rawWaitStatus']=120*256
    if fault=='summary':terminal['diagnostic']['complete']=False
    if fault=='missing-return':rows.pop(next(i for i,row in enumerate(rows) if row['event']=='stdio-write-return'))
    if fault=='source':rows[0]['metadata']['observerSHA256']='0'*64
    save()
    with self.assertRaises(RuntimeError):setup.verify_diagnostic(cfg,start,terminal)
 def test_complete_originals_reconstructed_and_changed_budget_refused(self):
  import source_conservation
  for name in ('helper_observer.py','helper_setup.py','qs_lifecycle.py'):
   self.assertEqual(source_conservation.reconstructed(name),(B.parent/'toolkit-held-matrix-v10'/name).read_bytes())
  name='helper_observer.py';changed=(B/name).read_bytes().replace(b'count>=limit',b'count>=limit+1')
  with self.assertRaises(RuntimeError):source_conservation.reconstructed(name,changed)
  for name in ('run_native.py','held_controller.py','evaluation_setup.py','observations.py','scroll_route.py','frontend_route.py','input_control.py','private_shell.py','service_observer.py'):
   self.assertEqual((B/name).read_bytes(),(B.parent/'toolkit-held-matrix-v10'/name).read_bytes(),name)
 def test_source_runtime_only_qs_snap_own_child_and_original_fd_routes(self):
  source=(B/'helper_observer.py').read_text();self.assertIn("if query_kind=='qs' and kind=='snap':",source);self.assertIn("if digest(config['delegateDiagnostic']['source'])!=config['delegateDiagnostic']['sourceSHA256']:os._exit(126)",source)
  module=(B/'delegate_diagnostics.py').read_text()
  for forbidden in ('PTRACE_ATTACH','PTRACE_SEIZE','PTRACE_POKE','PTRACE_SETREGS','os.dup2','setenv('):self.assertNotIn(forbidden,module)
  self.assertIn("os.execv(config['actual'], [config['actual'], *args])",source)
if __name__=='__main__':unittest.main(verbosity=2)
