"""Actual private parent-seat -> AQ viewport -> child -> GTK recipient probe."""
import importlib.util,json,os,re,shutil,socket,struct,subprocess,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
host=module('parent_input_host',ROOT/'candidate_host.py');host.original.qa.require_qa_scope()
inspection=module('parent_input_inspection',ROOT/'qa/fixture-inspection.py')
interactive=module('held_parent_interactive',ROOT/'qa/interactive-client.py')
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir()
OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-parent-input-'+str(time.time_ns()))
report={'passed':False,'mainDesktopActions':False,'scope':'Private protocol6 held-key child PID/start connection loss; actual GTK keyboard recipient and Core89 key/modifier/keybind ledgers; unchanged AQ120 baseline, no installed change or full release acceptance','checks':[]}
case=json.loads((ROOT/'held-mask.json').read_text());MASK=case['mask'];assert case['schema']==1 and type(MASK) is int and 1<=MASK<=3
KEYS=[code for bit,code in [(1,30),(2,42)] if MASK & bit]
report['heldKeyMask']=MASK
s=None;fixture=None;cover=None;controller=None;observer_loaded=False
LUA=b'hl.config({debug={disable_logs=false,enable_stdout_logs=true},xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
def check(name,value,**data):
 report['checks'].append({'name':name,'passed':bool(value),**data});assert value,name
def wait(function):
 until=time.monotonic()+6
 while time.monotonic()<until:
  s.guard();value=function()
  if value:return value
  time.sleep(.04)
 raise RuntimeError('Unchanged six-second observation deadline')
def control(operation):
 tmp=controls.with_suffix('.tmp');tmp.write_text(json.dumps({'op':operation}));tmp.replace(controls)
