"""Inert real-input controller. Requires root's reviewed actual scope/host readers.

The scope reader must observe an actual engine lifetime provider. This module
cannot create its witness, launch a desktop, or open a menu through IPC.
"""
from pathlib import Path
from decimal import Decimal
import json,os,time
from frontend_authority import binding,current,pointer,keyboard,helper,FrontendCase,layer,exact,numeric,shell_requester,completion_current,focus_projection,one_native_event
from native_authority import token,public,integer_point,move_command,input_safe,protected_order

B=Path(__file__).resolve().parent
KEYBOARD=B/'keyboard/physical-keyboard'

class FrontendCases:
 def __init__(self,route,shell,scope_reader,ipc_readonly,pin_config,helper_observer):
  self.route=route;self.session=route.session;self.shell=shell;self.scope_reader=scope_reader;self.ipc_readonly=ipc_readonly;self.config=pin_config;self.helper_observer=helper_observer
  self.output=route.output/'frontend';self.output.mkdir(mode=0o700)
  self.report=dict(result='pending',checks=[],observations=[],inputs=[],setupInputs=[],genuineFrontendAccepted=False,nativeRun=False,mainChanges=False,engineAuthorityProvided=False,automaticRetries=0)
 def persist(self):
  p=self.output/'report.json';p.write_text(json.dumps(self.report,indent=2,allow_nan=False)+'\n');p.chmod(0o600)
 def observe(self,label,reader):
  if len(self.report['observations'])>=4096:raise RuntimeError('Bounded frontend observation cap')
  row=dict(label=label,sequence=len(self.report['observations'])+1,startedNs=time.monotonic_ns());self.report['observations'].append(row);self.persist()
  try:self.session.guard();row['value']=reader();row['completedNs']=time.monotonic_ns();self.persist();return row['value']
  except BaseException as e:row['error']=repr(e);self.persist();raise
 def wait(self,label,reader,seconds=5):
  deadline=time.monotonic()+seconds
  while time.monotonic()<deadline:
   value=self.observe(label,reader)
   if value:return value
   time.sleep(.04)
  raise RuntimeError('Bounded actual frontend wait timed out: '+label)
 def query(self,name):
  if name not in('state','pinMenuState'):raise ValueError('Fixed readonly frontend query required; no IPC open/invoke')
  return json.loads(self.ipc_readonly('hoskinson.windows',name))
 def native(self):return json.loads(self.session.ctl('repl','print(hl.plugin.toolkit_held_probe.state())'))
 def scope(self):
  value=self.scope_reader()
  if type(value)is not dict or value.get('actualProviderVerified')is not True or value.get('sourceClosureVerified')is not True or value.get('processAndEngineCurrent')is not True or value.get('processId')!=self.shell.pid:raise RuntimeError('Actual reviewed engine lifetime provider required; no inferred/constant epoch')
  self.report['engineAuthorityProvided']=True;self.persist();return value['scope']
 def snapshots(self):return dict(menu=self.query('pinMenuState'),native=self.native(),scope=self.scope())
 def chord(self,name,setup=False):
  if name not in('super-t','menu','return','escape'):raise ValueError('Admitted physical frontend chord required')
  input_safe(self.native());self.session.guard()
  env=dict(self.session.env,WINDOW_QA_COMPOSITOR_PID=str(self.session.evidence['compositorPID']),WINDOW_QA_COMPOSITOR_START=str(self.session.evidence['compositorStart']))
  row=dict(route='physical '+name,setupOnly=setup,command=[str(KEYBOARD),'--chord',name]);self.report['setupInputs'if setup else'inputs'].append(row);self.persist()
  process=self.session.host.launch('pin-frontend-chord-'+str(len(self.report['setupInputs']))+'-'+str(len(self.report['inputs'])),row['command'],env)
  row['pid']=process.pid;row['start']=Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()[19];self.persist();process.wait(timeout=4)
  row['exitCode']=process.returncode;row['gone']=not Path(f'/proc/{process.pid}').exists();self.persist()
  if process.returncode!=0 or not row['gone']:raise RuntimeError('Actual physical driver normal exit and all releases required; no retry')
  return row
 def item_point(self,item,row):
  x,y,w,h=[Decimal(str(v))for v in row['box']];ix,iy,iw,ih=[Decimal(str(item[k]))for k in('x','y','width','height')]
  if ix<0 or iy<0 or iw<=0 or ih<=0 or ix+iw>w or iy+ih>h:raise ValueError('Whole actual item must be inside real layer')
  return integer_point([str(x+ix),str(y+iy),str(iw),str(ih)],1600,1000)
 def pointer_live(self):
  self.session.guard();process=self.route.pointer
  if not process or process.poll()is not None or Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()[19]!=self.route.report['pointer']['start']:raise RuntimeError('Exact current registered pointer lifetime required')
  return process
 def move_layer(self,point,expected_layer):
  text=move_command(point,1600,1000);input_safe(self.native());self.session.guard()
  process=self.route.pointer
  if not process or process.poll()is not None:raise RuntimeError('Exact live owned pointer required')
  actual=Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()[19]
  if actual!=self.route.report['pointer']['start']:raise RuntimeError('Owned pointer lifetime changed')
  process.stdin.write(text);process.stdin.flush()
  def arrived():
   native=self.native()
   try:input_safe(native)
   except ValueError:return None
   if native.get('pointerSurfacePresent')is True and exact(native.get('pointerLayerOwner'),expected_layer)and type(native.get('cursor'))is list and len(native['cursor'])==2 and all(numeric(v)==Decimal(p)for v,p in zip(native['cursor'],point)):return native
   return None
  return self.wait('Actual same layer/cursor before frontend press',arrived,3)
 def buttons(self,button,setup,before_press):
  if button not in(272,273):raise ValueError('Admitted actual mouse button required')
  process=self.pointer_live();before_press();input_safe(self.native())
  row=dict(route='pointer',button=button,setupOnly=setup,pressSent=False,releaseSent=False);self.report['setupInputs'if setup else'inputs'].append(row);self.persist()
  process.stdin.write(f'button {button} 1\n');process.stdin.flush();self.route.held=True;row['pressSent']=True;self.persist()
  process.stdin.write(f'button {button} 0\n');process.stdin.flush();self.route.held=False;row['releaseSent']=True;self.persist()
  return row
 def hover_preview(self,captured):
  state=self.observe('Actual taskbar icon source',lambda:dict(widget=self.query('state'),native=self.native(),scope=self.scope()))
  bar=layer(state['native'],self.shell.pid,'omarchy-bar');items=[r for r in state['widget']['taskbarItems']if captured['address']in r['windows']]
  if len(items)!=1:raise RuntimeError('One actual taskbar group for exact member required')
  point=self.item_point(items[0],bar);self.move_layer(point,bar)
  def opened():
   widget=self.query('state');native=self.native()
   if not widget.get('popupOpen')or widget.get('menuMode'):return None
   previews=[r for r in widget['previewItems']if r['address']==captured['address']]
   if len(previews)!=1:return None
   popup=layer(native,self.shell.pid,'hoskinson-taskbar-popup')
   return dict(widget=widget,native=native,item=previews[0],layer=popup,scope=self.scope())
  return self.wait('Genuine pointer hover opens exact real preview',opened)
 def open_right(self,name):
  captured=self.route.capture(name);before_events=self.route.query('pin_events');popup=self.hover_preview(captured)
  point=self.item_point(popup['item'],popup['layer']);self.move_layer(point,popup['layer'])
  fresh=self.observe('Actual preview member/layer before rightclick',lambda:dict(widget=self.query('state'),native=self.native(),scope=self.scope()))
  if not exact(fresh['scope'],popup['scope'])or not exact(layer(fresh['native'],self.shell.pid,'hoskinson-taskbar-popup'),popup['layer'])or [r for r in fresh['widget']['previewItems']if r['address']==captured['address']]!=[popup['item']]:raise RuntimeError('Actual preview allocation/source lifetime changed')
  def still_preview():
   value=dict(widget=self.query('state'),native=self.native(),scope=self.scope());input_safe(value['native'])
   if not exact(value['scope'],popup['scope'])or not exact(layer(value['native'],self.shell.pid,'hoskinson-taskbar-popup'),popup['layer'])or [r for r in value['widget']['previewItems']if r['address']==captured['address']]!=[popup['item']]:raise RuntimeError('Actual preview changed immediately before press')
   pointer(value['native'],dict(layer=popup['layer'],point=point));return value
  self.buttons(273,True,lambda:self.observe('Exact real preview immediately before rightclick',still_preview))
  return captured,before_events
 def open_keyboard(self):
  # Real installed SUPER+T binding opens the preview in keyboard mode. No IPC
  # cycle/menu invocation is made by this controller.
  self.chord('super-t',True)
  def selected():
   widget=self.query('state');native=self.native()
   if not widget.get('popupOpen')or widget.get('menuMode')or widget.get('keyboardMode')is not True or widget.get('keyboardFocus')is not True:return None
   popup=layer(native,self.shell.pid,'hoskinson-taskbar-popup')
   if native.get('keyboardSurfacePresent')is not True or not exact(native.get('keyboardLayerOwner'),popup):return None
   items=widget['previewItems'];index=widget['selectedWindowIndex']
   if type(index)is not int or not items:return None
   chosen=items[index%len(items)];clients=[w for w in self.session.data('clients')if w['address']==chosen['address']and w['pid']==self.route.fixture.pid]
   if len(clients)!=1:raise RuntimeError('Actual selected owned preview member required')
   return dict(widget=widget,native=native,layer=popup,selected=clients[0],scope=self.scope())
  value=self.wait('Actual selected-member preview keyboard surface',selected)
  names=[name for name in('owner','peer','child','nested')if (row:=self.route.own(name))and row['address']==value['selected']['address']]
  if len(names)!=1:raise RuntimeError('One exact selected fixture lifetime required')
  captured=self.route.capture(names[0]);before_events=self.route.query('pin_events');self.chord('menu',True)
  return captured,before_events
 @staticmethod
 def press_args(value,route):return dict(menu=value['menu'],native=value['native'],scope=value['scope'],route=route)
 def toggle(self,name,opener='right',route='pointer'):
  if opener not in('right','keyboard')or route not in('pointer','return'):raise ValueError('Admitted actual opener/action route required before any input')
  captured,events=self.open_right(name)if opener=='right'else self.open_keyboard()
  def ready():
   value=self.snapshots()
   if value['menu'].get('status')!='ready':return None
   expected=binding(value['menu'],value['native'],value['scope'])
   if not exact(expected['captured'],captured):raise RuntimeError('Actual popup capture changed selected native lifetime')
   return value,expected
  raw,expected=self.wait('Actual real per-window Pin menu capture',ready)
  if self.route.query('pin_events')!=events:raise RuntimeError('Menu setup/capture cannot count as native Pin mutation')
  before=self.route.scene();row=dict(opener=opener,route=route,captured=captured,menuBinding=expected,rawBefore=raw,sceneBefore=before,eventsBefore=events);self.report['inputs'].append(row);self.persist()
  owner=[w for w in before['clients']if w['address']==captured['address']and w['stableId']==captured['stableId']and w['pid']==captured['pid']]
  if len(owner)!=1:raise RuntimeError('Actual current selected owner required before Pin')
  case=FrontendCase(expected)
  if route=='pointer':self.move_layer(expected['point'],expected['layer'])
  pre=self.observe('Actual menu/layer/engine immediately before genuine Pin input',self.snapshots);case.press(pre['menu'],pre['native'],pre['scope'],route)
  if route=='pointer':row['realInput']=self.buttons(272,False,lambda:case.press(**self.press_args(self.observe('Current exact real row immediately before down',self.snapshots),route)))
  elif route=='return':row['realInput']=self.chord('return')
  else:raise ValueError('Admitted real Toggle pin route required')
  case.release(True);self.persist()
  def completed():
   value=self.snapshots();menu=value['menu']
   if menu.get('status')=='refused-or-uncertain':raise RuntimeError('Actual frontend helper refused or uncertain; no retry')
   if menu.get('status')!='complete':return None
   completion_current(menu,value['native'],value['scope'],expected)
   receipt=menu.get('receipt');helper(receipt,captured,owner[0]['pinned'],shell_requester(self.config,self.shell.pid),self.config['compositor']['identity'])
   proof=self.helper_observer(receipt)
   if type(proof)is not dict or any(proof.get(k)is not True for k in('actualOwnedDurableFile','exactActualHelperLifetime','normalProcessExit','registeredDescendantGone','rawReceiptExact')):raise RuntimeError('Actual normal registered helper lifecycle required')
   return dict(menu=menu,native=value['native'],scope=value['scope'],helper=receipt,helperLifecycle=proof)
  row['completion']=self.wait('Actual helper EOF/normal completion after real release',completed);case.receipt=True
  row['eventsAfter']=self.route.query('pin_events');one_native_event(events,row['eventsAfter'],row['completion']['helper']['rawNativeResult']);self.persist()
  after=self.route.scene();row['sceneAfter']=after;self.persist();protected_order(after['stack'])
  current_owner=[w for w in after['clients']if w['address']==captured['address']and w['stableId']==captured['stableId']and w['pid']==captured['pid']]
  if len(current_owner)!=1 or current_owner[0]['pinned']is not(not owner[0]['pinned']):raise RuntimeError('Actual latest one-toggle owner bit required')
  keys=('address','stableId','pid','pinned','floating','at','size','workspace','monitor','fullscreen','fullscreenClient')
  peers=lambda scene:{w['stableId']:{k:w.get(k)for k in keys}for w in scene['clients']if w['address']!=captured['address']}
  if not exact(peers(before),peers(after))or not exact(focus_projection(before),focus_projection(after))or not exact(raw['native'].get('keyboardLayerOwner'),row['completion']['native'].get('keyboardLayerOwner')):raise RuntimeError('Independent member and distinct entry Core/Seat preservation required')
  case.observed=True;accepted=case.accept();self.report['checks'].append(dict(name='Genuine '+opener+'/'+route+' per-window Toggle pin',passed=accepted,inputIndex=len(self.report['inputs'])-1));self.persist()
  self.chord('escape',True);self.wait('Actual user Escape closes Pin menu',lambda:self.query('pinMenuState').get('open')is False)
  return row
