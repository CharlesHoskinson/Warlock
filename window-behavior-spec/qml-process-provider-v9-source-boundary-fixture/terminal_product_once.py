"""One unchanged fast readonly product helper attempt; reviewed inert server.
No GUI, native pin effect, helper sleep, retry or replaced product entry.
"""
from pathlib import Path
import base64,hashlib,importlib.util,json,os,select,subprocess,sys,time,stat
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
def capture_raw_file(path,cap=1048576):
 # Diagnostic bytes are bounded and never provide acceptance authority.
 row={'path':str(path),'maximumBytes':cap};fd=None;raw=bytearray()
 try:
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC);before=os.fstat(fd)
  row['statBefore']={'device':before.st_dev,'inode':before.st_ino,'mode':before.st_mode,'uid':before.st_uid,'size':before.st_size}
  if not stat.S_ISREG(before.st_mode):raise ValueError('Receipt is not regular')
  raw=bytearray()
  while len(raw)<cap+1:
   part=os.read(fd,min(65536,cap+1-len(raw)))
   if not part:break
   raw.extend(part)
  truncated=len(raw)>cap;raw=bytes(raw[:cap]);row.update(rawBase64=base64.b64encode(raw).decode('ascii'),rawSHA256=hashlib.sha256(raw).hexdigest(),capturedBytes=len(raw),truncated=truncated)
  after=os.fstat(fd);row['statAfter']={'device':after.st_dev,'inode':after.st_ino,'mode':after.st_mode,'uid':after.st_uid,'size':after.st_size}
  row['stableMetadata']=(before.st_dev,before.st_ino,before.st_mode,before.st_uid,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_mode,after.st_uid,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
  if truncated:row['parseError']='Bounded diagnostic byte limit exceeded'
  else:
   try:row['parsed']=json.loads(raw)
   except (ValueError,UnicodeError)as error:row['parseError']=repr(error)
 except Exception as error:
  row['readError']=repr(error)
  captured=bytes(raw[:cap]);row.update(rawBase64=base64.b64encode(captured).decode('ascii'),rawSHA256=hashlib.sha256(captured).hexdigest(),capturedBytes=len(captured),truncated=len(raw)>cap)
 finally:
  if fd is not None:
   try:os.close(fd)
   except OSError as error:row['closeError']=repr(error)
 return row
def capture_receipts(directory):
 row={'directory':str(directory),'maximumEntries':8,'files':{}}
 try:
  paths=[]
  with os.scandir(directory)as entries:
   for entry in entries:
    if entry.name.endswith('.json'):
     paths.append(Path(directory)/entry.name)
     if len(paths)==9:break
  row['observedEntryCountLowerBound']=len(paths);row['entryLimitExceeded']=len(paths)>8
  for path in sorted(paths)[:8]:row['files'][path.name]=capture_raw_file(path)
 except Exception as error:row['enumerationError']=repr(error)
 return row
def main():
 require_qa_scope();build=json.loads((B/'terminal-module-build-v1.json').read_text());assert build['result']=='pass';assert all(sha(p)==h for p,h in build['sources'].items());binary=B/('cpu-terminal-disconnect'if sys.argv[1]=='fault-after-disconnect-source-boundary'else'cpu-terminal-product');assert sha(binary)==build['outputs'][str(binary)]
 loader=importlib.util.spec_from_file_location('reviewed_capture_cpu',P/'test_capture.py');tests=importlib.util.module_from_spec(loader);loader.loader.exec_module(tests);case=tests.CaptureTests('test_actual_capture_direct_shebang_exact_token_and_no_writes');actor=None;path=None;evidence=B/"terminal-disconnect-evidence"/str(time.time_ns());evidence.mkdir(parents=True,mode=0o700);evidence.chmod(0o700)
 row={'GUI':False,'nativePinEffectAccepted':False,'actualQSProcessAccepted':False,'helperWaitSleepOrRetryAdded':False,'originalHelperTransactionSeconds':2,'fixtureSource':str(P/'test_capture.py'),'fixtureSourceSHA256':sha(P/'test_capture.py')}
 try:
  _,env,token,config,path,reply=case.fixture();entry=path.with_name('pin_capture.py');entry.write_bytes((P/'pin_capture.py').read_bytes());entry.chmod(0o700);assert entry.read_bytes()==(P/'pin_capture.py').read_bytes();config['captureEntry']={'path':str(entry),'sha256':sha(entry)};public={k:token[k]for k in ['address','stableId','pid']};reply.write_text(json.dumps(token));publicJSON=json.dumps(public)
  argv=[str(binary)];actor=subprocess.Popen(argv,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);assert select.select([actor.stdout],[],[],3)[0],'Actual CPU requester did not register within fixture setup budget';ready=json.loads(actor.stdout.readline());assert ready['requesterPID']==actor.pid;requester=case.source(actor.pid,'harness');actualEnv=dict(x.split(b'=',1)for x in(Path('/proc')/str(actor.pid)/'environ').read_bytes().split(b'\0')if b'='in x);requester['environment']={'PATH':actualEnv[b'PATH'].decode()};config['requestRoots']=[requester];path.write_text(json.dumps(config));path.chmod(0o600)
  actualRequester=case.source(actor.pid,'harness');actualRequester['environment']={'PATH':dict(x.split(b'=',1)for x in(Path('/proc')/str(actor.pid)/'environ').read_bytes().split(b'\0')if b'='in x)[b'PATH'].decode()};assert actualRequester==config['requestRoots'][0];row.update(command=argv,config=config,configSHA256=sha(path),actualRequester=actualRequester,helperSource=str(P/'pin_capture.py'),helperSourceSHA256=sha(P/'pin_capture.py'),exactHelperCommand=[str(entry),'capture',publicJSON],evidenceDirectory=str(evidence));persist(evidence,"launch-before-communicate.json",row);before=time.monotonic();out,err=actor.communicate(json.dumps(dict(configPath=str(path),manifestPath='/home/hoskinson/window-behavior-spec/qml-object-lifetime-v5-popup/source-ready-inputs.json',publicJSON=publicJSON,registryCase=sys.argv[1],beforeHookEvidencePath=str(evidence/"before-hook.json")))+'\n',timeout=8);elapsed=time.monotonic()-before
  row.update(result='pass'if actor.returncode==0 else'fail',command=argv,exitCode=actor.returncode,stdout=out,stderr=err,elapsedSeconds=elapsed,helperSource=str(P/'pin_capture.py'),helperSourceSHA256=sha(P/'pin_capture.py'),entryCopySHA256=sha(entry),exactHelperCommand=[str(entry),'capture',publicJSON],selectedEnvironment=env,actualRequester=actualRequester,config=config,configSHA256=sha(path),receivedRequest=(Path(str(reply)+'.request').read_text()if Path(str(reply)+'.request').exists()else None),buildPath=str(B/'terminal-module-build-v1.json'),buildSHA256=sha(B/'terminal-module-build-v1.json'),sourcesUnchanged=all(sha(p)==h for p,h in build['sources'].items()))
  row['durableReceipts']=capture_receipts(config['evidenceDirectory'])
 except BaseException as e:
  row.update(result='fail',error=repr(e))
  if isinstance(e,subprocess.TimeoutExpired):
   row['partialStdout']=(e.stdout or b'').decode(errors='replace')if isinstance(e.stdout,bytes)else(e.stdout or '')
   row['partialStderr']=(e.stderr or b'').decode(errors='replace')if isinstance(e.stderr,bytes)else(e.stderr or '')
  if 'config'in row:
   row['durableReceiptsBeforeCleanup']=capture_receipts(config['evidenceDirectory'])
  # Persist all available observations before cleanup/finalization on failure.
  row['durableBeforeHookEvidence']=capture_raw_file(evidence/'before-hook.json')
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
 row['durableBeforeHookEvidence']=capture_raw_file(evidence/'before-hook.json')
 row['normalCPUPrivateRuntimeRemoved']=path is not None and not path.parent.exists();report=evidence/f'terminal-registry-{sys.argv[1]}-{time.time_ns()}.json';persist(evidence,report.name,row);print(json.dumps(dict(result=row['result'],report=str(report),exitCode=row.get('exitCode'))));return int(row['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
