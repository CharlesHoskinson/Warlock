from pathlib import Path
from copy import deepcopy
import hashlib,json,os,sys,threading,time
from unittest.mock import patch
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24');sys.path.insert(0,str(B))
from test_batch_preview import BatchTests
from native_desktop import NativeDesktop
from owned_commands import SealedFile
from pipe_transport import PipeTransport
import recovery_resources
OUT=Path(__file__).resolve().parent;EXE=Path('/home/hoskinson/window-integration-qa/renderer-job-closure-counterexample-v1/cpu_renderer');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();sources={n:sha(B/n)for n in ('batch_preview.py','native_runtime.py','native_desktop.py','helper_supervisor.py','recovery_resources.py','owned_launch.py','pipe_transport.py')};cases=[]
for mutate in (False,True):
 f=BatchTests();f.setUp();transport=None;row={};events=[]
 try:
  errors=[]
  with SealedFile(EXE)as executable:transport=PipeTransport('/proc/self/fd/'+str(executable.fd),env=f.env,failure=errors.append,pass_fds=(executable.fd,),keeper=f.keeper,actor=f.commands.actor)
  deadline=time.monotonic()+2
  while not transport.outputs()and time.monotonic()<deadline:time.sleep(.002)
  assert transport.outputs()and not errors
  f.batch.bind_renderer(transport,sha(EXE));f.stage()
  actor=NativeDesktop.__new__(NativeDesktop);actor.root=f.actor;actor.capture_lock=threading.RLock();actor.preview_batch=f.batch;actor.clients=lambda:deepcopy(f.members)
  receipt=threading.RLock();f.keeper.reservation_lock=receipt
  actual=deepcopy(f.keeper.jobs[transport.owned_launch.job]);entered=threading.Event();permit=threading.Event();acquired=threading.Event();failures=[];original=recovery_resources.material_path;registered=f.keeper.jobs[transport.owned_launch.job]
  target='/proc/'+str(transport.process.pid)+'/exe';gated=[False]
  def material(path,*args,**kwargs):
   if str(path)==target and not gated[0]:
    gated[0]=True;events.append(dict(event='actualRendererMaterialReadEntered',ns=time.monotonic_ns()));entered.set()
    if not permit.wait(2):raise TimeoutError('actual adapter material gate')
   return original(path,*args,**kwargs)
  def prepare():
   try:actor.finish_capture_previews(f.sources,f.members,current=lambda:True,reservation_lock=receipt)
   except BaseException as error:failures.append(dict(type=type(error).__name__,message=str(error)))
  def separate_receipt():
   with receipt,f.keeper.lock:
    if mutate:registered['kind']='unknown'
    events.append(dict(event='independentReceiptAndKeeperAcquired',ns=time.monotonic_ns()));acquired.set()
   permit.set()
  worker=threading.Thread(target=prepare);other=threading.Thread(target=separate_receipt)
  with patch.object(recovery_resources,'material_path',material):
   worker.start();assert entered.wait(1);other.start()
   try:assert acquired.wait(.5),'actual adapter held receipt/keeper during sealed-material read'
   finally:permit.set();worker.join(3);other.join(3)
  assert not worker.is_alive()and not other.is_alive();registered['kind']='renderer'
  if mutate:
   assert failures==[dict(type='ValueError',message='outstanding actor helper prevents thumbnail launch')]
   assert not list(f.preview.glob('0x*.png')) and len(f.batch.pending)==3
  else:
   assert not failures and not f.batch.pending and len(list(f.preview.glob('0x*.png')))==6
  row=dict(binding='genuine-mutated-during-IO'if mutate else'genuine-live-positive',liveRegisteredRow=actual,receiptAndKeeperReturnedBeforeMaterialRelease=True,actualNativeDesktopAdapter=True,failure=failures,events=events,publicationPNGs={p.name:sha(p)for p in f.preview.glob('0x*.png')},rendererStillAlive=transport.process.poll()is None)
  assert transport.close()==0 and not errors and not f.keeper.jobs
  f.keeper.stop();row['cleanup']=dict(rendererExit0=True,keeperExit0=f.keeper.process.returncode==0,threadsTerminal=all(not t.is_alive()for t in transport.threads));cases.append(row)
 finally:
  if transport is not None and not transport.closed:transport.close()
  f.tearDown()
assert all(sha(B/n)==h for n,h in sources.items())
report=dict(result='pass',scope=scope,cases=cases,sourceSHA256=sources,sourceUnchanged=True,producerSHA256=sha(EXE),nativeLaunch=False,nativeAccepted=False,scopeLimit='Actual nongraphical owned process and NativeDesktop finish adapter; unchanged factory I/O under receipt is excluded; no native seeding/performance claim')
with os.fdopen(os.open(OUT/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(dict(result='pass',cases=len(cases),nativeAccepted=False)))
