import hashlib,importlib.util,json,os,resource,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/('deadline-'+str(time.time_ns()));OUT.mkdir()
source=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'qa/captured/actor.py'
sys.path.insert(0,str(source.parent))
spec=importlib.util.spec_from_file_location('reviewed_actor',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
report={'passed':False,'nativeAcceptance':False,'source':str(source),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':[]}
try:
 for mode in ['receipt-final-persist','quit-final-persist','close-final-read','close-final-persist']:
  clock=[0.0];m.time=SimpleNamespace(monotonic=lambda:clock[0],sleep=lambda _:None)
  actor=m.Actor.__new__(m.Actor);actor.session=SimpleNamespace(guard=lambda:None);actor.number=0;actor.record={'commands':[]};actor.rows=[]
  readfd,writefd=os.pipe();pipe=os.fdopen(writefd,'wb',buffering=0);os.set_blocking(writefd,False)
  actor.process=SimpleNamespace(stdin=pipe,returncode=0,poll=lambda:None,wait=lambda timeout:0)
  actor.stdout=OUT/(mode+'.jsonl');actor.stdout.write_bytes(b'{}\n')
  def persist():
   attempts=actor.record['commands']
   if mode=='receipt-final-persist' and attempts and attempts[-1].get('requestObserved'):clock[0]=7
   if mode=='quit-final-persist' and attempts and attempts[-1].get('written'):clock[0]=7
   if mode=='close-final-persist' and actor.record.get('normalExit'):clock[0]=7
  actor.persist=persist
  def read():
   if mode.startswith('close'):
    if mode=='close-final-read':clock[0]=7
    actor.rows=[{'event':'normalexit'}]
   else:actor.rows=[{'event':'request','requestSequence':actor.number,'command':'inspect','requestedRole':None}]
   return actor.rows
  actor.read=read;actor.abort=lambda:actor.record.update(aborted=True)
  if mode.startswith('close'):actor.send=lambda operation,deadline:None
  refused=False
  try:
   if mode.startswith('close'):actor.close(6)
   else:actor.send('quit' if mode=='quit-final-persist' else 'inspect',6)
  except m.Refused:refused=True
  finally:pipe.close();os.close(readfd)
  report['cases'].append({'name':mode,'returnedAfterDeadline':not refused and clock[0]>6,'typedRefusal':refused,'elapsed':clock[0],'normalExitQualified':actor.record.get('normalExit',False),'record':actor.record})
 expected='--corrected' in sys.argv
 assert all(c['typedRefusal'] and not c['normalExitQualified'] for c in report['cases']) if expected else all(c['returnedAfterDeadline'] for c in report['cases'])
 report.update(passed=True,correctionAccepted=expected)
finally:
 report['testSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
