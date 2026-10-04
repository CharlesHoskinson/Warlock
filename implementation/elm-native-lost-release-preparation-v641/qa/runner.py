"""Additive native campaign: lost real release, same-view explicit reconnect.
Root alone launches this through the serialized native build-loop wrapper.
"""
import importlib.util,json,os,secrets,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-grant-retirement-runtime-v595'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
PREFLIGHT=Path(os.environ['ELM_RELEASE_NATIVE_PREFLIGHT'])
preflight=json.loads(PREFLIGHT.read_text());assert preflight['passed']
for path,digest in preflight['inputs'].items():assert host.digest(path)==digest,path
GUI=Path(preflight['gui']);build_path=Path(preflight['buildReport']);build=json.loads(build_path.read_text());assert build['passed']
sys.path.insert(0,str(build_path.parent/'inputs/adapter'));from endpoint import start_time
from effect_endpoint import Endpoint
OUT=Path(preflight['outputDirectory']);OUT.mkdir(mode=0o700);OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-lost-release-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
report={'passed':False,'checks':[],'mainDesktopActions':False,'preflightSHA256':host.digest(PREFLIGHT),'scope':'Additive lost real release/same Elm view native path; original135 separate; no full GUI acceptance'};apps=[];s=None;loaded=False;fixture=None
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
def check(name,value,**evidence):report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
def wait(fn,seconds=6):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  s.guard();value=fn()
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Unchanged observation deadline')
try:
 manifest=json.loads((CORE/'qa/build-pair-manifest.json').read_text());pair=manifest['nativePair'];plugin=pair['plugin']['path'];report.update(pair=pair,buildReport=str(build_path))
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),1600,1000,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello();env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0')
   control=OUTPUT/'fixture-control.json';fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(ROOT/'fixture.py'),str(control)],env=env);apps.append(fixture)
   wait(lambda:len(s.data('clients'))==2)
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'retire-peer'}));temp.replace(control);wait(lambda:len(s.data('clients'))==1)
   fault_dir=OUTPUT/'release-fault';fault_dir.mkdir(mode=0o700)
   daemon_path=build_path.parent/'inputs/adapter/daemon.py'
   fault_config={'schema':1,'campaignId':secrets.token_hex(16),'daemonPath':str(daemon_path),'daemonSHA256':host.digest(daemon_path),'markerDirectory':str(fault_dir),'runtime':str(s.host.runtime),'instance':config['instance']}
   fault_path=fault_dir/'config.json';fault_path.write_text(json.dumps(fault_config));fault_path.chmod(0o600)
   wrapper=ROOT/'qa/fault_backend.py';web=s.host.launch('elm-webview',[str(build_path.parent/'elm-host'),'--assets',str(build_path.parent/'inputs/assets'),'--backend',str(wrapper),'--authority-config',str(config_path),'--surface-experiment','--qa-exit-after-render','--qa-stay-open'],env=dict(env,WAYLAND_DEBUG='client',ELM_QA_RELEASE_FAULT_CONFIG=str(fault_path)));apps.append(web)
   sys.path.insert(0,str(ROOT/'qa'));from inspection import Collector
   collector=Collector();log=OUTPUT/'elm-webview.log'
   def projection():return collector.read(log.read_text(errors='replace'))
   def frames(prefix):return [json.loads(line[len(prefix):]) for line in log.read_text(errors='replace').splitlines() if line.startswith(prefix)]
   def effects():return [f for f in frames('frontend-request: ') if f['kind']=='window-effect']
   def row():
    p=projection();return next((g for g in p['groups'] if not g['disabled']),None) if p and p['phase']=='Coherent' else None
   def click(item):
    assert item.get('visible',True),'Target outside host viewport'
    x,y=(round(v) for v in item['point']);assert 0<x<800 and 0<y<420
    result=subprocess.run([str(POINTER),'800','600'],input=f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedPointerNormalExit',result.returncode==0,point=[x,y],stderr=result.stderr)
   def backend():
    for p in s.host.descendants():
     try:args=Path(f"/proc/{p['pid']}/cmdline").read_bytes().split(b'\0')
     except FileNotFoundError:continue
     if args[:3]==[b'/usr/bin/python3',b'-B',str(wrapper).encode()]:return p
   initial=wait(row);check('singleRealElmTargetEnabled',initial['label'].startswith('Minimize '),projection=projection())
   owner=next(w for w in client.snapshot('201')['windows'] if w['label']=='ELM-AUTHORITY-FIXTURE')['incarnation']
   old=wait(backend);old_binding=[f['binding'] for f in frames('backend-frame: ') if f['kind']=='attached'][-1]
   s.guard();os.kill(old['pid'],signal.SIGSTOP);click(initial)
   pending=wait(lambda:projection() if projection() and projection()['transaction']=='Pending' else None)
   interrupted=effects();check('realPendingCreatesOneExplicitIntent',len(interrupted)==1 and interrupted[0]['intent']['incarnation']==owner and all(g['disabled'] for g in pending['groups']),request=interrupted[0])
   check('stoppedBrokerDidNotApplyEffect',not next(w for w in client.scene_facts('202')['facts']['windows'] if w['incarnation']==owner)['minimized'])
   s.guard();os.kill(old['pid'],signal.SIGKILL)
   lost=wait(lambda:projection() if projection() and projection()['phase']=='Detached' and projection()['transaction']=='Unknown' and projection()['reconnect'] else None)
   check('sameWebviewSurvivesInterruptedBroker',web.poll() is None and effects()==interrupted)
   click(lost['reconnect'])
   marker_path=fault_dir/'lost-release.json'
   def completed_marker():
    try:
     value=json.loads(marker_path.read_text())
     return value if value.get('kind')=='qa-release-output-lost' and value.get('certificate') and value.get('originalRelease') else None
    except (FileNotFoundError,ValueError):return None
   fault=wait(completed_marker)
   wait(lambda:'backend-exit: waited=1 normal=1 code=1' in log.read_text(errors='replace') and projection()['phase']=='Detached' and projection()['transaction']=='Unknown')
   after_lost=projection();first_binding=fault['certificate']['proof']['binding'];archive=fault['originalRelease']
   check('actualDurableCertificateLostBeforeWire',fault['record']['status']=='Unknown' and archive['phase']=='Released' and fault['certificate']['anchorId']==archive['id'] and not any(f['kind']=='host-reservation-released' for f in frames('backend-frame: ')),fault=fault)
   check('lostReleaseRetainsUIUnknownAndSameView',web.poll() is None and after_lost['transaction']=='Unknown' and all(g['disabled'] for g in after_lost['groups']) and effects()==interrupted,projection=after_lost)
   marker_bytes=marker_path.read_bytes();check('firstRecoveryUsesRealFreshBinding',first_binding!=old_binding,old=old_binding,current=first_binding)
   click(after_lost['reconnect']);recovered=wait(row)
   new_binding=[f['binding'] for f in frames('backend-frame: ') if f['kind']=='attached'][-1]
   released=next(f for f in reversed(frames('backend-frame: ')) if f['kind']=='host-reservation-released' and f['binding']==new_binding)
   check('secondExplicitReconnectSettlesOriginalRetainedReservation',new_binding!=first_binding and web.poll() is None and projection()['transaction']=='Unknown' and effects()==interrupted,projection=projection(),wire=released)
   namespace=s.host.runtime/'elm-window-recovery'/config['instance']/new_binding['lifetime']
   parent=json.loads((namespace/'ledger-v6.json').read_text());sidecar=json.loads((namespace/'release-deliveries-v1.json').read_text());cert=next(c for c in sidecar['certificates'] if c['record']==fault['record'])
   check('freshCertificateAnchorsUnchangedOriginalUnknown',next(r for r in parent['releases'] if r['id']==archive['id'])==archive and cert['anchorId']==archive['id'] and cert['proof']['binding']==new_binding and int(cert['proof']['sequence'])>int(fault['certificate']['proof']['sequence']) and released['release']=={k:cert[k] for k in ['id','proof','observation']},parent=parent,certificate=cert)
   check('oneShotMarkerAndEffectCountersUnchanged',marker_path.read_bytes()==marker_bytes and effects()==interrupted and parent['watermarks']==[{'binding':old_binding,'request':interrupted[0]['intent']['request'],'generation':interrupted[0]['intent']['generation']}])
   stale=dict(interrupted[0]);stale['binding']=old_binding
   try:client.request(stale)
   except Exception as error:check('oldNativeBindingCannotReplayEffect',str(error)=='binding-mismatch',reason=str(error))
   else:check('oldNativeBindingCannotReplayEffect',False)
   click(recovered);wait(lambda:row() and projection()['transaction']=='Committed')
   fresh=effects()[-1];check('onlyNewExplicitUserActionSubmitsNextEffect',len(effects())==2 and fresh['binding']==new_binding and int(fresh['intent']['request'])==int(interrupted[0]['intent']['request'])+1 and int(fresh['intent']['generation'])==int(interrupted[0]['intent']['generation'])+1 and next(w for w in client.scene_facts('203')['facts']['windows'] if w['incarnation']==owner)['minimized'],request=fresh)
   report.update(fault=fault,originalInterruptedIntent=interrupted[0],freshCertificate=cert,oldBinding=old_binding,firstRecoveryBinding=first_binding,finalBinding=new_binding)
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('fixtureNormalExit',fixture.returncode==0);report['passed']=True
  finally:
   for process in reversed(apps):
    if process.poll() is None:
     owned=next(row for p,row in s.host.processes if p is process);s.host.stop(owned,process);process.wait(timeout=5)
    if process is not fixture:check('webviewAndBackendNormalExit',process.returncode==0,exitCode=process.returncode)
   if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok';loaded=False
   registered={row['pid'] for _,row in s.host.processes}
   for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):s.host.stop(descendant)
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost']=s.evidence if s else None
report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed']=report['passed'] and report['cleanupPassed']
if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',symlinks=True)
report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
