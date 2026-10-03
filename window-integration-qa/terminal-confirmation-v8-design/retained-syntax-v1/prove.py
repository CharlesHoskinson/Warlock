import hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
D=Path(__file__).parent;O=D/'formal-before-runtime-v1';O.mkdir(mode=0o700)
q='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint';checks=[]
for label,args in [('typecheck',['typecheck',str(D/'terminal_confirmation_test.qnt')]),('test',['test',str(D/'terminal_confirmation_test.qnt'),'--backend=rust','--seed=2026100801']),('run',['run',str(D/'terminal_confirmation.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100801','--verbosity=1'])]:
 with (O/(label+'.log')).open('x') as f:
  p=subprocess.run([q,*args],stdout=f,stderr=subprocess.STDOUT,timeout=60);f.flush();os.fsync(f.fileno())
 checks.append({'label':label,'exitCode':p.returncode,'log':str(O/(label+'.log'))})
 if p.returncode:break
row={'result':'pass' if len(checks)==3 and all(r['exitCode']==0 for r in checks) else 'fail','checks':checks,'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir() if p.is_file()},'runtimeChanged':False,'nativeGrant':False}
with (O/'report.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(row));raise SystemExit(row['result']!='pass')
