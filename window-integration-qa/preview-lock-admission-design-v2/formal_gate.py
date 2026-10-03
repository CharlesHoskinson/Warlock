import hashlib,json,os,subprocess,sys
from pathlib import Path
D=Path(__file__).parent;P=D/'formal-before-source-v1';P.mkdir(mode=0o700)
commands=[['quint','typecheck',str(D/'preview_admission_test.qnt')],['quint','test',str(D/'preview_admission_test.qnt'),'--backend=rust'],['quint','run',str(D/'preview_admission.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100225','--verbosity=1']]
checks=[]
for i,cmd in enumerate(commands):
 log=P/('check-'+str(i)+'.log')
 with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 checks.append({'command':cmd,'exitCode':r.returncode,'log':str(log),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
 if r.returncode:break
report={'result':'pass'if len(checks)==3 and all(x['exitCode']==0 for x in checks)else'fail','checks':checks,'sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [D/'preview_admission.qnt',D/'preview_admission_test.qnt',D/'ADMISSION_CONTRACT.md']},'runtimeEdited':False,'nativeAccepted':False,'cgroup':Path('/proc/self/cgroup').read_text().strip()}
with os.fdopen(os.open(P/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report));sys.exit(0 if report['result']=='pass'else 1)
