import copy,hashlib,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
import credentials
ROOT=Path(__file__).resolve().parent;out=ROOT/('credentials-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[]};procs=[]
def check(name,fn):fn();report['checks'].append({'name':name,'passed':True})
def refused(fn):
 try:fn()
 except (RuntimeError,ProcessLookupError):return
 raise AssertionError('Expected refusal')
try:
 with (out/'fusermount.stdout').open('wb') as stdout,(out/'fusermount.stderr').open('wb') as stderr:
  proc=subprocess.Popen(['/usr/bin/fusermount3','--version'],stdout=stdout,stderr=stderr);procs.append(proc)
  deadline=time.monotonic()+2
  while True:
   event=os.waitid(os.P_PID,proc.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
   if event:break
   assert time.monotonic()<deadline;time.sleep(.001)
  row=credentials.identity(proc.pid);(out/'actual-privileged.json').write_text(json.dumps({'identity':row,'metadata':credentials.metadata(proc.pid),'waitid':{'pid':event.si_pid,'uid':event.si_uid,'code':event.si_code,'status':event.si_status}},indent=2)+'\n')
  assert row['realUid']==event.si_uid==os.getuid() and row['procOwnerUid']==0 and row['effectiveUid']==0 and row['privilegedCredentials'] is True and event.si_status==0
  assert credentials.signalable(row,row) is False
  check('actual-setuid-zombie-real-ownership',lambda:None)
  check('privileged-effective-no-signal',lambda:refused(lambda:credentials.signal_exact(row,signal.SIGTERM)))
  assert proc.wait(timeout=1)==0
 proc=subprocess.Popen([sys.executable,'-c','import time;time.sleep(3)']);procs.append(proc);row=credentials.identity(proc.pid)
 changed=copy.deepcopy(row);changed['start']=str(int(row['start'])+1)
 check('actual-pidfd-wrong-start-refused',lambda:refused(lambda:credentials.signal_exact(changed,signal.SIGTERM)));assert proc.poll() is None
 changed=copy.deepcopy(row);changed['effectiveUid']=0
 check('original-privileged-tuple-refused',lambda:refused(lambda:credentials.signal_exact(changed,signal.SIGTERM)));assert proc.poll() is None
 observed=credentials.signal_exact(row,signal.SIGTERM);assert observed['start']==row['start'] and proc.wait(timeout=1)==-15;check('actual-pidfd-owned-term',lambda:None)
 check('retired-identity-refused',lambda:refused(lambda:credentials.signal_exact(row,signal.SIGTERM)))
 # Exercise actual bounded parser with captured genuine stat/status and hostile tuples.
 original=credentials.metadata(os.getpid());realmeta=credentials.metadata
 for name,mutate in [('foreign-real',lambda m:m.update(status=m['status'].replace('Uid:\t'+str(os.getuid()),'Uid:\t'+str(os.getuid()+1),1))),('wrong-pid',lambda m:m.update(stat='1 '+m['stat'].split(' ',1)[1])),('nonnumeric-uid',lambda m:m.update(status=m['status'].replace('Uid:\t','Uid:\tTrue ',1))),('missing-uid',lambda m:m.update(status='Name:\tx\n'))]:
  data=copy.deepcopy(original);mutate(data);credentials.metadata=lambda pid,d=data:d
  check(name,lambda:refused(lambda:credentials.identity(os.getpid())))
 credentials.metadata=realmeta;report['passed']=True
finally:
 credentials.metadata=globals().get('realmeta',credentials.metadata)
 for proc in procs:
  if proc.poll() is None:proc.kill();proc.wait(timeout=1)
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'credentials.py',ROOT/'activation-supervisor.py',Path('/usr/bin/fusermount3')]};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
