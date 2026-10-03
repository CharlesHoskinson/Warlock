"""Original collector CPU/formal gate; logs external, never launches GUI."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import time

B=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v11')
QA=B.parent
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
OUT=args.output.absolute();assert OUT.parent==QA and OUT.name.startswith('thumbnail-v11-')
OUT.mkdir(mode=0o700)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sources():
    return {str(p):{'sha256':sha(p),'mode':p.stat().st_mode&0o7777} for p in sorted(B.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='frozen-inputs.json' and not any(v.startswith('attempt-') for v in p.parts)}
before=sources();checks=[];started=time.monotonic();named=0;python_tests=0
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(B))
def run(argv,label,timeout=60):
    path=OUT/(label+'.log');start=time.monotonic_ns()
    with path.open('x') as f:
        result=subprocess.run(argv,cwd='/home/hoskinson',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
        f.flush();os.fsync(f.fileno())
    row={'argv':argv,'cwd':'/home/hoskinson','exitCode':result.returncode,'elapsedNs':time.monotonic_ns()-start,'log':str(path),'sha256':sha(path)}
    checks.append(row)
    if result.returncode:raise RuntimeError(label+' failed; exact log retained '+str(path))
    return path.read_text()
models=['helper_lifecycle','query_lifecycle','capture_lifecycle','service_queries','reversal','service_restart','recovery_collection','actual_service_binding','batch_service_binding','batch_callback_identity','terminal_confirmation','renderer_collector_binding','closure_alias_identity','helper_failure_drain']
error=None
try:
    text=run(['/usr/bin/python3','-B',str(B/'run_collector_v9_cpu.py')],'cpu',120)
    python_tests=int(re.search(r'Ran (\d+) tests',text).group(1))
    assert re.search(r'\nOK\s*$',text) and not re.search(r'skipped=',text)
    quint='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
    for name in models:
        source=B/(name+'.qnt');test=B/(name+'_test.qnt');test=test if test.exists() else source
        run([quint,'typecheck',str(test)],name+'-typecheck')
        text=run([quint,'test',str(test),'--backend=rust','--seed=2026100701'],name+'-test')
        count=int(re.search(r'(\d+) passing',text).group(1));named+=count;checks[-1]['named']=count
        invariant='allProps' if name in ('service_restart','recovery_collection','actual_service_binding','batch_service_binding','batch_callback_identity','terminal_confirmation','renderer_collector_binding','closure_alias_identity','helper_failure_drain') else 'invariant'
        run([quint,'run',str(source),'--invariant='+invariant,'--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100701','--verbosity=1'],name+'-run')
except BaseException as failure:
    error={'type':type(failure).__name__,'message':str(failure)}
after=sources()
row={'result':'pass' if error is None and before==after else 'fail','pythonTests':python_tests,'quintNamedScenarios':named,'quintModels':len(models),'samplesPerModel':2000,'stepsPerSample':100,'sources':before,'sourceUnchangedDuringProof':before==after,'sourceDriver':{'path':__file__,'sha256':sha(__file__)},'checks':checks,'error':error,'elapsedSeconds':time.monotonic()-started,'nativeLaunch':False,'mainChanged':False,'scope':{'cgroup':Path('/proc/self/cgroup').read_text().strip(),'coreLimit':1}}
with (OUT/'report.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({k:row[k] for k in ('result','pythonTests','quintNamedScenarios','quintModels','sourceUnchangedDuringProof','error')}))
raise SystemExit(row['result']!='pass')
