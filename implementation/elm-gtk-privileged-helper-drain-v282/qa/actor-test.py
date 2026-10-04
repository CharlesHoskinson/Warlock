"""Real CPU subprocess ownership/lifecycle tests; fake journal, no GTK/display."""
import hashlib,json,os,resource,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from actor import Actor
from journal import Refused
ROOT=Path(__file__).parent/('actor-'+str(time.time_ns()));ROOT.mkdir()
checks=[];report={'passed':False,'nativeAcceptance':False,'fakeJournalRealSubprocessOnly':True,'checks':checks}
class Session:
 def __init__(self):self.host=SimpleNamespace(runtime=ROOT,processes=[]);self.env=dict(os.environ)
 def guard(self):pass
class Original:
 @staticmethod
 def process(pid):return {'pid':pid,'start':Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]}
host=SimpleNamespace(original=Original)
source='''#!/usr/bin/python3
import json,os,sys,time
seq=0;request=0
start=int(open('/proc/self/stat').read().rsplit(')',1)[1].split()[19])
profile='default-group' if '--run-default-group' in sys.argv else 'independent-groups'
def emit(event,**fields):
 global seq
 seq+=1
 row=dict(schema=1,pid=os.getpid(),processStarted=start,sequence=seq,monotonicUs=int(time.monotonic()*1000000),requestSequence=request,event=event,profile=profile)
 row.update(fields);print(json.dumps(row),flush=True)
emit('ready')
for text in sys.stdin:
 words=text.split();request=int(words[0]);emit('request',command=words[1],**({'requestedRole':words[2]} if len(words)>2 else {}))
 if words[1]=='quit':
  emit('normalexit')
  MODE
  break
'''
try:
 for name,mode,expected,profile in [('normal','pass',True,'independent-groups'),('default-profile','pass',True,'default-group'),('partial-terminal',"sys.stdout.write('{');sys.stdout.flush()",False,'independent-groups'),('after-exit',"emit('unexpected-after-exit')",False,'independent-groups'),('repeat-exit',"emit('normalexit')",False,'independent-groups')]:
  case=ROOT/name;case.mkdir();binary=case/'fake-client';binary.write_text(source.replace('MODE',mode));binary.chmod(0o700)
  session=Session();actor=None;ok=False
  try:
   actor=Actor(session,host,binary,case/'evidence',time.monotonic()+1,profile=profile)
   actor.send('inspect',time.monotonic()+1);actor.close(time.monotonic()+1);ok=True
  except Refused:ok=False
  finally:
   if actor:actor.abort()
  entries=session.host.processes
  assert len(entries)==1 and entries[0][0].poll() is not None
  saved=json.loads((case/'evidence/actor.json').read_text())
  checks.append({'name':name,'passed':ok==expected and saved['registered'] is True and saved['exitCode']==0,'actualExit':saved['exitCode'],'record':str(case/'evidence/actor.json')})
  assert checks[-1]['passed'],name
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('actor.py'),Path(__file__).with_name('journal.py')]}
 (ROOT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(ROOT/'report.json')
