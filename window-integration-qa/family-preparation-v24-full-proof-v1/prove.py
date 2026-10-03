from pathlib import Path
import hashlib,json,os,re,stat,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24');BASE=B.with_name('service-family-preparation-v23');OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();scope=require_qa_scope()
sources={str(p):dict(sha256=sha(p),mode=stat.S_IMODE(p.stat().st_mode))for p in B.iterdir()if p.is_file()and p.suffix in ('.py','.qnt','.md','.c')}
prior=json.loads(Path('/home/hoskinson/window-integration-qa/family-preparation-v23-full-proof-v1/report.json').read_text());commands=[row['command'] for row in prior['checks']]
commands += [['quint','typecheck','renderer_job_role_test.qnt'],['quint','test','renderer_job_role_test.qnt'],['quint','run','renderer_job_role.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=20261002','--verbosity=0']]
env={k:v for k,v in os.environ.items()if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')};env['PYTHONDONTWRITEBYTECODE']='1'
checks=[];begin=time.monotonic()
for i,cmd in enumerate(commands):
 log=OUT/f'check-{i:02}.log'
 with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:
  try:p=subprocess.run(cmd,cwd=B,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300);code=p.returncode
  except subprocess.TimeoutExpired:code=124
 checks.append(dict(command=cmd,exitCode=code,log=str(log),sha256=sha(log)))
 print(json.dumps(dict(check=i,exitCode=code,elapsed=round(time.monotonic()-begin,2))),flush=True)
 if code:break
unchanged=all(sha(p)==r['sha256']and stat.S_IMODE(Path(p).stat().st_mode)==r['mode']for p,r in sources.items());changed=[];same=[]
for name,row in json.loads((B/'v23-source-inheritance-before-v24.json').read_text())['sources'].items():
 assert sha(row['base'])==row['sha256']and stat.S_IMODE(Path(row['base']).stat().st_mode)==row['mode']
 assert stat.S_IMODE((B/name).stat().st_mode)==row['mode']
 (same if sha(B/name)==row['sha256']else changed).append(name)
python_count=re.search(r'Ran (\d+) tests',Path(checks[0]['log']).read_text());python_count=int(python_count[1])if python_count else None
named=0;models=0
for check in checks:
 if check['command'][0]=='quint'and check['command'][1]=='test':
  match=re.search(r'(\d+) passing',Path(check['log']).read_text());named+=int(match[1])if match else 0
 if check['command'][0]=='quint'and check['command'][1]=='run':models+=1
passed=len(checks)==100 and all(c['exitCode']==0 for c in checks)and unchanged and changed==['batch_preview.py','native_runtime.py']and (python_count,named,models)==(377,332,33)
row=dict(result='pass'if passed else 'fail',scope=scope,pythonTests=python_count,quintNamedScenarios=named,quintModels=models,samplesPerModel=2000,stepsPerSample=100,sourceUnchangedDuringProof=unchanged,sources=sources,checks=checks,changedInheritedSources=changed,inheritedExact=same,baseManifestSHA256=sha(BASE/'manifest-family-preparation-v23.json'),elapsedSeconds=time.monotonic()-begin,nativeAccepted=False,mainChanged=False,originalDeadlineSeconds=2,batchTargetAPISelected=False)
with os.fdopen(os.open(OUT/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in row.items()if k not in ('sources','checks','inheritedExact')}));raise SystemExit(not passed)
