"""Actual private parent-seat -> AQ viewport -> child -> GTK recipient probe."""
import importlib.util,json,os,re,shutil,socket,struct,subprocess,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
host=module('parent_input_host',ROOT/'candidate_host.py');host.original.qa.require_qa_scope()
inspection=module('parent_input_inspection',ROOT/'qa/fixture-inspection.py')
interactive=module('parent_input_interactive',ROOT/'qa/interactive-client.py')
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir()
OUTPUT=Path('/home/hoskinson/window-integration-qa')/('elm-parent-input-'+str(time.time_ns()))
report={'passed':False,'mainDesktopActions':False,'scope':'Original V44 held-button/capability/full parent-cover focus-layout and stationary reentry oracle on exact V64 core/V30 AQ; private native transport only, no physical-device/full-release acceptance','checks':[]}
s=None;fixture=None;cover=None
LUA=b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
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
 report.update(buildReport=str(buildPath),buildReportSHA256=host.digest(buildPath),inputs={str(p):host.digest(p) for p in [Path(__file__),ROOT/'candidate_host.py',ROOT/'parent-probe-build.json',ROOT/'aq-tuple.json',ROOT/'native-build-report.json',ROOT/'fixture.py',ROOT/'qa/fixture-inspection.py',ROOT/'qa/interactive-client.py',ROOT/'parent-cover.py']})
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
   controls=OUTPUT/'fixture-control.json';events=OUTPUT/'fixture-events.jsonl'
   fixture=s.host.launch('recipient',['/usr/bin/python3','-B',str(ROOT/'fixture.py'),str(controls),str(events)],env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0'))
   def observed():return inspection.inspect(events,s.data('clients'))
   first=wait(observed);check('exactLaunchedFixturePID',first['pid']==fixture.pid);address=first['address'];report['fixtureIdentity']={'pid':first['pid'],'address':address,'title':first['title']}
   def inject(commands,expected=0):
    s.guard();assert host.original.same_process(parent) and identity==host.original.socket_identity(path,s.host.runtime)
    result=subprocess.run([build['client']],input=commands,text=True,capture_output=True,env=dict(s.host.env,ELM_PARENT_INPUT_QA='1'),cwd=s.host.runtime,timeout=5)
    messages=[json.loads(line) for line in result.stdout.splitlines()]
    check('parentClientNormalExit' if expected==0 else 'parentClientRejectedRequest',result.returncode==expected,commands=commands,messages=messages,stderr=result.stderr)
    return messages
   initial=inject('motion 1 1\nquit\n')
   check('naturalInitialParentMotionAccepted',len(initial)==2 and initial[0].get('ready') is True and initial[1].get('accepted') is True)
   modes=[(800,600,1),(640,480,1),(960,640,2),(800,600,1)]
   for index,(width,height,scale) in enumerate(modes):
    if index:
     receipt=s.ctl('eval',f'hl.monitor({{output="WAYLAND-1",mode="{width}x{height}@60",position="0x0",scale={scale},transform=0}})').strip();check('childModeChangeRequested',receipt=='ok',mode=[width,height,scale],receipt=receipt)
    monitor=wait(lambda:next((m for m in s.data('monitors') if m['name']=='WAYLAND-1' and m['width']==width and m['height']==height and m['scale']==scale),None))
    current=wait(observed);check('sameActualRecipientAcrossModes',current['address']==address and current['pid']==first['pid'],mode=[width,height,scale],observed=current)
    # This is wire-level queued viewport evidence, not pixel presentation proof.
    wait(lambda:'set_destination(800, 600)' in (OUTPUT/'hyprland.log').read_text(errors='replace'))
    points=[(current['size'][0]/2,current['size'][1]/2),(24,24),(current['size'][0]-24,current['size'][1]-24)]
    for point in points:
     before=wait(observed);seq=before['sequence'];parentPoint=inspection.parent_point(before,point,monitor,[800,600]);px,py=(round(v) for v in parentPoint)
     # Expected logical recipient point accounts for integer parent-coordinate quantization.
     expected=[px*(width/scale)/800-before['at'][0]+monitor['x'],py*(height/scale)/600-before['at'][1]+monitor['y']]
     messages=inject(f'motion {px} {py}\npress 272\nrelease 272\nquit\n')
     check('threeParentRequestsAccepted',len(messages)==4 and messages[0].get('ready') is True and all(m.get('accepted') is True for m in messages[1:]),mode=[width,height,scale],parentPoint=[px,py])
     def delivered():
      latest=observed()
      return latest if latest and inspection.delivered_since(latest,seq,'button-release',expected,button=1) else None
     after=wait(delivered)
     presses=inspection.delivered_since(after,seq,'button-press',expected,button=1);releases=inspection.delivered_since(after,seq,'button-release',expected,button=1)
     check('actualGTKRecipientAndCoordinates',len(presses)==1 and len(releases)==1 and after['counts']['button-press']==before['counts']['button-press']+1 and after['counts']['button-release']==before['counts']['button-release']+1,mode=[width,height,scale],widgetPoint=point,parentPoint=[px,py],expected=expected,press=presses,release=releases)
   before=wait(observed);inject('motion -1 0\nquit\n',expected=6);after=wait(observed)
   check('rejectedParentMotionDoesNotDeliverButtons',after['counts']['button-press']==before['counts']['button-press'] and after['counts']['button-release']==before['counts']['button-release'],before=before['counts'],after=after['counts'])
   report['interactiveClients']=[]
   def new_controller(name):
    client=interactive.InteractiveClient(s.host,host.original,buildPath,host.digest(buildPath),guard=s.guard,name=name)
    report['interactiveClients'].append(client.evidence)
    return client
   def physical(target,seq,kind,expected=None,button=1):
    return [event for event in inspection.delivered_since(target,seq,kind,expected,button=button)
            if event.get('eventType')==(4 if kind=='button-press' else 7)]
   def received(seq,kind,expected=None,button=1):
    current=observed()
    return current if current and physical(current,seq,kind,expected,button) else None
   def current_monitor():
    return next(m for m in s.data('monitors') if m['name']=='WAYLAND-1')
   def move_to(client,target):
    monitor=current_monitor();point=[target['size'][0]/3,target['size'][1]/3]
    pp=inspection.parent_point(target,point,monitor,[800,600]);px,py=(round(value) for value in pp)
    expected=[px*(monitor['width']/monitor['scale'])/800-target['at'][0]+monitor['x'],
              py*(monitor['height']/monitor['scale'])/600-target['at'][1]+monitor['y']]
    client.send(f'motion {px} {py}')
    return expected
   def press(client,label,button=272):
    before=wait(observed);expected=move_to(client,before);client.send(f'press {button}')
    gtk={272:1,273:3,274:2}[button]
    after=wait(lambda:received(before['sequence'],'button-press',expected,gtk))
    events=physical(after,before['sequence'],'button-press',expected,gtk)
    check(label+':physicalPressBeforeTransition',len(events)==1 and not physical(after,before['sequence'],'button-release',button=gtk)
          and after['pid']==first['pid'] and after['address']==address,press=events,expected=expected)
    return before['sequence'],expected
   def released(seq,label,expected=None,button=1):
    after=wait(lambda:received(seq,'button-release',expected,button))
    presses=physical(after,seq,'button-press',button=button);releases=physical(after,seq,'button-release',expected,button)
    check(label+':exactPhysicalPair',len(presses)==1 and len(releases)==1
          and presses[0]['sequence']<releases[0]['sequence'] and after['address']==address and after['pid']==first['pid'],
          press=presses,release=releases,expected=expected)
    return after
   def clean_click(label):
    client=new_controller(label+'-clean-click');seq,expected=press(client,label+':cleanClick')
    client.send('release 272');released(seq,label+':cleanClick',expected);client.quit()
    check(label+':cleanControllerNormalExit',client.process.returncode==0)
   for label,width,height,scale in [('held-shrink',640,480,1),('held-scale',960,640,2),('held-restore',800,600,1)]:
    client=new_controller(label);seq,originalPoint=press(client,label)
    prior=wait(observed)
    receipt=s.ctl('eval',f'hl.monitor({{output="WAYLAND-1",mode="{width}x{height}@60",position="0x0",scale={scale},transform=0}})').strip()
    check(label+':modeRequestedWhileHeld',receipt=='ok',mode=[width,height,scale])
    monitor=wait(lambda:next((m for m in s.data('monitors') if m['name']=='WAYLAND-1' and m['width']==width and m['height']==height and m['scale']==scale),None))
    def resized_recipient():
     value=observed()
     return value if value and value['size']!=prior['size'] else None
    changed=wait(resized_recipient)
    check(label+':sameRecipientResizedWhileHeld',changed['pid']==first['pid'] and changed['address']==address
          and len(physical(changed,seq,'button-press'))==1 and not physical(changed,seq,'button-release'),
          oldSize=prior['size'],newSize=changed['size'],monitor=monitor)
    expected=move_to(client,changed);client.send('release 272');released(seq,label,expected);client.quit()
    check(label+':persistentControllerNormalExit',client.process.returncode==0)
    clean_click(label)
   for label,shutdown in [('held-controller-quit','quit'),('held-controller-eof','eof')]:
    client=new_controller(label);seq,expected=press(client,label)
    getattr(client,shutdown)();released(seq,label,expected)
    check(label+':balancedControllerNormalExit',client.process.returncode==0,shutdown=shutdown)
    clean_click(label)
   client=new_controller('duplicate-parent-press');seq,expected=press(client,'duplicate-parent-press')
   denial=client.send('press 272',expected=False);client.quit();released(seq,'duplicate-parent-press',expected)
   check('duplicateParentPressRefusedAndControllerBalanced',denial['accepted'] is False and client.process.returncode==6)
   clean_click('after-duplicate-parent-refusal')
   client=new_controller('unmatched-parent-release');before=wait(observed)
   denial=client.send('release 272',expected=False);client.quit();after=wait(observed)
   check('unmatchedParentReleaseRefusedWithoutPhysicalPair',denial['accepted'] is False and client.process.returncode==6
         and not physical(after,before['sequence'],'button-press') and not physical(after,before['sequence'],'button-release'))
   clean_click('after-unmatched-parent-refusal')
   client=new_controller('three-held-buttons-eof');before=wait(observed);expected=move_to(client,before)
   for button,gtk in [(272,1),(273,3),(274,2)]:
    client.send(f'press {button}');wait(lambda gtk=gtk:received(before['sequence'],'button-press',expected,gtk))
   client.eof()
   for gtk in [1,3,2]:released(before['sequence'],'three-held-buttons-eof:'+str(gtk),expected,button=gtk)
   check('threeHeldButtonsControllerNormalExit',client.process.returncode==0)
   clean_click('after-three-held-buttons')
   report['capabilityCycles']=[]
   for cycle,held in enumerate([False,True]):
    label='capability-held' if held else 'capability-idle'
    controller=new_controller(label)
    if held:
     seq,expected=press(controller,label)
    else:
     before=wait(observed);seq=before['sequence'];expected=move_to(controller,before)
    before=wait(observed);old_mice=s.data('devices')['mice']
    check(label+':oneActualNestedPointerBeforeLoss',len(old_mice)==1 and old_mice[0]['name']=='wl_pointer',devices=old_mice)
    controller.send('pointer-capability 0')
    if held:released(seq,label,expected)
    wait(lambda:s.data('devices') if not s.data('devices')['mice'] else None)
    after_loss=wait(observed)
    check(label+':actualNestedPointerRetired',not s.data('devices')['mice'],before=old_mice,after=s.data('devices'))
    check(label+':noExtraPhysicalButtonsOnLoss',len(physical(after_loss,seq,'button-press'))==(1 if held else 0) and len(physical(after_loss,seq,'button-release'))==(1 if held else 0),counts=after_loss['counts'])
    controller.quit();check(label+':lossControllerNormalExit',controller.process.returncode==0)
    denied=new_controller(label+'-duplicate-disable');denied.send('pointer-capability 0',expected=False);denied.quit()
    check(label+':duplicateDisableRejected',denied.process.returncode==6 and not s.data('devices')['mice'])
    denied=new_controller(label+'-motion-absent');denied.send('motion 100 100',expected=False);denied.quit()
    check(label+':absentPointerMotionRejected',denied.process.returncode==6 and not s.data('devices')['mice'])
    scale=2 if cycle==0 else 1
    receipt=s.ctl('eval',f'hl.monitor({{output="WAYLAND-1",mode="800x600@60",position="0x0",scale={scale},transform=0}})').strip()
    check(label+':layoutRequestedWithNoPointer',receipt=='ok',scale=scale)
    wait(lambda:next((m for m in s.data('monitors') if m['name']=='WAYLAND-1' and m['width']==800 and m['height']==600 and m['scale']==scale),None))
    settle=time.monotonic()+.25
    while time.monotonic()<settle:s.guard();time.sleep(.04)
    after_layout=wait(observed)
    check(label+':noButtonsFromRetiredAnchorAfterLayout',after_layout['counts']['button-press']==after_loss['counts']['button-press'] and after_layout['counts']['button-release']==after_loss['counts']['button-release'] and not s.data('devices')['mice'],before=after_loss['counts'],after=after_layout['counts'])
    restored=new_controller(label+'-restore');restored.send('pointer-capability 1')
    wait(lambda:s.data('devices') if len(s.data('devices')['mice'])==1 else None)
    fresh=s.data('devices')['mice']
    check(label+':oneActualNestedPointerRestored',len(fresh)==1 and fresh[0]['name']=='wl_pointer',devices=fresh)
    restored.quit();check(label+':restoreControllerNormalExit',restored.process.returncode==0)
    clean_click(label+'-restored')
    denied=new_controller(label+'-duplicate-enable');denied.send('pointer-capability 1',expected=False);denied.quit()
    check(label+':duplicateEnableRejectedWithoutDeviceDuplication',denied.process.returncode==6 and len(s.data('devices')['mice'])==1)
    report['capabilityCycles'].append({'held':held,'before':old_mice,'absentCounts':after_layout['counts'],'restored':fresh,'scaleWhileAbsent':scale})
   # A real parent fullscreen GTK surface owns parent focus while the child layout changes.
   report['parentFocusCycles']=[]
   for cycle,scale in enumerate([2,1]):
    label='parent-focus-scale-'+str(scale)
    pre=wait(observed);anchor_controller=new_controller(label+'-anchor');move_to(anchor_controller,pre);anchor_controller.quit()
    child_position=s.data('cursorpos')
    cover_controls=OUTPUT/(label+'-control.json');cover_events=OUTPUT/(label+'-events.jsonl')
    wire_before=(OUTPUT/'hyprland.log').read_text(errors='replace')
    cover=s.host.launch(label,['/usr/bin/python3','-B',str(ROOT/'parent-cover.py'),str(cover_controls),str(cover_events)],env=dict(s.host.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0'))
    def cover_rows():
     return [json.loads(line) for line in cover_events.read_text().splitlines()] if cover_events.exists() else []
    def cover_ready():
     rows=cover_rows()
     return rows[-1] if rows and rows[-1]['pid']==cover.pid and rows[-1]['geometry']['recipientAllocation']['width']==800 and rows[-1]['geometry']['recipientAllocation']['height']==600 and rows[-1]['geometry']['mapped'] else None
    wait(cover_ready)
    before_child=wait(observed);before_cover=cover_rows()[-1]['sequence']
    inject('motion 400 300\nquit\n')
    def actual_cover_enter():
     rows=[r for r in cover_rows() if r['sequence']>before_cover and r['kind'] in ('enter','motion') and r['pid']==cover.pid and r['eventWidgetIsRecipient'] and r['eventWindowIsOwned'] and abs(r['x']-400)<1.1 and abs(r['y']-300)<1.1]
     return rows[-1] if rows else None
    wait(actual_cover_enter)
    # GTK allocation alone does not prove the parent compositor has picked this view.
    # Require an actual native enter or motion recipient before pressing; original observation deadlines remain unchanged.
    inject('press 272\nrelease 272\nquit\n')
    def actual_cover_pair():
     rows=[r for r in cover_rows() if r['sequence']>before_cover]
     presses=[r for r in rows if r['kind']=='button-press' and r['eventType']==4]
     releases=[r for r in rows if r['kind']=='button-release' and r['eventType']==7]
     return (presses,releases) if presses and releases else None
    presses,releases=wait(actual_cover_pair)
    check(label+':actualParentCoverRecipient',len(presses)==1 and len(releases)==1 and all(r['pid']==cover.pid and r['eventWidgetIsRecipient'] and r['signalWidgetIsRecipient'] and r['eventWindowIsOwned'] and abs(r['x']-400)<1.1 and abs(r['y']-300)<1.1 for r in presses+releases),press=presses,release=releases)
    new_wire=(OUTPUT/'hyprland.log').read_text(errors='replace')[len(wire_before):]
    check(label+':actualParentPointerLeaveOnWire',bool(re.search(r'wl_pointer[#@][0-9]+\.leave\(',new_wire)),wireTail=new_wire[-3000:])
    after_cover=wait(observed)
    check(label+':coverButtonsDoNotReachChild',not physical(after_cover,before_child['sequence'],'button-press') and not physical(after_cover,before_child['sequence'],'button-release'),before=before_child['counts'],after=after_cover['counts'])
    check(label+':focusLossKeepsActualPointerDevice',len(s.data('devices')['mice'])==1)
    receipt=s.ctl('eval',f'hl.monitor({{output="WAYLAND-1",mode="800x600@60",position="0x0",scale={scale},transform=0}})').strip()
    check(label+':layoutRequestedWhileParentCoverOwnsFocus',receipt=='ok')
    monitor=wait(lambda:next((m for m in s.data('monitors') if m['name']=='WAYLAND-1' and m['width']==800 and m['height']==600 and m['scale']==scale),None))
    settle=time.monotonic()+.25
    while time.monotonic()<settle:s.guard();time.sleep(.04)
    while_covered=wait(observed)
    check(label+':unfocusedAnchorNotReplayed',s.data('cursorpos')==child_position,prior=child_position,current=s.data('cursorpos'))
    check(label+':noChildButtonsWhileCoveredLayoutChanges',while_covered['counts']['button-press']==after_cover['counts']['button-press'] and while_covered['counts']['button-release']==after_cover['counts']['button-release'],before=after_cover['counts'],after=while_covered['counts'])
    wire_return=(OUTPUT/'hyprland.log').read_text(errors='replace')
    tmp=cover_controls.with_suffix('.tmp');tmp.write_text(json.dumps({'op':'quit'}));tmp.replace(cover_controls)
    cover.wait(timeout=5);check(label+':parentCoverNormalExit',cover.returncode==0);cover=None
    wait(lambda:bool(re.search(r'wl_pointer[#@][0-9]+\.enter\(', (OUTPUT/'hyprland.log').read_text(errors='replace')[len(wire_return):])))
    after_enter=wait(observed);expected=[400*(800/scale)/800-after_enter['at'][0],300*(600/scale)/600-after_enter['at'][1]]
    seq=after_enter['sequence'];inject('press 272\nrelease 272\nquit\n')
    pair=wait(lambda:received(seq,'button-release',expected))
    check(label+':stationaryActualChildPairAfterReentry',len(physical(pair,seq,'button-press',expected))==1 and len(physical(pair,seq,'button-release',expected))==1,expected=expected,press=physical(pair,seq,'button-press',expected),release=physical(pair,seq,'button-release',expected))
    report['parentFocusCycles'].append({'scale':scale,'priorCursor':child_position,'coverPress':presses,'coverRelease':releases,'returnedExpected':expected})
   control('quit');fixture.wait(timeout=5);check('recipientNormalExit',fixture.returncode==0);fixture=None
   for path,sha in report['inputs'].items():assert host.digest(path)==sha,path
   report['passed']=True
  finally:
   if cover is not None and cover.poll() is None:
    tmp=cover_controls.with_suffix('.tmp');tmp.write_text(json.dumps({'op':'quit'}));tmp.replace(cover_controls);cover.wait(timeout=5)
   if fixture is not None and fixture.poll() is None:control('quit');fixture.wait(timeout=5)
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
