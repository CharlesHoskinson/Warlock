"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-activation-protocol-v28'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(ROOT/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
FIXTURE=ROOT/'fixture.py'
report={'passed':False,'scope':'Private real pointer/Elm/effect/DOM path plus stopped broker pending interruption and explicit fresh-binding recovery; no renderer/compositor restart, full scene, GPU, AT, IME, UX or release acceptance','checks':[],'mainDesktopActions':False};apps=[];s=None;loaded=False
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
def check(name,value,**evidence):
 report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
def wait(fn,seconds=6):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  s.guard();value=fn()
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Unchanged observation deadline')
try:
 build_path=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
 for relative,digest in build['inputs'].items():assert host.digest(ROOT/relative)==digest,relative
 assert host.digest(build_path.parent/'elm-host')==build['binarySHA256']
 manifest=json.loads((CORE/'qa/build-pair-manifest.json').read_text());assert manifest['passed']
 for relative,digest in manifest['files'].items():assert host.digest(CORE/relative)==digest,relative
 pair=manifest['nativePair'];plugin=pair['plugin']['path'];assert host.digest(plugin)==pair['plugin']['sha256'];assert host.digest(pair['core']['path'])==pair['core']['sha256']
 report.update(buildReport=str(build_path),buildReportSHA256=host.digest(build_path),pair=pair,inputs={str(p):host.digest(p) for p in (Path(__file__),POINTER,FIXTURE,CORE/'candidate_host.py')})
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello()
   env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   control=OUTPUT/'fixture-control.json'
   fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=env);apps.append(fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
   web=s.host.launch('elm-webview',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--backend',str(ROOT/'adapter/daemon.py'),'--authority-config',str(config_path),'--layer','--qa-exit-after-render','--qa-stay-open'],env=env);apps.append(web)
   def projection():
    lines=(OUTPUT/'elm-webview.log').read_text(errors='replace').splitlines()
    values=[json.loads(line.split('projection-report: ',1)[1])['body'] for line in lines if line.startswith('projection-report: ')]
    return values[-1] if values else None
   def row(state):
    p=projection()
    return next((r for r in p['rows'] if r['label']=='ELM-AUTHORITY-FIXTURE' and r['state']==state and not r['disabled']),None) if p and p['phase']=='Coherent' else None
   def click(item):
    x,y=(round(v) for v in item['point']);assert 0<x<800 and 0<y<420
    result=subprocess.run([str(POINTER),'800','600'],input=f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedPointerNormalExit',result.returncode==0,point=[x,y],stderr=result.stderr)
   initial=wait(lambda:row('Open'));identity=initial['incarnation'];check('actualElmMinimizeControl',initial['action']=='Minimize',row=initial)
   keyboard=Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
   report['inputs'][str(keyboard)]=host.digest(keyboard);report['inputs'][str(keyboard.with_suffix('.c'))]=host.digest(keyboard.with_suffix('.c'))
   def key_recipient(label):
    events=control.with_suffix('.events.jsonl');before=events.read_text().splitlines() if events.exists() else []
    s.guard();process=subprocess.run([str(keyboard)],input='sleep 100\nkey 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
    assert process.returncode==0,process.stderr
    delivered=[json.loads(line) for line in events.read_text().splitlines()[len(before):]]
    report.setdefault('activationKeyboardReceipts',[]).append({'expected':label,'events':delivered,'exitCode':process.returncode})
    keys=[e for e in delivered if e['kind']=='key' and e['keyval']==97]
    return len(keys)==1 and keys[0]['window']==label
   initial_order=[r['incarnation'] for r in projection()['rows']]
   check('actualElmActivationControlEnabled',not initial['activation']['disabled'],row=initial)
   click(initial['activation'])
   wait(lambda:projection()['transaction']=='Committed' and projection()['phase']=='Coherent')
   check('pointerElmActivationNativeFocus',client.scene_facts('201')['facts']['focused']==identity and key_recipient('ELM-AUTHORITY-FIXTURE'))
   peer=wait(lambda:next((r for r in projection()['rows'] if r['label']=='ELM-ACTIVATION-PEER' and not r['activation']['disabled']),None))
   click(peer['activation']);wait(lambda:client.scene_facts('202')['facts']['focused']==peer['incarnation'] and projection()['transaction']=='Committed')
   check('pointerElmPeerActivationActualKeyboard',key_recipient('ELM-ACTIVATION-PEER'))
   wait(lambda:projection()['phase']=='Coherent')
   check('displayedWindowOrderStableAfterActivation',initial_order==[r['incarnation'] for r in projection()['rows']])
   initial=wait(lambda:row('Open'))

   click(initial)
   minimized=wait(lambda:row('Minimized'))
   facts=client.scene_facts('1');native_window=next(w for w in facts['facts']['windows'] if w['incarnation']==identity)
   check('pointerElmMinimizeNativeState',native_window['minimized'] and not native_window['acceptsInput'] and not native_window['shouldRenderAny'],window=native_window)
   check('minimizeReceiptThenAuthoritativeDOM',minimized['incarnation']==identity and minimized['action']=='Restore' and projection()['transaction']=='Committed',projection=projection())
   click(minimized)
   restored=wait(lambda:row('Open'));facts=client.scene_facts('2');native_window=next(w for w in facts['facts']['windows'] if w['incarnation']==identity)
   check('pointerElmRestoreNativeState',not native_window['minimized'] and native_window['acceptsInput'] and facts['facts']['focused']==identity,window=native_window)
   check('restoreReceiptThenAuthoritativeDOM',restored['incarnation']==identity and restored['action']=='Minimize' and projection()['transaction']=='Committed',projection=projection())
   def backend():
    def is_backend(p):
     try:args=Path(f"/proc/{p['pid']}/cmdline").read_bytes().split(b'\0')
     except FileNotFoundError:return False
     return args[:3]==[b'/usr/bin/python3',b'-B',str(ROOT/'adapter/daemon.py').encode()]
    return next((p for p in s.host.descendants() if is_backend(p)),None)
   def frames(prefix):
    return [json.loads(line.split(prefix,1)[1]) for line in (OUTPUT/'elm-webview.log').read_text().splitlines() if line.startswith(prefix)]
   old_backend=wait(backend)
   old_binding=[frame['binding'] for frame in frames('backend-frame: ') if frame['kind']=='attached'][-1]
   report['faultInjection']={'oldBackend':old_backend,'oldBinding':old_binding,'signal':'SIGSTOP then SIGKILL after actual Pending UI'}
   os.kill(old_backend['pid'],signal.SIGSTOP)
   click(restored)
   pending_projection=wait(lambda:projection() if projection() and projection()['transaction']=='Pending' else None)
   check('pendingRequestDisablesAllWindowActions',all(r['disabled'] for r in pending_projection['rows']),projection=pending_projection)
   check('pendingRequestHasNoOptimisticMinimize',not next(w for w in client.scene_facts('3')['facts']['windows'] if w['incarnation']==identity)['minimized'])
   os.kill(old_backend['pid'],signal.SIGKILL)
   lost=wait(lambda:projection() if projection() and projection()['phase']=='Detached' and projection()['transaction']=='Unknown' and projection()['reconnect'] else None)
   check('backendLossPreservesUnknownAndDisablesActions',all(r['disabled'] for r in lost['rows']) and all(r['state'].startswith('Last known: ') for r in lost['rows']),projection=lost)
   wait(lambda:'backend-exit: waited=1 normal=0 code=-1' in (OUTPUT/'elm-webview.log').read_text())
   click(lost['reconnect'])
   recovered=wait(lambda:row('Open'))
   fresh_binding=[frame['binding'] for frame in frames('backend-frame: ') if frame['kind']=='attached'][-1]
   check('explicitReconnectUsesFreshNativeBinding',fresh_binding!=old_binding,old=old_binding,new=fresh_binding)
   check('freshSnapshotPrecedesAdmissionWithoutReplay',projection()['transaction']=='Unknown' and len([f for f in frames('frontend-request: ') if f['kind']=='window-effect'])==3 and not next(w for w in client.scene_facts('4')['facts']['windows'] if w['incarnation']==identity)['minimized'],projection=projection())
   requests=[frame for frame in frames('frontend-request: ') if frame['kind']=='window-effect'];stale=dict(requests[-1]);stale['binding']=old_binding
   try:stale_result=client.request(stale)
   except Refused as refusal:stale_result={'kind':'authenticated-native-refusal','reason':str(refusal)}
   report['staleBindingOutcome']=stale_result
   check('retiredBackendBindingRefusedNatively',stale_result=={'kind':'authenticated-native-refusal','reason':'binding-mismatch'} and not next(w for w in client.scene_facts('5')['facts']['windows'] if w['incarnation']==identity)['minimized'])
   click(recovered);recovered_min=wait(lambda:row('Minimized'))
   request=[frame for frame in frames('frontend-request: ') if frame['kind']=='window-effect'][-1]
   check('freshExplicitIntentAfterReconnect',request['intent']['request']=='4' and request['binding']==fresh_binding and projection()['transaction']=='Committed',request=request)
   click(recovered_min);wait(lambda:row('Open'))
   check('freshRestoreAfterReconnect',client.scene_facts('6')['facts']['focused']==identity and projection()['transaction']=='Committed')
   screenshot=OUTPUT/'elm-effects-restored.png';subprocess.run(['grim',str(screenshot)],env=s.env,check=True,timeout=5);report['screenshotSHA256']=host.digest(screenshot)
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('fixtureNormalExit',fixture.returncode==0)
   report['passed']=True
  finally:
   for process in reversed(apps):
    if process.poll() is None:
     owned=next(row for p,row in s.host.processes if p is process);s.host.stop(owned,process);process.wait(timeout=5)
    if process is not fixture:
     report['checks'].append({'name':'webviewAndBackendNormalExit','passed':process.returncode==0,'exitCode':process.returncode});report['passed']=report['passed'] and process.returncode==0
   if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
   registered={row['pid'] for _,row in s.host.processes}
   for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):s.host.stop(descendant)
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost']=s.evidence if s else None
report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed']=report['passed'] and report['cleanupPassed']
if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',symlinks=True)
report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
