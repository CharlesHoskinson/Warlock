"""Actual controlled host admission/policy/pure renderer in reviewed private GUI."""
import hashlib,importlib.util,json,os,pathlib,resource,re,shutil,socket,struct,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pre=json.loads((ROOT/'qa/preflight.json').read_text());assert pre['passed'] and not pre['nativeLaunched']
for p,h in pre['inputs'].items():assert sha(p)==h,p
spec=importlib.util.spec_from_file_location('controlled_exact_private_host',ROOT/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
sys.path.insert(0,str(ROOT/'qa'));from session_bus import isolate_session_host
from system_isolation import supply,validate
isolate_session_host(host)
OUT=ROOT/'qa'/('native-controlled-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
private=pathlib.Path('/home/hoskinson/window-integration-qa')/('warlock-controlled-host-'+str(time.time_ns()))
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':pre['scope'],'pair':pre['pair'],'inputs':pre['inputs'],'checks':[]};s=None;web=None;loaded=False;fixtures=[];request_id=1
def check(name,ok,**values):r['checks'].append({'name':name,'passed':bool(ok),**values});assert ok,name
def wait(fn,seconds=6):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  s.guard();value=fn()
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Original six-second fixture observation deadline')
def full_log():
 p=private/'controlled-host.log';text=p.read_text() if p.exists() else ''
 return text if text.endswith('\n') else text[:text.rfind('\n')+1]
def private_states():return [json.loads(line.split(': ',1)[1]) for line in full_log().splitlines() if line.startswith('controlled-native-private-status: ')]
def pointer(name,script):
 path=private/(name+'-input.log')
 with path.open('xb') as output:
  p=subprocess.Popen([pre['pointer'],'800','600'],stdin=subprocess.PIPE,stdout=output,stderr=subprocess.STDOUT,env=env,cwd=s.host.runtime,start_new_session=True)
 record=host.original.process(p.pid);record.update(name=name+'-input',command=[pre['pointer'],'800','600'],log=str(path));s.host.processes.append((p,record))
 p.communicate(script.encode(),timeout=5);check(name+'ActualPointerNormalExit',p.returncode==0)
try:
 lua=b'hl.config({xwayland={enabled=false},animations={enabled=false},misc={disable_hyprland_logo=true,disable_splash_rendering=true}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
 s=host.PrivateHyprSession(private,dict(os.environ),1600,1000,lua,mesa_vendor=True)
 with s:
  try:
   check('controlledExactOwningPluginLoads',s.ctl('plugin','load',pre['pair']['plugin']['path']).strip()=='ok');loaded=True
   env=supply(s.env,s.host.runtime);validate(env,s.host.runtime);env.update(GTK_A11Y='none',NO_AT_BRIDGE='1',GTK_USE_PORTAL='0',GSETTINGS_BACKEND='memory')
   for name in ['source','companion']:
    p=s.host.launch(name,[pre['fixtureClient']],env=dict(env,WARLOCK_CHILD_CONTROL_PATH=str(private/(name+'-control'))));fixtures.append((name,p));wait(lambda:len(s.data('clients'))==len(fixtures))
   child=next(row for _,row in s.host.processes if row['name']=='hyprland');path=s.host.runtime/'hypr'/s.env['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock'
   def observe(body):
    before=host.original.socket_identity(path,s.host.runtime);assert host.original.same_process(child)
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
     c.settimeout(3);c.connect(str(path));pid,uid,gid=struct.unpack('3i',c.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));assert pid==child['pid'] and uid==os.getuid() and host.original.same_process(child) and host.original.socket_identity(path,s.host.runtime)==before
     c.sendall(('elm_observe '+json.dumps(body)).encode());reply=bytearray()
     while True:
      part=c.recv(4096)
      if not part:break
      reply.extend(part);assert len(reply)<=65536
    assert host.original.same_process(child) and host.original.socket_identity(path,s.host.runtime)==before;return json.loads(reply)
   attached=observe({'protocolVersion':3,'kind':'hello'})
   facts=observe({'protocolVersion':3,'kind':'scene-facts-request','binding':attached['binding'],'requestId':'1','minimumWatermark':'0'})
   subjects=[w['incarnation'] for w in facts['facts']['windows'] if w['application']=='warlock-child-probe'];check('controlledTwoActualApplicationFamilies',len(subjects)==2);subject=subjects[0]
   config=private/'provider-authority.json';config.write_text(json.dumps({'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':child['pid'],'expected_start':int(child['start']),'binary_sha256':pre['pair']['core']['sha256']}));config.chmod(0o600)
   web=s.host.launch('controlled-host',[pre['controlledHostBinary'],'--assets',pre['controlledHostAssets'],'--backend',pre['controlledHostBackend'],'--authority-config',str(config),'--surface-experiment','--qa-exit-after-render','--qa-stay-open','--qa-preview-controlled',subject,'--qa-preview-snapshot',str(private/'delayed-webkit.png'),'--qa-preview-reopened-snapshot'],env=env)
   def source_button():
    inspections=[json.loads(line.split(': ',1)[1]) for line in full_log().splitlines() if line.startswith('surface-inspection: ')]
    bars=[json.loads(line[len('surface-report: origin=bar '):]) for line in full_log().splitlines() if line.startswith('surface-report: origin=bar ')]
    if not inspections or not bars:return None
    inspection=inspections[-1];bar=bars[-1]['body']
    if inspection['body']['phase']!='Coherent' or inspection['publication']!=bar['publication'] or inspection['lease']!=bar['lease']:return None
    groups=[g for g in inspection['body']['groups'] if g['title']=='WARLOCK-CHILD-PROBE']
    if len(groups)!=1:return None
    buttons=[b for b in bar['buttons'] if b['id']==groups[0]['domId'] and not b['disabled']]
    return buttons[0] if len(buttons)==1 else None
   button=wait(source_button);x=round(button['x']+button['width']/2);y=round(button['y']+button['height']/2);check('controlledActualGroupPointerInOutput',0<x<800 and 0<y<48,button=button)
   check('controlledFactoryAbsentBeforeActualGTKAdmission','controlled-native-start:' not in full_log())
   pointer('controlled-open','move 400 500\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
   wait(lambda:'controlled-native-start:' in full_log());check('controlledFactoryAfterOriginalGTKAdmission',full_log().index('surface-presentation-applied:')<full_log().index('controlled-native-start:') and 'surface-configured:' in full_log())
   wait(lambda:'controlled-renderer-initialized:' in full_log());check('controlledActualPureWebKitRendererInitializedOnce',full_log().count('controlled-renderer-initialized:')==1 and 'windowPolicies=0 physicalReveal=0' in full_log())
   wait(lambda:'controlled-renderer-applied:' in full_log());check('controlledActualDOMAndNativeCurrentProjectionReceipt','originalContext=1 currentProjection=1 physicalReveal=0' in full_log())
   issued=wait(lambda:next((state for state in private_states() if int(state['transport']['nativeIssuedThrough'])>0 and int(state['transport']['deliveredThrough'])>0),None))
   check('controlledOriginalNativeTicketsActuallyIssuedAndDelivered',issued['nativeEffectError']=='' and issued['privatePolicy']['realm']['controlled'],state=issued)
   check('controlledNoLegacyBrowserCommandRoute','native-imported-command:' not in full_log() and 'native-client-command:' not in full_log())
   wait(lambda:'controlled-native-snapshot-held: actualResult=1 retainedResults=1 finishCalls=0' in full_log())
   check('controlledActualSnapshotResultRetainedBeforeClosure',not (private/'delayed-webkit.png').exists() and 'native-client-webkit-snapshot: saved=1' not in full_log())
   pointer('controlled-close','move 400 500\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
   def drained():
    states=private_states()
    if not states:return None
    state=states[-1];policy=state['privatePolicy'];transport=state['transport']
    return state if not policy['models'] and not policy['realm']['ingress']['pending'] and not policy['realm']['deferred'] and not state['retainedInputs'] and not state['postedTickets'] and not state['confirmations'] and not state['returnedEventBatches'] and transport['pending']==0 else None
   final=wait(drained);check('controlledOriginalPolicyInputTicketConfirmationCustodyDrained',final['nativeEffectError']=='',state=final)
   first_epoch=int(final['privatePolicy']['realm']['epoch']);first_binding=issued['privatePolicy']['commands']['binding']
   final=wait(lambda:next((state for state in reversed(private_states()) if int(state['privatePolicy']['realm']['epoch'])==first_epoch and state['privatePolicy']['realm']['closed']),None))
   wait(lambda:'controlled-renderer-context-replaced: retiredEpoch='+str(first_epoch)+' ' in full_log())
   check('controlledRealOldResultSurvivesStrictRealmCloseAndViewReplacement',not list(private.glob('delayed-webkit.png*')) and 'controlled-native-snapshot-released:' not in full_log(),state=final)
   button=wait(source_button);x=round(button['x']+button['width']/2);y=round(button['y']+button['height']/2);check('controlledReopenActualGroupPointerInOutput',0<x<800 and 0<y<48,button=button)
   pointer('controlled-reopen','move 400 500\nsleep 100\nmove '+str(x)+' '+str(y)+'\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
   reopened=wait(lambda:next((state for state in reversed(private_states()) if int(state['privatePolicy']['realm']['epoch'])>first_epoch and state['privatePolicy']['models'] and int(state['transport']['nativeIssuedThrough'])>0 and int(state['transport']['deliveredThrough'])>0),None))
   second_epoch=int(reopened['privatePolicy']['realm']['epoch'])
   check('controlledReopenedOriginalPolicyAndNativeBinding',reopened['privatePolicy']['commands']['binding']==first_binding and 'controlled-native-reopened: previousEpoch='+str(first_epoch)+' nativeEpoch='+str(second_epoch)+' samePolicy=1 sameBinding=1 originalNative=1 grantResets=0 rendererPolicies=0' in full_log(),state=reopened)
   wait(lambda:'controlled-renderer-initialized: nativeEpoch='+str(second_epoch)+' ' in full_log())
   check('controlledFreshRendererInitializedOnceEachEpoch',full_log().count('controlled-renderer-initialized:')==2)
   wait(lambda:'controlled-native-snapshot-released: retainedResults=0 originalFinishCalls=1' in full_log())
   check('controlledActualStaleSnapshotCompletionRejected',full_log().count('controlled-native-snapshot-held:')==1 and full_log().count('controlled-native-snapshot-released:')==1 and 'controlled-native-snapshot-refused: currentProjection=0 hardwarePresentation=0' in full_log() and not (private/'delayed-webkit.png').exists())
   r.update(actualDelayedWebKitResultRetained=True,actualStaleSnapshotCallbackQualified=True,actualStaleSnapshotArtifactRejected=True,actualRetainedResultConsumedOnce=True)
   crossed=re.search(r'controlled-native-snapshot-crossed-realm: retainedEpoch=(\d+) currentEpoch=(\d+) retainedNavigation=(\d+) currentNavigation=(\d+) replacedView=(\d+) originalResult=1 originalFinishCalls=0 nativeSettlement=0',full_log())
   check('controlledOriginalRealResultFinishedAcrossLaterEpochAndNavigation',crossed is not None and int(crossed.group(1))==first_epoch and int(crossed.group(2))==second_epoch and int(crossed.group(4))>int(crossed.group(3)) and crossed.group(5)=='1',observation=crossed.group(0) if crossed else '')
   def current_image():
    states=private_states()
    if not states or int(states[-1]['privatePolicy']['realm']['epoch'])!=second_epoch:return None
    models=states[-1]['privatePolicy']['models']
    return models[0]['model'] if len(models)==1 and models[0]['model'].get('image') and models[0]['model']['accepted']['owned'] and models[0]['model']['accepted']['signaled'] else None
   before=wait(current_image);check('controlledCurrentRealmOriginalImageUnaffectedByOldCompletion',before['scope']['binding']==first_binding,state=before)
   def current_snapshot():
    lines=[line for line in full_log().splitlines() if line.startswith('native-client-webkit-snapshot-job: ')]
    if not lines:return None
    image=pathlib.Path(lines[-1].split(' path=',1)[1]);assert image.parent==private and image.name.startswith('delayed-webkit.png.request-')
    return image if image.is_file() else None
   image=wait(current_snapshot);check('controlledNewSnapshotRequestChronologyPreserved',image.name=='delayed-webkit.png.request-2.png' and not (private/'delayed-webkit.png').exists(),path=str(image))
   decoder=s.host.launch('controlled-reopened-pixels',[pre['pixelOracle'],str(image)],env=env);decoder.wait(timeout=5);check('controlledCurrentSnapshotIndependentPixelOracleNormalExit',decoder.returncode==0)
   pixels=json.loads((private/'controlled-reopened-pixels.log').read_text());check('controlledCurrentRealmActualSourcePixels',pixels['red']==19200 and pixels['green']==0 and pixels['blue']==0,pixels=pixels)
   def current_paint():
    surface=private_states()[-1]['privatePolicy']['visuals']['surface'];rows=[json.loads(line.split(': ',1)[1]) for line in full_log().splitlines() if line.startswith('controlled-native-paint-observation: ')]
    return next((row for row in reversed(rows) if row['nativeEpoch']==str(second_epoch) and row['publication']==surface['publication'] and row['lease']==surface['lease']),None)
   paint=wait(current_paint);check('controlledCurrentRealmNativePaintAndClosedCurtain',paint['gtkAfterPaint'] and not paint['physicalFrameQualified'] and paint['opacity']==0 and paint['width']==700 and paint['height']==420,observation=paint)
   output=private/'reopened-wayland-output.png';grab=s.host.launch('controlled-reopened-wayland-output',['/usr/bin/grim','-o','WAYLAND-1',str(output)],env=env);grab.wait(timeout=5);check('controlledReopenedActualOutputCaptureNormalExit',grab.returncode==0)
   region=[paint['x']+8,paint['y']+48,paint['width']-16,paint['height']-56];decoder=s.host.launch('controlled-reopened-popup-region',[pre['popupCurtainOracle'],str(output),*map(str,region)],env=env);decoder.wait(timeout=5);check('controlledReopenedIndependentPopupRegionOracleNormalExit',decoder.returncode==0)
   region_pixels=json.loads((private/'controlled-reopened-popup-region.log').read_text());check('controlledReopenedActualClosedCurtainRegion',region_pixels['red']==0 and region_pixels['green']==0 and region_pixels['blue']==0 and region_pixels['opaque']==region_pixels['samples'],pixels=region_pixels)
   after=current_image();check('controlledCurrentOriginalImageStillCurrentAfterOutput',after is not None and after['scope']['context']==before['scope']['context'] and after['accepted']==before['accepted'],state=after)
   pointer('controlled-reclose','move 400 500\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
   final=wait(drained);wait(lambda:'controlled-native-realm-retired: epoch='+str(second_epoch)+' ' in full_log());check('controlledReopenedOriginalNativeCustodyDrainedAndStrictlyClosed',final['nativeEffectError']=='' and full_log().count('controlled-native-snapshot-released:')==1,state=final)
   r.update(actualOldResultAcrossReopenedRealmQualified=True,actualGUIRealmReopenQualified=True,actualSamePolicyRetained=True,actualOriginalNativeBindingRetained=True,actualReopenedWebKitPixels=pixels,actualReopenedNativePaint=paint,actualReopenedClosedCurtainRegionPixels=region_pixels,nativeGrantResets=0)

   web.terminate();web.wait(timeout=5);check('controlledFullHostNormalExit',web.returncode==0 and 'shared-host-exit: failure=0 rendered=1' in full_log() and 'Controlled native teardown incomplete:' not in full_log())
   r.update(actualControlledFactoryActivated=True,actualNativePolicyDriverActivated=True,actualPureWebKitRendererActivated=True,actualScopedURIRouterRegistered=True,actualDOMStampReceiptObserved=True,physicalRevealQualified=False,physicalConcealmentQualified=False,actualCapturedPixelsQualified=False,fullWorkloadProgressQualified=False,reloadRecoveryQualified=False)
  finally:
   if web and web.poll() is None:web.terminate();web.wait(timeout=5)
   for name,p in fixtures:
    if p.poll() is None:
     control=private/(name+'-control');temporary=private/(name+'-control.tmp');temporary.write_text('1 quit\n');temporary.chmod(0o600);temporary.replace(control);p.wait(timeout=5)
     check('controlled'+name.title()+'NormalExit',p.returncode==0)
   wait(lambda:len(s.data('clients'))==0)
   if loaded:check('controlledOwningPluginUnloads',s.ctl('plugin','unload',pre['pair']['plugin']['path']).strip()=='ok');loaded=False
  s.evidence['serialNativeCampaign']=True
 r['passed']=True
except Exception as error:r.update(passed=False,error=repr(error),traceback=traceback.format_exc())
finally:
 if s:
  r['privateHost']=s.host.evidence;r['cleanupPassed']=bool(s.host.evidence.get('runtimeGone') and not s.host.evidence.get('remainingDescendants') and not s.host.evidence.get('unexpectedInnerDescendants') and not s.host.evidence.get('cleanupErrors'));r['ownedExitCodes']=[{'name':row['name'],'pid':row['pid'],'start':row['start'],'exitCode':p.returncode} for p,row in s.host.processes]
 if private.exists():shutil.copytree(private,OUT/'private-evidence',symlinks=True)
 r['passed']=r['passed'] and r.get('cleanupPassed',False) and all(row['exitCode']==0 for row in r.get('ownedExitCodes',[]));r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error','')}),flush=True)
raise SystemExit(not r['passed'])
