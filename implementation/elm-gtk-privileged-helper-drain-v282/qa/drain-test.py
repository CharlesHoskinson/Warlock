"""Real process/wait drain with explicitly injected credential/signal-policy branches."""
import hashlib,json,os,resource,shutil,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;out=ROOT/('drain-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'credentialPolicyInjected':True,'checks':[]};runtime=private_runtime()
try:
 for mode in ['privileged-wait','privileged-timeout','repeated-signal-error']:
  case=out/mode;case.mkdir();marker=case/'helper.pid';journal=case/'journal.jsonl'
  code='import os,time\np=os.fork()\nif p==0:\n open('+repr(str(marker))+',"w").write(str(os.getpid()))\n time.sleep('+('4' if mode=='privileged-timeout' else '1')+')\n os._exit(0)\ntime.sleep(30)\n'
  descriptor=runtime/(mode+'.json');descriptor.write_text(json.dumps({'argv':[sys.executable,'-c',code],'binarySHA256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()}))
  worker=case/'worker.py';worker.write_text('''import importlib.util,sys
from pathlib import Path
sys.path.insert(0,'''+repr(str(ROOT))+''')
spec=importlib.util.spec_from_file_location('actual_supervisor','''+repr(str(ROOT/'activation-supervisor.py'))+''');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=m.signal_exact
marker=Path('''+repr(str(marker))+''')
def injected(row,sig):
 if marker.exists() and row['pid']==int(marker.read_text()):
  if '''+repr(mode)+'''=='repeated-signal-error':raise RuntimeError('injected repeated signal acquisition failure')
  current=m.identity(row['pid']);current.update(effectiveUid=0,savedUid=0,filesystemUid=0,privilegedCredentials=True)
  raise m.PrivilegedSignalRefused(current)
 return original(row,sig)
m.signal_exact=injected
sys.argv=['actual_supervisor','''+repr(str(descriptor))+','+repr(str(journal))+''']
sys.exit(m.main())
''')
  with (case/'stdout').open('wb') as stdout,(case/'stderr').open('wb') as stderr:
   proc=subprocess.Popen([sys.executable,'-B',str(worker)],env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime)),stdout=stdout,stderr=stderr,start_new_session=True)
   try:
    ready=time.monotonic()+1
    while True:
     rows=[json.loads(x) for x in journal.read_text().split('\n') if x] if journal.exists() else []
     if len([r for r in rows if r['kind']=='owned-child'])==2:break
     assert time.monotonic()<ready and proc.poll() is None;time.sleep(.005)
    began=time.monotonic();proc.send_signal(signal.SIGTERM);assert proc.wait(timeout=3)==2;elapsed=time.monotonic()-began;assert elapsed<3
   finally:
    if proc.poll() is None:proc.kill();proc.wait(timeout=1)
  rows=[json.loads(x) for x in journal.read_text().split('\n') if x];terminal=rows[-1];assert terminal['kind']=='terminal'
  if mode=='privileged-timeout':
   assert terminal['error'] is not None and terminal['fallback'] is False and len(terminal['liveDescendants'])==1 and len(terminal['allWaitStatuses'])==1
   helper=int(marker.read_text());assert terminal['liveDescendants'][0]['pid']==helper
   from credentials import identity,signal_exact
   real=identity(helper);signal_exact(real,signal.SIGTERM) # External control cleanup; production never signalled helper.
   assert not any(r['kind']=='signal' and r['identity']['pid']==helper for r in rows)
   report['checks'].append({'name':mode,'passed':True,'elapsed':elapsed,'positiveCleanup':False,'helperSignalledBySupervisor':False,'externalControlCleanup':'actual unprivileged owned toy SIGTERM','terminal':terminal});continue
  assert terminal['liveDescendants']==[] and len(terminal['allWaitStatuses'])==2
  helper=int(marker.read_text());helper_exit=next(r for r in rows if r['kind']=='child-exit' and r['identity']['pid']==helper);assert helper_exit['exitCode']==0
  assert not any(r['kind']=='signal' and r['identity']['pid']==helper for r in rows)
  if mode=='privileged-wait':
   assert terminal['error'] is None and terminal['fallback'] is False and terminal['cancelled'] is True
   refused=[r for r in rows if r['kind']=='signal-identity-refused'];assert refused and all(r['observedIdentity']['effectiveUid']==0 and r['metadata']['pid']==helper for r in refused)
  else:assert terminal['error'] is not None and any(r['kind']=='supervisor-failure' for r in rows)
  report['checks'].append({'name':mode,'passed':True,'elapsed':elapsed,'actualHelperExitCode':0,'helperSignalled':False,'terminal':terminal})
 report['passed']=True
finally:
 shutil.rmtree(runtime);report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'activation-supervisor.py',ROOT/'credentials.py']};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
