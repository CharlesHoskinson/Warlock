"""Actual current525 routes refactored for GTK targets; import creates no processes."""
import importlib.util,json,subprocess,time,os
from pathlib import Path
class Refused(ValueError):pass
ROOT=Path(__file__).resolve().parents[1]
GUI=ROOT.parent/'elm-stable-surface-publication-v521'
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
KEYBOARD=Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
def remaining(deadline):
 value=deadline-time.monotonic()
 if value<=0:raise Refused('Original absolute six-second stage deadline')
 return value
def full_key(request,outcome):
 if type(request) is not dict or type(outcome) is not dict:raise Refused('full native request/outcome')
 def canonical(value):
  if type(value) is not str or not value.isascii() or not value.isdecimal() or value.startswith('0') or len(value)>20 or int(value)>2**64-1:raise Refused('original canonical native counter')
 for packet in (request,outcome):
  if type(packet.get('protocolVersion')) is not int or packet['protocolVersion']!=3:raise Refused('owning native protocol')
  bound=packet.get('binding');intent=packet.get('intent')
  if type(bound) is not dict or set(bound)!={'lifetime','session','frontend'}:raise Refused('original full binding shape')
  for value in bound.values():canonical(value)
  if type(intent) is not dict or set(intent)!={'request','generation','incarnation','operation','context'}:raise Refused('full intent shape')
  for key in ['request','generation','incarnation']:canonical(intent[key])
  if type(intent['context']) is not dict or set(intent['context'])!={'lifetime','epoch','output','revision'}:raise Refused('original complete intent context')
  for value in intent['context'].values():canonical(value)
  if type(intent['operation']) is not str or intent['operation'] not in ('activate','minimize','restore','maximize','restore-geometry'):raise Refused('closed native intent operation')
 if request.get('kind')!='window-effect' or outcome.get('kind')!='effect-outcome':raise Refused('native effect kinds')
 for name in ['binding','intent','effectProtocol']:
  if name not in request or outcome.get(name)!=request[name]:raise Refused('original immutable full native key')
 if type(outcome.get('effectProtocol')) is not int or type(request['effectProtocol']) is not int or request['effectProtocol'] not in (1,2):raise Refused('exact negotiated effect version')
 if request['intent']['context']['lifetime']!=request['binding']['lifetime']:raise Refused('binding/context owning lifetime')
 if (request['effectProtocol']==1 and request['intent']['operation'] not in ('activate','minimize','restore')) or (request['effectProtocol']==2 and request['intent']['operation'] not in ('maximize','restore-geometry')):raise Refused('operation belongs to exact effect version')
 if outcome.get('status')!='Committed':raise Refused('actual Committed native outcome required')
 return True
