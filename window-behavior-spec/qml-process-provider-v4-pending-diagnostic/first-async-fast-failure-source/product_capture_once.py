"""One unchanged fast readonly product helper attempt; reviewed inert server.
No GUI, native pin effect, helper sleep, retry or replaced product entry.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,select,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
P=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3/frontend')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();build=json.loads((B/'product-capture-build.json').read_text());assert build['result']=='pass';assert all(sha(p)==h for p,h in build['sources'].items());assert sha(B/'cpu-product-capture')==build['binarySHA256']
 loader=importlib.util.spec_from_file_location('reviewed_capture_cpu',P/'test_capture.py');tests=importlib.util.module_from_spec(loader);loader.loader.exec_module(tests);case=tests.CaptureTests('test_actual_capture_direct_shebang_exact_token_and_no_writes');actor=None
 row={'GUI':False,'nativePinEffectAccepted':False,'actualQSProcessAccepted':False,'helperWaitSleepOrRetryAdded':False,'originalHelperTransactionSeconds':2,'fixtureSource':str(P/'test_capture.py'),'fixtureSourceSHA256':sha(P/'test_capture.py')}
 try:
  _,env,token,config,path,reply=case.fixture();entry=path.with_name('pin_capture.py');entry.write_bytes((P/'pin_capture.py').read_bytes());entry.chmod(0o700);assert entry.read_bytes()==(P/'pin_capture.py').read_bytes();config['captureEntry']={'path':str(entry),'sha256':sha(entry)};public={k:token[k]for k in ['address','stableId','pid']};reply.write_text(json.dumps(token));publicJSON=json.dumps(public)
  argv=[str(B/'cpu-product-capture')];actor=subprocess.Popen(argv,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);assert select.select([actor.stdout],[],[],3)[0],'Actual CPU requester did not register within fixture setup budget';ready=json.loads(actor.stdout.readline());assert ready['requesterPID']==actor.pid;requester=case.source(actor.pid,'harness');actualEnv=dict(x.split(b'=',1)for x in(Path('/proc')/str(actor.pid)/'environ').read_bytes().split(b'\0')if b'='in x);requester['environment']={'PATH':actualEnv[b'PATH'].decode()};config['requestRoots']=[requester];path.write_text(json.dumps(config));path.chmod(0o600)
  actualRequester=case.source(actor.pid,'harness');actualRequester['environment']={'PATH':dict(x.split(b'=',1)for x in(Path('/proc')/str(actor.pid)/'environ').read_bytes().split(b'\0')if b'='in x)[b'PATH'].decode()};assert actualRequester==config['requestRoots'][0];before=time.monotonic();out,err=actor.communicate(json.dumps(dict(configPath=str(path),manifestPath='/home/hoskinson/window-behavior-spec/qml-object-lifetime-v5-popup/source-ready-inputs.json',publicJSON=publicJSON))+'\n',timeout=8);elapsed=time.monotonic()-before
  row.update(result='pass'if actor.returncode==0 else'fail',command=argv,exitCode=actor.returncode,stdout=out,stderr=err,elapsedSeconds=elapsed,helperSource=str(P/'pin_capture.py'),helperSourceSHA256=sha(P/'pin_capture.py'),entryCopySHA256=sha(entry),exactHelperCommand=[str(entry),'capture',publicJSON],selectedEnvironment=env,actualRequester=actualRequester,config=config,configSHA256=sha(path),receivedRequest=(Path(str(reply)+'.request').read_text()if Path(str(reply)+'.request').exists()else None),buildPath=str(B/'product-capture-build.json'),buildSHA256=sha(B/'product-capture-build.json'),sourcesUnchanged=all(sha(p)==h for p,h in build['sources'].items()))
  row['durableReceipts']={p.name:json.loads(p.read_text())for p in Path(config['evidenceDirectory']).glob('*.json')}
 except BaseException as e:row.update(result='fail',error=repr(e))
 finally:
  if actor and actor.poll()is None:
   # The ordinary fixture's stdin EOF and original requester timer provide
   # normal shutdown; no force cleanup or retry.
   if actor.stdin:actor.stdin.close()
   actor.wait(timeout=5)
  row['normalFixtureCleanup']=case.doCleanups()
  if not row['normalFixtureCleanup']:row['result']='fail'
 row['normalCPUPrivateRuntimeRemoved']=not path.parent.exists();report=B/f'product-capture-runtime-{time.time_ns()}.json';report.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(report),exitCode=row.get('exitCode'))));return int(row['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
