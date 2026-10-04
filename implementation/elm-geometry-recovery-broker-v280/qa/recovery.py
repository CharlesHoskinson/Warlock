"""Real daemon subprocess stdio and durable journal, synthetic native transport."""
import copy,fcntl,hashlib,json,os,resource,selectors,subprocess,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from recovery_journal import Journal,validate
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('recovery-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'checks':[],'scope':'Actual broker subprocess/stdio/filesystem and strict endpoint decoders with synthetic native transport; no native process authentication, geometry mutation, pixels or Elm integration acceptance','inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*sorted((ROOT/'adapter').glob('*.py')),Path(__file__),ROOT/'qa/transport.py']},'runs':[]}
B={'lifetime':'71','session':'2','frontend':'3'}
def effect(p,op):return {'protocolVersion':3,'kind':'window-effect','effectProtocol':p,'binding':copy.deepcopy(B),'intent':{'request':'41','generation':'43','incarnation':'7','operation':op,'context':{'lifetime':'71','epoch':'3','output':'14','revision':'13'}}}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
class Reader:
 def __init__(self,stream):self.stream=stream;self.tail=b'';self.frames=[]
 def frame(self):
  deadline=time.monotonic()+3
  while not self.frames:
   with selectors.DefaultSelector() as selector:
    selector.register(self.stream,selectors.EVENT_READ);assert selector.select(max(0,deadline-time.monotonic())),'CPU receipt timeout'
   data=os.read(self.stream.fileno(),4096);assert data,'Unexpected EOF';self.tail+=data
   while b'\n' in self.tail:
    row,_,self.tail=self.tail.partition(b'\n');self.frames.append(json.loads(row))
  return self.frames.pop(0)
def send(proc,frame):proc.stdin.write(json.dumps(frame).encode()+b'\n');proc.stdin.flush()
try:
 with tempfile.TemporaryDirectory(prefix='elm-broker-recovery-') as tmp:
  base=Path(tmp);base.chmod(0o700)
  cases=[(p,op,status) for p,ops in [(1,['minimize','restore','activate']),(2,['maximize','restore-geometry'])] for op in ops for status in ['Committed','Refused','Unknown']]
  cases += [(p,op,mode) for p,op in [(1,'minimize'),(2,'maximize')] for mode in ['transport-failure','wrong-receipt','settlement-read-failure','full-before-submit','directory-fsync-failure']]
  for n,(p,op,mode) in enumerate(cases):
   label=f'{p}:{op}:{mode}';runtime=base/str(n);runtime.mkdir(mode=0o700)
   with Journal(runtime,'fixture','71'):pass
   config=runtime/'config.json';config.write_text(json.dumps({'runtime':str(runtime),'instance':'fixture','mode':mode}));config.chmod(0o600)
   proc=subprocess.Popen(['/usr/bin/python3','-B',str(ROOT/'qa/transport.py'),str(config)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);reader=Reader(proc.stdout)
   try:
    check('attached after journal acquisition '+label,reader.frame()['kind']=='attached')
    check('geometry negotiation '+label,reader.frame()=={'protocolVersion':3,'kind':'host-geometry-negotiate'})
    if p==2:
     send(proc,{'protocolVersion':3,'kind':'geometry-attach','geometryProtocol':1,'binding':B,'requestId':'1'});check('strict geometry attach '+label,reader.frame()['kind']=='geometry-attached')
    request=effect(p,op);send(proc,request)
    if mode in ['Committed','Refused','Unknown']:
     frame=reader.frame();check('published correlated terminal '+label,frame['kind']=='effect-outcome' and frame['effectProtocol']==p and frame['intent']==request['intent'] and frame['status']==mode)
     stored=validate(json.loads((Journal.namespace_path(runtime,'fixture','71')/'intent.json').read_text()));check('terminal durable before frontend '+label,stored['status']==mode)
     proc.stdin.close();code=proc.wait(timeout=3);check('normal EOF exit '+label,code==0)
    else:
     frames=[reader.frame()]
     if mode in ['settlement-read-failure','full-before-submit','directory-fsync-failure']:
      reason={'settlement-read-failure':'unverified','full-before-submit':'full','directory-fsync-failure':'unavailable'}[mode]
      check('typed storage failure '+label,frames[0]=={'protocolVersion':3,'kind':'host-recovery-failed','reason':reason});frames.append(reader.frame())
     check('no invented receipt on failure '+label,frames[-1]=={'protocolVersion':3,'kind':'host-disconnected'} and all(f['kind']!='effect-outcome' for f in frames))
     code=proc.wait(timeout=3);check('recorded failure exit '+label,code==1)
     if mode not in ['full-before-submit','directory-fsync-failure']:
      stored=json.loads((Journal.namespace_path(runtime,'fixture','71')/'intent.json').read_text());check('failed terminal remains Pending '+label,stored['status']=='Pending')
    submitted=runtime/'submitted.jsonl';rows=[json.loads(s) for s in submitted.read_text().splitlines()] if submitted.exists() else []
    check('one submit or pre-submit refusal '+label,len(rows)==(0 if mode in ['full-before-submit','directory-fsync-failure'] else 1))
    check('actual durable Pending at submit '+label,all(r['durableBeforeSubmit']['status']=='Pending' and r['request']==request for r in rows))
    report['runs'].append({'case':label,'exitCode':code,'submitted':len(rows),'stderr':proc.stderr.read().decode()})
   finally:
    if proc.poll() is None:proc.kill();proc.wait(timeout=3)
    for stream in [proc.stdin,proc.stdout,proc.stderr]:stream.close()
  # Persisted geometry admission is informational at startup, not a retry queue.
  runtime=base/'uncertain';runtime.mkdir(mode=0o700);request=effect(2,'maximize')
  with Journal(runtime,'fixture','71') as journal:journal.begin(B,request['intent'],2)
  config=runtime/'config.json';config.write_text(json.dumps({'runtime':str(runtime),'instance':'fixture','mode':'Committed'}));config.chmod(0o600)
  proc=subprocess.Popen(['/usr/bin/python3','-B',str(ROOT/'qa/transport.py'),str(config)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  try:
   reader=Reader(proc.stdout);check('new broker attached',reader.frame()['kind']=='attached')
   check('geometry Unknown informational startup',reader.frame()=={'protocolVersion':3,'kind':'host-uncertain','effectProtocol':2,'binding':B,'intent':request['intent']})
   check('negotiation after uncertainty',reader.frame()['kind']=='host-geometry-negotiate');proc.stdin.close();check('recovery broker normal EOF',proc.wait(timeout=3)==0)
   check('startup never replays native effect',not (runtime/'submitted.jsonl').exists())
  finally:
   if proc.poll() is None:proc.kill();proc.wait(timeout=3)
   for stream in [proc.stdin,proc.stdout,proc.stderr]:stream.close()
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
