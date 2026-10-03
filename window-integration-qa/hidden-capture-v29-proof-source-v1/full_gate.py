"""One original unfiltered CPU command; unchanged formal proofs retained exactly."""
import hashlib,json,os,re,stat,subprocess,sys,time
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-hidden-capture-fusion-v29')
BASE=B.with_name('service-restore-focus-transaction-v28')
sys.path.insert(0,str(QA));from qa_launch import require_qa_scope
def stamp(p):return {'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest(),'mode':stat.S_IMODE(Path(p).stat().st_mode)}
def main():
 scope=require_qa_scope();out=QA/'hidden-capture-v29-full-proof-v1';out.mkdir(mode=0o700,exist_ok=False)
 priorpath=QA/'restore-focus-v28-complete-proof-v1/report.json';prior=json.loads(priorpath.read_text());assert prior['result']=='pass'and prior['pythonTests']==444
 selected=QA/'restore-v6-actual-named-correction-v1/report.json';corrected=json.loads(selected.read_text());assert corrected['result']=='pass'
 fusionpath=QA/'hidden-capture-fusion-design-v2/formal-before-runtime.json';fusion=json.loads(fusionpath.read_text());assert fusion['result']=='pass'and fusion['namedActuallyRun']==23
 inputs={str(p):stamp(p)for p in (priorpath,selected,fusionpath,Path(__file__))}
 formal=[];named=0;retained=0
 for check in prior['formalChecks']:
  if check.get('epoch')!='retained-original-v27':continue
  assert check['exitCode']==0
  log=Path(check['log']);assert stamp(log)['sha256']==check['sha256'];inputs[str(log)]=stamp(log)
  command=check['command'];formal.append(check)
  model=BASE/command[2];current=B/command[2]
  assert model.read_bytes()==current.read_bytes();inputs[str(model)]=stamp(model);inputs[str(current)]=stamp(current)
  if command[1]=='test':
   match=re.search(r'(\d+) passing',log.read_text());assert match;named+=int(match[1]);retained+=1
 assert (named,retained)==(435,37)
 rootlog=QA/'restore-v6-actual-named-correction-v1/named.log';roottext=rootlog.read_text();assert '45 passing'in roottext;inputs[str(rootlog)]=stamp(rootlog)
 # Exact owning model bytes are separately held in the root correction packet.
 for check in fusion['checks']:
  assert check['exitCode']==0;log=Path(check['log']);assert stamp(log)['sha256']==check['sha256'];inputs[str(log)]=stamp(log)
 for path,row in fusion['sources'].items():assert stamp(path)==row;inputs[path]=row
 paths=[p for p in B.iterdir()if p.is_file()and p.suffix in ('.py','.c','.qnt','.md')]
 paths.extend(p for p in Path(__file__).parent.iterdir()if p.is_file())
 sources={str(p):stamp(p)for p in paths}
 env={k:v for k,v in os.environ.items()if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')};env['PYTHONDONTWRITEBYTECODE']='1'
 command=prior['CPUCommand'];assert command==['/usr/bin/python3','-m','unittest','discover','-s','.','-p','test_*.py','-v']
 log=out/'tests.log';start=time.monotonic()
 with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:
  try:result=subprocess.run(command,cwd=B,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90);code=result.returncode
  except subprocess.TimeoutExpired:code=124
 text=log.read_text();actual={}
 for line in text.splitlines():
  match=re.match(r'^(\w+) \(([^)]+)\) \.\.\. (ok|FAIL|ERROR)',line)
  if match:actual[match[2]+'.'+match[1]]=match[3]
 count=re.search(r'Ran (\d+) tests',text);count=int(count[1])if count else 0
 original=set(prior['perTestResults']);coverage=original.issubset(actual) and all(actual[n]=='ok'for n in original)
 stable=sources=={p:stamp(p)for p in sources} and inputs=={p:stamp(p)for p in inputs}
 passed=code==0 and count==462 and len(actual)==462 and coverage and stable and all(v=='ok'for v in actual.values())
 row={'result':'pass'if passed else 'fail','pythonTests':count,'originalPythonTests':444,'newAppliedTests':18,'originalAllTestIdentitiesExact':coverage,'perTestResults':actual,'CPUCommand':command,'cwd':str(B),'exitCode':code,'wallSeconds':time.monotonic()-start,'log':str(log),'logSHA256':stamp(log)['sha256'],'sources':sources,'inputs':inputs,'sourceUnchanged':stable,'retainedFormalChecks':formal,'retainedOriginalNamedActuallyLogged':435,'retainedOriginalModels':37,'rootCorrectedFocusNamedActuallyRun':45,'newFusionNamedActuallyRun':23,'quintNamedScenarios':503,'quintModels':39,'allModelsNewlyRun':False,'formalChecksRetainedNoRerun':True,'scope':scope,'nativeLaunch':False,'original38Accepted':False,'original34Accepted':False}
 with os.fdopen(os.open(out/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({k:row[k]for k in ('result','pythonTests','originalAllTestIdentitiesExact','exitCode','sourceUnchanged','quintNamedScenarios','quintModels')}));return int(not passed)
if __name__=='__main__':raise SystemExit(main())
