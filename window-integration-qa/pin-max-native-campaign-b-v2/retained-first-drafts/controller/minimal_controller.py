"""Draft B04/B05 only. No entry point and no implicit GUI/native launch."""
from pathlib import Path
import importlib.util,json,os,time

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
  self.registry=self.registry_module.Registry(session,self.output,frozen)
  self.root=dict(compositorPid=session.evidence['compositorPID'],compositorPgid=session.evidence['compositorPGID'],compositorStart=session.evidence['compositorStart'],session=session.evidence['signature'])
 def persist(self):
  p=self.output/'campaign-b-trace.json';p.write_text(json.dumps(dict(trace=self.trace,blocked=self.blocked,original14Credit=False,maxPolicyAccepted=False),indent=2,allow_nan=False)+'\n');p.chmod(0o600)
 def raw(self,label,fn):
  require(not self.blocked and len(self.trace)<4096,'bounded current source-only review protocol')
  row=dict(label=label,startedNs=time.monotonic_ns());self.trace.append(row);self.persist()
  try:
   self.session.guard();row['value']=fn();row['completedNs']=time.monotonic_ns();self.persist();return row['value']
  except BaseException as error:
   row['error']=repr(error);self.blocked=True;self.persist();raise
 def attest(self,phase):
  pair=self.raw('actual completed source pair '+phase,lambda:self.binding.read_pair(self.pair_path))
  require(pair.get('observerBuildComplete')is True and type(pair.get('observer'))is str and pair['observer']in pair['inputs']and pair['observer']in pair['inputModes'],'new observer must be actually built/reviewed/paired first')
  value=self.raw('actual root/modules '+phase,lambda:self.binding.attest(self.session,pair,phase,(pair['plugin'],pair['probe'],pair['observer'])))
  require(value['passed']is True,'actual source-bound owned core/plugin/old probe/new observer')
  return pair
 def query(self,name):
  require(name in {'pin_capture','pin_events','pin_stack_state','pin_bar_state'},'fixed native product read/query')
  require(name!='pin_capture','capture requires typed selected lifetime')
  return self.raw('actual product '+name,lambda:json.loads(self.session.ctl('repl','print(hl.plugin.hyprbars.'+name+'())')))
 def old_probe(self,name):
  require(name in {'state','keyboard_state','events','keyboard_events'},'unchanged diagnostic probe query')
  return self.raw('actual unchanged probe '+name,lambda:json.loads(self.session.ctl('repl','print(hl.plugin.qt_modal_probe.'+name+'())')))
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
  value=self.authority.token(self.raw('actual complete captured product receipt',lambda:json.loads(self.session.ctl('repl',command))))
  require(self.decoder.exact(self.authority.public(value),public)and value['compositorPid']==self.root['compositorPid']and value['compositorStart']==self.root['compositorStart']and value['session']==self.root['session'],'captured same root/member')
  return value
 def snapshot(self,captured,mask=0,ignore=False):
  self.attest('before-read')
  self.decoder.integer(mask,0,4);self.decoder.boolean(ignore)
  command='print(hl.plugin.pin_campaign_b.observe('+json.dumps(captured['address'])+','+json.dumps(captured['stableId'])+','+str(captured['pid'])+','+str(mask)+','+('true'if ignore else'false')+'))'
  raw=self.raw('actual new owning read',lambda:self.session.ctl('repl',command))
  value=self.decoder.decode(raw.encode(),self.root,captured,mask,ignore)
  require(int(value['sequence'])>self.sequence,'new current observation, no replay')
  self.sequence=int(value['sequence']);return value
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
  self.attest('before-setup')
  row=self.raw('explicit preparation only '+label,lambda:self.session.ctl('dispatch',command))
  # Dispatch ACK is archived as preparation, never a feature outcome.
  return row
 def launch_actor(self,case,ordinal=1):
  require(case in {'B04','B05'},'minimal implemented scenario only')
  self.attest('before-private-actor')
  folder=self.output/'actors'/case/('qt-'+str(ordinal));folder.mkdir(mode=0o700,parents=True,exist_ok=False)
  proc,row=self.registry.launch(case,'qt',ordinal,actor_output=folder)
  actor=dict(proc=proc,row=row,output=folder,epoch=0)
  def ready():
   def sample():
    require(proc.poll()is None,'current Qt actor during readiness')
    p=folder/'state.json'
    return json.loads(p.read_bytes())if p.exists()else None
   state=self.raw('actual pending/ready Qt state',sample)
   if state is None:return None
   require(type(state.get('pid'))is int and state['pid']==proc.pid and state.get('platform')=='wayland'and state.get('qtVersion')=='6.11.2','real exact source-bound Qt readiness')
   return state if all(type(state['windows'].get(name))is dict and state['windows'][name].get('visible')is True and state['windows'][name].get('native')is True for name in ['owner','peer'])else None
  self.wait('actual private actor ready',ready)
  current=self.capture(actor)
  if case=='B05':
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
  events=[json.loads(line)for line in (folder/'events.jsonl').read_text().splitlines()]
  require(any(type(e)is dict and e.get('event')=='commandHandled'and e.get('command')=='quit'and type(e.get('epoch'))is int and e['epoch']==actor['epoch']for e in events),'genuine same-epoch Qt quit callback')
  receipt=dict(kind='qt-quit',pid=proc.pid,commandEpoch=actor['epoch'],commandHandled=True,eventLogSHA256=self.registry_module.sha(folder/'events.jsonl'),stateSHA256=self.registry_module.sha(folder/'state.json'))
  self.registry.terminal(proc,row,timeout=8,receipt=receipt)
 def focus(self,actor,captured):
  self.setup('current fixture focus','hl.dsp.focus({window='+json.dumps('address:'+captured['address'])+'})')
  def accepted():
   native=self.old_probe('state');seat=self.old_probe('keyboard_state')
   return (native,seat)if self.authority.matches(native.get('nativeFocus'),captured)and self.authority.matches(seat.get('keyboardOwner'),captured)and seat.get('keyboardSurfacePresent')is True and seat.get('keyboardResourcePresent')is True else None
  self.wait('actual core and distinct Seat',accepted)
 def pin_keyboard(self,case,actor,ordinal):
  captured=self.capture(actor);self.focus(actor,captured);before=self.scene(captured)
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
  self.registry.terminal(proc,row,timeout=4,receipt=dict(kind='physical-chord',route='super-p',delivery=delivery))
  after=self.scene(captured);current=self.capture(actor)
  require(self.decoder.exact(current,captured),'post-input exact full lifetime/epoch')
  fields=['address','stableId','pid','pinned','floating','at','size','workspace','monitor','fullscreen','fullscreenClient']
  def peers(scene):return [{k:r.get(k)for k in fields}for r in scene['clients']if not self.authority.matches(r,captured)]
  require(self.decoder.exact(peers(before),peers(after)),'all independent peer geometry/workspace/output/pin/mode fields')
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
  first,_=self.pin_keyboard(case,actor,1);second,_=self.pin_keyboard(case,actor,2)
  require(first['after']['pinned']is True and second['after']['pinned']is False,'actual pin then unpin while native MAX')
  current=self.snapshot(self.capture(actor))['body']
  conserved=['internalMode','clientMode','floating','logicalBox','visualBox','restoreGeneration','restoreLogicalBox','restoreVisualBox','target','space','workspace','output']
  require(all(self.decoder.exact(maximum['body'][k],current[k])for k in conserved),'actual native mode/owning MAX conservation')
  self.setup('actual native MAX unset','hl.dsp.window.fullscreen({mode="maximized",action="unset",layout_aware=true,window='+target+'})')
  def returned():
   value=self.snapshot(self.capture(actor));return value if value['body']['internalMode']==0 else None
  after=self.wait('actual native normal return',returned)['body']
  require(after['floating']is normal['floating']and self.decoder.exact(after['logicalBox'],normal['logicalBox'])and self.decoder.exact(after['visualBox'],normal['visualBox'])and after['clientMode']==normal['clientMode'],'exact actual normal/floating return and client mode')
  self.trace.append(dict(case=case,nativeMaxReturnObserved=True,original14Credit=False,normal=normal,maximum=maximum['body'],returned=after));self.persist()
