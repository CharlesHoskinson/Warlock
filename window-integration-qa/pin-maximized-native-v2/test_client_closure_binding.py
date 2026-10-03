import ast,copy,hashlib,importlib.util,json,os,stat,subprocess,sys,time,unittest
from pathlib import Path
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'proposed'))
import client_closure_binding as cb
import host_observation as ob
OLD=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v1')

class ClientBinding(unittest.TestCase):
 def setUp(self):
  self.actual=json.loads((B/'retained-v1/attempt-1/host/host-normal-closure.json').read_bytes())
  self.report=json.loads((B/'retained-v1/attempt-1/native/cases.json').read_bytes())
  self.registered=[{k:v for k,v in r.items()if k not in {'registeredExact','reaped','returncode','signals','stopError'}}for r in self.actual['rows']]
  self.sources={str(p):dict(sha256=cb.digest(p),mode=stat.S_IMODE(p.stat().st_mode))for p in [B/'native_cases.py',cb.FIXTURE,cb.POINTER,cb.KEYBOARD]}
  self.output=OLD/'attempt-1/native'
 def bound(self):
  bindings=cb.derive(self.registered,self.report,self.sources,self.output)
  row=copy.deepcopy(self.actual)
  # Historical CPU classification fixture, not a new native acceptance witness.
  pre=[dict(name=b['name'],pid=b['pid'],start=b['start'],pgid=b['pgid'],command=b['command'],registeredExact=True,returncode=0,gone=True)for b in bindings]
  row['clientClosureBinding']=dict(ok=True,error=None,beforeDelegatedClose=True,rawPersisted=True,bindings=bindings,rows=pre)
  return row
 def test_retained_actual_roles_exact_and_original_refuses(self):
  spec=importlib.util.spec_from_file_location('old_ob',B/'retained-v1/host_observation.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
  self.assertFalse(old.normal_closure(self.actual));self.assertTrue(ob.normal_closure(self.bound()))
 def test_whole_stop_base_normal_and_runner_original_cases_exact(self):
  old=ast.parse((B/'retained-v1/host_observation.py').read_text());new=ast.parse((B/'proposed/host_observation.py').read_text())
  def function(tree,name):
   return next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name==name)
  for name in ['normal_row','_inherited_stop','stop','_observed_signal']:
   self.assertEqual(ast.dump(function(old,name),include_attributes=False),ast.dump(function(new,name),include_attributes=False),name)
  for name in ['run_native.py','candidate_host.py']:
   self.assertEqual((B/'proposed'/name).read_bytes(),(OLD/'proposed'/name).read_bytes())
  for name in ['native_cases.py','case_authority.py','input_episode.py']:
   self.assertEqual((B/name).read_bytes(),(OLD/name).read_bytes())
 def test_source_report_replacement_refusals(self):
  for kind in ['pid','start','argv','source','modeType','forced','receipt','normal','extraInput','extraRole','duplicate','route']:
   rows=copy.deepcopy(self.registered);report=copy.deepcopy(self.report);sources=copy.deepcopy(self.sources)
   if kind=='pid':report['fixture']['pid']=float(report['fixture']['pid'])
   elif kind=='start':report['fixture']['start']='999999'
   elif kind=='argv':rows[5]['command'][-1]='super-ctrl-t'
   elif kind=='source':report['fixture']['sha256']='0'*64
   elif kind=='modeType':sources[str(cb.FIXTURE)]['mode']=float(sources[str(cb.FIXTURE)]['mode'])
   elif kind=='forced':report['cleanup']['pointer']['forced']=True
   elif kind=='receipt':report['cleanup']['fixture']['exitCode']=False
   elif kind=='normal':report['normalCleanup']=False
   elif kind=='extraInput':report['inputs'].append(report['inputs'][-1])
   elif kind=='extraRole':rows[-1]['name']='arbitrary'
   elif kind=='duplicate':rows[-1]['pid']=rows[-2]['pid'];rows[-1]['pgid']=rows[-2]['pgid']
   elif kind=='route':report['inputs'][2]['route']='super-ctrl-t'
   with self.subTest(kind=kind):
    with self.assertRaises((ValueError,KeyError,TypeError)):cb.derive(rows,report,sources,self.output)
 def test_before_after_terminal_refusals(self):
  for kind in ['running','pidPresent','pidAlias','newStart','newCommand','forcedTerm','nonzero','falseRc','notReaped','stopError','unknownRole','order','duplicate','reportMissing','captureError','missingRaw','lateCaptured','baseKill']:
   row=self.bound();proof=row['clientClosureBinding'];final=row['rows'][3];pre=proof['rows'][0]
   if kind=='running':pre['returncode']=None
   elif kind=='pidPresent':pre['gone']=False
   elif kind=='pidAlias':pre['pid']=float(pre['pid'])
   elif kind=='newStart':final['start']='999'
   elif kind=='newCommand':final['command']=['/usr/bin/true']
   elif kind=='forcedTerm':final['signals']=[dict(pid=final['pid'],signal=15,sent=True,error=None)]
   elif kind=='nonzero':final['returncode']=1
   elif kind=='falseRc':final['returncode']=False
   elif kind=='notReaped':final['reaped']=False
   elif kind=='stopError':final['stopError']='error'
   elif kind=='unknownRole':final['name']='arbitrary'
   elif kind=='order':row['registeredStopOrder'].reverse()
   elif kind=='duplicate':row['rows'][-1]['pid']=final['pid'];row['rows'][-1]['pgid']=final['pgid']
   elif kind=='reportMissing':row.pop('clientClosureBinding')
   elif kind=='captureError':proof['error']='unknown'
   elif kind=='missingRaw':proof['rawPersisted']=False
   elif kind=='lateCaptured':proof['beforeDelegatedClose']=False
   elif kind=='baseKill':row['rows'][2]['signals'].append(dict(pid=row['rows'][2]['pid'],signal=9,sent=True,error=None))
   with self.subTest(kind=kind):self.assertFalse(ob.normal_closure(row))
 def test_actual_cpu_process_before_vs_after_reap_not_native_acceptance(self):
  proc=subprocess.Popen([sys.executable,'-c','import sys;sys.stdin.read()'],stdin=subprocess.PIPE,start_new_session=True)
  try:
   before=dict(returncode=proc.poll(),gone=not Path('/proc/'+str(proc.pid)).exists())
   row=self.bound();row['clientClosureBinding']['rows'][0].update(before)
   self.assertIsNone(before['returncode']);self.assertFalse(before['gone']);self.assertFalse(ob.normal_closure(row))
   proc.stdin.close();proc.wait(timeout=4)
   after=dict(returncode=proc.poll(),gone=not Path('/proc/'+str(proc.pid)).exists())
   self.assertEqual(after,dict(returncode=0,gone=True))
  finally:
   if proc.poll()is None:proc.kill();proc.wait(timeout=4)
 def test_original_no_client_three_role_classifier_conserved(self):
  row=copy.deepcopy(self.actual);row['rows']=row['rows'][:3];row['registeredStopOrder']=list(reversed(cb.BASE))
  self.assertTrue(ob.normal_closure(row))
 def test_malformed_and_duplicate_raw_objects_refuse(self):
  with self.assertRaises(ValueError):json.loads('{"normalCleanup":true,"normalCleanup":false}',object_pairs_hook=cb.unique_object)
  for field in ['rows','bindings']:
   row=self.bound();row['clientClosureBinding'][field][0]=None
   self.assertFalse(ob.normal_closure(row))
  row=self.bound();row['rows'][3]=None;self.assertFalse(ob.normal_closure(row))
  report=copy.deepcopy(self.report);report['cleanupErrors']=0
  with self.assertRaises(ValueError):cb.derive(self.registered,report,self.sources,self.output)

if __name__=='__main__':unittest.main(verbosity=2)
