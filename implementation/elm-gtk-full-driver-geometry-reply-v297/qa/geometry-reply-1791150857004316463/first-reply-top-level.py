"""Full GTK01–08 imperative orchestration; resources acquired by reviewed root launcher."""
import json,time
from keyboard import shift_pair
from pathlib import Path
class Refused(ValueError):pass
PHASES=tuple('GTK%02d'%i for i in range(1,9))
def remaining(deadline):
 value=deadline-time.monotonic()
 if value<=0:raise Refused('Original absolute six-second GTK phase deadline')
 return value
class Driver:
 def __init__(self,actor,session,host,endpoint,parent_factory,shell,helpers,event_types,directory):
  self.actor=actor;self.session=session;self.host=host;self.endpoint=endpoint;self.parent_factory=parent_factory;self.shell=shell;self.h=helpers;self.types=event_types;self.directory=Path(directory);self.directory.mkdir(mode=0o700,parents=True,exist_ok=False);self.read_id=0;self.report={'passed':False,'fullCampaignPassed':False,'nativeAcceptance':False,'phases':[],'checks':[],'openGates':[]};self.parent=None;self.shell.driver=self
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
  bound=self.binding(role,False);self.read_id+=1;snapshot=self.endpoint.snapshot(str(self.read_id));remaining(self.deadline)
  identities=[w for w in snapshot['windows'] if w['label']==f'ELM-GTK4-{role}-{self.actor.pid}']
  if len(identities)!=1:raise Refused('exact native GTK projection identity')
  matches=[w for w in self.observe()['facts']['windows'] if w['incarnation']==identities[0]['incarnation']]
  if len(matches)!=1:raise Refused('exact current full native window fact')
  return matches[0]
 def binding(self,role,landmark=True):return self.wait(lambda:self.h.scene.bind(self.actor,self.session,role,require_landmark=landmark))
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
   value=self.session.ctl('eval','local r=hl.dispatch('+expression+');if type(r)~="table" or r.ok~=true then error("GTK fixture placement refused") end').strip()
   if value!='ok':raise Refused('actual structured native placement result')
  def current():return next((row for row in self.session.data('clients') if row['address']==address and row['pid']==self.actor.pid),None)
  dispatch('hl.dsp.window.float({action="enable",window='+selector+'})');self.wait(lambda:current() if current() and current()['floating'] else None)
  dispatch('hl.dsp.window.resize({x='+str(w)+',y='+str(h)+',window='+selector+'})');resized=self.wait(lambda:current() if current() and current()['size']==[w,h] else None)
  dx=x-resized['at'][0];dy=y-resized['at'][1]
  dispatch('hl.dsp.window.move({x='+str(dx)+',y='+str(dy)+',relative=true,window='+selector+'})');self.wait(lambda:current() if current() and current()['at']==[x,y] else None)
  self.inspect();after=self.binding(name);self.h.scene.same(b,after);return after
 def stable_capture(self,name,others=()):
  before=self.binding(name);census=self.session.data('clients');popup=json.loads(self.session.ctl('elm_popup_state'))
  bindings={r:self.binding(r) for r in others};exclusions=[self.h.geometry.attribution(before,b) for b in bindings.values()]
  directory=self.directory/(self.phase+'-'+name+'-'+str(time.time_ns()))
  data,measurement=self.h.pixels.capture(self.session,self.host,directory,self.deadline,selected={'binding':before,'census':census,'popup':popup,'otherBindings':bindings,'exclusions':exclusions})
  samples=self.h.pixels.yellow_marker(data,before['marker']['global']);measurement['markerSamples']=samples
  (directory/'record.json').write_text(json.dumps(measurement,indent=2)+'\n')
  self.inspect();after=self.binding(name);self.h.scene.same(before,after)
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
 def pair(self,role,*,blocked=False):
  b=self.binding(role);baseline=self.interval_start();self.pointer_parent(b['marker']['global'])
  self.parent.send('press 272',self.deadline);self.parent.send('release 272',self.deadline);rows=self.inspect()
  if blocked:self.h.journal.blocked_interval(rows,baseline)
  else:self.h.journal.full_pointer_interval(rows,baseline,role=role,**dict(instance=b['identity']['instance'],map_generation=b['identity']['mapGeneration'],surface_id=b['identity']['surfaceId']),expected_surface=b['marker']['surface'],event_types=self.types,button=1)
  self.check(self.phase+':full-pointer-'+role,True,baseline=baseline,blocked=blocked,rows=rows)
 def key(self,role,*,blocked=False):
  b=self.binding(role,False);baseline=self.interval_start();wire_baseline=len(self.h.protocol.Trace(self.actor.stderr.read_bytes()).calls);self.parent.send('key-press 42',self.deadline);self.parent.send('key-release 42',self.deadline);rows=self.inspect()
  if blocked:self.h.journal.blocked_key_interval(rows,baseline)
  else:
   # Qualified247 Shift_L generates no document text. Preserve the entire interval
   # and expected before/after XKB state instead of filtering a favorable key pair.
   selected=[r for r in rows if r['sequence']>baseline and r['event'] in ('key-press','key-release')]
   if len(selected)!=2:raise Refused('entire nontext keyboard interval exact pair')
   wire=shift_pair(self.h.protocol.Trace(self.actor.stderr.read_bytes()),wire_baseline,surface_id=b['identity']['surfaceId'],xkb_shift_mask=self.h.keymap.xkb_shift_mask,gdk_shift_mask=self.h.keymap.gdk_shift_mask)
   for row,event,raw in zip(selected,('key-press','key-release'),wire):
    mods=raw['gdkModifiers']
    self.h.journal.recipient(row,event,role,b['identity']['instance'],b['identity']['mapGeneration'],b['identity']['surfaceId'],self.types)
    for field,expected in [('keyval',65505),('rawKeyval',65505),('keycode',50),('rawKeycode',50),('modifiers',mods),('rawModifiers',mods)]:
     if type(row.get(field)) is not int or row[field]!=expected:raise Refused('exact owning Shift_L raw key/domain state')
    if row.get('rawEventTime')!=raw['time']:raise Refused('actual GDK event time differs from current owning Wayland key')
  self.check(self.phase+':full-key-'+role,True,baseline=baseline,rows=rows)
 def drafts(self,names,baseline):
  rows=self.inspect();ids={r:self.identity(self.binding(r,False)) for r in names};self.h.journal.stable_drafts(rows,baseline,{r:'ELM-ROLE-DRAFT' for r in names},ids)
 def retired(self,old):
  def gone():
   self.actor.read();current=self.h.scene.current_role(self.actor.rows,old['identity']['role'])
   clients=self.session.data('clients')
   return current is None and not any(w['address']==old['native']['address'] and w['pid']==self.actor.pid for w in clients)
  self.wait(gone);self.check(self.phase+':actual-role-retired-'+old['identity']['role'],True,old=old)
 def GTK01(self):
  self.send('create-owners');a=self.place('A',40,90);c=self.place('C',420,90)
  self.check('GTK01:unique-native-resources',a['identity']['surfaceId']!=c['identity']['surfaceId'] and a['native']['address']!=c['native']['address'])
  self.stable_capture('C',('A',));self.pair('C');self.focus('C');self.key('C');self.drafts(('A','C'),0)
  # Measured overlap: C placed over A, selected actual opaque landmark must contribute.
  a=self.place('A',40,90);c=self.place('C',60,110);self.stable_capture('C');self.pair('C');self.focus('C');self.key('C')
 def GTK02(self):
  ordinary=self.fact('A');before=self.binding('A');self.read_id+=1;g=self.endpoint.geometry_facts(str(self.read_id));remaining(self.deadline)
  window=next(w for w in g['windows'] if w['incarnation']==ordinary['incarnation']);self.report['geometryOrdinary']=window
  if not window['capabilities']['maximize']:
   self.shell.refuse_unavailable(before,ordinary['incarnation'],'maximize',self.deadline)
   after=self.fact('A');self.check('GTK02:unsupported-effect2-no-native-mutation',all(ordinary[k]==after[k] for k in ('geometry','workspace','monitor','incarnation','minimized','shouldRenderAny','shouldRenderOwnMonitor','acceptsInput')),before=ordinary,after=after)
   self.report['openGates'].append('GTK02 actual geometryEffect2 MAX/restore capability unavailable')
  else:
   receipt=self.shell.invoke(f'ELM-GTK4-A-{self.actor.pid}',ordinary['incarnation'],'maximize',self.deadline)
   self.wait(lambda:self.binding('A',False) if self.binding('A',False)['gtk'].get('observedMaximized') is True else None)
   self.stable_capture('A',('C',));restored=self.shell.invoke(f'ELM-GTK4-A-{self.actor.pid}',ordinary['incarnation'],'restore-geometry',self.deadline);after=self.fact('A')
   self.check('GTK02:effect2-exact-ordinary-restored',all(after[k]==ordinary[k] for k in ['geometry','workspace','monitor','incarnation']),before=ordinary,after=after,receipts=[receipt,restored])
  # Mandatory standard toolkit protocol is independent of experiment capability.
  standard_before=self.binding('A');prior_shell=self.shell.journal();self.send('maximize','A')
  maximized=self.wait(lambda:self.binding('A') if self.binding('A')['gtk'].get('observedMaximized') is True else None)
  self.read_id+=1;geo=self.endpoint.geometry_facts(str(self.read_id));remaining(self.deadline);actual=next(w for w in geo['facts']['windows'] if w['incarnation']==ordinary['incarnation'])
  self.check('GTK02:actual-standard-GTK-MAX',actual['nativeMode']==actual['clientMode']=='maximized' and maximized['wire']['ack']['serial']!=standard_before['wire']['ack']['serial'] and self.shell.journal()==prior_shell,before=standard_before,after=maximized,native=actual)
  self.stable_capture('A',('C',));self.send('unmaximize','A')
  standard_after=self.wait(lambda:self.binding('A') if self.binding('A')['gtk'].get('observedMaximized') is False and self.binding('A')['native']['at']==standard_before['native']['at'] and self.binding('A')['native']['size']==standard_before['native']['size'] else None)
  self.check('GTK02:standard-restores-original-position-size',standard_before['native']['at']==standard_after['native']['at'] and standard_before['native']['size']==standard_after['native']['size'] and standard_before['native']['workspace']==standard_after['native']['workspace'] and standard_before['native']['monitor']==standard_after['native']['monitor'] and self.shell.journal()==prior_shell,before=standard_before,after=standard_after)
  self.stable_capture('A',('C',));self.drafts(('A','C'),0)
 def GTK03(self):
  self.send('open-modal');self.role('B','A',True,False);self.role('A',None,False,True);self.place('B',240,320)
  baseline=self.interval_start();self.pair('A',blocked=True);self.focus('B');self.key('B');self.drafts(('A','B','C'),baseline)
 def GTK04(self):
  self.place('C',420,90);self.role('C',None,False,False);self.stable_capture('C',('A','B'));baseline=self.interval_start()
  if self.actor.profile=='independent-groups':self.pair('C');self.focus('C');self.key('C')
  else:
   self.pair('C',blocked=True);self.key('B');self.report['openGates'].append('Default-group toolkit-global suppression is distinct from native peer eligibility')
  self.drafts(('A','B','C'),baseline)
 def GTK05(self):
  self.send('open-nested');d=self.binding('D',False);self.role('D','B',True,False);self.role('B','A',True,True);self.pair('A',blocked=True);self.focus('D');self.send('close-nested');self.retired(d);self.role('B','A',True,False);self.pair('A',blocked=True);self.focus('B');self.key('B')
  self.send('open-sibling');e=self.binding('E',False);b=self.binding('B',False);baseline=self.interval_start();request=self.send('reparent-sibling','B');rows=self.inspect()
  self.h.journal.gtk_parent_relation(rows,baseline,request_sequence=request['sequence'],parent_role='B',child_identity=self.identity(e),parent_identity=self.identity(b));self.role('E','B',True,False);self.pair('A',blocked=True);self.focus('E');self.key('E')
  self.send('reparent-sibling','A');self.role('E','A',True,False);self.pair('A',blocked=True);self.focus('E');self.key('E');self.send('close-sibling');self.retired(e)
  # Continuous held press survives modal retirement; no newly eligible recipient release.
  a=self.binding('A');b=self.binding('B',False);baseline=self.interval_start();self.pointer_parent(a['marker']['global']);self.parent.send('press 272',self.deadline);self.send('close-modal');self.retired(b);self.parent.send('release 272',self.deadline);rows=self.inspect();self.h.journal.blocked_interval(rows,baseline);self.check('GTK05:entire-held-retirement-interval-no-release-leak',True,rows=rows)
 def GTK06(self):
  self.send('open-popover');self.shell.popup_guard(self.actor,self.parent,self.session,self.deadline)
  # popup_guard executes actual parent click on measured popup-button bounds,
  # checks raw xdg parent/grab/native popup, exact key/input and normal button closure.
 def GTK07(self):
  if self.h.scene.current_role(self.actor.read(),'B') is None:self.send('open-modal')
  self.place('B',240,320);self.place('C',420,90);self.role('B','A',True,False)
  baseline=self.interval_start();ordinary=self.fact('A');child_before=self.fact('B');c=self.fact('C');bounds={r:self.binding(r) for r in ('A','B')}
  for name in ('A','B'):self.stable_capture(name,tuple(r for r in ('A','B','C') if r!=name))
  receipt=self.shell.invoke(f'ELM-GTK4-A-{self.actor.pid}',ordinary['incarnation'],'minimize',self.deadline)
  hidden=self.wait(lambda:self.fact('A') if self.fact('A')['minimized'] else None);hidden_b=self.wait(lambda:self.fact('B') if self.fact('B')['minimized'] else None)
  for name,fact in [('A',hidden),('B',hidden_b)]:self.check('GTK07:actual-native-hidden-'+name,not fact['shouldRenderAny'] and not fact['shouldRenderOwnMonitor'] and not fact['acceptsInput'],fact=fact,receipt=receipt)
  self.shell.family_hidden_pixels(bounds,self.deadline)
  # Complete pointer/key intervals over hidden family regions. Native focus
  # determines whether the legitimate remaining C receives the nontext key.
  start=self.interval_start();self.pointer_parent(bounds['A']['marker']['global']);self.parent.send('press 272',self.deadline);self.parent.send('release 272',self.deadline);rows=self.inspect();self.h.journal.blocked_interval(rows,start)
  focus=json.loads(self.session.ctl('elm_held_state'))['focus'];c_binding=self.binding('C',False)
  if focus['surfaceId'] in [bounds[r]['identity']['surfaceId'] for r in ('A','B')]:raise Refused('hidden family retains keyboard recipient')
  if focus['surfaceClientPID']==self.actor.pid and focus['surfaceId']==c_binding['identity']['surfaceId']:self.key('C')
  else:self.key('A',blocked=True)
  all_rows=self.actor.read();self.check('GTK07:whole-hidden-interval-no-family-input',not any(row['sequence']>start and row.get('role') in ('A','B') and row['event'] in ('button-press','button-release','key-press','key-release') for row in all_rows),rows=all_rows,nativeFocus=focus)
  receipt=self.shell.invoke(f'ELM-GTK4-A-{self.actor.pid}',ordinary['incarnation'],'restore',self.deadline);shown=self.wait(lambda:self.fact('A') if not self.fact('A')['minimized'] else None);shown_b=self.wait(lambda:self.fact('B') if not self.fact('B')['minimized'] else None)
  stable=['geometry','workspace','monitor','incarnation','minimized','shouldRenderAny','shouldRenderOwnMonitor','acceptsInput']
  self.check('GTK07:restored-owner-child-and-independent-peer',shown['workspace']==ordinary['workspace'] and shown['monitor']==ordinary['monitor'] and shown_b['acceptsInput'] and all(c[k]==self.fact('C')[k] for k in stable),ownerBefore=ordinary,ownerAfter=shown,childBefore=child_before,childAfter=shown_b,receipt=receipt)
  self.stable_capture('B',('A','C'));self.focus('B');self.pair('B');self.key('B');self.pair('A',blocked=True);self.focus('B');self.drafts(('A','B','C'),baseline)
 def GTK08(self):
  self.send('open-nested');d=self.binding('D',False);self.send('close-nested');self.retired(d);b=self.binding('B',False);self.send('close-modal');self.retired(b);self.send('open-popover');a=self.binding('A',False);p=self.h.scene.current_role(self.actor.read(),'P');self.send('close-owner');self.retired(a);self.check('GTK06/08:opener-popup-retirement',self.h.scene.current_role(self.actor.read(),'P') is None,oldPopup=p);self.pair('C');self.focus('C');self.key('C')
  before=self.binding('C',False);draft_start=self.interval_start();recovery=self.shell.reconnect(self.deadline);after=self.binding('C',False)
  self.check('GTK08:actual-normal-EOF-physical-reconnect-preserves-C',before['identity']==after['identity'] and before['native']['address']==after['native']['address'],before=before,after=after,recovery=recovery)
  self.pair('C');self.focus('C');self.key('C');self.drafts(('C',),draft_start)
  self.report['faultCompanionRequired']='qa/fault-native.py: original controlled-XDG01–10 separately serialized; not GTK journal or acceptance'
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
