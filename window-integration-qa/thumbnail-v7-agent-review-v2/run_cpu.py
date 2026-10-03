from pathlib import Path
import hashlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();OUT=Path(__file__).resolve().parent;checks=[]
for n in ('initial_callback_probe.py','initial_callback_owner_probe_v2.py','focused.py'):
 cmd=['/usr/bin/python3','-B',str(OUT/n)];paths=[OUT/(n+'.stdout.log'),OUT/(n+'.stderr.log')]
 with os.fdopen(os.open(paths[0],os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as out,os.fdopen(os.open(paths[1],os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as error:
  p=subprocess.run(cmd,cwd='/home/hoskinson',stdout=out,stderr=error,timeout=90,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 checks.append(dict(command=cmd,cwd='/home/hoskinson',exitCode=p.returncode,logs=[dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest())for q in paths]))
 if p.returncode:break
row=dict(result='pass'if len(checks)==3 and all(c['exitCode']==0 for c in checks)else'fail',scope=scope,checks=checks,nativeLaunch=False)
with os.fdopen(os.open(OUT/'cpu.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps(row));raise SystemExit(row['result']!='pass')
