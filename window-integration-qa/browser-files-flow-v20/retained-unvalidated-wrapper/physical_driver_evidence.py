"""Owned physical fixture driver observations; neither focus nor DOM writes."""
import json,subprocess,time
from pathlib import Path
from private_desktop import PrivateDesktop
from process_evidence import snapshot

def matched_owner(state,expected):
 return all(state.get(k)is True for k in ('keyboardSurfacePresent','keyboardResourcePresent')) and all(isinstance(state.get(route),dict)and all(type(state[route].get(k))is type(v)and state[route][k]==v for k,v in expected.items())for route in ('keyboardOwner','coreNativeFocus'))

class PhysicalDriverEvidence:
 def __init__(self,path,obs,native,pid,start,identity,guard):
  self.path=Path(path);self.obs=obs;self.native=native;self.pid=pid;self.start=start;self.identity=dict(identity);self.guard=guard
  self.selectors={k:obs.environment.get(k)for k in ('XDG_RUNTIME_DIR','WAYLAND_DISPLAY','HYPRLAND_INSTANCE_SIGNATURE')}
  self.proof={'scope':'Bounded private driver before/after observed Seat/core owner and owned Browser lifetime; not continuous input delivery or original feature acceptance','originalFeatureAcceptance':False,'expectedBrowserIdentity':self.identity,'browserPID':pid,'browserStart':start,'selectors':self.selectors,'commands':[]};self.persist()
 def persist(self):PrivateDesktop.private_json(self.path,self.proof)
 def owner(self,row):
  self.guard()
  try:
   row['monotonicNs']=time.monotonic_ns();row['startBefore']=self.obs.start(self.pid);row['selectorsBefore']={k:self.obs.environment.get(k)for k in self.selectors};self.persist()
   row['clients']=self.obs.data('clients');self.persist();row['native']=self.native();self.persist()
   row['seatKeyboardRaw']=self.obs.run('hyprctl','repl','print(hl.plugin.qt_modal_probe.keyboard_state())');self.persist()
   row['seatKeyboard']=json.loads(row['seatKeyboardRaw']);self.persist()
   row['startAfter']=self.obs.start(self.pid);row['selectorsAfter']={k:self.obs.environment.get(k)for k in self.selectors};self.persist();self.guard()
   peers=[p for p in row['clients']if p.get('pid')==self.pid]
   row['accepted']=(row['startBefore']==row['startAfter']==self.start and row['selectorsBefore']==row['selectorsAfter']==self.selectors and len(peers)==1 and all(type(peers[0].get(k))is type(v)and peers[0][k]==v for k,v in self.identity.items())and matched_owner(row['seatKeyboard'],self.identity));self.persist()
   if not row['accepted']:raise AssertionError('Exact observed Browser Seat/core/public lifetime required before/after driver')
  except BaseException as error:
   row['accepted']=False;row['error']={'type':type(error).__name__,'error':str(error)};self.persist();raise
 def run(self,command,env,timeout,delegate=None):
  row={'command':list(command),'timeoutSeconds':timeout,'before':{},'after':{},'stdout':None,'stderr':None,'returncode':None};self.proof['commands'].append(row);self.persist();self.owner(row['before'])
  try:
   if delegate is not None:
    assert timeout==12;result=delegate(command,env)
   else:
    with subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)as p:
     row['pid']=p.pid;self.persist()
     try:
      identity={'pid':p.pid,'start':PrivateDesktop.start(p.pid)};row['identity']=identity;self.persist()
      def same(r):
       try:return PrivateDesktop.start(r['pid'])==r['start']
       except OSError:return False
      row['actualOwnedProcess']=snapshot(identity,same);self.persist()
     except OSError as error:row['processObservationError']={'type':type(error).__name__,'error':str(error)};self.persist()
     try:stdout,stderr=p.communicate(timeout=timeout)
     except subprocess.TimeoutExpired:
      row['timeout']=True;row['forcedTimeoutCleanup']=True;self.persist();p.kill();p.communicate();raise
     except BaseException:p.kill();raise
     result=subprocess.CompletedProcess(command,p.returncode,stdout,stderr);row['pidPathAbsentAfterWait']=not Path(f'/proc/{p.pid}').exists();self.persist()
   row.update(stdout=result.stdout,stderr=result.stderr,returncode=result.returncode,normalExit=result.returncode==0);self.persist();self.owner(row['after'])
   if result.returncode!=0:raise AssertionError('Private physical driver failed; no retry')
   return result
  except BaseException as error:
   row['error']={'type':type(error).__name__,'error':str(error)};self.persist();raise
