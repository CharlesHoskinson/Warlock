"""Original unfiltered CPU command; source-exact fourteen models are retained."""
import hashlib,json,os,re,resource,stat,subprocess,sys,time
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa');B=QA/'family-preparation-thumbnail-v14';BASE=QA/'family-preparation-thumbnail-v12';OUT=QA/'thumbnail-v14-cpu-proof-v1'
sys.path.insert(0,str(QA));from qa_launch import require_qa_scope
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sources():return {str(p):{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}for p in sorted(B.rglob('*'))if p.is_file()and '__pycache__'not in p.parts and p.name!='frozen-inputs.json'and not any(n.startswith('attempt-')for n in p.parts)}
def main():
 scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1);OUT.mkdir(mode=0o700)
 before=sources();command=['/usr/bin/python3','-B',str(B/'run_collector_v9_cpu.py')];log=OUT/'cpu.log';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(B));start=time.monotonic();error=None;code=None
 with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as stream:
  try:code=subprocess.run(command,cwd='/home/hoskinson',env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=120).returncode
  except subprocess.TimeoutExpired:error='original120s aggregate expired'
  stream.flush();os.fsync(stream.fileno())
 text=log.read_text();match=re.search(r'Ran (\d+) tests',text);count=int(match[1])if match else 0
 actual={name+'.'+test:status for test,name,status in re.findall(r'^(test\S+) \(([^)]+)\) \.\.\. (.*)$',text,re.M)}
 prior_path=QA/'thumbnail-v12-full-proof-v1/report.json';prior=json.loads(prior_path.read_text());assert (prior['result'],prior['pythonTests'],prior['quintNamedScenarios'],prior['quintModels'])==('pass',169,205,14)
 original_log=Path(prior['checks'][0]['log']);original={name+'.'+test for test,name,status in re.findall(r'^(test\S+) \(([^)]+)\) \.\.\. (.*)$',original_log.read_text(),re.M)}
 formal=[]
 for row in prior['checks'][1:]:
  assert row['exitCode']==0 and sha(row['log'])==row['sha256'];formal.append({'epoch':'retained-unprofiled-B12',**row})
 models={}
 for p in BASE.rglob('*.qnt'):
  rel=p.relative_to(BASE)
  if '__pycache__'in rel.parts or any(n.startswith('attempt-')for n in rel.parts):continue
  target=B/rel;assert p.read_bytes()==target.read_bytes()and stat.S_IMODE(p.stat().st_mode)==stat.S_IMODE(target.stat().st_mode)
  models[str(p)]={'current':str(target),'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}
 after=sources();passed=error is None and code==0 and before==after and count==169 and len(actual)==169 and set(actual)==original and all(v=='ok'for v in actual.values())and re.search(r'\nOK\s*$',text)and not re.search(r'skipped=',text)
 row={'result':'pass'if passed else 'fail','pythonTests':count,'quintNamedScenarios':205,'quintModels':14,'allModelsNewlyRun':False,'sourceUnchangedDuringProof':before==after,'sources':before,'sourceDriver':{'path':__file__,'sha256':sha(__file__)},'checks':[{'argv':command,'cwd':'/home/hoskinson','exitCode':code,'elapsedSeconds':time.monotonic()-start,'log':str(log),'sha256':sha(log)}]+formal,'retainedFormalDependencies':models,'perTestResults':actual,'originalUnfilteredTestIdentitiesExact':set(actual)==original,'retainedOriginalModelReport':str(prior_path),'retainedOriginalModelReportSHA256':sha(prior_path),'error':error,'scope':scope,'nativeLaunch':False,'mainChanged':False,'original38BaselineAccepted':False,'original34FaultsAccepted':False}
 with os.fdopen(os.open(OUT/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({k:row[k]for k in ('result','pythonTests','quintNamedScenarios','quintModels','allModelsNewlyRun','sourceUnchangedDuringProof','error')}));return int(not passed)
if __name__=='__main__':raise SystemExit(main())
