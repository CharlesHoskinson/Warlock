import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
def stamp(path):return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':stat.S_IMODE(path.stat().st_mode)}
def save(path,row):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as stream:json.dump(row,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
scope=require_qa_scope()
paths=[path for path in HERE.iterdir() if path.is_file() and path.name!='focused-proof.json' and not path.name.endswith('.log')]
sources={str(path):stamp(path) for path in paths}
command=['/usr/bin/python3','-B',str(HERE/'test_proposal.py')];start=time.monotonic()
log=HERE/'focused-proof.log'
with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as stream:result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=60)
unchanged=sources=={str(path):stamp(path) for path in paths}
observations=json.loads((HERE/'focused-observations.json').read_text())
row={'result':'pass' if result.returncode==0 and unchanged and observations['result']=='pass' else 'fail',
    'scope':scope,'command':command,'exitCode':result.returncode,'seconds':time.monotonic()-start,'log':str(log),'logMaterial':stamp(log),
    'sources':sources,'sourceUnchanged':unchanged,'tests':observations['tests'],'CPUProtocolOnly':True,'nativeLuaExecuted':False,'runtimeApplied':False,
    'observations':str(HERE/'focused-observations.json'),'observationMaterial':stamp(HERE/'focused-observations.json')}
save(HERE/'focused-proof.json',row);print(json.dumps({'result':row['result'],'tests':row['tests'],'report':str(HERE/'focused-proof.json')}))
raise SystemExit(row['result']!='pass')
