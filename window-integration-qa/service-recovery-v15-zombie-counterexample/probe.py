from pathlib import Path
import sys,tempfile,time,json,traceback,hashlib,os
BASE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-recovery-v15-frozen-v2')
sys.path.insert(0,str(BASE))
from test_recovery_runtime import RecoveryTests
from helper_supervisor import Keeper
from owned_commands import SealedFile
from owned_launch import OwnedLaunch
from recovery_runtime import NativeRecovery
from recovery_resources import retire_renderer
from service_runtime import RuntimeLease
result={'nativeLaunch':False,'mainChanged':False,'actualCpuElfOnly':True}
with tempfile.TemporaryDirectory() as raw:
 factory,store,d,actor,body=RecoveryTests().fixture(raw)
 keeper=Keeper(factory.root,factory.guard.env,lambda value:None)
 with SealedFile('/usr/bin/true') as selected:
  launch=OwnedLaunch(['/proc/self/fd/'+str(selected.fd)],env=factory.guard.env,keeper=keeper,kind='renderer',actor=1,executable_fd=selected.fd)
 deadline=time.monotonic()+3
 while time.monotonic()<deadline:
  state=Path('/proc/'+str(launch.process.pid)+'/stat').read_text().rsplit(') ',1)[1].split()[0]
  if state=='Z':break
  time.sleep(.002)
 else:raise RuntimeError('actual owned ELF must be zombie before probe')
 job=next(iter(keeper.jobs));ownership=keeper.jobs[job]['ownership']
 keeper.complete(job);keeper.stop()
 factory.producer_hash=ownership['producer']['sha256']
 body['helperOwnership']=keeper.snapshot();body['actorResources'][0].update(phase='launched',renderer=ownership)
 store.write(body);d.windows.pop(0)
 d.family=lambda w,windows,single=False:([row for row in windows if row.get('mapped',True)],windows[-1])
 lease=RuntimeLease(factory.root,'offline')
 try:
  result.update(pid=launch.process.pid,start=ownership['start'],actualState=state,inheritedRetire=retire_renderer(ownership,expected_environment=ownership['environment']))
  try:NativeRecovery(factory,store=store,desktop=d,lease_verify=lease.verify).recover(body);result['unexpectedAccepted']=True
  except Exception as error:result.update(error=str(error),exceptionType=type(error).__name__,traceback=traceback.format_exc())
  result.update(captureDirectoryRetained=actor.exists(),journal=store.read(),nativeWrites=d.commits)
 finally:lease.close();launch.process.wait(timeout=3)
result['frozenManifestSHA256']=hashlib.sha256((BASE/'manifest-recovery-v15.json').read_bytes()).hexdigest()
Path(__file__).with_name('result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result.get(k) for k in ('actualState','inheritedRetire','error','captureDirectoryRetained','nativeWrites')}))
