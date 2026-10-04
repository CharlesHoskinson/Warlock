"""Full QT01–08 imperative orchestration; resources acquired by reviewed root launcher."""
import json,time
from keyboard import shift_pair
from capture_scope import attribution
from coordinates import input_coordinates
from pathlib import Path
class Refused(ValueError):pass
PHASES=tuple('QT%02d'%i for i in range(1,9))
def remaining(deadline):
 value=deadline-time.monotonic()
 if value<=0:raise Refused('Original absolute six-second QT phase deadline')
 return value
class Driver:
 def __init__(self,actor,session,host,endpoint,parent_factory,shell,helpers,event_types,directory):
  self.actor=actor;self.session=session;self.host=host;self.endpoint=endpoint;self.parent_factory=parent_factory;self.shell=shell;self.h=helpers;self.types=event_types;self.directory=Path(directory);self.directory.mkdir(mode=0o700,parents=True,exist_ok=False);self.read_id=0;self.targets={};self.report={'passed':False,'fullCampaignPassed':False,'nativeAcceptance':False,'phases':[],'checks':[],'openGates':[]};self.parent=None;self.shell.driver=self
 def check(self,name,value,**evidence):
  self.report['checks'].append(dict(name=name,passed=bool(value),**evidence));self.persist()
  if not value:raise Refused(name)
 def persist(self):(self.directory/'report.json').write_text(json.dumps(self.report,indent=2)+'\n')
 def wait(self,fn):
  while remaining(self.deadline):
   self.session.guard();value=fn();remaining(self.deadline)
   if value:return value
   time.sleep(min(.02,remaining(self.deadline)))
 def send(self,op,role=None):return self.actor.send(op,self.deadline,role)
 def observe(self):
  self.read_id+=1;remaining(self.deadline);value=self.endpoint.scene_facts(str(self.read_id));remaining(self.deadline);return value
 def fact(self,role):
  self.session.guard();rows=self.actor.read();bound=self.targets.get(role)
  if bound is None:bound=self.binding(role,False)
  ident=bound['identity'];current=[r for r in rows if r.get('role')==role]
  if not current or max(r['instance'] for r in current)!=ident['instance'] or any(r['event'] in ('destroy-request','local-destroy') and r.get('instance')==ident['instance'] for r in current):raise Refused('captured fact target retired or replaced')
  clients=self.session.data('clients');matches=[w for w in clients if w['address']==bound['native']['address'] and w['pid']==self.actor.pid and w['title']==f'ELM-QT6-{role}-{self.actor.pid}']
  if len(matches)!=1:raise Refused('captured hidden/live native identity missing or replaced')
  self.read_id+=1;snapshot=self.endpoint.snapshot(str(self.read_id));remaining(self.deadline)
  identities=[w for w in snapshot['windows'] if w['label']==f'ELM-QT6-{role}-{self.actor.pid}']
  if len(identities)!=1:raise Refused('exact native Qt projection identity')
  matching=[w for w in self.observe()['facts']['windows'] if w['incarnation']==identities[0]['incarnation']]
  if len(matching)!=1:raise Refused('exact current full native fact')
  previous=bound.get('factIncarnation')
  if previous is not None and matching[0]['incarnation']!=previous:raise Refused('captured native fact incarnation changed')
  bound['factIncarnation']=matching[0]['incarnation'];return matching[0]
 def binding(self,role,landmark=True):
  result=self.wait(lambda:self.h.scene.bind(self.actor,self.session,role,require_landmark=landmark))
  old=self.targets.get(role)
  if old and old['identity']==result['identity'] and old['native']['address']==result['native']['address'] and 'factIncarnation' in old:result['factIncarnation']=old['factIncarnation']
  self.targets[role]=result;return result
 def interval_start(self):
  rows=self.actor.read();return rows[-1]['sequence'] if rows else 0
 def inspect(self):self.send('inspect');return self.actor.read()
 def identity(self,b):return {k:b['identity'][k] for k in ('instance','mapGeneration','surfaceId')}
 def native_roles(self):
  value=json.loads(self.session.ctl('elm_role_state'));return self.h.observer.roles(value,compositor_pid=self.native_pid)
 def role(self,name,parent=None,modal=None,blocked=None):
  b=self.binding(name,False);p=self.binding(parent,False)['native']['address'] if parent else '0x0'
  row=self.h.observer.selected(self.native_roles(),address=b['native']['address'],pid=self.actor.pid,parent_address=p,modal=modal,blocked=blocked)
  expected=self.binding(parent,False)['wire']['toplevelId'] if parent else None
  if b['wire']['parentToplevel']!=expected:raise Refused('actual Wayland transient parent differs from declared native owner')
  return row
 def place(self,name,x,y,w=320,h=180):
  b=self.binding(name,False);address=b['native']['address'];selector=json.dumps('address:'+address)
  def dispatch(expression):
   value=self.session.ctl('eval','local r=hl.dispatch('+expression+');if type(r)~="table" or r.ok~=true then error("QT fixture placement refused") end').strip()
   if value!='ok':raise Refused('actual structured native placement result')
  def current():return next((row for row in self.session.data('clients') if row['address']==address and row['pid']==self.actor.pid),None)
  dispatch('hl.dsp.window.float({action="enable",window='+selector+'})');self.wait(lambda:current() if current() and current()['floating'] else None)
  dispatch('hl.dsp.window.resize({x='+str(w)+',y='+str(h)+',window='+selector+'})');resized=self.wait(lambda:current() if current() and current()['size']==[w,h] else None)
  dx=x-resized['at'][0];dy=y-resized['at'][1]
  dispatch('hl.dsp.window.move({x='+str(dx)+',y='+str(dy)+',relative=true,window='+selector+'})');self.wait(lambda:current() if current() and current()['at']==[x,y] else None)
  self.inspect();after=self.binding(name);self.check(self.phase+':placement-retains-original-current-role',b['identity']==after['identity'] and b['native']['address']==after['native']['address'],before=b,after=after);return after
 def stable_capture(self,name,others=()):
  before=self.binding(name);census=self.session.data('clients');popup=json.loads(self.session.ctl('elm_popup_state'))
  bindings={r:self.binding(r) for r in others};exclusions=[attribution(self.actor.stderr.read_bytes(),before,b) for b in bindings.values()]
  directory=self.directory/(self.phase+'-'+name+'-'+str(time.time_ns()))
  data,measurement=self.h.pixels.capture(self.session,self.host,directory,self.deadline,selected={'binding':before,'census':census,'popup':popup,'otherBindings':bindings,'exclusions':exclusions})
  samples=self.h.pixels.yellow_marker(data,before['marker']['global']);measurement['markerSamples']=samples
  (directory/'record.json').write_text(json.dumps(measurement,indent=2)+'\n')
  self.inspect();after=self.binding(name);self.check(self.phase+':exact-bound-scene-before-after-capture',self.h.scene.same(before,after),before=before,after=after)
  self.check(self.phase+':stable-real-capture-'+name,before['native']['at']==after['native']['at'] and before['native']['size']==after['native']['size'] and before['wire']['windowGeometry']==after['wire']['windowGeometry'] and before['wire']['ack']==after['wire']['ack'] and before['wire']['lastCommitIndex']==after['wire']['lastCommitIndex'] and census==self.session.data('clients') and popup==json.loads(self.session.ctl('elm_popup_state')),before=before,after=after,measurement=measurement)
  self.check(self.phase+':actual-marker-'+name,samples['passed'],samples=samples)
  return after
 def pointer_parent(self,point):
  # Actual parent observation validates the nested surface before and after motion.
  text=f'observe {self.native_pid} {self.native_start}'
  a=self.parent.send(text,self.deadline)['observation'];a=json.loads(a) if type(a) is str else a
  if a.get('target')!={'pid':self.native_pid,'started':self.native_start} or a.get('surfaceExtent')!=[800,600] or a.get('viewportDestination')!=[800,600] or a.get('output',{}).get('scale')!=1:raise Refused('actual parent/nested output identity and extent')
  corners=a.get('corners')
  if type(corners) is not list or len(corners)!=4:raise Refused('actual parent global transform corners')
  origin=corners[0]
  if corners!=[origin,[origin[0]+800,origin[1]],[origin[0],origin[1]+600],[origin[0]+800,origin[1]+600]]:raise Refused('current parent unscaled axis-aligned mapping')
  global_point=[origin[i]+point[i] for i in (0,1)]
  if any(type(v) not in (int,float) or int(v)!=v or not 0<=v<=4096 for v in global_point):raise Refused('bounded exact parent motion coordinate')
  self.parent.send('motion %d %d'%tuple(global_point),self.deadline)
  b=self.parent.send(text,self.deadline)['observation'];b=json.loads(b) if type(b) is str else b
  for field in ['target','viewId','surfaceId','surfaceExtent','viewportDestination','output','corners']:
   if b.get(field)!=a.get(field):raise Refused('parent surface identity changed across motion')
  if b.get('pointer',{}).get('focusedPid')!=self.native_pid or b['pointer'].get('focusedStarted')!=self.native_start or b['pointer'].get('focusedViewId')!=b['viewId'] or b['pointer'].get('focusedSurfaceId')!=b['surfaceId'] or b['pointer'].get('global')!=global_point:raise Refused('actual parent focus/current exact nested surface')
  return b
 def focus(self,role):
  b=self.binding(role,False);value=json.loads(self.session.ctl('elm_held_state'))
  self.check(self.phase+':actual-focus-'+role,value['focus']['surfaceClientPID']==self.actor.pid and value['focus']['surfaceId']==b['identity']['surfaceId'],focus=value['focus'],binding=b)
 def retired(self,old):
  def gone():
   self.actor.read();current=self.h.scene.current_role(self.actor.rows,old['identity']['role'])
   clients=self.session.data('clients')
   return current is None and not any(w['address']==old['native']['address'] and w['pid']==self.actor.pid for w in clients)
  self.wait(gone);self.check(self.phase+':actual-role-retired-'+old['identity']['role'],True,old=old)
 def QT01(self):
  self.send('create-owners');a=self.place('A',40,90);c=self.place('C',420,90)
  self.check('QT01:unique-native-resources',a['identity']['surfaceId']!=c['identity']['surfaceId'] and a['native']['address']!=c['native']['address'])
  self.stable_capture('C',('A',));self.pair('C');self.focus('C');self.key('C');self.drafts(('A','C'),0)
  # Measured overlap: C placed over A, selected actual opaque landmark must contribute.
  a=self.place('A',40,90);c=self.place('C',60,110);self.stable_capture('C');self.pair('C');self.focus('C');self.key('C')
 def QT02(self):
  ordinary=self.fact('A');before=self.binding('A');self.read_id+=1;g=self.endpoint.geometry_facts(str(self.read_id));remaining(self.deadline)
  window=next(w for w in g['facts']['windows'] if w['incarnation']==ordinary['incarnation']);self.report['geometryOrdinary']=window
  if not window['capabilities']['maximize']:
   self.shell.refuse_unavailable(before,ordinary['incarnation'],'maximize',self.deadline)
   after=self.fact('A');self.check('QT02:unsupported-effect2-no-native-mutation',all(ordinary[k]==after[k] for k in ('geometry','workspace','monitor','incarnation','minimized','shouldRenderAny','shouldRenderOwnMonitor','acceptsInput')),before=ordinary,after=after)
   self.report['openGates'].append('QT02 actual geometryEffect2 MAX/restore capability unavailable')
  else:
   receipt=self.shell.invoke(f'ELM-QT6-A-{self.actor.pid}',ordinary['incarnation'],'maximize',self.deadline)
   self.wait(lambda:self.binding('A',False) if self.binding('A',False)['qt'].get('observedMaximized') is True else None)
   self.stable_capture('A',('C',));restored=self.shell.invoke(f'ELM-QT6-A-{self.actor.pid}',ordinary['incarnation'],'restore-geometry',self.deadline);after=self.fact('A')
   self.check('QT02:effect2-exact-ordinary-restored',all(after[k]==ordinary[k] for k in ['geometry','workspace','monitor','incarnation']),before=ordinary,after=after,receipts=[receipt,restored])
  # Mandatory standard toolkit protocol is independent of experiment capability.
  standard_before=self.binding('A');prior_shell=self.shell.journal();self.send('maximize','A')
  maximized=self.wait(lambda:self.binding('A') if bool(self.binding('A')['qt'].get('observedWindowState',0)&self.types['windowMaximized']) else None)
  self.read_id+=1;geo=self.endpoint.geometry_facts(str(self.read_id));remaining(self.deadline);actual=next(w for w in geo['facts']['windows'] if w['incarnation']==ordinary['incarnation'])
  self.check('QT02:actual-standard-QT-MAX',actual['nativeMode']==actual['clientMode']=='maximized' and maximized['wire']['ack']['serial']!=standard_before['wire']['ack']['serial'] and self.shell.journal()==prior_shell,before=standard_before,after=maximized,native=actual)
  self.stable_capture('A',('C',));self.send('unmaximize','A')
  standard_after=self.wait(lambda:self.binding('A') if not (self.binding('A')['qt'].get('observedWindowState',0)&self.types['windowMaximized']) and self.binding('A')['native']['at']==standard_before['native']['at'] and self.binding('A')['native']['size']==standard_before['native']['size'] else None)
  self.check('QT02:standard-restores-original-position-size',standard_before['native']['at']==standard_after['native']['at'] and standard_before['native']['size']==standard_after['native']['size'] and standard_before['native']['workspace']==standard_after['native']['workspace'] and standard_before['native']['monitor']==standard_after['native']['monitor'] and self.shell.journal()==prior_shell,before=standard_before,after=standard_after)
  self.stable_capture('A',('C',));self.drafts(('A','C'),0)
 def QT03(self):
  self.send('open-modal');self.role('B','A',True,False);self.role('A',None,False,True);self.place('B',240,320)
  baseline=self.interval_start();self.pair('A',blocked=True);self.focus('B');self.key('B');self.drafts(('A','B','C'),baseline)
 def QT07(self):
  if self.h.scene.current_role(self.actor.read(),'B') is None:self.send('open-modal')
  self.place('B',240,320);self.place('C',420,90);self.role('B','A',True,False)
  baseline=self.interval_start();ordinary=self.fact('A');child_before=self.fact('B');c=self.fact('C');bounds={r:self.binding(r) for r in ('A','B')}
  for name in ('A','B'):self.stable_capture(name,tuple(r for r in ('A','B','C') if r!=name))
  receipt=self.shell.invoke(f'ELM-QT6-A-{self.actor.pid}',ordinary['incarnation'],'minimize',self.deadline)
  hidden=self.wait(lambda:self.fact('A') if self.fact('A')['minimized'] else None);hidden_b=self.wait(lambda:self.fact('B') if self.fact('B')['minimized'] else None)
  for name,fact in [('A',hidden),('B',hidden_b)]:self.check('QT07:actual-native-hidden-'+name,not fact['shouldRenderAny'] and not fact['shouldRenderOwnMonitor'] and not fact['acceptsInput'],fact=fact,receipt=receipt)
  self.shell.family_hidden_pixels(bounds,self.deadline)
  # Complete pointer/key intervals over hidden family regions. Native focus
  # determines whether the legitimate remaining C receives the nontext key.
  start=self.interval_start();self.pointer_parent(bounds['A']['marker']['global']);self.parent.send('press 272',self.deadline);self.parent.send('release 272',self.deadline);rows=self.inspect();self.h.journal.blocked_raw_pointer_interval(rows,start)
  focus=json.loads(self.session.ctl('elm_held_state'))['focus'];c_binding=self.binding('C',False)
  if focus['surfaceId'] in [bounds[r]['identity']['surfaceId'] for r in ('A','B')]:raise Refused('hidden family retains keyboard recipient')
  if focus['surfaceClientPID']==self.actor.pid and focus['surfaceId']==c_binding['identity']['surfaceId']:self.key('C')
  else:self.key('A',blocked=True)
  all_rows=self.actor.read();self.check('QT07:whole-hidden-interval-no-family-input',not any(row['sequence']>start and row.get('role') in ('A','B') and row['event'] in ('window-button-press','window-button-release','window-key-press','window-key-release','widget-button-press','widget-button-release','widget-key-press','widget-key-release') for row in all_rows),rows=all_rows,nativeFocus=focus)
  receipt=self.shell.invoke(f'ELM-QT6-A-{self.actor.pid}',ordinary['incarnation'],'restore',self.deadline);shown=self.wait(lambda:self.fact('A') if not self.fact('A')['minimized'] else None);shown_b=self.wait(lambda:self.fact('B') if not self.fact('B')['minimized'] else None)
  stable=['geometry','workspace','monitor','incarnation','minimized','shouldRenderAny','shouldRenderOwnMonitor','acceptsInput']
  self.check('QT07:restored-owner-child-and-independent-peer',shown['workspace']==ordinary['workspace'] and shown['monitor']==ordinary['monitor'] and shown_b['acceptsInput'] and all(c[k]==self.fact('C')[k] for k in stable),ownerBefore=ordinary,ownerAfter=shown,childBefore=child_before,childAfter=shown_b,receipt=receipt)
  self.stable_capture('B',('A','C'));self.focus('B');self.pair('B');self.key('B');self.pair('A',blocked=True);self.focus('B');self.drafts(('A','B','C'),baseline)
 def QT08(self):
  self.send('open-nested');d=self.binding('D',False);self.send('close-nested');self.retired(d);b=self.binding('B',False);self.send('close-modal');self.retired(b);self.send('open-popup');a=self.binding('A',False);p=self.h.scene.current_role(self.actor.read(),'P');self.send('close-owner');self.retired(a);self.check('QT06/08:opener-popup-retirement',self.h.scene.current_role(self.actor.read(),'P') is None,oldPopup=p);self.pair('C');self.focus('C');self.key('C')
  before=self.binding('C',False);draft_start=self.interval_start();recovery=self.shell.reconnect(self.deadline);after=self.binding('C',False)
  self.check('QT08:actual-normal-EOF-physical-reconnect-preserves-C',before['identity']==after['identity'] and before['native']['address']==after['native']['address'],before=before,after=after,recovery=recovery)
  self.pair('C');self.focus('C');self.key('C');self.drafts(('C',),draft_start)
  self.report['faultCompanionRequired']='qa/fault-native.py: original controlled-XDG01–10 separately serialized; not QT journal or acceptance'
 def pair(self,role,*,blocked=False):
  b=self.binding(role);baseline=self.interval_start()
  if not blocked:
   expected=input_coordinates(b,b['marker']['global']);local=expected['window'];global_qt=expected['toolkitGlobal']
   if local!=b['marker']['window'] or expected['surface']!=b['marker']['surface']:raise Refused('marker and input measured inverse disagree')
  self.pointer_parent(b['marker']['global'])
  self.parent.send('press 272',self.deadline);self.parent.send('release 272',self.deadline);rows=self.inspect()
  if blocked:
   self.h.journal.blocked_raw_pointer_interval(rows,baseline)
   if self.h.journal.widget_input_observations(rows,baseline):raise Refused('blocked Qt pair reached a QWidget')
  else:
   self.h.journal.raw_pointer_interval(rows,baseline,role=role,instance=b['identity']['instance'],map_generation=b['identity']['mapGeneration'],surface_id=b['identity']['surfaceId'],event_types=self.types,qt_button=self.types['leftButton'],qt_mouse_source=self.types['mouseNotSynthesized'],modifiers=0,expected_local=local,expected_global=global_qt)
  self.check(self.phase+':entire-raw-QWindow-pointer-'+role,True,baseline=baseline,blocked=blocked,rows=rows,widgetPropagation=self.h.journal.widget_input_observations(rows,baseline),expectedCoordinates=expected if not blocked else None)
 def key(self,role,*,blocked=False):
  b=self.targets.get(role) if blocked else self.binding(role,False)
  if b is None:raise Refused('captured identity required for blocked keyboard interval')
  baseline=self.interval_start();wire_baseline=len(self.h.protocol.Trace(self.actor.stderr.read_bytes()).calls)
  self.parent.send('key-press 42',self.deadline);self.parent.send('key-release 42',self.deadline);rows=self.inspect()
  if blocked:
   if self.h.journal.interval(rows,baseline,('window-key-press','window-key-release')) or self.h.journal.widget_input_observations(rows,baseline):raise Refused('entire blocked Qt key interval leaked')
  else:
   wire=shift_pair(self.h.protocol.Trace(self.actor.stderr.read_bytes()),wire_baseline,surface_id=b['identity']['surfaceId'],xkb_shift_mask=self.h.keymap.xkb_shift_mask,qt_shift_mask=self.types['shiftModifier'],mapping=self.h.keymap.qt_mapping,seat_registry_id=self.h.keymap.seat_registry_id)
   self.h.journal.raw_key_interval(rows,baseline,role=role,instance=b['identity']['instance'],map_generation=b['identity']['mapGeneration'],surface_id=b['identity']['surfaceId'],event_types=self.types,qt_key=self.types['shiftKey'],native_scan=wire[0]['nativeScanCode'],native_virtual=wire[0]['nativeVirtualKey'],qt_modifiers=[v['qtModifiers'] for v in wire],native_modifiers=[v['nativeModifiers'] for v in wire])
   selected=self.h.journal.interval(rows,baseline,('window-key-press','window-key-release'))
   if any(row['qtTimestamp']!=value['time'] for row,value in zip(selected,wire)):raise Refused('actual Qt timestamp differs from admitted Wayland key')
  self.check(self.phase+':entire-raw-QWindow-key-'+role,True,baseline=baseline,rows=rows,widgetPropagation=self.h.journal.widget_input_observations(rows,baseline))
 def drafts(self,names,baseline):
  self.h.journal.integer(baseline,0,2**63-1);rows=self.inspect()
  for name in names:
   b=self.binding(name,False);current=b['identity'];matching=[r for r in rows if r['sequence']>baseline and r.get('role')==name and 'draftUTF8' in r]
   if not matching:raise Refused('actual current Qt draft evidence absent')
   for row in matching:
    if any(row.get(k)!=current[k] for k in ('instance','mapGeneration','surfaceId')):raise Refused('draft interval crosses resource/map lifetime')
    if row['draftUTF8']!='ELM-ROLE-DRAFT' or row['draftBytes']!=len(b'ELM-ROLE-DRAFT'):raise Refused('Qt draft sentinel changed')
 def QT04(self):
  self.place('C',420,90);self.stable_capture('C',('A','B'));baseline=self.interval_start()
  if self.actor.profile=='window-modal':self.role('C',None,False,False);self.pair('C');self.focus('C');self.key('C')
  else:
   self.pair('C',blocked=True);self.focus('B');self.key('B')
   self.check('QT04:fresh-explicit-application-modal-profile',self.actor.profile=='application-modal',profile=self.actor.profile,nativeRoles=self.native_roles())
  self.drafts(('A','B','C'),baseline)
 def QT05(self):
  self.send('open-nested');d=self.binding('D',False);self.role('D','B',True,False);self.role('B','A',True,True);self.pair('A',blocked=True);self.focus('D');self.send('close-nested');self.retired(d);self.role('B','A',True,False);self.pair('A',blocked=True);self.focus('B');self.key('B')
  original_b=self.binding('B',False);a=self.binding('A',False);c=self.binding('C',False);baseline=self.interval_start();request=self.send('reparent-modal','C');self.inspect();b=self.binding('B',False)
  self.check('QT05:actual-request-current-B-reparent-to-C',b['identity']['instance']==original_b['identity']['instance'] and b['identity']['mapGeneration']>original_b['identity']['mapGeneration'] and b['qt']['transientSurfaceId']==c['identity']['surfaceId'] and b['wire']['parentToplevel']==c['wire']['toplevelId'],before=original_b,after=b,request=request)
  self.role('B','C',True,False);self.pair('C',blocked=True);self.focus('B');self.key('B');self.send('close-owner');self.retired(a)
  after_c=self.binding('C',False);after_b=self.binding('B',False);self.check('QT05:new-family-retains-native-identities',c['identity']==after_c['identity'] and b['identity']==after_b['identity'] and c['native']['address']==after_c['native']['address'] and b['native']['address']==after_b['native']['address'] and c['wire']['surfaceEpoch']==after_c['wire']['surfaceEpoch'] and b['wire']['surfaceEpoch']==after_b['wire']['surfaceEpoch'],before=[c,b],after=[after_c,after_b]);self.role('B','C',True,False);self.focus('B');self.key('B')
  # Recreate an independent A under a new actual lifetime, and return B to it
  # for popup and integrated whole-family operations in following phases.
  self.send('open-owner');new_a=self.binding('A',False)
  self.check('QT05:replacement-owner-is-new-local-native-lifetime',new_a['identity']['instance']!=a['identity']['instance'],old=a,replacement=new_a)
  self.send('reparent-modal','A');self.role('B','A',True,False);self.place('A',40,90);self.place('B',240,320)
  a=self.binding('A');b=self.binding('B',False);baseline=self.interval_start();self.pointer_parent(a['marker']['global']);self.parent.send('press 272',self.deadline);self.send('close-modal');self.retired(b);self.parent.send('release 272',self.deadline);rows=self.inspect();self.h.journal.blocked_raw_pointer_interval(rows,baseline)
  if self.h.journal.widget_input_observations(rows,baseline):raise Refused('held-modal retirement leaked QWidget input')
  self.check('QT05:entire-held-modal-retirement-no-raw-release-leak',True,rows=rows)
 def QT06(self):
  self.send('open-popup');self.shell.popup_guard(self.actor,self.parent,self.session,self.deadline)

 def run(self):
  self.native_pid=next(row['pid'] for _,row in self.session.host.processes if row['name']=='hyprland');self.native_start=Path('/proc',str(self.native_pid),'stat').read_text().rsplit(')',1)[1].split()[19]
  try:
   for phase in PHASES:
    self.phase=phase;self.deadline=time.monotonic()+6;self.session.deadline=self.deadline;self.endpoint.parentDeadline=self.deadline;record={'name':phase,'deadline':self.deadline,'passed':False};self.report['phases'].append(record);self.persist()
    self.parent=self.parent_factory(self.deadline)
    try:getattr(self,phase)();remaining(self.deadline);self.parent.close(self.deadline);remaining(self.deadline);record['passed']=True
    finally:
     if not record['passed']:self.parent.abort()
    self.persist()
   self.report['passed']=True;self.report['fullCampaignPassed']=not self.report['openGates'];self.report['nativeAcceptance']=False;self.report['nativeOraclesCompleted']=self.report['fullCampaignPassed']
  except BaseException as error:self.report['error']=repr(error);raise
  finally:self.persist()
  return self.report
