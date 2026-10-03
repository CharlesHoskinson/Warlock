"""Source proposal: B01–B12 owning/input subsets only. No entry point and no implicit GUI/native launch."""
from pathlib import Path
import importlib.util,json,os,time,math,stat

V2=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v2')
CORE=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
HERE=Path(__file__).resolve().parent.parent
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def require(ok,message):
 if ok is not True:raise ValueError(message)

class MinimalController:
 def __init__(self,session,output,pair_path,frozen):
  self.session=session;self.output=Path(output);self.pair_path=Path(pair_path);self.frozen=frozen;self.trace=[];self.identity={};self.sequence=0;self.blocked=False
  # These imports occur only on explicit construction by a later reviewed root collector.
  self.authority=module('_b_original_token',V2/'case_authority.py')
  # input_episode imports original case_authority; bind its exact immutable location.
  import sys
  sys.path.insert(0,str(V2))
  try:self.episode=module('_b_original_episode',V2/'input_episode.py')
  finally:sys.path.pop(0)
  self.helper=module('_b_v3_exact_report_decoder',CORE/'helper/pin_helper.py')
  self.binding=module('_b_v2_exact_binding',V2/'proposed/pair_binding.py')
  self.decoder=module('_b_draft_observation_decoder',HERE/'observer/decode_observation.py')
  self.registry_module=module('_b_draft_registry',HERE/'producer-registry/registry.py')
  require(self.output.is_absolute()and self.output.resolve()==self.output and self.output.is_dir()and not self.output.is_symlink()and self.output.stat().st_uid==os.getuid()and stat.S_IMODE(self.output.stat().st_mode)==0o700,'exact current owned private0700 controller output')
  self.registry=self.registry_module.Registry(session,self.output,frozen)
  self.root=dict(compositorPid=session.evidence['compositorPID'],compositorPgid=session.evidence['compositorPGID'],compositorStart=session.evidence['compositorStart'],session=session.evidence['signature'])
 def persist(self):
  target=self.output/'campaign-b-trace.json';temporary=self.output/'campaign-b-trace.new'
  require(not target.is_symlink(),'no trace alias')
  with temporary.open('x')as f:
   json.dump(dict(trace=self.trace,blocked=self.blocked,original14Credit=False,maxPolicyAccepted=False),f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
  temporary.chmod(0o600);temporary.replace(target)
  fd=os.open(self.output,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:os.fsync(fd)
  finally:os.close(fd)
 def raw(self,label,fn):
  require(not self.blocked and len(self.trace)<4096,'bounded current source-only review protocol')
  row=dict(label=label,startedNs=time.monotonic_ns());self.trace.append(row);self.persist()
  try:
   self.session.guard();row['value']=fn();row['completedNs']=time.monotonic_ns();self.persist();return row['value']
  except BaseException as error:
   row['error']=repr(error);self.blocked=True;self.persist();raise
 def attest(self,phase):
  pair=self.raw('actual completed source pair '+phase,lambda:self.binding.read_pair(self.pair_path))
  observer=Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-observer-v2-build/build/libpin-campaign-b-observer.so')
  require(pair.get('observerBuildComplete')is True and pair.get('observer')==str(observer)and pair['inputs'].get(str(observer))=='3aa57212f976039fdeb89444fb68151231d97f7a41cdfed85b7449e9200f8f42'and type(pair['inputModes'].get(str(observer)))is int and pair['inputModes'][str(observer)]==0o755,'exact root-reviewed completed observer required')
  value=self.raw('actual root/modules '+phase,lambda:self.binding.attest(self.session,pair,phase,(pair['plugin'],pair['probe'],pair['observer'])))
  require(value['passed']is True,'actual source-bound owned core/plugin/old probe/new observer')
  return pair
 def query(self,name):
  require(name in {'pin_capture','pin_events','pin_stack_state','pin_bar_state'},'fixed native product read/query')
  require(name!='pin_capture','capture requires typed selected lifetime')
  return self.raw('actual product '+name,lambda:self.helper.strict_json(self.session.ctl('repl','print(hl.plugin.hyprbars.'+name+'())')))
 def old_probe(self,name):
  require(name in {'state','keyboard_state','events','keyboard_events'},'unchanged diagnostic probe query')
  return self.raw('actual unchanged probe '+name,lambda:self.helper.strict_json(self.session.ctl('repl','print(hl.plugin.qt_modal_probe.'+name+'())')))
 def public(self,actor,title='owner'):
  clients=self.raw('actual current public clients',lambda:self.session.data('clients'))
  require(actor['proc'].poll()is None and self.registry_module.lifetime(actor['proc'].pid)['start']==actor['row']['registered']['start'],'same current Qt actor')
  rows=[r for r in clients if type(r)is dict and type(r.get('pid'))is int and r['pid']==actor['proc'].pid and r.get('title')=='Qt WindowModal QA '+title]
  require(len(rows)==1,'one genuine current Qt member')
  row=rows[0];key={k:row[k]for k in ['address','stableId','pid']};old=self.identity.setdefault((actor['proc'].pid,title),key)
  require(self.decoder.exact(old,key),'no replacement lifetime selection')
  return row
 def capture(self,actor,title='owner'):
  row=self.public(actor,title);public={k:row[k]for k in ['address','stableId','pid']}
  command='print(hl.plugin.hyprbars.pin_capture({address='+json.dumps(public['address'])+',stableId='+json.dumps(public['stableId'])+',pid='+str(public['pid'])+'}))'
  value=self.authority.token(self.raw('actual complete captured product receipt',lambda:self.helper.strict_json(self.session.ctl('repl',command))))
  require(self.decoder.exact(self.authority.public(value),public)and value['compositorPid']==self.root['compositorPid']and value['compositorStart']==self.root['compositorStart']and value['session']==self.root['session'],'captured same root/member')
  return value
 def await_capture(self,actor,title):
  def current():
   clients=self.raw('actual pending current public member',lambda:self.session.data('clients'))
   rows=[r for r in clients if type(r)is dict and type(r.get('pid'))is int and r['pid']==actor['proc'].pid and r.get('title')=='Qt WindowModal QA '+title]
   if not rows:
    require((actor['proc'].pid,title)not in self.identity,'previous accepted member disappeared')
    return None
   require(len(rows)==1,'ambiguous current public member refuses')
   return self.capture(actor,title)
  return self.wait('actual complete public '+title+' receipt',current)
 def snapshot(self,captured,mask=None,ignore=False):
  self.attest('before-read')
  self.decoder.boolean(ignore)
  args=json.dumps(captured['address'])+','+json.dumps(captured['stableId'])+','+str(captured['pid'])
  if mask is None:
   require(ignore is False,'pure metadata has no ignored-owner query');function='observe'
  else:
   self.decoder.integer(mask,0,4);function='query_hit';args+=','+str(mask)+','+('true'if ignore else'false')
  command='print(hl.plugin.pin_campaign_b.'+function+'('+args+'))'
  raw=self.raw('actual new owning read',lambda:self.session.ctl('repl',command))
  value=self.decoder.decode(raw.encode(),self.root,captured,mask,ignore)
  require(int(value['sequence'])>self.sequence,'new current observation, no replay')
  self.sequence=int(value['sequence']);self.attest('after-owning-read');return value
 def scene(self,captured):
  return dict(clients=self.raw('actual scene public',lambda:self.session.data('clients')),native=self.old_probe('state'),seat=self.old_probe('keyboard_state'),stack=self.query('pin_stack_state'),owned=self.snapshot(captured))
 def wait(self,label,fn,seconds=5):
  deadline=time.monotonic()+seconds
  while time.monotonic()<deadline:
   value=fn()
   if value:return value
   time.sleep(.04)
  raise TimeoutError('Original bounded observation: '+label)
 def setup(self,label,command):
  require(type(command)is str and any(command.startswith(prefix)for prefix in ['hl.dsp.window.float(', 'hl.dsp.window.fullscreen(', 'hl.dsp.window.set_prop(', 'hl.dsp.focus(']),'fixed reviewed Lua fixture preparation')
  self.attest('before-setup')
  # Actual dispatcher object is evaluated through hl.dispatch, never passed as
  # an untyped legacy dispatcher name. Result is preparation only.
  lua='local r=hl.dispatch('+command+' ); if type(r)~="table" or type(r.ok)~="boolean" or r.ok~=true or type(r.pass_event)~="boolean" then error("B preparation refused") end; print(\'{"ok":\'..tostring(r.ok)..\',"pass_event":\'..tostring(r.pass_event)..\'}\')'
  row=self.raw('explicit Lua preparation only '+label,lambda:self.session.ctl('repl',lua))
  result=self.helper.strict_json(row)
  require(type(result)is dict and set(result)=={'ok','pass_event'}and result['ok']is True and type(result['pass_event'])is bool,'exact typed preparation result; no feature authority')
  return result
 def launch_actor(self,case,ordinal=1):
  require(case in {'B%02d'%i for i in range(1,13)},'fixed reachable B01–B12 proposal only')
  self.attest('before-private-actor')
  actors=self.output/'actors';actors.mkdir(mode=0o700,exist_ok=True)
  parent=actors/case;parent.mkdir(mode=0o700,exist_ok=True)
  for directory in [actors,parent]:require(not directory.is_symlink()and directory.resolve()==directory and stat.S_IMODE(directory.stat().st_mode)==0o700,'literal private actor output ancestors')
  folder=parent/('qt-'+str(ordinal));folder.mkdir(mode=0o700,exist_ok=False)
  proc,row=self.registry.launch(case,'qt',ordinal,actor_output=folder)
  actor=dict(proc=proc,row=row,output=folder,epoch=0)
  def ready():
   def sample():
    require(proc.poll()is None,'current Qt actor during readiness')
    p=folder/'state.json'
    return self.helper.strict_json(p.read_bytes())if p.exists()else None
   state=self.raw('actual pending/ready Qt state',sample)
   if state is None:return None
   require(type(state)is dict and type(state.get('windows'))is dict and type(state.get('pid'))is int and state['pid']==proc.pid and state.get('platform')=='wayland'and state.get('qtVersion')=='6.11.2','real exact source-bound Qt readiness')
   return state if all(type(state['windows'].get(name))is dict and state['windows'][name].get('visible')is True and state['windows'][name].get('native')is True for name in ['owner','peer'])else None
  self.wait('actual private actor ready',ready)
  current=self.await_capture(actor,'owner');self.await_capture(actor,'peer')
  if case in {'B01','B05'}:
   self.setup('explicit ordinary floating preparation before native MAX','hl.dsp.window.float({action="set",window='+json.dumps('address:'+current['address'])+'})')
   self.wait('actual floating preparation',lambda:self.public(actor)if self.public(actor).get('floating')is True else None)
  else:require(self.public(actor).get('floating')is False,'actual tiled origin without arrange()/float')
  return actor
 def retire_actor(self,actor):
  # Independent normal owned-client channel; works after a feature refusal.
  self.session.guard();proc=actor['proc'];row=actor['row']
  require(proc.poll()is None and self.registry_module.lifetime(proc.pid)['start']==row['registered']['start'],'same exact live actor before explicit quit')
  actor['epoch']+=1;folder=actor['output'];p=folder/'command.new'
  with p.open('x')as out:json.dump(dict(epoch=actor['epoch'],command='quit'),out);out.write('\n');out.flush();os.fsync(out.fileno())
  p.replace(folder/'command.json');proc.wait(timeout=8)
  events=[self.helper.strict_json(line)for line in (folder/'events.jsonl').read_bytes().splitlines()]
  require(any(type(e)is dict and e.get('event')=='commandHandled'and e.get('command')=='quit'and type(e.get('epoch'))is int and e['epoch']==actor['epoch']for e in events),'genuine same-epoch Qt quit callback')
  receipt=dict(kind='qt-quit',pid=proc.pid,commandEpoch=actor['epoch'],commandHandled=True,eventLogSHA256=self.registry_module.sha(folder/'events.jsonl'),stateSHA256=self.registry_module.sha(folder/'state.json'))
  self.registry.terminal(proc,row,timeout=8,receipt=receipt)
 def focus(self,actor,captured):
  self.setup('current fixture focus','hl.dsp.focus({window='+json.dumps('address:'+captured['address'])+'})')
  def accepted():
   native=self.old_probe('state');seat=self.old_probe('keyboard_state')
   return (native,seat)if self.authority.matches(native.get('nativeFocus'),captured)and self.authority.matches(seat.get('keyboardOwner'),captured)and seat.get('keyboardSurfacePresent')is True and seat.get('keyboardResourcePresent')is True else None
  self.wait('actual core and distinct Seat',accepted)
 def pin_keyboard(self,case,actor,ordinal,title='owner'):
  captured=self.capture(actor,title);self.focus(actor,captured);before=self.scene(captured)
  self.authority.input_safe(before['native']);require(before['stack'].get('keyboardPresent')is True and type(before['stack'].get('keyboardModifiers'))is int and before['stack']['keyboardModifiers']==0,'actual keyboard/zero modifiers')
  input_before=self.old_probe('keyboard_events');native_before=self.query('pin_events')
  self.attest('before-genuine-keyboard')
  proc,row=self.registry.launch(case,'key',ordinal,route='super-p')
  proc.wait(timeout=4)
  def complete():
   inputs=self.old_probe('keyboard_events');delivery=self.episode.episode(input_before,inputs,'super-p',captured,allow_pending=True)
   if delivery is None:return None
   events=self.query('pin_events')
   require(self.decoder.exact(events[:len(native_before)],native_before),'exact immutable native report prefix')
   if len(events)==len(native_before):return None
   require(len(events)==len(native_before)+1,'exactly one native pin result, no retry')
   report=self.helper.decode(json.dumps(events[-1],separators=(',',':'),allow_nan=False).encode(),self.decoder.POLICY)
   require(report['ok']is True and self.decoder.exact(report['captured'],captured),'actual native successful complete same capture')
   return delivery,report
  delivery,report=self.wait('actual native report after real delivery/release',complete)
  self.registry.terminal(proc,row,timeout=4,receipt=dict(kind='physical-chord',route='super-p',captured=captured,delivery=delivery))
  after=self.scene(captured);current=self.capture(actor,title)
  require(self.decoder.exact(current,captured),'post-input exact full lifetime/epoch')
  self.check_peers(before,after,captured)
  for k in ['nativeFocus']:
   require(self.decoder.exact(before['native'][k],after['native'][k]),'no pin-driven core focus change')
  for k in ['keyboardOwner','keyboardSurfacePresent','keyboardResourcePresent']:
   require(self.decoder.exact(before['seat'][k],after['seat'][k]),'no pin-driven Seat change')
  require(type(after['stack'].get('keyboardModifiers'))is int and after['stack']['keyboardModifiers']==0,'all physical keys released')
  self.trace.append(dict(genuineInputComplete=True,before=before,after=after,receipt=report,nativeAcceptedOnlyForThisTransition=True,original14Credit=False));self.persist()
  return report,after
 def native_max_case(self,case,actor):
  require(case in {'B04','B05'},'only two positive native MAX cases implemented in this draft')
  captured=self.capture(actor);normal=self.snapshot(captured)['body'];require(normal['internalMode']==0 and normal['clientMode']==0,'actual ordinary initial modes')
  require(normal['floating']is (case=='B05'),'actual intended tiled/floating origin, never force floating in tiled case')
  self.focus(actor,captured)
  target=json.dumps('address:'+captured['address'])
  self.setup('actual native MAX set','hl.dsp.window.fullscreen({mode="maximized",action="set",layout_aware=true,window='+target+'})')
  def max_ready():
   value=self.snapshot(self.capture(actor));return value if value['body']['internalMode']==1 and value['body']['restoreValid']is True else None
  maximum=self.wait('actual owning native MAX',max_ready)
  first,first_after=self.pin_titlebar(case,actor,1)if case=='B04'else self.pin_keyboard(case,actor,1)
  conserved=['internalMode','clientMode','floating','logicalBox','visualBox','restoreValid','restoreGeneration','restoreLogicalBox','restoreVisualBox','restoreFloating','restoreLayoutHandled','restoreTarget','restoreLayoutTarget','restoreSpace','target','space','workspace','output']
  require(all(self.decoder.exact(maximum['body'][k],first_after['owned']['body'][k])for k in conserved),'native MAX context conserved immediately after genuine pin')
  require(first_after['owned']['body']['restoreOrigin']is True and first_after['owned']['body']['restoreManaged']is True,'exact native MAX pin-origin and managed markers immediately after genuine pin')
  second,second_after=self.pin_titlebar(case,actor,2)if case=='B04'else self.pin_keyboard(case,actor,2)
  require(all(self.decoder.exact(maximum['body'][k],second_after['owned']['body'][k])for k in conserved),'native MAX context conserved immediately after genuine unpin')
  require(second_after['owned']['body']['restoreOrigin']is False and second_after['owned']['body']['restoreManaged']is True,'exact native MAX unpin-origin and managed markers immediately after genuine unpin')
  require(first['after']['pinned']is True and second['after']['pinned']is False,'actual pin then unpin while native MAX')
  current=self.snapshot(self.capture(actor))['body']
  require(all(self.decoder.exact(maximum['body'][k],current[k])for k in conserved),'actual native mode/owning MAX conservation')
  require(current['restoreOrigin']is False and current['restoreManaged']is True,'exact native MAX unpin-origin and managed markers at final observation')
  self.setup('actual native MAX unset','hl.dsp.window.fullscreen({mode="maximized",action="unset",layout_aware=true,window='+target+'})')
  def returned():
   value=self.snapshot(self.capture(actor));return value if value['body']['internalMode']==0 else None
  after=self.wait('actual native normal return',returned)['body']
  require(after['floating']is normal['floating']and self.decoder.exact(after['logicalBox'],normal['logicalBox'])and self.decoder.exact(after['visualBox'],normal['visualBox'])and after['clientMode']==normal['clientMode'],'exact actual normal/floating return and client mode')
  self.trace.append(dict(case=case,nativeMaxReturnObserved=True,original14Credit=False,normal=normal,maximum=maximum['body'],returned=after));self.persist()
 def fixture_state(self,actor):
  value=self.raw('actual current Qt state',lambda:self.helper.strict_json((actor['output']/'state.json').read_bytes()))
  require(type(value.get('pid'))is int and value['pid']==actor['proc'].pid and value.get('platform')=='wayland','current genuine actor state')
  return value
 def fixture_command(self,actor,command):
  require(command in {'open','nested','closeNested','closeChild'},'fixed real Qt commands')
  self.session.guard();self.attest('before-Qt-command');actor['epoch']+=1;epoch=actor['epoch'];path=actor['output']/'command.new'
  with path.open('x')as f:json.dump(dict(epoch=epoch,command=command),f);f.write('\n');f.flush();os.fsync(f.fileno())
  path.replace(actor['output']/'command.json')
  def done():
   state=self.fixture_state(actor)
   return state if type(state.get('commandEpoch'))is int and state['commandEpoch']==epoch else None
  state=self.wait('genuine same-epoch Qt '+command,done)
  events=self.raw('actual Qt command event suffix',lambda:[self.helper.strict_json(v)for v in (actor['output']/'events.jsonl').read_bytes().splitlines()])
  require(any(e.get('event')=='commandHandled'and e.get('command')==command and type(e.get('epoch'))is int and e['epoch']==epoch for e in events),'same actual handled command')
  return state
 def pointer(self,case):
  proc,row=self.registry.launch(case,'pointer',1)
  return dict(proc=proc,row=row,held=False)
 def pointer_write(self,pointer,text):
  self.session.guard();proc=pointer['proc'];current=self.registry_module.lifetime(proc.pid)
  require(proc.poll()is None and self.decoder.exact(current,{k:pointer['row']['registered'][k]for k in ['pid','start','pgid']}),'same actual owned pointer before every write')
  self.authority.input_safe(self.old_probe('state')) if not pointer['held']else None
  proc.stdin.write(text);proc.stdin.flush()
 def move_pointer(self,pointer,point,expected=None,excluded=()):
  require(type(point)is list and len(point)==2 and all(type(x)is int for x in point),'actual bounded point')
  self.pointer_write(pointer,self.authority.move_command(point,1600,1000))
  def arrived():
   state=self.old_probe('state');self.authority.input_safe(state)
   if not self.decoder.exact(state.get('cursor'),point):
    # Probe cursor uses native JSON numeric doubles; exact numeric values allowed
    # only after typed finite coordinate validation below, never for identity.
    coordinates=state.get('cursor')
    if type(coordinates)is not list or len(coordinates)!=2 or any(type(x)not in {int,float}or not math.isfinite(x)for x in coordinates)or coordinates!=point:return None
   if expected is not None and not self.authority.matches(state.get('hitOwner'),expected):return None
   require(not any(self.authority.matches(state.get('hitOwner'),c)for c in excluded),'excluded native hit must never be revived')
   return state
  return self.wait('actual cursor and eligible/excluded current hit',arrived,3)
 def close_pointer(self,pointer):
  # Genuine release if needed, EOF and normal wait; no signals or silent kill.
  proc=pointer['proc'];self.session.guard()
  if pointer['held']:
   self.pointer_write(pointer,'button 272 0\n');pointer['held']=False
  proc.stdin.close();proc.wait(timeout=5)
  final=self.old_probe('state');self.authority.input_safe(final)
  self.registry.terminal(proc,pointer['row'],timeout=5,receipt=dict(kind='pointer-eof',allButtonsReleased=True,stdinClosed=True,finalNative=final))
 def pin_titlebar(self,case,actor,ordinal,title='owner'):
  captured=self.capture(actor,title);self.focus(actor,captured);before=self.scene(captured)
  boxes=self.query('pin_bar_state');rows=[r for r in boxes if self.decoder.exact(r.get('captured'),captured)]
  require(len(rows)==1 and type(rows[0].get('pinHitBoxes'))is list and len(rows[0]['pinHitBoxes'])==1,'one exact current owning reserved pin box')
  point=self.authority.integer_point(rows[0]['pinHitBoxes'][0],1600,1000)
  # One pointer producer per titlebar episode, with unique registered role.
  proc,row=self.registry.launch(case,'pointer',ordinal);pointer=dict(proc=proc,row=row,held=False)
  try:
   self.move_pointer(pointer,point,captured)
   prefix=self.old_probe('events');native_prefix=self.query('pin_events');self.attest('before-real-titlebar')
   self.pointer_write(pointer,'button 272 1\n');pointer['held']=True
   self.pointer_write(pointer,'button 272 0\n');pointer['held']=False
   def done():
    delivery=self.episode.episode(prefix,self.old_probe('events'),'titlebar',captured,point,allow_pending=True)
    if delivery is None:return None
    current=self.query('pin_events');require(self.decoder.exact(current[:len(native_prefix)],native_prefix),'immutable native report prefix')
    if len(current)==len(native_prefix):return None
    require(len(current)==len(native_prefix)+1,'one actual titlebar toggle')
    report=self.helper.decode(json.dumps(current[-1],allow_nan=False,separators=(',',':')).encode(),self.decoder.POLICY)
    require(report['ok']is True and self.decoder.exact(report['captured'],captured),'same current native titlebar report')
    return delivery,report
   delivery,report=self.wait('real titlebar release and complete native report',done)
   after=self.scene(captured);require(self.decoder.exact(self.capture(actor,title),captured),'post-titlebar full same token')
   self.check_peers(before,after,captured)
   for a,b in [(before['native']['nativeFocus'],after['native']['nativeFocus']),(before['seat']['keyboardOwner'],after['seat']['keyboardOwner'])]:require(self.decoder.exact(a,b),'no titlebar-pin driven core/Seat change')
   self.trace.append(dict(route='titlebar',delivery=delivery,receipt=report,before=before,after=after,nativeTransitionOnly=True));self.persist()
   return report,after
  finally:self.close_pointer(pointer)
 def check_peers(self,before,after,captured):
  fields=['address','stableId','pid','pinned','floating','at','size','workspace','monitor','fullscreen','fullscreenClient']
  def peers(scene):return sorted([{k:r.get(k)for k in fields}for r in scene['clients']if not self.authority.matches(r,captured)],key=lambda r:(r['pid'],r['stableId'],r['address']))
  require(self.decoder.exact(peers(before),peers(after)),'all exact independent peer mode/workspace/output/geometry/pin state')
 def native_mode(self,actor,title,mode,action):
  require(mode in {'maximized','fullscreen'}and action in {'set','unset'},'fixed native mode request')
  captured=self.capture(actor,title);selector=json.dumps('address:'+captured['address'])
  self.setup('actual native '+mode+' '+action,'hl.dsp.window.fullscreen({mode='+json.dumps(mode)+',action='+json.dumps(action)+',layout_aware=true,window='+selector+'})')
  expected=({'maximized':1,'fullscreen':2}[mode]if action=='set'else 0)
  def reached():
   current=self.snapshot(self.capture(actor,title));return current if current['body']['internalMode']==expected else None
  return self.wait('actual raw owning mode '+str(expected),reached)
 def qt_box(self,actor,title,captured):
  state=self.fixture_state(actor);client=state['windows'][title]['buttonClient']
  require(type(client)is list and len(client)==4 and all(type(v)is int for v in client),'current typed Qt client button hint')
  native=self.old_probe('state');rows=[r for r in native['windows']if self.authority.matches(r,captured)]
  require(len(rows)==1 and type(rows[0].get('surfaceBox'))is list,'actual current native surface box required')
  box=rows[0]['surfaceBox'];require(len(box)==4,'actual surface box shape')
  # Native compositor origin is authoritative; QWidget global position is a hint only.
  require(all(type(v)in {int,float}and math.isfinite(v)for v in box),'typed finite actual native surface box')
  return [str(self.decoder.decimal(str(box[0]))+client[0]),str(self.decoder.decimal(str(box[1]))+client[1]),str(client[2]),str(client[3])]
 def qt_point(self,actor,title,captured):
  return self.authority.integer_point(self.qt_box(actor,title,captured),1600,1000)
 def click_fixture(self,case,actor,title,ordinal=1,point_override=None):
  captured=self.capture(actor,title);box=self.qt_box(actor,title,captured)
  point=self.authority.integer_point(box,1600,1000)if point_override is None else point_override
  require(type(point)is list and len(point)==2 and all(type(v)is int for v in point)and self.point_inside(point,box),'same actual integer point inside current native Qt button')
  before=self.fixture_state(actor)
  require(type(before['windows'][title]['clicks'])is int and before['windows'][title]['clicks']>=0,'typed original real button click count')
  proc,row=self.registry.launch(case,'pointer',ordinal);pointer=dict(proc=proc,row=row,held=False)
  try:
   self.move_pointer(pointer,point,captured);prefix=self.old_probe('events');self.attest('before-real-widget-button')
   self.pointer_write(pointer,'button 272 1\n');pointer['held']=True
   self.pointer_write(pointer,'button 272 0\n');pointer['held']=False
   def done():
    # Original frozen decoder parses the physical button pair; its route string
    # is retained as parser evidence, not re-labelled as a titlebar pin receipt.
    delivery=self.episode.episode(prefix,self.old_probe('events'),'titlebar',captured,point,allow_pending=True)
    if delivery is None:return None
    state=self.fixture_state(actor);count=state['windows'][title]['clicks']
    if count==before['windows'][title]['clicks']:return None
    require(type(count)is int and count==before['windows'][title]['clicks']+1,'one real Qt button callback')
    native=self.old_probe('state');seat=self.old_probe('keyboard_state')
    if not(self.authority.matches(native.get('nativeFocus'),captured)and self.authority.matches(seat.get('keyboardOwner'),captured)and seat.get('keyboardSurfacePresent')is True and seat.get('keyboardResourcePresent')is True):return None
    require(self.decoder.exact(self.capture(actor,title),captured),'post-widget same full current token')
    return dict(semanticRoute='fixture-button',originalButtonPairDecoder=delivery,qtBefore=before,qtAfter=state,native=native,seat=seat,captured=captured,point=point,currentNativeButtonBox=box)
   result=self.wait('actual widget callback and distinct core/Seat',done);self.trace.append(result);self.persist();return result
  finally:self.close_pointer(pointer)
 def ordinary_case(self,case,actor):
  if case=='B01':
   captured=self.capture(actor);before=self.scene(captured);first,_=self.pin_keyboard(case,actor,1);second,after=self.pin_keyboard(case,actor,2)
   require(first['after']['pinned']is True and second['after']['pinned']is False,'ordinary genuine pin/unpin')
   self.check_peers(before,after,captured)
   for key in ['internalMode','clientMode','floating','logicalBox','visualBox','workspace','output']:require(self.decoder.exact(before['owned']['body'][key],after['owned']['body'][key]),'ordinary context conserved '+key)
   return dict(case=case,component='ordinary-native-pin-conservation',completeNativeSubset=True)
  if case=='B02':
   maximum=self.native_mode(actor,'owner','maximized','set');captured=self.capture(actor);peer=self.capture(actor,'peer');peer_before=self.snapshot(peer)
   require(peer_before['body']['acceptsInput']is False,'actual ordinary tiled peer blocked under unprotected MAX')
   click=self.click_fixture(case,actor,'owner');require(self.snapshot(peer)['body']['acceptsInput']is False,'blocked peer not revived by physical click')
   self.native_mode(actor,'owner','maximized','unset')
   return dict(case=case,component='unprotected-MAX-actual-hit-callback-Seat',maximum=maximum,click=click,blockedPeer=peer_before,completeNativeSubset=True)
  if case=='B03':
   exclusive=self.native_mode(actor,'owner','fullscreen','set');captured=self.capture(actor);before=self.scene(captured);prefix=self.query('pin_events')
   request=self.helper.command(captured).decode('utf8');require(request.startswith('repl '),'exact immutable helper wire command')
   self.attest('before-captured-native-refusal')
   raw=self.raw('exact helper command bytes via owned native IPC; CLI ingress NOT claimed',lambda:self.session.ctl('repl',request[5:]))
   report=self.helper.decode(raw.encode(),self.decoder.POLICY)
   require(report['ok']is False and report['phase']=='validate'and report['actionsInvoked']is False and report['possiblePartialOutcome']is False and self.decoder.exact(report['captured'],captured),'definite exact exclusive native pin refusal')
   after=self.scene(captured);self.check_peers(before,after,captured)
   require(self.decoder.exact(before['owned']['body'],after['owned']['body'])and self.decoder.exact(self.capture(actor),captured),'selected native state conserved on refusal')
   current=self.query('pin_events');require(self.decoder.exact(current[:len(prefix)],prefix)and len(current)==len(prefix)+1 and self.decoder.exact(current[-1],report),'actual exactly one registered native refusal')
   self.native_mode(actor,'owner','fullscreen','unset')
   return dict(case=case,component='exclusive-native-request-refusal',exclusive=exclusive,receipt=report,CLIHelperIngressAccepted=False,fullDesignCaseAccepted=False)
 def retained_tiled(self,case,actor):
  captured=self.capture(actor);normal=self.snapshot(captured)['body'];require(normal['floating']is False and normal['internalMode']==0,'real original tiled normal target')
  maximum=self.native_mode(actor,'owner','maximized','set');report,_=self.pin_keyboard(case,actor,1)
  require(report['after']['pinned']is True,'actual admitted nativeMAX pin')
  returned=self.native_mode(actor,'owner','maximized','unset')['body']
  require(returned['pinned']is True and returned['floating']is False and returned['internalMode']==0 and returned['clientMode']==normal['clientMode'],'actual retained normal tiled pin')
  for key in ['logicalBox','visualBox','workspace','output']:require(self.decoder.exact(returned[key],normal[key]),'exact tiled return '+key)
  return dict(normal=normal,maximum=maximum,returned=returned)
 def retained_case(self,case,actor):
  reached=self.retained_tiled(case,actor);report,after=self.pin_keyboard(case,actor,2)
  require(report['after']['pinned']is False and report['after']['floating']is False,'explicit same-owned unpin without synthetic float')
  for key in ['logicalBox','visualBox','target','space','workspace','output']:require(self.decoder.exact(after['owned']['body'][key],reached['returned'][key]),'unpin conserves current tiled context '+key)
  return dict(case=case,component='retained-tiled-unpin',reached=reached,receipt=report,completeNativeSubset=True)
 def coexistence_case(self,case,actor):
  reached=self.retained_tiled(case,actor);owner=self.capture(actor);peer=self.capture(actor,'peer')
  peer_max=self.native_mode(actor,'peer','maximized','set');require(self.public(actor,'peer').get('pinned')is False,'independent ordinary MAX peer pin intent false')
  if case=='B08':
   report,_=self.pin_keyboard(case,actor,2,'peer');require(report['after']['pinned']is True,'independent real MAX peer pin intent true')
  owner_point=self.qt_point(actor,'owner',owner);peer_box=self.qt_box(actor,'peer',peer);require(self.point_inside(owner_point,peer_box),'actual current overlapping owner/peer point')
  winner=self.raw('current actual protected band witness',lambda:self.query('pin_stack_state'))
  require(winner.get('planValid')is True and winner.get('satisfied')is True,'actual native shared-band plan/satisfied')
  protected=[r for r in winner['order']if r.get('coreProtected')is True]
  require(any(self.authority.matches(r,owner)for r in protected),'actual protected tiled owner still in shared native band')
  # Use actual native query winner, never list order as presentation proof.
  proc,row=self.registry.launch(case,'pointer',1);pointer=dict(proc=proc,row=row,held=False)
  try:
   self.move_pointer(pointer,owner_point);observed=self.snapshot(owner,0)
   actual=observed['hitOwner'];require(self.authority.matches(actual,owner)or self.authority.matches(actual,peer),'current overlapping winner belongs to protected scene')
   if case=='B07':require(self.authority.matches(actual,owner),'protected tiled owner wins over ordinary MAX')
  finally:self.close_pointer(pointer)
  click=self.click_fixture(case,actor,'owner'if self.authority.matches(actual,owner)else'peer',2,point_override=owner_point)
  require(self.decoder.exact(click['point'],owner_point),'same actual overlap query/button point')
  if case=='B08':self.pin_keyboard(case,actor,3,'peer')
  self.native_mode(actor,'peer','maximized','unset');self.pin_keyboard(case,actor,4)
  return dict(case=case,component='coexisting-native-owning-hit-and-distinct-Seat',reached=reached,peerMaximum=peer_max,actualNativeBand=winner,query=observed,queryPoint=owner_point,click=click,sameOverlapDeliveryAccepted=True,presentationROIAccepted=False,fullDesignCaseAccepted=False)
 def point_inside(self,point,box):
  x,y,w,h=[self.decoder.decimal(v)for v in box];return x<point[0]<x+w and y<point[1]<y+h
 def modal_case(self,case,actor):
  self.fixture_command(actor,'open');child=self.await_capture(actor,'child')
  if case=='B09':
   self.pin_keyboard(case,actor,1,'child');require(self.public(actor)['pinned']is False and self.public(actor,'child')['pinned']is True,'independent child intent without ancestor intent')
  self.fixture_command(actor,'nested');nested=self.await_capture(actor,'nested')
  bits={name:self.public(actor,name)['pinned']for name in ['owner','peer','child','nested']}
  require(bits['owner']is False and bits['peer']is False and bits['nested']is False,'no fabricated ancestor/sibling/nested intent')
  if case=='B09':require(bits['child']is True,'independent real child pin retained')
  modal_captures={name:self.capture(actor,name)for name in ['owner','child','nested']};qt_before=self.fixture_state(actor)
  fields=['visible','native','modality','transientParentTitle','clicks']
  modal_before={name:{k:qt_before['windows'][name][k]for k in fields}for name in modal_captures}
  for name in modal_before:
   state=modal_before[name];require(state['visible']is True and state['native']is True and type(state['modality'])is int and type(state['clicks'])is int and state['clicks']>=0 and type(state['transientParentTitle'])is str,'actual complete current modal source projection')
  require(modal_before['owner']['modality']==0 and modal_before['child']['modality']==1 and modal_before['nested']['modality']==1 and modal_before['child']['transientParentTitle']=='Qt WindowModal QA owner'and modal_before['nested']['transientParentTitle']=='Qt WindowModal QA child','genuine current WindowModal child/nested parent chain')
  click=self.click_fixture(case,actor,'peer');after={name:self.public(actor,name)['pinned']for name in bits}
  require(self.decoder.exact(bits,after),'unrelated physical focus does not fabricate pin intent')
  qt_after=self.fixture_state(actor);modal_after={name:{k:qt_after['windows'][name][k]for k in fields}for name in modal_captures}
  require(self.decoder.exact(modal_before,modal_after),'unrelated current peer focus conserves original visible/native/modal/transient/click fields')
  after_captures={name:self.capture(actor,name)for name in modal_captures}
  require(self.decoder.exact(modal_captures,after_captures),'exact owner/child/nested current captures conserved after unrelated peer focus')
  return dict(case=case,component='independent-child/unrelated-current-core-Seat-focus',bits=bits,child=child,nested=nested,click=click,modalBefore=modal_before,modalAfter=modal_after,modalCapturesBefore=modal_captures,modalCapturesAfter=after_captures,actualModalSourceConserved=True,presentationROIAccepted=False,fullDesignCaseAccepted=case=='B10')
 def exclusion_case(self,case,actor):
  reached=self.retained_tiled(case,actor);owner=self.capture(actor);peer=self.capture(actor,'peer')
  self.native_mode(actor,'peer','maximized','set');self.focus(actor,peer)
  original=self.snapshot(owner)['body']
  require(original['acceptsInput']is True and original['noFocus']is False,'real admitted input/focus before explicit exclusion; no vacuous property success')
  prop='allows_input'if case=='B11'else'no_focus';value='0'if case=='B11'else'1'
  self.setup('explicit actual excluded owner property','hl.dsp.window.set_prop({prop='+json.dumps(prop)+',value='+json.dumps(value)+',window='+json.dumps('address:'+owner['address'])+'})')
  def changed():
   r=self.snapshot(self.capture(actor));return r if (r['body']['acceptsInput']is False if case=='B11'else r['body']['noFocus']is True)else None
  excluded=self.wait('actual selected property reflected',changed)
  point=self.qt_point(actor,'owner',owner);before=self.fixture_state(actor)
  require(type(before['windows']['owner']['clicks'])is int and before['windows']['owner']['clicks']>=0,'typed original excluded-owner click count')
  proc,row=self.registry.launch(case,'pointer',1);pointer=dict(proc=proc,row=row,held=False)
  try:
   self.move_pointer(pointer,point,excluded=(owner,));query=self.snapshot(owner,0)
   require(not self.authority.matches(query['hitOwner'],owner),'excluded protected owner absent from native hit')
   prefix=self.old_probe('events');self.pointer_write(pointer,'button 272 1\n');pointer['held']=True;self.pointer_write(pointer,'button 272 0\n');pointer['held']=False
   def complete():
    rows=self.old_probe('events');require(self.decoder.exact(rows[:len(prefix)],prefix),'actual button prefix exact')
    if len(rows)==len(prefix):return None
    if len(rows)<len(prefix)+2:return None
    require(len(rows)==len(prefix)+2,'exact physical exclusion press/release')
    for r,(code,state)in zip(rows[len(prefix):],[(272,1),(272,0)],strict=True):
     require(type(r.get('button'))is int and type(r.get('buttonState'))is int and r['button']==code and r['buttonState']==state and type(r.get('native'))is dict,'typed actual exclusion buttons')
     require(not self.authority.matches(r['native'].get('hitOwner'),owner),'excluded owner not hit during real press/release')
    native=self.old_probe('state');seat=self.old_probe('keyboard_state');require(not self.authority.matches(native.get('nativeFocus'),owner)and not self.authority.matches(seat.get('keyboardOwner'),owner),'excluded owner not actual core or Seat accepted target')
    return dict(buttons=rows[len(prefix):],native=native,seat=seat,qt=self.fixture_state(actor))
   actual=self.wait('actual excluded real-input closure/current core+Seat',complete)
   require(type(actual['qt']['windows']['owner']['clicks'])is int and actual['qt']['windows']['owner']['clicks']==before['windows']['owner']['clicks'],'no excluded owner Qt button callback')
  finally:self.close_pointer(pointer)
  self.setup('restore only explicit fixture property','hl.dsp.window.set_prop({prop='+json.dumps(prop)+',value='+json.dumps('1'if case=='B11'else'0')+',window='+json.dumps('address:'+owner['address'])+'})')
  self.native_mode(actor,'peer','maximized','unset');self.pin_keyboard(case,actor,2)
  return dict(case=case,component='excluded-protected-owner-current-native-hit-core-Seat',excluded=excluded,query=query,actual=actual,thirdBlockedTiledPeerPresent=False,fullDesignCaseAccepted=False)
 def run_first_phase(self):
  # Root must construct this only after the separate collector/source grant.
  # No GUI execution happens from import. Remaining B13–B24 are never counted.
  results=[]
  for case in ['B%02d'%n for n in range(1,13)]:
   self.attest('before-case-'+case);actor=self.launch_actor(case)
   try:
    if case in {'B01','B02','B03'}:result=self.ordinary_case(case,actor)
    elif case in {'B04','B05'}:
     self.native_max_case(case,actor);result=dict(case=case,component='native-MAX-pin-unpin-normal-return',completeNativeSubset=True,exhaustiveNativeModeTrajectoryAccepted=False)
    elif case=='B06':result=self.retained_case(case,actor)
    elif case in {'B07','B08'}:result=self.coexistence_case(case,actor)
    elif case in {'B09','B10'}:result=self.modal_case(case,actor)
    else:result=self.exclusion_case(case,actor)
    self.attest('after-case-'+case);self.trace.append(dict(caseResult=result));self.persist();results.append(result)
   finally:self.retire_actor(actor)
  self.registry.seal_before_host_close()
  return dict(actualComponentResults=results,remainingCases=['B%02d'%n for n in range(13,25)],fullCampaignBAccepted=False,original14Credit=False,sourceOnlyUntilRootGrant=True)
