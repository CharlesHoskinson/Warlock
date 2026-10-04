"""Real child lifecycle with controlled late-completion observation and unsafe ancestor."""
import hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,time,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):
 spec=importlib.util.spec_from_file_location('deadline_relay',p);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);return r
if len(sys.argv)>1 and sys.argv[1]=='worker':
 r=load(Path(sys.argv[3]));real_os=os;real_clock=time.monotonic;late={'value':False,'eof':False,'fd':None};origin=real_clock();real_popen=subprocess.Popen
 class Actor:
  def __init__(self,*a,**k):self.real=real_popen(*a,**k);late['fd']=self.real.stdout.fileno()
  def __getattr__(self,n):return getattr(self.real,n)
  def poll(self):
   result=self.real.poll()
   if result==0:
    if not late['eof']:return None
    late['value']=True
   return result
 def read(fd,n):
  data=real_os.read(fd,n)
  if fd==late['fd'] and not data:late['eof']=True
  return data
 r.subprocess=types.SimpleNamespace(Popen=Actor,PIPE=subprocess.PIPE,TimeoutExpired=subprocess.TimeoutExpired)
 r.os=types.SimpleNamespace(**{k:getattr(os,k) for k in dir(os) if not k.startswith('__')});r.os.read=read
 r.time=types.SimpleNamespace(monotonic=lambda:origin+100 if late['value'] else real_clock())
 r.pump([sys.executable,'-B','-c','import sys;sys.stdin.buffer.read()'],sys.argv[2]);raise SystemExit(0)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('deadline-'+str(time.time_ns()));(OUT/'inputs/qa').mkdir(parents=True)
for p in [Path(__file__),ROOT/'qa/relay.py']:shutil.copy2(p,OUT/'inputs/qa'/p.name)
ancestor=ROOT.parents[1]/'elm-geometry-broker-eof-relay-fixed-v89/qa/relay.py';shutil.copy2(ancestor,OUT/'inputs/qa/unsafe-success-first.py')
r=load(OUT/'inputs/qa/relay.py');checks=[];children=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
report={'passed':False,'scope':'Controlled late observation of real child normal completion; unsafe previous publication ordering must fail exact cutoff oracle','checks':checks}
try:
 for name,path,wanted in [('candidate',OUT/'inputs/qa/relay.py',False),('unsafe-ancestor',OUT/'inputs/qa/unsafe-success-first.py',True)]:
  ctl=OUT/name;ctl.mkdir(mode=0o700);c=subprocess.Popen([sys.executable,'-B',str(OUT/'inputs/qa/deadline.py'),'worker',str(ctl),str(path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);children.append(c)
  end=time.monotonic()+3
  while not (ctl/'actor.json').exists():
   assert c.poll() is None and time.monotonic()<end;time.sleep(.005)
  r.close_stdin(ctl);out,err=c.communicate(timeout=4)
  check(name+' exact late-publication outcome',(c.returncode==0)==wanted)
  check(name+' no fabricated stdout',out==b'')
  check(name+' completion record agrees with cutoff',(ctl/'exit.json').exists()==wanted)
  if not wanted:check('candidate refuses absolute late completion',b'Broker EOF deadline' in err)
  report[name]={'exitCode':c.returncode,'stderr':err.decode(),'normalRecordPublished':(ctl/'exit.json').exists()}
 report['passed']=True
except Exception as error:report['error']=repr(error)
finally:
 for c in children:
  if c.poll() is None:c.terminate();c.wait(timeout=3)
 report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
