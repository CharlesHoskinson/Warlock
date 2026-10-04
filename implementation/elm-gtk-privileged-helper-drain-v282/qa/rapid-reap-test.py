"""Actual rapid adopted exits; real kernel WNOWAIT identities and wait statuses."""
import hashlib,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;OUT=ROOT/('rapid-reap-'+str(time.time_ns()));OUT.mkdir();runtime=private_runtime();checks=[];report={'passed':False,'nativeAcceptance':False,'checks':checks};captured=0
try:
 for sample in range(8):
  # Own actual descendant exits before adoption; no parent wait/reaping hides status.
  code='import os\nfor i in range(16):\n p=os.fork()\n if p==0:\n  if i%2==0:os.setsid()\n  os._exit(7 if i==15 else 0)\nos._exit(0)\n'
  descriptor=runtime/(str(sample)+'.json');descriptor.write_text(json.dumps({'argv':['/usr/bin/python3','-c',code],'binarySHA256':hashlib.sha256(Path('/usr/bin/python3').read_bytes()).hexdigest()}));journal=OUT/(str(sample)+'.jsonl')
  with (OUT/(str(sample)+'.stdout')).open('wb') as out,(OUT/(str(sample)+'.stderr')).open('wb') as err:
   proc=subprocess.Popen([sys.executable,'-B',str(ROOT/'activation-supervisor.py'),str(descriptor),str(journal)],env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime)),stdout=out,stderr=err,start_new_session=True)
   try:exitcode=proc.wait(timeout=3)
   finally:
    if proc.poll() is None:proc.kill();proc.wait(timeout=1)
  rows=[json.loads(x) for x in journal.read_text().split('\n') if x];terminal=rows[-1];acquired=[r for r in rows if r['kind']=='kernel-child-acquired'];captured+=len(acquired)
  assert exitcode==0 and terminal['kind']=='terminal' and terminal['error'] is None and terminal['liveDescendants']==[]
  owned=[r['identity'] for r in rows if r['kind']=='owned-child'];exits=[r for r in rows if r['kind']=='child-exit'];assert len(owned)==len(exits)==17
  assert len({(r['pid'],r['start']) for r in owned})==17 and sorted(r['exitCode'] for r in exits)==[0]*16+[7]
  wrapper=rows[0]['identity']
  for r in acquired:assert r['identity']['ppid']==wrapper['pid'] and r['waitidCode']==os.CLD_EXITED
  checks.append({'sample':sample,'passed':True,'kernelAcquired':len(acquired),'actualExitCounts':{'zero':16,'seven':1},'journal':str(journal)})
 assert captured>0,'Actual identity-before-reap path must execute'
 report['kernelAcquiredTotal']=captured;report['passed']=True
finally:
 shutil.rmtree(runtime);report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'activation-supervisor.py',ROOT/'private_bus.py']};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
