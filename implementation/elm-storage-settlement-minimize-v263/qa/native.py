"""Real pointer -> Elm update -> authenticated native effect -> authoritative DOM."""
import importlib.util,json,os,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];CORE=REPO/'implementation/elm-grab-safe-background-v89';GUI=REPO/'implementation/elm-storage-stale-fix-v256'
spec=importlib.util.spec_from_file_location('private_effect_host',CORE/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0,str(GUI/'adapter'));from endpoint import start_time,Refused
from effect_endpoint import Endpoint
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir();OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-gui-effects-'+str(time.time_ns()))
POINTER=Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
OPERATION='minimize';FAULT='lost'
FIXTURE=ROOT/'fixture.py';SUP=REPO/'implementation/elm-storage-stale-supervisor-v257'
report={'passed':False,'scope':'Private real pointer/Elm/effect/DOM path plus stopped broker pending interruption and explicit fresh-binding recovery; no renderer/compositor restart, full scene, GPU, AT, IME, UX or release acceptance','checks':[],'mainDesktopActions':False};apps=[];s=None;loaded=False;failed_web=None
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
 report.update(buildReport=str(build_path),buildReportSHA256=host.digest(build_path),pair=pair,inputs={str(p):host.digest(p) for p in (Path(__file__),ROOT/'qa/inspection.py',ROOT/'qa/sampling.py',POINTER,FIXTURE,CORE/'candidate_host.py',SUP/'supervisor.py',SUP/'runtime-manifest.json',SUP/'cohort.py')})
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),1600,1000,LUA,mesa_vendor=True) as s:
  try:
   assert s.ctl('plugin','load',plugin).strip()=='ok';loaded=True
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':start_time(native['pid']),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello()
   env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')
   control=OUTPUT/'fixture-control.json'
   fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control)],env=env);apps.append(fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
   wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' for w in s.data('clients')))
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'hide-peer'}));temp.replace(control)
   wait(lambda:not any(w['title']=='ELM-ACTIVATION-PEER' for w in s.data('clients')))
   supervisor=s.host.launch('elm-supervisor',['/usr/bin/python3','-B',str(SUP/'cohort.py'),'--manifest',str(SUP/'runtime-manifest.json'),'--authority-config',str(config_path),'--qa','--qa-log-directory',str(OUTPUT)],env=dict(env,ELM_WINDOW_RECOVERY_FAULT=('before-effect-write' if FAULT=='unread' else 'after-submit')));apps.append(supervisor)
   def supervisor_events(prefix):
    log=OUTPUT/'elm-supervisor.log'
    return [json.loads(line[len(prefix):]) for line in log.read_text().splitlines() if line.startswith(prefix)]
   def starts():return supervisor_events('supervisor-host-start: ')
   first=wait(lambda:starts()[-1] if starts() else None);web_pid=first['pid'];web_start=first['start'];failed_pid=web_pid
   cohort=wait(lambda:supervisor_events('cohort-ready: ')[-1] if supervisor_events('cohort-ready: ') else None);report['cohort']=cohort
   check('cohortScopeExcludesCompositorAndApplicationFixture',cohort['controlGroup'] in Path('/proc/'+str(web_pid)+'/cgroup').read_text() and cohort['controlGroup'] not in Path('/proc/'+str(native['pid'])+'/cgroup').read_text() and cohort['controlGroup'] not in Path('/proc/'+str(fixture.pid)+'/cgroup').read_text(),cohort=cohort)

   check('supervisedHostIsOwnedSealedNativeBinary',Path('/proc/'+str(web_pid)+'/exe').resolve()==(build_path.parent/'elm-host').resolve() and start_time(web_pid)==web_start,child=first)
   sys.path.insert(0,str(ROOT/'qa'))
   from inspection import Collector
   current_log=Path(first['log'])
   collector=Collector()
   def projection():return collector.read(current_log.read_text(errors='replace'))
   def row(state):
    p=projection()
    action='Restore ' if state=='Minimized' else 'Minimize '
    return next((g for g in p['groups'] if g['label'].startswith(action) and not g['disabled']),None) if p and p['phase']=='Coherent' else None
   def journal():
    return [json.loads(line.split('frontend-request: ',1)[1]) for line in current_log.read_text().splitlines() if line.startswith('frontend-request: ') and json.loads(line.split('frontend-request: ',1)[1])['kind']=='window-effect']
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
   initial=wait(group);check('actualElmGroupedControl',initial['label'].startswith('Minimize '),group=initial)
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
   def choose(label):
    control_group=wait(group);before_journal=journal();click(control_group)
    item=wait(lambda:selection(label))
    check('multipleFamilyPrimaryOpensPickerWithoutEffect',journal()==before_journal,projection=projection())
    click(item)
    wait(lambda:projection()['transaction']=='Committed' and projection()['phase']=='Coherent' and projection()['picker'] is None)
    request=journal()[-1]
    check('pickerSelectionEmitsActivate',request['intent']['operation']=='activate' and request['intent']['incarnation']==item['incarnation'],request=request)
    return item['incarnation']
   def press_key(code):
    s.guard();process=subprocess.run([str(keyboard)],input=f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
    check('ownedKeyboardCommandNormalExit',process.returncode==0,code=code,stderr=process.stderr)
   def supervisor_idle_snapshot():
    values={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in Path('/proc/'+str(supervisor.pid)+'/status').read_text().splitlines() if ':' in line}
    return {'voluntarySwitches':int(values['voluntary_ctxt_switches']),'involuntarySwitches':int(values['nonvoluntary_ctxt_switches']),'waitChannel':Path('/proc/'+str(supervisor.pid)+'/wchan').read_text().strip()}
   idle_samples=[supervisor_idle_snapshot()]
   for _ in range(4):s.guard();time.sleep(.5);idle_samples.append(supervisor_idle_snapshot())
   report['supervisorIdleSamples']=idle_samples
   check('supervisorBlocksOnKernelEventsAtWarmIdle',all('ep' in row['waitChannel'].lower() for row in idle_samples),samples=idle_samples)
   from sampling import sample_tree
   def frames(prefix):return [json.loads(line[len(prefix):]) for line in current_log.read_text().splitlines() if line.startswith(prefix)]
   def window_facts():return client.scene_facts('440')
   initial_facts=window_facts();check('oneVisibleNativeWindowStartsWithRealKeyboardFocus',len(initial_facts['facts']['windows'])==1 and not initial_facts['facts']['windows'][0]['minimized'] and key_recipient('ELM-AUTHORITY-FIXTURE'))
   target=initial_facts['facts']['windows'][0]['incarnation']
   def native_minimized():return next(w['minimized'] for w in window_facts()['facts']['windows'] if w['incarnation']==target)
   def pixels(stage,minimized):
    path=OUTPUT/(stage+'.png');subprocess.run(['grim',str(path)],env=s.env,check=True,timeout=5)
    import gi
    gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    picture=GdkPixbuf.Pixbuf.new_from_file(str(path));data=picture.get_pixels();stride=picture.get_rowstride();channels=picture.get_n_channels()
    assert (picture.get_width(),picture.get_height())==(800,600) and channels in [3,4]
    window=next(w for w in window_facts()['facts']['windows'] if w['incarnation']==target);x,y,width,height=window['geometry']
    # Inspect the fixture's body below its title/entry and compositor diagnostic
    # banner. Whole-output red also includes Hyprland's startup warning stripe.
    left,top,right,bottom=map(int,(x+16,y+80,x+width-16,y+height-16))
    assert 0<=left<right<=picture.get_width() and 0<=top<bottom<=picture.get_height()
    count=sum(1 for py in range(top,bottom) for px in range(left,right) if data[py*stride+px*channels]>220 and data[py*stride+px*channels+1]<45 and data[py*stride+px*channels+2]<45)
    check(stage+'ActualApplicationPixelsMatchNativeMinimized',count==0 if minimized else count>2000,redPixels=count,minimized=minimized,bodyRegion=[left,top,right,bottom],nativeGeometry=window['geometry'],image=str(path))
   def input_state(stage,minimized):
    if not minimized:check(stage+'ActualKeyboardRecipient',key_recipient('ELM-AUTHORITY-FIXTURE'));return
    events=control.with_suffix('.events.jsonl');prior=events.read_text().splitlines() if events.exists() else []
    result=subprocess.run([str(keyboard)],input='sleep 100\nkey 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
    delivered=[json.loads(line) for line in events.read_text().splitlines()[len(prior):]]
    check(stage+'MinimizedApplicationReceivesNoKey',result.returncode==0 and not any(e['kind']=='key' and e['keyval']==97 for e in delivered),events=delivered)
   if OPERATION=='restore':
    click(wait(lambda:row('Visible')));wait(lambda:projection()['transaction']=='Committed' and native_minimized())
    check('restoreSetupUsesActualCommittedMinimize',journal()[-1]['intent']['operation']=='minimize' and native_minimized())
   initial_minimized=OPERATION=='restore';pixels('beforeFault',initial_minimized);input_state('beforeFault',initial_minimized)
   initial_binding=[f['binding'] for f in frames('backend-frame: ') if f['kind']=='attached'][-1]
   recovery_dir=Path(config['runtime'])/'elm-window-recovery'/config['instance']/initial_binding['lifetime']
   report['journalNamespace']={'instance':config['instance'],'lifetime':initial_binding['lifetime'],'path':str(recovery_dir)}
   check('actualBrokerCompletesNamespacedMigrationBeforeAttached',(recovery_dir/'migration.json').is_file() and json.loads((recovery_dir/'migration.json').read_text())['target']=={'instance':config['instance'],'lifetime':initial_binding['lifetime']})
   arm=recovery_dir/('host-before-write-arm' if FAULT=='unread' else 'fault-arm');arm.write_bytes(b'before-effect-write\n' if FAULT=='unread' else b'after-submit\n');arm.chmod(0o600)
   click(wait(lambda:row('Minimized' if initial_minimized else 'Visible')))
   marker_path=recovery_dir/('host-before-write-marker.json' if FAULT=='unread' else 'fault-marker.json')
   def marker_ready():
    if not marker_path.exists():return None
    try:return json.loads(marker_path.read_text())
    except json.JSONDecodeError:return None
   marker=wait(marker_ready);report['operationFaultMarker']=marker
   old_request=journal()[-1];old_binding=old_request['binding'];report['operation']=OPERATION;report['faultBoundary']=FAULT
   check('actualPrimaryActionHasRequestedMinimizeOrRestore',old_request['intent']['operation']==OPERATION and old_request['intent']['incarnation']==target,request=old_request)
   wait(lambda:projection()['transaction']=='Pending' and projection()['picker'] is None)
   tree=sample_tree(web_pid,web_start);report['brokerTree']=tree
   backend=json.loads((SUP/'runtime-manifest.json').read_text())['backend']
   brokers=[r for r in tree['processes'] if r['pid']!=web_pid and Path('/proc/'+str(r['pid'])+'/cmdline').read_bytes().split(b'\0')[:1]==[b'/usr/bin/python3'] and backend.encode() in Path('/proc/'+str(r['pid'])+'/cmdline').read_bytes().split(b'\0')]
   check('oneOriginalBrokerIdentityOwnsSelectedOperation',len(brokers)==1)
   broker=brokers[0];broker_pid=broker['pid'];broker_start=broker['start']
   check('faultTargetsActualOwnedBrokerPIDAndStart',start_time(broker_pid)==broker_start and cohort['controlGroup'] in Path('/proc/'+str(broker_pid)+'/cgroup').read_text(),broker=broker)
   expected_minimized=initial_minimized if FAULT=='unread' else OPERATION=='minimize'
   wait(lambda:native_minimized()==expected_minimized)
   admitted=json.loads((recovery_dir/'host-intent.json').read_text())
   check('selectedWindowIntentHasDurableHostAdmission',admitted['status']=='Pending' and admitted['binding']==old_binding and admitted['intent']==old_request['intent'],admitted=admitted)
   if FAULT=='unread':
    check('actualHostHoldsOperationBeforeBrokerRead',marker['hostPID']==web_pid and int(marker['brokerPID'])==broker_pid and marker['request']==old_request and 'host-before-write-held: durable-marker=1' in current_log.read_text(),marker=marker)
    s.guard();os.kill(broker_pid,signal.SIGSTOP)
   else:
    check('actualNativeCommitPrecedesLostMinimizeOrRestoreReceipt',marker['pid']==broker_pid and marker['start']==broker_start and marker['outcome']['status']=='Committed' and marker['outcome']['intent']==old_request['intent'] and marker['durableRecord']['status']=='Pending',marker=marker)
   wait(lambda:next(line for line in Path('/proc/'+str(broker_pid)+'/status').read_text().splitlines() if line.startswith('State:')).split()[1]=='T')
   check('pendingUIHasNoMatchingNativeTerminalReceipt',not any(f.get('kind')=='effect-outcome' and f.get('intent')==old_request['intent'] for f in frames('backend-frame: ')))
   pixels('atInterruption',expected_minimized);input_state('atInterruption',expected_minimized)
   before=window_facts();native_identity={'pid':native['pid'],'start':start_time(native['pid'])}
   report['stateBeforeRecovery']={'expectedMinimized':expected_minimized,'facts':before}

   record_path=recovery_dir/'intent.json';pending_raw=record_path.read_bytes();record_path.chmod(0o644)
   check('realNativeCommitHasOnlyPendingBrokerRecord',json.loads(pending_raw)['status']=='Pending' and marker['outcome']['status']=='Committed')
   s.guard();assert start_time(broker_pid)==broker_start;os.kill(broker_pid,signal.SIGCONT)
   wait(lambda:projection()['phase']=='Detached' and projection()['transaction']=='Unknown')
   def bar_reports():return [json.loads(line.split('surface-report: origin=bar ',1)[1])['body'] for line in current_log.read_text().splitlines() if line.startswith('surface-report: origin=bar ')]
   wait(lambda:bar_reports() and 'Repair it, then reconnect.' in bar_reports()[-1]['text'])
   check('actualBarExplainsUnverifiedSettlementStorage','Repair it, then reconnect.' in bar_reports()[-1]['text'] and 'could not be confirmed' in bar_reports()[-1]['text'],body=bar_reports()[-1])
   check('actualBrokerClassifiesSettlementReadRefusal',any(f.get('kind')=='host-recovery-failed' and f.get('reason')=='unverified' for f in frames('backend-frame: ')))
   wait(lambda:'backend-exit: waited=1 normal=1 code=1' in current_log.read_text())
   check('settlementFailureExitIsExplicitlyRecorded','backend-exit: waited=1 normal=1 code=1' in current_log.read_text())
   check('failedSettlementPreservesPendingBytes',record_path.read_bytes()==pending_raw)
   check('failedSettlementWithholdsNativeTerminalReceipt',not any(f.get('kind')=='effect-outcome' and f.get('intent')==old_request['intent'] for f in frames('backend-frame: ')))
   def application_state(facts):return sorted((w['incarnation'],w['application'],w['minimized'],tuple(w['geometry'])) for w in facts['facts']['windows'])
   check('settlementFailurePreservesActualCommittedWindowState',application_state(window_facts())==application_state(before))
   pixels('settlementFailure',expected_minimized);input_state('settlementFailure',expected_minimized)
   effect_count=len(journal());record_path.chmod(0o600)
   observation=time.monotonic()+.5
   while time.monotonic()<observation:
    s.guard();assert len(journal())==effect_count and len([f for f in frames('backend-frame: ') if f['kind']=='attached'])==1;time.sleep(.04)
   check('permissionCorrectionDoesNotAutomaticallyRetryOrReplay',len(journal())==effect_count)
   pixels('correctedBeforeRetry',expected_minimized);input_state('correctedBeforeRetry',expected_minimized)
   wait(lambda:projection()['reconnect'] and not projection()['reconnect']['disabled']);click(projection()['reconnect']);wait(group)
   fresh_binding=[f['binding'] for f in frames('backend-frame: ') if f['kind']=='attached'][-1]
   check('explicitReconnectGetsFreshBindingWithoutHostReplacement',fresh_binding!=old_binding and fresh_binding['lifetime']==old_binding['lifetime'] and start_time(web_pid)==web_start and len(starts())==1,old=old_binding,new=fresh_binding)
   uncertain=next(f for f in frames('backend-frame: ') if f.get('kind')=='host-uncertain')
   check('newBrokerReportsOnlyInformationalUnknownIntent',uncertain['binding']==fresh_binding and uncertain['intent']==old_request['intent'])
   check('freshSnapshotRetainsUnknownAndActualCommittedState',projection()['transaction']=='Unknown' and application_state(window_facts())==application_state(before))
   check('explicitReconnectDoesNotReplayCommittedOldIntent',len(journal())==effect_count)
   pixels('afterExplicitReconnect',expected_minimized);input_state('afterExplicitReconnect',expected_minimized)
   next_operation='restore' if expected_minimized else 'minimize'
   click(wait(lambda:row('Minimized' if expected_minimized else 'Visible')))
   wait(lambda:projection()['transaction']=='Committed' and projection()['phase']=='Coherent' and native_minimized()!=expected_minimized)
   explicit=journal()[-1]
   check('freshExplicitActionUsesCurrentStateAndAdvancedIdentity',explicit['intent']['operation']==next_operation and int(explicit['intent']['request'])==int(old_request['intent']['request'])+1 and int(explicit['intent']['generation'])==int(old_request['intent']['generation'])+1 and explicit['binding']==fresh_binding,request=explicit)
   final_minimized=not expected_minimized;pixels('freshExplicitAction',final_minimized);input_state('freshExplicitAction',final_minimized)
   check('freshExplicitActionPreservesApplicationAndCompositor',window_facts()['facts']['windows'][0]['incarnation']==target and start_time(native['pid'])==native_identity['start'])
   report['settlementFailure']={'kind':'real public journal mode refuses guarded settle read after actual native Committed receipt','mode':0o644,'pendingRecord':json.loads(pending_raw),'oldBinding':old_binding,'freshBinding':fresh_binding,'sameHost':True,'noAutomaticReplay':True,'evidencePreserved':True}
   owned=next(row for process,row in s.host.processes if process is supervisor);s.host.stop(owned,supervisor);supervisor.wait(timeout=5)
   check('normalSupervisorStopHasOneGeneration',supervisor.returncode==0 and len(starts())==1)
   report['supervisorEvents']={'starts':starts(),'exits':supervisor_events('supervisor-host-exit: ')};report['cohortCleanup']=supervisor_events('cohort-cleanup: ')
   check('ownedShellScopeHasNoRemainingProcesses',report['cohortCleanup'][-1]['remaining']==[])
   temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'quit'}));temp.replace(control);fixture.wait(timeout=5);check('fixtureNormalExit',fixture.returncode==0)
   report['scope']='Actual post-native-commit journal settlement read refusal, typed repair/Unknown UI, six actual pixel/input stages, explicit same-host reconnect without replay, fresh current-state action; other storage stages and full release open'
   report['passed']=True
  finally:
   for process in reversed(apps):
    if process.poll() is None:
     owned=next(row for p,row in s.host.processes if p is process);s.host.stop(owned,process);process.wait(timeout=5)
    if process is not fixture:
     expected=0
     report['checks'].append({'name':'hostExitMatchesDeclaredFailureOrNormalExit','passed':process.returncode==expected,'exitCode':process.returncode,'expected':expected});report['passed']=report['passed'] and process.returncode==expected
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
