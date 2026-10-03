"""Minimal genuine-QS route composition. Importing does not launch or query."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys,time
from io_guard import publish_json,strict,sha,exact
from selection import *
from materialize import identity,exact_exec

def load_controller():
 # Preserve the approved controller's own dependency resolution and methods.
 sys.path.insert(0,str(COMPOSITION));sys.path.insert(1,str(QA/'pin-frontend-qa-v1'))
 try:
  spec=importlib.util.spec_from_file_location('_pin_private_actual_controller',COMPOSITION/'frontend_cases.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 finally:sys.path.pop(0);sys.path.pop(0)
 if Path(m.KEYBOARD)!=COMPOSITION/'keyboard/physical-keyboard' or sha(m.KEYBOARD)!=sha(KEYBOARD):raise ValueError('Approved actual physical keyboard source differs')
 return m

class QuickshellChannel:
 def __init__(self,session,prepared,output):
  if prepared.get('published')is not True:raise ValueError('No query before all actual source configs are published')
  self.session=session;self.prepared=prepared;self.output=Path(output);self.output.mkdir(mode=0o700);self.rows=[]
 def guard(self):
  self.session.guard();p=self.prepared['process'];root=self.prepared['requester']
  if p.poll()is not None:raise ValueError('Actual requester exited')
  return exact_exec(p.pid,root['identity']['start'],self.prepared['environment'],self.prepared['command'])
 def call(self,target,method,args=()):
  if (target,method)not in {('hoskinson.windows','state'),('hoskinson.windows','pinMenuState'),('hoskinson.windows','pinTypedRetirementRefusal'),('shell','ping')}:
   raise ValueError('Fixed observation/refusal route only; no positive IPC Pin action')
  if method=='pinTypedRetirementRefusal':
   if tuple(args)not in [('boolean',),('string',),('null',),('wrong-collector',)]:raise ValueError('Only four fixed malformed public arguments admitted')
  elif args:raise ValueError('Read-only query accepts no arguments')
  before=self.guard();ordinal=len(self.rows)+1;env=self.prepared['environment'];command=[str(QS),'ipc','--pid',str(self.prepared['process'].pid),'call','--',target,method,*args]
  row=dict(ordinal=ordinal,command=command,targetRequester=before,purpose='public malformed retirement stimulus'if method=='pinTypedRetirementRefusal'else'read-only query');self.rows.append(row)
  process=self.session.host.launch('pin-qs-observation-'+self.prepared['life']+'-'+str(ordinal),command,env)
  row['registered']=dict(self.session.host.processes[-1][1]);publish_json(self.output/(str(ordinal)+'-before.json'),row)
  try:
   process.wait(timeout=2);row.update(exitCode=process.returncode,gone=not Path('/proc/'+str(process.pid)).exists());raw=Path(row['registered']['log']).read_bytes();row.update(rawBytes=len(raw),rawSHA256=hashlib.sha256(raw).hexdigest(),raw=raw.decode('utf8','strict'),requesterAfter=self.guard())
   if process.returncode!=0 or not row['gone']or len(raw)>2*1024*1024 or row['requesterAfter']!=before:raise ValueError('Actual bounded source-bound QS observation did not close normally')
   if method=='ping':
    if raw.strip()!=b'ok':raise ValueError('Actual owned shell ping refused')
   else:strict(raw)
   return raw.decode()
  except BaseException as e:row['error']=repr(e);raise
  finally:publish_json(self.output/(str(ordinal)+'-after.json'),row)
 def readonly(self,target,method):
  if method not in('state','pinMenuState'):raise ValueError('Composition controller read-only methods only')
  return self.call(target,method)

def process_state(value,role,require_current=True):
 if type(value)is not dict or value.get('schema')!='qml-pin-process-lifecycle-v1'or type(value.get('lease'))is not int or value['lease']<=0 or value.get('fault')is not False or type(value.get('exitCode'))is not int or value['exitCode']!=0:raise ValueError('Actual successful typed Process registration required')
 for k in('started','exited','normalExit','stdoutEOF','stderrEOF','workerCreated','workerFinished','workerJoined','kernelGone','receiptVerified','normalLifecycle','historicalKernelProof'):
  if value.get(k)is not True:raise ValueError('Actual full kernel/actor lifecycle missing: '+k)
 if require_current and any(value.get(k)is not True for k in('current','kernelBound','complete')):raise ValueError('Actual current kernel proof missing')
 if not require_current and any(value.get(k)is not False for k in('current','kernelBound','complete')):raise ValueError('Cancelled consumer must deny current authority')
 if value.get('nativeWrites')!=0 or type(value.get('nativeWrites'))is not int or value.get('automaticRetries')!=0 or type(value.get('automaticRetries'))is not int:raise ValueError('Typed zero native writes/retries required')
 if type(value.get('stdout'))is not str or value.get('stderr')!='':raise ValueError('Complete raw helper stream required')
 receipt=strict(value['stdout'])
 if role not in('capture','toggle')or type(receipt)is not dict or receipt.get('result')!=('captured'if role=='capture'else'complete')or type(receipt.get('automaticRetries'))is not int or receipt['automaticRetries']!=0:raise ValueError('Actual unchanged helper receipt missing')
 if role=='capture' and (type(receipt.get('nativeWrites'))is not int or receipt['nativeWrites']!=0 or receipt.get('nativeCompletionClaimed')is not False):raise ValueError('Capture must have no native mutation')
 if role=='toggle' and receipt.get('nativeCompletionClaimed')is not True:raise ValueError('Actual native toggle receipt missing')
 return receipt

class HelperReceipts:
 def __init__(self,prepared,channel,public_refusals=False):self.prepared=prepared;self.channel=channel;self.seen={};self.public_refusals=public_refusals;self.refusals=[]
 def one(self,state,role,current=True):
  receipt=process_state(state,role,current);root=self.prepared['requester'];authority=receipt.get('authority',{});life=authority.get('frontend',{});requester=authority.get('requester',{})
  if type(life.get('pid'))is not int or life['pid']<=0 or type(life.get('start'))is not str or type(life.get('parent'))is not int or life['parent']!=root['identity']['pid']or type(life.get('pgid'))is not int or life['pgid']!=root['identity']['pgid']or not exact(requester,root['identity'])or authority.get('role')!='shell':raise ValueError('Exact actual helper/requester lifetime required')
  p=Path(self.prepared['entry']['evidenceDirectory'])/(str(life['pid'])+'-'+life['start']+'.json');s=p.lstat();raw=p.read_bytes()
  if not stat.S_ISREG(s.st_mode)or s.st_uid!=os.getuid()or s.st_nlink!=1 or stat.S_IMODE(s.st_mode)!=0o600 or len(raw)>1048576 or not exact(strict(raw),receipt)or Path('/proc/'+str(life['pid'])).exists():raise ValueError('Actual durable helper source/lifecycle/file differs')
  key=(life['pid'],life['start']);row=dict(role=role,lease=state['lease'],processState=state,receiptPath=str(p),receiptSHA256=sha(p),receipt=receipt)
  if key in self.seen and not exact(self.seen[key]['receipt'],receipt):raise ValueError('Historical helper receipt changed')
  self.seen[key]=row;return row
 def completion(self,receipt):
  menu=strict(self.channel.call('hoskinson.windows','pinMenuState'));d=menu.get('processDiagnostics')
  if type(d)is not dict or d.get('retirementObservationLost')is not False:raise ValueError('Actual source-bound process diagnostics missing')
  capture=self.one(d['capture'],'capture');action=self.one(d['action'],'toggle')
  if not exact(action['receipt'],receipt):raise ValueError('Genuine callback receipt differs from current registered Process')
  if self.public_refusals and not self.refusals:
   for kind in ('boolean','string','null','wrong-collector'):
    observed=strict(self.channel.call('hoskinson.windows','pinTypedRetirementRefusal',(kind,)))
    if observed.get('schema')!='pin-public-typed-refusal-observation-v1'or observed.get('kind')!=kind or observed.get('lease')!=d['actionLease']or not exact(observed.get('before'),observed.get('after'))or not exact(observed.get('before'),d['action']):raise ValueError('Actual typed refusal must preserve exact successful registered record')
    refused=observed.get('result')
    if type(refused)is not dict or type(refused.get('error'))is not str or not refused['error']or refused.get('schema')!='qml-pin-process-lifecycle-v1'or type(refused.get('nativeWrites'))is not int or refused['nativeWrites']!=0 or type(refused.get('automaticRetries'))is not int or refused['automaticRetries']!=0 or refused.get('terminalRetired')is True:raise ValueError('Actual malformed public argument must refuse without retirement')
    process_state(observed['after'],'toggle');self.refusals.append(observed)
  return dict(actualOwnedDurableFile=True,exactActualHelperLifetime=True,normalProcessExit=True,registeredDescendantGone=True,rawReceiptExact=True,capture=capture,action=action,rawMenu=menu)
 def terminal(self):
  menu=strict(self.channel.call('hoskinson.windows','pinMenuState'));d=menu['processDiagnostics']
  for role in('capture','action'):
   s=d[role]
   if s is not None:self.one(s,'capture'if role=='capture'else'toggle',False)
  folder=Path(self.prepared['entry']['evidenceDirectory']);files=sorted(folder.glob('*.json'))
  if len(files)!=len(self.seen)or {str(p)for p in files}!={row['receiptPath']for row in self.seen.values()}:raise ValueError('Every actual Pin/capture receipt must be accounted; no extra warmups/helpers')
  return dict(rows=list(self.seen.values()),exactDurableCount=len(files),allNormal=True,allGone=True)

def controller(route,shell,channel,receipts):
 m=load_controller()
 class ExactPrivateFrontend(m.FrontendCases):
  # The genuine original toggle method and effect oracles are inherited exact.
  def open_keyboard(self):
   expected=self.expected_name;wanted=self.route.own(expected);self.chord('super-t',True)
   def actual():
    widget=self.query('state');native=self.native()
    if not widget.get('popupOpen')or widget.get('menuMode')or widget.get('keyboardMode')is not True or widget.get('keyboardFocus')is not True:return None
    popup=m.layer(native,self.shell.pid,'hoskinson-taskbar-popup')
    if native.get('keyboardSurfacePresent')is not True or not m.exact(native.get('keyboardLayerOwner'),popup):return None
    items=widget['previewItems'];index=widget['selectedWindowIndex']
    if type(index)is not int or not items:return None
    item=items[index%len(items)];current=[w for w in self.session.data('clients')if w['address']==item['address']and w['pid']==self.route.fixture.pid]
    if len(current)!=1:raise ValueError('One actual currently selected owned preview required')
    return dict(widget=widget,native=native,layer=popup,selected=current[0],scope=self.scope())
   value=self.wait('Genuine private keyboard selection before menu',actual)
   # Fixture combineMode=never exposes two real one-window groups. A single
   # extra actual SUPER+T cycles the existing product's group function.
   if value['selected']['address']!=wanted['address']:
    if value['widget']['groups']!=2:raise ValueError('Fixed two actual fixture groups required; no arbitrary cycling')
    self.chord('super-t',True);value=self.wait('Actual second group selected by genuine cycling',actual)
   if any(value['selected'][k]!=wanted[k]for k in('address','stableId','pid')):raise ValueError('Fixed planned member selection failed; no replacement/retry')
   captured=self.route.capture(expected);events=self.route.query('pin_events');self.chord('menu',True);return captured,events
 return ExactPrivateFrontend(route,shell,None,channel.readonly,receipts.prepared['pinConfig'],receipts.completion)

def retirement_proof(before,after,expected_role):
 old=before['processDiagnostics'];new=after['processDiagnostics'];name='capture'if expected_role=='capture'else'action';lease=old[name+'Lease'];observations=new['retirements']
 if lease<=0 or len(observations)!=len(old['retirements'])+2:raise ValueError('Both genuine previous capture and action must retire before replacement')
 matches=[r for r in observations[len(old['retirements']):]if r['role']==expected_role]
 if len(matches)!=1 or matches[0]['lease']!=lease:raise ValueError('Exact previous public typed retirement not observed')
 r=matches[0]['result']
 if r.get('schema')!='qml-pin-process-lifecycle-v1'or r.get('lease')!=lease or any(r.get(k)is not True for k in('terminalRetired','normalLifecycle','historicalKernelProof','workerJoined'))or any(r.get(k)is not False for k in('current','kernelBound','complete'))or r.get('nativeWrites')!=0 or r.get('automaticRetries')!=0:raise ValueError('Exact typed normal public retirement refused')
 if type(new[name+'Lease'])is not int or new[name+'Lease']<=lease:raise ValueError('Replacement must use genuinely fresh actual lease')
 return matches[0]
