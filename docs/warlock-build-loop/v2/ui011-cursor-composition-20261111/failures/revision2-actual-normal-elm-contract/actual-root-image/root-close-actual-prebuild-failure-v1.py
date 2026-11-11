from hashlib import sha256
from pathlib import Path
import datetime
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

repo = Path.cwd()
record_name = '.warlock-contributor/ui011-observed-opener-closure-root-20261110.json'
record_path = repo / record_name
candidate, handle, raw, raw_sha, directory, prefix, failure = sys.argv[1:]
out = Path(directory)
assert not Path(prefix).is_absolute() and '..' not in Path(prefix).parts

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_bytes())

def encode(row):
    return (json.dumps(row,indent=2)+'\n').encode()

raw_path = repo / raw
assert raw_path.is_relative_to(repo) and raw_path.resolve(strict=True)==raw_path
assert digest(raw_path)==raw_sha
actual = read(raw_path)
outer = read(out/'terminal.json')
assert outer['stdoutSha256']==digest(out/'stdout') and outer['stderrSha256']==digest(out/'stderr')
exit_code = outer['actualExit']
assert type(exit_code) is int and exit_code != 0 and actual == outer and digest(raw_path)==digest(out/'terminal.json')
assert (exit_code==0 and not failure) or (exit_code!=0 and failure)
launch = json.loads(Path(str(record_path)+'.launches.jsonl').read_text().splitlines()[-1])
assert launch['candidateSha256']==candidate
assert launch['scope']=='cpu' and failure=='image-input-current-loader-cache-changed-313a'
job = launch['jobId']
processes = {launch['pid']:launch['startTicks']}
if launch['scope']=='native':
    processes.update({row['pid']:row['startTicks'] for row in actual.get('stackRetirement',{}).get('processes',[])})
for entry in Path('/proc').iterdir():
    if not entry.name.isdecimal():continue
    try:
        fields=(entry/'stat').read_text().rsplit(')',1)[1].split()
    except (FileNotFoundError,ProcessLookupError,PermissionError):
        continue
    assert fields[19]!=processes.get(int(entry.name)) and int(fields[2]) not in processes
launch_path=out/'launch.json'
if launch_path.exists():
    assert read(launch_path)==launch
else:
    with launch_path.open('xb') as stream:stream.write(encode(launch))
spec=importlib.util.spec_from_file_location('warlock',repo/'plugins/warlock-contributor/scripts/warlock.py')
core=importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
path=prefix+'-terminal.json'
terminal=dict(terminal=True,jobId=job,candidateSha256=candidate,scope=launch['scope'],
              manifestSha256=core.json_sha256(launch['manifest']),
              fixtureSha256=core.json_sha256(launch['manifest']['fixtures']),
              exit=exit_code,classification='pass' if exit_code==0 else 'failed',
              actualOuterHandle=handle,actualOuterHandleConsumed=True,originalAcceptance=False,
              nativeAcceptance=False,rawReport=dict(path=raw,sha256=raw_sha))
if failure:
    terminal['failureSignature']=failure
if launch['scope']=='cpu':
    terminal.update(imageQualificationOnly=True,newProductAdvance=False)
else:
    terminal.update(nativeExecuteReached=True)
terminal.update(inputVerificationFailedBeforeBuild=True,builderReportProduced=False,buildCommandsExecuted=False,cleanupClaimed=False)
body=encode(terminal)
common=dict(candidateSha256=candidate,jobId=job)
files={path:body,prefix+'-started-event.json':encode(dict(common,eventId=f'ui011-keymap-{launch["scope"]}-started-{handle}',
            kind='execution-started',outerHandle=handle)),prefix+'-finished-event.json':encode(dict(common,
            eventId=f'ui011-keymap-{launch["scope"]}-finished-{handle}',kind='execution-finished',
            outerHandleConsumed=True,report=dict(path=path,sha256=sha256(body).hexdigest())))}
claims={}
claim_path=out/'closure-claims.jsonl'
if claim_path.exists():
    claims={row['resource'].removeprefix('file:'+str(repo)+'/'):row for row in map(json.loads,claim_path.read_text().splitlines())}
    assert set(claims)<=set(files)
with claim_path.open('a') as evidence:
    for name in files:
        if name in claims:continue
        claim=subprocess.run(['agentbus','claim','file:'+str(repo/name),'--lease','60','--wait','4'],capture_output=True,text=True)
        if claim.returncode:
            print(claim.stdout,claim.stderr,file=sys.stderr)
            claim.check_returncode()
        row=json.loads(claim.stdout);assert row['kind']=='grant' and row['hold']
        claims[name]=row
        evidence.write(claim.stdout.rstrip()+'\n')
        evidence.flush()
with core.delivery_edit_lock(repo,record_name):
    rec=core.read(record_path);rec['_recordPath']=record_name
    assert rec['delivery']['events'][-1]['kind']=='review'
    assert rec['delivery']['events'][-1]['candidateSha256']==candidate
    reqs,state=core.context(repo)
    core.validate_delivery_edit_precheck(repo,rec,reqs,state,34,list(files))
    for name in files:
        assert not (repo/name).exists() and not (repo/name).is_symlink()
        assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(claims[name]['lease_end'])
    for name,value in files.items():
        dest=repo/name
        with tempfile.NamedTemporaryFile(dir=dest.parent,delete=False) as stream:
            stream.write(value);stream.flush();os.fsync(stream.fileno())
        os.replace(stream.name,dest)
for phase in ('started','finished'):
    command=['/usr/bin/python3','-B','plugins/warlock-contributor/scripts/warlock.py','--repo',str(repo),
             '--record',record_name,'delivery-event','--event-file',prefix+f'-{phase}-event.json',
             '--expect-record-sha',digest(record_path),'--expect-selection','34']
    with (out/(phase+'-admission.stdout')).open('xb') as stdout,(out/(phase+'-admission.stderr')).open('xb') as stderr:
        subprocess.run(command,stdout=stdout,stderr=stderr,check=True)
print(job,'closed',exit_code,'record',digest(record_path),'terminal',digest(repo/path),'absent births',len(processes))
