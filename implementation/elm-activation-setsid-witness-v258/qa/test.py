"""Actual pre-fix supervisor witness with real setsid grandchild; no GUI."""
import hashlib,json,os,resource,shutil,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'qa'/('witness-'+str(time.time_ns()));out.mkdir()
supervisor=ROOT/'original/activation-supervisor.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'unsafeWitnessConfirmed':False,'nativeAcceptance':False,'cases':[],'sourceSHA256':sha(supervisor)}
try:
 for label,code,expected in [('ordinary-exit','import time;time.sleep(.08)',True),('setsid-grandchild','import os,time;pid=os.fork();os.setsid() if pid==0 else None;time.sleep(.05 if pid==0 else .2)',False)]:
  case=out/label;case.mkdir();runtime=private_runtime();process=None;record={'name':label,'expectedNormalSuccess':expected,'runtime':str(runtime)}
  try:
   descriptor=runtime/'activation.json';descriptor.write_text(json.dumps({'argv':['/usr/bin/python3','-c',code],'binarySHA256':sha(Path('/usr/bin/python3'))}))
   shutil.copyfile(descriptor,case/'descriptor.json')
   argv=['/usr/bin/python3','-B',str(supervisor),str(descriptor),str(case/'events.jsonl')]
   with (case/'stdout').open('xb') as stdout,(case/'stderr').open('xb') as stderr:
    process=subprocess.Popen(argv,stdout=stdout,stderr=stderr,env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime)),start_new_session=True)
    record['pid']=process.pid;record['start']=Path('/proc',str(process.pid),'stat').read_text().rsplit(')',1)[1].split()[19]
    process.wait(timeout=5);record['exitCode']=process.returncode
   events=[json.loads(line) for line in (case/'events.jsonl').read_text().splitlines()]
   if expected:assert process.returncode==0 and events[-1]['kind']=='terminal' and events[-1]['childExitCode']==0
   else:
    assert process.returncode!=0 and events[-1]['kind']=='unobserved-child-exit'
    assert os.waitstatus_to_exitcode(events[-1]['status'])==0
    assert 'child exited before identity observation' in (case/'stderr').read_text()
   record['passed']=True;report['cases'].append(record)
  finally:
   if process is not None and process.poll() is None:
    process.terminate()
    try:process.wait(timeout=.5)
    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=.5)
   token=('XDG_RUNTIME_DIR='+str(runtime)).encode();cleanup=[]
   for p in Path('/proc').glob('[0-9]*'):
    try:
     if p.stat().st_uid!=os.getuid() or token not in (p/'environ').read_bytes().split(b'\0'):continue
     started=(p/'stat').read_text().rsplit(')',1)[1].split()[19]
     if (p/'stat').read_text().rsplit(')',1)[1].split()[19]!=started:continue
     os.kill(int(p.name),signal.SIGTERM);cleanup.append({'pid':int(p.name),'start':started})
    except (OSError,IndexError):pass
   record['failureCleanupSignals']=cleanup
   assert not cleanup,'toy child remained after actual terminal wait statuses'
   # Both literal toy child branches have already exited before the supervisor
   # failure. Unknown-child waitStatus is a real completed/reaped child status.
   shutil.rmtree(runtime)
 report.update(passed=True,unsafeWitnessConfirmed=True)
finally:
 report['testSHA256']=sha(Path(__file__));(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
