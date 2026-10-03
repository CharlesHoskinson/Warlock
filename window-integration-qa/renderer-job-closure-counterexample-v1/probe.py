from pathlib import Path
import hashlib,json,os,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v23');sys.path.insert(0,str(B))
from test_batch_preview import BatchTests
from owned_commands import SealedFile
from pipe_transport import PipeTransport
from recovery_resources import verify_process,checked_renderer,process_start
OUT=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();fixture=BatchTests();fixture.setUp();transport=None;failures=[];row=None
try:
 with SealedFile(OUT/'cpu_renderer')as executable:
  transport=PipeTransport('/proc/self/fd/'+str(executable.fd),env=fixture.env,failure=failures.append,pass_fds=(executable.fd,),keeper=fixture.keeper,actor=fixture.commands.actor)
 end=time.monotonic()+2
 while not transport.outputs()and time.monotonic()<end:time.sleep(.002)
 assert transport.outputs()and not failures
 launch=transport.owned_launch;job=fixture.keeper.jobs[launch.job];checked_renderer(launch.ownership);phase=verify_process(launch.ownership);assert phase=='executed'
 fixture.stage([(20,20,2,2,True,1),(20,20,2,2,True,1),(20,20,2,2,True,1)])
 closed=fixture.batch._closed();error=None
 try:fixture.finish()
 except BaseException as failure:error=dict(type=type(failure).__name__,message=str(failure))
 assert error==dict(type='ValueError',message='outstanding actor helper prevents thumbnail launch')
 row=dict(result='counterexample reproduced',scope=scope,sourceSHA256={n:sha(B/n)for n in ('batch_preview.py','helper_supervisor.py','owned_launch.py','pipe_transport.py','owned_commands.py')},producerSHA256=sha(OUT/'cpu_renderer'),producerSourceSHA256=sha(OUT/'cpu_renderer.c'),observation=dict(threeActualOwnedPNGStages=len(fixture.batch.pending),batchClosed=False,error=error,genuineRenderer=job,actualPipeTransportType=type(transport).__name__,actualOwnedLaunchType=type(launch).__name__,keeperVerified=True,actualOwnedProcessVerified=phase,rendererLeaderAlive=transport.process.poll()is None,registeredPopenIsActual=fixture.keeper.children[launch.job]is transport.process,ownedLaunchJobMatches=True,thumbnailHelperExecuted=False),nativeLaunch=False,scopeLimit='Real sealed nongraphical C protocol process via genuine PipeTransport/OwnedLaunch/Keeper; frozen V23 batch refuses actual persistent renderer. No compositor/client/native GUI or native timing claim.')
 pid=transport.process.pid;start=launch.ownership['start'];code=transport.close();assert code==0 and not failures and not fixture.keeper.jobs
 fixture.keeper.stop();row['cleanup']=dict(rendererExitCode=code,rendererLifetimeGone=process_start(pid)!=start,keeperExitCode=fixture.keeper.process.returncode,allJobsNormallyCompleted=True,allTransportThreadsTerminal=all(not t.is_alive()for t in transport.threads))
finally:
 if transport is not None and not transport.closed:transport.close()
 fixture.tearDown()
with os.fdopen(os.open(OUT/'counterexample.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in row.items()if k!='observation'}))
