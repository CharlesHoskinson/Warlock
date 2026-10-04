"""CPU fake-wire subprocess tests; no Wayland/native input admission."""
import hashlib,json,os,resource,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from parent import Parent
from journal import Refused
ROOT=Path(__file__).parent/('parent-'+str(time.time_ns()));ROOT.mkdir();checks=[]
report={'passed':False,'nativeAcceptance':False,'fakeWireRealSubprocessOnly':True,'checks':checks}
class Session:
 def __init__(self):self.host=SimpleNamespace(runtime=ROOT,processes=[],env=dict(os.environ))
 def guard(self):pass
class Original:
 @staticmethod
 def process(pid):return {'pid':pid,'start':Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]}
host=SimpleNamespace(original=Original)
source='''#!/usr/bin/python3
import json,sys
print('{"ready":true,"scope":"parent-notify-only"}',flush=True)
sequence=0
for command in sys.stdin:
 if command.strip()=='quit':break
 sequence+=1
 MODE
'''
try:
 modes=[('normal','print(json.dumps(dict(sequence=sequence,accepted=True,scope="parent-notify-only")),flush=True)',True),('bool-sequence','print(json.dumps(dict(sequence=True,accepted=True,scope="parent-notify-only")),flush=True)',False),('float-sequence','print(json.dumps(dict(sequence=float(sequence),accepted=True,scope="parent-notify-only")),flush=True)',False),('numeric-accepted','print(json.dumps(dict(sequence=sequence,accepted=1,scope="parent-notify-only")),flush=True)',False),('duplicate-json','print(\'{"sequence":1,"sequence":1,"accepted":true,"scope":"parent-notify-only"}\',flush=True)',False),('partial-json','sys.stdout.write("{");sys.stdout.flush();break',False),('extra-receipt','print(json.dumps(dict(sequence=sequence,accepted=True,scope="parent-notify-only")),flush=True);print(json.dumps(dict(sequence=sequence,accepted=True,scope="parent-notify-only")),flush=True)',False)]
 for name,mode,expected in modes:
  case=ROOT/name;case.mkdir();binary=case/'fake-client';binary.write_text(source.replace('MODE',mode));binary.chmod(0o700);session=Session();parent=None;accepted=False
  try:
   parent=Parent(session,host,binary,case/'evidence',time.monotonic()+.5,lambda deadline:{'fakePeer':True});parent.send('press 272',time.monotonic()+.5)
   if expected:parent.send('release 272',time.monotonic()+.5);parent.close(time.monotonic()+.5)
   accepted=True
  except Refused:accepted=False
  finally:
   if parent:parent.abort()
  saved=json.loads((case/'evidence/record.json').read_text())
  check={'name':name,'passed':accepted==expected and saved['registered'] is True and session.host.processes[0][0].poll() is not None,'record':str(case/'evidence/record.json')};checks.append(check);assert check['passed'],name
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('parent.py'),Path(__file__).with_name('actor.py'),Path(__file__).with_name('journal.py')]}
 (ROOT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(ROOT/'report.json')
