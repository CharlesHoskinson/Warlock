"""Joint physical Elm menu/native ACK/serial-RGB qualification, private tuple only."""
import importlib.util,json,os,signal,shutil,socket,struct,subprocess,sys,time,traceback
from pathlib import Path
SLICE=Path(__file__).resolve().parents[1];REPO=SLICE.parents[1]
ROOT=REPO/'implementation/elm-stable-surface-publication-v521';AUTH=SLICE/'runtime';FIXTURE=REPO/'implementation/elm-geometry-client-suspend-v53'
RELAY=SLICE/'relay-final';RELAY_MANIFEST_HASH='d29a5235bfa30c5bc471fb9b26cb481a90a80018f1a5b5e02fc72a822013a3ed'
RECEIPT=SLICE/'receipt-final';RECEIPT_MANIFEST_HASH='63678469f0fe517ac7fce2bc7eca9863b0735b59387175a030a4be34d92cbd6c'
BUILD=ROOT/'qa/build-1791138800386580258/report.json';BUILD_HASH='40d5fbc2853b9611a08e8aa9a7f4682671f298b17eb13ac0584284b47cc4f3b8'
spec=importlib.util.spec_from_file_location('v60_private_host',AUTH/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
sys.path.insert(0,str(SLICE/'qa'));import client_evidence as evidence
sys.path.insert(0,str(REPO/'implementation/elm-menu-native-pair-v8/qa'));from inspection import Collector
KEYBOARD=Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
LUA=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
report={'passed':False,'allContractScenariosPassed':False,'fullRoadmapAccepted':False,'nativeAcceptance':False,'mainDesktopActions':False,'scope':'Joint actual physical menu/native configure/ACK/serial-RGB with actual receipt-delivery hold; original V52 separately frozen','observerTransportPolicy':'Copied authenticated observer transport bounded by min(original3s,parent09six-second deadline); bootstrap remains original3s','checks':[],'scenarios':[]}
session=None;client=None;web=None;loaded=False;stopped=None;OUT=None;OUTPUT=None

def check(name,value,**data):
 report['checks'].append({'name':name,'passed':bool(value),**data});assert value,name

def wait(predicate,timed=False,deadline=None):
 if deadline is None:deadline=time.monotonic()+6
 while time.monotonic()<deadline:
  session.guard();value=predicate(deadline) if timed else predicate()
  if time.monotonic()>=deadline:raise RuntimeError('Whole-transition absolute six-second deadline')
  if value:return value
  time.sleep(min(.025,max(0,deadline-time.monotonic())))
 raise RuntimeError('Whole-transition absolute six-second deadline')

def load_relay():
 manifest=RELAY/'qa/held-source-manifest.json'
 assert host.digest(manifest)==RELAY_MANIFEST_HASH,'Reviewed relay source hold changed'
 packet=json.loads(manifest.read_text());assert packet['sourceHeld'] is True and packet['evidenceIntegrityPassed'] is True
 for relative,row in packet['files'].items():
  path=RELAY/relative
  if 'symlink' in row:assert path.is_symlink() and os.readlink(path)==row['symlink'],relative
  else:assert not path.is_symlink() and path.resolve().is_relative_to(RELAY.resolve()) and host.digest(path)==row['sha256'],relative
 for relative,target in packet.get('symlinks',{}).items():
  path=RELAY/relative;assert path.is_symlink() and os.readlink(path)==target,relative
 spec=importlib.util.spec_from_file_location('reviewed_qa_broker_relay',RELAY/'qa/relay.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def load_receipt():
 manifest=RECEIPT/'qa/held-source-manifest.json';assert host.digest(manifest)==RECEIPT_MANIFEST_HASH
 packet=json.loads(manifest.read_text());assert packet['sourceHeld'] is True and packet['evidenceIntegrityPassed'] is True
 for relative,row in packet['files'].items():
  path=RECEIPT/relative
  if 'symlink' in row:assert path.is_symlink() and os.readlink(path)==row['symlink'],relative
  else:assert not path.is_symlink() and path.resolve().is_relative_to(RECEIPT.resolve()) and host.digest(path)==row['sha256'] and path.stat().st_size==row['size'] and (path.stat().st_mode&0o777)==row['mode'],relative
 spec=importlib.util.spec_from_file_location('reviewed_receipt_controls',RECEIPT/'qa/wrapper.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def native_observer(config):
 sys.path.insert(0,str(BUILD.parent/'inputs/adapter'))
 from observer_endpoint import ObserverEndpoint
 observer=ObserverEndpoint(**config);hello=observer.hello();attached=observer.geometry_attach('1');facts=observer.geometry_facts('2')
 return observer,hello,attached,facts

def private_json(path,value):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(value,stream);stream.flush();os.fsync(stream.fileno())

def preflight():
 assert host.digest(BUILD)==BUILD_HASH;build=json.loads(BUILD.read_text());assert build['passed']
 for rel,digest in build['inputs'].items():assert host.digest(ROOT/rel)==digest and host.digest(BUILD.parent/'inputs'/rel)==digest
 for rel,digest in build['artifacts'].items():assert host.digest(BUILD.parent/rel)==digest
 assert host.digest(BUILD.parent/'elm-host')==build['binarySHA256']
 for section in ['compilerDependencies','linkedLibraries']:
  for path,row in build[section].items():assert host.digest(path)==(row['sha256'] if isinstance(row,dict) else row)
 pair=json.loads((AUTH/'qa/build-pair-manifest.json').read_text());assert pair['passed']
 for rel,digest in pair['files'].items():assert host.digest(AUTH/rel)==digest
 for row in pair['nativePair'].values():assert host.digest(row['path'])==row['sha256']
 producer=Path(pair['producerEvidence']);assert host.digest(producer)==pair['producerEvidenceSHA256']
 for entry in json.loads(producer.read_text())['files']:assert host.digest(REPO/entry['path'])==entry['sha256']
 probe=json.loads((AUTH/'parent-probe-build.json').read_text());assert host.digest(probe['buildReport'])==probe['buildReportSHA256'];p=json.loads(Path(probe['buildReport']).read_text());assert p['passed'];pointer=Path(p['client']);assert host.digest(pointer)==p['clientSHA256']
 descriptor=json.loads((FIXTURE/'client-build-report.json').read_text());assert descriptor['requiresXdgVersion']==6 and descriptor['suspendedStateObserved'] is True
 assert host.digest(descriptor['client'])==descriptor['clientSHA256'];assert host.digest(descriptor['buildReport'])==descriptor['buildReportSHA256'];fb=json.loads(Path(descriptor['buildReport']).read_text());assert fb['passed']
 for section in ['inputs','dependencies','tools','linkedLibraries']:
  for path,digest in fb[section].items():assert host.digest(path)==digest
 for rel,digest in fb['artifacts'].items():assert host.digest(Path(descriptor['buildReport']).parent/rel)==digest
 assert callable(load_receipt().write_release);relay=load_relay();assert all(callable(getattr(relay,n)) for n in ['close_stdin','actor_status','exit_status'])
 return build,pair,pointer,descriptor

def run():
 global session,client,web,loaded,stopped,OUT,OUTPUT
 host.original.qa.require_qa_scope();OUT=SLICE/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-geometry-menu-'+str(time.time_ns()))
 try:
  build,pair,pointer,fixture=preflight();binary=BUILD.parent/'elm-host';backend_path=BUILD.parent/'inputs/adapter/daemon.py';plugin=pair['nativePair']['plugin']['path']
  paths=[Path(__file__),AUTH/'candidate_host.py',RELAY/'qa/relay.py',RELAY/'qa/held-source-manifest.json',RECEIPT/'qa/wrapper.py',RECEIPT/'qa/broker-entrypoint.py',RECEIPT/'qa/held-source-manifest.json',REPO/'implementation/elm-gtk-current-tuple-adoption-review-v254/component-manifest.json',AUTH/'native-build-report.json',AUTH/'qa/build-pair-manifest.json',Path(pair['producerEvidence']),SLICE/'origin.json',SLICE/'qa/client_evidence.py',SLICE/'qa/observer_endpoint.py',KEYBOARD,Path(pointer),BUILD,FIXTURE/'client-build-report.json',REPO/'implementation/elm-menu-native-pair-v8/qa/inspection.py']
  report.update(buildReport=str(BUILD),buildReportSHA256=BUILD_HASH,pair=pair['nativePair'],inputs={str(p):host.digest(p) for p in paths})
  for i,p in enumerate(paths):dest=OUT/'inputs'/str(i)/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as session:
   try:
    parent=next(row for _,row in session.host.processes if row['name']=='weston');parent_socket=session.host.runtime/'weston-host';socket_identity=host.original.socket_identity(parent_socket,session.host.runtime)
    with socket.socket(socket.AF_UNIX) as probe:
     probe.settimeout(2);probe.connect(str(parent_socket));pid,uid,gid=struct.unpack('3i',probe.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    check('parentSocketAndProcessExact',pid==parent['pid'] and uid==os.getuid() and host.original.same_process(parent))
    check('pluginLoad',session.ctl('plugin','load',plugin).strip()=='ok');loaded=True
    compositor=next(row for _,row in session.host.processes if row['name']=='hyprland');maps=host.original.mapped_files(compositor['pid']);check('pluginMapExact',maps['files'].get(str(Path(plugin).resolve()))==pair['nativePair']['plugin']['sha256']);report['pluginMapsAfterLoad']=maps
    config={'runtime':str(session.host.runtime),'instance':session.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':compositor['pid'],'expected_start':'','binary_sha256':pair['nativePair']['core']['sha256']}
    # Process helper uses startTime on some archived versions; derive Linux start directly.
    raw=Path('/proc',str(compositor['pid']),'stat').read_text();config['expected_start']=raw[raw.rfind(')')+2:].split()[19]
    config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
    client_log=OUTPUT/'xdg-max-client.log';stream=os.fdopen(os.open(client_log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb');session.host.logs.append(stream)
    client=subprocess.Popen([fixture['client']],stdin=subprocess.PIPE,stdout=stream,stderr=subprocess.STDOUT,env=dict(session.env,WAYLAND_DEBUG='1'),cwd=session.host.runtime,start_new_session=True)
    client_identity=host.original.process(client.pid);client_identity.update(name='xdg-max-client',command=[fixture['client']],log=str(client_log));session.host.processes.append((client,client_identity))
    evidence.session=session;evidence.client=client;evidence.host=host;evidence.client_identity=client_identity;evidence.client_log=client_log;evidence.report=report;evidence.check=check;evidence.wait=wait;evidence.OUTPUT=OUTPUT
    wait(lambda:any(r['event']=='ready' for r in evidence.events()));native=wait(evidence.native_window);report['fixtureIdentity']={'pid':client.pid,'address':native['address'],'title':native['title'],'stableId':native['stableId']}
    selector=json.dumps('address:'+native['address'])
    for operation,fields in [('float','action="enable"'),('resize','x=320,y=180,relative=false'),('move','x=83,y=61,relative=false')]:
     expression='hl.dsp.window.'+operation+'({'+fields+',window='+selector+'})';check('ordinaryPlacement:'+operation,session.ctl('eval','local r=hl.dispatch('+expression+');if type(r)~="table" or r.ok~=true then error("placement refused") end').strip()=='ok')
    wait(lambda:evidence.settled(0) if evidence.native_window()['at']==[83,61] and evidence.native_window()['size']==[320,180] else None)
    env=dict(session.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')
    relay=load_relay();relay_control=OUTPUT/'relay-actor-1';relay_control.mkdir(mode=0o700)
    observer,observer_hello,observer_attach,observer_facts=native_observer(config)
    assert len(observer_facts['facts']['windows'])==1;selected_identity=observer_facts['facts']['windows'][0]['incarnation']
    report['bootstrapNativeObserver']={'peer':host.original.process(os.getpid()),'hello':observer_hello,'attach':observer_attach,'facts':observer_facts,'scope':'Separate authenticated observation peer; never injected into Elm'}
    receipt=load_receipt();receipt_control=OUTPUT/'receipt-actor-1';receipt_control.mkdir(mode=0o700);private_json(receipt_control/'gate.json',{'action':'hold'})
    receipt_config=OUTPUT/'receipt-config.json';private_json(receipt_config,{'authorityConfig':str(config_path),'controlDirectory':str(receipt_control),'incarnation':selected_identity,'effectOperation':'restore-geometry','selectorOrdinal':2})
    relay_config=OUTPUT/'relay-config.json';private_json(relay_config,{'profile':'receipt','receiptConfig':str(receipt_config),'controlDirectory':str(relay_control),'runtime':config['runtime'],'instance':config['instance']})
    captured_backend=RECEIPT/'qa/broker-entrypoint.py';backend_path=RELAY/'qa/relay.py'
    web=session.host.launch('elm-webview',[str(binary),'--assets',str(BUILD.parent/'inputs/assets'),'--backend',str(backend_path),'--authority-config',str(relay_config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=env)
    log=OUTPUT/'elm-webview.log';collector=Collector()
    def frames(prefix):return [json.loads(line[len(prefix):]) for line in log.read_text(errors='replace').splitlines() if line.startswith(prefix)] if log.exists() else []
    def projection():return collector.read(log.read_text(errors='replace')) if log.exists() else None
    def incoming():return frames('backend-frame: ')
    def effects():return [r for r in frames('frontend-request: ') if r['kind']=='window-effect']
    def geometry():return next((r for r in reversed(incoming()) if r.get('kind')=='geometry-facts'),None)
    identity=None
    def geometry_row():
     if not geometry():return None
     rows=geometry()['facts']['windows']
     return next((r for r in rows if r['incarnation']==identity),None) if identity else rows[0] if len(rows)==1 else None
    def coherent():return projection() if projection() and projection()['phase']=='Coherent' else None
    wait(lambda:coherent() and geometry_row());identity=geometry_row()['incarnation'];report['nativeIncarnation']=identity
    check('receiptSelectorUsesActualNativeIncarnation',identity==selected_identity and observer_hello['binding']['lifetime']==geometry()['binding']['lifetime'])
    attach=next(r for r in reversed(incoming()) if r.get('kind')=='geometry-attached');hello=next(r for r in reversed(incoming()) if r.get('kind')=='attached')
    check('observerHasIndependentPeerBinding',observer_hello['binding']['lifetime']==hello['binding']['lifetime'] and observer_hello['binding']['session']!=hello['binding']['session'])
    check('helloThenExplicitGeometryNegotiation',hello['binding']==attach['binding']==geometry()['binding'] and attach['capabilities']['effects'] is True and attach['capabilities']['operations']==['maximize','restore-geometry'])
    check('separateCorrelatedLegacyGeometryObservations',any(r.get('kind')=='action-projection' and r['binding']==attach['binding'] and r['requestId']!=geometry()['requestId'] for r in incoming()))
    def row(state):
     p=coherent();return next((r for r in p['picker']['selections'] if r['incarnation']==identity and r['state']==state and not r['disabled']),None) if p and p['picker'] else None
    def parent_pointer(item,button,deadline):
     x,y=[round(v) for v in item['point']];assert 0<x<800 and 0<y<600;session.guard();assert host.original.same_process(parent) and socket_identity==host.original.socket_identity(parent_socket,session.host.runtime)
     remaining=deadline-time.monotonic();assert remaining>0;result=subprocess.run([str(pointer)],input=f'motion {x} {y}\npress {button}\nrelease {button}\nquit\n',text=True,capture_output=True,env=dict(session.host.env,ELM_PARENT_INPUT_QA='1'),cwd=session.host.runtime,timeout=min(3,remaining));acks=[json.loads(line) for line in result.stdout.splitlines()]
     check('physicalParentClick',result.returncode==0 and len(acks)==4 and acks[0].get('ready') is True and all(r.get('accepted') is True for r in acks[1:]),point=[x,y],button=button,acks=acks);assert time.monotonic()<deadline
    def open_menu(state='Open',deadline=None):
     if deadline is None:deadline=time.monotonic()+6
     expected_minimized=state=='Minimized'
     current=wait(lambda:geometry_row() if coherent() and geometry_row() and geometry_row()['minimized']==expected_minimized else None,deadline=deadline)
     legacy=wait(lambda:next((r for r in reversed(incoming()) if r.get('kind')=='action-projection' and r['binding']==geometry()['binding'] and any(w['incarnation']==identity and w['minimized']==expected_minimized and w['available'] and w['owner'] is None for w in r['scene']['windows'])),None),deadline=deadline)
     roots=[w for w in legacy['scene']['windows'] if w['application']=='elm-maximize-probe' and w['owner'] is None and w['available']]
     check('openingMenuExactRootAndState',current['incarnation']==identity and any(w['incarnation']==identity for w in roots),state=state,geometry=current,roots=roots)
     before=len(effects())
     if len(roots)==1:
      check('singletonBarSecondaryTargetsFixture',roots[0]['incarnation']==identity)
      group=wait(lambda:next((g for g in coherent()['groups'] if g['key']=='application:elm-maximize-probe' and not g['disabled']),None) if coherent() else None,deadline=deadline)
      parent_pointer(group,273,deadline)
     else:
      if not row(state):
       group=wait(lambda:next((g for g in coherent()['groups'] if g['key']=='application:elm-maximize-probe' and not g['disabled']),None) if coherent() else None,deadline=deadline)
       parent_pointer(group,273,deadline)
      target=wait(lambda:row(state),deadline=deadline);parent_pointer(target,273,deadline)
     menu=wait(lambda:coherent()['menu'] if coherent() else None,deadline=deadline)
     check('rightClickReleaseOnlyOpensMenu',len(effects())==before and menu['incarnation']==identity,menu=menu);return menu
    def action(menu,label):return next(a for a in menu['actions'] if a['label']==label)
    def settle_menu(label,operation,protocol,mode,suspended=False,held=False):
     nonlocal before
     global stopped
     deadline=time.monotonic()+6;menu=open_menu('Minimized' if operation=='restore' else 'Open',deadline);item=action(menu,label);check(label+':enabled',not item['disabled'])
     if held:
      owned_backends=[]
      for owned in session.host.descendants():
       try:args=Path('/proc',str(owned['pid']),'cmdline').read_bytes().split(b'\0')
       except FileNotFoundError:continue
       if args[:3]==[b'/usr/bin/python3',b'-B',str(backend_path).encode()]:owned_backends.append(owned)
      check('heldBackendExactUniqueOwned',len(owned_backends)==1)
      stopped=owned_backends[0]['pid'];assert host.original.same_process(owned_backends[0]);os.kill(stopped,signal.SIGSTOP)
     before=evidence.latest_buffer();previous_geometry_sequence=int(geometry()['sequence']);dispatched_lease=projection()['lease'];count=len(effects());start_inspection=len(frames('surface-inspection: '));parent_pointer(item,272,deadline)
     issued=wait(lambda:effects()[-1] if len(effects())==count+1 else None,deadline=deadline);intent=issued['intent'];check(label+':exactOperationNamespace',issued['effectProtocol']==protocol and intent['operation']==operation and intent['incarnation']==identity)
     pending=wait(lambda:next((r['body'] for r in frames('surface-inspection: ')[start_inspection:] if r['body']['menu'] is None and r['body']['outstanding']==1),None),deadline=deadline)
     check(label+':pendingPopupClosed',pending['menu'] is None and pending['outstanding']==1,pending=pending)
     if held:
      check('heldPendingClosesPopupAndNoOutcome',pending['menu'] is None and pending['outstanding']==1 and not any(r.get('kind')=='effect-outcome' and r.get('intent')==intent for r in incoming()))
      time.sleep(min(.2,max(0,deadline-time.monotonic())));check('heldNoDuplicateDispatch',len(effects())==count+1);os.kill(stopped,signal.SIGCONT);stopped=None
     receipt=wait(lambda:next((r for r in incoming() if r.get('kind')=='effect-outcome' and r.get('intent')==intent and r.get('binding')==issued['binding'] and r.get('effectProtocol')==protocol),None),deadline=deadline)
     check(label+':definitiveFullCorrelation',receipt['status']=='Committed',issued=issued,receipt=receipt)
     native,buffer=wait(lambda:evidence.settled(mode,before['sequence'],suspended),deadline=deadline);facts=wait(lambda:geometry_row() if geometry_row() and int(geometry()['sequence'])>previous_geometry_sequence and geometry_row()['minimized']==suspended and geometry_row()['nativeMode']==('maximized' if mode else 'ordinary') and geometry_row()['visualGeometry']==[*native['at'],*native['size']] else None,deadline=deadline)
     wait(lambda:coherent() if coherent() and coherent()['menu'] is None and coherent()['outstanding']==0 else None,deadline=deadline)
     check(label+':oneIntentOnly',len(effects())==count+1)
     log_lines=log.read_text(errors='replace').splitlines();closed_indices=[i for i,line in enumerate(log_lines) if line.startswith('surface-popup-closed: lease='+dispatched_lease)];dispatch_index=next(i for i,line in enumerate(log_lines) if line.startswith('frontend-request: ') and json.loads(line.split(': ',1)[1])==issued)
     check(label+':nativePopupRetiredBeforeEffectQueue',any(i<dispatch_index for i in closed_indices),lease=dispatched_lease)
     check(label+':selectedBufferUsesActualConfigureAck',buffer['serial']==buffer['ackedSerial'] and any(r['event']=='configure' and r['serial']==buffer['serial'] and r['ackedSerial']==buffer['serial'] and r['sequence']<buffer['sequence'] and [r['width'],r['height']]==native['size'] and r['suspended']==suspended for r in evidence.events()),buffer=buffer)
     if suspended:check(label+':realSuspendedAndInputBlocked',buffer['suspended'] is True and native['acceptsInput'] is False and facts['ordinaryPlacementKnown'] is True,buffer=buffer,facts=facts)
     else:
      if mode:
       area=facts['workArea'];check(label+':exactWorkAreaWithBorder',facts['logicalGeometry']==area and native['at']==[area[0]+1,area[1]+1] and native['size']==[area[2]-2,area[3]-2],facts=facts,native=native)
      else:check(label+':exactOriginalPlacement',native['at']==[83,61] and native['size']==[320,180] and facts['ordinaryPlacementKnown'] is False,facts=facts)
      evidence.validate_pixels(operation,native,buffer,deadline)
     report.setdefault('transitions',[]).append({'label':label,'deadlineSeconds':6,'finishedBeforeDeadline':time.monotonic()<deadline,'issued':issued,'receipt':receipt,'facts':facts,'buffer':buffer});return facts
    before=None
    menu=open_menu();check('ordinaryMenuGeometryCapabilities',not action(menu,'Maximize')['disabled'] and action(menu,'Restore')['disabled'],menu=menu)
    # Close via physical dedicated menu-dismiss control before next transition.
    parent_pointer(menu['close'],272,time.monotonic()+6);wait(lambda:coherent() if coherent() and coherent()['menu'] is None else None)
    report['scenarios']+=['GEOMETRY-MENU-01','GEOMETRY-MENU-02']
    settle_menu('Maximize','maximize',2,1);report['scenarios'].append('GEOMETRY-MENU-03')
    settle_menu('Minimize','minimize',1,1,True);report['scenarios'].append('GEOMETRY-MENU-04')
    settle_menu('Restore','restore',1,1);report['scenarios'].append('GEOMETRY-MENU-05')
    settle_menu('Restore','restore-geometry',2,0);report['scenarios'].append('GEOMETRY-MENU-06')
    check('receiptActorOneForwardsFirstRestoreGeometry',not (receipt_control/'held.json').exists() and report['transitions'][-1]['receipt']['status']=='Committed' and report['transitions'][-1]['receipt']['intent']['operation']=='restore-geometry')
    report['receiptActorOneForwarded06']=report['transitions'][-1]['receipt']
    # External client changes produce real broker notifications and fresh observations.
    count=len(effects());previous=geometry();deadline=time.monotonic()+6;evidence.request('maximize',deadline)
    native,buffer=wait(lambda:evidence.settled(1),deadline=deadline);wait(lambda:geometry_row() if geometry_row() and geometry_row()['nativeMode']=='maximized' and int(geometry()['sequence'])>int(previous['sequence']) else None,deadline=deadline)
    menu=open_menu(deadline=deadline);check('externalMaxUpdatesMenuWithoutEffect',len(effects())==count and action(menu,'Maximize')['disabled'] and action(menu,'Restore')['disabled'],menu=menu,geometry=geometry());parent_pointer(menu['close'],272,deadline)
    wait(lambda:coherent() if coherent() and coherent()['menu'] is None else None,deadline=deadline);evidence.validate_pixels('external-max',native,buffer,deadline)
    deadline=time.monotonic()+6;evidence.request('unmaximize',deadline);wait(lambda:evidence.settled(0),deadline=deadline);wait(lambda:geometry_row() if geometry_row() and geometry_row()['nativeMode']=='ordinary' else None,deadline=deadline);menu=open_menu(deadline=deadline);check('externalOrdinaryRefreshNoReplay',len(effects())==count and not action(menu,'Maximize')['disabled'],menu=menu);parent_pointer(menu['close'],272,deadline);wait(lambda:coherent() if coherent() and coherent()['menu'] is None else None,deadline=deadline)
    report['scenarios'].append('GEOMETRY-MENU-07')
    # Reconnect occurs after a saved native MAX origin exists.
    settle_menu('Maximize','maximize',2,1);old_binding=geometry()['binding'];count=len(effects());deadline=time.monotonic()+6
    check('reconnectQuiescentBeforeEOF',coherent() is not None and coherent()['outstanding']==0 and coherent()['registry']==0 and coherent()['transaction']=='Committed' and len(effects())==count)
    actor=relay.actor_status(relay_control);owned={row['pid']:row for row in session.host.descendants()}
    for kind in ['relay','child']:
     record=actor[kind];check('reconnectExactOwnedActor:'+kind,record['pid'] in owned and owned[record['pid']]['start']==record['start'] and host.original.same_process(owned[record['pid']]))
    child_command=[part for part in Path('/proc',str(actor['child']['pid']),'cmdline').read_bytes().split(b'\0') if part]
    relay_command=[part for part in Path('/proc',str(actor['relay']['pid']),'cmdline').read_bytes().split(b'\0') if part]
    check('reconnectExactCapturedBrokerAndRelayCommands',child_command==[b'/usr/bin/python3',b'-B',str(captured_backend).encode(),str(receipt_config).encode()] and relay_command==[b'/usr/bin/python3',b'-B',str(backend_path).encode(),str(relay_config).encode()])
    old_log_size=len(log.read_text(errors='replace').splitlines());old_config_bytes=relay_config.read_bytes();old_receipt_bytes=receipt_config.read_bytes();relay.close_stdin(relay_control)
    def eof_status():
     if not (relay_control/'exit.json').exists() or (relay_control/'exit.json').stat().st_size==0:return None
     status=relay.exit_status(relay_control)
     check('reconnectOwnedBrokerNormalEOF',status['relay']==actor['relay'] and status['child']==actor['child'] and status['childExit']==0 and status['stdinClosed'] is True,status=status)
     return status
    retired_actor=wait(eof_status,deadline=deadline)
    wait(lambda:projection() if projection() and projection()['phase']=='Detached' and projection()['reconnect'] else None,deadline=deadline)
    wait(lambda:True if not host.original.same_process(owned[actor['relay']['pid']]) and not host.original.same_process(owned[actor['child']['pid']]) else None,deadline=deadline)
    check('reconnectHostObservedNormalRelayExit',any(line=='backend-exit: waited=1 normal=1 code=0' for line in log.read_text(errors='replace').splitlines()[old_log_size:]))
    check('reconnectNoNativeEffectDuringDisconnect',len(effects())==count and projection()['outstanding']==0 and projection()['registry']==0)
    private_json(OUTPUT/'relay-config-actor-1.json',json.loads(old_config_bytes));check('reconnectRetiredConfigArchivedExact', (OUTPUT/'relay-config-actor-1.json').read_bytes()==old_config_bytes);relay_control=OUTPUT/'relay-actor-2';relay_control.mkdir(mode=0o700)
    private_json(OUTPUT/'receipt-config-actor-1.json',json.loads(old_receipt_bytes));check('receiptActorOneConfigArchivedExact',(OUTPUT/'receipt-config-actor-1.json').read_bytes()==old_receipt_bytes)
    receipt_control=OUTPUT/'receipt-actor-2';receipt_control.mkdir(mode=0o700);private_json(receipt_control/'gate.json',{'action':'hold'})
    next_receipt=OUTPUT/'receipt-config-next.json';private_json(next_receipt,{'authorityConfig':str(config_path),'controlDirectory':str(receipt_control),'incarnation':identity,'effectOperation':'restore-geometry','selectorOrdinal':1});old_receipt_inode=receipt_config.stat().st_ino;os.replace(next_receipt,receipt_config);check('receiptActorTwoFreshConfiguration',receipt_config.stat().st_ino!=old_receipt_inode)
    next_config=OUTPUT/'relay-config-next.json';private_json(next_config,{'profile':'receipt','receiptConfig':str(receipt_config),'controlDirectory':str(relay_control),'runtime':config['runtime'],'instance':config['instance']});os.replace(next_config,relay_config)
    report['reconnectFixture']={'retiredActor':actor,'normalEOF':retired_actor,'oldConfigSHA256':__import__('hashlib').sha256(old_config_bytes).hexdigest(),'newConfigSHA256':host.digest(relay_config),'actualDetachedBeforePhysicalClick':True,'deadlineSeconds':6,'oldReceiptConfigSHA256':__import__('hashlib').sha256(old_receipt_bytes).hexdigest(),'newReceiptConfigSHA256':host.digest(receipt_config),'receiptActorOneOrdinal':2,'receiptActorTwoOrdinal':1}
    parent_pointer(wait(lambda:projection()['reconnect'] if projection() and projection()['phase']=='Detached' else None,deadline=deadline),272,deadline)
    new_attach=wait(lambda:next((r for r in reversed(incoming()) if r.get('kind')=='geometry-attached' and r['binding']!=old_binding),None),deadline=deadline)
    wait(lambda:coherent() and geometry_row() and geometry()['binding']==new_attach['binding'] and geometry_row()['ordinaryPlacementKnown'],deadline=deadline)
    new_actor=relay.actor_status(relay_control);check('reconnectFreshBrokerActor',new_actor['relay']!=actor['relay'] and new_actor['child']!=actor['child']);new_owned={r['pid']:r for r in session.host.descendants()}
    for kind in ['relay','child']:
     record=new_actor[kind];check('reconnectNewActorOwned:'+kind,record['pid'] in new_owned and new_owned[record['pid']]['start']==record['start'] and host.original.same_process(new_owned[record['pid']]))
    check('reconnectFreshActorFixedCommands',Path('/proc',str(new_actor['child']['pid']),'cmdline').read_bytes().split(b'\0')[:-1]==[b'/usr/bin/python3',b'-B',str(captured_backend).encode(),str(receipt_config).encode()] and Path('/proc',str(new_actor['relay']['pid']),'cmdline').read_bytes().split(b'\0')[:-1]==[b'/usr/bin/python3',b'-B',str(backend_path).encode(),str(relay_config).encode()]);report['reconnectFixture']['newActor']=new_actor
    menu=open_menu(deadline=deadline);check('reconnectRenegotiatesPreservingSavedOriginNoReplay',not action(menu,'Restore')['disabled'] and action(menu,'Maximize')['disabled'] and len(effects())==count and new_attach['binding']['lifetime']==old_binding['lifetime'],oldBinding=old_binding,newAttach=new_attach,geometry=geometry());parent_pointer(menu['close'],272,deadline);wait(lambda:coherent() if coherent() and coherent()['menu'] is None else None,deadline=deadline)
    report['scenarios'].append('GEOMETRY-MENU-08')
    # Delivery fault holds an already committed native receipt, not the native operation.
    deadline=time.monotonic()+6;menu=open_menu('Open',deadline);item=action(menu,'Restore');check('heldRestoreGeometryEnabled',not item['disabled'])
    before=evidence.latest_buffer();previous_geometry_sequence=int(geometry()['sequence']);dispatched_lease=projection()['lease'];count=len(effects());inspection_start=len(frames('surface-inspection: '))
    parent_pointer(item,272,deadline)
    issued=wait(lambda:effects()[-1] if len(effects())==count+1 else None,deadline=deadline)
    check('heldExactRestoreGeometryNamespace',issued['effectProtocol']==2 and issued['intent']['operation']=='restore-geometry' and issued['intent']['incarnation']==identity)
    def held_marker():
     path=receipt_control/'held.json'
     return relay.read_private(path) if path.exists() and path.stat().st_size else None
    held=wait(held_marker,deadline=deadline);held_receipt=held['receipt'];owner=held['wrapper'];current_owned={r['pid']:r for r in session.host.descendants()}
    check('heldReceiptOwnerIsExactLiveActorTwo',owner==new_actor['child'] and owner['pid'] in current_owned and current_owned[owner['pid']]['start']==owner['start'] and host.original.same_process(current_owned[owner['pid']]))
    check('heldReceiptIsActualFullCommittedKey',held['effectProtocol']==2 and held['binding']==issued['binding'] and held['intent']==issued['intent'] and held_receipt['effectProtocol']==2 and held_receipt['binding']==issued['binding'] and held_receipt['intent']==issued['intent'] and held_receipt['status']=='Committed')
    pending=wait(lambda:projection() if projection() and projection()['menu'] is None and projection()['outstanding']==1 and projection()['registry']==1 and projection()['transaction']=='Pending' else None,deadline=deadline)
    def matching_outcomes():return [r for r in incoming() if r.get('kind')=='effect-outcome' and r.get('effectProtocol')==2 and r.get('binding')==issued['binding'] and r.get('intent')==issued['intent']]
    check('heldPendingClosesPopupAndNoOutcome',pending['menu'] is None and pending['outstanding']==1 and not matching_outcomes(),pending=pending)
    native,buffer=wait(lambda:evidence.settled(0,before['sequence'],False),deadline=deadline)
    observer.parentDeadline=deadline
    try:fresh=wait(lambda:observer.geometry_facts('3'),deadline=deadline)
    finally:observer.parentDeadline=float('inf')
    fresh_row=next(r for r in fresh['facts']['windows'] if r['incarnation']==identity)
    check('heldNativeRestoreCommittedBeforeDelivery',fresh_row['nativeMode']=='ordinary' and not fresh_row['minimized'] and not fresh_row['ordinaryPlacementKnown'] and fresh_row['visualGeometry']==[*native['at'],*native['size']] and native['at']==[83,61] and native['size']==[320,180],observerFacts=fresh)
    def notification_after_intent():
     lines=log.read_text(errors='replace').splitlines();index=next(i for i,line in enumerate(lines) if line.startswith('frontend-request: ') and json.loads(line.split(': ',1)[1])==issued)
     return next((json.loads(line.split(': ',1)[1]) for line in lines[index+1:] if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind')=='host-refresh'),None)
    notification=wait(notification_after_intent,deadline=deadline)
    check('heldRealNotificationWhilePending',notification['kind']=='host-refresh' and projection()['menu'] is None and projection()['transaction']=='Pending' and projection()['outstanding']==1 and projection()['registry']==1 and not matching_outcomes() and len(effects())==count+1)
    check('heldSelectedBufferUsesActualConfigureAck',buffer['serial']==buffer['ackedSerial'] and buffer['suspended'] is False and any(r['event']=='configure' and r['serial']==buffer['serial'] and r['ackedSerial']==buffer['serial'] and r['sequence']<buffer['sequence'] and [r['width'],r['height']]==native['size'] and r['suspended'] is False for r in evidence.events()),buffer=buffer)
    evidence.validate_pixels('held-restore-geometry',native,buffer,deadline)
    check('heldNoDuplicateDispatch',len(effects())==count+1 and not matching_outcomes())
    release=receipt.write_release(receipt_control)
    delivered=wait(lambda:matching_outcomes()[0] if matching_outcomes() else None,deadline=deadline)
    check('heldExactOriginalReceiptReleasedOnce',delivered==held_receipt and len(matching_outcomes())==1)
    facts=wait(lambda:geometry_row() if geometry_row() and int(geometry()['sequence'])>previous_geometry_sequence and not geometry_row()['minimized'] and geometry_row()['nativeMode']=='ordinary' and geometry_row()['visualGeometry']==[*native['at'],*native['size']] else None,deadline=deadline)
    wait(lambda:coherent() if coherent() and coherent()['menu'] is None and coherent()['outstanding']==0 and coherent()['registry']==0 else None,deadline=deadline)
    check('heldOneIntentOnlyAfterRefresh',len(effects())==count+1 and len(matching_outcomes())==1)
    lines=log.read_text(errors='replace').splitlines();dispatch_index=next(i for i,line in enumerate(lines) if line.startswith('frontend-request: ') and json.loads(line.split(': ',1)[1])==issued)
    check('heldNativePopupRetiredBeforeEffectQueue',any(i<dispatch_index and line.startswith('surface-popup-closed: lease='+dispatched_lease) for i,line in enumerate(lines)))
    report['receiptHold09']={'scope':'Actual native commit with delivery held; separate observer facts are never injected into Elm','held':held,'issued':issued,'pending':pending,'notification':notification,'observerFacts':fresh,'buffer':buffer,'receipt':delivered,'freshElmFacts':facts,'deadlineSeconds':6,'finishedBeforeDeadline':time.monotonic()<deadline}
    report['scenarios'].append('GEOMETRY-MENU-09')
    # Retire the exact open-menu target, then map a fresh same-title/application client.
    deadline=time.monotonic()+6;menu=open_menu(deadline=deadline);count=len(effects());retired_pid=client.pid;client.stdin.write(b'quit\n');client.stdin.flush();client.wait(timeout=max(.001,deadline-time.monotonic()));check('retiredClientNormalExit',client.returncode==0)
    wait(lambda:coherent() if coherent() and coherent()['menu'] is None and all(r['incarnation']!=identity for r in geometry()['facts']['windows']) else None,deadline=deadline)
    replacement_log=OUTPUT/'replacement-xdg.log';replacement_stream=os.fdopen(os.open(replacement_log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb');session.host.logs.append(replacement_stream)
    client=subprocess.Popen([fixture['client']],stdin=subprocess.PIPE,stdout=replacement_stream,stderr=subprocess.STDOUT,env=dict(session.env,WAYLAND_DEBUG='1'),cwd=session.host.runtime,start_new_session=True);replacement_identity=host.original.process(client.pid);replacement_identity.update(name='replacement-xdg-client',command=[fixture['client']],log=str(replacement_log));session.host.processes.append((client,replacement_identity))
    replacement=wait(lambda:next((w for w in session.data('clients') if w.get('pid')==client.pid and w.get('title')=='ELM-MAXIMIZE-PROBE'),None),deadline=deadline)
    replacement_fact=wait(lambda:next((r for r in geometry()['facts']['windows'] if r['incarnation']!=identity),None),deadline=deadline)
    report['retirementAddressDiagnostic']={'originalAddress':report['fixtureIdentity']['address'],'replacementAddress':replacement['address'],'addressReused':replacement['address']==report['fixtureIdentity']['address'],'scope':'Address allocation is not lifetime identity; original431 address assertion preserved as failed evidence'}
    check('retirementNeverTargetsSameTitleReplacement',client.pid!=retired_pid and replacement['stableId']!=report['fixtureIdentity']['stableId'] and replacement_fact['incarnation']!=identity and replacement['fullscreen']==replacement['fullscreenClient']==0 and not replacement_fact['minimized'] and len(effects())==count and coherent()['menu'] is None,replacement=replacement,geometry=replacement_fact)
    report['scenarios'].append('GEOMETRY-MENU-10')
    for path,value in report['inputs'].items():assert host.digest(path)==value,path
    report.update(passed=True,allContractScenariosPassed=False,fullRoadmapAccepted=False,geometryMenuCompleteAccepted=False)

   finally:
    if stopped:
     try:os.kill(stopped,signal.SIGCONT)
     except ProcessLookupError:pass
     stopped=None
    if client and client.poll() is None:
     client.stdin.write(b'quit\n');client.stdin.flush();client.wait(timeout=6);check('normalXdgClientExit',client.returncode==0)
    if web and web.poll() is None:
     owned=next(r for p,r in session.host.processes if p is web);session.host.stop(owned,web);web.wait(timeout=6);check('normalWebviewAndBackendExit',web.returncode==0)
    if loaded:
     wait(lambda:True if not session.data('clients') else None)
     check('nativeFixtureClientsEmptyBeforeUnload',session.data('clients')==[])
     assert session.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
    registered={r['pid'] for _,r in session.host.processes}
    for descendant in reversed([r for r in session.host.descendants() if r['pid'] not in registered]):session.host.stop(descendant)
 except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
 report['privateHost']=session.evidence if session else None;report['cleanupPassed']=bool(session and session.evidence.get('runtimeGone') and not session.evidence.get('cleanupErrors') and not session.evidence.get('remainingDescendants') and not session.evidence.get('unexpectedInnerDescendants'))
 report['passed']=report['passed'] and report['cleanupPassed']
 if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',symlinks=True)
 report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));return not report['passed']
if __name__=='__main__':
 if sys.argv[1:]==['--preflight']:
  host.original.qa.require_qa_scope();output=SLICE/'qa'/('fault-preflight-'+str(time.time_ns()));output.mkdir();result={'passed':False,'nativeAcceptance':False}
  (output/'fault-native.py').write_bytes(Path(__file__).read_bytes())
  try:
   build,pair,pointer,fixture=preflight();result.update(passed=True,pair=pair['nativePair'],client=fixture['client'])
  except BaseException as error:result.update(error=repr(error),traceback=traceback.format_exc())
  (output/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(output/'report.json');raise SystemExit(0 if result['passed'] else 1)
 if sys.argv[1:]:raise SystemExit('No arbitrary companion arguments')
 raise SystemExit(run())
