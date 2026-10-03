"""Replay complete CPU log and unchanged formal dependencies; no test reruns."""
import hashlib,json,os,re,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-focus-transaction-v28')
OLD=B.with_name('service-restore-planning-v27')
P=QA/'restore-focus-v28-complete-proof-v1'
def material(p):
 p=Path(p);return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def cases(text):return {name+'.'+method:status for method,name,status in re.findall(r'^(test\S+) \(([^)]+)\) \.\.\. (.*)$',text,re.M)}
def write(p,row):
 with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 P.mkdir(mode=0o700)
 prior_path=QA/'restore-planning-v27-full-proof-v1/report.json';prior=json.loads(prior_path.read_text());assert (prior['result'],prior['pythonTests'],prior['quintNamedScenarios'],prior['quintModels'])==('pass',424,435,37)
 v6_path=QA/'restore-focus-transaction-design-v6/formal-before-runtime.json';v6=json.loads(v6_path.read_text());assert v6['result']=='pass' and v6['named']==45
 failed_path=QA/'restore-focus-v28-full-proof-v1/report.json';failed=json.loads(failed_path.read_text());assert failed['result']=='fail' and failed['pythonTests']==444 and failed['sourceUnchangedDuringProof']
 log=QA/'restore-focus-v28-full-proof-v2/check-000.log';text=log.read_text();actual=cases(text);original=cases(Path(prior['checks'][0]['log']).read_text())
 assert len(original)==424 and len(actual)==444 and all(v=='ok' for v in actual.values()) and set(original)<=set(actual)
 assert 'Ran 444 tests' in text and text.rstrip().endswith('OK')
 new=set(actual)-set(original);assert len(new)==20 and all(n.startswith('test_focus_transaction.') for n in new)
 first=cases(Path(failed['checks'][0]['log']).read_text());assert set(first)==set(actual)
 original_failures=sorted(n for n,v in first.items() if v=='FAIL');assert len(original_failures)==2 and all(n.startswith('test_restore_planning.') for n in original_failures)
 fixture=json.loads((Path(__file__).parent/'legacy-fixture-selection.json').read_text());assert material(B/'fixture_restore_planning.py')['sha256']==fixture['newSHA256']
 importer_rows=[]
 for path in sorted(B.rglob('*.py')):
  if '__pycache__' in path.parts:continue
  for number,line in enumerate(path.read_text().splitlines(),1):
   if re.search(r'^\s*(?:from\s+fixture_restore_planning\s+import|import\s+fixture_restore_planning\b)',line):importer_rows.append({'path':str(path),'line':number,'source':line})
 assert len(importer_rows)==1 and Path(importer_rows[0]['path']).name=='test_restore_planning.py'
 assert material(B/'test_restore_planning.py')==material(OLD/'test_restore_planning.py')
 provenance=json.loads((Path(__file__).parent/'v27-copy-application.json').read_text());changed=[]
 for name,row in provenance['copied'].items():
  assert material(OLD/name)==row
  if material(B/name)!=row:changed.append(name)
 assert sorted(changed)==['fixture_restore_planning.py','native_desktop.py','owned_commands.py','scene_controller.py']
 for name in ('native_desktop.py','owned_commands.py','scene_controller.py'):
  assert material(B/name)['sha256']==material(QA/'restore-focus-transaction-design-v6/intended'/(name+'.proposed'))['sha256']
 dependencies={}
 for path in sorted(OLD.rglob('*.qnt')):
  target=B/path.relative_to(OLD);assert material(path)==material(target)
  dependencies[str(path)]={'selectedCurrent':str(target),**material(path),'imports':[line for line in path.read_text().splitlines() if re.match(r'^\s*(import|export)\b',line)]}
 formal=[]
 for index,row in enumerate(prior['checks'][1:],1):
  assert row['exitCode']==0 and material(row['log'])['sha256']==row['sha256']
  formal.append({'epoch':'retained-original-v27','originalIndex':index,**row})
 for row in v6['checks']:
  assert row['exitCode']==0 and material(row['log'])['sha256']==row['sha256']
  formal.append({'epoch':'actual-v6-final-admission',**row})
 for path,row in v6['sources'].items():assert material(path)==row
 for path,row in prior['sources'].items():
  source=Path(path)
  if source.suffix=='.qnt':assert material(source)==row
 sources={str(p):material(p) for p in B.rglob('*') if p.is_file() and p.suffix in ('.py','.qnt','.md') and '__pycache__' not in p.parts}
 sources.update({str(p):material(p) for p in Path(__file__).parent.rglob('*') if p.is_file() and p.suffix in ('.py','.qnt','.md')})
 inputs={str(p):material(p) for p in (prior_path,v6_path,failed_path,log,Path(__file__).parent/'legacy-fixture-selection.json',QA/'restore-focus-v6-root-source-application-grant-v1.json')}
 for row in formal:inputs[row['log']]=material(row['log'])
 row={'result':'pass','pythonTests':444,'originalPythonTests':424,'newActualCandidateTransactionTests':20,'quintNamedScenarios':480,'quintModels':38,'retainedOriginalQuintNamedScenarios':435,'retainedOriginalQuintModels':37,'newFinalTransactionQuintNamedScenarios':45,'newFinalTransactionQuintModels':1,'samplesPerModel':2000,'stepsPerSample':100,'allModelsNewlyRun':False,'original112CommandCoverage':True,'CPUCommand':prior['checks'][0]['command'],'CPULog':str(log),'CPULogMaterial':material(log),'perTestResults':actual,'originalFixtureImporters':importer_rows,'originalTwoFailedTestsRetained':original_failures,'legacyRouteCompatibilityOnly':True,'originalSixJobsAssertionsUnchanged':True,'changedInheritedFiles':sorted(changed),'formalChecks':formal,'formalDependencyMap':dependencies,'sources':sources,'inputs':inputs,'stoppedSupersededDriver':{'scope':'qa-harness-5cb0598933514ce48817c09d8833a1bb','exitCode':143,'completeCPUCommandBeforeStop':True,'reason':'Root requested retaining unchanged model proofs instead of broad repeats','partialLogsDirectory':str(QA/'restore-focus-v28-full-proof-v2')},'firstFailedFullProof':str(failed_path),'runtimeImplemented':True,'nativeAccepted':False,'nativeLaunch':False,'mainChanged':False,'original38BaselineAccepted':False,'original34FaultsAccepted':False}
 write(P/'report.json',row)
 print(json.dumps({'result':'pass','report':str(P/'report.json'),'pythonTests':444,'retainedModels':37,'newModelNamed':45,'sources':len(sources),'sha256':material(P/'report.json')['sha256']}))
if __name__=='__main__':main()
