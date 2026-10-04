"""Actual CPU process tree/wait-status tests. No private compositor or portals."""
import hashlib,json,os,resource,shutil,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;OUT=ROOT/('activation-'+str(time.time_ns()));OUT.mkdir();runtime=private_runtime();checks=[];report={'passed':False,'nativeAcceptance':False,'actualCPUProcessesOnly':True,'checks':checks}
try:
 cases=[('normal','import time;time.sleep(.1)',False,0),('nonzero','import time;time.sleep(.1);raise SystemExit(7)',False,7),('term','import time;time.sleep(30)',True,-15),('kill','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)',True,-9),('orphan','import subprocess,sys,time;subprocess.Popen([sys.executable,"-c","import time;time.sleep(.2)"]);time.sleep(.05)',False,0),('setsid','import subprocess,sys,time;subprocess.Popen([sys.executable,"-c","import os,time;os.setsid();time.sleep(.2)"]);time.sleep(.05)',False,0),('latefork','import signal,subprocess,sys,time;signal.signal(signal.SIGTERM,lambda *_:subprocess.Popen([sys.executable,"-c","import os,time;os.setsid();time.sleep(30)"]));time.sleep(30)',True,-9)]
 for name,code,cancel,expected in cases:
  descriptor=runtime/(name+'.json');descriptor.write_text(json.dumps({'argv':[sys.executable,'-c',code],'binarySHA256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()}));journal=OUT/(name+'.jsonl');env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime));proc=None
  with (OUT/(name+'.stdout')).open('wb') as out,(OUT/(name+'.stderr')).open('wb') as err:
   try:
    proc=subprocess.Popen([sys.executable,'-B',str(ROOT/'activation-supervisor.py'),str(descriptor),str(journal)],env=env,stdout=out,stderr=err,start_new_session=True)
    if cancel:
     deadline=time.monotonic()+1
     while True:
      rows=[json.loads(x) for x in journal.read_text().split('\n') if x] if journal.exists() else []
      if any(r['kind']=='owned-child' for r in rows):break
      assert time.monotonic()<deadline;time.sleep(.01)
     time.sleep(.05);proc.send_signal(signal.SIGTERM)
    exitcode=proc.wait(timeout=3)
   finally:
    if proc and proc.poll() is None:proc.kill();proc.wait(timeout=1)
  rows=[json.loads(x) for x in journal.read_text().split('\n') if x];terminal=rows[-1]
  assert terminal['kind']=='terminal',name
  assert terminal['childExitCode']==expected,name
  assert terminal['cancelled'] is cancel and terminal['fallback'] is (name in ('kill','latefork')),name
  assert exitcode==(0 if name in ('normal','orphan','setsid') else 2),name
  assert [r['sequence'] for r in rows]==list(range(1,len(rows)+1)),name
  exits=[r for r in rows if r['kind']=='child-exit'];owned=[r for r in rows if r['kind']=='owned-child']
  assert {r['identity']['pid'] for r in exits}=={r['identity']['pid'] for r in owned},name
  if name in ('orphan','setsid'):assert len(exits)==2 and all(r['exitCode']==0 for r in exits)
  if name=='latefork':assert len(exits)>=2 and any(r['exitCode']==-15 for r in exits),name
  checks.append({'name':name,'passed':True,'actualWaitStatuses':terminal['allWaitStatuses'],'journal':str(journal)})
 report['passed']=True
finally:
 shutil.rmtree(runtime)
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'activation-supervisor.py',Path(sys.executable),Path('/home/hoskinson/window-integration-qa/qa_launch.py')]}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
