"""Owned continuation diagnostics. Only original wtype driver delegates input."""
from pathlib import Path
import json,subprocess,time
from private_desktop import PrivateDesktop
from process_evidence import snapshot

class ContinuationEvidence:
 def __init__(self,path,obs,native,browser_pid,browser_start,identity,session):
  self.path=Path(path);self.obs=obs;self.native=native
  self.browser_pid=browser_pid;self.browser_start=browser_start
  self.private_selector=obs.environment['HYPRLAND_INSTANCE_SIGNATURE']
  self.proof={'scope':'Actual private continuation evidence; diagnostics are not original feature acceptance','originalFeatureAcceptance':False,'expectedBrowserIdentity':dict(identity),'expectedBrowserProcess':{'pid':browser_pid,'start':browser_start},'session':session,'samples':[],'commands':[]}
  self.persist()
 def persist(self):PrivateDesktop.private_json(self.path,self.proof)
 def read(self,row,name,fn):
  try:row[name]=fn();self.persist();return row[name]
  except Exception as error:
   row.setdefault('errors',{})[name]={'type':type(error).__name__,'errno':getattr(error,'errno',None),'error':str(error)};self.persist();raise
 def native_sample(self,row):
  self.read(row,'privateSelectorBefore',lambda:self.obs.environment['HYPRLAND_INSTANCE_SIGNATURE'])
  row['samePrivateSelector']=row['privateSelectorBefore']==self.private_selector;self.persist()
  if not row['samePrivateSelector']:
   row.setdefault('errors',{})['identityValidation']={'type':'AssertionError','error':'Captured private instance selector changed before observation'};self.persist()
   raise AssertionError('Captured private instance selector changed before observation')
  self.read(row,'monotonicNs',time.monotonic_ns)
  self.read(row,'browserProcessStart',lambda:self.obs.start(self.browser_pid))
  self.read(row,'actualPrivateClients',lambda:self.obs.data('clients'))
  self.read(row,'native',self.native)
  raw=self.read(row,'seatKeyboardRaw',lambda:self.obs.run('hyprctl','repl','print(hl.plugin.qt_modal_probe.keyboard_state())'))
  self.read(row,'seatKeyboard',lambda:json.loads(raw))
  raw_events=self.read(row,'keyboardEventsRaw',lambda:self.obs.run('hyprctl','repl','print(hl.plugin.qt_modal_probe.keyboard_events())'))
  self.read(row,'keyboardEvents',lambda:json.loads(raw_events))
  self.read(row,'browserProcessStartAfter',lambda:self.obs.start(self.browser_pid))
  self.read(row,'privateSelectorAfter',lambda:self.obs.environment['HYPRLAND_INSTANCE_SIGNATURE'])
  expected=self.proof['expectedBrowserIdentity']
  peers=[peer for peer in row['actualPrivateClients'] if peer.get('pid')==self.browser_pid]
  row['sameBrowserLifetime']=(row['browserProcessStart']==self.browser_start==row['browserProcessStartAfter'] and len(peers)==1 and all(peers[0].get(key)==expected[key] for key in ('address','stableId','pid')))
  row['samePrivateSelector']=row['privateSelectorAfter']==self.private_selector
  self.persist()
  if not row['sameBrowserLifetime'] or not row['samePrivateSelector']:
   row.setdefault('errors',{})['identityValidation']={'type':'AssertionError','error':'Captured private Browser lifetime or instance selector changed'};self.persist()
   raise AssertionError('Captured private Browser lifetime or instance selector changed')
 def begin_dom(self):
  row={'phase':'Before actual fixed read-only DOM query','before':{},'after':{}}
  self.proof['samples'].append(row);self.persist();self.native_sample(row['before']);return row
 def end_dom(self,row,dom):
  row['dom']=dom;self.persist();self.native_sample(row['after'])
 def dom_error(self,row,error):
  row.setdefault('errors',{})['dom']={'type':type(error).__name__,'error':str(error)};self.persist()
 def prepare(self,returned,expected,text,env):
  self.proof.update(expectedValue=expected,requestedContinuation=text,acceptedCaptionDom=returned,
    selectedEnvironment={k:env.get(k)for k in ('WAYLAND_DISPLAY','HYPRLAND_INSTANCE_SIGNATURE','XDG_RUNTIME_DIR','HOME','DISPLAY','DBUS_SESSION_BUS_ADDRESS')},privateDevices=None,privateLayout=None)
  self.persist();self.read(self.proof,'privateDevices',lambda:self.obs.data('devices'))
  self.read(self.proof,'privateLayout',lambda:json.loads(self.obs.run('hyprctl','getoption','input:kb_layout','-j')))
  row={'phase':'Before unchanged continuation type action','before':{},'dom':returned,'after':{}}
  self.proof['samples'].append(row);self.persist();self.native_sample(row['before']);self.native_sample(row['after'])
 def run_wtype(self,command,env):
  record={'command':list(command),'timeoutSeconds':12,'stdout':None,'stderr':None,'returncode':None}
  self.proof['commands'].append(record);self.persist()
  with subprocess.Popen(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) as process:
   record['pid']=process.pid;self.persist()
   try:
    identity={'pid':process.pid,'start':PrivateDesktop.start(process.pid)};record['identity']=identity;self.persist()
    def same(value):
     try:return PrivateDesktop.start(value['pid'])==value['start']
     except OSError:return False
    record['actualOwnedProcess']=snapshot(identity,same);self.persist()
   except OSError as error:
    record['processObservationError']={'type':type(error).__name__,'errno':error.errno,'error':str(error)};self.persist()
   try:
    stdout,stderr=process.communicate(timeout=12)
   except subprocess.TimeoutExpired:
    # Match subprocess.run's original timeout behavior; it is never a normal
    # lifecycle acceptance. The actual child Popen identity is retained.
    record['timeout']=True;record['forcedTimeoutCleanup']=True;self.persist()
    process.kill();process.communicate();raise
   except BaseException:
    process.kill();raise
   record.update(stdout=stdout,stderr=stderr,returncode=process.returncode,normalExit=process.returncode==0,originalProcessGoneAfterWait=(not same(identity) if 'identity' in record else None),pidPathAbsentAfterWait=not Path(f'/proc/{process.pid}').exists());self.persist()
   return subprocess.CompletedProcess(command,process.returncode,stdout,stderr)
