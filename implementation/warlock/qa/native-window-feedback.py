"""ELM-UI-007 restore feedback on the real private Wayland/Elm/native path.

Reuse immutable ABI/runtime by reference; no preview, supervisor or new source
lineage. Native/AT acceptance remain separate, with AT explicitly outstanding.
"""
import hashlib,importlib.util,json,os,pathlib,signal,subprocess,sys,time,traceback
ACCESSIBILITY=sys.argv[1:]==['--accessibility']
CONTRAST=sys.argv[1:]==['--high-contrast']
DRAG=sys.argv[1:]==['--drag-ownership']
KEYBOARD=sys.argv[1:]==['--keyboard-shell']
ATTENTION=sys.argv[1:]==['--attention']
JUMP=sys.argv[1:]==['--jump-lists']
FILES=sys.argv[1:]==['--files']
SYSTEM=sys.argv[1:]==['--system-menu']
NOTIFICATIONS=sys.argv[1:]==['--notifications']
SETTINGS=sys.argv[1:]==['--settings'] or CONTRAST
PLACEMENT=sys.argv[1:]==['--snap-placement']
SNAP=sys.argv[1:]==['--snap-chooser'] or PLACEMENT
REFLOW=sys.argv[1:]==['--popup-reflow']
DENSEMENU=sys.argv[1:]==['--dense-menu'] or REFLOW
DENSEPICKER=sys.argv[1:]==['--dense-picker'] or DENSEMENU
DENSE=sys.argv[1:]==['--dense-taskbar']
SMALL=DENSE or DENSEPICKER
PINMENUS=sys.argv[1:]==['--pinned-menus'] or DENSE or SNAP
PRIMARY=sys.argv[1:]==['--taskbar-primary'] or PINMENUS or ATTENTION
PRE_READY_RETIRE=sys.argv[1:]==['--switcher-pre-ready-retirement']
MEMBERSHIP=sys.argv[1:]==['--switcher-membership'] or PRE_READY_RETIRE
CHORD=sys.argv[1:]==['--switcher-chord'] or MEMBERSHIP
SWITCHER=sys.argv[1:]==['--switcher'] or ACCESSIBILITY
NAV=sys.argv[1:]==['--workspace-navigation'];FOCUS=sys.argv[1:]==['--taskbar-focus'] or DENSEPICKER or KEYBOARD;PRESENTATION=sys.argv[1:]==['--launcher-presentation'];SEARCH=sys.argv[1:]==['--launcher-search'] or PRESENTATION;PINS=sys.argv[1:]==['--taskbar-pins'];CATALOG=SEARCH or PINS or PINMENUS or REFLOW or SETTINGS or NOTIFICATIONS or SYSTEM or FILES or JUMP or KEYBOARD;RETIRE_OPENER=sys.argv[1:]==['--task-view-retired-opener'];TASKVIEW=sys.argv[1:]==['--task-view'] or NAV or RETIRE_OPENER;assert not sys.argv[1:] or FOCUS or CATALOG or TASKVIEW or PRIMARY or SWITCHER or CHORD or DRAG
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];HELD=REPO/'implementation/warlock-preview-provider-v143';RUNTIME=REPO/'implementation/warlock-client-provider-native-v204'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('feedback_private_host',RUNTIME/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope();sys.path.insert(0,str(RUNTIME/'qa'))
from session_bus import isolate_session_host
if ACCESSIBILITY:
 spec_at=importlib.util.spec_from_file_location('warlock_accessibility_session',ROOT/'qa/accessibility-session.py');at_session=importlib.util.module_from_spec(spec_at);spec_at.loader.exec_module(at_session);isolate_session_host=at_session.isolate_session_host
from system_isolation import supply,validate
from inspection import Collector
isolate_session_host(host)
sys.path.insert(0,str(ROOT/'adapter'));from effect_endpoint import Endpoint;from endpoint import start_time
if PLACEMENT:
 from geometry_endpoint import GeometryEndpoint as Endpoint
pre=json.loads((RUNTIME/'qa/preflight.json').read_text());pair=pre['pair'];build_path=pathlib.Path(pre['controlledHostBuild']);build=json.loads(build_path.read_text());assert build['passed'];binary=build_path.parent/'elm-host';assert sha(binary)==build['binarySHA256']
assert not NAV or (ROOT/'qa/current-native-pair.json').exists()
assert not (ROOT/'native/authority.cpp').exists() or (ROOT/'qa/current-native-pair.json').exists()
if (ROOT/'qa/current-native-pair.json').exists():
 native_pair=json.loads((ROOT/'qa/current-native-pair.json').read_text());authority_path=REPO/native_pair['authorityReport'];assert sha(authority_path)==native_pair['authorityReportSHA256'];authority=json.loads(authority_path.read_text());assert authority['passed'] and authority['missingSymbols']==[]
 assert native_pair['pair']['aquamarine']==pair['aquamarine'] and sha(RUNTIME/'qa/preflight.json')==native_pair['unchangedRuntimePreflightSHA256']
 if native_pair['pair']['core']!=pair['core']:
  focus=authority['focusCoreReport'];focus_path=REPO/focus['report'];assert sha(focus_path)==focus['reportSHA256'];focus_core=json.loads(focus_path.read_text())
  assert focus_core['passed'] and focus_core['existingPublicHeadersUnchanged'] and focus_core['existingObjectLayoutsUnchanged']
  assert sha(ROOT/'native/core/SeatManager.cpp')==focus_core['sourceSHA256']
  assert native_pair['pair']['core']=={'path':focus_core['binary'],'sha256':focus_core['binarySHA256']}
  ancestor_path=pathlib.Path(focus_core['ancestor']['report']);assert sha(ancestor_path)==focus_core['ancestor']['reportSHA256'];ancestor=json.loads(ancestor_path.read_text())
  assert pair['core']=={'path':ancestor['binary'],'sha256':ancestor['binarySHA256']}
  assert all(sha(p)==h for p,h in focus_core['dependencies'].items())
  assert all(sha(p)==h for p,h in focus_core['linkDependencies'].items())
 assert native_pair['authorityInputs']==authority['inputs'] and all(sha(ROOT/p)==h for p,h in authority['inputs'].items()) and all(sha(p)==h for p,h in authority['dependencies'].items())
 assert native_pair['pair']['plugin']=={'path':authority['binary'],'sha256':authority['binarySHA256']};pair=native_pair['pair']
CURRENT=(ROOT/'qa/current-search-build.json').exists()
assert not (CATALOG or TASKVIEW) or CURRENT
if CURRENT:
 current=json.loads((ROOT/'qa/current-search-build.json').read_text());build_path=REPO/current['report'];assert sha(build_path)==current['reportSHA256'];build=json.loads(build_path.read_text());assert build['passed'];binary=build_path.parent/'elm-host';assert sha(binary)==build['binarySHA256'];assert all(sha(ROOT/p)==h for p,h in build['inputs'].items() if p.startswith(('src/','native/','adapter/')))
else:
 ancestry=json.loads((ROOT/'ANCESTRY.json').read_text());assert all(sha(ROOT/p)==h for p,h in ancestry['parentSources'].items() if p.startswith('native/'))
for row in pair.values():assert sha(row['path'])==row['sha256']
assets=ROOT/'assets';assert all(sha(assets/n)==h for n,h in json.loads((ROOT/'qa'/('current-search-build.json' if CURRENT else 'current-feedback-build.json')).read_text())['compiledAssets'].items())
subprocess.run(['node','--check',str(assets/'bar-adapter.js')],check=True)
OUT=ROOT/'qa/runs'/(('native-accessibility-' if ACCESSIBILITY else 'native-high-contrast-' if CONTRAST else 'native-drag-ownership-' if DRAG else 'native-keyboard-shell-' if KEYBOARD else 'native-attention-' if ATTENTION else 'native-jump-lists-' if JUMP else 'native-files-' if FILES else 'native-system-menu-' if SYSTEM else 'native-notifications-' if NOTIFICATIONS else 'native-settings-' if SETTINGS else 'native-snap-placement-' if PLACEMENT else 'native-snap-chooser-' if SNAP else 'native-dense-picker-' if DENSEPICKER else 'native-dense-taskbar-' if DENSE else 'native-pinned-menus-' if PINMENUS else 'native-switcher-membership-' if MEMBERSHIP else 'native-switcher-chord-' if CHORD else 'native-switcher-' if SWITCHER else 'native-primary-' if PRIMARY else 'native-workspace-navigation-' if NAV else 'native-task-view-' if TASKVIEW else 'native-pins-' if PINS else 'native-search-' if SEARCH else 'native-taskbar-focus-' if FOCUS else 'native-feedback-')+str(time.time_ns()));OUT.mkdir(parents=True)
OUTPUT=pathlib.Path('/home/hoskinson/window-integration-qa')/('warlock-window-feedback-'+str(time.time_ns()))
focus_host=None
if native_pair.get('pair',{}).get('core')!=pre['pair']['core']:
 # The frozen host's process selector reads its sibling native build tuple.
 # Keep every other verified runtime asset at the frozen root and give this
 # private, recorded copy the newly compiled core tuple. Never edit that root.
 focus_inputs=OUTPUT.with_name(OUTPUT.name+'-inputs');focus_inputs.mkdir(mode=0o700)
 original_host=(RUNTIME/'candidate_host.py').read_text();needle='ROOT=Path(__file__).resolve().parent'
 assert original_host.count(needle)==1
 adapted=original_host.replace(needle,'ROOT=Path('+repr(str(RUNTIME))+')')
 host_path=focus_inputs/'focus_host.py';host_path.write_text(adapted)
 (focus_inputs/'native-build-report.json').write_text(json.dumps({'result':'pass','binary':pair['core']['path'],'sha256':pair['core']['sha256']}))
 spec=importlib.util.spec_from_file_location('focus_core_private_host',host_path);host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
 isolate_session_host(host)
 focus_host={'originalSHA256':sha(RUNTIME/'candidate_host.py'),'adaptedPath':str(host_path),'adaptedSHA256':sha(host_path),'change':'Keep frozen asset ROOT; sibling process tuple points only to the source-verified focus core.'}
POINTER=pathlib.Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer');FIXTURE=RUNTIME/'fixture.py'
retirement_fixture=None
primary_fixture=None
if RETIRE_OPENER:
 fixture_inputs=OUTPUT.with_name(OUTPUT.name+'-inputs');fixture_inputs.mkdir(mode=0o700,exist_ok=True)
 fixture_source=FIXTURE.read_text();needle="        elif request['op'] == 'retire-peer':"
 assert fixture_source.count(needle)==1
 adapted=fixture_source.replace(needle,"        elif request['op'] == 'retire-primary':\n            windows.pop('ELM-AUTHORITY-FIXTURE').destroy()\n"+needle)
 original_fixture=FIXTURE;FIXTURE=fixture_inputs/'retire-opener-fixture.py';FIXTURE.write_text(adapted)
 retirement_fixture={'originalSHA256':sha(original_fixture),'path':str(FIXTURE),'sha256':sha(FIXTURE),'change':'Retire only the original primary window; create no replacement/modal.'}
if PRIMARY:
 fixture_inputs=OUTPUT.with_name(OUTPUT.name+'-inputs');fixture_inputs.mkdir(mode=0o700,exist_ok=True)
 fixture_source=FIXTURE.read_text();initial="create('ELM-AUTHORITY-FIXTURE', 'red')\ncreate('ELM-ACTIVATION-PEER', 'green')"
 assert fixture_source.count(initial)==1 and fixture_source.count('control = Path(sys.argv[1])')==1
 adapted=fixture_source.replace('control = Path(sys.argv[1])',"GLib.set_prgname('warlock-primary-fixture' if sys.argv[2]=='primary' else 'warlock-peer-fixture')\ncontrol = Path(sys.argv[1])")
 adapted=adapted.replace(initial,"create('ELM-AUTHORITY-FIXTURE', 'red') if sys.argv[2]=='primary' else create('ELM-ACTIVATION-PEER', 'green')")
 if ATTENTION:
  needle="        elif request['op'] == 'retire-peer':";assert adapted.count(needle)==1
  adapted=adapted.replace(needle,"        elif request['op'] == 'request-attention':\n            next(iter(windows.values())).present()\n            log(next(iter(windows)), 'attention-requested')\n"+needle)
 original_fixture=FIXTURE;FIXTURE=fixture_inputs/'primary-action-fixture.py';FIXTURE.write_text(adapted)
 primary_fixture={'originalSHA256':sha(original_fixture),'path':str(FIXTURE),'sha256':sha(FIXTURE),'change':'One original colored GTK root per process; distinct program identities create two single-family taskbar entries.'}
if CHORD:
 fixture_inputs=OUTPUT.with_name(OUTPUT.name+'-inputs');fixture_inputs.mkdir(mode=0o700,exist_ok=True)
 fixture_source=FIXTURE.read_text();initial="create('ELM-AUTHORITY-FIXTURE', 'red')\ncreate('ELM-ACTIVATION-PEER', 'green')"
 assert fixture_source.count(initial)==1
 adapted=fixture_source.replace(initial,initial+"\ncreate('ELM-CHORD-THIRD', 'blue')")
 needle="        elif request['op'] == 'retire-peer':"
 assert adapted.count(needle)==1
 adapted=adapted.replace(needle,"        elif request['op'] == 'arrive-peer':\n            create('ELM-ACTIVATION-PEER', 'green')\n        elif request['op'] == 'arrive-chord':\n            create('ELM-CHORD-ARRIVAL', 'blue')\n        elif request['op'] == 'retire-third':\n            windows.pop('ELM-CHORD-THIRD').destroy()\n        elif request['op'] == 'retire-arrival':\n            windows.pop('ELM-CHORD-ARRIVAL').destroy()\n        elif request['op'] == 'retire-primary':\n            windows.pop('ELM-AUTHORITY-FIXTURE').destroy()\n"+needle)
 original_fixture=FIXTURE;FIXTURE=fixture_inputs/'chord-fixture.py';FIXTURE.write_text(adapted)
 chord_fixture={'originalSHA256':sha(original_fixture),'path':str(FIXTURE),'sha256':sha(FIXTURE),'change':'Third independent GTK root plus controlled retire/arrival operations; original client input/controllers unchanged.'}
report={'schema':1,'requirements':['ELM-UI-007'],'scenarios':['restore-pending','restore-refused','restore-unknown'],'scope':'Actual pointer/Elm/native effect feedback and private compositor pixels; no AT/IME/full release acceptance','nativeFeedbackObserved':False,'nativeAcceptance':False,'assistiveTechnologyAccepted':False,'fullReleaseAccepted':False,'mainDesktopActions':False,'passed':False,'checks':[],'sourceInputs':{str(p.relative_to(ROOT)):sha(p) for folder in ['src','native','adapter','assets'] for p in (ROOT/folder).iterdir() if p.is_file()},'pair':pair,'nativeHost':{'path':str(binary),'sha256':sha(binary),'heldBuild':str(build_path),'heldBuildSHA256':sha(build_path)},'runtimeByReference':{'root':str(RUNTIME),'hostSHA256':sha(RUNTIME/'candidate_host.py')},'helpers':[],'nativeFixtures':[]};s=None;loaded=False;apps=[];notification_producer=None;broker=None;paused=False;sequence=0;chord_keyboard=None;chord_writer=None;drag_pointer=None;drag_writer=None
if focus_host:report['focusHostAdaptation']=focus_host
if retirement_fixture:report['retirementFixture']=retirement_fixture
if primary_fixture:report['primaryFixture']=primary_fixture
if SEARCH:report.update(requirements=['ELM-UI-005','ELM-UX-029'],scenarios=['search-no-match','search-race','search-refused','launcher-refused'],scope='Actual current query and private catalog, native typing/Enter refusal and no duplicate launch; AT/IME and popup physical presentation acceptance remain pending',popupPresentationAccepted=False)
if KEYBOARD:report.update(requirements=['ELM-UX-023'],scenarios=['ux-023','keyboard-launcher','keyboard-taskbar-groups','keyboard-switcher','keyboard-task-view','keyboard-snap-chooser','keyboard-menus','keyboard-settings','keyboard-notifications','keyboard-jump-lists'],scope='Original physical keyboard-only migrated-surface journey; no pointer helper, native focus/effect/readback. Applicable AT and independent original acceptance remain separate.',nativeKeyboardShellObserved=False,keyboardSurfaces=[])
if ATTENTION:report.update(requirements=['ELM-UX-009'],scenarios=['ux-009'],scope='Actual GTK activation request while inactive, native bound/revisioned urgency read, distinct visible taskbar indicators and accessible DOM state. Actual AT and independent acceptance remain open.',nativeAttentionObserved=False)
if JUMP:report.update(requirements=['ELM-UX-010'],scenarios=['ux-010','jump-list-recent-identity'],scope='Physical private native jump list: catalog-declared actions, exact application-bound local XBEL file, actual GIO argv; foreign entries absent. Native negative admission is separate adapter evidence, AT and independent acceptance remain open.',nativeJumpListsObserved=False)
if FILES:report.update(requirements=['ELM-UX-033'],scenarios=['ux-033'],scope='Actual installed Files explorer in private home/runtime; physical Elm collection choice, exact native instance reuse, location readback, no unchanged file operation source edits. Independent/AT and other-workspace summon acceptance remain open.',nativeFilesObserved=False)
if SYSTEM:report.update(requirements=['ELM-UX-032'],scenarios=['ux-032'],scope='Actual isolated native menu with current private PipeWire volume and login1 session/power capabilities, unavailable network, physical keyboard changes, readback, confirmation and pixels; real hardware, AT and independent acceptance remain open.',nativeSystemMenuObserved=False)
if NOTIFICATIONS:report.update(requirements=['ELM-UX-031'],scenarios=['ux-031','notification-valid','notification-reused'],scope='Actual private native producers and physical Elm center: exactly-once current dispatch, expired history and reused-incarnation queued refusal; independent/AT acceptance remains open.',nativeNotificationsObserved=False)
if SETTINGS:report.update(requirements=['ELM-UX-030'],scenarios=['ux-030'],scope='Actual integrated settings controls, exact saved appearance, native text size/reservation and whole-host restart; native-bound invalid scale refuses without changing stored or presented settings. Independent and applicable AT/IME/release acceptance remain open.',nativeSettingsObserved=False)
if PINS:report.update(requirements=['ELM-UI-004','ELM-UX-004'],scenarios=['taskbar-zero','ux-004'],scope='Actual native keyboard pin/reorder, shell restart, identity order and one current zero-window launch; popup physical presentation and AT acceptance remain separate',popupPresentationAccepted=False,nativePinJourneyObserved=False)
if TASKVIEW:report.update(requirements=['ELM-UX-017','ELM-UI-006'],scenarios=['ux-017','overview-cancel'],scope='Actual two populated native workspaces, exact window membership and active marker, keyboard/pointer local browsing and Escape recipient; independent and applicable AT acceptance remain pending',nativeTaskViewJourneyObserved=False)
if RETIRE_OPENER:report['scope']='Actual native Task View browse then primary opener retirement; Escape must not revive its incarnation or dispatch a window effect. Independent/AT acceptance remains pending.'
if NAV:report.update(requirements=['ELM-UI-002','ELM-UI-006','ELM-UX-008'],scenarios=['activate-other-workspace','overview-select','ux-008','activation-refused'],scope='Actual minimized workspace-2 family selected through Task View and taskbar; native receipts, focus/keyboard, pixels and unchanged membership; stale-context refusal; other-output, partial-refusal and AT acceptance remain separate',nativeNavigationJourneyObserved=False,authorityBuild={'path':str(authority_path),'sha256':sha(authority_path)})
if FOCUS:report.update(requirements=['ELM-UI-004','ELM-UX-024'],scenarios=['taskbar-group','ux-024'],scope='Actual native picker traversal and Escape/focus recipient diagnosis; menu/AT original acceptance remains pending')
if CHORD:report.update(requirements=['ELM-UI-003','ELM-UX-012','ELM-UX-013'],scenarios=['switcher-order','switcher-cancel','switcher-zero-one','switcher-retire-arrive','ux-012','ux-013'],scope='Actual global native Alt-Tab three-root order, startup release, native cancellation fence, membership freeze and zero/one; modal/protected/AT/independent acceptance remain open',nativeChordJourneyObserved=False,chordFixture=chord_fixture)
if MEMBERSHIP:report.update(scenarios=['switcher-membership','switcher-retire-arrive'],scope='Actual native '+('one-step selected retirement' if PRE_READY_RETIRE else 'two-step buffered retirement')+' before readiness/arrival, modal-family activation/recipient and minimized workspace-2 restore; lock, other-output, AT and independent review remain open',nativeMembershipJourneyObserved=False)
if SWITCHER:report.update(requirements=['ELM-UI-003'],scenarios=['switcher-order','switcher-cancel'],scope='Actual native MRU observation, integrated switcher control pixels, local keyboard cycling/cancel and identity-bound chosen activation; global Alt-Tab journal, modal representation and AT/independent acceptance remain pending',nativeSwitcherJourneyObserved=False)
if PRIMARY:report.update(requirements=['ELM-UI-004'],scenarios=['taskbar-inactive','taskbar-active','taskbar-minimized'],scope='Actual pointer single-family activation/minimize/restore, exact native receipt and GTK keyboard recipient, MRU/desktop succession and pixels; primary keyboard and AT acceptance remain pending',nativePrimaryJourneyObserved=False)
if PINMENUS:report.update(requirements=['ELM-UI-008','ELM-UX-023'],scenarios=['menu-invocation','keyboard-menus'],scope='Actual current running pin, native secondary click/Menu/Shift-F10 menus and existing minimize/restore path; dense/enlarged-text, AT and independent acceptance remain open',nativePinnedMenusObserved=False)
if SNAP:report.update(requirements=['ELM-UX-019','ELM-UX-020'],scenarios=['ux-019','ux-020'],scope='Actual native snap chooser presentation/keyboard/output-scale invalidation only; native snap placement authority and accepted half-work-area oracle remain required',nativeSnapChooserObserved=False)
if CONTRAST:report.update(requirements=['ELM-UX-027'],scenarios=['ux-027'],scope='Actual native high contrast appearance at enlarged text, named keyboard focus/pixels and committed persistence/restart; all-surface/theme/scale original qualification and native AT remain open.')
if PLACEMENT:report.update(scope='Actual GUI snap submission through shared allocator/custody/native geometry authority, exact half-work-area readback/pixels and stale output refusal; original independent/AT release acceptance remains separate',nativeSnapPlacementObserved=False)
if DENSE:report.update(requirements=['ELM-UI-008'],scenarios=['overflow-first-last','overflow-resize','menu-invocation'],scope='Actual small native output, enlarged text, configured overflowing pins, physical keyboard/wheel/menu traversal and output resize; AT and independent review remain open',nativeDenseTaskbarObserved=False)
if DENSEPICKER:report.update(requirements=['ELM-UI-008','ELM-UI-004'],scenarios=['overflow-first-last','overflow-resize','menu-invocation','taskbar-group'],scope='Actual ten-root native enlarged-text picker arrow/endpoints, first/last menus and identity-bound selection/input; browser resize continuity is separate; native popup reflow, AT and independent review remain open',nativeDensePickerObserved=False)
if DENSEMENU:report.update(requirements=['ELM-UI-008'],scenarios=['overflow-first-last','menu-invocation'],scope='Actual ten-root 480x360 native output at 200% text; overflow of current three-operation menu, typed endpoint/arrows/disabled/Tab/Escape and operation-label pixels; renderer capacity/growth/blur are component observations; AT/independent and native popup reflow remain open',nativeDenseMenuObserved=False)
if REFLOW:report.update(requirements=['ELM-UI-008'],scenarios=['overflow-resize'],scope='Actual 18 configured overflowing pins and ten-root picker, 200% text, physical picker/menu selection across native output geometry changes with fresh leases and pixels; applicable AT/independent acceptance remains separate',nativePopupReflowObserved=False)
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
if SMALL:LUA=LUA.replace(b'800x600',b'480x360' if DENSEMENU else b'480x600')
if ATTENTION:LUA+=b'hl.config({misc={focus_on_activate=false}})\n'
if CHORD or KEYBOARD or DRAG:LUA+=(ROOT/'native/switcher-bindings.lua').read_bytes()
if KEYBOARD or DRAG:LUA+=(ROOT/'native/shell-bindings.lua').read_bytes()
if DRAG:
 LUA+=b'hl.monitor({output="WAYLAND-2",mode="800x600@60",position="800x0",scale=1})\n'
 report.update(requirements=['ELM-UX-021'],scenarios=['ux-021'],scope='Actual native move/resize input across taskbar and two outputs; native controller owner/serial, real blocked shell shortcut and competing native effect, one end per gesture. No caption/edge, AT, touch/tablet or independent acceptance inferred.')
if ACCESSIBILITY:report.update(requirements=['ELM-UX-025'],scenarios=['actual-surface-at'],scope='Actual private GTK/WebKit taskbar and switcher AT-SPI tree/states/focus and real Orca observations with physical input; independent original acceptance remains separate.')
def check(name,condition,**data):
 report['checks'].append({'name':name,'passed':bool(condition),**data});assert condition,name
def wait(fn,seconds=6):
 deadline=time.monotonic()+seconds
 while time.monotonic()<deadline:
  s.guard();value=fn()
  if value:return value
  time.sleep(.025)
 raise RuntimeError('Original observation deadline '+getattr(fn,'__name__',''))
def helper(command,input_text=None,timeout=5):
 global sequence
 sequence+=1;name='feedback-helper-'+str(sequence)
 if input_text is not None:
  p=OUTPUT/(name+'.input');fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:f.write(input_text)
  command=['/usr/bin/python3','-B',str(RUNTIME/'qa/input_helper.py'),str(p),*command]
 proc=s.host.launch(name,command,env=s.env)
 try:proc.wait(timeout=timeout)
 except BaseException:
  owned=next(row for p,row in s.host.processes if p is proc);s.host.stop(owned,proc);proc.wait(timeout=5);raise
 row={'name':name,'pid':proc.pid,'exitCode':proc.returncode,'command':command};report['helpers'].append(row);check(name+'NormalExit',proc.returncode==0)
 return (OUTPUT/(name+'.log')).read_text(errors='replace')
def pause(value):
 global paused
 assert start_time(broker['pid'])==broker['start'] and pathlib.Path('/proc/'+str(broker['pid'])+'/exe').resolve()==pathlib.Path('/usr/bin/python3').resolve()
 os.kill(broker['pid'],signal.SIGSTOP if value else signal.SIGCONT);paused=value
 report.setdefault('brokerStops',[]).append({'stopped':value,'pid':broker['pid'],'start':broker['start'],'clock':time.monotonic()})
def fixture_control(op):
 temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':op}));temp.replace(control)
try:
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),1600,1000,LUA,mesa_vendor=True) as s:
  try:
   plugin=pair['plugin']['path'];check('OwningPluginLoads',s.ctl('plugin','load',plugin).strip()=='ok');loaded=True
   if DRAG:
    check('CreateSecondWaylandOutput',s.ctl('output','create','wayland').strip()=='ok')
    wait(lambda:len(s.data('monitors'))==2 and all(m['width']==800 and m['height']==600 for m in s.data('monitors')))
    report['dragOutputs']=s.data('monitors')
    check('TwoNativeOutputsHaveOriginalCrossingGeometry',[(m['name'],m['x'],m['y'],m['width'],m['height']) for m in sorted(report['dragOutputs'],key=lambda m:m['x'])]==[('WAYLAND-1',0,0,800,600),('WAYLAND-2',800,0,800,600)])
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':int(start_time(native['pid'])),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello();
   if PLACEMENT:client.geometry_attach('15000')
   env=supply(s.env,s.host.runtime);validate(env,s.host.runtime);env['XDG_STATE_HOME']=str(s.host.runtime/'private-warlock-state');report['privateStateRoot']=env['XDG_STATE_HOME'];env.update(GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')
   if ACCESSIBILITY:
    env['AT_SPI_BUS_ADDRESS']='unix:path='+str(s.host.runtime/'a11y-bus');env.pop('GTK_A11Y',None);env.pop('NO_AT_BRIDGE',None)
    s.env.update(AT_SPI_BUS_ADDRESS=env['AT_SPI_BUS_ADDRESS'])
    at_bus=s.host.launch('accessibility-bus',['/usr/bin/true'],env=env);apps.append(at_bus);wait(lambda:(s.host.runtime/'a11y-bus').exists())
    at_registry=s.host.launch('accessibility-registry',['/usr/lib/at-spi2-registryd'],env=env);apps.append(at_registry)
    at_request=OUTPUT/'at-request.json';at_reply=OUTPUT/'at-reply.json';at_ready=OUTPUT/'at-ready.json';at_events=OUTPUT/'at-events.jsonl'
    at_inspector=s.host.launch('accessibility-inspector',['/usr/bin/python3','-B',str(ROOT/'qa/accessibility-inspector.py'),str(at_request),str(at_reply),str(at_ready),str(at_events)],env=env);apps.append(at_inspector);wait(lambda:at_ready.exists())
    reader_env=dict(env,ORCA_QA_UTTERANCES=str(OUTPUT/'orca-utterances.jsonl'))
    at_reader=s.host.launch('accessibility-orca',['/usr/bin/python3','-B',str(ROOT/'qa/accessibility-reader.py')],env=reader_env);apps.append(at_reader)
    def at_observe():
     global sequence
     sequence+=1;temp=at_request.with_suffix('.tmp');temp.write_text(json.dumps({'sequence':sequence}));temp.replace(at_request)
     def reply():
      if not at_reply.exists():return None
      result=json.loads(at_reply.read_text());return result if result['sequence']==sequence else None
     return wait(reply)
    wait(lambda:at_observe().get('reader'))
    held_reader=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader')
    report['accessibilityFixture']={'session':env['DBUS_SESSION_BUS_ADDRESS'],'accessibility':env['AT_SPI_BUS_ADDRESS'],'systemBusRemainsRefusing':True,'servicesExplicitlyOwned':True,'activationDisabled':True,'inspectorSHA256':sha(ROOT/'qa/accessibility-inspector.py'),'readerLauncherSHA256':sha(ROOT/'qa/accessibility-reader.py'),'sessionWrapperSHA256':sha(ROOT/'qa/accessibility-session.py'),'orcaPackageSHA256':sha(held_reader/'packages.json'),'readerEntrySHA256':sha(held_reader/'prefix/usr/bin/orca'),'speechAdapterSHA256':sha(held_reader/'silent_factory.py'),'observationAdapterSHA256':sha(held_reader/'data/orca/orca-customizations.py'),'nativeATObserved':False}
   if CATALOG:
    catalog_root=pathlib.Path(env['XDG_DATA_HOME'])/'applications';catalog_root.mkdir(mode=0o700,parents=True,exist_ok=True)
    # Only explicitly owned fixture metadata is visible to this broker.
    catalog_dirs=s.host.runtime/'empty-search-catalog';catalog_dirs.mkdir(mode=0o700)
    roots={'dataHome':env['XDG_DATA_HOME'],'dataDirs':[str(catalog_dirs)],'cacheDir':str(s.host.runtime/'search-catalog-cache')}
    broker_config=OUTPUT/'search-broker-config.json';broker_config.write_text(json.dumps({**config,'catalogRoots':roots}));broker_config.chmod(0o600)
    backend_fixture=OUTPUT/'catalog-fixture-backend.py';backend_fixture.write_text('import os,sys\nfrom pathlib import Path\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nos.execv("/usr/bin/python3",["/usr/bin/python3","-B",'+repr(str(ROOT/'adapter/daemon.py'))+','+repr(str(broker_config))+'])\n');backend_fixture.chmod(0o600)
    report['catalogFixture']={'backend':str(backend_fixture),'backendSHA256':sha(backend_fixture),'roots':roots,'originalConfigUnchanged':True}
    desktop=catalog_root/'warlock-files.desktop';desktop.write_text('[Desktop Entry]\nType=Application\nName=Files\nGenericName=File manager\nKeywords=folders;documents;\nExec=/usr/bin/true\n')
    (catalog_root/'warlock-editor.desktop').write_text('[Desktop Entry]\nType=Application\nName=Editor\nGenericName=Text editor\nExec=/usr/bin/true\n')
   if JUMP or KEYBOARD:
    import gi;gi.require_version('GLib','2.0');from gi.repository import GLib
    jump_events=OUTPUT/'jump-action-events.jsonl';jump_recorder=OUTPUT/'jump-action-recorder.py'
    jump_recorder.write_text('import json,os,sys\nwith open(sys.argv[1],"a") as stream:stream.write(json.dumps({"argv":sys.argv[2:],"pid":os.getpid()})+"\\n")\n')
    jump_document=pathlib.Path(env['HOME'])/'Warlock recent document.txt';jump_document.write_text('Owned recent document')
    jump_foreign=pathlib.Path(env['HOME'])/'Foreign recent document.txt';jump_foreign.write_text('Foreign recent document')
    jump_exec='/usr/bin/python3 '+str(jump_recorder)+' '+str(jump_events)
    (catalog_root/'warlock-editor.desktop').write_text('[Desktop Entry]\nType=Application\nName=A Warlock Editor\nExec='+jump_exec+' RECENT %u\nActions=Alpha;Beta;\n[Desktop Action Alpha]\nName=New document\nExec='+jump_exec+' ALPHA\n[Desktop Action Beta]\nName=Private window\nExec='+jump_exec+' BETA\n[Desktop Action Unsupported]\nName=Unsupported action\nExec=/usr/bin/false\n')
    bookmarks=GLib.BookmarkFile.new()
    for document,owner,title in [(jump_document,'warlock-editor.desktop','Warlock recent document'),(jump_foreign,'foreign.desktop','Foreign recent document')]:
     uri=document.as_uri();bookmarks.set_title(uri,title);bookmarks.set_mime_type(uri,'text/plain');bookmarks.set_application_info(uri,owner,'/usr/bin/false %u',1,GLib.DateTime.new_now_utc())
    jump_xbel=pathlib.Path(env['XDG_DATA_HOME'])/'recently-used.xbel';bookmarks.to_file(str(jump_xbel))
    report['jumpFixture']={'desktop':str(catalog_root/'warlock-editor.desktop'),'desktopSHA256':sha(catalog_root/'warlock-editor.desktop'),'recentSource':str(jump_xbel),'recentSHA256':sha(jump_xbel),'recorder':str(jump_recorder),'recorderSHA256':sha(jump_recorder),'document':str(jump_document),'documentSHA256':sha(jump_document),'canonicalApplicationIdentity':'warlock-editor.desktop','storedBookmarkCommandIgnored':True}
   if PINMENUS:
    (catalog_root/'warlock-running-peer.desktop').write_text('[Desktop Entry]\nType=Application\nName=Peer\nStartupWMClass=warlock-peer-fixture\nExec=/usr/bin/true\n')
   if REFLOW:
    reflow_ids=['warlock-reflow-'+str(i) for i in range(18)]
    for i in range(18):(catalog_root/(reflow_ids[i]+'.desktop')).write_text('[Desktop Entry]\nType=Application\nName=Reflow '+str(i)+'\nExec=/usr/bin/true\n')
    from taskbar_preferences import Store
    configured=Store(env['XDG_STATE_HOME']);status,saved=configured.save({'revision':configured.read()['revision'],'identities':reflow_ids})
    check('ReflowFixturePinsSavedThroughActualStore',status=='Saved' and saved['identities']==reflow_ids)
    report['configuredReflowPins']={'identities':reflow_ids,'saved':saved,'path':str(configured.path/'taskbar.json'),'sha256':sha(configured.path/'taskbar.json')}
   if DENSE:
    (catalog_root/'warlock-running-primary.desktop').write_text('[Desktop Entry]\nType=Application\nName=Primary\nStartupWMClass=warlock-primary-fixture\nExec=/usr/bin/true\n')
    dense_labels=['Primary']+['Dense '+str(i) for i in range(16)]+['Peer']
    dense_ids=['warlock-running-primary']+['warlock-dense-'+str(i) for i in range(16)]+['warlock-running-peer']
    for i in range(16):(catalog_root/('warlock-dense-'+str(i)+'.desktop')).write_text('[Desktop Entry]\nType=Application\nName=Dense '+str(i)+'\nExec=/usr/bin/true\n')
    from taskbar_preferences import Store
    configured=Store(env['XDG_STATE_HOME']);status,saved=configured.save({'revision':configured.read()['revision'],'identities':dense_ids})
    check('DenseFixturePinsSavedThroughActualStore',status=='Saved' and saved['identities']==dense_ids)
    report['configuredDensePins']={'identities':dense_ids,'labels':dense_labels,'saved':saved,'path':str(configured.path/'taskbar.json'),'sha256':sha(configured.path/'taskbar.json')}
   control=OUTPUT/'fixture-control.json';fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control),*(['primary'] if PRIMARY else [])],env=env);apps.append(fixture)
   if PRIMARY:
    peer_control=OUTPUT/'peer-control.json';peer_fixture=s.host.launch('peer-fixture',['/usr/bin/python3','-B',str(FIXTURE),str(peer_control),'peer'],env=env);apps.append(peer_fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')));wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' for w in s.data('clients')));
   if not (FOCUS or TASKVIEW or PRIMARY or SWITCHER or CHORD):fixture_control('hide-peer');wait(lambda:len(s.data('clients'))==1)
   if PRIMARY:
    peer=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER');peer_selector='address:'+peer['address']
    if not peer['floating']:check('PeerFixtureFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+peer_selector+"'})").strip()=='ok')
    check('PeerFixtureSize',s.ctl('dispatch',"hl.dsp.window.resize({x=320,y=240,window='"+peer_selector+"'})").strip()=='ok')
    check('PeerFixturePosition',s.ctl('dispatch',"hl.dsp.window.move({x="+('120' if DENSE else '400')+",y=150,window='"+peer_selector+"'})").strip()=='ok')
   if TASKVIEW:
    peer=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER')
    if NAV:
     peer_selector='address:'+peer['address'];primary=next(w for w in s.data('clients') if w['title']=='ELM-AUTHORITY-FIXTURE')
     if not peer['floating']:check('PeerFixtureFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+peer_selector+"'})").strip()=='ok')
     check('PeerFixtureSize',s.ctl('dispatch',"hl.dsp.window.resize({x=320,y=240,window='"+peer_selector+"'})").strip()=='ok')
     check('PeerFixturePosition',s.ctl('dispatch',"hl.dsp.window.move({x=360,y=150,window='"+peer_selector+"'})").strip()=='ok')
     check('PrimaryFocusBeforeFixtureMinimize',s.ctl('dispatch',"hl.dsp.focus({window='address:"+primary['address']+"'})").strip()=='ok')
     peer_identity=next(w['incarnation'] for w in client.snapshot('440')['windows'] if w['label']=='ELM-ACTIVATION-PEER')
     setup_facts=client.scene_facts('440');setup_intent={'request':'9000','generation':'9000','incarnation':peer_identity,'operation':'minimize','context':client.context(setup_facts)};setup_result=client.effect(setup_intent)
     report['nativeFixtures'].append({'intent':setup_intent,'result':setup_result});check('PeerFixtureMinimizedBeforeWorkspaceMove',setup_result['status']=='Committed',result=setup_result)
    check('OwnedPeerMovesToWorkspaceTwo',s.ctl('dispatch',"hl.dsp.window.move({workspace=2,follow=false,window='address:"+peer['address']+"'})").strip()=='ok')
    wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' and w['workspace']['id']==2 for w in s.data('clients')))
   w=next(w for w in s.data('clients') if w['title']=='ELM-AUTHORITY-FIXTURE');selector='address:'+w['address']
   if not w['floating']:check('FixtureFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+selector+"'})").strip()=='ok')
   check('FixtureSize',s.ctl('dispatch',"hl.dsp.window.resize({x=320,y=240,window='"+selector+"'})").strip()=='ok')
   check('FixturePosition',s.ctl('dispatch',"hl.dsp.window.move({x=40,y=100,window='"+selector+"'})").strip()=='ok')
   if DENSEPICKER:
    fixture_control('many-documents');wait(lambda:len(s.data('clients'))==10)
    check('TenActualNativeRoots',len(client.snapshot('442')['windows'])==10)
    for row in s.data('clients'):
     if not row['title'].startswith('LONG-DOC-'):continue
     member_selector='address:'+row['address']
     if not row['floating']:check('DenseMemberFixtureFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+member_selector+"'})").strip()=='ok')
     check('DenseMemberFixtureSize',s.ctl('dispatch',"hl.dsp.window.resize({x=320,y=240,window='"+member_selector+"'})").strip()=='ok')
     check('DenseMemberFixturePosition',s.ctl('dispatch',"hl.dsp.window.move({x=70,y="+('110' if DENSEMENU else '280')+",window='"+member_selector+"'})").strip()=='ok')
   check('FixtureFocus',s.ctl('dispatch',"hl.dsp.focus({window='"+selector+"'})").strip()=='ok')
   if CHORD:
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');report['keyboard']={'path':str(keyboard),'sha256':sha(keyboard)}
    fifo=OUTPUT/'chord-keyboard.fifo';os.mkfifo(fifo,0o600);chord_writer=os.open(fifo,os.O_RDWR|os.O_NOFOLLOW)
    input_wrapper=OUTPUT/'chord-keyboard-input.py';input_wrapper.write_text('import os,stat,sys\nfd=os.open(sys.argv[1],os.O_RDONLY|os.O_NOFOLLOW)\nst=os.fstat(fd)\nassert stat.S_ISFIFO(st.st_mode) and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o600\nos.dup2(fd,0);os.close(fd)\nos.execv(sys.argv[2],[sys.argv[2]])\n')
    chord_keyboard=s.host.launch('chord-keyboard',['/usr/bin/python3','-B',str(input_wrapper),str(fifo),str(keyboard)],env=s.env)
    report['persistentInput']={'wrapper':str(input_wrapper),'sha256':sha(input_wrapper),'fifoMode':'0600','commands':[]}
    def physical(commands):
     assert chord_keyboard.poll() is None
     before=(OUTPUT/'chord-keyboard.log').read_text().splitlines().count('ready')
     raw=(commands+'\nsync\n').encode();assert len(raw)<=4096;assert os.write(chord_writer,raw)==len(raw)
     report['persistentInput']['commands'].append(commands)
     wait(lambda:(OUTPUT/'chord-keyboard.log').read_text().splitlines().count('ready')>before)
    native_roots=client.snapshot('430')['windows'];chord_labels={row['label']:row['incarnation'] for row in native_roots}
    a,b,c=[chord_labels[name] for name in ['ELM-AUTHORITY-FIXTURE','ELM-ACTIVATION-PEER','ELM-CHORD-THIRD']]
    def native_focus(identity):
     row=client.scene_facts('430');n=str((10000 if MEMBERSHIP else 8000)+len(report['nativeFixtures']));intent={'request':n,'generation':n,'incarnation':identity,'operation':'activate','context':client.context(row)};result=client.effect(intent);report['nativeFixtures'].append({'intent':intent,'result':result});check('CommittedHistoryFixture',result['status']=='Committed',result=result)
    for identity in [a,b,c]:native_focus(identity)
    check('NativeHistoryABCBeforeFrontend',client.activation_history('430')['roots']==[c,b,a])
    physical('key 56 1\nkey 15 1\nsleep 50\nkey 15 0\n'+('key 15 1\nsleep 50\nkey 15 0\n' if MEMBERSHIP and not PRE_READY_RETIRE else '')+'key 56 0\nsleep 100')
    startup=client.switcher_journal('430',observe=True);report['startupJournalBeforeHost']=startup
    check('NativeReleaseRecordedBeforeFrontendExists',startup['chord']['released'] and startup['chord']['steps']==([1,1] if MEMBERSHIP and not PRE_READY_RETIRE else [1]) and startup['chord']['history']==[c,b,a] and not startup['chord']['consumed'])
    if MEMBERSHIP:
     fixture_control('retire-peer');wait(lambda:all(row['incarnation']!=b for row in client.snapshot('430')['windows']));fixture_control('arrive-chord');wait(lambda:any(row['label']=='ELM-CHORD-ARRIVAL' for row in client.snapshot('430')['windows']))
     report['startupAfterRetirement']=client.scene_facts('430');check('RetirementAndArrivalBeforeElmHost',b in startup['chord']['roots'] and len(client.snapshot('430')['windows'])==3)
    hold_arm=OUTPUT/'chord-hold.arm';hold_waiting=OUTPUT/'chord-hold.waiting';hold_release=OUTPUT/'chord-hold.release'
    backend_fixture=OUTPUT/'chord-backend.py'
    backend_fixture.write_text(f"""import sys,time,json
from pathlib import Path
sys.path.insert(0,{str(ROOT/'adapter')!r})
import daemon
original=daemon.handle_request
last_effect=None
retries=Path({str(OUTPUT/'chord-retries.jsonl')!r})
def handle(*args):
 global last_effect
 client,request=args[0],args[2]
 if not hasattr(client,'qa_original_effect'):
  client.qa_original_effect=client.effect
  def observed(intent):
   global last_effect
   outcome=client.qa_original_effect(intent)
   last_effect=(json.loads(json.dumps(intent)),outcome)
   return outcome
  client.effect=observed
 arm=Path({str(hold_arm)!r});waiting=Path({str(hold_waiting)!r});release=Path({str(hold_release)!r})
 if request.get('kind')=='switcher-selection-request' and arm.exists():
  arm.unlink();waiting.write_text(json.dumps(request));deadline=time.monotonic()+2
  while not release.exists():
   if time.monotonic()>=deadline:raise RuntimeError('Controlled QA hold expired')
   time.sleep(.01)
  release.unlink()
 result=original(*args)
 if request.get('kind')=='switcher-selection-request' and last_effect:
  intent,outcome=last_effect
  retry=client.qa_original_effect(intent)
  with retries.open('a') as stream:stream.write(json.dumps(dict(intent=intent,original=outcome,retry=retry,afterPreparation=request['requestId'],matches=retry==outcome))+'\\n')
  if retry!=outcome:raise RuntimeError('Exact terminal retry changed after new selection preparation')
 return result
daemon.handle_request=handle
raise SystemExit(daemon.run())
""")
    report['commitHoldFixture']={'path':str(backend_fixture),'sha256':sha(backend_fixture),'maximumSeconds':2,'scope':'Only delay transport before selection prepare; original effect path and six-second observation deadline unchanged.'}
   if NOTIFICATIONS:
    notification_arm=OUTPUT/'notification-hold-arm';notification_waiting=OUTPUT/'notification-hold-waiting';notification_release=OUTPUT/'notification-hold-release'
    backend_fixture=OUTPUT/'notification-backend.py'
    backend_fixture.write_text('import json,sys,time\nfrom pathlib import Path\nsys.path.insert(0,'+repr(str(ROOT/'adapter'))+')\nimport daemon\nsys.argv[1]='+repr(str(broker_config))+'\noriginal=daemon.handle_request\ndef handle(*args):\n request=args[2]\n arm=Path('+repr(str(notification_arm))+');waiting=Path('+repr(str(notification_waiting))+');release=Path('+repr(str(notification_release))+')\n if request.get("kind")=="notification-effect" and arm.exists():\n  arm.unlink();waiting.write_text(json.dumps(request));deadline=time.monotonic()+2\n  while not release.exists():\n   if time.monotonic()>=deadline:raise RuntimeError("Notification transport hold expired")\n   time.sleep(.005)\n  release.unlink()\n return original(*args)\ndaemon.handle_request=handle\nraise SystemExit(daemon.run())\n')
    report['notificationHoldFixture']={'path':str(backend_fixture),'sha256':sha(backend_fixture),'maximumSeconds':2,'scope':'Hold actual queued request before its unchanged admission route; no artificial effect or receipt.'}
   if FILES:
    installed_files=pathlib.Path('/home/hoskinson/.local/share/omarchy-files');private_home=pathlib.Path(env['HOME'])
    assert private_home.resolve().is_relative_to(s.host.runtime.resolve())
    for directory in ['Pictures','Documents','Downloads']:(private_home/directory).mkdir(mode=0o700,exist_ok=True)
    (private_home/'Documents/warlock-files-fixture.txt').write_text('Private Files navigation fixture')
    env.update(FILES_OPEN='home',FILES_WIDGET='0',FILES_DRYRUN='1',QT_QPA_PLATFORM='wayland',QT_QUICK_CONTROLS_STYLE='Basic')
    operation_hashes={str(path):sha(path) for path in [installed_files/'scripts/ops.sh',installed_files/'spec/fileops.qnt']}
    qml_hashes={str(path):sha(path) for path in installed_files.rglob('*') if path.is_file() and path.suffix in ['.qml','.js']}
    files_process=s.host.launch('installed-files',['/usr/bin/qs','-p',str(installed_files),'--no-duplicate'],env=env);apps.append(files_process)
    def files_ipc(method,*args):
     assert files_process.poll() is None
     raw=helper(['/usr/bin/qs','--log-rules','quickshell.bare.info=false','-p',str(installed_files),'ipc','--pid',str(files_process.pid),'call','files',method,*args])
     return json.loads(raw.strip()) if method in ['migrationStatus','uiState'] else raw
    wait(lambda:files_process.poll() is not None or any(w['label']=='Files' for w in client.snapshot('452')['windows']))
    check('ActualInstalledExplorerMapped',files_process.poll() is None,log=str(OUTPUT/'installed-files.log'))
    files_native_status=files_ipc('migrationStatus');files_original_ui=files_ipc('uiState')
    check('InstalledExplorerReadyInPrivateHome',files_native_status['ready'] and not files_native_status['error'] and files_original_ui['view']=='home' and files_original_ui['visible'],status=files_native_status,ui=files_original_ui)
    backend_fixture=OUTPUT/'files-backend.py'
    backend_fixture.write_text('import os,sys\nfrom pathlib import Path\nsys.path.insert(0,'+repr(str(ROOT/'adapter'))+')\nimport daemon\nfrom explorer import Explorer\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nassert not Path(os.environ["DBUS_SYSTEM_BUS_ADDRESS"].removeprefix("unix:path=")).exists()\nsys.argv[1]='+repr(str(broker_config))+'\ndaemon.Explorer=lambda:Explorer('+repr(str(installed_files))+')\nraise SystemExit(daemon.run())\n')
    report['filesFixture']={'backend':str(backend_fixture),'backendSHA256':sha(backend_fixture),'installedRoot':str(installed_files),'installedQmlSHA256':qml_hashes,'installedOperationSHA256':operation_hashes,'qsSHA256':sha('/usr/bin/qs'),'home':env['HOME'],'runtime':env['XDG_RUNTIME_DIR'],'wayland':env['WAYLAND_DISPLAY'],'systemBusRemainsRefusing':True,'scope':'Actual unmodified installed explorer; native-only root constructor selects existing installation in private home, no operation script/spec edits or invocation.'}
   if SYSTEM:
    import importlib.util
    system_spec=importlib.util.spec_from_file_location('private_system_fixture',ROOT/'qa/system-menu-provider.py');system_fixture=importlib.util.module_from_spec(system_spec);system_spec.loader.exec_module(system_fixture)
    audio_root=s.host.runtime/'system-audio';env=system_fixture.audio_config(audio_root,env)
    audio_core=s.host.launch('system-audio-core',['/usr/bin/pipewire','-c',str(audio_root/'core.conf')],env=env);apps.append(audio_core);wait(lambda:(audio_root/'warlock-audio').exists())
    audio_pulse=s.host.launch('system-audio-pulse',['/usr/bin/pipewire-pulse','-c',str(audio_root/'pulse.conf')],env=env);apps.append(audio_pulse);wait(lambda:(audio_root/'pulse/native').exists())
    system_state=OUTPUT/'system-state.json';system_provider=s.host.launch('system-login-provider',['/usr/bin/python3','-B',str(ROOT/'qa/system-menu-provider.py'),str(system_state)],env=env);apps.append(system_provider);wait(lambda:system_state.exists())
    backend_fixture=OUTPUT/'system-menu-backend.py'
    backend_fixture.write_text('import os,sys\nfrom pathlib import Path\nsys.path.insert(0,'+repr(str(ROOT/'adapter'))+')\nimport daemon\nfrom system_menu import Menu\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nassert not Path(os.environ["DBUS_SYSTEM_BUS_ADDRESS"].removeprefix("unix:path=")).exists()\nassert os.environ["PULSE_SERVER"]=='+repr(env['PULSE_SERVER'])+'\nsys.argv[1]='+repr(str(broker_config))+'\ndaemon.SystemMenu=lambda:Menu(system_address=os.environ["DBUS_SESSION_BUS_ADDRESS"])\nraise SystemExit(daemon.run())\n')
    report['systemFixture']={'backend':str(backend_fixture),'backendSHA256':sha(backend_fixture),'provider':str(ROOT/'qa/system-menu-provider.py'),'providerSHA256':sha(ROOT/'qa/system-menu-provider.py'),'audioCoreConfigSHA256':sha(audio_root/'core.conf'),'audioPulseConfigSHA256':sha(audio_root/'pulse.conf'),'audioEndpoint':env['PULSE_SERVER'],'systemBusRemainsRefusing':True,'privateSessionBus':env['DBUS_SESSION_BUS_ADDRESS'],'scope':'Native-only fixture constructor selects owned private login1 provider; unchanged production admission/effect path, real private null audio sink, network owner absent, no hardware/desktop system effect.'}
   web=s.host.launch('warlock',['%s'%binary,'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(backend_fixture if CATALOG or CHORD else ROOT/'adapter/daemon.py'),'--qa-exit-after-render','--qa-stay-open','--surface-experiment',*(['--text-scale','2' if DENSEMENU else '1.5'] if SMALL else [])],env=env);apps.append(web);log=OUTPUT/'warlock.log';collector=Collector()
   def text():
    raw=log.read_text(errors='replace')
    # The live file may end in a producer's unfinished JSON record. Observe
    # complete lines only; malformed completed records still fail normally.
    return raw[:raw.rfind('\n')+1]
   def projection():return collector.read(text())
   def group(operation):
    p=projection();return next((g for g in p['groups'] if (FOCUS or NAV or g['title']==('ELM-ACTIVATION-PEER' if PRIMARY else 'ELM-AUTHORITY-FIXTURE')) and g['label'].startswith(operation+' ') and not g['disabled']),None) if p and p['phase']=='Coherent' else None
   def journal():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']=='window-effect']
   def feedback(state):
    p=projection()
    if not p or p['transaction']!=state:return None
    rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=bar ')]
    return next((r for r in reversed(rows) if r['publication']==p['publication']),None)
   def click(item):
    check('PointerTargetWithinActualViewport',item['visible'],item=item);x,y=map(round,item['point']);helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
   def facts():return client.scene_facts('441')
   initial=None if TASKVIEW or SWITCHER or CHORD or FILES or JUMP or KEYBOARD or DRAG else wait(lambda:group('Activate' if PRIMARY else 'Choose a window from' if FOCUS else 'Minimize'))
   target=next(w['incarnation'] for w in client.snapshot('442')['windows'] if w['label']==('ELM-ACTIVATION-PEER' if PRIMARY else 'ELM-AUTHORITY-FIXTURE'))
   initial_workspace=next(w['workspace'] for w in facts()['facts']['windows'] if w['incarnation']==target)
   def current_window():return next(w for w in facts()['facts']['windows'] if w['incarnation']==target)
   def transaction_state():return (projection() or {}).get('transaction')
   def private_effect(operation,identity=None):
    before=facts();n=str((10000 if MEMBERSHIP else 9000)+len(report['nativeFixtures']));intent={'request':n,'generation':n,'incarnation':identity or target,'operation':operation,'context':client.context(before)};result=client.effect(intent);report['nativeFixtures'].append({'intent':intent,'result':result});check('ControlledNativeFixture'+operation,result['status']=='Committed',result=result)
   def screenshot(state):
    body=wait(lambda:feedback(state));o=body['feedback'];check(state+'VisibleCorrelatedMessage',o and o['width']>=180 and o['height']==48 and o['clip']=='none' and o['display']!='none' and o['accessibleName']==o['text'] and o['atomic']=='true' and o['live']=='polite',feedback=o)
    image=OUTPUT/(state+'.png');helper(['/usr/bin/grim',str(image)])
    import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));data=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();left,top=int(o['x'])+5,int(o['y'])+3;right,bottom=min(800,int(o['x']+o['width'])-3),min(48,int(o['y']+o['height'])-3)
    bright=sum(1 for y in range(top,bottom) for x in range(left,right) if all(data[y*stride+x*channels+i]>170 for i in range(3)))
    check(state+'NativeTaskbarHasTextPixels',pix.get_width()==800 and pix.get_height()==600 and bright>30,image=str(image),sha256=sha(image),brightPixels=bright,region=[left,top,right,bottom]);report.setdefault('feedback',{})[state]=body
   if DRAG:
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');report['keyboard']={'path':str(keyboard),'sha256':sha(keyboard)}
    wrapper=OUTPUT/'drag-input.py';wrapper.write_text('import os,stat,sys\nfd=os.open(sys.argv[1],os.O_RDONLY|os.O_NOFOLLOW)\nst=os.fstat(fd)\nassert stat.S_ISFIFO(st.st_mode) and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o600\nos.dup2(fd,0);os.close(fd)\nos.execv(sys.argv[2],sys.argv[2:])\n')
    fifo=OUTPUT/'drag-keyboard.fifo';os.mkfifo(fifo,0o600);chord_writer=os.open(fifo,os.O_RDWR|os.O_NOFOLLOW)
    chord_keyboard=s.host.launch('chord-keyboard',['/usr/bin/python3','-B',str(wrapper),str(fifo),str(keyboard)],env=s.env)
    pfifo=OUTPUT/'drag-pointer.fifo';os.mkfifo(pfifo,0o600);drag_writer=os.open(pfifo,os.O_RDWR|os.O_NOFOLLOW)
    drag_pointer=s.host.launch('drag-pointer',['/usr/bin/python3','-B',str(wrapper),str(pfifo),str(POINTER),'1600','600'],env=s.env)
    report['persistentInput']={'wrapper':str(wrapper),'sha256':sha(wrapper),'commands':[]};report['dragPointerCommands']=[]
    def physical(commands):
     assert chord_keyboard.poll() is None
     before=(OUTPUT/'chord-keyboard.log').read_text().splitlines().count('ready')
     raw=(commands+'\nsync\n').encode();assert len(raw)<=4096 and os.write(chord_writer,raw)==len(raw)
     report['persistentInput']['commands'].append(commands)
     wait(lambda:(OUTPUT/'chord-keyboard.log').read_text().splitlines().count('ready')>before)
    def pointer(commands):
     assert drag_pointer.poll() is None
     raw=(commands+'\n').encode();assert len(raw)<=4096 and os.write(drag_writer,raw)==len(raw)
     report['dragPointerCommands'].append(commands)
    def ownership():return client.pointer_ownership('470')
    def owned(state):
     value=ownership();return value if value['state']==state else None
    def root_window():return next(w for w in s.data('clients') if w['title']=='ELM-AUTHORITY-FIXTURE')
    def received_owner(state,serial):
     rows=[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind')=='pointer-ownership']
     return next((row for row in reversed(rows) if row['state']==state and row['serial']==serial),None)
    wait(lambda:(projection() or {}).get('phase')=='Coherent' and received_owner('idle',ownership()['serial']))
    report['gestures']=[]
    for name,button,modifier,points in [('MoveAcrossTaskbarAndOutput',272,125,[(200,580),(1000,350)]),('ResizeAcrossTaskbarAndOutput',273,56,[(1000,580),(700,550)])]:
     before=ownership();window_before=root_window();x,y=map(round,[window_before['at'][0]+window_before['size'][0]/2,window_before['at'][1]+window_before['size'][1]/2])
     check(name+'StartsIdle',before['state']=='idle')
     pointer(f'move {x} {y}\nsleep 100');physical(f'key {modifier} 1\nsleep 50');pointer(f'button {button} 1\nsleep 50\nmove {x+10} {y+10}\nsleep 100')
     state='move' if button==272 else 'resize';active=wait(lambda:owned(state));wait(lambda:received_owner(state,active['serial']))
     check(name+'NativeOwnerIsOriginalWindow',active['owner']==target and int(active['serial'])==int(before['serial'])+1,observation=active)
     crossings=[]
     for px,py in points:
      pointer(f'move {px} {py}\nsleep 100')
      wait(lambda:s.data('cursorpos')=={'x':px,'y':py})
      current=ownership();crossings.append({'point':[px,py],'owner':current,'projection':projection()})
      check(name+'CrossingRetainsNativeOwner',current['state']==state and current['owner']==target and current['serial']==active['serial'] and (projection() or {}).get('mode')=='closed',point=[px,py],observation=current)
     # Both adopted modifiers are exercised. Super or Alt is already held.
     other=56 if modifier==125 else 125
     physical(f'key {other} 1\nkey 57 1\nsleep 50\nkey 57 0\nkey {other} 0\nsleep 100')
     check(name+'AppsShortcutCannotStealGesture',ownership()==active and (projection() or {}).get('mode')=='closed',observation=ownership(),projection=projection())
     outcome=private_effect('minimize',target)
     check(name+'CompetingNativeEffectRefused',outcome['status']=='Refused' and outcome['reason']=='native-pointer-owned' and ownership()==active,result=outcome)
     pointer(f'button {button} 0\nsleep 100');ended=wait(lambda:owned('idle'));physical(f'key {modifier} 0\nsleep 100');wait(lambda:received_owner('idle',ended['serial']))
     check(name+'ExactlyOneNativeEnd',int(ended['serial'])==int(active['serial'])+1 and ended['owner'] is None and not current_window()['minimized'],before=before,active=active,end=ended)
     after=root_window();check(name+'NativeGeometryChanged',after['at']!=window_before['at'] if button==272 else after['size']!=window_before['size'],before=window_before,after=after)
     report['gestures'].append({'name':name,'before':before,'active':active,'crossings':crossings,'end':ended,'windowBefore':window_before,'windowAfter':after})
    physical('key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100')
    wait(lambda:(projection() or {}).get('mode')=='applications')
    check('FreshAppsShortcutWorksAfterNativeRelease',(projection() or {}).get('mode')=='applications')
    image=OUTPUT/'drag-two-output.png';helper(['/usr/bin/grim',str(image)]);report['dragPixels']={'path':str(image),'sha256':sha(image)}
    report['nativeDragOwnershipObserved']=True
   elif ATTENTION:
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');report['keyboard']={'path':str(keyboard),'sha256':sha(keyboard)}
    def bar_body():
     rows=[json.loads(line.split(' ',2)[2])['body'] for line in text().splitlines() if line.startswith('surface-report: origin=bar ')]
     body=rows[-1] if rows else None;p=projection()
     return body if body and p and p['phase']=='Coherent' and body['publication']==p['publication'] else None
    def attention_facts():return client.scene_facts('445',attention=True)
    def marker(label,state):
     body=bar_body()
     return next((b for b in body['buttons'] if b['accessibleName'].startswith(('Activate '+label+';','Minimize '+label+';')) and state in b['accessibleName']),None) if body else None
    before_native=attention_facts();before_window=len(journal());origin=before_native['facts']['focused'];before_member=sorted((w['incarnation'],w['workspace'],w['monitor']) for w in before_native['facts']['windows'])
    check('AttentionFixtureTargetIsInitiallyInactive',origin!=target and not next(w for w in before_native['facts']['windows'] if w['incarnation']==target)['attention'],facts=before_native)
    temp=peer_control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'request-attention'}));temp.replace(peer_control)
    observed=wait(lambda:(value:=attention_facts()) and next(w for w in value['facts']['windows'] if w['incarnation']==target)['attention'] and value)
    attention=wait(lambda:marker('ELM-ACTIVATION-PEER','Attention; Open'));active=wait(lambda:marker('ELM-AUTHORITY-FIXTURE','Active'))
    check('OriginalNativeAttentionDiffersFromActiveAccessibleState','Attention; Open' in attention['accessibleName'] and '; Active' in active['accessibleName'],attention=attention,active=active,facts=observed)
    check('NativeAttentionRequestDoesNotStealFocusOrSubmitWindowEffect',observed['facts']['focused']==origin and len(journal())==before_window)
    image=OUTPUT/'taskbar-native-attention.png';helper(['/usr/bin/grim',str(image)])
    import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels()
    def colors(button):
     left,top=max(0,int(button['x'])),max(0,int(button['y']));right,bottom=min(800,int(button['x']+button['width'])),min(48,int(button['y']+button['height']));amber=blue=0
     for y in range(top,bottom):
      for x in range(left,right):
       at=y*stride+x*channels;r,g,b=pixels[at:at+3];amber+=r>200 and g>140 and b<160;blue+=b>180 and g>160 and r<180
     return {'amberPixels':amber,'bluePixels':blue,'region':[left,top,right,bottom],'area':max(0,right-left)*max(0,bottom-top)}
    attention_pixels=colors(attention);active_pixels=colors(active)
    check('OriginalNativeAttentionAndActiveIndicatorsDifferInPixels',attention_pixels['amberPixels']>30 and active_pixels['bluePixels']>30 and attention_pixels['amberPixels']>active_pixels['amberPixels'],attention=attention_pixels,active=active_pixels,image=str(image),sha256=sha(image))
    report['nativeAttentionImage']={'path':str(image),'sha256':sha(image),'attention':attention,'active':active,'pixelCounts':{'attention':attention_pixels,'active':active_pixels}}
    check('NativeAttentionPreservesIdentityAndMembership',sorted((w['incarnation'],w['workspace'],w['monitor']) for w in observed['facts']['windows'])==before_member)
    check('AttentionTargetActualHitTargetIsVisible',attention['x']>=0 and attention['x']+attention['width']<=800 and attention['y']>=0 and attention['y']+attention['height']<=48,button=attention)
    click({'visible':True,'point':[attention['x']+attention['width']/2,attention['y']+attention['height']/2]})
    wait(lambda:attention_facts()['facts']['focused']==target)
    wait(lambda:marker('ELM-ACTIVATION-PEER','Active'))
    final=attention_facts();check('ActivatingAttentionTargetShowsObservedActiveAndClearsUrgency',not next(w for w in final['facts']['windows'] if w['incarnation']==target)['attention'] and len(journal())==before_window+1,facts=final,requests=journal()[before_window:])
    before_events=len(peer_control.with_suffix('.events.jsonl').read_text().splitlines());helper([str(keyboard)],'key 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n')
    delivered=[json.loads(line) for line in peer_control.with_suffix('.events.jsonl').read_text().splitlines()[before_events:]]
    check('ActivatedAttentionTargetReceivesActualKeyboardInput',any(e['kind']=='key' and e['keyval']==97 and e['window']=='ELM-ACTIVATION-PEER' for e in delivered),events=delivered)
    report['nativeAttentionFacts']={'before':before_native,'attention':observed,'afterActivation':final};report['nativeAttentionObserved']=True
   elif PRIMARY and not PINMENUS:
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');report['keyboard']={'path':str(keyboard),'sha256':sha(keyboard)}
    roots=client.snapshot('443')['windows'];companion=next(w['incarnation'] for w in roots if w['label']=='ELM-AUTHORITY-FIXTURE')
    check('DistinctSingleFamilyApplicationIdentities',len(roots)==2 and len({w['application'] for w in roots})==2,windows=roots)
    initial_membership=sorted((w['incarnation'],w['workspace'],w['monitor']) for w in facts()['facts']['windows'])
    check('NativeInactiveMemberBeforePrimary',facts()['facts']['focused']==companion and not current_window()['minimized'],nativeFacts=facts())
    def events():
     return {str(path):[json.loads(line) for line in path.read_text().splitlines()] if path.exists() else [] for path in [control.with_suffix('.events.jsonl'),peer_control.with_suffix('.events.jsonl')]}
    def actual_recipient(stage,identity):
     before={name:len(rows) for name,rows in events().items()};helper([str(keyboard)],'key 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n')
     delivered=[event for name,rows in events().items() for event in rows[before[name]:]];expected='ELM-ACTIVATION-PEER' if identity==target else 'ELM-AUTHORITY-FIXTURE'
     check(stage+'ActualKeyboardRecipient',facts()['facts']['focused']==identity and any(e['kind']=='key' and e['keyval']==97 and e['window']==expected for e in delivered),nativeFocus=facts()['facts']['focused'],events=delivered)
    def state_cue(minimized,focus):
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=bar ')]
     body=rows[-1] if rows else None;p=projection()
     if not body or not p or p['phase']!='Coherent' or body['publication']!=p['publication']:return None
     operation='Restore' if minimized else 'Minimize' if focus==target else 'Activate'
     button=next((b for b in body['buttons'] if b['accessibleName'].startswith(operation+' ELM-ACTIVATION-PEER;') and not b['disabled']),None)
     cue='Minimized' if minimized else 'Active' if focus==target else 'Open'
     return (body,button,cue) if button and cue in button['label'] else None
    def capture(stage,minimized):
     body,button,cue=wait(lambda:state_cue(minimized,facts()['facts']['focused']))
     check(stage+'AdmittedStateCueIsVisible',button['height']<=48 and button['width']>=112 and button['y']>=0 and button['y']+button['height']<=48,cue=cue,button=button)
     image=OUTPUT/(stage+'.png');helper(['/usr/bin/grim',str(image)])
     import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));data=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();x,y,width,height=map(int,current_window()['geometry']);left,top=max(0,x+10),max(100,y+10);right,bottom=min(800,x+width-10),min(600,y+height-10)
     green=sum(1 for py in range(top,bottom) for px in range(left,right) if data[py*stride+px*channels+1]>100 and data[py*stride+px*channels+1]>data[py*stride+px*channels]+30 and data[py*stride+px*channels+1]>data[py*stride+px*channels+2]+30)
     check(stage+'ActualWindowPresentation',green==0 if minimized else green>1000,greenPixels=green,region=[left,top,right,bottom],image=str(image),sha256=sha(image))
     left,top=max(0,int(button['x'])+5),max(0,int(button['y']+button['height']/2));right,bottom=min(800,int(button['x']+button['width'])-5),min(48,int(button['y']+button['height'])-3)
     bright=sum(1 for py in range(top,bottom) for px in range(left,right) if all(data[py*stride+px*channels+c]>170 for c in range(3)))
     check(stage+'ActualStateCueTextPixels',bright>15,brightPixels=bright,region=[left,top,right,bottom],cue=cue)
     report.setdefault('primaryCaptures',[]).append({'stage':stage,'path':str(image),'sha256':sha(image),'nativeFacts':facts(),'stateCue':cue,'barBody':body})
    def action(stage,operation,focus,minimized):
     button=wait(lambda:group(operation.title()));before=len(journal());click(button)
     wait(lambda:transaction_state()=='Committed' and current_window()['minimized']==minimized and facts()['facts']['focused']==focus)
     check(stage+'ExactlyOneBoundEffect',len(journal())==before+1 and journal()[-1]['intent']['incarnation']==target and journal()[-1]['intent']['operation']==operation,journal=journal()[before:])
     submitted=journal()[-1]
     def receipts():return [f for f in [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ')] if f.get('kind')=='effect-outcome' and f.get('binding')==submitted['binding'] and f.get('effectProtocol')==submitted['effectProtocol'] and f.get('intent')==submitted['intent']]
     rows=wait(receipts);check(stage+'NativeCommittedReceipt',len(rows)==1 and rows[0]['status']=='Committed',request=submitted,receipts=rows)
     report.setdefault('primaryReceipts',[]).append({'stage':stage,'request':submitted,'receipt':rows[0]})
     check(stage+'PreservesFamilyMembership',sorted((w['incarnation'],w['workspace'],w['monitor']) for w in facts()['facts']['windows'])==initial_membership)
     capture(stage,minimized)
     if focus is not None:actual_recipient(stage,focus)
    before_body,before_button,before_cue=wait(lambda:state_cue(False,companion));check('InactiveMemberHasOpenCue',before_cue=='Open',button=before_button)
    action('InactiveActivation','activate',target,False)
    action('ActiveMinimizeToMRU','minimize',companion,True)
    action('MinimizedRestore','restore',target,False)
    # Remove the only eligible successor through a separate owned fixture effect.
    private_effect('minimize',companion);check('OnlyMinimizedCompanionRemains',next(w for w in facts()['facts']['windows'] if w['incarnation']==companion)['minimized'])
    action('ActiveMinimizeToDesktop','minimize',None,True)
    before=[p.read_text().splitlines() if p.exists() else [] for p in [control.with_suffix('.events.jsonl'),peer_control.with_suffix('.events.jsonl')]]
    helper([str(keyboard)],'key 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n')
    after=[p.read_text().splitlines() if p.exists() else [] for p in [control.with_suffix('.events.jsonl'),peer_control.with_suffix('.events.jsonl')]]
    check('NoEligibleSuccessorDoesNotSendKeysToMinimizedFamily',facts()['facts']['focused'] is None and all(a==b for a,b in zip(before,after)),before=before,after=after)
    action('DesktopRestore','restore',target,False)
    launches=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']=='application-launch']
    check('OrdinaryPrimaryActionsNeverLaunchDuplicates',not launches and len(journal())==5,launchRequests=launches,windowRequests=len(journal()))
    report['nativePrimaryJourneyObserved']=True
   elif (CATALOG or TASKVIEW or SWITCHER or CHORD) and not DENSEPICKER:
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');report['keyboard']={'path':str(keyboard),'sha256':sha(keyboard)}
    def key(code):helper([str(keyboard)],f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100\nsync\n')
    def popup_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=popup ')]
     return rows[-1] if rows else None
    def field_value():
     body=popup_body();fields=body.get('fields',[]) if body else []
     return next((f['value'] for f in fields if f['id']=='launcher-search'),None)
    def launches():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']=='application-launch']
    def popup_capture(stage):
     import re
     rows=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l]
     box=tuple(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',rows[-1]).groups()))
     body=popup_body();image=OUTPUT/('popup-'+stage+'.png');helper(['/usr/bin/grim',str(image)])
     import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();regions=[]
     # Count only current control interiors. Whole-popup counts incorrectly
     # included the compositor's warning overlay above a black reopened popup.
     for button in body['buttons']+(body.get('content',[]) if NOTIFICATIONS or SYSTEM or FILES or JUMP else []):
      selected=button['id']==body['focus'] if SETTINGS else button['id']==body['focus'] if SNAP and (projection() or {}).get('mode')=='snap' else button['accessibleName'] in ['Minimize','Close window actions','Maximize'] if PINMENUS else button['accessibleName'].startswith(('Activate ELM-','Restore ELM-')) if SWITCHER or CHORD else (button['accessibleName'].startswith('Browse workspace ') or (NAV and button['accessibleName'].startswith('Restore ELM-ACTIVATION-PEER'))) if TASKVIEW else button['accessibleName'] in ['Refresh applications','Open Files']
      if KEYBOARD:selected=button['id']==body['focus']
      if JUMP:selected=button.get("identity","")=="jump:title:state" or button["id"]==body["focus"]
      if FILES:selected=button.get('identity','') in ['files:location:state','files:collection:images'] or button['id']==body['focus']
      if SYSTEM:selected=button.get('identity','').endswith(':state') or button['id']==body['focus']
      if NOTIFICATIONS:selected=button['accessibleName']=='Warlock fixture: Expiring notification'
      if not selected or (button['disabled'] and not (NOTIFICATIONS or SYSTEM or FILES or JUMP)) or button['y']<0 or button['y']+button['height']>box[3]:continue
      left,top=max(0,int(box[0]+button['x'])+12),max(100,int(box[1]+button['y'])+6)
      right,bottom=min(pix.get_width(),int(box[0]+button['x']+min(220,button['width']))-12),min(pix.get_height(),box[1]+box[3],int(box[1]+button['y']+button['height'])-6)
      bright=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>170 for c in range(3)))
      painted=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>15 for c in range(3)))
      regions.append({'accessibleName':button['accessibleName'],'brightPixels':bright,'paintedPixels':painted,'area':max(0,right-left)*max(0,bottom-top),'region':[left,top,right,bottom]})
     report.setdefault('popupCaptures',[]).append({'stage':stage,'path':str(image),'sha256':sha(image),'nativeBox':list(box),'controlRegions':regions,'body':body,'drawObservations':[l for l in text().splitlines() if l.startswith('popup-draw-observation:')][-3:]})

    def bar_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=bar ')]
     return rows[-1] if rows else None
    def requests(kind):return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']==kind]
    def query(codes,expected):
     wait(lambda:(popup_body() or {}).get('focus')=='launcher-search')
     helper([str(keyboard)],'key 29 1\nkey 30 1\nsleep 50\nkey 30 0\nkey 29 0\nkey 14 1\nkey 14 0\nsleep 100\nsync\n')
     for code in codes:key(code)
     wait(lambda:field_value()==expected)
    def keyboard_button(label,code=57):
     button=wait(lambda:next((b for b in (popup_body() or {}).get('buttons',[]) if b['accessibleName']==label and not b['disabled']),None))
     for _ in range(len(popup_body()['buttons'])+2):
      if popup_body()['focus']==button['id']:break
      key(15)
     check('KeyboardReaches'+label,popup_body()['focus']==button['id'],body=popup_body())
     key(code)
    if KEYBOARD:
     # A persistent real virtual keyboard keeps modifier ownership across
     # observations. Every key retains the original 50ms/100ms cadence.
     fifo=OUTPUT/'keyboard-shell.fifo';os.mkfifo(fifo,0o600);chord_writer=os.open(fifo,os.O_RDWR|os.O_NOFOLLOW)
     wrapper=OUTPUT/'keyboard-shell-input.py';wrapper.write_text('import os,stat,sys\nfd=os.open(sys.argv[1],os.O_RDONLY|os.O_NOFOLLOW)\nst=os.fstat(fd)\nassert stat.S_ISFIFO(st.st_mode) and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o600\nos.dup2(fd,0);os.close(fd)\nos.execv(sys.argv[2],[sys.argv[2]])\n')
     chord_keyboard=s.host.launch('chord-keyboard',['/usr/bin/python3','-B',str(wrapper),str(fifo),str(keyboard)],env=s.env)
     report['persistentInput']={'wrapper':str(wrapper),'sha256':sha(wrapper),'commands':[]}
     def physical(commands):
      assert chord_keyboard.poll() is None
      path=OUTPUT/'chord-keyboard.log';before=path.read_text().splitlines().count('ready')
      raw=(commands+'\nsync\n').encode();assert len(raw)<=4096 and os.write(chord_writer,raw)==len(raw)
      report['persistentInput']['commands'].append(commands);wait(lambda:path.read_text().splitlines().count('ready')>before)
     def key(code):physical(f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100')
     def chord(modifiers,code):physical(''.join(f'key {mod} 1\n' for mod in modifiers)+f'key {code} 1\nsleep 50\nkey {code} 0\n'+''.join(f'key {mod} 0\n' for mod in reversed(modifiers))+'sleep 100')
     def body_for(mode):
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')==mode and p['publication']==body['publication'] else None
     def closed():return (projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent'
     def frames(kind):return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind')==kind]
     def events():return [json.loads(line) for line in jump_events.read_text().splitlines()] if jump_events.exists() else []
     def open_apps():
      chord([125,56],57)
      return wait(lambda:(body:=body_for('applications')) and body['focus']=='launcher-search' and any(b['accessibleName']=='Actions for A Warlock Editor' and not b['disabled'] for b in body['buttons']) and body)
     def bar_focus():
      body=bar_body();p=projection()
      return body if body and body.get('documentFocused') and p and closed() and body['publication']==p['publication'] and any(b['id']==body['focus'] and not b['disabled'] for b in body['buttons']) else None
     def enter_bar():
      open_apps();key(1);return wait(bar_focus)
     def bar_route(label):
      enter_bar();key(102)
      button=wait(lambda:next((b for b in (bar_focus() or {}).get('buttons',[]) if b['accessibleName']==label and not b['disabled']),None))
      for _ in range(len(bar_body()['buttons'])+1):
       if (bar_focus() or {}).get('focus')==button['id']:break
       key(106)
      check('KeyboardBarRoute'+label,(bar_focus() or {}).get('focus')==button['id'],body=bar_body());key(28)
     def reached(name,details):report['keyboardSurfaces'].append({'surface':name,'passed':True,**details})
     # Establish the original attached, observed surface before user input.
     wait(lambda:closed() and bool(frames('shell-shortcuts')))
     # Launcher: current catalog query and one real GIO launch.
     open_apps();key(30);wait(lambda:field_value()=='a');before=len(launches());key(28)
     wait(lambda:closed() and len(events())==1 and len(frames('application-launch-outcome'))>0)
     check('KeyboardLauncherDispatchesOneNativeCatalogEntry',len(launches())==before+1 and events()[0]['argv']==['RECENT'],requests=launches(),events=events())
     reached('launcher',{'events':events(),'outcome':frames('application-launch-outcome')[-1]})
     # Jump lists: native declared action once, then keyboard dismissal.
     open_apps();keyboard_button('Actions for A Warlock Editor',28);wait(lambda:body_for('jump'))
     keyboard_button('New document',28);wait(lambda:closed() and len(events())==2)
     check('KeyboardJumpListDispatchesExactlyOnce',events()[-1]['argv']==['ALPHA'] and len(requests('jump-list-effect'))==1,events=events())
     open_apps();keyboard_button('Actions for A Warlock Editor',28);wait(lambda:body_for('jump'));key(1);wait(lambda:body_for('applications'));key(1);wait(closed)
     reached('jump-lists',{'events':events(),'dismissed':True})
     # Recorded Omarchy bindings enter notifications and the system menu.
     chord([125,42,56],51);wait(lambda:body_for('notifications'));before=len(requests('notification-request'))
     keyboard_button('Refresh notifications',28);wait(lambda:len(requests('notification-request'))==before+1 and len(frames('notification-snapshot'))>=2)
     key(1);wait(closed);reached('notifications',{'snapshots':len(frames('notification-snapshot')),'dismissed':True})
     chord([125],1);wait(lambda:body_for('system'));before=len(requests('system-menu-request'))
     keyboard_button('Refresh system state',28);wait(lambda:len(requests('system-menu-request'))==before+1 and len(frames('system-menu-snapshot'))>=2)
     key(1);wait(closed);reached('menus',{'systemSnapshots':len(frames('system-menu-snapshot')),'dismissed':True})
     # Settings: current native Saved receipt/readback without pointer entry.
     bar_route('Open settings');wait(lambda:body_for('settings'));keyboard_button('Dawn theme',28);keyboard_button('Save settings',28)
     saved=wait(lambda:next((f for f in frames('shell-settings-outcome') if f.get('status')=='Saved'),None))
     check('KeyboardSettingsNativeSaved',saved['snapshot']['values']=={'theme':'dawn','textScale':100},receipt=saved)
     wait(lambda:(body:=body_for('settings')) and body['theme']=='dawn' and 'Settings saved.' in body['text'] and ('surface-presentation-applied: publication='+body['publication']+' lease='+body['lease']) in text().splitlines())
     key(1);wait(closed);reached('settings',{'receipt':saved,'dismissed':True})
     # Taskbar groups: exact selected incarnation, committed activation and input.
     enter_bar();key(102);wait(lambda:(body:=bar_focus()) and any(b['id']==body['focus'] and b['identity'].startswith('bar:group:') for b in body['buttons']));key(28);picker=wait(lambda:(projection() or {}).get('picker'));wait(lambda:body_for('picker'))
     check('KeyboardGroupOpensWithoutDuplicateLaunch',len(picker['selections'])==2 and len(launches())==1,picker=picker)
     selected=next(row for row in picker['selections'] if row['title']=='ELM-ACTIVATION-PEER')
     label=next(b['accessibleName'] for b in popup_body()['buttons'] if 'ELM-ACTIVATION-PEER' in b['accessibleName'] and not b['disabled'])
     before=len(journal());keyboard_button(label,28);wait(lambda:closed() and len(journal())==before+1 and facts()['facts']['focused']==selected['incarnation'])
     event_path=control.with_suffix('.events.jsonl');before_input=len(event_path.read_text().splitlines());key(30)
     delivered=[json.loads(line) for line in event_path.read_text().splitlines()[before_input:]]
     check('KeyboardChosenGroupMemberReceivesInput',any(e['kind']=='key' and e['keyval']==97 and e['window']==selected['title'] for e in delivered),events=delivered)
     enter_bar();key(102);wait(lambda:(body:=bar_focus()) and any(b['id']==body['focus'] and b['identity'].startswith('bar:group:') for b in body['buttons']));key(28);wait(lambda:body_for('picker'));key(1);wait(closed)
     reached('taskbar-groups',{'selected':selected,'events':delivered,'dismissed':True})
     # Window menu and snap chooser: select a current native family with Shift-F10.
     enter_bar();key(102);wait(lambda:(body:=bar_focus()) and any(b['id']==body['focus'] and b['identity'].startswith('bar:group:') for b in body['buttons']));key(28);wait(lambda:body_for('picker'))
     button=next(b for b in popup_body()['buttons'] if 'ELM-AUTHORITY-FIXTURE' in b['accessibleName'] and not b['disabled'])
     for _ in range(len(popup_body()['buttons'])+2):
      if popup_body()['focus']==button['id']:break
      key(15)
     check('KeyboardMenuTargetIsCurrentFamily',popup_body()['focus']==button['id']);chord([42],68);wait(lambda:body_for('menu'))
     keyboard_button('Open snapping',28);wait(lambda:body_for('snap'))
     label=next(b['accessibleName'] for b in popup_body()['buttons'] if b['identity']=='snap:region:right-half');keyboard_button(label,28)
     before_geometry=current_window()['geometry'];keyboard_button('Snap to right half',28)
     receipt=wait(lambda:next((f for f in frames('effect-outcome') if f.get('status')=='Committed' and f.get('intent',{}).get('operation')=='snap'),None))
     wait(lambda:closed() and current_window()['geometry']!=before_geometry)
     check('KeyboardSnapHasNativeCommittedPlacement',receipt['intent']['incarnation']==target and current_window()['geometry']!=before_geometry,receipt=receipt,geometry=current_window()['geometry'])
     reached('snap-chooser',{'receipt':receipt,'geometry':current_window()['geometry'],'dismissed':True})
     # Task View: browse the observed workspace, activate its exact member, dismiss.
     bar_route('Open Task View');wait(lambda:body_for('overview'))
     workspace=next(b['accessibleName'] for b in popup_body()['buttons'] if b['accessibleName'].startswith('Browse workspace '));keyboard_button(workspace,28)
     label=next(b['accessibleName'] for b in popup_body()['buttons'] if 'ELM-ACTIVATION-PEER on workspace' in b['accessibleName'] and not b['disabled'])
     before=len(journal());keyboard_button(label,28);wait(lambda:closed() and len(journal())==before+1 and facts()['facts']['focused']==selected['incarnation'])
     bar_route('Open Task View');wait(lambda:body_for('overview'));key(1);wait(closed)
     reached('task-view',{'selected':selected,'dismissed':True})
     # Global Alt-Tab keeps Alt held through two actual native observations.
     before=len(journal());physical('key 56 1\nkey 15 1\nsleep 50\nkey 15 0\nsleep 100');wait(lambda:body_for('switcher'))
     first=next(b['identity'] for b in popup_body()['buttons'] if b['id']==popup_body()['focus'])
     key(15);wait(lambda:(body:=body_for('switcher')) and any(b['id']==body['focus'] and b['identity']!=first for b in body['buttons']))
     physical('key 56 0\nsleep 100');wait(lambda:closed() and len(journal())==before+1)
     physical('key 56 1\nkey 15 1\nsleep 50\nkey 15 0\nsleep 100');wait(lambda:body_for('switcher'));key(1);physical('key 56 0\nsleep 100');wait(closed)
     reached('switcher',{'request':journal()[-1],'dismissed':True})
     open_apps();popup_capture('keyboard-shell-finished');key(1);wait(closed)
     pointer_events=[json.loads(line) for line in event_path.read_text().splitlines() if json.loads(line)['kind'] in ['pressed','released']]
     check('OriginalJourneyUsesZeroInjectedPointerEvents',not pointer_events and not any(str(POINTER) in row['command'] for row in report['helpers']),events=pointer_events)
     report['pointerEventsInjected']=0
     check('OriginalAllNineKeyboardSurfacesCompleted',len(report['keyboardSurfaces'])==9 and {row['surface'] for row in report['keyboardSurfaces']}=={'launcher','taskbar-groups','switcher','task-view','snap-chooser','menus','settings','notifications','jump-lists'},surfaces=report['keyboardSurfaces'])
     report['nativeKeyboardShellObserved']=True
    elif DENSE:
     def dense_body():
      body=bar_body();p=projection()
      return body if body and p and p['phase']=='Coherent' and p['mode']=='closed' and body['publication']==p['publication'] and len([b for b in body['buttons'] if b.get('identity','').startswith('bar:pin:')])==len(dense_ids) else None
     def dense_pin(identity):
      body=dense_body()
      return next((b for b in body['buttons'] if b.get('identity')=='bar:pin:'+identity and not b['disabled']),None) if body else None
     def visible(button,body):
      box=body['actions']
      return button and button['x']>=box['x']-.5 and button['x']+button['width']<=box['x']+box['width']+.5 and button['y']>=box['y']-.5 and button['y']+button['height']<=box['y']+box['height']+.5
     def selected(identity):
      button=dense_pin(identity);body=dense_body()
      return body if button and body['focus']==button['id'] and visible(button,body) else None
     def order(body):return [b['identity'][len('bar:pin:'):] for b in body['buttons'] if b.get('identity','').startswith('bar:pin:')]
     def dense_capture(stage):
      image=OUTPUT/(stage+'.png');helper(['/usr/bin/grim',str(image)])
      import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
      pix=GdkPixbuf.Pixbuf.new_from_file(str(image));check(stage+'ActualOutputPixels',pix.get_width()==dense_body()['viewportWidth'] and pix.get_height()==600)
      report.setdefault('denseCaptures',[]).append({'stage':stage,'path':str(image),'sha256':sha(image),'body':dense_body()})
     def dense_menu():
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')=='menu' and body['publication']==p['publication'] and any(b['accessibleName']=='Minimize' and not b['disabled'] for b in body['buttons']) else None
     before=len(journal());body=wait(dense_body)
     check('NativeDenseFixtureUsesSmallOutputAndEnlargedText',body['fontSize']=='24px' and body['viewportWidth']==480 and body['actions']['height']==72 and body['scrollWidth']>body['clientWidth'],body=body)
     check('NativeConfiguredPinOrderIsRendered',order(body)==dense_ids,body=body)
     for _ in range(12):
      body=dense_body();button=dense_pin(dense_ids[0]);box=body['actions']
      # Pointer opening needs a visible hit region. Complete selection reveal
      # is asserted after Escape, when this control actually receives focus.
      if button['x']+button['width']>box['x']+8 and button['x']<box['x']+box['width']-8:break
      delta=-120 if button['x']<box['x'] else 120
      helper([str(POINTER),'480','600'],f'move {round(box["x"]+box["width"]/2)} 30\nwheel {delta} 0\nsleep 100\n')
     body=dense_body();button=dense_pin(dense_ids[0]);box=body['actions']
     check('NativeWheelMakesFirstConfiguredPinReachable',button['x']+button['width']>box['x']+8 and button['x']<box['x']+box['width']-8,body=body)
     x=round((max(button['x'],box['x'])+min(button['x']+button['width'],box['x']+box['width']))/2);y=round(button['y']+button['height']/2)
     check('FirstDensePinSecondaryClickUsesVisibleIntersection',box['x']<=x<box['x']+box['width'] and 0<=y<72,button=button)
     helper([str(POINTER),'480','600'],f'move {x} {y}\nsleep 100\nbutton 273 1\nsleep 50\nbutton 273 0\nsleep 100\n')
     wait(dense_menu);popup_capture('dense-first-menu')
     check('DenseFirstPinMenuLabelsHaveNativePixels',bool(report['popupCaptures'][-1]['controlRegions']) and all(r['brightPixels']>15 for r in report['popupCaptures'][-1]['controlRegions']))
     key(1);wait(lambda:selected(dense_ids[0]));check('DenseMenuEscapeRevealsFirstPin',bool(selected(dense_ids[0])))
     key(107);wait(lambda:selected(dense_ids[-1]));check('NativeEndRevealsLastPin',bool(selected(dense_ids[-1])));dense_capture('dense-last')
     key(102);wait(lambda:(dense_body() or {}).get('focus')==(dense_body() or {}).get('buttons',[{}])[0].get('id'))
     visited=[]
     for identity in dense_ids:
      for _ in range(len(dense_body()['buttons'])+1):
       if selected(identity):break
       key(106)
      body=wait(lambda:selected(identity));visited.append(identity)
      check('NativeKeyboardReachesConfiguredPin'+identity,visible(dense_pin(identity),body) and order(body)==dense_ids and bool(dense_pin(identity)['accessibleName']))
     report['keyboardVisitedPins']=visited
     proofs=sum('surface-context-admitted:' in l and 'origin=bar trigger=keyboard' in l for l in text().splitlines())
     key(127);wait(dense_menu);check('DenseLastPinMenuKeyUsesCurrentNativeProof',sum('surface-context-admitted:' in l and 'origin=bar trigger=keyboard' in l for l in text().splitlines())==proofs+1)
     key(1);wait(lambda:selected(dense_ids[-1]))
     helper([str(keyboard)],'key 42 1\nkey 68 1\nsleep 50\nkey 68 0\nkey 42 0\nsleep 100\nsync\n');wait(dense_menu);popup_capture('dense-last-menu');key(1);wait(lambda:selected(dense_ids[-1]))
     check('DenseMenusAndNavigationHaveNoWindowEffectsOrLaunches',len(journal())==before and not launches())
     helper([str(POINTER),'480','600'],'move 200 30\nwheel -30000 0\nsleep 100\n')
     wait(lambda:(dense_body() or {}).get('scrollLeft')==0);check('NativeVerticalWheelReachesBeginning',dense_body()['scrollLeft']==0)
     key(107);wait(lambda:selected(dense_ids[-1]))
     for width in [640,480]:
      result=s.ctl('eval','hl.monitor({output="WAYLAND-1",mode="'+str(width)+'x600@60",position="0x0",scale=1})')
      check('NativeOutputResizeCommand'+str(width),result.strip()=='ok',result=result)
      wait(lambda:any(m['name']=='WAYLAND-1' and m['width']==width and m['height']==600 for m in s.data('monitors')))
      wait(lambda:(dense_body() or {}).get('viewportWidth')==width and selected(dense_ids[-1]))
      body=dense_body();check('NativeResize'+str(width)+'PreservesOrderAndRevealsSelection',order(body)==dense_ids and visible(dense_pin(dense_ids[-1]),body),body=body)
      dense_capture('dense-resize-'+str(width))
      admitted=sum('surface-context-admitted:' in l for l in text().splitlines())
      if width==480:
       helper([str(keyboard)],'key 127 1\nsleep 100\nkey 127 1\nsleep 50\nkey 127 0\nsleep 100\nsync\n')
      else:key(127)
      wait(dense_menu)
      check('NativeMenuAfterResize'+str(width)+'AdmitsOnlyOneFreshKey',sum('surface-context-admitted:' in l for l in text().splitlines())==admitted+1 and len(journal())==before and not launches())
      key(1);wait(lambda:selected(dense_ids[-1]))
     check('DenseResizeKeepsConfiguredIdentityFile',configured.read()['identities']==dense_ids and sha(configured.path/'taskbar.json')==report['configuredDensePins']['sha256'])
     check('DenseJourneyDoesNotActivateOrLaunch',len(journal())==before and not launches())
     report['nativeDenseTaskbarObserved']=True
    elif PINMENUS:
     click(wait(lambda:projection().get('openApplications') if projection() else None))
     wait(lambda:field_value()=='');query([25,18,18,19],'peer');keyboard_button('Pin Peer')
     wait(lambda:any(button['label'].startswith('Peer') and 'Pinned;' in button['label'] for button in (bar_body() or {}).get('buttons',[])))
     keyboard_button('Close applications and return to windows');wait(lambda:(projection() or {}).get('mode')=='closed' and projection()['phase']=='Coherent')
     def pin_button():return next((button for button in (bar_body() or {}).get('buttons',[]) if button['label'].startswith('Peer') and 'Pinned;' in button['label'] and not button['disabled']),None)
     def menu():
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')=='menu' and body['publication']==p['publication'] and any(button['accessibleName']=='Minimize' for button in body['buttons']) else None
     before=len(journal());button=wait(pin_button);report['runningPin']=button
     x,y=round(button['x']+button['width']/2),round(button['y']+button['height']/2)
     check('RunningPinPointerTargetWithinBar',0<=x<800 and 0<=y<48,button=button)
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 273 1\nsleep 50\nbutton 273 0\nsleep 100\n')
     body=wait(menu);check('PinnedSecondaryClickOpensLabeledWindowMenu',len(journal())==before and any(button['accessibleName']=='Minimize' for button in body['buttons']),body=body)
     popup_capture('pinned-window-menu');check('NativeMenuControlsHaveTextPixels',bool(report['popupCaptures'][-1]['controlRegions']) and all(region['brightPixels']>15 for region in report['popupCaptures'][-1]['controlRegions']))
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed');wait(lambda:(bar_body() or {}).get('focus')==(pin_button() or {}).get('id'))
     check('MenuEscapeReturnsRunningPinFocus',bar_body()['focus']==pin_button()['id'])
     key(127);wait(menu);check('PinnedMenuKeyUsesNativeBarProof',any('surface-context-admitted:' in line and 'origin=bar trigger=keyboard' in line for line in text().splitlines()))
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed');wait(lambda:(bar_body() or {}).get('focus')==(pin_button() or {}).get('id'))
     helper([str(keyboard)],'key 42 1\nkey 68 1\nsleep 50\nkey 68 0\nkey 42 0\nsleep 100\nsync\n');wait(menu)
     check('PinnedShiftF10DoesNotActivateOrLaunch',len(journal())==before and not launches())
     def selected_action():
      body=menu()
      return next((button['accessibleName'] for button in body['buttons'] if button['id']==body['focus']),None) if body else None
     key(108);wait(lambda:selected_action()=='Maximize');key(103);wait(lambda:selected_action()=='Minimize')
     check('NativeMenuArrowTraversalReturnsToMinimize',selected_action()=='Minimize' and len(journal())==before)
     for _ in range(12):
      body=menu();focused=next((button for button in body['buttons'] if button['id']==body['focus']),None)
      if focused and focused['accessibleName']=='Minimize':break
      key(108)
     check('KeyboardSelectsLabeledMinimize',next(button for button in menu()['buttons'] if button['id']==menu()['focus'])['accessibleName']=='Minimize')
     prior_focus=facts()['facts']['focused'];key(28);wait(lambda:current_window()['minimized'] and len(journal())==before+1 and transaction_state()=='Committed')
     check('PinnedMenuMinimizesExactlyOnce',journal()[-1]['intent']['incarnation']==target and journal()[-1]['intent']['operation']=='minimize',request=journal()[-1])
     check('InactiveMenuMinimizePreservesExistingFocus',prior_focus!=target and facts()['facts']['focused']==prior_focus,priorFocus=prior_focus)
     wait(lambda:(bar_body() or {}).get('focus')==(pin_button() or {}).get('id'))
     # The inactive-family oracle preserves its real bar recipient; it must
     # not fabricate activation of another application after minimizing it.
     proofs=sum('surface-context-admitted:' in line and 'origin=bar trigger=keyboard' in line for line in text().splitlines());key(127);wait(menu)
     check('InactiveMinimizeRetainsNativeBarKeyboard',sum('surface-context-admitted:' in line and 'origin=bar trigger=keyboard' in line for line in text().splitlines())==proofs+1 and len(journal())==before+1)
     check('MinimizedPinExposesCurrentRestoreAction',any(button['accessibleName']=='Restore' and not button['disabled'] for button in menu()['buttons']))
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed');wait(lambda:(bar_body() or {}).get('focus')==(pin_button() or {}).get('id'))
     button=wait(pin_button);x,y=round(button['x']+button['width']/2),round(button['y']+button['height']/2);helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n');wait(lambda:not current_window()['minimized'] and facts()['facts']['focused']==target and len(journal())==before+2 and transaction_state()=='Committed')
     check('RunningPinRestoresWithoutDuplicateLaunch',journal()[-1]['intent']['operation']=='restore' and not launches())
     events=peer_control.with_suffix('.events.jsonl');n=len(events.read_text().splitlines()) if events.exists() else 0;key(30)
     delivered=wait(lambda:[json.loads(line) for line in events.read_text().splitlines()[n:]] if events.exists() else None)
     check('RestoredPinReceivesActualApplicationTyping',any(row['window']=='ELM-ACTIVATION-PEER' and row['kind']=='key' and row['keyval']==97 for row in delivered),events=delivered)
     # Switching from an on-demand menu parent to Task View must retain its
     # ordinary application dismissal policy, with a real GTK recipient.
     button=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Task View' and not b['disabled']),None));x,y=round(button['x']+button['width']/2),round(button['y']+button['height']/2)
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n');wait(lambda:(projection() or {}).get('mode')=='overview' and popup_body())
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed' and projection()['phase']=='Coherent')
     n=len(events.read_text().splitlines());key(30);delivered=wait(lambda:[json.loads(line) for line in events.read_text().splitlines()[n:]])
     check('TaskViewAfterMenuReturnsApplicationKeyboard',facts()['facts']['focused']==target and any(row['window']=='ELM-ACTIVATION-PEER' and row['kind']=='key' and row['keyval']==97 for row in delivered),events=delivered)
     report['nativePinnedMenusObserved']=True
     if SNAP:
      before=len(journal());before_launches=len(launches())
      button=wait(pin_button);x,y=round(button['x']+button['width']/2),round(button['y']+button['height']/2)
      helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 273 1\nsleep 50\nbutton 273 0\nsleep 100\n');wait(menu)
      keyboard_button('Open snapping',28)
      def snap_body():
       body=popup_body();p=projection()
       return body if body and p and p.get('mode')=='snap' and body['publication']==p['publication'] and len([b for b in body['buttons'] if b.get('identity','').startswith('snap:region:')])==6 else None
      body=wait(snap_body);check('NativeSnapChooserHasSixRegions',len([b for b in body['buttons'] if b.get('identity','').startswith('snap:region:')])==6,body=body)
      keyboard_button('Right half');body=wait(lambda:next((b for b in [snap_body()] if b and any(row['accessibleName']=='Right half; selected preview' for row in b['buttons'])),None))
      check('NativeRegionSelectionHasNoWindowEffect',len(journal())==before and len(launches())==before_launches,body=body)
      check('NativeNegotiatedSnapPlacementAvailable',any(b['identity']=='snap:apply' and not b['disabled'] for b in body['buttons']),body=body)
      popup_capture('native-snap-chooser');capture=report['popupCaptures'][-1]
      check('NativeSnapSelectedControlHasActualTextPixels',len(capture['controlRegions'])==1 and capture['controlRegions'][0]['accessibleName']=='Right half; selected preview' and all(r['area']>0 and r['brightPixels']>15 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
      def focused_snap(identity):
       body=snap_body();button=next((b for b in (body or {}).get('buttons',[]) if b.get('identity')==identity),None)
       return body if button and button['id']==body['focus'] and button['y']>=-.5 and button['y']+button['height']<=body['viewportHeight']+.5 else None
      key(107);wait(lambda:focused_snap('snap:apply'));key(103);body=wait(lambda:focused_snap('snap:region:bottom-right'));popup_capture('native-snap-last-region');capture=report['popupCaptures'][-1]
      check('NativeSnapEndReachesApplyAndArrowRevealsLastRegion',len(capture['controlRegions'])==1 and capture['controlRegions'][0]['accessibleName']=='Bottom right quarter' and all(r['area']>0 and r['brightPixels']>15 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),body=body,capture=capture)
      key(102);wait(lambda:focused_snap('control:close'));check('NativeSnapHomeReturnsToVisibleClose',len(journal())==before and len(launches())==before_launches,body=snap_body())
      if PLACEMENT:
       keyboard_button('Left half');wait(lambda:any(b['accessibleName']=='Left half; selected preview' for b in (snap_body() or {}).get('buttons',[])))
       old=client.geometry_facts('16001');row=next(w for w in old['facts']['windows'] if w['incarnation']==target);area=row['workArea'];expected=[area[0],area[1],area[2]/2,area[3]]
       original_membership=sorted((w['incarnation'],w['workspace'],w['monitor']) for w in facts()['facts']['windows'])
       original_focus=facts()['facts']['focused'];keyboard_button('Snap to left half')
       wait(lambda:(projection() or {}).get('mode')=='closed' and len(journal())==before+1 and transaction_state()=='Committed')
       request=journal()[-1];check('NativeSnapSubmitsOneExactGenerationBoundPlacement',request['effectProtocol']==2 and request['intent']['operation']=='snap' and request['intent']['incarnation']==target and request['intent']['placement']['geometry']==expected and request['intent']['placement']['outputOwnershipGeneration']==row['outputOwnershipGeneration'] and request['intent']['placement']['workAreaRevision']==row['workAreaRevision'] and request['intent']['placement']['workspaceGeneration']==row['workspaceGeneration'],request=request,observed=row)
       actual=client.geometry_facts('16002');placed=next(w for w in actual['facts']['windows'] if w['incarnation']==target)
       check('OriginalUX019AcceptedHalfWorkAreaWithinRounding',all(abs(a-b)<=1 for a,b in zip(placed['logicalGeometry'],expected)) and placed['nativeMode']=='ordinary' and placed['clientMode']=='ordinary',expected=expected,actual=placed)
       check('NativeSnapPreservesMembershipAndFocus',original_membership==sorted((w['incarnation'],w['workspace'],w['monitor']) for w in facts()['facts']['windows']) and facts()['facts']['focused']==original_focus)
       receipts=[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind')=='effect-outcome']
       correlated=[r for r in receipts if r.get('binding')==request['binding'] and r.get('intent')==request['intent'] and r.get('effectProtocol')==2]
       check('NativeSnapHasOneCorrelatedCommittedReceipt',len(correlated)==1 and correlated[0]['status']=='Committed',request=request,receipts=correlated)
       report['nativeSnapReceipt']={'request':request,'receipt':correlated[0],'before':old,'after':actual}
       image=OUTPUT/'native-left-half-placement.png';helper(['/usr/bin/grim',str(image)])
       import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
       pix=GdkPixbuf.Pixbuf.new_from_file(str(image));data=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();x,y,width,height=placed['logicalGeometry'];left,top=max(0,int(x+10)),max(80,int(y+10));right,bottom=min(800,int(x+width-10)),min(600,int(y+height-10))
       green=sum(1 for py in range(top,bottom) for px in range(left,right) if data[py*stride+px*channels+1]>100 and data[py*stride+px*channels+1]>data[py*stride+px*channels]+30 and data[py*stride+px*channels+1]>data[py*stride+px*channels+2]+30)
       check('NativeAcceptedSnapHasActualWindowPixels',green>1000,image=str(image),sha256=sha(image),region=[left,top,right,bottom],greenPixels=green)
       report['nativeSnapCapture']={'path':str(image),'sha256':sha(image),'expected':expected,'actual':placed,'greenPixels':green}
       # Reopen the same target's real chooser, then retain its exact observed
       # placement scope for a stale native request after the scale change.
       before=len(journal());button=wait(pin_button);x,y=round(button['x']+button['width']/2),round(button['y']+button['height']/2)
       helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 273 1\nsleep 50\nbutton 273 0\nsleep 100\n');wait(menu);keyboard_button('Open snapping',28);wait(snap_body)
       stale=client.geometry_facts('16003');stale_row=next(w for w in stale['facts']['windows'] if w['incarnation']==target);wa=stale_row['workArea']
       stale_intent={'request':'20000','generation':'20000','incarnation':target,'operation':'snap','context':{'lifetime':client.bound['lifetime'],'epoch':client.bound['frontend'],'output':stale['outputGeneration'],'revision':stale['revision']},'placement':{'region':'left-half','geometry':[wa[0],wa[1],wa[2]/2,wa[3]],'monitor':stale_row['monitor'],'outputOwnershipGeneration':stale_row['outputOwnershipGeneration'],'workAreaRevision':stale_row['workAreaRevision'],'workspaceGeneration':stale_row['workspaceGeneration']}}
      result=s.ctl('eval','hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1.25})');check('NativeSnapOutputScaleCommand',result.strip()=='ok',result=result)
      wait(lambda:any(m['name']=='WAYLAND-1' and m['scale']==1.25 for m in s.data('monitors')))
      wait(lambda:(projection() or {}).get('mode')=='closed')
      check('NativeOutputScaleRetiresSnapWithoutCommit',len(journal())==before and len(launches())==before_launches,projection=projection(),monitors=s.data('monitors'))
      if PLACEMENT:
       after_scale=client.geometry_facts('16004');before_refusal=next(w for w in after_scale['facts']['windows'] if w['incarnation']==target)
       receipt=client.geometry_effect(stale_intent);after_refusal=client.geometry_facts('16005');final=next(w for w in after_refusal['facts']['windows'] if w['incarnation']==target)
       check('OriginalUX020OldOutputGeometryNeverCommits',receipt['status']=='Refused' and receipt['reason']=='dependency-mismatch' and final['logicalGeometry']==before_refusal['logicalGeometry'] and len(journal())==before,receipt=receipt,before=before_refusal,after=final)
       report['nativeSnapStaleRefusal']={'intent':stale_intent,'receipt':receipt,'before':after_scale,'after':after_refusal};report['nativeSnapPlacementObserved']=True
      report['nativeSnapChooserObserved']=True

    elif CHORD:
     def coherent_closed():return (projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent'
     def native_journal():return client.switcher_journal('450',observe=True)['chord']
     def selected_window(label):
      body=popup_body();p=projection()
      if not body or not p or p.get('mode')!='switcher' or body['publication']!=p['publication']:return None
      chosen=next((button for button in body['buttons'] if button['accessibleName'].endswith(label+'; selected') and not button['disabled']),None)
      ack='surface-presentation-applied: publication='+body['publication']+' lease='+body['lease']
      return body if chosen and body['focus']==chosen['id'] and ack in text().splitlines() else None
     def chord_start(reverse=False):physical('key 56 1\n'+('key 42 1\n' if reverse else '')+'key 15 1\nsleep 50\nkey 15 0\n'+('key 42 0\n' if reverse else '')+'sleep 100')
     def chord_step(reverse=False):physical(('key 42 1\n' if reverse else '')+'key 15 1\nsleep 50\nkey 15 0\n'+('key 42 0\n' if reverse else '')+'sleep 100')
     def release_alt():physical('key 56 0\nsleep 100')
     def escape():physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100')
     def receipt(stage,count,identity,status='Committed'):
      wait(coherent_closed);wait(lambda:len(journal())==count+1)
      request=journal()[-1]
      def receipts():
       frames=[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ')]
       return [row for row in frames if row.get('kind')=='effect-outcome' and row.get('binding')==request['binding'] and row.get('intent')==request['intent']]
      rows=wait(receipts)
      check(stage+'ExactlyOneNativeReceipt',len(rows)==1 and rows[0]['status']==status and request['intent']['incarnation']==identity and request['intent']['operation'] in ['activate','restore'],request=request,receipts=rows)
      report.setdefault('chordReceipts',[]).append({'stage':stage,'request':request,'receipt':rows[0]})
     def recipient(stage,identity,label):
      events=control.with_suffix('.events.jsonl');before=len(events.read_text().splitlines()) if events.exists() else 0
      physical('key 30 1\nsleep 50\nkey 30 0\nsleep 100')
      delivered=[json.loads(line) for line in events.read_text().splitlines()[before:]] if events.exists() else []
      check(stage+'RealKeyboardRecipient',facts()['facts']['focused']==identity and any(row['kind']=='key' and row['keyval']==97 and row['window']==label for row in delivered),focus=facts()['facts']['focused'],events=delivered)
     if MEMBERSHIP:
      receipt('StartupFrozenSteps',0,a);recipient('StartupFrozenSteps',a,'ELM-AUTHORITY-FIXTURE')
      check('StartupRetiredPeerAndArrivalDoNotRenumberBufferedSteps',b not in [row['incarnation'] for row in facts()['facts']['windows']] and journal()[-1]['intent']['incarnation']==a)
      fixture_control('arrive-peer');b=wait(lambda:next((row['incarnation'] for row in client.snapshot('450')['windows'] if row['label']=='ELM-ACTIVATION-PEER'),None))
      fixture_control('add-modal');modal=wait(lambda:next((row['incarnation'] for row in client.snapshot('450')['windows'] if row['label']=='SCENE-MODAL'),None))
      wait(lambda:any(row['incarnation']==modal and row['owner']==a for row in facts()['facts']['windows']))
      native_focus(c);private_effect('minimize',b)
      peer=next(row for row in s.data('clients') if row['title']=='ELM-ACTIVATION-PEER')
      check('MinimizedPeerMovesToWorkspaceTwo',s.ctl('dispatch',"hl.dsp.window.move({workspace=2,follow=false,window='address:"+peer['address']+"'})").strip()=='ok')
      wait(lambda:any(row['incarnation']==b and row['workspace']=='2' and row['minimized'] for row in facts()['facts']['windows']))
      membership=sorted((row['incarnation'],row['workspace'],row['monitor']) for row in facts()['facts']['windows'])
      report['membershipBeforeChoice']=facts();before=len(journal());chord_start();body=wait(lambda:selected_window('ELM-AUTHORITY-FIXTURE'))
      labels=[row['accessibleName'].split(';',1)[0] for row in body['buttons'] if row['accessibleName'].startswith(('Activate ELM-','Restore ELM-'))]
      check('ModalFamilyAndAllOrdinaryWorkspaceRootsEnumeratedOnce',len(labels)==4 and len(set(labels))==4 and modal not in native_journal()['roots'] and b in native_journal()['roots'] and any(label=='Restore ELM-ACTIVATION-PEER' for label in labels),body=body,journal=native_journal())
      popup_capture('modal-all-workspaces');release_alt();receipt('ModalFamilyActivation',before,a);recipient('ModalFamilyActivation',modal,'SCENE-MODAL')
      check('ModalActivationPreservesNativeMembership',membership==sorted((row['incarnation'],row['workspace'],row['monitor']) for row in facts()['facts']['windows']))
      before=len(journal());chord_start();wait(lambda:(projection() or {}).get('mode')=='switcher')
      for _ in range(4):
       if selected_window('ELM-ACTIVATION-PEER'):break
       chord_step()
      wait(lambda:selected_window('ELM-ACTIVATION-PEER'));release_alt();receipt('OtherWorkspaceMinimizedRestore',before,b);recipient('OtherWorkspaceMinimizedRestore',b,'ELM-ACTIVATION-PEER')
      check('OtherWorkspaceRestorePreservesMembershipAndUsesRestore',membership==sorted((row['incarnation'],row['workspace'],row['monitor']) for row in facts()['facts']['windows']) and journal()[-1]['intent']['operation']=='restore' and s.data('monitors')[0]['activeWorkspace']['id']==2)
      excluded=next(row for row in s.data('clients') if row['title']=='ELM-CHORD-THIRD')
      check('FixtureMovesOnlyThirdToSpecialWorkspace',s.ctl('dispatch',"hl.dsp.window.move({workspace='special:warlock-excluded',follow=false,window='address:"+excluded['address']+"'})").strip()=='ok')
      wait(lambda:any(row['incarnation']==c and int(row['workspace'])<0 for row in facts()['facts']['windows']))
      before=len(journal());chord_start();body=wait(lambda:next((body for body in [popup_body()] if body and (projection() or {}).get('mode')=='switcher' and body['publication']==projection()['publication'] and all('ELM-CHORD-THIRD' not in row['accessibleName'] for row in body['buttons'])),None))
      check('SpecialWorkspaceExcludedFromSwitcher',c not in native_journal()['roots'] and all('ELM-CHORD-THIRD' not in row['accessibleName'] for row in body['buttons']),body=body,journal=native_journal())
      excluded_membership=sorted((row['incarnation'],row['workspace'],row['monitor']) for row in facts()['facts']['windows'])
      escape();release_alt();wait(coherent_closed);check('ExclusionBrowseCancelHasNoWindowEffect',len(journal())==before)
      check('ExclusionBrowseCancelPreservesMembership',excluded_membership==sorted((row['incarnation'],row['workspace'],row['monitor']) for row in facts()['facts']['windows']))
      report['membershipAfterChoice']=facts();check('MembershipJourneyNeverLaunchesApplications',not launches());report['nativeMembershipJourneyObserved']=True
     else:
      receipt('StartupRelease',0,b);check('StartupOneResolutionAndNoOpenSwitcher',len(journal())==1 and native_journal()['consumed']);recipient('StartupRelease',b,'ELM-ACTIVATION-PEER')
      for identity in [a,b,c]:native_focus(identity)
      wait(coherent_closed);before=len(journal());history_before=client.activation_history('450')['roots'];chord_start();body=wait(lambda:selected_window('ELM-ACTIVATION-PEER'))
      order=[button['accessibleName'].split(';',1)[0] for button in body['buttons'] if button['accessibleName'].startswith(('Activate ELM-','Restore ELM-'))]
      check('NativeThreeRootFrozenMRUOrder',order==['Activate ELM-CHORD-THIRD','Activate ELM-ACTIVATION-PEER','Activate ELM-AUTHORITY-FIXTURE'],body=body,journal=native_journal())
      popup_capture('global-mru');chord_step();wait(lambda:selected_window('ELM-AUTHORITY-FIXTURE'));chord_step();wait(lambda:selected_window('ELM-CHORD-THIRD'))
      check('ForwardBACWrapNoMutation',len(journal())==before);escape();release_alt();wait(coherent_closed)
      check('CancelPreservesCAndCommittedMRU',facts()['facts']['focused']==c and client.activation_history('450')['roots']==history_before and len(journal())==before,expectedFocus=c,actualFocus=facts()['facts']['focused'],historyBefore=history_before,historyAfter=client.activation_history('450')['roots']);recipient('Cancel',c,'ELM-CHORD-THIRD')
      chord_start(True);wait(lambda:selected_window('ELM-AUTHORITY-FIXTURE'));escape();release_alt();wait(coherent_closed);check('FirstReverseAWithoutMutation',len(journal())==before and facts()['facts']['focused']==c)
      chord_start();wait(lambda:selected_window('ELM-ACTIVATION-PEER'));hold_arm.write_text('armed');release_alt();wait(lambda:hold_waiting.exists());prepared=json.loads(hold_waiting.read_text());report['heldSelection']=prepared
      escape();check('NativeCancelBeforeQueuedEffectCommit',native_journal()['cancelled'] and not native_journal()['consumed']);hold_release.write_text('release')
      receipt('QueuedCancel',before,b,'Refused');check('QueuedCancelPreservesFocusMRU',facts()['facts']['focused']==c and client.activation_history('450')['roots']==history_before);recipient('QueuedCancel',c,'ELM-CHORD-THIRD')
      before=len(journal());chord_start();wait(lambda:selected_window('ELM-ACTIVATION-PEER'));release_alt();receipt('GlobalForward',before,b);recipient('GlobalForward',b,'ELM-ACTIVATION-PEER')
      for identity in [a,b,c]:native_focus(identity)
      wait(coherent_closed);report['beforeControlledRetirements']=facts();check('ChordOriginalTargetMembershipBeforeRetirement',current_window()['workspace']==initial_workspace,nativeWorkspace=current_window()['workspace'],originalWorkspace=initial_workspace);before=len(journal());chord_start();wait(lambda:selected_window('ELM-ACTIVATION-PEER'));frozen=native_journal()['roots'];fixture_control('retire-peer');wait(lambda:all(row['incarnation']!=b for row in facts()['facts']['windows']));fixture_control('arrive-chord');arrival=wait(lambda:next((row['incarnation'] for row in client.snapshot('450')['windows'] if row['label']=='ELM-CHORD-ARRIVAL'),None));wait(lambda:selected_window('ELM-AUTHORITY-FIXTURE'))
      body=popup_body();check('HeldChordRetiresBAndExcludesArrival',arrival not in frozen and all('ELM-CHORD-ARRIVAL' not in row['accessibleName'] for row in body['buttons']),body=body,journal=native_journal());release_alt();receipt('RetiredSelectionFallback',before,a);recipient('RetiredSelectionFallback',a,'ELM-AUTHORITY-FIXTURE')
      chord_start();wait(lambda:selected_window('ELM-CHORD-ARRIVAL'));check('ArrivalEntersNextChord',arrival in native_journal()['roots']);escape();release_alt();wait(coherent_closed)
      fixture_control('retire-third');wait(lambda:all(row['incarnation']!=c for row in facts()['facts']['windows']));fixture_control('retire-arrival');wait(lambda:len(client.snapshot('450')['windows'])==1);wait(coherent_closed)
      before=len(journal());chord_start();wait(lambda:selected_window('ELM-AUTHORITY-FIXTURE'));release_alt();receipt('SoleCandidate',before,a);check('SoleCandidateNeverMinimized',not facts()['facts']['windows'][0]['minimized']);recipient('SoleCandidate',a,'ELM-AUTHORITY-FIXTURE')
      private_effect('minimize',a);wait(lambda:facts()['facts']['windows'][0]['minimized'] and coherent_closed());before=len(journal());chord_start();wait(lambda:selected_window('ELM-AUTHORITY-FIXTURE'));release_alt();receipt('SoleMinimizedRestore',before,a);check('SoleMinimizedCandidateRestores',not facts()['facts']['windows'][0]['minimized'] and journal()[-1]['intent']['operation']=='restore');recipient('SoleMinimizedRestore',a,'ELM-AUTHORITY-FIXTURE')
      fixture_control('retire-primary');wait(lambda:len(client.snapshot('450')['windows'])==0);wait(coherent_closed);before=len(journal());before_publication=int(projection()['publication']);chord_start();release_alt();zero_journal=native_journal();zero_generation=zero_journal['generation'];wait(lambda:any(json.loads(line.split(': ',1)[1]).get('chord',{}).get('generation')==zero_generation for line in text().splitlines() if line.startswith('backend-frame: ')));wait(lambda:coherent_closed() and int(projection()['publication'])>before_publication);check('ZeroCandidateNoEffectNoOpenSwitcher',len(journal())==before and facts()['facts']['focused'] is None)
      check('GlobalChordNeverLaunchesApplications',not launches())
      retries=[json.loads(line) for line in (OUTPUT/'chord-retries.jsonl').read_text().splitlines()]
      check('ExactTerminalRetriesSurviveNewSelectionPreparation',len(retries)>=3 and all(row['matches'] for row in retries),retries=retries)
      report['nativeChordJourneyObserved']=True
    elif SWITCHER:
     roots=client.snapshot('443')['windows'];labels={row['incarnation']:row['label'] for row in roots}
     native_history=client.activation_history('444');before_focus=facts()['facts']['focused'];before=len(journal())
     peer_identity=next(row['incarnation'] for row in roots if row['label']=='ELM-ACTIVATION-PEER')
     check('SwitcherNativeHistoryStartsAtCommittedFocus',len(roots)==2 and native_history['roots']==[before_focus,peer_identity],history=native_history,focus=before_focus)
     original_membership=sorted((row['incarnation'],row['workspace'],row['monitor']) for row in facts()['facts']['windows'])
     report['switcherOracle']={'history':native_history,'labels':labels,'beforeFocus':before_focus,'membership':original_membership}
     def open_switcher():
      opener=wait(lambda:next((button for button in (bar_body() or {}).get('buttons',[]) if button['accessibleName']=='Open window switcher' and not button['disabled']),None))
      click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     def selected_window(label):
      body=popup_body()
      if not body or 'Switch windows' not in body['text']:return None
      chosen=next((button for button in body['buttons'] if button['accessibleName'].endswith(label+'; selected') and not button['disabled']),None)
      ack='surface-presentation-applied: publication='+body['publication']+' lease='+body['lease']
      return body if chosen and body['focus']==chosen['id'] and ack in text().splitlines() else None
     def typed_recipient(label):
      events=control.with_suffix('.events.jsonl');offset=len(events.read_text().splitlines()) if events.exists() else 0
      key(30);delivered=[json.loads(line) for line in events.read_text().splitlines()[offset:]] if events.exists() else []
      check('ActualKeyboardRecipient'+label,any(row['kind']=='key' and row['keyval']==97 and row['window']==label for row in delivered),events=delivered)
     def selected_effect(operation):
      count=len(journal());key(28)
      wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent' and facts()['facts']['focused']==peer_identity)
      check('SwitcherExactlyOne'+operation,len(journal())==count+1 and journal()[-1]['intent']['incarnation']==peer_identity and journal()[-1]['intent']['operation']==operation,journal=journal()[count:])
      submitted=journal()[-1]
      def receipts():
       frames=[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ')]
       return [frame for frame in frames if frame.get('kind')=='effect-outcome' and frame.get('binding')==submitted['binding'] and frame.get('effectProtocol')==submitted['effectProtocol'] and frame.get('intent')==submitted['intent']]
      observed=wait(receipts);check('SwitcherCorrelatedNative'+operation,len(observed)==1 and observed[0]['status']=='Committed',receipts=observed)
      report.setdefault('switcherReceipts',[]).append({'request':submitted,'receipt':observed[0]})
      typed_recipient('ELM-ACTIVATION-PEER')
     if ACCESSIBILITY:
      dom=wait(lambda:(body if body and body.get('buttons') and any(b['accessibleName'].startswith('Choose a window from') for b in body['buttons']) else None) if (body:=bar_body()) else None);names=[b['accessibleName'] for b in dom['buttons']]
      def bar_tree():
       value=at_observe();rows=[row for row in value['nodes'] if any(a['role']=='tool bar' and a['name']=='Warlock taskbar' for a in row['ancestors']) and row['role'] in ['push button','toggle button']]
       return (value,rows) if len(rows)==len(names) and sorted(row['name'] for row in rows)==sorted(names) else None
      tree,at_bar=wait(bar_tree);report['accessibilitySnapshots']=[{'stage':'TaskbarInitial',**tree}]
      check('ActualTaskbarExportsAllControlNames',len(at_bar)==len(names) and sorted(row['name'] for row in at_bar)==sorted(names),native=at_bar,dom=names)
      check('ActualTaskbarActiveStateHasNativeToggleState',sum(bool({'pressed','checked'} & set(row['states'])) for row in at_bar)==1 and all(bool({'pressed','checked'} & set(row['states']))==('Active' in row['name']) for row in at_bar),native=at_bar)
      button=next(b for b in dom['buttons'] if b['accessibleName'].startswith('Choose a window from'))
      click({'visible':0<=button['x']+button['width']/2<800 and 0<=button['y']<48,'point':[button['x']+button['width']/2,button['y']+button['height']/2]})
      # Click opens the actual group picker. Escape then leaves physical focus
      # on its existing taskbar opener; no injected DOM/AT focus qualifies it.
      wait(lambda:(projection() or {}).get('mode')=='picker');key(1);wait(lambda:(projection() or {}).get('mode')=='closed')
      def bar_focus():
       value=at_observe();return value if ((value.get('reader') or {}).get('focus') or {}).get('name')==button['accessibleName'] and any(row['name']==button['accessibleName'] and 'focused' in row['states'] for row in value['nodes']) else None
      bar_state=wait(bar_focus);report['accessibilitySnapshots'].append({'stage':'TaskbarFocusAfterDismissal',**bar_state})
      check('ActualOrcaAndInspectorAgreeTaskbarFocus',bar_state['reader']['focus']['role'] in ['push button','toggle button'],reader=bar_state['reader'])
     def accessible_choice(stage,body):
      name=next(b['accessibleName'] for b in body['buttons'] if b['id']==body['focus'])
      def agrees():
       value=at_observe();options=[row for row in value['nodes'] if row['role']=='list item' and any(a['role']=='list box' and a['name']=='Switch windows' for a in row['ancestors'])]
       reader=value.get('reader') or {};focus=reader.get('focus') or {}
       selected=[row for row in options if 'selected' in row['states']]
       return value if len(options)==2 and len(selected)==1 and selected[0]['name']==name and 'focused' in selected[0]['states'] and focus.get('name')==name else None
      value=wait(agrees);report['accessibilitySnapshots'].append({'stage':stage,**value})
      check(stage+'NativeNamesRolesSelectionAndOrcaFocusAgree',value['reader']['focus']['role']=='list item',reader=value['reader'])
     open_switcher();body=wait(lambda:selected_window('ELM-ACTIVATION-PEER'))
     if ACCESSIBILITY:accessible_choice('SwitcherInitial',body)
     visible_order=[button['accessibleName'].split(';',1)[0] for button in body['buttons'] if button['accessibleName'].startswith(('Activate ELM-','Restore ELM-'))]
     check('SwitcherFrozenOrderMatchesNativeHistory',visible_order==['Activate '+labels[root] for root in native_history['roots']],body=body)
     popup_capture('mru-initial');key(15);wait(lambda:selected_window('ELM-AUTHORITY-FIXTURE'))
     if ACCESSIBILITY:accessible_choice('SwitcherForward',wait(lambda:selected_window('ELM-AUTHORITY-FIXTURE')))
     key(105);wait(lambda:selected_window('ELM-ACTIVATION-PEER'))
     if ACCESSIBILITY:accessible_choice('SwitcherReverse',wait(lambda:selected_window('ELM-ACTIVATION-PEER')))
     check('SwitcherLocalForwardReverseHasNoWindowEffect',len(journal())==before and facts()['facts']['focused']==before_focus)
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     check('SwitcherNativeEscapeRetainsPressUntilPhysicalRelease','surface-native-escape-stored:' in text() and 'surface-terminal-released: key=65307' in text())
     check('SwitcherEscapePreservesNativeFocusAndEffects',facts()['facts']['focused']==before_focus and len(journal())==before)
     typed_recipient('ELM-AUTHORITY-FIXTURE')
     open_switcher();wait(lambda:selected_window('ELM-ACTIVATION-PEER'));popup_capture('reopened');selected_effect('activate')
     private_effect('minimize',peer_identity)
     wait(lambda:any(row['incarnation']==peer_identity and row['minimized'] for row in facts()['facts']['windows']) and (projection() or {}).get('phase')=='Coherent')
     open_switcher();wait(lambda:selected_window('ELM-ACTIVATION-PEER'));selected_effect('restore')
     check('SwitcherLeavesWorkspaceOutputMembershipUnchanged',sorted((row['incarnation'],row['workspace'],row['monitor']) for row in facts()['facts']['windows'])==original_membership)
     for capture in report['popupCaptures']:check('ActualSwitcherControlPixels'+capture['stage'],len(capture['controlRegions'])==2 and all(row['area']>0 and row['brightPixels']>30 and row['paintedPixels']>.9*row['area'] for row in capture['controlRegions']),capture=capture)
     check('SwitcherDoesNotLaunchApplications',not launches())
     if ACCESSIBILITY:
      final_at=at_observe();report['accessibilitySnapshots'].append({'stage':'SwitcherRetired',**final_at})
      check('ActualRetiredSwitcherHasNoSelectedNativeOptions',not any(row['role']=='list item' and 'selected' in row['states'] for row in final_at['nodes']))
      check('ActualBridgePublishesFocusAndSelectionEvents',any(e['type']=='object:state-changed:focused' and e['detail1']==1 for e in final_at['events']) and any(e['type']=='object:state-changed:selected' for e in final_at['events']),events=final_at['events'])
      utterances=OUTPUT/'orca-utterances.jsonl';report['orcaSpeechOutput']=[json.loads(line) for line in utterances.read_text().splitlines()]
      check('ActualOrcaSpeaksTaskbarAndSwitcherNames',any('Choose a window from' in row.get('text','') for row in report['orcaSpeechOutput']) and all(any(label in row.get('text','') for row in report['orcaSpeechOutput']) for label in ['ELM-AUTHORITY-FIXTURE','ELM-ACTIVATION-PEER']),utterances=report['orcaSpeechOutput'])
      report['accessibilityFixture']['nativeATObserved']=True
     report['nativeSwitcherJourneyObserved']=True
    elif NAV:
     def peer_window():return next(w for w in facts()['facts']['windows'] if w['incarnation']==peer_identity)
     def native_membership():return sorted((w['incarnation'],w['workspace'],w['monitor']) for w in facts()['facts']['windows'])
     original_membership=native_membership()
     check('OriginalWorkspaceTwoMinimizedFixture',peer_window()['workspace']=='2' and peer_window()['minimized'] and not peer_window()['workspaceVisible'] and s.data('monitors')[0]['activeWorkspace']['id']==1,membership=original_membership)
     def restored(stage,before):
      wait(lambda:peer_window()['workspaceVisible'] and not peer_window()['minimized'] and facts()['facts']['focused']==peer_identity and (projection() or {}).get('phase')=='Coherent')
      check(stage+'ExactlyOneRestore',len(journal())==before+1 and journal()[-1]['intent']['incarnation']==peer_identity and journal()[-1]['intent']['operation']=='restore',journal=journal()[before:])
      submitted=journal()[-1]
      def correlated_receipts():
       frames=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ')]
       return [f for f in frames if f.get('kind')=='effect-outcome' and f.get('binding')==submitted['binding'] and f.get('effectProtocol')==submitted['effectProtocol'] and f.get('intent')==submitted['intent']]
      receipts=wait(correlated_receipts);check(stage+'CorrelatedNativeRestoreReceipt',len(receipts)==1 and receipts[0]['status']=='Committed',request=submitted,receipts=receipts)
      report.setdefault('navigationReceipts',[]).append({'stage':stage,'request':submitted,'receipt':receipts[0]})
      check(stage+'PreservesWorkspaceAndOutput',native_membership()==original_membership and s.data('monitors')[0]['activeWorkspace']['id']==2,membership=native_membership())
      events=control.with_suffix('.events.jsonl');before_events=len(events.read_text().splitlines()) if events.exists() else 0
      key(30);delivered=[json.loads(l) for l in events.read_text().splitlines()[before_events:]] if events.exists() else []
      check(stage+'RealKeyboardRecipient',facts()['facts']['focused']==peer_identity and any(e['kind']=='key' and e['keyval']==97 and e['window']=='ELM-ACTIVATION-PEER' for e in delivered),events=delivered)
      image=OUTPUT/(stage+'.png');helper(['/usr/bin/grim',str(image)])
      import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
      pix=GdkPixbuf.Pixbuf.new_from_file(str(image));data=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();x,y,width,height=map(int,peer_window()['geometry']);left,top=max(0,x+10),max(100,y+10);right,bottom=min(800,x+width-10),min(600,y+height-10)
      green=sum(1 for py in range(top,bottom) for px in range(left,right) if data[py*stride+px*channels+1]>100 and data[py*stride+px*channels+1]>data[py*stride+px*channels]+30 and data[py*stride+px*channels+1]>data[py*stride+px*channels+2]+30)
      check(stage+'ActualRestoredWindowPixels',green>1000,image=str(image),sha256=sha(image),region=[left,top,right,bottom],greenPixels=green)
      report.setdefault('navigationCaptures',[]).append({'stage':stage,'path':str(image),'sha256':sha(image),'nativeFacts':facts(),'events':delivered})
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Task View' and not b['disabled']),None))
     before=len(journal());click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     button=wait(lambda:next((b for b in (popup_body() or {}).get('buttons',[]) if 'ELM-ACTIVATION-PEER on workspace 2' in b['accessibleName'] and not b['disabled']),None))
     popup_capture('task-view-before-select');capture=report['popupCaptures'][-1];check('TaskViewNavigationControlsArePainted',bool(capture['controlRegions']) and all(r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
     keyboard_button(button['accessibleName']);restored('TaskViewRestore',before)
     # Set up a second original journey before its user input. These fixture
     # actions are never used to repair focus after the GUI selection.
     private_effect('minimize',peer_identity)
     check('SecondFixtureReturnsWorkspaceOne',s.ctl('dispatch',"hl.dsp.focus({window='"+selector+"'})").strip()=='ok')
     wait(lambda:peer_window()['minimized'] and not peer_window()['workspaceVisible'] and s.data('monitors')[0]['activeWorkspace']['id']==1 and (projection() or {}).get('phase')=='Coherent')
     before=len(journal());click(wait(lambda:group('Choose a window from')))
     button=wait(lambda:next((b for b in (popup_body() or {}).get('buttons',[]) if 'ELM-ACTIVATION-PEER' in b['accessibleName'] and not b['disabled']),None))
     popup_capture('taskbar-before-select');capture=report['popupCaptures'][-1];check('TaskbarNavigationControlsArePainted',bool(capture['controlRegions']) and all(r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
     keyboard_button(button['accessibleName']);restored('TaskbarRestore',before)
     old=facts();check('RefusalFixtureFocusChanges',s.ctl('dispatch',"hl.dsp.focus({window='"+selector+"'})").strip()=='ok');wait(lambda:facts()['facts']['focused']==target)
     before_refusal=facts();n=str((10000 if MEMBERSHIP else 9000)+len(report['nativeFixtures']));intent={'request':n,'generation':n,'incarnation':peer_identity,'operation':'activate','context':client.context(old)};receipt=client.effect(intent);report['nativeFixtures'].append({'intent':intent,'result':receipt})
     check('StaleActivationRefusesWithoutNavigationOrFocus',receipt['status']=='Refused' and receipt['reason']=='dependency-mismatch' and facts()['facts']==before_refusal['facts'] and s.data('monitors')[0]['activeWorkspace']['id']==1,result=receipt,before=before_refusal,after=facts())
     report['nativeNavigationJourneyObserved']=True
    elif TASKVIEW:
     wait(lambda:(projection() or {}).get('phase')=='Coherent')
     native_facts=facts();labels={w['incarnation']:w['label'] for w in client.snapshot('443')['windows']}
     membership=[{'incarnation':w['incarnation'],'label':labels[w['incarnation']],'workspace':w['workspace']} for w in native_facts['facts']['windows'] if w['incarnation'] in labels]
     active=s.data('monitors')[0]['activeWorkspace']['id'];before=len(journal());before_focus=native_facts['facts']['focused']
     check('TwoPopulatedNativeWorkspaceFixture',sorted((w['label'],w['workspace']) for w in membership)==[('ELM-ACTIVATION-PEER','2'),('ELM-AUTHORITY-FIXTURE','1')] and active==1,membership=membership,activeWorkspace=active)
     report['workspaceOracle']={'membership':membership,'activeWorkspace':str(active),'beforeFocus':before_focus}
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Task View' and not b['disabled']),None))
     click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     body=wait(lambda:next((b for b in [popup_body()] if b and 'Task View' in b['text'] and 'active workspace' in b['text'].lower() and all(any(w['label']+' on workspace '+w['workspace'] in button['accessibleName'] for button in b['buttons']) for w in membership)),None))
     marker=next(b for b in body['buttons'] if b['accessibleName']=='Browse workspace 1; active workspace')
     wait(lambda:(popup_body() or {}).get('focus')==marker['id'])
     check('TaskViewGroupsMatchNativeMembership',all(any(w['label']+' on workspace '+w['workspace'] in b['accessibleName'] and 'Workspace '+w['workspace'] in b['label'] for b in body['buttons']) for w in membership),body=body)
     check('ActiveWorkspaceMarkerIsKeyboardSelected',popup_body()['focus']==marker['id'] and 'Active workspace' in marker['label'],body=popup_body())
     popup_capture('initial')
     keyboard_button('Browse workspace 2')
     body=wait(lambda:next((b for b in [popup_body()] if b and 'ELM-ACTIVATION-PEER' in b['text'] and 'ELM-AUTHORITY-FIXTURE' not in b['text'] and any(button['accessibleName']=='Browse workspace 2' and 'Selected' in button['label'] and button['id']==b['focus'] for button in b['buttons'])),None))
     check('KeyboardWorkspaceBrowseDoesNotMutateNative',len(journal())==before and facts()['facts']['focused']==before_focus and s.data('monitors')[0]['activeWorkspace']['id']==active,body=body)
     popup_capture('workspace-two')
     for capture in report['popupCaptures']:check('ActualTaskViewControlPixels'+capture['stage'],bool(capture['controlRegions']) and all(r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
     report['nativeTaskViewMembershipObserved']=True
     all_windows=next(b for b in body['buttons'] if b['accessibleName']=='Browse all workspaces')
     import re
     rows=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l];box=tuple(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',rows[-1]).groups()))
     x,y=map(round,(box[0]+all_windows['x']+all_windows['width']/2,box[1]+all_windows['y']+all_windows['height']/2))
     helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     wait(lambda:all(w['label'] in (popup_body() or {}).get('text','') for w in membership))
     check('PointerAllWorkspacesRestoresGroupsWithoutMutation',len(journal())==before,body=popup_body())
     if RETIRE_OPENER:
      fixture_control('retire-primary')
      wait(lambda:not any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
      wait(lambda:(projection() or {}).get('phase')=='Coherent' and before_focus not in [w['incarnation'] for w in facts()['facts']['windows']])
      check('OriginalOpenerActuallyRetired',before_focus not in [w['incarnation'] for w in facts()['facts']['windows']])
      def current_popup_presented():
       body=popup_body()
       if not body:return False
       ack='surface-presentation-applied: publication='+body['publication']+' lease='+body['lease']
       return body if ack in text().splitlines() else False
      presented=wait(current_popup_presented)
      report['retiredOpenerPresentationBarrier']={'publication':presented['publication'],'lease':presented['lease'],'observedNativeAck':True}
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
     escape_trace=[line for line in text().splitlines() if line.startswith(('surface-native-escape-stored:','surface-terminal-released: key=65307'))]
     check('TaskViewNativeEscapeRetainsPressUntilPhysicalRelease',len(escape_trace)==2,nativeTrace=escape_trace)
     events=control.with_suffix('.events.jsonl');before_events=len(events.read_text().splitlines()) if events.exists() else 0
     key(30);delivered=[json.loads(l) for l in events.read_text().splitlines()[before_events:]] if events.exists() else []
     if RETIRE_OPENER:
      check('OverviewEscapeCannotReviveRetiredOpener',facts()['facts']['focused']!=before_focus and not any(e['window']=='ELM-AUTHORITY-FIXTURE' for e in delivered),events=delivered,retired=before_focus,after=facts()['facts']['focused'])
      report['nativeRetiredOpenerNegativeObserved']=True
     else:
      check('OverviewEscapeReturnsToEligibleOpener',facts()['facts']['focused']==before_focus and any(e['kind']=='key' and e['keyval']==97 and e['window']=='ELM-AUTHORITY-FIXTURE' for e in delivered),events=delivered,before=before_focus,after=facts()['facts']['focused'])
     check('OverviewDismissalHasNoNativeMutation',len(journal())==before)
     report['nativeTaskViewJourneyObserved']=not RETIRE_OPENER
    elif JUMP:
     def jump_body():
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')=='jump' and body['publication']==p['publication'] else None
     def jump_frames():return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind') in ['jump-list-snapshot','jump-list-outcome']]
     def requests(kind):return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('frontend-request: ') and json.loads(line.split(': ',1)[1]).get('kind')==kind]
     def events():return [json.loads(line) for line in jump_events.read_text().splitlines()] if jump_events.exists() else []
     def open_jump():
      opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open applications' and not b['disabled']),None))
      click({'visible':0<=opener['x'] and opener['x']+opener['width']<=800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
      wait(lambda:(body:=popup_body()) and any(b['accessibleName']=='Actions for A Warlock Editor' and not b['disabled'] for b in body['buttons']))
      keyboard_button('Actions for A Warlock Editor',28)
      return wait(lambda:(body:=jump_body()) and jump_frames() and jump_frames()[-1]['kind']=='jump-list-snapshot' and body)
     before_window=len(journal());body=open_jump();snapshot=jump_frames()[-1]['snapshot'];actions=snapshot['actions']
     check('OriginalTwoDeclaredActionsAppearAndUnsupportedIsAbsent',[a['id'] for a in actions if a['kind']=='desktop']==['desktop:Alpha','desktop:Beta'] and not any('Unsupported' in b['label'] for b in body['buttons']),snapshot=snapshot,body=body)
     check('OriginalOnlyOwnedRecentIdentityIsRendered',len([a for a in actions if a['kind']=='recent'])==1 and not any('Foreign recent' in b['label'] for b in body['buttons']) and snapshot['entry']=='warlock-editor',snapshot=snapshot)
     key(107);wait(lambda:(body:=jump_body()) and any(b['identity']=='jump:action:recent:'+actions[-1]['id'].removeprefix('recent:') and b['id']==body['focus'] for b in body['buttons']))
     popup_capture('jump-list-declared-and-recent');check('JumpListActualNativeTextPixels',bool(report['popupCaptures'][-1]['controlRegions']) and all(r['brightPixels']>15 for r in report['popupCaptures'][-1]['controlRegions']),capture=report['popupCaptures'][-1])
     keyboard_button('New document',28)
     wait(lambda:jump_frames()[-1]['kind']=='jump-list-outcome' and len(events())==1)
     outcome=jump_frames()[-1];check('NativeDeclaredActionSubmittedOnce',outcome['status']=='Submitted' and events()[0]['argv']==['ALPHA'] and len(requests('jump-list-effect'))==1,outcome=outcome,events=events())
     wait(lambda:(projection() or {}).get('mode')=='closed');check('JumpPopupClosesBeforeNativeEffect',len(journal())==before_window and not launches())
     body=open_jump();keyboard_button('Open Warlock recent document',28)
     wait(lambda:jump_frames()[-1]['kind']=='jump-list-outcome' and len(events())==2)
     outcome=jump_frames()[-1];check('NativeOwnedRecentDispatchUsesExactGioDocument',outcome['status']=='Submitted' and events()[1]['argv'] in [['RECENT',str(jump_document)],['RECENT',jump_document.as_uri()]] and len(requests('jump-list-effect'))==2,outcome=outcome,events=events())
     check('ForeignRecentNeverAppearsOrReceivesDispatch',all(str(jump_foreign) not in json.dumps(row) and jump_foreign.as_uri() not in json.dumps(row) for row in events()) and all(r['intent']['entry']=='warlock-editor' for r in requests('jump-list-effect')))
     check('JumpListLeavesWindowAuthorityAndCatalogLaunchUntouched',len(journal())==before_window and not launches())
     report['actualJumpGioEvents']=events();report['jumpOutcomes']=[row for row in jump_frames() if row['kind']=='jump-list-outcome'];report['nativeJumpListsObserved']=True
    elif FILES:
     def files_body():
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')=='files' and body['publication']==p['publication'] else None
     def files_frames():return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind') in ['files-snapshot','files-outcome']]
     before_window=len(journal())
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Files menu' and not b['disabled']),None))
     click({'visible':0<=opener['x'] and opener['x']+opener['width']<=800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     body=wait(lambda:(body:=files_body()) and files_frames() and files_frames()[-1]['snapshot']['peer'] and body)
     peer=files_frames()[-1]['snapshot']['peer']
     check('ElmObservesActualExistingExplorerIdentity',peer['pid']==str(files_process.pid) and peer['start']==start_time(files_process.pid) and peer['instance']==files_native_status['instance'] and peer['target']=='home',peer=peer)
     images=next(b for b in body['buttons'] if b.get('identity')=='files:collection:images' and not b['disabled'])
     for _ in range(len(body['buttons'])+2):
      if (files_body() or {}).get('focus')==images['id']:break
      key(15)
     wait(lambda:(body:=files_body()) and body['focus']==images['id'])
     popup_capture('files-existing-explorer')
     check('FilesMenuHasActualNativeControlPixels',any(row['accessibleName']=='Images' and row['brightPixels']>15 for row in report['popupCaptures'][-1]['controlRegions']),capture=report['popupCaptures'][-1])
     key(28)
     wait(lambda:files_frames()[-1]['kind']=='files-outcome')
     outcome=files_frames()[-1];opened=outcome['snapshot']['peer'];ui=files_ipc('uiState');status=files_ipc('migrationStatus')
     check('OriginalExistingExplorerReusedAtRequestedCollection',outcome['status']=='Opened' and len(requests('files-open'))==1 and all(opened[k]==peer[k] for k in ['pid','start','instance']) and ui['collId']=='images' and ui['visible'] and status['instance']==files_native_status['instance'],outcome=outcome,ui=ui,status=status)
     check('FilesOpeningClosesPopupWithoutWindowEffects',projection()['mode']=='closed' and len(journal())==before_window and not launches())
     # Read-only native UI capture from the same exact explorer instance.
     explorer_image=OUTPUT/'installed-files-images.png';files_ipc('shot','explorer',str(explorer_image))
     def image_ready(path):
      if not path.exists() or path.stat().st_size<=1000:return False
      import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf,GLib
      try:image=GdkPixbuf.Pixbuf.new_from_file(str(path))
      except GLib.Error:return False
      return image.get_width()>300 and image.get_height()>300
     wait(lambda:image_ready(explorer_image))
     check('RequestedCollectionHasInstalledExplorerNativeImage',explorer_image.stat().st_size>1000,path=str(explorer_image),sha256=sha(explorer_image))
     check('InstalledOperationsAndQuintSemanticsUnchanged',all(sha(path)==digest for path,digest in operation_hashes.items()) and all(sha(path)==digest for path,digest in qml_hashes.items()),hashes=operation_hashes)
     check('FilesNavigationDoesNotCreateAnotherExplorer',len(json.loads(helper(['/usr/bin/qs','--log-rules','quickshell.bare.info=false','-p',str(installed_files),'list','--json'])))==1)
     report['filesCollectionOutcome']=outcome
     # A separate explicit folder gesture exercises the actual native field,
     # composition-free keyboard editing, and the installed directory view.
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Files menu' and not b['disabled']),None))
     click({'visible':0<=opener['x'] and opener['x']+opener['width']<=800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     wait(lambda:(body:=files_body()) and files_frames()[-1]['kind']=='files-snapshot' and body)
     for _ in range(len(files_body()['buttons'])+3):
      body=files_body()
      if any(field['id']==body['focus'] for field in body['fields']):break
      key(15)
     check('NativeKeyboardReachesFolderField',any(field['id']==files_body()['focus'] for field in files_body()['fields']),body=files_body())
     # Held Shift for the two uppercase characters; original key pulses.
     helper([str(keyboard)],'key 29 1\nkey 30 1\nsleep 50\nkey 30 0\nkey 29 0\nkey 14 1\nsleep 50\nkey 14 0\nsleep 100\nkey 42 1\nkey 41 1\nsleep 50\nkey 41 0\nkey 42 0\nsleep 100\nkey 53 1\nsleep 50\nkey 53 0\nsleep 100\nkey 42 1\nkey 32 1\nsleep 50\nkey 32 0\nkey 42 0\nsleep 100\nsync\n')
     for code in [24,46,22,50,18,49,20,31]:key(code)
     wait(lambda:any(field['value']=='~/Documents' for field in (files_body() or {}).get('fields',[])))
     check('NativeFolderTypingDoesNotOpen',len(requests('files-open'))==1)
     key(15);keyboard_button('Open folder',28)
     wait(lambda:files_frames()[-1]['kind']=='files-outcome' and len(requests('files-open'))==2)
     folder=files_frames()[-1];ui=files_ipc('uiState')
     check('NativeExplicitFolderOpeningReusesSameExplorer',folder['status']=='Opened' and folder['snapshot']['peer']['target']==str(private_home/'Documents') and all(folder['snapshot']['peer'][k]==peer[k] for k in ['pid','start','instance']) and ui['cwd']==str(private_home/'Documents') and ui['collId']=='',outcome=folder,ui=ui)
     check('NativeFolderOpeningPreservesOperationsAndNoWindowEffects',len(journal())==before_window and all(sha(path)==digest for path,digest in operation_hashes.items()))
     report['filesOutcome']=folder;report['nativeFilesObserved']=True
    elif SYSTEM:
     def system_body():
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')=='system' and body['publication']==p['publication'] else None
     def system_frames():return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind') in ['system-menu-snapshot','system-menu-outcome']]
     def state():return system_frames()[-1]['snapshot'] if system_frames() else None
     def navigate(label):
      target=wait(lambda:next((b for b in (system_body() or {}).get('buttons',[]) if b['accessibleName']==label and not b['disabled']),None))
      for _ in range(len(system_body()['buttons'])+2):
       if system_body()['focus']==target['id']:break
       key(15)
      wait(lambda:(body:=system_body()) and body['focus']==target['id'])
     before_window=len(journal());opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open system menu' and not b['disabled']),None));click({'visible':0<=opener['x'] and opener['x']+opener['width']<=800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     body=wait(lambda:(body:=system_body()) and state() and state()['volume'] and state()['session'] and body)
     check('OriginalUnavailableNetworkAndObservedRemainingCapabilities',state()['network'] is None and 'Network unavailable' in body['text'] and state()['volume']['percent']==100 and state()['power']=={'suspend':'yes','reboot':'yes','poweroff':'no'} and state()['session']['name']=='Warlock private session',snapshot=state(),body=body)
     check('UnavailableNetworkHasNoActionTarget',not any(b.get('identity','').startswith('system:network-enable:') for b in body['buttons']))
     navigate('Suspend');popup_capture('system-menu-capabilities');capture=report['popupCaptures'][-1]
     check('UnavailableNetworkHasActualNativeTextPixels',any(row['accessibleName']=='Network unavailable' and row['brightPixels']>15 for row in capture['controlRegions']),capture=capture)
     keyboard_button('Set volume 25%',28)
     wait(lambda:state()['volume']['percent']==25 and system_frames()[-1].get('status')=='Committed')
     sent=requests('system-menu-effect');receipt=system_frames()[-1]
     check('KeyboardVolumeChangeHasOneCorrelatedObservedNativeOutcome',len(sent)==1 and sent[0]['intent']['operation']=='volume-set' and sent[0]['intent']['value']==25 and receipt['requestId']==sent[0]['requestId'] and receipt['status']=='Committed',request=sent[0],receipt=receipt)
     wait(lambda:(body:=system_body()) and any(b.get('identity')=='system:volume-set:25' and b['disabled'] for b in body['buttons']))
     keyboard_button('Mute',28);wait(lambda:state()['volume']['muted'] and system_frames()[-1].get('status')=='Committed')
     check('MuteReadbackUsesCurrentNativeAudioSink',len(requests('system-menu-effect'))==2 and 'muted' in system_body()['text'],receipt=system_frames()[-1])
     before_system=len(requests('system-menu-effect'));keyboard_button('Restart',28)
     wait(lambda:(body:=system_body()) and any(b.get('identity')=='system:cancel' and not b['disabled'] for b in body['buttons']))
     check('RestartPromptDoesNotSubmitNativePowerChange',len(requests('system-menu-effect'))==before_system and json.loads(system_state.read_text())['calls']==[])
     keyboard_button('Cancel system change',28);wait(lambda:(body:=system_body()) and not any(b.get('identity')=='system:confirm' for b in body['buttons']))
     check('CancelPreservesSessionWithoutNativeEffects',json.loads(system_state.read_text())['calls']==[] and len(requests('system-menu-effect'))==before_system)
     keyboard_button('Refresh system state',28);wait(lambda:system_frames()[-1]['kind']=='system-menu-snapshot')
     check('RefreshReadsCurrentStateAndNeverRepeatsChanges',len(requests('system-menu-effect'))==before_system and state()['volume']['percent']==25 and state()['volume']['muted'])
     key(1);wait(lambda:projection()['mode']=='closed')
     check('SystemEscapeClosesWithoutWindowOrLaunchEffects',len(journal())==before_window and not launches())
     report['systemProviderState']=json.loads(system_state.read_text());report['nativeSystemMenuObserved']=True
    elif NOTIFICATIONS:
     notification_control=OUTPUT/'notification-control.json'
     producer=s.host.launch('notification-producers',['/usr/bin/python3','-B',str(ROOT/'qa/notification-producer.py'),str(notification_control)],env=env);apps.append(producer);notification_producer=producer
     notification_serial=0
     def producer_events():
      path=notification_control.with_suffix('.events.jsonl')
      raw=path.read_text() if path.exists() else ''
      return [json.loads(line) for line in raw[:raw.rfind('\n')+1].splitlines()]
     wait(lambda:any(row['kind']=='ready' for row in producer_events()))
     def notify(producer_index,summary,label,timeout=0,replaces=0):
      global notification_serial
      notification_serial+=1
      temp=notification_control.with_suffix('.tmp');temp.write_text(json.dumps({'serial':notification_serial,'op':'notify','producer':producer_index,'summary':summary,'label':label,'timeout':timeout,'replaces':replaces}));os.replace(temp,notification_control)
      return wait(lambda:next((row['id'] for row in producer_events() if row['kind']=='notified' and row['serial']==notification_serial),None))
     def center_body():
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')=='notifications' and body['publication']==p['publication'] else None
     def incoming():return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ')]
     def notification_snapshot():
      frames=[frame['snapshot'] for frame in incoming() if frame.get('kind') in ['notification-update','notification-snapshot','notification-outcome']]
      return frames[-1] if frames else None
     def notification_row(identifier):return next((row for row in (notification_snapshot() or {}).get('entries',[]) if row['id']==str(identifier)),None)
     def signals(identifier):return [row for row in producer_events() if row['kind']=='signal' and row['values'][0]==identifier]
     before_effects=len(journal());before_focus=facts()['facts']['focused']
     current=notify(0,'Current notification','Open current notification');other=notify(1,'Other producer','Open other notification')
     wait(lambda:notification_row(current) and notification_row(other))
     check('IncomingNotificationsDoNotOpenPopupOrStealNativeFocus',projection()['mode']=='closed' and facts()['facts']['focused']==before_focus)
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open notifications' and not b['disabled']),None))
     helper([str(POINTER),'800','600'],f"move {round(opener['x']+opener['width']/2)} {round(opener['y']+opener['height']/2)}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n")
     wait(lambda:(body:=center_body()) and any(b['accessibleName']=='Open current notification' and not b['disabled'] for b in body['buttons']))
     keyboard_button('Open current notification',28)
     wait(lambda:any(row['signal']=='ActionInvoked' for row in signals(current)))
     sent=requests('notification-effect');outcomes=[frame for frame in incoming() if frame.get('kind')=='notification-outcome' and frame.get('requestId')==sent[-1]['requestId']]
     check('CurrentActionDispatchesExactlyOnceToItsProducer',len(sent)==1 and len(outcomes)==1 and outcomes[0]['status']=='Dispatched' and signals(current)==[{'kind':'signal','producer':0,'signal':'ActionInvoked','values':[current,'open']}],request=sent,outcomes=outcomes,signals=signals(current))
     check('AnotherNotificationAndProducerUnaffected',signals(other)==[] and notification_row(other)['state']=='live')
     wait(lambda:(body:=center_body()) and not any(b['accessibleName']=='Open current notification' for b in body['buttons']))
     expired=notify(0,'Expiring notification','Open expiring notification',timeout=1200)
     wait(lambda:(body:=center_body()) and any(b['accessibleName']=='Open expiring notification' and not b['disabled'] for b in body['buttons']))
     old_expiring=notification_row(expired)
     wait(lambda:notification_row(expired) and notification_row(expired)['state']=='expired' and (body:=center_body()) and not any(b['accessibleName']=='Open expiring notification' for b in body['buttons']))
     check('ExpiryRemovesFormerActionAndKeepsReadableHistory',any(b['accessibleName']=='Warlock fixture: Expiring notification' and 'expired' in b['label'] for b in center_body().get('content',[])) and signals(expired)==[{'kind':'signal','producer':0,'signal':'NotificationClosed','values':[expired,1]}],body=center_body(),signals=signals(expired))
     # The latest entry is first; queue its real keyboard action while live,
     # let it expire, replace the same ID on the native bus, then admit it.
     reuse=notify(0,'Reuse original','Open old incarnation',timeout=1800)
     wait(lambda:(body:=center_body()) and any(b['accessibleName']=='Open old incarnation' and not b['disabled'] for b in body['buttons']))
     notification_arm.write_text('hold')
     keyboard_button('Open old incarnation',28)
     queued=wait(lambda:json.loads(notification_waiting.read_text()) if notification_waiting.exists() else None)
     wait(lambda:any(row['signal']=='NotificationClosed' and row['values']==[reuse,1] for row in signals(reuse)))
     replacement=notify(0,'Reuse replacement','Open replacement notification',replaces=reuse)
     notification_release.write_text('release')
     refused=wait(lambda:next((frame for frame in incoming() if frame.get('kind')=='notification-outcome' and frame.get('requestId')==queued['requestId']),None))
     wait(lambda:(body:=center_body()) and any(b['accessibleName']=='Open replacement notification' and not b['disabled'] for b in body['buttons']))
     check('OldQueuedActionRefusedAfterExpiredIdReuse',replacement==reuse and refused['status']=='Refused' and notification_row(reuse)['incarnation']!=queued['intent']['incarnation'] and not any(row['signal']=='ActionInvoked' for row in signals(reuse)),queued=queued,outcome=refused,producerSignals=signals(reuse))
     keyboard_button('Open replacement notification',28)
     wait(lambda:any(row['signal']=='ActionInvoked' for row in signals(reuse)))
     check('OnlyNewIncarnationReceivesChosenAction',len([row for row in signals(reuse) if row['signal']=='ActionInvoked'])==1 and signals(other)==[],signals=signals(reuse))
     helper([str(POINTER),'800','600'],'move 400 280\nwheel 180 0\nsleep 100\n')
     popup_capture('notification-history')
     capture=report['popupCaptures'][-1]
     check('HistoryHasActualNativeTextPixels',any(region['accessibleName']=='Warlock fixture: Expiring notification' and region['brightPixels']>15 for region in capture['controlRegions']),capture=capture)
     key(1);wait(lambda:projection()['mode']=='closed')
     check('NotificationEscapeClosesCenterWithoutWindowEffects',len(journal())==before_effects and not launches())
     notification_serial+=1;notification_control.write_text(json.dumps({'serial':notification_serial,'op':'quit'}));producer.wait(timeout=5)
     check('NativeNotificationProducersExitNormally',producer.returncode==0)
     report['notificationProducerEvents']=producer_events();report['nativeNotificationsObserved']=True
    elif SETTINGS:
     desired_theme="high-contrast" if CONTRAST else "dawn"
     state_file=pathlib.Path(env['XDG_STATE_HOME'])/'warlock/settings.json'
     def stored():return json.loads(state_file.read_text()) if state_file.exists() else None
     def settings_body():
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')=='settings' and body['publication']==p['publication'] and any(b['identity']=='settings:theme:'+desired_theme for b in body['buttons']) else None
     def opener():
      body=bar_body()
      if not body:return None
      button=next((b for b in body['buttons'] if b['accessibleName']=='Open settings' and not b['disabled']),None)
      if not button:return None
      actions=body['actions']
      if button['x']<actions['x'] or button['x']+button['width']>actions['x']+actions['width']:
       # A bounding box outside the scrolling action strip is not a hit target.
       # Use ordinary native pointer wheel input to reveal the actual control.
       helper([str(POINTER),'800','600'],f"move {round(actions['x']+actions['width']/2)} {round(actions['y']+actions['height']/2)}\nsleep 100\nwheel 4096\nsleep 100")
       return None
      return button
     # Pointer opens the surface; every preference edit/save/dismissal uses
     # actual native keyboard events with the original 6-second observations.
     button=wait(opener);click({'visible':0<=button['x']<800 and 0<=button['y']<48,'point':[button['x']+button['width']/2,button['y']+button['height']/2]})
     body=wait(lambda:settings_body() if settings_body() and any(b['identity']=='settings:theme:'+desired_theme and not b['disabled'] for b in settings_body()['buttons']) else None)
     check('SettingsLoadedNativeDefaultAppearance',body['theme']=='night' and body['textScale']=='100' and body['fontSize']=='16px',body=body)
     keyboard_button('High contrast theme' if CONTRAST else 'Dawn theme',28);keyboard_button('Text size 150%',28)
     check('SettingsDraftDoesNotChangeAppearanceOrWrite',settings_body()['theme']=='night' and settings_body()['textScale']=='100' and not requests('shell-settings-write') and not stored())
     keyboard_button('Save settings',28)
     saved=wait(lambda:stored() if stored() and stored()['values']=={'theme':desired_theme,'textScale':150} else None)
     body=wait(lambda:settings_body() if settings_body() and settings_body()['theme']==desired_theme and settings_body()['fontSize']=='24px' else None)
     submitted=requests('shell-settings-write');check('SettingsSavesOneExactProposal',len(submitted)==1 and submitted[0]['proposal']['values']==saved['values'],request=submitted,storage=saved)
     rows=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ')]
     receipts=[f for f in rows if f.get('kind')=='shell-settings-outcome' and f.get('binding')==submitted[0]['binding'] and f.get('requestId')==submitted[0]['requestId']]
     check('SettingsHasExactSavedReceipt',len(receipts)==1 and receipts[0]['status']=='Saved' and receipts[0]['snapshot']==saved,receipts=receipts)
     wait(lambda:(bar_body() or {}).get('theme')==desired_theme and (bar_body() or {}).get('textScale')=='150')
     monitors=json.loads(s.ctl('monitors','-j'));check('CommittedScaleReservesActualNativeBar',monitors[0]['reserved'][1]==72 and bar_body()['fontSize']=='24px',monitors=monitors,bar=bar_body())
     check('SettingsStorageIsPrivate',state_file.stat().st_mode&0o777==0o600 and state_file.parent.stat().st_mode&0o777==0o700)
     # Invalid text scale crosses the real authenticated transport bound to
     # this native authority, with only its supervisor-owned private storage.
     from catalog_transport import CatalogTransport
     from shell_preferences import Store as SettingsStore
     transport=CatalogTransport(client,roots);transport.settings=SettingsStore(env['XDG_STATE_HOME'])
     original=state_file.read_bytes();invalid={**saved,'values':{'theme':'night','textScale':77}}
     bad_request={'protocolVersion':3,'kind':'shell-settings-write','binding':client.bound,'requestId':'31000','proposal':invalid};refusal=transport.handle(bad_request)
     check('NativeBoundInvalidScaleRefusedAndUnapplied',refusal['status']=='Refused' and refusal['snapshot'] is None and state_file.read_bytes()==original and settings_body()['theme']==desired_theme and settings_body()['textScale']=='150',request=bad_request,receipt=refusal)
     report['nativeSettingsInvalidScale']={'request':bad_request,'receipt':refusal,'storedSHA256':sha(state_file)}
     keyboard_button('Refresh settings',28);wait(lambda:settings_body() and settings_body()['theme']==desired_theme and any(b['identity']=='settings:theme:'+desired_theme and not b['disabled'] for b in settings_body()['buttons']))
     popup_capture('settings-before-restart');check('LiveEnlargedSettingsPopupStartsBelowNativeBar',report['popupCaptures'][-1]['nativeBox'][1]>=72,nativeBox=report['popupCaptures'][-1]['nativeBox']);check('SettingsCaptureShowsActualControls',bool(report['popupCaptures'][-1]['controlRegions']) and all((c['brightPixels']>30 if CONTRAST else c['paintedPixels']>.9*c['area']) and c['area']>0 for c in report['popupCaptures'][-1]['controlRegions']))
     report['nativeSettingsBeforeRestart']={'storage':saved,'body':settings_body(),'writes':submitted,'receipt':receipts[0]}
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed')
     owned=next(row for proc,row in s.host.processes if proc is web);s.host.stop(owned,web);web.wait(timeout=5);check('SettingsFirstHostExitsNormallyForRestart',web.returncode==0)
     web=s.host.launch('warlock-settings-restarted',[str(binary),'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(backend_fixture),'--qa-exit-after-render','--qa-stay-open','--surface-experiment'],env=env);apps.append(web);log=OUTPUT/'warlock-settings-restarted.log';collector=Collector()
     wait(lambda:(projection() or {}).get('phase')=='Coherent' and (bar_body() or {}).get('theme')==desired_theme and (bar_body() or {}).get('textScale')=='150' and bar_body()['fontSize']=='24px')
     check('WholeHostRestartRestoresCommittedAppearance',stored()==saved and not requests('shell-settings-write') and not journal() and not launches(),storage=stored(),body=bar_body())
     button=wait(opener);click({'visible':0<=button['x']<800 and 0<=button['y']<72,'point':[button['x']+button['width']/2,button['y']+button['height']/2]})
     body=wait(lambda:settings_body() if settings_body() and settings_body()['theme']==desired_theme and settings_body()['fontSize']=='24px' else None)
     check('ReopenedSettingsReadsSavedValues',body['textScale']=='150' and 'Settings loaded.' in body['text'],body=body)
     if CONTRAST:
      for _ in range(len(body['buttons'])+1):
       body=settings_body();focus=next((button for button in body['buttons'] if button['id']==body['focus']),None)
       if focus and focus['identity']=='settings:theme:high-contrast':break
       key(15)
      else:raise AssertionError('Original native high contrast focus traversal')
      body=wait(lambda:settings_body() if settings_body() and settings_body()['focus']==focus['id'] and settings_body()['documentFocused'] else None)
      style=body['focusStyle'];report['nativeContrastFocus']={'body':body,'target':focus}
      check('NativeHighContrastHasReadableCommittedPalette',body['theme']=='high-contrast' and body['fontSize']=='24px' and body['palette']=={'background':'rgb(0, 0, 0)','foreground':'rgb(255, 255, 255)'},body=body)
      check('ActualKeyboardFocusHasInsetContrastOutline',style['outlineColor']=='rgb(255, 255, 0)' and style['outlineWidth']=='3px' and style['outlineOffset']=='-4px' and focus['accessibleName']=='High contrast theme',body=body)
      check('HighContrastFocusedLabelAndTargetAreVisible',focus['width']>0 and focus['height']>0 and focus['x']>=0 and focus['y']>=0 and focus['x']+focus['width']<=body['viewportWidth'] and focus['y']+focus['height']<=body['viewportHeight'] and focus['labelRect']['x']>=focus['x'] and focus['labelRect']['x']+focus['labelRect']['width']<=focus['x']+focus['width'],target=focus,body=body)
     popup_capture('settings-after-restart');check('EnlargedSettingsPopupStartsBelowNativeBar',report['popupCaptures'][-1]['nativeBox'][1]>=72,nativeBox=report['popupCaptures'][-1]['nativeBox']);report['nativeSettingsAfterRestart']={'storage':stored(),'body':body,'writes':requests('shell-settings-write')}
     if CONTRAST:
      capture=report['popupCaptures'][-1];image=pathlib.Path(capture['path']);import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
      pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();box=capture['nativeBox']
      left,top=max(0,int(box[0]+focus['x'])),max(0,int(box[1]+focus['y']));right,bottom=min(pix.get_width(),int(box[0]+focus['x']+focus['width'])),min(pix.get_height(),int(box[1]+focus['y']+focus['height']))
      white=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+i]>200 for i in range(3)))
      yellow=sum(1 for y in range(top,bottom) for x in range(left,right) if pixels[y*stride+x*channels]>200 and pixels[y*stride+x*channels+1]>200 and pixels[y*stride+x*channels+2]<80)
      check('ActualNativeHighContrastTextAndFocusPixels',white>30 and yellow>60,image=str(image),sha256=sha(image),whiteTextPixels=white,yellowFocusPixels=yellow,region=[left,top,right,bottom]);report['nativeHighContrastObserved']=True
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed');check('SettingsJourneyNeverMutatesOrLaunchesWindows',not journal() and not launches());report['nativeSettingsObserved']=True
    elif PINS:
     state_file=pathlib.Path(env['XDG_STATE_HOME'])/'warlock/taskbar.json'
     def saved_order():return json.loads(state_file.read_text())['identities'] if state_file.exists() else []
     click(wait(lambda:(projection() or {}).get('openApplications')))
     wait(lambda:field_value()=='' and (popup_body() or {}).get('focus')=='launcher-search')
     query([33,23,38,18,31],'files');keyboard_button('Pin Files');wait(lambda:saved_order()==['warlock-files'])
     query([18,32,23,20,24,19],'editor');keyboard_button('Pin Editor');wait(lambda:saved_order()==['warlock-files','warlock-editor'])
     keyboard_button('Move Editor left');wait(lambda:saved_order()==['warlock-editor','warlock-files'])
     check('NativeKeyboardPinAndReorderWriteExactlyOnce',len(requests('taskbar-pins-write'))==3 and not launches() and not journal(),requests=requests('taskbar-pins-write'),storage=json.loads(state_file.read_text()))
     check('PinStorageIsPrivate',state_file.stat().st_mode&0o777==0o600 and state_file.parent.stat().st_mode&0o777==0o700)
     report['beforeRestartOrder']=saved_order();report['firstSessionRequests']=requests('taskbar-pins-write')
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed')
     owned=next(row for proc,row in s.host.processes if proc is web);s.host.stop(owned,web);web.wait(timeout=5);check('FirstShellExitsNormallyForRestart',web.returncode==0)
     web=s.host.launch('warlock-restarted',[str(binary),'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(backend_fixture),'--qa-exit-after-render','--qa-stay-open','--surface-experiment'],env=env);apps.append(web);log=OUTPUT/'warlock-restarted.log';collector=Collector()
     def pins_on_bar():return [b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName'] in ('Open Editor','Open Files')]
     wait(lambda:len(pins_on_bar())==2 and (projection() or {}).get('phase')=='Coherent')
     buttons=pins_on_bar();check('ActualRestartRetainsBothIdentitiesInChosenOrder',[b['accessibleName'] for b in buttons]==['Open Editor','Open Files'] and saved_order()==report['beforeRestartOrder'],body=bar_body(),storage=json.loads(state_file.read_text()))
     check('RestartDoesNotReplayPinWriteOrLaunch',not requests('taskbar-pins-write') and not launches() and not journal())
     image=OUTPUT/'pins-after-restart.png';helper(['/usr/bin/grim',str(image)]);report['capture']={'path':str(image),'sha256':sha(image)}
     import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels()
     for button in buttons:
      left,top=max(0,int(button['x'])+4),max(0,int(button['y'])+4);right,bottom=min(800,int(button['x']+button['width'])-4),min(48,int(button['y']+button['height'])-4)
      bright=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>170 for c in range(3)))
      check('RestartedPinHasNativeTextPixels'+button['accessibleName'],bright>15,brightPixels=bright,region=[left,top,right,bottom])
     chosen=buttons[0];click({'visible':0<=chosen['x']<800 and 0<=chosen['y']<48,'point':[chosen['x']+chosen['width']/2,chosen['y']+chosen['height']/2]})
     wait(lambda:len(launches())==1 and 'application-launch-outcome' in text())
     check('CurrentZeroWindowPinIssuesOneIdentityBoundLaunch',launches()[0]['intent']['entry']=='warlock-editor' and len(launches())==1 and not journal(),requests=launches())
     outcomes=[json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ') and 'application-launch-outcome' in l]
     report['launchOutcomes']=outcomes;check('NativeGioSubmissionConfirmed',len(outcomes)==1 and outcomes[0]['outcome']['status']=='Submitted',outcomes=outcomes)
     report['afterRestartOrder']=saved_order();report['afterRestartLaunches']=launches();report['nativePinJourneyObserved']=True
    else:
     click(wait(lambda:(projection() or {}).get('openApplications')));wait(lambda:field_value()=='' and any(b['accessibleName']=='Open Files' for b in (popup_body() or {}).get('buttons',[])));wait(lambda:(popup_body() or {}).get('focus')=='launcher-search')
     check('NativeCatalogAndEditableSearchHaveNames',popup_body()['focus']=='launcher-search',body=popup_body())
     if PRESENTATION:popup_capture('initial')
     for code in [33,23,38,18,31]:key(code)
     wait(lambda:field_value()=='files' and any(b['accessibleName']=='Open Files' and not b['disabled'] for b in (popup_body() or {}).get('buttons',[])))
     check('CurrentQueryFiltersNativeCatalog',not any(b['accessibleName']=='Open Editor' for b in popup_body()['buttons']),body=popup_body());check('TypingIsObservationOnly',not launches() and not journal())
     if PRESENTATION:popup_capture('filtered')
     # Remove the exact selected identity after its observed current result.
     desktop.unlink();key(28);wait(lambda:'refused' in (popup_body() or {}).get('text','').lower() and field_value()=='files' and (popup_body() or {}).get('focus')=='launcher-search')
     check('NativeEnterIssuesOneIdentityBoundLaunch',len(launches())==1 and launches()[0]['intent']['entry']=='warlock-files',requests=launches())
     check('RefusalPreservesQueryAndReachableFocus',popup_body()['focus']=='launcher-search' and field_value()=='files' and any(b['accessibleName']=='Refresh applications' and not b['disabled'] for b in popup_body()['buttons']),body=popup_body())
     if PRESENTATION:popup_capture('refused')
     body=popup_body();refresh=next(b for b in body['buttons'] if b['accessibleName']=='Refresh applications' and not b['disabled']);rows=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l];import re;rect=tuple(map(int,re.search(r'configure\((\d+), (\d+), (\d+), (\d+)\)',rows[-1]).groups()));x,y=map(round,(rect[0]+refresh['x']+refresh['width']/2,rect[1]+refresh['y']+refresh['height']/2));helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     wait(lambda:field_value()=='files' and 'No matching' in (popup_body() or {}).get('text',''));key(28);check('RefreshAndNoMatchNeverLaunchReplacement',len(launches())==1,body=popup_body())
     screenshot_path=OUTPUT/'search-refused.png';helper(['/usr/bin/grim',str(screenshot_path)]);report['capture']={'path':str(screenshot_path),'sha256':sha(screenshot_path)}
     report['nativeSearchJourneyObserved']=True
     if PRESENTATION:
      popup_capture('no-match')
      for capture in report['popupCaptures']:check('ActualPopupControlPixels'+capture['stage'],bool(capture['controlRegions']) and all(r['area']>0 and r['brightPixels']>30 and r['paintedPixels']>.9*r['area'] for r in capture['controlRegions']),capture=capture)
      report['popupControlsPhysicallyObserved']=True
   elif DENSEPICKER:
    dense_height=360 if DENSEMENU else 600
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');report['keyboard']={'path':str(keyboard),'sha256':sha(keyboard)}
    def key(code):helper([str(keyboard)],f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100\nsync\n')
    def surface_body(origin):
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin='+origin+' ')]
     return rows[-1] if rows else None
    def popup_body():
     body=surface_body('popup');p=projection()
     return body if body and p and body['publication']==p['publication'] else None
    def bar_body():return surface_body('bar')
    def launches():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']=='application-launch']
    def group_button():return next((b for b in (bar_body() or {}).get('buttons',[]) if b.get('identity','').startswith('bar:group:') and not b['disabled']),None)
    def open_picker():
     button=wait(group_button);body=bar_body();box=body['actions']
     left=max(box['x'],button['x']);right=min(box['x']+box['width'],button['x']+button['width'])
     for _ in range(18 if REFLOW else 1):
      if right-left>=20:break
      helper([str(POINTER),'480',str(dense_height)],f'move {round(box["x"]+box["width"]/2)} 30\nwheel 400 0\nsleep 100\n')
      button=wait(group_button);body=bar_body();box=body['actions'];left=max(box['x'],button['x']);right=min(box['x']+box['width'],button['x']+button['width'])
     check('ActualGroupPointerIntersection',right-left>=20,button=button,body=body)
     x,y=round((left+right)/2),round(button['y']+button['height']/2)
     helper([str(POINTER),'480',str(dense_height)],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n')
     picker=wait(lambda:(projection() or {}).get('picker'))
     wait(lambda:popup_body() and len([b for b in popup_body()['buttons'] if b.get('identity','').startswith('family:')])==10)
     return picker
    def members():return [b for b in (popup_body() or {}).get('buttons',[]) if b.get('identity','').startswith('family:') and not b['disabled']]
    def selected(identity):
     body=popup_body();button=next((b for b in (body or {}).get('buttons',[]) if b.get('identity')==identity),None)
     return body if button and body['focus']==button['id'] and button['y']>=-.5 and button['y']+button['height']<=body['viewportHeight']+.5 else None
    def capture(stage):
     import re,gi
     body=popup_body();button=next(b for b in body['buttons'] if b['id']==body['focus'])
     rows=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l];box=tuple(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',rows[-1]).groups()))
     image=OUTPUT/('dense-picker-'+stage+'.png');helper(['/usr/bin/grim',str(image)])
     gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
     pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels()
     label=button['labelRect']
     left,top=max(0,int(box[0]+label['x'])),max(0,int(box[1]+label['y']))
     right,bottom=min(pix.get_width(),int(box[0]+label['x']+min(220,label['width']))),min(pix.get_height(),box[1]+box[3],int(box[1]+label['y']+label['height']))
     area=max(0,right-left)*max(0,bottom-top)
     bright=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>170 for c in range(3)))
     painted=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>15 for c in range(3)))
     packet={'stage':stage,'path':str(image),'sha256':sha(image),'region':[left,top,right,bottom],'brightPixels':bright,'paintedPixels':painted,'area':area,'body':body}
     report.setdefault('densePickerCaptures',[]).append(packet)
     check(stage+'ActualFocusedControlPixels',area>0 and bright>15 and painted>.9*area,capture=packet)
    before=len(journal());before_launches=len(launches());picker=open_picker();order=[b['identity'] for b in members()]
    check('ActualTenMemberGroupOpensWithoutLaunchOrWindowEffect',len(picker['selections'])==10 and len(journal())==before and len(launches())==before_launches,picker=picker)
    check('NativePickerHasEnlargedTextAndOverflow',popup_body()['fontSize']==('32px' if DENSEMENU else '24px') and popup_body()['scrollHeight']>popup_body()['viewportHeight'],body=popup_body())
    key(107);wait(lambda:selected(order[-1]));capture('last')
    if REFLOW:
     def pin_order(body):return [b['identity'][len('bar:pin:'):] for b in body['buttons'] if b.get('identity','').startswith('bar:pin:')]
     check('ReflowFixtureHasConfiguredOverflow',pin_order(bar_body())==reflow_ids and bar_body()['scrollWidth']>bar_body()['clientWidth'],body=bar_body())
     def resize_selected(stage,mode,identity,width,height):
      prior=projection();previous_lease=int(popup_body()['lease']);previous_order=[b['identity'] for b in popup_body()['buttons']];closed=text().count('surface-popup-closed:');reflows=text().count('view-reflow:')
      result=s.ctl('eval','hl.monitor({output="WAYLAND-1",mode="'+str(width)+'x'+str(height)+'@60",position="0x0",scale=1})')
      check(stage+'NativeOutputResizeCommand',result.strip()=='ok',result=result)
      wait(lambda:any(m['name']=='WAYLAND-1' and m['width']==width and m['height']==height for m in s.data('monitors')))
      expected_width,expected_height=min(700,width-8),min(420,height-52)
      wait(lambda:(projection() or {}).get('mode')==mode and int((popup_body() or {}).get('lease','0'))>previous_lease and (popup_body() or {}).get('viewportWidth')==expected_width and (popup_body() or {}).get('viewportHeight')==expected_height and selected(identity))
      wait(lambda:(bar_body() or {}).get('viewportWidth')==width)
      body=popup_body();check(stage+'CurrentSelectionAndOrderPersist',[b['identity'] for b in body['buttons']]==previous_order and pin_order(bar_body())==reflow_ids and len(journal())==before and len(launches())==before_launches,body=body,prior=prior,current=projection())
      import re
      boxes=[line for line in text().splitlines() if 'xdg_popup' in line and '.configure(' in line];box=tuple(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',boxes[-1]).groups()));focused=next(b for b in body['buttons'] if b['id']==body['focus'])
      check(stage+'EntireFocusedControlWithinPhysicalOutput',box[0]+focused['x']>=0 and box[1]+focused['y']>=0 and box[0]+focused['x']+focused['width']<=width and box[1]+focused['y']+focused['height']<=height,box=box,focused=focused,output=[width,height])
      check(stage+'RetiresOldInputBeforeFreshPopup',text().count('surface-popup-closed:')>closed and text().count('view-reflow:')>reflows and 'surface-popup-open: lease='+body['lease'] in text(),oldLease=previous_lease,newLease=body['lease'])
      capture(stage)
     resize_selected('picker-reflow-grow','picker',order[-1],640,480)
     resize_selected('picker-reflow-shrink','picker',order[-1],480,360)
    key(102);wait(lambda:selected('control:close'));key(108);wait(lambda:selected(order[0]));capture('first')
    for identity in order[1:]:
     key(108);body=wait(lambda:selected(identity));check('PhysicalArrowReaches'+identity,selected(identity),body=body)
    check('PhysicalArrowsReachEveryMemberWithoutReorderOrEffect',[b['identity'] for b in members()]==order and len(journal())==before,body=popup_body())
    key(102);key(108);wait(lambda:selected(order[0]))
    import re
    rows=[l for l in text().splitlines() if 'xdg_popup' in l and '.configure(' in l];box=tuple(map(int,re.search(r'configure\((-?\d+), (-?\d+), (\d+), (\d+)\)',rows[-1]).groups()))
    button=members()[0];x,y=round(box[0]+button['x']+button['width']/2),round(box[1]+button['y']+button['height']/2)
    helper([str(POINTER),'480',str(dense_height)],f'move {x} {y}\nsleep 100\nbutton 273 1\nsleep 50\nbutton 273 0\nsleep 100\n')
    wait(lambda:(projection() or {}).get('mode')=='menu' and popup_body() and any(b['accessibleName']=='Minimize' and not b['disabled'] for b in popup_body()['buttons']));capture('first-secondary-menu')
    key(1);wait(lambda:(projection() or {}).get('mode')=='closed');wait(lambda:bar_body()['focus']==group_button()['id'])
    open_picker();key(102);key(108);wait(lambda:selected(order[0]));key(127)
    wait(lambda:(projection() or {}).get('mode')=='menu' and popup_body() and any(b['accessibleName']=='Minimize' and not b['disabled'] for b in popup_body()['buttons']));capture('first-menu')
    key(1);wait(lambda:(projection() or {}).get('mode')=='closed')
    wait(lambda:bar_body()['focus']==group_button()['id'])
    open_picker();key(107);wait(lambda:selected(order[-1]))
    helper([str(keyboard)],'key 42 1\nkey 68 1\nsleep 50\nkey 68 0\nkey 42 0\nsleep 100\nsync\n')
    wait(lambda:(projection() or {}).get('mode')=='menu' and popup_body() and any(b['accessibleName']=='Minimize' and not b['disabled'] for b in popup_body()['buttons']));capture('last-menu')
    if DENSEMENU:
     def menu_selected(label):
      body=popup_body();button=next((b for b in (body or {}).get('buttons',[]) if b['accessibleName']==label and not b['disabled']),None)
      return body if button and body['focus']==button['id'] and button['y']>=0 and button['y']+button['height']<=body['viewportHeight'] else None
     menu_order=[b['identity'] for b in popup_body()['buttons']]
     check('NativeOperationMenuActuallyOverflowsAt200Percent',popup_body()['fontSize']=='32px' and popup_body()['scrollHeight']>popup_body()['viewportHeight'],body=popup_body())
     key(107);body=wait(lambda:menu_selected('Maximize'));check('NativeMenuEndRevealsLastEnabledOperation',True,body=body);capture('operation-end')
     if REFLOW:
      maximum=next(b['identity'] for b in popup_body()['buttons'] if b['accessibleName']=='Maximize')
      resize_selected('menu-reflow-grow','menu',maximum,640,480)
      resize_selected('menu-reflow-shrink','menu',maximum,480,360)
     key(102);body=wait(lambda:menu_selected('Minimize'));check('NativeMenuHomeSkipsDisabledRestore',True,body=body)
     key(103);wait(lambda:menu_selected('Maximize'));key(108);wait(lambda:menu_selected('Minimize'))
     check('NativeMenuArrowsWrapEnabledOperationsInOriginalOrder',[b['identity'] for b in popup_body()['buttons']]==menu_order and len(journal())==before,body=popup_body())
     key(15);wait(lambda:menu_selected('Close window actions'));capture('operation-close')
     key(15);wait(lambda:menu_selected('Minimize'));check('NativeMenuTabReturnsToElmSelectedOperation',len(journal())==before,body=popup_body())
    key(1);wait(lambda:(projection() or {}).get('mode')=='closed');wait(lambda:bar_body()['focus']==group_button()['id'])
    check('FirstLastMenusAndDismissalSendNoWindowEffect',len(journal())==before)
    key(28);picker=wait(lambda:(projection() or {}).get('picker'));wait(lambda:popup_body() and len(members())==10)
    check('KeyboardPrimaryActivationOpensSameTenMemberPicker',len(picker['selections'])==10 and len(journal())==before and len(launches())==before_launches,picker=picker)
    key(107);wait(lambda:selected(order[-1]));chosen=next(row for row in picker['selections'] if 'family:'+row['incarnation']==order[-1])
    key(28);wait(lambda:transaction_state()=='Committed' and (projection() or {}).get('picker') is None)
    check('ChosenDenseGroupMemberActivatesExactlyOnce',len(journal())==before+1 and journal()[-1]['intent']['incarnation']==chosen['incarnation'] and facts()['facts']['focused']==chosen['incarnation'],chosen=chosen,request=journal()[-1])
    events=control.with_suffix('.events.jsonl');before_events=len(events.read_text().splitlines()) if events.exists() else 0
    key(30)
    def chosen_input():
     delivered=[json.loads(l) for l in events.read_text().splitlines()[before_events:]] if events.exists() else []
     return delivered if any(e['kind']=='key' and e['keyval']==97 and e['window']==chosen['title'] for e in delivered) else None
    delivered=wait(chosen_input)
    check('ChosenDenseMemberReceivesRealKeyboardInput',any(e['kind']=='key' and e['keyval']==97 and e['window']==chosen['title'] for e in delivered),events=delivered,chosen=chosen)
    image=OUTPUT/'dense-picker-chosen-window.png';helper(['/usr/bin/grim',str(image)])
    import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));pixels=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels()
    chosen_window=next(row for row in facts()['facts']['windows'] if row['incarnation']==chosen['incarnation']);x,y,width,height=map(int,chosen_window['geometry'])
    left,top=max(0,x+10),max(100,y+10);right,bottom=min(pix.get_width(),x+width-10),min(pix.get_height(),y+height-10)
    green=sum(1 for py in range(top,bottom) for px in range(left,right) if pixels[py*stride+px*channels+1]>100 and pixels[py*stride+px*channels+1]>pixels[py*stride+px*channels]+30 and pixels[py*stride+px*channels+1]>pixels[py*stride+px*channels+2]+30)
    report['chosenWindowCapture']={'path':str(image),'sha256':sha(image),'chosen':chosen_window,'region':[left,top,right,bottom],'greenPixels':green}
    check('ChosenDenseWindowIsPhysicallyPresented',green>1000,capture=report['chosenWindowCapture'])
    report['nativeDensePickerObserved']=True
    if DENSEMENU:report['nativeDenseMenuObserved']=True
    if REFLOW:report['nativePopupReflowObserved']=True
   elif FOCUS:
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
    report['keyboard']={'path':str(keyboard),'sha256':sha(keyboard)}
    def key(code):helper([str(keyboard)],f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100\nsync\n')
    before=len(journal());before_focus=facts()['facts']['focused'];click(initial)
    picker=wait(lambda:(projection() or {}).get('picker'))
    wait(lambda:'surface-focus-applied:' in text())
    check('ActualGroupOpensWithoutWindowMutation',len(journal())==before and len(picker['selections'])==2,picker=picker)
    def popup_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=popup ')]
     return rows[-1] if rows else None
    body=wait(popup_body);first_focus=body['focus'];check('NativePopupFocusNamesAnEligibleMember',first_focus in [row['domId'] for row in picker['selections']],body=body)
    key(15);next_body=wait(lambda:next((b for b in [popup_body()] if b and b['focus']!=first_focus),None))
    check('TabRemainsInsidePopup',next_body['focus'] in [b['id'] for b in next_body['buttons'] if not b['disabled']],body=next_body)
    order=[b['id'] for b in next_body['buttons'] if not b['disabled']]
    for _ in range(len(order)):
     old=popup_body()['focus'];expected=order[(order.index(old)+1)%len(order)];key(15)
     wrapped=wait(lambda:next((b for b in [popup_body()] if b and b['focus']==expected),None))
     check('ForwardTabWrapsInDocumentedPopupOrder',wrapped['focus']==expected,expected=expected,actual=wrapped['focus'])
    old=popup_body()['focus'];expected=order[(order.index(old)-1)%len(order)]
    helper([str(keyboard)],'key 42 1\nkey 15 1\nsleep 50\nkey 15 0\nkey 42 0\nsleep 100\nsync\n')
    reverse=wait(lambda:next((b for b in [popup_body()] if b and b['focus']==expected),None))
    check('ShiftTabTraversesPopupInReverse',reverse['focus']==expected,expected=expected,actual=reverse['focus'])
    key(1);wait(lambda:(projection() or {}).get('mode')=='closed' and (projection() or {}).get('phase')=='Coherent')
    after_focus=facts()['facts']['focused'];report['focusReturn']={'before':before_focus,'after':after_focus,'bar':projection()}
    events=control.with_suffix('.events.jsonl');before_events=len(events.read_text().splitlines()) if events.exists() else 0
    key(30);delivered=[json.loads(l) for l in events.read_text().splitlines()[before_events:]] if events.exists() else [];report['keyboardRecipients']=delivered
    check('EscapeDismissalDoesNotDispatchWindowEffect',len(journal())==before)
    check('EscapeRestoresOriginalNativeRecipient',after_focus==before_focus and any(e['kind']=='key' and e['keyval']==97 and e['window']=='ELM-AUTHORITY-FIXTURE' for e in delivered),before=before_focus,after=after_focus,events=delivered)
    click(wait(lambda:group('Choose a window from')));picker=wait(lambda:(projection() or {}).get('picker'));selected=next(x for x in picker['selections'] if x['title']=='ELM-ACTIVATION-PEER');click(selected)
    wait(lambda:transaction_state()=='Committed' and (projection() or {}).get('picker') is None)
    check('ChosenGroupMemberActuallyActivates',facts()['facts']['focused']==selected['incarnation'] and len(journal())==before+1 and journal()[-1]['intent']['incarnation']==selected['incarnation'],request=journal()[-1])
   else:
    # Current real taskbar primary action, before adding any fault.
    click(initial);wait(lambda:transaction_state()=='Committed' and current_window()['minimized']);check('TaskbarMinimizeActuallyCommits',journal()[-1]['intent']['operation']=='minimize')
    def find_broker():
     rows=[]
     for row in s.host.descendants():
      try:args=pathlib.Path('/proc/'+str(row['pid'])+'/cmdline').read_bytes().split(b'\0')
      except FileNotFoundError:continue
      if str(ROOT/'adapter/daemon.py').encode() in args and int(pathlib.Path('/proc/'+str(row['pid'])+'/stat').read_text().rsplit(')',1)[1].split()[1])==web.pid:rows.append({'pid':row['pid'],'start':start_time(row['pid'])})
     return rows[0] if len(rows)==1 else None
    broker=wait(find_broker);report['broker']=broker;restore=wait(lambda:group('Restore'));pause(True);before=len(journal());click(restore);screenshot('Pending');check('PendingDoesNotCommitOrDuplicate',current_window()['minimized'] and len(journal())==before+1)
    # Change native truth independently while its original UI intent is held.
    private_effect('restore');pause(False);wait(lambda:transaction_state()=='Refused');screenshot('Refused');check('RefusalProducesOneRestoreRequest',len(journal())==before+1 and journal()[-1]['intent']['operation']=='restore')
    private_effect('minimize');restore=wait(lambda:group('Restore'));pause(True);before=len(journal());click(restore);wait(lambda:transaction_state()=='Pending')
    # Genuine transport loss makes the issued request Unknown; no invented timer.
    os.kill(broker['pid'],signal.SIGTERM);pause(False);wait(lambda:transaction_state()=='Unknown');screenshot('Unknown');check('UnknownIsPersistentAndNeverAutoRetried',len(journal())==before+1 and current_window()['minimized'])
    body=feedback('Unknown');check('DisconnectedFeedbackNamesReachableRecovery','Reconnect' in body['feedback']['text'] and any(b['accessibleName'].startswith('Reconnect') and not b['disabled'] for b in body['buttons']))
    reconnect=next(b for b in body['buttons'] if b['accessibleName'].startswith('Reconnect') and not b['disabled']);x,y=map(round,(reconnect['x']+reconnect['width']/2,reconnect['y']+reconnect['height']/2));helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n');wait(lambda:(projection() or {}).get('phase')=='Coherent');check('ReconnectReadsWithoutReplayingRestore',len(journal())==before+1 and current_window()['minimized'])
    body=feedback('Unknown');refresh=next(b for b in body['buttons'] if b['accessibleName'].startswith('Refresh window status') and not b['disabled']);x,y=map(round,(refresh['x']+refresh['width']/2,refresh['y']+refresh['height']/2));helper([str(POINTER),'800','600'],f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n');check('RefreshQueuesNoSecondWindowEffect',len(journal())==before+1)
    wait(lambda:(projection() or {}).get('phase')=='Coherent');check('ReadOnlyRecoveryPreservesUnknownAndNoReplay',transaction_state()=='Unknown' and len(journal())==before+1 and current_window()['minimized'])
   if RETIRE_OPENER:
    peer=next(w for w in membership if w['label']=='ELM-ACTIVATION-PEER')
    before_peer=next(w for w in native_facts['facts']['windows'] if w['incarnation']==peer['incarnation'])
    after_peer=next(w for w in facts()['facts']['windows'] if w['incarnation']==peer['incarnation'])
    check('NoScratchpadOrWorkspaceTransfer',all(before_peer[k]==after_peer[k] for k in ['workspace','monitor']),before={k:before_peer[k] for k in ['workspace','monitor']},after={k:after_peer[k] for k in ['workspace','monitor']})
   else:
    if MEMBERSHIP:check('OnlyExplicitSpecialWorkspaceFixtureMoved',len(facts()['facts']['windows'])==5 and any(row['incarnation']==c and int(row['workspace'])<0 for row in facts()['facts']['windows']),nativeFacts=facts())
    elif DRAG:check('OnlyExplicitNativeGestureCanChangeOutput',all(g['end']['state']=='idle' for g in report['gestures']),gestures=report['gestures'])
    else:check('NoScratchpadOrWorkspaceTransfer',not facts()['facts']['windows'] and report['beforeControlledRetirements']['facts']['windows'] if CHORD else current_window()['workspace']==initial_workspace,nativeWorkspace='controlled original roots retired' if CHORD else current_window()['workspace'],originalWorkspace=initial_workspace)
   report['nativeFeedbackObserved']=not FOCUS and not CATALOG and not TASKVIEW and not PRIMARY and not SWITCHER and not CHORD;report['nativeFocusJourneyObserved']=FOCUS;check('EveryRegisteredHelperExitedNormally',all(r['exitCode']==0 for r in report['helpers']));report['passed']=True
  finally:
   if paused:pause(False)
   if drag_writer is not None:
    os.close(drag_writer);drag_writer=None
   if drag_pointer is not None:
    drag_pointer.wait(timeout=5);check('PersistentPointerNormalExit',drag_pointer.returncode==0)
   if chord_writer is not None:
    os.close(chord_writer);chord_writer=None
   if chord_keyboard is not None:
    chord_keyboard.wait(timeout=5);check('PersistentKeyboardNormalExit',chord_keyboard.returncode==0)
   if notification_producer is not None and notification_producer.poll() is None:
    notification_serial+=1;notification_control.write_text(json.dumps({"serial":notification_serial,"op":"quit"}));notification_producer.wait(timeout=5)
   if FILES and 'files_process' in locals() and 'files_native_status' in locals() and files_process.poll() is None:
    helper(['/usr/bin/qs','kill','--id',files_native_status['instance']]);files_process.wait(timeout=5)
   for proc in reversed(apps):
    if proc.poll() is None:
     if proc is fixture:fixture_control('quit');proc.wait(timeout=5)
     else:owned=next(row for p,row in s.host.processes if p is proc);s.host.stop(owned,proc);proc.wait(timeout=5)
    check('OwnedClientNormalExit',proc.returncode==0 or (ACCESSIBILITY and proc is at_registry and proc.returncode==-signal.SIGTERM),pid=proc.pid,exitCode=proc.returncode,expectedRegistryStop=bool(ACCESSIBILITY and proc is at_registry and proc.returncode==-signal.SIGTERM))
   if loaded:s.guard();check('OwningPluginUnloads',s.ctl('plugin','unload',pair['plugin']['path']).strip()=='ok');loaded=False
   registered={row['pid'] for _,row in s.host.processes}
   for row in reversed([r for r in s.host.descendants() if r['pid'] not in registered]):s.host.stop(row)
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost']=s.evidence if s else None
report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed']=report['passed'] and report['cleanupPassed']
report['runtimeEvidenceDirectory']=str(OUTPUT);report['runnerSHA256']=sha(__file__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
