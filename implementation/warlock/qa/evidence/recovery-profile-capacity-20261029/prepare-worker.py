#!/usr/bin/python3
"""Private Profile.prepare measurement; never activate or run either host."""
import hashlib,json,os,sys,traceback
from pathlib import Path

REPO=Path('/home/charles/Warlock');sys.path.insert(0,str(REPO/'implementation/warlock/adapter'))
recovery_path=REPO/'implementation/warlock/adapter/recovery_profile.py'
if hashlib.sha256(recovery_path.read_bytes()).hexdigest()!='ace346503b5afd2c691748e7c2e1c25394fd81cc0a90be60525ff6cd85a78142':raise RuntimeError('Recovery source changed before manager import')
import recovery_profile as recovery
if recovery.BOUND!=65536 or recovery.PROFILE_BOUND!=1048576:raise RuntimeError('Unexpected recovery metadata limits')
from taskbar_preferences import Store as Pins
from shell_preferences import Store as Settings
from shortcut_preferences import Store as Shortcuts
from motion_preferences import Store as Motion

def write(path,body):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as stream:stream.write(body);stream.flush();os.fsync(stream.fileno())
def main():
 if len(sys.argv)!=2:raise RuntimeError('exact private input required')
 packet_path=Path(sys.argv[1]);packet=json.loads(packet_path.read_bytes());run=packet_path.parent
 runtime=Path(os.environ['XDG_RUNTIME_DIR']);home=Path(os.environ['HOME']);state=Path(os.environ['XDG_STATE_HOME'])
 if not all(p.is_absolute() and p.resolve()==p and p.is_relative_to(runtime) for p in (home,state)) or os.environ.get('DBUS_SYSTEM_BUS_ADDRESS')!='unix:path='+str(runtime/'denied-system-bus') or os.environ.get('DBUS_SESSION_BUS_ADDRESS')!='unix:path='+str(runtime/'bus'):
  raise RuntimeError('profile-manager private environment mismatch')
 if os.environ.get('PULSE_SERVER')!='unix:'+str(runtime/'denied-pulse') or os.environ.get('PIPEWIRE_REMOTE')!='denied-pipewire' or os.environ.get('PIPEWIRE_RUNTIME_DIR')!=str(runtime):raise RuntimeError('audio refusal missing')
 if os.environ.get('OMARCHY_PATH')!='/usr/share/omarchy' or os.environ.get('PATH','').split(':')[0]!=str(Path(packet['guardDirectory'])):raise RuntimeError('named guard environment missing')
 result={'phase':'actual Profile.prepare only; no activation, candidate launch or rollback','nativeAcceptance':False,'offlineRecoveryObserved':False,'passed':False,'prepareInvoked':False}
 try:
  stores=[Settings(str(state)),Shortcuts(str(state)),Motion(str(state)),Pins(str(state))]
  old=stores[0].read();status,_=stores[0].save({**old,'values':{**old['values'],'theme':'dawn','effectsOff':True}});assert status=='Saved'
  old=stores[1].read();status,_=stores[1].save({**old,'choices':{'applications':'alternate','system':'keep','notifications':'keep'}});assert status=='Saved'
  status,_=stores[2].save({**stores[2].read(),'override':'reduced'});assert status=='Saved'
  status,_=stores[3].save({**stores[3].read(),'identities':['warlock-editor']});assert status=='Saved'
  directory,lock=Pins(str(state))._open()
  try:bodies={name:recovery.read_at(directory,name) for name in recovery.PREFERENCES}
  finally:os.close(lock);os.close(directory)
  for name,body in bodies.items():recovery.preference(name,body)
  predecessor=recovery.descriptor(packet['predecessor']);candidate=recovery.descriptor(packet['candidate'])
  manifest={'schema':1,'predecessor':predecessor,'candidate':candidate,'baseline':{name:recovery.digest(bodies[name]) for name in recovery.PREFERENCES}}
  encoded=recovery.encode(manifest);write(run/'actual-profile-manifest.json',encoded)
  measurement={'bytes':len(encoded),'sha256':hashlib.sha256(encoded).hexdigest(),'bound':recovery.PROFILE_BOUND,'otherMetadataBound':recovery.BOUND,'candidateFiles':len(candidate['files']),'predecessorFiles':len(predecessor['files']),'baselineHashes':manifest['baseline']}
  write(run/'actual-profile-measurement.json',(json.dumps(measurement,indent=2)+'\n').encode())
  result['measurement']=measurement;result['prepareInvoked']=True
  result['prepareResult']=recovery.Profile(Path(packet['profile'])).prepare(predecessor,candidate,str(state))
  actual=(Path(packet['profile'])/'profile.json').read_bytes()
  if actual!=encoded:raise RuntimeError('Prepared profile differs from measured coherent fixture')
  result['passed']=True
 except Exception as error:
  result['error']=repr(error);result['traceback']=traceback.format_exc()
 write(run/'prepare-result.json',(json.dumps(result,indent=2)+'\n').encode())
 print(json.dumps({'passed':result['passed'],'prepareInvoked':result['prepareInvoked'],'result':str(run/'prepare-result.json'),'measurement':str(run/'actual-profile-measurement.json')}))
 return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
