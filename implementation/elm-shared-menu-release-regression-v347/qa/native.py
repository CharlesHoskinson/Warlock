"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,shutil,signal,struct,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-shared-terminal-runtime-v336';GUI=REPO/'implementation/elm-shared-terminal-early-release-v344'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
FIXTURE=ROOT/'fixture.py'
report={'passed':False,'scope':'Actual shared host native pointer context/keyboard navigation and staged native minimize/restore; private owning tuple only, no original137/full recovery/AT/IME/hardware/release acceptance','checks':[],'mainDesktopActions':False};apps=[];s=None;loaded=False
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
 preflight=json.loads((ROOT/'qa/preflight.json').read_text());assert preflight['passed']
 for path,digest in preflight['inputs'].items():assert host.digest(path)==digest,path
 report['preflightSHA256']=host.digest(ROOT/'qa/preflight.json')
 build_path=GUI/'qa/build-1791117293165760899/report.json';build=json.loads(build_path.read_text());assert build['passed']
 for relative,digest in build['inputs'].items():assert host.digest(GUI/relative)==digest,relative
 assert host.digest(build_path.parent/'elm-host')==build['binarySHA256']
 manifest=json.loads((CORE/'qa/build-pair-manifest.json').read_text());assert manifest['passed']
 for relative,digest in manifest['files'].items():assert host.digest(CORE/relative)==digest,relative
 pair=manifest['nativePair'];plugin=pair['plugin']['path'];assert host.digest(plugin)==pair['plugin']['sha256'];assert host.digest(pair['core']['path'])==pair['core']['sha256']
 assert host.digest(manifest['owningAcceptance'])==manifest['owningAcceptanceSHA256']
 report.update(buildReport=str(build_path),buildReportSHA256=host.digest(build_path),pair=pair,inputs={str(p):host.digest(p) for p in (Path(__file__),ROOT/'qa/inspection.py',ROOT/'qa/grab_guard.py',ROOT/'qa/sampling.py',POINTER,FIXTURE,CORE/'candidate_host.py')})
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),1600,1000,LUA,mesa_vendor=True) as s:
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
   web=s.host.launch('elm-webview',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--backend',str(build_path.parent/'inputs/adapter/daemon.py'),'--authority-config',str(config_path),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=dict(env,WAYLAND_DEBUG='client'));apps.append(web)
   sys.path.insert(0,str(ROOT/'qa'))
   from inspection import Collector
   collector=Collector()
   def projection():return collector.read((OUTPUT/'elm-webview.log').read_text(errors='replace'))
   def row(state):
    p=projection()
    action='Restore ' if state=='Minimized' else 'Minimize '
    return next((g for g in p['groups'] if g['label'].startswith(action) and not g['disabled']),None) if p and p['phase']=='Coherent' else None
   def journal():
    return [json.loads(line.split('frontend-request: ',1)[1]) for line in (OUTPUT/'elm-webview.log').read_text().splitlines() if line.startswith('frontend-request: ') and json.loads(line.split('frontend-request: ',1)[1])['kind']=='window-effect']
   def group():
    p=projection()
    return p['groups'][0] if p and p['phase']=='Coherent' and len(p['groups'])==1 and not p['groups'][0]['disabled'] else None
   def selection(label):
    p=projection()
    return next((r for r in p['picker']['selections'] if r['title']==label and not r['disabled']),None) if p and p['phase']=='Coherent' and p['picker'] else None
   def click(item):
    assert item.get('visible',True),'Target outside host viewport'
    x,y=(round(v) for v in item['point']);assert 0<x<800 and 0<y<420
    result=subprocess.run([str(POINTER),'800','600'],input=f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedPointerNormalExit',result.returncode==0,point=[x,y],stderr=result.stderr)
   initial=wait(group);check('sharedNativeTaskbarReady',initial['label'].startswith('Choose a window from '),group=initial)
   KEYBOARD=Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
   report['inputs'][str(KEYBOARD)]=host.digest(KEYBOARD)
   def log():return (OUTPUT/'elm-webview.log').read_text(errors='replace')
   def inspections():
    return [json.loads(line.split(': ',1)[1]) for line in log().splitlines() if line.startswith('surface-inspection: ')]
   def native_menu():
    values=inspections()
    if not values:return None
    model=values[-1]
    return model if model['body']['mode']=='menu' and model['body']['phase']=='Coherent' and model['body']['menu'] else None
   def keys(commands):
    result=subprocess.run([str(KEYBOARD)],input=commands+'sleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedNativeKeyboardNormalExit',result.returncode==0,stderr=result.stderr,commands=commands)
   def right(item):
    assert item.get('visible',True),'Target outside fixed viewport'
    x,y=(round(v) for v in item['point']);assert 0<x<800 and 0<y<600
    result=subprocess.run([str(POINTER),'800','600'],input=f'move {x} {y}\nsleep 100\nbutton 273 1\nsleep 50\nbutton 273 0\nsleep 100\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedNativeContextPointerNormalExit',result.returncode==0,point=[x,y],stderr=result.stderr)
   before_journal=journal();right(initial)
   item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'))
   check('multifamilyContextOpensNativePickerWithoutEffect',journal()==before_journal,selection=item)
   right(item);opened=wait(native_menu)
   check('realPopupPointerContextOpensElmWindowMenu',opened['body']['menu']['incarnation']==item['incarnation'],inspection=opened)
   check('nativeContextProofIdentifiesActualOutput','surface-context-admitted: view=1 generation=1 origin=popup trigger=pointer' in log())
   check('menuOpenDoesNotMutateNativeWindows',journal()==before_journal)
   keys('key 1 1\nsleep 50\nkey 1 0\n');wait(lambda:inspections()[-1]['body']['mode']=='closed')
   check('realEscapeClosesMenuWithoutNativeEffect',journal()==before_journal)
   # Open the ordinary picker again, retaining its native focused selection.
   click(wait(group));wait(lambda:selection('ELM-AUTHORITY-FIXTURE'))
   keys('key 127 1\nsleep 50\nkey 127 0\n');opened=wait(native_menu)
   check('realMenuKeyOpensWindowMenu','surface-context-admitted: view=1 generation=1 origin=popup trigger=keyboard' in log(),inspection=opened)
   selected=opened['body']['menu']['selected'];enabled=[i for i,a in enumerate(opened['body']['menu']['actions']) if a['enabled']]
   assert enabled==[selected], 'This tiled fixture has exactly one enabled action; multi-action navigation needs a separate floating fixture'
   count=len(inspections());keys('key 108 1\nsleep 50\nkey 108 0\n')
   navigated=wait(lambda:native_menu() if len(inspections())>count and native_menu() and native_menu()['body']['menu']['id']==opened['body']['menu']['id'] else None)
   check('realArrowDownSkipsDisabledRowsAndRetainsSoleEnabledAction',navigated['body']['menu']['selected']==selected and journal()==before_journal,inspection=navigated)
   keys('key 1 1\nsleep 50\nkey 1 0\n');wait(lambda:inspections()[-1]['body']['mode']=='closed')
   click(wait(group));wait(lambda:selection('ELM-AUTHORITY-FIXTURE'))
   keys('key 42 1\nkey 68 1\nsleep 50\nkey 68 0\nkey 42 0\n');shift=wait(native_menu)
   check('realShiftF10OpensElmMenu',shift['body']['menu'] is not None,inspection=shift)
   keys('key 1 1\nsleep 50\nkey 1 0\n');wait(lambda:inspections()[-1]['body']['mode']=='closed')
   check('allNativeOpenNavigateCancelRoutesKeepEffectsInert',journal()==before_journal)
   observation=1
   def facts():
    global observation
    observation+=1
    return client.scene_facts(str(observation))
   identities=client.snapshot('1');inc=next(w['incarnation'] for w in identities['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE')
   baseline=facts();target=next(w for w in baseline['facts']['windows'] if w['incarnation']==inc)
   def pixels(name,expected_red,expected):
    geometry=expected['geometry'];x,y,w,h=geometry
    points=[(round(x+w*f),round(y+h*f)) for f in [.5,.7,.3]];attempts=[];deadline=time.monotonic()+6
    def capture():
     s.guard();remaining=deadline-time.monotonic()
     if remaining<=0:raise RuntimeError('Unchanged observation deadline')
     picture=OUTPUT/(name+'-'+str(len(attempts))+'.png')
     process=subprocess.run(['/usr/bin/grim',str(picture)],env=s.env,capture_output=True,timeout=min(5,remaining));assert process.returncode==0,process.stderr
     raw=picture.read_bytes();assert raw[:8]==bytes.fromhex('89504e470d0a1a0a') and raw[12:16]==b'IHDR' and struct.unpack('>II',raw[16:24])==(800,600)
     remaining=deadline-time.monotonic()
     if remaining<=0:raise RuntimeError('Unchanged observation deadline')
     converted=subprocess.run(['/usr/bin/magick',str(picture),'-depth','8','rgb:-'],capture_output=True,timeout=min(5,remaining));assert converted.returncode==0 and len(converted.stdout)==800*600*3
     samples=[]
     for px,py in points:
      assert 0<px<800 and 48<py<600
      offset=(py*800+px)*3;samples.append(list(converted.stdout[offset:offset+3]))
     current=next(v for v in facts()['facts']['windows'] if v['incarnation']==inc)
     assert all(current[k]==expected[k] for k in ['incarnation','geometry','workspace','monitor','minimized','shouldRenderAny','shouldRenderOwnMonitor','acceptsInput']), 'Native state changed during pixel observation'
     row={'path':str(picture),'sha256':host.digest(picture),'points':points,'samples':samples};attempts.append(row);report.setdefault('pixelAttempts',[]).append(row)
     matched=all(v==[255,0,0] for v in samples) if expected_red else all(v!=[255,0,0] for v in samples)
     return row if matched else None
    observed=wait(capture);check(name,True,capture=observed,expectedRed=expected_red)
   pixels('initialNativeFixturePixelsAreRed',True,target)
   def state(minimized):
    current=facts();window=next((w for w in current['facts']['windows'] if w['incarnation']==inc),None)
    return {'facts':current,'window':window} if window and window['minimized']==minimized else None
   def outcomes():
    return [json.loads(line.split('backend-frame: ',1)[1]) for line in log().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split('backend-frame: ',1)[1]).get('kind')=='effect-outcome']
   click(wait(group));target_item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'));right(target_item);chosen=wait(native_menu)
   check('nativeTiledMenuSelectsMinimize',chosen['body']['menu']['incarnation']==inc and chosen['body']['menu']['selected']==1 and chosen['body']['menu']['actions'][1]['enabled'])
   keys('key 28 1\nsleep 50\nkey 28 0\n');hidden=wait(lambda:state(True));wait(lambda:len(outcomes())==1)
   minimized_request=journal()
   check('realElmMenuMinimizeSubmitsExactlyOnce',len(minimized_request)==1 and minimized_request[0]['intent']['incarnation']==inc and minimized_request[0]['intent']['operation']=='minimize',requests=minimized_request)
   check('minimizeNativeReceiptIsCorrelatedCommitted',outcomes()[0]['status']=='Committed' and outcomes()[0]['intent']==minimized_request[0]['intent'],outcome=outcomes()[0])
   check('minimizeNativeRenderAndInputSuppressionKeepsOriginalWorkspace',not hidden['window']['shouldRenderAny'] and not hidden['window']['shouldRenderOwnMonitor'] and not hidden['window']['acceptsInput'] and hidden['window']['workspace']==target['workspace'] and hidden['window']['monitor']==target['monitor'],before=target,after=hidden['window'])
   pixels('minimizedNativeFixturePixelsDisappear',False,hidden['window'])
   click(wait(group));target_item=wait(lambda:selection('ELM-AUTHORITY-FIXTURE'));right(target_item);restoring=wait(native_menu)
   check('nativeMinimizedMenuSelectsRestore',restoring['body']['menu']['incarnation']==inc and restoring['body']['menu']['selected']==0 and restoring['body']['menu']['actions'][0]['enabled'])
   keys('key 28 1\nsleep 50\nkey 28 0\n');shown=wait(lambda:state(False));wait(lambda:len(outcomes())==2)
   restored_requests=journal()
   check('realElmMenuRestoreSubmitsExactlyOnce',len(restored_requests)==2 and restored_requests[1]['intent']['incarnation']==inc and restored_requests[1]['intent']['operation']=='restore',requests=restored_requests)
   check('restoreNativeReceiptIsCorrelatedCommitted',outcomes()[1]['status']=='Committed' and outcomes()[1]['intent']==restored_requests[1]['intent'],outcome=outcomes()[1])
   check('restoreNativeRenderAndInputEligibilityKeepsOriginalWorkspace',shown['window']['shouldRenderAny'] and shown['window']['shouldRenderOwnMonitor'] and shown['window']['acceptsInput'] and shown['window']['workspace']==target['workspace'] and shown['window']['monitor']==target['monitor'],before=target,after=shown['window'])
   pixels('restoredNativeFixturePixelsReturn',True,shown['window'])
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