class Shell:
 def __init__(self,session,host,build_root,config,output,collector):
  self.session=session;self.host=host;self.build=Path(build_root);self.config=Path(config);self.output=Path(output);self.collector=collector;self.web=None;self.actions=[];self.relay=None;self.relay_control=None;self.relay_config=self.output/'gtk-broker-relay.json';self.actor_number=0
 def launch(self,deadline):
  remaining(deadline);self.session.guard()
  self.prepare_relay()
  argv=[str(self.build/'elm-host'),'--assets',str(self.build/'inputs/assets'),'--backend',str(ROOT/'relay/qa/relay.py'),'--authority-config',str(self.relay_config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open']
  self.web=self.session.host.launch('elm-webview',argv,env=dict(self.session.env,WAYLAND_DEBUG='client'))
  self.wait(lambda:self.projection() if self.projection() and self.projection()['phase']=='Coherent' else None,deadline)
 def prepare_relay(self):
  if self.relay is None:
   spec=importlib.util.spec_from_file_location('gtk_owned_eof_relay',ROOT/'relay/qa/relay.py');self.relay=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.relay)
  self.actor_number+=1;self.relay_control=self.output/('gtk-broker-actor-'+str(self.actor_number));self.relay_control.mkdir(mode=0o700)
  authority=self.relay.read_private(self.config)
  packet={'profile':'broker','authorityConfig':str(self.config),'controlDirectory':str(self.relay_control),'runtime':authority['runtime'],'instance':authority['instance']}
  temporary=self.output/('gtk-broker-config-'+str(self.actor_number)+'.json')
  fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600)
  with os.fdopen(fd,'w') as stream:json.dump(packet,stream,separators=(',',':'));stream.flush();os.fsync(stream.fileno())
  os.replace(temporary,self.relay_config)
 def geometry_attach(self):
  values=self.frames('backend-frame: ','geometry-attached')
  return values[-1] if values else None
 def owned_actor(self):
  marker=self.relay.actor_status(self.relay_control);owned={row['pid']:row for row in self.session.host.descendants()}
  for kind in ('relay','child'):
   actor=marker[kind];record=owned.get(actor['pid'])
   if record is None or record.get('start')!=actor['start'] or not self.host.original.same_process(record):raise Refused('exact owned broker relay PID/start')
   command=Path('/proc',str(actor['pid']),'cmdline').read_bytes().split(b'\0')[:-1]
   wanted=[b'/usr/bin/python3',b'-B',str(ROOT/'relay/qa/relay.py').encode(),str(self.relay_config).encode()] if kind=='relay' else [b'/usr/bin/python3',b'-B',str(self.build/'inputs/adapter/daemon.py').encode(),str(self.config).encode()]
   if command!=wanted:raise Refused('fixed captured broker/relay command')
  return marker,owned
 def reconnect(self,deadline):
  remaining(deadline);before=self.projection();effects=list(self.journal());old=self.geometry_attach()
  if not before or before['phase']!='Coherent' or before['outstanding']!=0 or before['registry']!=0 or old is None:raise Refused('quiescent authenticated shell required before owned EOF')
  marker,owned=self.owned_actor();old_control=self.relay_control;old_config=self.relay_config.read_bytes();line_count=len(self.log().split('\n'))
  self.relay.close_stdin(old_control)
  def retired():
   status_path=old_control/'exit.json'
   if not status_path.is_file() or status_path.stat().st_size==0:return None
   status=self.relay.exit_status(old_control)
   if status!={**marker,'childExit':0,'stdinClosed':True}:raise Refused('exact normal broker EOF receipt')
   if any(self.host.original.same_process(owned[row['pid']]) for row in marker.values()):return None
   return status
  status=self.wait(retired,deadline)
  self.wait(lambda:self.projection() if self.projection() and self.projection()['phase']=='Detached' and self.projection().get('reconnect') else None,deadline)
  if 'backend-exit: waited=1 normal=1 code=0' not in self.log().split('\n')[line_count:]:raise Refused('host must observe normal relay exit')
  if self.journal()!=effects or self.projection()['outstanding']!=0 or self.projection()['registry']!=0:raise Refused('disconnect cannot replay or discard native operations')
  archive=self.output/('gtk-retired-relay-config-'+str(self.actor_number)+'.json');fd=os.open(archive,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as stream:stream.write(old_config)
  self.prepare_relay();self.pointer(self.projection()['reconnect'],272,deadline)
  fresh=self.wait(lambda:self.geometry_attach() if self.geometry_attach() and self.geometry_attach()['binding']!=old['binding'] else None,deadline)
  self.wait(lambda:self.projection() if self.projection() and self.projection()['phase']=='Coherent' else None,deadline)
  new,new_owned=self.owned_actor()
  if any(new[key]==marker[key] for key in ('relay','child')) or fresh['binding']['lifetime']!=old['binding']['lifetime'] or self.journal()!=effects:raise Refused('fresh authenticated peers retain native lifetime without effect replay')
  record={'retiredActor':marker,'normalEOF':status,'newActor':new,'oldBinding':old['binding'],'newBinding':fresh['binding'],'deadlineSeconds':6,'noReplay':True};self.actions.append({'reconnect':record});return record
 def log(self):
  path=self.output/'elm-webview.log'
  if not path.exists():return ''
  if path.stat().st_size>16*1024*1024:raise Refused('owned shell log bound')
  return path.read_text(encoding='utf-8',errors='strict')
 def frames(self,prefix,kind):
  values=[]
  for line in self.log().split('\n'):
   if line.startswith(prefix):
    value=json.loads(line[len(prefix):])
    if value.get('kind')==kind:values.append(value)
  return values
 def journal(self):return self.frames('frontend-request: ','window-effect')
 def outcomes(self):return self.frames('backend-frame: ','effect-outcome')
 def projection(self):return self.collector.read(self.log())
 def inspections(self):return [json.loads(line.split(': ',1)[1]) for line in self.log().split('\n') if line.startswith('surface-inspection: ')]
 def menu(self):
  values=self.inspections()
  if not values:return None
  model=values[-1]
  return model if model['body']['mode']=='menu' and model['body']['phase']=='Coherent' and model['body']['menu'] else None
 def wait(self,fn,deadline):
  while remaining(deadline):
   self.session.guard();value=fn();remaining(deadline)
   if value:return value
   if self.web and self.web.poll() is not None:raise Refused('owned shell exited')
   time.sleep(min(.02,remaining(deadline)))
 def group(self):
  p=self.projection()
  return p['groups'][0] if p and p['phase']=='Coherent' and len(p['groups'])==1 and not p['groups'][0]['disabled'] else None
 def selection(self,title):
  p=self.projection()
  if not p or p['phase']!='Coherent' or not p['picker']:return None
  rows=[row for row in p['picker']['selections'] if row['title']==title and not row['disabled']]
  if len(rows)>1:raise Refused('unique exact GTK picker title')
  return rows[0] if rows else None
 def helper(self,name,argv,payload,deadline):
  remaining(deadline);self.session.guard();directory=self.output/(name+'-'+str(time.time_ns()));directory.mkdir(mode=0o700)
  record={'argv':argv,'startedMonotonic':time.monotonic(),'deadline':deadline,'payload':payload};process=None
  try:
   with (directory/'stdout').open('xb') as out,(directory/'stderr').open('xb') as err:
    process=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=out,stderr=err,env=self.session.env,cwd=self.session.host.runtime,start_new_session=True)
   owned=self.host.original.process(process.pid);owned.update(name=name,command=argv,log=str(directory/'stderr'));self.session.host.processes.append((process,owned));record['owned']=owned
   process.communicate(payload.encode('ascii'),timeout=min(5,remaining(deadline)));record['exit']=process.returncode;remaining(deadline);self.session.guard()
   if process.returncode!=0:raise Refused('normal owning input helper exit')
   for stream,cap in [('stdout',65536),('stderr',65536)]:
    path=directory/stream
    if path.stat().st_size>cap:raise Refused('bounded owned input helper output')
    record[stream]=path.read_text(encoding='utf-8',errors='strict')
   return record
  except BaseException as error:
   record['error']=repr(error)
   if process is not None and process.poll() is None:
    process.terminate();record['failureTerminate']=True
    try:process.wait(timeout=.5)
    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=.5);record['failureKill']=True
   raise
  finally:
   if process is not None:record['exit']=process.poll()
   (directory/'record.json').write_text(json.dumps(record,indent=2)+'\n');self.actions.append(record)
 def pointer(self,item,button,deadline):
  if type(item) is not dict or item.get('visible',True) is not True or button not in (272,273):raise Refused('owned visible shell target')
  point=item.get('point')
  if type(point) is not list or len(point)!=2 or any(type(v) not in (int,float) for v in point):raise Refused('actual DOM point')
  x,y=(round(v) for v in point)
  if not 0<x<800 or not 0<y<(420 if button==272 else 600):raise Refused('target outside qualified viewport')
  remaining(deadline);self.session.guard()
  self.helper('shell-pointer',[str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton {button} 1\nsleep 50\nbutton {button} 0\nsleep 100\n',deadline)
 def keys(self,commands,deadline):
  self.helper('shell-keyboard',[str(KEYBOARD)],commands+'sleep 100\nsync\n',deadline)
 def invoke(self,title,incarnation,operation,deadline):
  if type(incarnation) is not str or not incarnation.isascii() or not incarnation.isdecimal() or incarnation.startswith('0'):raise Refused('native exact incarnation')
  names={'restore':'Restore','minimize':'Minimize','maximize':'Maximize','restore-geometry':'Restore'}
  if operation not in names:raise Refused('closed native operations')
  before=list(self.journal());self.pointer(self.wait(self.group,deadline),272,deadline)
  selected=self.wait(lambda:self.selection(title),deadline)
  if selected.get('incarnation')!=incarnation:raise Refused('current picker incarnation differs')
  self.pointer(selected,273,deadline);model=self.wait(self.menu,deadline);menu=model['body']['menu']
  if menu.get('incarnation')!=incarnation:raise Refused('captured menu incarnation differs')
  actions=menu.get('actions');target=[i for i,a in enumerate(actions) if a.get('label','').startswith(names[operation]) and a.get('enabled') is True]
  if len(target)!=1:raise Refused('exact enabled typed menu action')
  # Native navigation keeps actual Elm selection/binding guard; no direct Shell.Act.
  self.keys('key 102 1\nkey 102 0\n'+('key 108 1\nkey 108 0\n'*sum(a.get('enabled') is True for a in actions[:target[0]]))+'key 28 1\nkey 28 0\n',deadline)
  def receipt():
   requests=self.journal()
   if len(requests)<len(before)+1:return None
   if len(requests)!=len(before)+1:raise Refused('exactly one native dispatch, no replay')
   request=requests[-1]
   if request.get('intent',{}).get('incarnation')!=incarnation or request['intent'].get('operation')!=operation:raise Refused('native requested target/operation mismatch')
   matches=[row for row in self.outcomes() if row.get('binding')==request.get('binding') and row.get('intent')==request.get('intent') and row.get('effectProtocol')==request.get('effectProtocol')]
   if len(matches)>1:raise Refused('one native full-key outcome')
   if not matches:return None
   full_key(request,matches[0]);return {'request':request,'outcome':matches[0],'noReplay':True}
  return self.wait(receipt,deadline)

 def refuse_unavailable(self,binding,incarnation,operation,deadline):
  before=self.journal();self.pointer(self.wait(self.group,deadline),272,deadline);title=binding['native']['title'];selection=self.wait(lambda:self.selection(title),deadline)
  if selection.get('incarnation')!=incarnation:raise Refused('unavailable target current incarnation')
  self.pointer(selection,273,deadline);model=self.wait(self.menu,deadline);actions=model['body']['menu']['actions']
  matching=[a for a in actions if a.get('label','').startswith('Maximize')]
  if len(matching)!=1 or matching[0].get('enabled') is not False:raise Refused('actual disabled geometry action required')
  self.keys('key 1 1\nkey 1 0\n',deadline);self.wait(lambda:self.inspections()[-1]['body']['mode']=='closed',deadline)
  if self.journal()!=before:raise Refused('unsupported action fabricated native effect')
 def minimized_pixels(self,actor,session,ordinary,deadline):
  d=self.driver;before=d.actor.read();a=d.h.scene.current_role(before,'A');directory=d.directory/('GTK07-hidden-'+str(time.time_ns()))
  rgb,record=d.h.pixels.capture(session,d.host,directory,deadline,selected={'nativeBefore':ordinary,'gtkBefore':a,'expectedHidden':True})
  x,y,w,h=ordinary['geometry'];points=[[int(x+w/3),int(y+h/3)],[int(x+2*w/3),int(y+2*h/3)]]
  measured=[]
  for px,py in points:
   if not 0<=px<800 or not 0<=py<600:raise Refused('hidden ordinary region outside measured output')
   measured.append(list(rgb[(py*800+px)*3:(py*800+px)*3+3]))
  record['samples']=dict(points=points,rgb=measured);(directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')
  # A opaque drawing area is red; server hidden/render/input checks are separate.
  if any(sample==[204,51,51] for sample in measured):raise Refused('actual minimized owner color remains visible')
  after=d.fact('A')
  if not after['minimized'] or after['shouldRenderAny'] or after['acceptsInput']:raise Refused('native hidden state changed across capture')
 def popup_guard(self,actor,parent,session,deadline):
  from popup import binding,samples
  from keyboard import shift_pair
  d=self.driver;root=d.binding('A',False);before=d.wait(lambda:binding(actor,session,root));sid=before['identity']['surfaceId']
  # Actual PNG+RGB retained before interpreting samples or postcapture state.
  directory=d.directory/('GTK06-popup-'+str(time.time_ns()));census=session.data('clients')
  image,measurement=d.h.pixels.capture(session,d.host,directory,deadline,selected={'popup':before,'root':root,'nativeClients':census,'expectedRGB':[255,0,255]})
  measured=samples(image,before['marker']['global'],[255,0,255]);measurement['markerSamples']=measured;(directory/'record.json').write_text(json.dumps(measurement,indent=2)+'\n')
  d.inspect();after=d.wait(lambda:binding(actor,session,d.binding('A',False)))
  d.check('GTK06:stable-current-popup-capture',before['identity']==after['identity'] and before['native']==after['native'] and before['wire']==after['wire'] and before['gtk']['surfaceWidth']==after['gtk']['surfaceWidth'] and before['gtk']['surfaceHeight']==after['gtk']['surfaceHeight'] and before['marker']==after['marker'] and census==session.data('clients'),before=before,after=after,measurement=measurement)
  d.check('GTK06:actual-magenta-popup-body',measured['passed'],samples=measured)
  focus=json.loads(session.ctl('elm_held_state'))['focus']
  d.check('GTK06:popup-actual-keyboard-recipient',focus['surfaceClientPID']==actor.pid and focus['surfaceId']==sid,focus=focus)
  baseline=d.interval_start();wire_baseline=len(d.h.protocol.Trace(actor.stderr.read_bytes()).calls)
  parent.send('key-press 42',deadline);parent.send('key-release 42',deadline);rows=d.inspect();keys=[r for r in rows if r['sequence']>baseline and r['event'] in ('key-press','key-release')]
  wire=shift_pair(d.h.protocol.Trace(actor.stderr.read_bytes()),wire_baseline,surface_id=sid,xkb_shift_mask=d.h.keymap.xkb_shift_mask,gdk_shift_mask=d.h.keymap.gdk_shift_mask)
  if len(keys)!=2:raise Refused('entire popup nontext key interval')
  for row,event,key in zip(keys,('key-press','key-release'),wire):
   d.h.journal.recipient(row,event,'P',before['identity']['instance'],before['identity']['mapGeneration'],sid,d.types)
   for field,value in [('keyval',65505),('rawKeyval',65505),('keycode',50),('rawKeycode',50),('modifiers',key['gdkModifiers']),('rawModifiers',key['gdkModifiers']),('rawEventTime',key['time'])]:
    if type(row.get(field)) is not int or row[field]!=value:raise Refused('owning popup raw key/domain/modifier/time')
  current=d.wait(lambda:binding(actor,session,d.binding('A',False)))
  if current['identity']!=before['identity'] or current['button']!=before['button']:raise Refused('popup button lifetime/geometry changed before pair')
  baseline=d.interval_start();d.pointer_parent(current['button']['global']);parent.send('press 272',deadline);parent.send('release 272',deadline);rows=d.inspect()
  d.h.journal.full_pointer_interval(rows,baseline,role='P',instance=before['identity']['instance'],map_generation=before['identity']['mapGeneration'],surface_id=sid,expected_surface=current['button']['surface'],event_types=d.types,button=1)
  clicked=[row for row in rows if row['sequence']>baseline and row['event']=='popover-button-clicked' and row.get('instance')==before['identity']['instance'] and row.get('surfaceId')==sid]
  if len(clicked)!=1 or d.h.scene.current_role(rows,'P') is not None:raise Refused('one actual button action and local popup retirement')
  d.wait(lambda:not any(p.get('surface',{}).get('id')==sid and p['surface'].get('pid')==actor.pid for p in json.loads(session.ctl('elm_popup_state'))['popups']))
  d.check('GTK06:actual-popup-parent-grab-key-click-close',True,popup=current,rows=rows)

 def family_hidden_pixels(self,bounds,deadline):
  d=self.driver;directory=d.directory/('GTK07-hidden-family-'+str(time.time_ns()))
  rgb,record=d.h.pixels.capture(d.session,d.host,directory,deadline,selected={'originalBindings':bounds,'expectedHiddenFamily':['A','B']})
  samples={}
  for name,binding in bounds.items():
   sampled=d.h.pixels.yellow_marker(rgb,binding['marker']['global']);samples[name]=sampled
  record['markerSamples']=samples;(directory/'record.json').write_text(json.dumps(record,indent=2)+'\n')
  if any(any(pixel['rgb']==[255,255,0] for pixel in sample['samples']) for sample in samples.values()):raise Refused('actual minimized family marker remains visible')
  for name in bounds:
   current=d.fact(name)
   if not current['minimized'] or current['shouldRenderAny'] or current['acceptsInput']:raise Refused('actual family hidden state changed across capture')
