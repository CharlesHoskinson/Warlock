#!/usr/bin/python3
from pathlib import Path
import os,sys,json,time,subprocess,hashlib,stat
D=Path(__file__).resolve().parent
if len(sys.argv)>1 and sys.argv[1]=='delegate':
    fd=os.open(sys.argv[2],os.O_RDONLY)
    value=os.read(fd,1);os.close(fd)
    sys.exit(0 if value==b'1' else 125)
sys.path.insert(0,'/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v10')
import helper_setup as setup
import helper_observer as observer
from qa_launch import require_qa_scope
scope=require_qa_scope()
def write(path,row):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(row,f,indent=2);f.write('\n')
log=D/'actual-helper-events.jsonl';fd=os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
gate=D/'delegate.fifo';os.mkfifo(gate,0o600)
# O_RDWR retains an owned writer so opening the actual delegate never blocks startup.
gate_fd=os.open(gate,os.O_RDWR|os.O_CLOEXEC)
ready=D/'actual-ready.json';wrapper=None
try:
    command=['/usr/bin/python3','-B',str(D/'fixture_wrapper.py'),str(log),str(ready),str(gate),str(D/'replay.py')]
    wrapper=subprocess.Popen(command)
    limit=time.monotonic()+3
    while not ready.exists() and time.monotonic()<limit:
        if wrapper.poll() is not None:raise RuntimeError('fixture wrapper exited before ready')
        time.sleep(.002)
    row=json.loads(ready.read_text())
    actual={name:observer.process(row[name]['pid']) for name in ('wrapper','delegate')}
    for name in actual:
        if actual[name]!=row[name]:raise RuntimeError('actual fixture identity differs')
    config={'log':str(log),'allowed':['hydrate'],'fixtureOnly':True}
    before=time.monotonic()
    try:setup.wait_and_archive(config,D/'original-failure-archive.json',expect_harness=True)
    except RuntimeError as e:error=str(e)
    else:raise AssertionError('Original missing harness oracle accepted')
    elapsed=time.monotonic()-before
    live_at_failure={name:observer.still_live(row[name]) for name in ('wrapper','delegate')}
    if error!='Exactly one harness query required' or not all(live_at_failure.values()):raise AssertionError('Expected live-job early failure absent')
    os.write(gate_fd,b'1')
    code=wrapper.wait(timeout=3)
    with observer.locked_log(log) as stream:events=observer.rows(stream)
    closure=observer.summarize(events,config['allowed'],require_all=False,expect_harness=False)
    if code!=0 or closure is None or not closure['allNormal']:raise AssertionError('Actual fixture normal closure absent')
    # The unchanged full acceptance oracle still refuses AFTER genuine normal closure.
    try:observer.summarize(events,config['allowed'],expect_harness=True)
    except RuntimeError as e:after_error=str(e)
    else:raise AssertionError('Missing harness was normalized')
    if after_error!=error:raise AssertionError('Original error changed')
    inputs=[D/'replay.py',D/'fixture_wrapper.py',Path(setup.__file__),Path(observer.__file__)]
    write(D/'actual-counterexample.json',dict(result='pass',scope=scope,fixtureOnly=True,nativeLaunched=False,compositorAuthorityClaimed=False,sourceInputs={str(p):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)} for p in inputs},wrapperArgv=command,actualRegistration=actual,originalError=error,errorAfterClosure=after_error,originalErrorSeconds=elapsed,liveAtOriginalError=live_at_failure,actualWrapperExitCode=code,actualTerminalClosure=closure,allSelectedLifetimesGone=not any(observer.still_live(row[name]) for name in ('wrapper','delegate')),productionWrapperEnvelopeExercised=False))
    print(json.dumps({'result':'pass','originalError':error,'liveAtOriginalError':live_at_failure,'actualNormalClosure':True,'originalErrorSeconds':elapsed}))
finally:
    os.close(gate_fd)
    if wrapper is not None and wrapper.poll() is None:
        fd=os.open(gate,os.O_RDWR);os.write(fd,b'1');os.close(fd);wrapper.wait(timeout=3)
