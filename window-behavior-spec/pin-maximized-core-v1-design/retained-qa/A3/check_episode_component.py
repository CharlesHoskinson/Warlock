import hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
B=Path(__file__).parent;O=B.parent/'pin-input-episode-v2-cpu-v2';O.mkdir(mode=0o700)
files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(B));cmd=['/usr/bin/python3','-B','-m','unittest','discover','-s',str(B),'-v']
with (O/'cpu.log').open('x') as f:
 p=subprocess.run(cmd,cwd='/home/hoskinson',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=60);f.flush();os.fsync(f.fileno())
unchanged=all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==s for n,s in files.items());row={'result':'pass' if p.returncode==0 and unchanged else 'fail','exitCode':p.returncode,'sourceUnchanged':unchanged,'sources':files,'nativeLaunch':False,'mainChanged':False,'scope':Path('/proc/self/cgroup').read_text().strip()}
with (O/'report.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({k:v for k,v in row.items() if k!='sources'}));raise SystemExit(row['result']!='pass')
