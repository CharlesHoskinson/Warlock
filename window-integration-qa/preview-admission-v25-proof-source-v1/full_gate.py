"""External unfiltered inherited proof; no native GUI or candidate writes."""
import hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-preview-lock-admission-v25')
P=QA/'preview-admission-v25-full-proof-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 P.mkdir(mode=0o700)
 env={k:v for k,v in os.environ.items()if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')};env['PYTHONDONTWRITEBYTECODE']='1'
 prior=json.loads((QA/'family-preparation-v24-full-proof-v1/report.json').read_text())
 commands=[c['command']for c in prior['checks']]
 assert len(commands)==100
 commands.extend([['quint','typecheck','preview_admission_test.qnt'],['quint','test','preview_admission_test.qnt','--backend=rust','--seed=2026100225'],['quint','run','preview_admission.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100225','--verbosity=0']])
 paths=sorted(p for p in B.iterdir()if p.is_file()and p.suffix in('.py','.qnt','.md'))
 paths.extend([Path(__file__),Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v9/payload/home/.local/bin/hypr-window-preview')])
 sources={str(p):{'sha256':sha(p),'mode':p.stat().st_mode&0o777}for p in paths}
 checks=[];cpu=0;named=0;started=time.monotonic();failure=None
 for index,command in enumerate(commands):
  log=P/('check-'+str(index).zfill(2)+'.log')
  with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as out:
   try:result=subprocess.run(command,cwd=B,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=90);code=result.returncode
   except subprocess.TimeoutExpired:code=124
  text=log.read_text();checks.append({'command':command,'exitCode':code,'log':str(log),'sha256':sha(log)})
  if index==0:
   m=re.search(r'Ran (\d+) tests',text);cpu=int(m[1])if m else 0
  elif command[1]=='test':
   m=re.search(r'(\d+) passing',text);named+=int(m[1])if m else 0
  if code or'error:'in text:failure='required command failed: '+str(index);break
 exact=all(sha(Path(p))==row['sha256']and Path(p).stat().st_mode&0o777==row['mode']for p,row in sources.items())
 passed=failure is None and exact and(cpu,named,len(checks))==(395,377,103)
 report={'result':'pass'if passed else'fail','pythonTests':cpu,'quintNamedScenarios':named,'quintModels':34,'samplesPerModel':2000,'stepsPerSample':100,'checks':checks,'sources':sources,'sourceUnchangedDuringProof':exact,'original100CommandsExact':[x['command']for x in checks[:100]]==[x['command']for x in prior['checks']],'wallSeconds':time.monotonic()-started,'failure':failure,'nativeLaunch':False,'nativeAccepted':False,'scope':Path('/proc/self/cgroup').read_text().strip(),'mainChanged':False}
 with os.fdopen(os.open(P/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as out:json.dump(report,out,indent=2);out.write('\n')
 print(json.dumps({k:v for k,v in report.items()if k not in('checks','sources')}));sys.exit(0 if passed else 1)
main()
