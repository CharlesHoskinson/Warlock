"""All original106 commands plus approved scheduler/fixture formal proofs."""
import hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-focus-transaction-v28')
P=QA/'restore-focus-v28-full-proof-v1'
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 scope=require_qa_scope();P.mkdir(mode=0o700)
 env={k:v for k,v in os.environ.items() if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')};env['PYTHONDONTWRITEBYTECODE']='1'
 prior=json.loads((QA/'restore-planning-v27-full-proof-v1/report.json').read_text())
 assert (prior['result'],prior['pythonTests'],prior['quintNamedScenarios'],prior['quintModels'])==('pass',424,435,37)
 commands=[r['command'] for r in prior['checks']];assert len(commands)==112
 paths=sorted(p for p in B.iterdir() if p.is_file() and p.suffix in ('.py','.qnt','.md'))
 paths.extend(p for p in Path(__file__).parent.rglob('*') if p.is_file() and p.suffix in ('.py','.qnt','.md') and '__pycache__' not in p.parts)
 paths.append(QA/'family-preparation-thumbnail-v9/payload/home/.local/bin/hypr-window-preview')
 sources={str(p):{'sha256':sha(p),'mode':p.stat().st_mode&0o777} for p in paths}
 rows=[];cpu=named=0;failure=None;started=time.monotonic()
 for index,command in enumerate(commands):
  log=P/('check-'+str(index).zfill(3)+'.log')
  with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:
   try:r=subprocess.run(command,cwd=B,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90);code=r.returncode
   except subprocess.TimeoutExpired:code=124
  text=log.read_text();rows.append({'command':command,'exitCode':code,'log':str(log),'sha256':sha(log)})
  if index==0:
   match=re.search(r'Ran (\d+) tests',text);cpu=int(match[1]) if match else 0
  elif command[1]=='test':
   match=re.search(r'(\d+) passing',text);named+=int(match[1]) if match else 0
  if code or 'error:' in text:failure='required command failed: '+str(index);break
 exact=all(sha(Path(p))==row['sha256'] and Path(p).stat().st_mode&0o777==row['mode'] for p,row in sources.items())
 original=[r['command'] for r in rows[:112]]==[r['command'] for r in prior['checks']]
 passed=failure is None and exact and original and (cpu,named,len(rows))==(444,435,112)
 report={'result':'pass' if passed else 'fail','pythonTests':cpu,'quintNamedScenarios':named,'quintModels':37,'samplesPerModel':2000,'stepsPerSample':100,'checks':rows,'sources':sources,'sourceUnchangedDuringProof':exact,'original112CommandsExact':original,'wallSeconds':time.monotonic()-started,'failure':failure,'nativeLaunch':False,'nativeAccepted':False,'scope':scope,'mainChanged':False}
 with os.fdopen(os.open(P/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({k:v for k,v in report.items() if k not in ('checks','sources')}));return int(not passed)
if __name__=='__main__':raise SystemExit(main())
