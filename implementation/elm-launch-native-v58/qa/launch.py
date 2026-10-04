"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-effect-invalidation-v43';GUI=REPO/'implementation/elm-launch-host-v57'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
FIXTURE=ROOT/'fixture.py'
report={'passed':False,'scope':'Actual pointer/Elm/authenticated host/catalog/GIO/owned GTK launch and argv/normal child exit; not production launcher/readiness acceptance','checks':[],'mainDesktopActions':False};apps=[];s=None;loaded=False
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
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
   web=s.host.launch('elm-webview',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--backend',str(GUI/'adapter/daemon.py'),'--authority-config',str(config_path),'--layer','--qa-exit-after-render','--qa-stay-open'],env=env);apps.append(web)
   def projection():
    lines=(OUTPUT/'elm-webview.log').read_text(errors='replace').splitlines()
    values=[json.loads(line.split('projection-report: ',1)[1])['body'] for line in lines if line.startswith('projection-report: ')]
    return values[-1] if values else None
   def click(item):
    assert item['visible'] and not item['disabled'],'Target unavailable/outside viewport'
    x,y=(round(v) for v in item['point']);assert 0<x<800 and 0<y<420
    result=subprocess.run([str(POINTER),'800','600'],input=f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedPointerNormalExit',result.returncode==0,point=[x,y],stderr=result.stderr)
   initial=wait(lambda:projection() if projection() and projection()['phase']=='Coherent' else None)
   check('originalWindowProjectionAvailable',len(initial['groups'])==1)
   click(initial['openApplications'])
   catalog=wait(lambda:projection() if projection() and projection()['phase']=='Applications' and len(projection()['entries'])==1 else None)
   check('realCatalogAppearsThroughAuthenticatedHost',catalog['entries'][0]['id']=='owned-fixture' and catalog['entries'][0]['label']=='Open Owned Launch Fixture' and not catalog['entries'][0]['disabled'],projection=catalog)
   before=len([w for w in s.data('clients') if w['title']=='ELM-CATALOG-LAUNCHED'])
   check('ownedLaunchWindowInitiallyAbsent',before==0)
   click(catalog['entries'][0])
   settled=wait(lambda:projection() if projection() and projection()['phase']=='Applications' and projection()['launchStatus']=='Submitted' else None)
   check('realNativeReceiptSettlesElmSubmitted',settled['status']=='Launch submitted.',projection=settled)
   window=wait(lambda:next((w for w in s.data('clients') if w['title']=='ELM-CATALOG-LAUNCHED'),None))
   check('actualOwnedApplicationWindowMapped',window['mapped'],client=window)
   record=wait(lambda:json.loads(receipt_path.read_text()) if receipt_path.exists() else None)
   expected=['literal space','$HOME','%','Owned Launch Fixture',str(entry),'--icon','owned-fixture']
   check('actualGUIRoutePreservesNativeGIOArguments',record['argv']==expected,actual=record['argv'],expected=expected)
   check('actualGUIRouteKeepsOriginalDesktopFilename',record['desktop']==str(entry))
   launches=[json.loads(line.split('frontend-request: ',1)[1]) for line in (OUTPUT/'elm-webview.log').read_text().splitlines() if line.startswith('frontend-request: ') and json.loads(line.split('frontend-request: ',1)[1])['kind']=='application-launch']
   check('oneBoundDesktopIdentityIntentWithoutCommands',len(launches)==1 and set(launches[0]['intent'])=={'request','lifetime','generation','entry'} and launches[0]['intent']['entry']=='owned-fixture',intents=launches)
   # Refresh after a native-only Exec byte change revalidates catalog generation.
   entry.write_text(entry.read_text()+'# native source revision\n')
   click(next(c for c in settled['controls'] if c['text']=='Refresh'))
   refreshed=wait(lambda:projection() if projection()['phase']=='Applications' and len(projection()['entries'])==1 else None)
   check('refreshRetainsAdmittedApplicationWithoutResubmission',len([w for w in s.data('clients') if w['title']=='ELM-CATALOG-LAUNCHED'])==1 and refreshed['launchStatus']=='Submitted')
   screenshot=OUTPUT/'elm-applications.png';subprocess.run(['grim',str(screenshot)],env=s.env,check=True,timeout=5);report['screenshotSHA256']=host.digest(screenshot)
   quit_path.touch();terminal=wait(lambda:json.loads(receipt_path.read_text()) if 'returnCode' in json.loads(receipt_path.read_text()) else None)
   check('actualLaunchedFixtureNormalExit',terminal['returnCode']==0,receipt=terminal)
   wait(lambda:not any(w['title']=='ELM-CATALOG-LAUNCHED' for w in s.data('clients')))
   click(next(c for c in refreshed['controls'] if c['text']=='Windows'))
   returned=wait(lambda:projection() if projection()['phase']=='Coherent' else None)
   check('returnToNativeWindowControls',len(returned['groups'])==1 and not returned['groups'][0]['disabled'])
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