try:
 desc=json.loads((ROOT/'parent-probe-build.json').read_text());buildPath=Path(desc['buildReport']);assert host.digest(buildPath)==desc['buildReportSHA256'];build=json.loads(buildPath.read_text());assert build['passed']
 for rel,sha in build['inputs'].items():assert host.digest(ROOT/rel)==sha,rel
 assert host.digest(build['client'])==build['clientSHA256'] and host.digest(build['module'])==build['moduleSHA256']
 report.update(buildReport=str(buildPath),buildReportSHA256=host.digest(buildPath),inputs={str(p):host.digest(p) for p in [Path(__file__),ROOT/'candidate_host.py',ROOT/'parent-probe-build.json',ROOT/'aq-tuple.json',ROOT/'native-build-report.json',ROOT/'fixture.py',ROOT/'qa/fixture-inspection.py',ROOT/'qa/interactive-client.py',ROOT/'observer-build.json',ROOT/'held-mask.json']})
 shutil.copy2(__file__,OUT/'native.py')
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as s:
  try:
   core=json.loads((ROOT/'native-build-report.json').read_text())
   check('exactReviewedCoreMapped',s.evidence['hyprlandMaps']['files'].get(str(Path(core['binary']).resolve()))==core['sha256'])
   maps=s.evidence['westonMaps']['files'];check('exactParentInputModuleMapped',maps.get(str(Path(build['module']).resolve()))==build['moduleSHA256'])
   parent=next(row for proc,row in s.host.processes if row['name']=='weston');assert host.original.same_process(parent)
   path=s.host.runtime/'weston-host';identity=host.original.socket_identity(path,s.host.runtime)
   with socket.socket(socket.AF_UNIX) as connection:
    connection.settimeout(2);connection.connect(str(path));pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
   check('exactOwnedParentSocketPeer',pid==parent['pid'] and uid==os.getuid() and identity==host.original.socket_identity(path,s.host.runtime) and host.original.same_process(parent),pid=pid,uid=uid,start=parent['start'],socket=identity)
   observer_desc=json.loads((ROOT/'observer-build.json').read_text());observer_report=Path(observer_desc['buildReport']);assert host.digest(observer_report)==observer_desc['buildReportSHA256']
   observer=json.loads(observer_report.read_text());assert observer['passed'] and observer['core']['sha256']==core['sha256'] and not observer['missingSymbols'] and len(observer['owningHeaders'])==694
   assert host.digest(observer['binary'])==observer['binarySHA256']
   for rel,digest in observer['artifacts'].items():assert host.digest(observer_report.parent/rel)==digest,rel
   report['observerBuild']={**observer_desc,'binary':observer['binary'],'binarySHA256':observer['binarySHA256']}
   loaded=s.ctl('plugin','load',observer['binary']);check('owningObserverLoaded',loaded.strip().lower()=='ok',reply=loaded);observer_loaded=True
   mapped=host.original.mapped_files(s.child.pid);check('exactObserverMapped',mapped['files'].get(str(Path(observer['binary']).resolve()))==observer['binarySHA256'])
   def held_state():
    row=json.loads(s.ctl('elm_held_state'));assert row.get('schema')==1 and row.get('pid')==s.child.pid,row
    return row
   check('noHeldKeysBeforePhysicalInput',held_state()['keys']==[] and held_state()['bindKeys']==[] and held_state()['mods']==0)
   controls=OUTPUT/'fixture-control.json' ;events=OUTPUT/'fixture-events.jsonl'
   fixture=s.host.launch('recipient',['/usr/bin/python3','-B',str(ROOT/'fixture.py'),str(controls),str(events)],env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0'))
   def observed():return inspection.inspect(events,s.data('clients'))
   first=wait(observed);check('exactLaunchedFixturePID',first['pid']==fixture.pid);address=first['address'];report['fixtureIdentity']={'pid':first['pid'],'address':address,'title':first['title']}
   def inject(commands,expected=0):
    s.guard();assert host.original.same_process(parent) and identity==host.original.socket_identity(path,s.host.runtime)
    result=subprocess.run([build['client']],input=commands,text=True,capture_output=True,env=dict(s.host.env,ELM_PARENT_INPUT_QA='1'),cwd=s.host.runtime,timeout=5)
    messages=[json.loads(line) for line in result.stdout.splitlines()]
    check('parentClientNormalExit' if expected==0 else 'parentClientRejectedRequest',result.returncode==expected,commands=commands,messages=messages,stderr=result.stderr,exitCode=result.returncode)
    return messages
   target=wait(observed);monitor=next(m for m in s.data('monitors') if m['name']=='WAYLAND-1')
   point=[target['size'][0]/2,target['size'][1]/2];px,py=(round(v) for v in inspection.parent_point(target,point,monitor,[800,600]))
   expected=[px*(monitor['width']/monitor['scale'])/800-target['at'][0]+monitor['x'],py*(monitor['height']/monitor['scale'])/600-target['at'][1]+monitor['y']]
   seq=target['sequence'];inject(f'motion {px} {py}\npress 272\nrelease 272\nquit\n')
   current=wait(lambda:observed() if inspection.delivered_since(observed(),seq,'button-release',expected,button=1) else None)
   presses=[e for e in inspection.delivered_since(current,seq,'button-press',button=1) if e['eventType']==4]
   releases=[e for e in inspection.delivered_since(current,seq,'button-release',button=1) if e['eventType']==7]
   check('actualRecipientPhysicalPairBeforeLoss',len(presses)==len(releases)==1 and all(abs(e['x']-expected[0])<1.1 and abs(e['y']-expected[1])<1.1 for e in presses+releases),press=presses,release=releases,expected=expected)
   child=s.child_identity;check('exactOwnedChildProcess',child['pid']==s.child.pid and host.original.same_process(child),identity=child)
   before=s.data('devices');check('livePointerAndKeyboardBeforeLoss',len(before['mice'])==1 and len(before['keyboards'])==1,devices=before)
   bad=inject(f"disconnect-child {child['pid']} {int(child['start'])+1}\nquit\n",expected=6)
   check('wrongChildIncarnationRefused',len(bad)==2 and bad[1]['accepted'] is False and host.original.same_process(child) and s.data('devices')==before)
   bad=inject(f"disconnect-child {parent['pid']} {parent['start']}\nquit\n",expected=6)
   check('parentTargetRefused',len(bad)==2 and bad[1]['accepted'] is False and host.original.same_process(parent) and s.data('devices')==before)
   def poll_state():
    s.guard();entries={};links={}
    for info in Path(f"/proc/{child['pid']}/fdinfo").glob('[0-9]*'):
     try:text=info.read_text()
     except FileNotFoundError:continue
     fds=[int(v) for v in re.findall(r'^tfd:\s+(\d+)\s',text,re.MULTILINE)]
     if fds:
      entries[info.name]=fds
      for fd in fds:
       try:links[str(fd)]=os.readlink(f"/proc/{child['pid']}/fd/{fd}")
       except FileNotFoundError:links[str(fd)]='gone'
    s.guard();return {'epoll':entries,'links':links}
   kernel_before=poll_state();check('actualKernelPollRegistrationObserved',bool(kernel_before['epoll']))
   report['kernelPollBefore']=kernel_before
   bad=inject(f"disconnect-held-key-child {child['pid']} {child['start']} 1\nquit\n",expected=6)
   check('missingHeldKeyMaskRefused',len(bad)==2 and bad[1]['accepted'] is False and held_state()['held'] is False)
   controller=interactive.InteractiveClient(s.host,host.original,buildPath,desc['buildReportSHA256'],guard=s.guard,name='held-transport-controller')
   report['interactive']=controller.evidence
   controller.send(f'motion {px} {py}');seq=current['sequence']
   def key_events(latest, sequence, kind):
    out=[]
    for event in latest['records']:
     if event['sequence']<=sequence or event['kind']!=kind:continue
     assert event['signalRecipient']=='parent-key-recipient' and event['signalWidgetIsWindow'] is True and event['eventWidgetIsWindow'] is True and event['eventWindowIsWindow'] is True and event['eventWindowReference'] is not None,event
     assert event['eventType']==(8 if kind=='key-press' else 9) and event['sendEvent'] is False,event
     out.append(event)
    return out
   controller.send('key-press 30');controller.send('key-release 30')
   paired=wait(lambda: observed() if key_events(observed(),seq,'key-release') else None)
   down=key_events(paired,seq,'key-press');up=key_events(paired,seq,'key-release')
   check('actualRecipientKeyPairBeforeLoss',len(down)==len(up)==1 and down[0]['hardwareKeycode']==up[0]['hardwareKeycode']==38,press=down,release=up)
   check('actualCoreKeyPairBalanced',held_state()['keys']==[] and held_state()['bindKeys']==[] and held_state()['mods']==0,state=held_state())
   seq=paired['sequence']
   for code in KEYS:controller.send(f'key-press {code}')
   def actual_held_press():
    latest=observed()
    return latest if latest and all(any(e['hardwareKeycode']==code+8 for e in key_events(latest,seq,'key-press')) for code in KEYS) else None
   current=wait(actual_held_press);state=held_state()
   held_presses=key_events(current,seq,'key-press');held_releases=key_events(current,seq,'key-release')
   check('physicalKeysHeldInActualChild',sorted(state['keys'])==sorted(KEYS) and sorted(state['bindKeys'])==sorted(code+8 for code in KEYS) and state['keyboardPresent'] is True and all(sum(e['hardwareKeycode']==code+8 for e in held_presses)==1 for code in KEYS) and not held_releases,state=state,recipient=current,physicalPress=held_presses)
   report['beforeLoss']={'devices':before,'monitors':s.data('monitors'),'recipient':current,'child':child,'parent':parent,'heldState':state}
   message=controller.send(f"disconnect-held-key-child {child['pid']} {child['start']} {MASK}")
   check('exactHeldKeyChildConnectionLossAdmitted',message['accepted'] is True)

   check('parentSurvivesWithSameSocket',host.original.same_process(parent) and identity==host.original.socket_identity(path,s.host.runtime))
   def retired():
    devices=s.data('devices');report['lastDevicesAfterLoss']=devices
    return {'devices':devices} if not devices['mice'] and not devices['keyboards'] else None
   after=wait(retired)
   check('actualPointerAndKeyboardRetiredWithinOriginalDeadline',not after['devices']['mice'] and not after['devices']['keyboards'],devices=after['devices'])
   report['heldStateAfterLoss']=held_state()
   check('actualChildHeldKeysCancelled',report['heldStateAfterLoss']['keys']==[] and report['heldStateAfterLoss']['bindKeys']==[] and report['heldStateAfterLoss']['mods']==0,state=report['heldStateAfterLoss'])
   check('sameChildProcessAndIPCRemainLive',host.original.same_process(child) and bool(s.data('version')))
   monitors=wait(lambda:{'monitors':s.data('monitors')} if not any(m['name'].startswith('WAYLAND-') for m in s.data('monitors')) else None)
   check('actualNestedOutputsRetired',not any(m['name'].startswith('WAYLAND-') for m in monitors['monitors']),monitors=monitors['monitors'])
   before_fds={fd for fds in kernel_before['epoll'].values() for fd in fds}
   def withdrawn():
    kernel_after=poll_state();after_fds={fd for fds in kernel_after['epoll'].values() for fd in fds}
    removed=before_fds-after_fds
    report['kernelPollAfter']=kernel_after;report['removedKernelPollFDs']=sorted(removed)
    removed_sockets=[fd for fd in removed if kernel_before['links'].get(str(fd),'').startswith('socket:[')]
    return {'removedSockets':removed_sockets,'after':kernel_after} if len(removed_sockets)==1 else None
   kernel=wait(withdrawn)
   dead_fd=kernel['removedSockets'][0]
   # The kernel registration may use a duplicated event-source descriptor.
   # Its closure on source removal is expected, not a fixture read failure.
   try:after_link=os.readlink(f"/proc/{child['pid']}/fd/{dead_fd}")
   except FileNotFoundError:after_link='closed'
   s.guard()
   check('failedTransportSocketWithdrawnFromActualKernelPoll',dead_fd not in {fd for fds in kernel['after']['epoll'].values() for fd in fds},removedFD=dead_fd,beforeLink=kernel_before['links'][str(dead_fd)],afterLink=after_link)
   # Parent admission does not imply child delivery: send a real balanced pair
   # through the surviving parent seat and demand an independent GTK inspection.
   controller.send(f'motion {px+1} {py+1}');controller.send('key-press 30');controller.send('key-release 30');controller.quit();controller=None
   check('survivingParentSeatAcceptsBalancedKeyPair',True)
   previous=inspection.receipts(events)[-1]['sequence'];control('inspect')
   def fresh_receipt():
    records=inspection.receipts(events)
    return records[-1] if records and records[-1]['kind']=='inspection' and records[-1]['sequence']>previous else None
   receipt=wait(fresh_receipt)
   check('liveRecipientReportsNoStalePhysicalKeys',receipt['pid']==fixture.pid and receipt['counts']['key-press']==current['counts']['key-press'] and receipt['counts']['key-release']==current['counts']['key-release']+len(KEYS),receipt=receipt)
   cancelled=key_events(inspection.inspect(events,s.data('clients')),current['sequence'],'key-release')
   check('exactCancellationForEveryAdmittedHeldKey',len(cancelled)==len(KEYS) and all(sum(e['hardwareKeycode']==code+8 for e in cancelled)==1 for code in KEYS),releases=cancelled)
   until=time.monotonic()+.3
   while time.monotonic()<until:s.guard();time.sleep(.02)
   check('retiredDevicesStayAbsent',not s.data('devices')['mice'] and not s.data('devices')['keyboards'])
   wire=(OUTPUT/'hyprland.log').read_text(errors='replace')
   check('oneShotTransportFailureDiagnostic',wire.count('Wayland parent transport failed; retiring nested resources')==1,occurrences=wire.count('Wayland parent transport failed; retiring nested resources'))
   check('noHeldKeysRevivedByLaterParentPair',held_state()['keys']==[] and held_state()['bindKeys']==[] and held_state()['mods']==0,state=held_state())
   renderer=(OUTPUT/'weston-renderer.log').read_text(errors='replace');check('parentPeerDestroyedBeforeParentBalance','held-key-peer-destroyed-before-parent-balance' in renderer)
   report['afterLoss']={'devices':after['devices'],'monitors':monitors['monitors'],'recipient':receipt}

   control('quit');fixture.wait(timeout=5);check('recipientNormalExit',fixture.returncode==0);fixture=None
   unloaded=s.ctl('plugin','unload',observer['binary']);check('observerNormallyUnloaded',unloaded.strip().lower()=='ok',reply=unloaded);observer_loaded=False
   for path,sha in report['inputs'].items():assert host.digest(path)==sha,path
   report['passed']=True
  finally:
   if controller is not None:controller.eof();controller=None
   if cover is not None and cover.poll() is None:
    tmp=cover_controls.with_suffix('.tmp');tmp.write_text(json.dumps({'op':'quit'}));tmp.replace(cover_controls);cover.wait(timeout=5)
   if fixture is not None and fixture.poll() is None:control('quit');fixture.wait(timeout=5)
   if observer_loaded:
    unloaded=s.ctl('plugin','unload',observer['binary']);assert unloaded.strip().lower()=='ok';observer_loaded=False
   registered={row['pid'] for proc,row in s.host.processes}
   for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):s.host.stop(descendant)
except Exception as error:report['error']=repr(error);report['traceback']=traceback.format_exc()
finally:
 if OUTPUT.exists():
  shutil.copytree(OUTPUT,OUT/'native-evidence',dirs_exist_ok=True)
 if s is not None:report['privateHost']=s.evidence;report['cleanupPassed']=bool(not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
 else:report['cleanupPassed']=False
 report['passed']=report['passed'] and report['cleanupPassed']
 report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True)
raise SystemExit(not report['passed'])
