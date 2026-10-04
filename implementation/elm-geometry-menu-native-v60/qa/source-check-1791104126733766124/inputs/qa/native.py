"""Joint physical Elm menu/native ACK/serial-RGB qualification, private tuple only."""
import importlib.util,json,os,signal,shutil,socket,struct,subprocess,sys,time,traceback
from pathlib import Path
SLICE=Path(__file__).resolve().parents[1];REPO=SLICE.parents[1]
ROOT=REPO/'implementation/elm-geometry-integrated-menu-v59';AUTH=REPO/'implementation/elm-window-geometry-owning-pair-v49';FIXTURE=REPO/'implementation/elm-geometry-client-suspend-v53'
BUILD=ROOT/'qa/build-1791103452303629948/report.json';BUILD_HASH='b0320e54bcd2f3b58dbb5702e07ae2d58b821473fd8cb1b3c5d90fd382da73b4'
spec=importlib.util.spec_from_file_location('v60_private_host',SLICE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
sys.path.insert(0,str(SLICE/'qa'));import client_evidence as evidence
sys.path.insert(0,str(REPO/'implementation/elm-menu-native-pair-v8/qa'));from inspection import Collector
KEYBOARD=Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
LUA=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
report={'passed':False,'nativeAcceptance':False,'mainDesktopActions':False,'scope':'Joint actual physical menu and native configure/ACK/serial-RGB campaign; original V52 separately frozen','checks':[],'scenarios':[]}
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

def preflight():
 assert host.digest(BUILD)==BUILD_HASH;build=json.loads(BUILD.read_text());assert build['passed'] is True
 for relative,value in build['inputs'].items():
  if relative not in ('assets/elm.js','assets/popup.js'):assert host.digest(BUILD.parent/'inputs'/relative)==value,relative
 for relative,origin in build['origins'].items():assert host.digest(origin)==build['inputs'][relative],origin
 for relative,value in build['artifacts'].items():assert host.digest(BUILD.parent/relative)==value,relative
 assert host.digest(BUILD.parent/'elm-host')==build['binarySHA256']
 manifest_path=ROOT/'component-manifest.json';assert host.digest(manifest_path)=='90b3838d01da30e9e99f76290eb7dd96bd49a84499b602e38e6339b4e97d68e3';manifest=json.loads(manifest_path.read_text());assert manifest['passed']
 for entry in manifest['files']:
  path=ROOT/entry['path'];assert not path.is_symlink() and path.stat().st_size==entry['size'] and host.digest(path)==entry['sha256'],path
 for item in manifest['guiAssets'].values():assert host.digest(item['path'])==item['sha256']
 closure=manifest['hostDependencyClosure'];assert host.digest(closure['buildReport'])==closure['buildReportSHA256'];host_build=json.loads(Path(closure['buildReport']).read_text())
 for section in ['dependencies','tools']:
  for path,value in host_build[section].items():assert host.digest(path)==value,path
 for path,value in closure['linkedLibraries'].items():assert host.digest(path)==value,path
 assert host.digest(closure['lddTool'])==closure['lddToolSHA256']
 core_manifest=REPO/'implementation/elm-window-geometry-default-limits-v40/component-manifest.json';assert host.digest(core_manifest)=='dd924d35c3568b4b0e0434bbc2eb841789e69c4451806a6a62659111180ca712';core_packet=json.loads(core_manifest.read_text())
 for entry in core_packet['files']:
  path=REPO/entry['path'];assert path.is_file() and not path.is_symlink() and path.stat().st_size==entry['size'] and host.digest(path)==entry['sha256'],path
 pair=host.pair_tuple();pointer=host.input_tuple()[1];descriptor=json.loads((FIXTURE/'client-build-report.json').read_text());assert descriptor['requiresXdgVersion']==6 and descriptor['suspendedStateObserved'] is True
 assert host.digest(descriptor['client'])==descriptor['clientSHA256'];assert host.digest(descriptor['buildReport'])==descriptor['buildReportSHA256']
 fixture_build=json.loads(Path(descriptor['buildReport']).read_text());assert fixture_build['passed']
 for section in ['inputs','dependencies','tools','linkedLibraries']:
  for path,value in fixture_build[section].items():assert host.digest(path)==value,path
 for relative,value in fixture_build['artifacts'].items():assert host.digest(Path(descriptor['buildReport']).parent/relative)==value,relative
 upstream=json.loads((SLICE/'upstream.json').read_text());assert host.digest(upstream['parentHost'])==upstream['parentHostSHA256']==host.digest(SLICE/'candidate_host.py');assert host.digest(upstream['clientHelperParent'])==upstream['clientHelperParentSHA256']
 return build,pair,pointer,descriptor

def run():
 global session,client,web,loaded,stopped,OUT,OUTPUT
 host.original.qa.require_qa_scope();OUT=SLICE/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-geometry-menu-'+str(time.time_ns()))
 try:
  build,pair,pointer,fixture=preflight();binary=BUILD.parent/'elm-host';backend_path=BUILD.parent/'inputs/adapter/daemon.py';plugin=pair['nativePair']['plugin']['path']
  paths=[Path(__file__),SLICE/'candidate_host.py',SLICE/'upstream.json',SLICE/'qa/client_evidence.py',KEYBOARD,Path(pointer),BUILD,FIXTURE/'client-build-report.json']
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
    wait(lambda:any(r['event']=='ready' for r in evidence.events()));native=wait(evidence.native_window);report['fixtureIdentity']={'pid':client.pid,'address':native['address'],'title':native['title']}
    selector=json.dumps('address:'+native['address'])
    for operation,fields in [('float','action="enable"'),('resize','x=320,y=180,relative=false'),('move','x=83,y=61,relative=false')]:
     expression='hl.dsp.window.'+operation+'({'+fields+',window='+selector+'})';check('ordinaryPlacement:'+operation,session.ctl('eval','local r=hl.dispatch('+expression+');if type(r)~="table" or r.ok~=true then error("placement refused") end').strip()=='ok')
    wait(lambda:evidence.settled(0) if evidence.native_window()['at']==[83,61] and evidence.native_window()['size']==[320,180] else None)
    env=dict(session.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')
    web=session.host.launch('elm-webview',[str(binary),'--assets',str(BUILD.parent/'inputs/assets'),'--backend',str(backend_path),'--authority-config',str(config_path),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=env)
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
    attach=next(r for r in reversed(incoming()) if r.get('kind')=='geometry-attached');hello=next(r for r in reversed(incoming()) if r.get('kind')=='attached')
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
     if not row(state):
      group=wait(lambda:next((g for g in coherent()['groups'] if g['key']=='application:elm-maximize-probe' and not g['disabled']),None) if coherent() else None,deadline=deadline);parent_pointer(group,272,deadline)
     target=wait(lambda:row(state),deadline=deadline);before=len(effects());parent_pointer(target,273,deadline);menu=wait(lambda:coherent()['menu'] if coherent() else None,deadline=deadline)
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
     check(label+':pendingPopupClosed',any(r['body']['menu'] is None and r['body']['outstanding']==1 for r in frames('surface-inspection: ')[start_inspection:]))
     if held:
      check('heldPendingClosesPopupAndNoOutcome',projection()['menu'] is None and projection()['outstanding']==1 and not any(r.get('kind')=='effect-outcome' and r.get('intent')==intent for r in incoming()))
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
    # External client changes produce real broker notifications and fresh observations.
    count=len(effects());previous=geometry();deadline=time.monotonic()+6;evidence.request('maximize',deadline)
    native,buffer=wait(lambda:evidence.settled(1),deadline=deadline);wait(lambda:geometry_row() if geometry_row() and geometry_row()['nativeMode']=='maximized' and int(geometry()['sequence'])>int(previous['sequence']) else None,deadline=deadline)
    menu=open_menu(deadline=deadline);check('externalMaxUpdatesMenuWithoutEffect',len(effects())==count and action(menu,'Maximize')['disabled'] and action(menu,'Restore')['disabled'],menu=menu,geometry=geometry());parent_pointer(menu['close'],272,deadline)
    wait(lambda:coherent() if coherent() and coherent()['menu'] is None else None,deadline=deadline);evidence.validate_pixels('external-max',native,buffer,deadline)
    deadline=time.monotonic()+6;evidence.request('unmaximize',deadline);wait(lambda:evidence.settled(0),deadline=deadline);wait(lambda:geometry_row() if geometry_row() and geometry_row()['nativeMode']=='ordinary' else None,deadline=deadline);menu=open_menu(deadline=deadline);check('externalOrdinaryRefreshNoReplay',len(effects())==count and not action(menu,'Maximize')['disabled'],menu=menu);parent_pointer(menu['close'],272,deadline);wait(lambda:coherent() if coherent() and coherent()['menu'] is None else None,deadline=deadline)
    report['scenarios'].append('GEOMETRY-MENU-07')
    # Reconnect occurs after a saved native MAX origin exists.
    settle_menu('Maximize','maximize',2,1);old_binding=geometry()['binding'];count=len(effects());deadline=time.monotonic()+6
    parent_pointer(wait(lambda:coherent()['reconnect'] if coherent() else None,deadline=deadline),272,deadline)
    new_attach=wait(lambda:next((r for r in reversed(incoming()) if r.get('kind')=='geometry-attached' and r['binding']!=old_binding),None),deadline=deadline)
    wait(lambda:coherent() and geometry_row() and geometry()['binding']==new_attach['binding'] and geometry_row()['ordinaryPlacementKnown'],deadline=deadline)
    menu=open_menu(deadline=deadline);check('reconnectRenegotiatesPreservingSavedOriginNoReplay',not action(menu,'Restore')['disabled'] and action(menu,'Maximize')['disabled'] and len(effects())==count and new_attach['binding']['lifetime']==old_binding['lifetime'],oldBinding=old_binding,newAttach=new_attach,geometry=geometry());parent_pointer(menu['close'],272,deadline);wait(lambda:coherent() if coherent() and coherent()['menu'] is None else None,deadline=deadline)
    report['scenarios'].append('GEOMETRY-MENU-08')
    settle_menu('Restore','restore-geometry',2,0,held=True)
    report['partialScenarios']={'GEOMETRY-MENU-09':{'heldPendingClosedAndSingleIntent':True,'notificationsDuringHeldReceiptQualified':False,'reason':'SIGSTOP prevents notification delivery too; separate controlled real receipt-hold fixture required'}}
    # Retire the exact open-menu target, then map a fresh same-title/application client.
    deadline=time.monotonic()+6;menu=open_menu(deadline=deadline);count=len(effects());retired_pid=client.pid;client.stdin.write(b'quit\n');client.stdin.flush();client.wait(timeout=max(.001,deadline-time.monotonic()));check('retiredClientNormalExit',client.returncode==0)
    wait(lambda:coherent() if coherent() and coherent()['menu'] is None and all(r['incarnation']!=identity for r in geometry()['facts']['windows']) else None,deadline=deadline)
    replacement_log=OUTPUT/'replacement-xdg.log';replacement_stream=os.fdopen(os.open(replacement_log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb');session.host.logs.append(replacement_stream)
    client=subprocess.Popen([fixture['client']],stdin=subprocess.PIPE,stdout=replacement_stream,stderr=subprocess.STDOUT,env=dict(session.env,WAYLAND_DEBUG='1'),cwd=session.host.runtime,start_new_session=True);replacement_identity=host.original.process(client.pid);replacement_identity.update(name='replacement-xdg-client',command=[fixture['client']],log=str(replacement_log));session.host.processes.append((client,replacement_identity))
    replacement=wait(lambda:next((w for w in session.data('clients') if w.get('pid')==client.pid and w.get('title')=='ELM-MAXIMIZE-PROBE'),None),deadline=deadline)
    replacement_fact=wait(lambda:next((r for r in geometry()['facts']['windows'] if r['incarnation']!=identity),None),deadline=deadline)
    check('retirementNeverTargetsSameTitleReplacement',client.pid!=retired_pid and replacement['address']!=report['fixtureIdentity']['address'] and replacement_fact['incarnation']!=identity and replacement['fullscreen']==replacement['fullscreenClient']==0 and not replacement_fact['minimized'] and len(effects())==count and coherent()['menu'] is None,replacement=replacement,geometry=replacement_fact)
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
    if loaded:assert session.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
    registered={r['pid'] for _,r in session.host.processes}
    for descendant in reversed([r for r in session.host.descendants() if r['pid'] not in registered]):session.host.stop(descendant)
 except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
 report['privateHost']=session.evidence if session else None;report['cleanupPassed']=bool(session and session.evidence.get('runtimeGone') and not session.evidence.get('cleanupErrors') and not session.evidence.get('remainingDescendants') and not session.evidence.get('unexpectedInnerDescendants'))
 report['passed']=report['passed'] and report['cleanupPassed']
 if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',symlinks=True)
 report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));return not report['passed']
if __name__=='__main__':raise SystemExit(run())
