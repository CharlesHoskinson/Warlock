from pathlib import Path
import sys,tempfile,time,json,traceback,hashlib
BASE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-recovery-v15-frozen-v2')
sys.path.insert(0,str(BASE))
from test_recovery_runtime import RecoveryTests
from owned_commands import SealedFile
from recovery_resources import gated_process,retire_renderer,checked_renderer
from recovery_runtime import NativeRecovery
from service_runtime import RuntimeLease
result={'nativeLaunch':False,'mainChanged':False,'actualCpuElfOnly':True,'scope':'legacy gated renderer ownership accepted by current preflight; registered modern keeper case refused correctly'}
with tempfile.TemporaryDirectory() as raw:
 f,s,d,a,b=RecoveryTests().fixture(raw);owners=[]
 with SealedFile('/usr/bin/true') as selected:
  child=gated_process('/proc/self/fd/'+str(selected.fd),env=f.guard.env,pass_fds=(selected.fd,),record=owners.append)
 deadline=time.monotonic()+3
 while time.monotonic()<deadline:
  state=Path('/proc/'+str(child.pid)+'/stat').read_text().rsplit(') ',1)[1].split()[0]
  if state=='Z':break
  time.sleep(.002)
 else:raise RuntimeError('actual owned CPU child must become Z')
 owned=checked_renderer(owners[0]);f.producer_hash=owned['producer']['sha256'];b['actorResources'][0].update(phase='launched',renderer=owned);s.write(b)
 d.windows.pop(0);d.family=lambda w,windows,single=False:(windows,windows[-1])
 lease=RuntimeLease(f.root,'offline')
 try:
  coordinator=NativeRecovery(f,store=s,desktop=d,lease_verify=lease.verify);coordinator.preflight(b);result['exactCurrentPreflightAccepted']=True
  result.update(pid=child.pid,start=owned['start'],actualState=state,inheritedRetire=retire_renderer(owned,expected_environment=owned['environment']))
  try:coordinator.recover(b);result['accepted']=True
  except Exception as error:result.update(error=str(error),exceptionType=type(error).__name__,traceback=traceback.format_exc())
  result.update(captureDirectoryRetained=a.exists(),journal=s.read(),nativeWrites=d.commits)
 finally:
  lease.close();child.wait(timeout=3)
  for stream in (child.stdin,child.stdout,child.stderr):stream.close()
result['frozenManifestSHA256']=hashlib.sha256((BASE/'manifest-recovery-v15.json').read_bytes()).hexdigest()
Path(__file__).with_name('legacy-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result.get(k) for k in ('actualState','exactCurrentPreflightAccepted','inheritedRetire','error','captureDirectoryRetained','nativeWrites')}))
