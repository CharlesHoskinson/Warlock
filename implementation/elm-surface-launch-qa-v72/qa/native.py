"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,re,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-effect-invalidation-v43';GUI=REPO/'implementation/elm-surface-host-v70'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
FIXTURE=ROOT/'fixture.py'
report={'passed':False,'scope':'Dual-view Elm bar/controller and presentation-only popup native experiment','checks':[],'mainDesktopActions':False};apps=[];s=None;loaded=False
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
 build_path=sorted((GUI/'qa').glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
 for relative,digest in build['inputs'].items():assert host.digest(GUI/relative)==digest,relative
 assert host.digest(build_path.parent/'elm-host')==build['binarySHA256']
 manifest=json.loads((CORE/'qa/build-pair-manifest.json').read_text());assert manifest['passed']
 for relative,digest in manifest['files'].items():assert host.digest(CORE/relative)==digest,relative
 pair=manifest['nativePair'];plugin=pair['plugin']['path'];assert host.digest(plugin)==pair['plugin']['sha256'];assert host.digest(pair['core']['path'])==pair['core']['sha256']
 report.update(buildReport=str(build_path),buildReportSHA256=host.digest(build_path),pair=pair,inputs={str(p):host.digest(p) for p in (Path(__file__),POINTER,FIXTURE,ROOT/'launch_fixture.py',ROOT/'launch_supervisor.py',CORE/'candidate_host.py')})
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   data=OUTPUT/'catalog-data';applications=data/'applications';applications.mkdir(parents=True)
   receipt_path=OUTPUT/'launch-argv.json';quit_path=OUTPUT/'launch-quit'
   entry=applications/'owned-fixture.desktop'
   entry.write_text('[Desktop Entry]\nType=Application\nName=Owned Launch Fixture\nIcon=owned-fixture\nExec=/usr/bin/python3 -B '+str(ROOT/'launch_supervisor.py')+' '+str(ROOT/'launch_fixture.py')+' '+str(receipt_path)+' '+str(quit_path)+' "literal space" "$HOME" %% %c %k %i %F\n')
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps({**config,'catalogRoots':{'dataHome':str(data),'dataDirs':[],'cacheDir':str(OUTPUT/'catalog-cache')}}));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello()
   env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   control=OUTPUT/'fixture-control.json'
   fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=env);apps.append(fixture)
   wait(lambda:len(s.data('clients'))==2)
   web=s.host.launch('elm-webview',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--backend',str(GUI/'adapter/daemon.py'),'--authority-config',str(config_path),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=dict(env,WAYLAND_DEBUG='client'));apps.append(web)
   def log():return (OUTPUT/'elm-webview.log').read_text(errors='replace')
   def projection(origin):
    prefix='surface-report: origin='+origin+' '
    values=[json.loads(line[len(prefix):])['body'] for line in log().splitlines() if line.startswith(prefix)]
    return values[-1] if values else None
   def button(origin,label):
    p=projection(origin)
    return next((b for b in p['buttons'] if label in b['label'] and not b['disabled']),None) if p else None
   def click(x,y):
    result=subprocess.run([str(POINTER),'800','600'],input=f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedPointerNormalExit',result.returncode==0,point=[x,y],stderr=result.stderr)
   reserved=wait(lambda:s.data('monitors') if s.data('monitors')[0]['reserved'][1]==48 else None)
   check('actualNativeWorkareaReservesOnlyBar48',reserved[0]['reserved']==[0,48,0,0],monitors=reserved)
   wait(lambda:re.search(r'wl_surface[#@][0-9]+\.attach\(wl_buffer[#@]',log()))
   check('barBufferAttachedBeforeOpenerInput',bool(re.search(r'wl_surface[#@][0-9]+\.attach\(wl_buffer[#@]',log())))
   opener=wait(lambda:button('bar','Applications'))
   check('actualElmBarControlIn48PixelWorkarea',opener['height']>=36 and opener['y']>=0 and opener['y']+opener['height']<=48,button=opener)
   click(int(opener['x']+opener['width']/2),24)
   shown=wait(lambda:projection('popup') if projection('popup') and button('popup','Refresh') else None)
   wait(lambda:'surface-popup-open:' in log())
   check('actualPresentationOnlyElmPopup',bool(button('popup','Refresh')) and bool(button('popup','Windows')),projection=shown)
   protocol=log();popups=re.findall(r'zwlr_layer_surface_v1[#@]([0-9]+)\.get_popup\(xdg_popup[#@]([0-9]+)\)',protocol)
   check('actualLayerParentOwnsXDgPopupProtocolRole',bool(popups),roles=popups)
   popup_id=popups[-1][1]
   check('actualPopupHasWaylandSeatGrab',bool(re.search(r'xdg_popup[#@]'+popup_id+r'\.grab\(',protocol)))
   check('ordinaryBarRequestsNoKeyboardAndExclusive48','set_keyboard_interactivity(0)' in protocol and 'set_exclusive_zone(48)' in protocol)
   screenshot=OUTPUT/'elm-native-popover.png';subprocess.run(['grim',str(screenshot)],env=s.env,check=True,timeout=5);report['screenshotSHA256']=host.digest(screenshot)
   before=log().count('surface-popup-closed')
   click(600,550)
   wait(lambda:log().count('surface-popup-closed')>before)
   check('outsidePointerDismissesNativePopup',bool(re.search(r'xdg_popup[#@]'+popup_id+r'\.popup_done\(',log())))
   # After the popup grab is retired, an ordinary client receives pointer/key.
   click(600,550)
   peer=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER')
   check('dismissedPopupDoesNotOccupyApplicationHitRegion',s.data('activewindow')['address']==peer['address'])
   keyboard=Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');report['inputs'][str(keyboard)]=host.digest(keyboard);report['inputs'][str(keyboard.with_suffix('.c'))]=host.digest(keyboard.with_suffix('.c'))
   events=control.with_suffix('.events.jsonl');before_events=events.read_text().splitlines() if events.exists() else []
   process=subprocess.run([str(keyboard)],input='key 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
   check('ownedKeyboardNormalExit',process.returncode==0)
   delivered=[json.loads(line) for line in events.read_text().splitlines()[len(before_events):]]
   keys=[row for row in delivered if row['kind']=='key' and row['keyval']==97]
   check('applicationKeyboardRecipientAfterPopupDismissal',len(keys)==1 and keys[0]['window']=='ELM-ACTIVATION-PEER',events=delivered)
   opener=wait(lambda:button('bar','Applications'))
   click(int(opener['x']+opener['width']/2),24);wait(lambda:log().count('surface-popup-open')>=2)
   check('sameElmControllerReopensWithoutNativeBindingRestart',log().count('"kind":"attached"')==1)
   process=subprocess.run([str(keyboard)],input='key 1 1\nsleep 50\nkey 1 0\nsleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
   check('ownedEscapeNormalExit',process.returncode==0)
   wait(lambda:log().count('surface-popup-closed')>=2)
   check('actualElmEscapeDismissesPopup',log().count('surface-popup-closed')>=2)
   opener=wait(lambda:button('bar','Applications'))
   click(int(opener['x']+opener['width']/2),24)
   choice=wait(lambda:button('popup','Open Owned Launch Fixture'))
   check('actualOwnedCatalogInPresentationView',choice['y']>=0 and choice['y']+choice['height']<=420,button=choice)
   check('ownedLaunchInitiallyAbsent',not any(w['title']=='ELM-CATALOG-LAUNCHED' for w in s.data('clients')))
   click(int(50+choice['x']+choice['width']/2),int(48+choice['y']+choice['height']/2))
   window=wait(lambda:next((w for w in s.data('clients') if w['title']=='ELM-CATALOG-LAUNCHED'),None))
   check('actualOwnedGIOApplicationMapped',window['mapped'],window=window)
   record=wait(lambda:json.loads(receipt_path.read_text()) if receipt_path.exists() else None)
   expected=['literal space','$HOME','%','Owned Launch Fixture',str(entry),'--icon','owned-fixture']
   check('actualLaunchArgumentsAndOriginalFilename',record['argv']==expected and record['desktop']==str(entry),receipt=record)
   lines=log().splitlines()
   launches=[(i,json.loads(line.split('frontend-request: ',1)[1])) for i,line in enumerate(lines) if line.startswith('frontend-request: ') and json.loads(line.split('frontend-request: ',1)[1])['kind']=='application-launch']
   check('oneOpaqueDesktopIDLaunchOnly',len(launches)==1 and set(launches[0][1]['intent'])=={'request','lifetime','generation','entry'} and launches[0][1]['intent']['entry']=='owned-fixture',intents=launches)
   last_open=max(i for i,line in enumerate(lines) if line.startswith('surface-popup-open:'))
   close=next(i for i,line in enumerate(lines) if i>last_open and line.startswith('surface-popup-closed:'))
   check('actualNativeGrabRetiredBeforeLaunchForwarded',last_open<close<launches[0][0],openLine=last_open,closeLine=close,launchLine=launches[0][0])
   wait(lambda:projection('bar') if projection('bar') and 'Launch submitted.' in projection('bar')['text'] else None)
   check('singleControllerSettlesSubmittedAfterPopupClosed','Launch submitted.' in projection('bar')['text'])
   click(400,300)
   wait(lambda:s.data('activewindow')['title']=='ELM-CATALOG-LAUNCHED')
   check('launchedApplicationPointerAfterGrabRetirement',s.data('activewindow')['title']=='ELM-CATALOG-LAUNCHED')
   quit_path.touch();terminal=wait(lambda:json.loads(receipt_path.read_text()) if 'returnCode' in json.loads(receipt_path.read_text()) else None)
   check('actualLaunchedChildNormalExit',terminal['returnCode']==0,receipt=terminal)
   wait(lambda:not any(w['title']=='ELM-CATALOG-LAUNCHED' for w in s.data('clients')))
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('initialFixtureNormalExit',fixture.returncode==0)
   report['passed']=True
  finally:
   if 'quit_path' in locals():quit_path.touch()
   for process in reversed(apps):
    if process.poll() is None:
     owned=next(row for p,row in s.host.processes if p is process);s.host.stop(owned,process);process.wait(timeout=5)
    if process is not fixture:
     report['checks'].append({'name':'webviewAndBackendNormalExit','passed':process.returncode==0,'exitCode':process.returncode});report['passed']=report['passed'] and process.returncode==0
   registered={row['pid'] for _,row in s.host.processes}
   for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):s.host.stop(descendant)
   if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost']=s.evidence if s else None
report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed']=report['passed'] and report['cleanupPassed']
if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',ignore=shutil.ignore_patterns('*.sock'))
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
