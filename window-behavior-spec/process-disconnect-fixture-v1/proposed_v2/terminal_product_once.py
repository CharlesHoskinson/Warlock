"""One unchanged fast readonly product helper attempt; reviewed inert server.
No GUI, native pin effect, helper sleep, retry or replaced product entry.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,select,subprocess,sys,time,stat
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
P=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def persist(directory,name,value):
 raw=(json.dumps(value,indent=2)+'\n').encode();directoryFD=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  before=os.fstat(directoryFD);named=os.lstat(directory);assert before.st_dev==named.st_dev and before.st_ino==named.st_ino and before.st_mode==named.st_mode and before.st_uid==os.getuid() and before.st_mode&0o7777==0o700
  fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directoryFD)
  try:
   position=0
   while position<len(raw):
    count=os.write(fd,raw[position:]);assert count>0;position+=count
   opened=os.fstat(fd);assert stat.S_ISREG(opened.st_mode) and opened.st_uid==os.getuid() and opened.st_mode&0o7777==0o600 and opened.st_size==len(raw);os.fsync(fd)
  finally:os.close(fd)
  os.fsync(directoryFD);after=os.lstat(directory);assert (after.st_dev,after.st_ino,after.st_mode,after.st_uid)==(before.st_dev,before.st_ino,before.st_mode,before.st_uid)
 finally:os.close(directoryFD)
def main():
 require_qa_scope();build=json.loads((B/'terminal-module-build-v1.json').read_text());assert build['result']=='pass';assert all(sha(p)==h for p,h in build['sources'].items());binary=B/('cpu-terminal-disconnect'if sys.argv[1]=='fault-after-disconnect-source-boundary'else'cpu-terminal-product');assert sha(binary)==build['outputs'][str(binary)]
 loader=importlib.util.spec_from_file_location('reviewed_capture_cpu',P/'test_capture.py');tests=importlib.util.module_from_spec(loader);loader.loader.exec_module(tests);case=tests.CaptureTests('test_actual_capture_direct_shebang_exact_token_and_no_writes');actor=None;path=None;evidence=B/"terminal-disconnect-evidence"/str(time.time_ns());evidence.mkdir(parents=True,mode=0o700);evidence.chmod(0o700)
 row={'GUI':False,'nativePinEffectAccepted':False,'actualQSProcessAccepted':False,'helperWaitSleepOrRetryAdded':False,'originalHelperTransactionSeconds':2,'fixtureSource':str(P/'test_capture.py'),'fixtureSourceSHA256':sha(P/'test_capture.py')}
 try:
  _,env,token,config,path,reply=case.fixture();entry=path.with_name('pin_capture.py');entry.write_bytes((P/'pin_capture.py').read_bytes());entry.chmod(0o700);assert entry.read_bytes()==(P/'pin_capture.py').read_bytes();config['captureEntry']={'path':str(entry),'sha256':sha(entry)};public={k:token[k]for k in ['address','stableId','pid']};reply.write_text(json.dumps(token));publicJSON=json.dumps(public)
  argv=[str(binary)];actor=subprocess.Popen(argv,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);assert select.select([actor.stdout],[],[],3)[0],'Actual CPU requester did not register within fixture setup budget';ready=json.loads(actor.stdout.readline());assert ready['requesterPID']==actor.pid;requester=case.source(actor.pid,'harness');actualEnv=dict(x.split(b'=',1)for x in(Path('/proc')/str(actor.pid)/'environ').read_bytes().split(b'\0')if b'='in x);requester['environment']={'PATH':actualEnv[b'PATH'].decode()};config['requestRoots']=[requester];path.write_text(json.dumps(config));path.chmod(0o600)
  actualRequester=case.source(actor.pid,'harness');actualRequester['environment']={'PATH':dict(x.split(b'=',1)for x in(Path('/proc')/str(actor.pid)/'environ').read_bytes().split(b'\0')if b'='in x)[b'PATH'].decode()};assert actualRequester==config['requestRoots'][0];row.update(command=argv,config=config,configSHA256=sha(path),actualRequester=actualRequester,helperSource=str(P/'pin_capture.py'),helperSourceSHA256=sha(P/'pin_capture.py'),exactHelperCommand=[str(entry),'capture',publicJSON],evidenceDirectory=str(evidence));persist(evidence,"launch-before-communicate.json",row);before=time.monotonic();out,err=actor.communicate(json.dumps(dict(configPath=str(path),manifestPath='/home/hoskinson/window-behavior-spec/qml-object-lifetime-v5-popup/source-ready-inputs.json',publicJSON=publicJSON,registryCase=sys.argv[1],beforeHookEvidencePath=str(evidence/"before-hook.json")))+'\n',timeout=8);elapsed=time.monotonic()-before
  row.update(result='pass'if actor.returncode==0 else'fail',command=argv,exitCode=actor.returncode,stdout=out,stderr=err,elapsedSeconds=elapsed,helperSource=str(P/'pin_capture.py'),helperSourceSHA256=sha(P/'pin_capture.py'),entryCopySHA256=sha(entry),exactHelperCommand=[str(entry),'capture',publicJSON],selectedEnvironment=env,actualRequester=actualRequester,config=config,configSHA256=sha(path),receivedRequest=(Path(str(reply)+'.request').read_text()if Path(str(reply)+'.request').exists()else None),buildPath=str(B/'terminal-module-build-v1.json'),buildSHA256=sha(B/'terminal-module-build-v1.json'),sourcesUnchanged=all(sha(p)==h for p,h in build['sources'].items()))
  row['durableReceipts']={p.name:json.loads(p.read_text())for p in Path(config['evidenceDirectory']).glob('*.json')}
 except BaseException as e:
  row.update(result='fail',error=repr(e))
  if isinstance(e,subprocess.TimeoutExpired):
   row['partialStdout']=(e.stdout or b'').decode(errors='replace')if isinstance(e.stdout,bytes)else(e.stdout or '')
   row['partialStderr']=(e.stderr or b'').decode(errors='replace')if isinstance(e.stderr,bytes)else(e.stderr or '')
  if 'config'in row:
   row['durableReceiptsBeforeCleanup']={p.name:json.loads(p.read_text())for p in Path(config['evidenceDirectory']).glob('*.json')}
  # Persist all available observations before cleanup/finalization on failure.
  if(evidence/'before-hook.json').exists():row['durableBeforeHookRaw']=(evidence/'before-hook.json').read_text()
  persist(evidence,"failure-before-cleanup.json",row)
 finally:
  if actor and actor.poll()is None:
   if actor.stdin:
    try:actor.stdin.close()
    except (OSError,ValueError):pass
   try:actor.wait(timeout=5)
   except subprocess.TimeoutExpired:
    row.update(result='fail',diagnosticActorStillLive=True,normalFixtureCleanup=False,retainedPrivateRuntime=str(path.parent)if path else None,actorPID=actor.pid)
    own=Path('/proc')/str(actor.pid)
    row['ownedActorReadOnlyEvidence']={}
    for name in ['stat','status','wchan','cgroup']:
     try:row['ownedActorReadOnlyEvidence'][name]=(own/name).read_text()[:65536]
     except OSError as e:row['ownedActorReadOnlyEvidence'][name]={'error':repr(e)}
  if not actor or actor.poll()is not None:
   row['normalFixtureCleanup']=case.doCleanups()
   if not row['normalFixtureCleanup']:row['result']='fail'
 if(evidence/'before-hook.json').exists():row['durableBeforeHookRaw']=(evidence/'before-hook.json').read_text()
 row['normalCPUPrivateRuntimeRemoved']=path is not None and not path.parent.exists();report=B/f'terminal-registry-{sys.argv[1]}-{time.time_ns()}.json';report.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(report),exitCode=row.get('exitCode'))));return int(row['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
