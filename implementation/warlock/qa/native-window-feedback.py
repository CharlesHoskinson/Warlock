"""ELM-UI-007 restore feedback on the real private Wayland/Elm/native path.

Reuse immutable ABI/runtime by reference; no preview, supervisor or new source
lineage. Native/AT acceptance remain separate, with AT explicitly outstanding.
"""
import hashlib,importlib.util,json,os,pathlib,signal,subprocess,sys,time,traceback
UNAVAILABLE=sys.argv[1:]==['--adapter-unavailable']
LIVE=sys.argv[1:]==['--live-motion']
MOTION=sys.argv[1:]==['--reduced-motion'] or LIVE
LAYER=sys.argv[1:]==['--layer-appearance']
TRANSFER=sys.argv[1:]==['--transfer-workspace']
IME=sys.argv[1:]==['--ime']
ACCESSIBILITY=sys.argv[1:]==['--accessibility']
CONTRAST=sys.argv[1:]==['--high-contrast']
DRAG=sys.argv[1:]==['--drag-ownership']
KEYBOARD=sys.argv[1:]==['--keyboard-shell']
ATTENTION=sys.argv[1:]==['--attention']
JUMP=sys.argv[1:]==['--jump-lists']
FILES=sys.argv[1:]==['--files']
SYSTEM=sys.argv[1:]==['--system-menu']
NOTIFICATIONS=sys.argv[1:]==['--notifications']
SETTINGS=LAYER or sys.argv[1:]==['--settings'] or CONTRAST
PLACEMENT=sys.argv[1:]==['--snap-placement']
SNAP=sys.argv[1:]==['--snap-chooser'] or PLACEMENT
REFLOW=sys.argv[1:]==['--popup-reflow']
DENSEMENU=sys.argv[1:]==['--dense-menu'] or REFLOW
DENSEPICKER=sys.argv[1:]==['--dense-picker'] or DENSEMENU
DENSE=sys.argv[1:]==['--dense-taskbar']
SMALL=DENSE or DENSEPICKER
PINMENUS=sys.argv[1:]==['--pinned-menus'] or DENSE or SNAP
PRIMARYKEY=sys.argv[1:]==['--taskbar-primary-keyboard']
PRIMARY=sys.argv[1:]==['--taskbar-primary'] or PRIMARYKEY or PINMENUS or ATTENTION or MOTION
PRE_READY_RETIRE=sys.argv[1:]==['--switcher-pre-ready-retirement']
MEMBERSHIP=sys.argv[1:]==['--switcher-membership'] or PRE_READY_RETIRE
CHORD=sys.argv[1:]==['--switcher-chord'] or MEMBERSHIP
SWITCHER=sys.argv[1:]==['--switcher'] or ACCESSIBILITY
NAV=sys.argv[1:]==['--workspace-navigation'];FOCUS=sys.argv[1:]==['--taskbar-focus'] or DENSEPICKER or KEYBOARD;PRESENTATION=sys.argv[1:]==['--launcher-presentation'];SEARCH=sys.argv[1:]==['--launcher-search'] or PRESENTATION or IME;PINS=sys.argv[1:]==['--taskbar-pins'];CATALOG=UNAVAILABLE or SEARCH or PINS or PINMENUS or REFLOW or SETTINGS or NOTIFICATIONS or SYSTEM or FILES or JUMP or KEYBOARD or PRIMARYKEY;RETIRE_OPENER=sys.argv[1:]==['--task-view-retired-opener'];TASKVIEW=sys.argv[1:]==['--task-view'] or NAV or RETIRE_OPENER or TRANSFER;assert not sys.argv[1:] or FOCUS or CATALOG or TASKVIEW or PRIMARY or SWITCHER or CHORD or DRAG
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
if PLACEMENT or TRANSFER:
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
  qualified_core=focus_core
  if 'pinCoreReport' in native_pair:
   pin=native_pair['pinCoreReport'];pin_path=REPO/pin['report'];assert sha(pin_path)==pin['reportSHA256'];pin_core=json.loads(pin_path.read_text())
   assert pin_core['passed'] and pin_core['existingPublicHeadersUnchanged'] and pin_core['existingObjectLayoutsUnchanged'] and pin_core['owningHeaders']==focus_core['owningHeaders']
   assert sha(ROOT/'native/core/ConfigActions.cpp')==pin_core['sourceSHA256'] and pin_core['ancestor']=={'report':str(focus_path),'reportSHA256':sha(focus_path)}
   assert all(sha(p)==h for p,h in pin_core['dependencies'].items()) and all(sha(p)==h for p,h in pin_core['linkDependencies'].items())
   qualified_core=pin_core
  if 'maxCoreReport' in native_pair:
   maximum=native_pair['maxCoreReport'];max_path=REPO/maximum['report'];assert sha(max_path)==maximum['reportSHA256'];max_core=json.loads(max_path.read_text())
   assert max_core['passed'] and max_core['existingPublicHeadersUnchanged'] and max_core['existingObjectLayoutsUnchanged'] and max_core['owningHeaders']==pin_core['owningHeaders']
   assert sha(ROOT/'native/core/FullscreenController.cpp')==max_core['sourceSHA256'] and all(sha((max_path.parent/'owning-headers'/('src/desktop/state/ViewHitTester.cpp' if p=='native/core/ViewHitTester.cpp' else 'src/desktop/view/Window.cpp')) if 'sceneCoreReport' in native_pair and p in ('native/core/ViewHitTester.cpp','native/core/Window.cpp') else ROOT/p)==h for p,h in max_core['sourceHashes'].items()) and max_core['ancestor']=={'report':str(pin_path),'reportSHA256':sha(pin_path)}
   assert all(sha(p)==h for p,h in max_core['dependencies'].items()) and all(sha(p)==h for p,h in max_core['linkDependencies'].items())
   qualified_core=max_core
  if 'sceneCoreReport' in native_pair:
   scene=native_pair['sceneCoreReport'];scene_path=REPO/scene['report'];assert sha(scene_path)==scene['reportSHA256'];scene_core=json.loads(scene_path.read_text())
   assert scene_core['passed'] and scene_core['existingPublicHeadersUnchanged'] and scene_core['existingObjectLayoutsUnchanged'] and scene_core['existingStrongExportsPreserved'] and scene_core['owningHeaders']==max_core['owningHeaders']
   expected_ancestor={'report':str(max_path),'reportSHA256':sha(max_path)}
   scene_base=scene_core
   seen_ancestors=set()
   while scene_base['ancestor']!=expected_ancestor:
    child=scene_base;parent_path=pathlib.Path(child['ancestor']['report'])
    assert str(parent_path) not in seen_ancestors and len(seen_ancestors)<2;seen_ancestors.add(str(parent_path))
    assert sha(parent_path)==child['ancestor']['reportSHA256']
    scene_base=json.loads(parent_path.read_text());assert scene_base['passed'] and sha(scene_base['binary'])==scene_base['binarySHA256']
    assert scene_base['existingPublicHeadersUnchanged'] and scene_base['existingObjectLayoutsUnchanged'] and scene_base['existingStrongExportsPreserved']
    assert child['owningHeaders']==scene_base['owningHeaders']
    changes=set(child.get('changedSources',['native/core/KeybindManager.cpp','native/core/GestureKeyPolicy.hpp']))
    assert changes in ({'native/core/KeybindManager.cpp','native/core/GestureKeyPolicy.hpp'},{'native/core/Window.cpp','native/core/CaptionGesturePolicy.hpp'})
    assert set(child['sourceHashes'])==set(scene_base['sourceHashes'])|changes
    assert all(child['sourceHashes'][p]==h for p,h in scene_base['sourceHashes'].items() if p not in changes)
    assert all(sha(p)==h for p,h in {**scene_base['dependencies'],**scene_base['linkDependencies']}.items())
   assert 'native/core/Window.cpp' in scene_core['sourceHashes'] or sha(ROOT/'native/core/Window.cpp')==max_core['sourceHashes']['native/core/Window.cpp']
   assert scene_base['ancestor']==expected_ancestor and all(sha(ROOT/p)==h for p,h in scene_core['sourceHashes'].items())
   assert all(sha(p)==h for p,h in scene_core['dependencies'].items()) and all(sha(p)==h for p,h in scene_core['linkDependencies'].items())
   qualified_core=scene_core
  assert native_pair['pair']['core']=={'path':qualified_core['binary'],'sha256':qualified_core['binarySHA256']}
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
OUT=ROOT/'qa/runs'/(('native-adapter-unavailable-' if UNAVAILABLE else 'native-layer-appearance-' if LAYER else 'native-primary-keyboard-' if PRIMARYKEY else 'native-live-motion-' if LIVE else 'native-reduced-motion-' if MOTION else 'native-transfer-workspace-' if TRANSFER else 'native-ime-' if IME else 'native-accessibility-' if ACCESSIBILITY else 'native-high-contrast-' if CONTRAST else 'native-drag-ownership-' if DRAG else 'native-keyboard-shell-' if KEYBOARD else 'native-attention-' if ATTENTION else 'native-jump-lists-' if JUMP else 'native-files-' if FILES else 'native-system-menu-' if SYSTEM else 'native-notifications-' if NOTIFICATIONS else 'native-settings-' if SETTINGS else 'native-snap-placement-' if PLACEMENT else 'native-snap-chooser-' if SNAP else 'native-dense-picker-' if DENSEPICKER else 'native-dense-taskbar-' if DENSE else 'native-pinned-menus-' if PINMENUS else 'native-switcher-membership-' if MEMBERSHIP else 'native-switcher-chord-' if CHORD else 'native-switcher-' if SWITCHER else 'native-primary-' if PRIMARY else 'native-workspace-navigation-' if NAV else 'native-task-view-' if TASKVIEW else 'native-pins-' if PINS else 'native-search-' if SEARCH else 'native-taskbar-focus-' if FOCUS else 'native-feedback-')+str(time.time_ns()));OUT.mkdir(parents=True)
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
report={'schema':1,'requirements':['ELM-UI-007'],'scenarios':['restore-pending','restore-refused','restore-unknown'],'scope':'Actual pointer/Elm/native effect feedback and private compositor pixels; no AT/IME/full release acceptance','nativeFeedbackObserved':False,'nativeAcceptance':False,'assistiveTechnologyAccepted':False,'fullReleaseAccepted':False,'mainDesktopActions':False,'passed':False,'checks':[],'sourceInputs':{str(p.relative_to(ROOT)):sha(p) for folder in ['src','native','adapter','assets'] for p in (ROOT/folder).iterdir() if p.is_file()},'pair':pair,'nativeHost':{'path':str(binary),'sha256':sha(binary),'heldBuild':str(build_path),'heldBuildSHA256':sha(build_path)},'runtimeByReference':{'root':str(RUNTIME),'hostSHA256':sha(RUNTIME/'candidate_host.py')},'helpers':[],'nativeFixtures':[]};s=None;loaded=False;apps=[];unavailable_owner=None;notification_producer=None;broker=None;paused=False;sequence=0;chord_keyboard=None;chord_writer=None;drag_pointer=None;drag_writer=None
if focus_host:report['focusHostAdaptation']=focus_host
if retirement_fixture:report['retirementFixture']=retirement_fixture
if primary_fixture:report['primaryFixture']=primary_fixture
if SEARCH:report.update(requirements=['ELM-UI-005','ELM-UX-029'],scenarios=['search-no-match','search-race','search-refused','launcher-refused'],scope='Actual current query and private catalog, native typing/Enter refusal and no duplicate launch; AT/IME and popup physical presentation acceptance remain pending',popupPresentationAccepted=False)
if KEYBOARD:report.update(requirements=['ELM-UX-023'],scenarios=['ux-023','keyboard-launcher','keyboard-taskbar-groups','keyboard-switcher','keyboard-task-view','keyboard-snap-chooser','keyboard-menus','keyboard-settings','keyboard-notifications','keyboard-jump-lists'],scope='Original physical keyboard-only migrated-surface journey; no pointer helper, native focus/effect/readback. Applicable AT and independent original acceptance remain separate.',nativeKeyboardShellObserved=False,keyboardSurfaces=[])
if ATTENTION:report.update(requirements=['ELM-UX-009'],scenarios=['ux-009'],scope='Actual GTK activation request while inactive, native bound/revisioned urgency read, distinct visible taskbar indicators and accessible DOM state. Actual AT and independent acceptance remain open.',nativeAttentionObserved=False)
if JUMP:report.update(requirements=['ELM-UX-010'],scenarios=['ux-010','jump-list-recent-identity'],scope='Physical private native jump list: catalog-declared actions, exact application-bound local XBEL file, actual GIO argv; foreign entries absent. Native negative admission is separate adapter evidence, AT and independent acceptance remain open.',nativeJumpListsObserved=False)
if FILES:report.update(requirements=['ELM-UX-033'],scenarios=['ux-033'],scope='Actual installed Files explorer in private home/runtime; physical Elm collection choice, exact native instance reuse, location readback, no unchanged file operation source edits. Independent/AT and other-workspace summon acceptance remain open.',nativeFilesObserved=False)
if SYSTEM:report.update(requirements=['ELM-UX-032'],scenarios=['ux-032'],scope='Actual isolated native menu with current private PipeWire volume and login1 session/power capabilities, unavailable network, physical keyboard changes, readback, confirmation and pixels; real hardware, AT and independent acceptance remain open.',nativeSystemMenuObserved=False)
if UNAVAILABLE:report.update(requirements=['ELM-UI-010'],scenarios=['announce-adapter unavailable'],scope='Actual private native occupied notification service, physical keyboard refresh/recovery, duplicated real matched read receipts, exact polite owner/correlation and retained focused node; all-provider native matrix, speech/braille and independent acceptance remain open.',nativeAdapterUnavailableObserved=False)
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
if PRIMARYKEY:report.update(scope='Actual physical keyboard-only primary activation/minimize/restore, native receipts/pixels and actual app-key recipients, MRU/desktop succession, no pointer helper and normal cleanup. Native AT and independent original acceptance remain open.',nativeKeyboardPrimaryJourneyObserved=False)
if PINMENUS:report.update(requirements=['ELM-UI-008','ELM-UX-023'],scenarios=['menu-invocation','keyboard-menus'],scope='Actual current running pin, native secondary click/Menu/Shift-F10 menus and existing minimize/restore path; dense/enlarged-text, AT and independent acceptance remain open',nativePinnedMenusObserved=False)
if SNAP:report.update(requirements=['ELM-UX-019','ELM-UX-020'],scenarios=['ux-019','ux-020'],scope='Actual native snap chooser presentation/keyboard/output-scale invalidation only; native snap placement authority and accepted half-work-area oracle remain required',nativeSnapChooserObserved=False)
if LAYER:report.update(requirements=['ELM-UX-030','ELM-UX-027'],scenarios=['ux-030','ux-027'],scope='Native keyboard appearance flag edit/save and whole-host restart, exact Saved receipt, invalid scale refusal and physical controls at enlarged text. Applicable AT, all surfaces and independent acceptance remain separate.')
if CONTRAST:report.update(requirements=['ELM-UX-027'],scenarios=['ux-027'],scope='Actual native high contrast appearance at enlarged text, named keyboard focus/pixels and committed persistence/restart; all-surface/theme/scale original qualification and native AT remain open.')
if PLACEMENT:report.update(scope='Actual GUI snap submission through shared allocator/custody/native geometry authority, exact half-work-area readback/pixels and stale output refusal; original independent/AT release acceptance remains separate',nativeSnapPlacementObserved=False)
if DENSE:report.update(requirements=['ELM-UI-008'],scenarios=['overflow-first-last','overflow-resize','menu-invocation'],scope='Actual small native output, enlarged text, configured overflowing pins, physical keyboard/wheel/menu traversal and output resize; AT and independent review remain open',nativeDenseTaskbarObserved=False)
if DENSEPICKER:report.update(requirements=['ELM-UI-008','ELM-UI-004'],scenarios=['overflow-first-last','overflow-resize','menu-invocation','taskbar-group'],scope='Actual ten-root native enlarged-text picker arrow/endpoints, first/last menus and identity-bound selection/input; browser resize continuity is separate; native popup reflow, AT and independent review remain open',nativeDensePickerObserved=False)
if DENSEMENU:report.update(requirements=['ELM-UI-008'],scenarios=['overflow-first-last','menu-invocation'],scope='Actual ten-root 480x360 native output at 200% text; overflow of current three-operation menu, typed endpoint/arrows/disabled/Tab/Escape and operation-label pixels; renderer capacity/growth/blur are component observations; AT/independent and native popup reflow remain open',nativeDenseMenuObserved=False)
if REFLOW:report.update(requirements=['ELM-UI-008'],scenarios=['overflow-resize'],scope='Actual 18 configured overflowing pins and ten-root picker, 200% text, physical picker/menu selection across native output geometry changes with fresh leases and pixels; applicable AT/independent acceptance remains separate',nativePopupReflowObserved=False)
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
if MOTION:LUA=LUA.replace(b'animations={enabled=false}',b'animations={enabled=true}')
if SMALL:LUA=LUA.replace(b'800x600',b'480x360' if DENSEMENU else b'480x600')
if ATTENTION:LUA+=b'hl.config({misc={focus_on_activate=false}})\n'
if CHORD or KEYBOARD or DRAG:LUA+=(ROOT/'native/switcher-bindings.lua').read_bytes()
if KEYBOARD or PRIMARYKEY or DRAG:LUA+=(ROOT/'native/shell-bindings.lua').read_bytes()
if DRAG:
 LUA+=b'hl.monitor({output="WAYLAND-2",mode="800x600@60",position="800x0",scale=1})\n'
 report.update(requirements=['ELM-UX-021'],scenarios=['ux-021'],scope='Actual native move/resize input across taskbar and two outputs; native controller owner/serial, real blocked shell shortcut and competing native effect, one end per gesture. No caption/edge, AT, touch/tablet or independent acceptance inferred.')
if ACCESSIBILITY:report.update(requirements=['ELM-UX-025'],scenarios=['actual-surface-at'],scope='Actual private GTK/WebKit taskbar and switcher AT-SPI tree/states/focus and real Orca observations with physical input; independent original acceptance remains separate.')
if IME:report.update(requirements=['ELM-UX-028'],scenarios=['ime-spike-commit','ime-spike-cancel'],scope='Actual installed private Fcitx Unicode preedit/candidate keyboard traversal/commit/cancel through GTK/WebKit in integrated launcher; query/caret/native effects observed at original deadline. Independent original acceptance remains separate.')
if TRANSFER:report.update(requirements=['ELM-UX-018'],scenarios=['ux-018','transfer-refused','transfer-accepted'],scope='Actual physical Task View transfers, native pinned refusal/source retention, matching committed receipts and observed existing/empty workspace membership under original deadlines. Independent and AT acceptance separate.')
if MOTION:report.update(requirements=['ELM-UX-022'],scenarios=['ux-022'],scope='Original physical minimize/restore and shell overlay recording with actual private GTK reduced-motion setting and compositor animations enabled. Exact native settled-state traces and physical presentation; independent acceptance separate.')
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
 # Each nested Wayland output receives its actual parent configure size. The
 # original two-output oracle requires two 800x600 outputs, not a 1600x1000
 # parent that overrides both monitor rules. Other journeys keep their parent.
 with host.PrivateHyprSession(OUTPUT,dict(os.environ),800 if DRAG else 1600,600 if DRAG else 1000,LUA,mesa_vendor=True) as s:
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
   if MOTION:
    gtk_root=s.host.runtime/'motion-config';(gtk_root/'gtk-3.0').mkdir(parents=True,mode=0o700)
    gtk_settings=gtk_root/'gtk-3.0/settings.ini';gtk_settings.write_text('[Settings]\ngtk-enable-animations=false\n');env['XDG_CONFIG_HOME']=str(gtk_root)
    report['nativeMotionPreference']={'path':str(gtk_settings),'sha256':sha(gtk_settings),'mainDesktopUnchanged':True,'compositorAnimationsEnabled':True,'fixture':'Actual GtkSettings gtk-enable-animations property selected in the QA-only host because the unchanged protected launcher forces GSETTINGS_BACKEND=memory; no fake motion frame.'}
   if LIVE:
    motion_control=s.host.runtime/'motion-source.control';motion_control.write_text('R\n');motion_control.chmod(0o600)
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
   if IME:
    config_home=pathlib.Path(env['XDG_CONFIG_HOME']);assert config_home.resolve().is_relative_to(s.host.runtime.resolve());profile=config_home/'fcitx5/profile';profile.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    profile.write_text('[Groups/0]\nName=Default\nDefault Layout=us\nDefaultIM=keyboard-us\n[Groups/0/Items/0]\nName=keyboard-us\nLayout=\n[GroupOrder]\n0=Default\n');profile.chmod(0o600)
    fcitx_env=dict(env,XDG_DATA_DIRS='/usr/local/share:/usr/share');fcitx_env.pop('WAYLAND_DEBUG',None)
    fcitx=s.host.launch('ime-fcitx',['/usr/bin/fcitx5','-D','--disable','all','--enable','dbus,dbusfrontend,keyboard,unicode,classicui,wayland','-u','classicui','--verbose','key_trace=5'],env=fcitx_env);apps.append(fcitx)
    wait(lambda:fcitx.poll() is not None or 'Loaded addon dbusfrontend' in (OUTPUT/'ime-fcitx.log').read_text(errors='replace'))
    check('PrivateInstalledFcitxRemainsAlive',fcitx.poll() is None)
    owner_raw=helper(['/usr/bin/gdbus','call','--session','--dest','org.freedesktop.DBus','--object-path','/org/freedesktop/DBus','--method','org.freedesktop.DBus.GetConnectionUnixProcessID','org.fcitx.Fcitx5'])
    check('IMEBusOwnerIsExactOwnedProcess',str(fcitx.pid) in owner_raw,pid=fcitx.pid,owner=owner_raw)
    env['GTK_IM_MODULE']='fcitx';s.env['GTK_IM_MODULE']='fcitx'
    module=pathlib.Path('/usr/lib/gtk-3.0/3.0.0/immodules/im-fcitx5.so')
    report['imeFixture']={'binary':'/usr/bin/fcitx5','binarySHA256':sha('/usr/bin/fcitx5'),'gtkModule':str(module),'gtkModuleSHA256':sha(module),'profile':str(profile),'profileSHA256':sha(profile),'sessionBus':env['DBUS_SESSION_BUS_ADDRESS'],'systemBusRemainsRefusing':True,'installedAddonsSelected':['dbus','dbusfrontend','keyboard','unicode','classicui','wayland'],'sourceReference':'https://fcitx-im.org/wiki/Tips_and_Tricks','nativeIMEObserved':False}
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
   if UNAVAILABLE:
    unavailable_ready=OUTPUT/'notification-owner.ready';unavailable_stop=OUTPUT/'notification-owner.stop'
    unavailable_owner=s.host.launch('notification-name-owner',['/usr/bin/python3','-B',str(ROOT/'qa/notification-unavailable-owner.py'),str(unavailable_ready),str(unavailable_stop)],env=env);apps.append(unavailable_owner)
    wait(lambda:unavailable_ready.exists() or unavailable_owner.poll() is not None)
    check('PrivateActualNotificationNameOwnerReady',unavailable_owner.poll() is None and json.loads(unavailable_ready.read_text())['available'])
    backend_fixture=OUTPUT/'unavailable-backend.py'
    backend_fixture.write_text('import json,sys\nfrom pathlib import Path\nsys.path.insert(0,'+repr(str(ROOT/'adapter'))+')\nimport daemon\nassert Path(sys.argv[1]).read_text()=='+repr(config_path.read_text())+'\nsys.argv[1]='+repr(str(broker_config))+'\noriginal=daemon.send\ndef send(value):\n original(value)\n if value.get("kind")=="notification-snapshot":original(value)\ndaemon.send=send\nraise SystemExit(daemon.run())\n')
    report['unavailableFixture']={'owner':str(ROOT/'qa/notification-unavailable-owner.py'),'ownerSHA256':sha(ROOT/'qa/notification-unavailable-owner.py'),'backend':str(backend_fixture),'backendSHA256':sha(backend_fixture),'scope':'Another actual private bus service owns the name; duplicate only the original real read receipt, never synthesize unavailable facts or repeat an action.'}
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
   web=s.host.launch('warlock',['%s'%binary,'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(backend_fixture if CATALOG or CHORD else ROOT/'adapter/daemon.py'),'--qa-exit-after-render','--qa-stay-open','--surface-experiment',*(['--qa-motion-control',str(motion_control)] if LIVE else ['--qa-reduced-motion'] if MOTION else []),*(['--text-scale','2' if DENSEMENU else '1.5'] if SMALL else [])],env=env);apps.append(web);log=OUTPUT/'warlock.log';collector=Collector()
   def text():
    raw=log.read_text(errors='replace')
    # The live file may end in a producer's unfinished JSON record. Observe
    # complete lines only; malformed completed records still fail normally.
    return raw[:raw.rfind('\n')+1]
   def projection():return collector.read(text())
   def group(operation):
    p=projection();return next((g for g in p['groups'] if (FOCUS or NAV or g['title']==('ELM-ACTIVATION-PEER' if PRIMARY else 'ELM-AUTHORITY-FIXTURE')) and g['label'].startswith(operation+' ') and not g['disabled']),None) if p and p['phase']=='Coherent' else None
   def journal():return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']=='window-effect']
   if MOTION:
    import socket,struct
    motion_socket=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);client.verify_process();client.verify_paths();motion_socket.connect(str(client.path.with_name('.socket2.sock')))
    event_pid,event_uid,_=struct.unpack('3i',motion_socket.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));check('MotionTraceHasActualNativePeer',event_pid==native['pid'] and event_uid==os.getuid());motion_socket.setblocking(False)
    motion_buffer=b'';motion_traces=[];motion_log=OUTPUT/'native-motion-events.jsonl'
    def motion_events():
     global motion_buffer
     while True:
      try:chunk=motion_socket.recv(65536)
      except BlockingIOError:break
      assert chunk,'native motion event socket closed';motion_buffer+=chunk;assert len(motion_buffer)<=1048576
      while b'\n' in motion_buffer:
       line,motion_buffer=motion_buffer.split(b'\n',1)
       if line.startswith(b'warlockmotion>>'):
        raw=line.split(b'>>',1)[1];record=json.loads(raw);motion_traces.append(record)
        with motion_log.open('ab') as out:out.write(raw+b'\n')
     return motion_traces
    preferences=wait(lambda:[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('motion-preference: ')])
    check('ActualNativeGtkReducedMotionObserved',preferences[-1]['source']=='gtk' and preferences[-1]['profile']=='reduced',preferences=preferences)
    applied=wait(lambda:[json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind')=='motion-profile'])
    check('NativeProfileAcknowledgesElmReducedPreference',applied[-1]['profile']=='reduced',receipts=applied)
    report['motionPreferenceObservations']=preferences;report['motionProfileReceipts']=applied

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
   def private_effect(operation,identity=None,expected_status="Committed"):
    before=facts();n=str((10000 if MEMBERSHIP else 9000)+len(report['nativeFixtures']));intent={'request':n,'generation':n,'incarnation':identity or target,'operation':operation,'context':client.context(before)};result=client.effect(intent);report['nativeFixtures'].append({'intent':intent,'result':result});check('ControlledNativeFixture'+operation,result['status']==expected_status,result=result,expectedStatus=expected_status);return result
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
     outcome=private_effect('minimize',target,expected_status='Refused')
     check(name+'CompetingNativeEffectRefused',outcome['status']=='Refused' and outcome['reason']=='native-pointer-owned' and ownership()==active,result=outcome)
     pointer(f'button {button} 0\nsleep 100');ended=wait(lambda:owned('idle'));physical(f'key {modifier} 0\nsleep 100');wait(lambda:received_owner('idle',ended['serial']))
     check(name+'ExactlyOneNativeEnd',int(ended['serial'])==int(active['serial'])+1 and ended['owner'] is None and not current_window()['minimized'],before=before,active=active,end=ended)
     after=root_window();check(name+'NativeGeometryChanged',after['at']!=window_before['at'] if button==272 else after['size']!=window_before['size'],before=window_before,after=after)
     report['gestures'].append({'name':name,'before':before,'active':active,'crossings':crossings,'end':ended,'windowBefore':window_before,'windowAfter':after})
    # Additive explicit-cancellation recording; the original two crossings,
    # blocked shortcut/effect and one-release assertions above are unchanged.
    cancel_before=ownership();cancel_window=root_window()
    cx,cy=map(round,[cancel_window['at'][0]+cancel_window['size'][0]/2,cancel_window['at'][1]+cancel_window['size'][1]/2])
    pointer(f'move {cx} {cy}\nsleep 100');physical('key 125 1\nsleep 50');pointer(f'button 272 1\nsleep 50\nmove {cx+10} {cy+10}\nsleep 100')
    cancel_active=wait(lambda:owned('move'));wait(lambda:received_owner('move',cancel_active['serial']))
    check('ExplicitEscapeStartsOriginalNativeOwner',cancel_active['owner']==target and int(cancel_active['serial'])==int(cancel_before['serial'])+1,observation=cancel_active)
    physical('key 1 1\nsleep 50\nkey 1 0\nsleep 100');cancel_end=wait(lambda:owned('idle'));wait(lambda:received_owner('idle',cancel_end['serial']))
    check('ExplicitEscapeEndsGestureExactlyOnce',int(cancel_end['serial'])==int(cancel_active['serial'])+1 and cancel_end['owner'] is None and (projection() or {}).get('mode')=='closed',observation=cancel_end)
    pointer('button 272 0\nsleep 100');physical('key 125 0\nsleep 100')
    check('ReleaseAfterExplicitCancelCannotEndAgain',ownership()==cancel_end,observation=ownership())
    report['explicitCancel']={'before':cancel_before,'active':cancel_active,'end':cancel_end,'afterPhysicalRelease':ownership()}
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
    def primary_key(code):helper([str(keyboard)],f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100\nsync\n')
    def keyboard_primary(operation):
     helper([str(keyboard)],'key 125 1\nkey 56 1\nkey 57 1\nsleep 50\nkey 57 0\nkey 56 0\nkey 125 0\nsleep 100\nsync\n')
     wait(lambda:(projection() or {}).get('mode')=='applications')
     primary_key(1)
     def focused_bar():
      rows=[json.loads(line.split(' ',2)[2])['body'] for line in text().splitlines() if line.startswith('surface-report: origin=bar ')]
      body=rows[-1] if rows else None;p=projection()
      return body if body and body.get('documentFocused') and p and p['phase']=='Coherent' and p['mode']=='closed' and body['publication']==p['publication'] and any(b['id']==body['focus'] and not b['disabled'] for b in body['buttons']) else None
     wait(focused_bar);primary_key(102)
     body=wait(focused_bar);chosen=next(b for b in body['buttons'] if b['accessibleName'].startswith(operation.title()+' ELM-ACTIVATION-PEER;') and not b['disabled'])
     for _ in range(len(body['buttons'])+1):
      current=wait(focused_bar)
      if any(b['id']==current['focus'] and b['identity']==chosen['identity'] for b in current['buttons']):break
      old_focus=current['focus'];primary_key(106);wait(lambda:(b:=focused_bar()) and b['focus']!=old_focus)
     body=wait(focused_bar);check('KeyboardPrimaryReachesCurrent'+operation.title(),any(b['id']==body['focus'] and b['identity']==chosen['identity'] for b in body['buttons']),body=body)
     primary_key(28)
    def action(stage,operation,focus,minimized):
     button=wait(lambda:group(operation.title()));before=len(journal())
     if PRIMARYKEY:keyboard_primary(operation)
     else:click(button)
     wait(lambda:transaction_state()=='Committed' and current_window()['minimized']==minimized and facts()['facts']['focused']==focus)
     check(stage+'ExactlyOneBoundEffect',len(journal())==before+1 and journal()[-1]['intent']['incarnation']==target and journal()[-1]['intent']['operation']==operation,journal=journal()[before:])
     submitted=journal()[-1]
     def receipts():return [f for f in [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('backend-frame: ')] if f.get('kind')=='effect-outcome' and f.get('binding')==submitted['binding'] and f.get('effectProtocol')==submitted['effectProtocol'] and f.get('intent')==submitted['intent']]
     rows=wait(receipts);check(stage+'NativeCommittedReceipt',len(rows)==1 and rows[0]['status']=='Committed',request=submitted,receipts=rows)
     report.setdefault('primaryReceipts',[]).append({'stage':stage,'request':submitted,'receipt':rows[0]})
     if MOTION:
      observed=wait(lambda:next((row for row in motion_events() if row['binding']==submitted['binding'] and row['intent']==submitted['intent']),None))
      check(stage+'NativeMotionProfileIsInstant',observed['profile']=='reduced' and observed['settled'],motion=observed)
      report.setdefault('motionTransitionReceipts',[]).append(observed)

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
    if PRIMARYKEY:
     check('PrimaryJourneyUsesZeroInjectedPointerEvents',not any(str(POINTER) in row['command'] for row in report['helpers']))
     report['nativeKeyboardPrimaryJourneyObserved']=True
    if MOTION:
     def bar_body_motion():
      bodies=[json.loads(line.split(' ',2)[2])['body'] for line in text().splitlines() if line.startswith('surface-report: origin=bar ')]
      return bodies[-1] if bodies else None
     body=wait(bar_body_motion);check('NativeTaskbarProjectsInstantProfile',body['motionProfile']=='reduced' and body['motionAnimations']==0,body=body)
     opener=next(b for b in body['buttons'] if b['accessibleName']=='Open Task View' and not b['disabled'])
     check('TaskViewOpenerPhysicallyVisible',0<=opener['x']+opener['width']/2<800 and 0<=opener['y']<48,opener=opener)
     before_effects=len(journal());click({'visible':True,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     def overlay_motion():
      bodies=[json.loads(line.split(' ',2)[2])['body'] for line in text().splitlines() if line.startswith('surface-report: origin=popup ')]
      return bodies[-1] if bodies and 'Task View' in bodies[-1]['text'] else None
     overlay=wait(overlay_motion);check('ActualNativeOverlayUsesReducedProfileWithoutDecorativeMotion',overlay['motionProfile']=='reduced' and overlay['motionAnimations']==0 and overlay['documentFocused'],body=overlay)
     image=OUTPUT/'motion-task-view.png';helper(['/usr/bin/grim',str(image)]);report['motionOverlayRecording']={'path':str(image),'sha256':sha(image),'body':overlay}
     helper([str(keyboard)],'key 1 1\nsleep 50\nkey 1 0\nsleep 100\nsync\n');wait(lambda:(projection() or {}).get('mode')=='closed');check('ReducedMotionOverlayDismissalCreatesNoWindowEffect',len(journal())==before_effects)
     if not LIVE:motion_socket.close()
     report['nativeReducedMotionObserved']=True
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
      if UNAVAILABLE:selected=button.get('identity')=='notifications:refresh'
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
     check('KeyboardSettingsNativeSaved',saved['snapshot']['values']=={'theme':'dawn','textScale':100,'effectsOff':False,'reducedTransparency':False},receipt=saved)
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
    elif TRANSFER:
     wait(lambda:(projection() or {}).get('phase')=='Coherent')
     root=target
     def member():return next(w for w in facts()['facts']['windows'] if w['incarnation']==root)
     def transfer_receipts():
      return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ') and json.loads(line.split(': ',1)[1]).get('kind')=='effect-outcome' and json.loads(line.split(': ',1)[1]).get('intent',{}).get('operation')=='transfer-workspace']
     def open_transfer(destination="2"):
      opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Task View' and not b['disabled']),None))
      click({'visible':0<=opener['x']<800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
      wait(lambda:(projection() or {}).get('mode')=='overview' and any(b['accessibleName']=='Move ELM-AUTHORITY-FIXTURE to another workspace' for b in (popup_body() or {}).get('buttons',[])))
      keyboard_button('Move ELM-AUTHORITY-FIXTURE to another workspace')
      return wait(lambda:any(b['accessibleName']=='Move selected window to workspace '+destination for b in (popup_body() or {}).get('buttons',[])))
     before=len(journal());original=member();original_transfer_membership={w['incarnation']:(w['workspace'],w['monitor']) for w in facts()['facts']['windows']};check('OriginalTransferStartsOnWorkspaceOne',original['workspace']=='1',member=original)
     open_transfer();keyboard_button('Cancel window transfer');wait(lambda:not any(b['accessibleName'].startswith('Move selected window') for b in (popup_body() or {}).get('buttons',[])))
     check('CancelTransferDoesNotSubmitOrMove',len(journal())==before and member()['workspace']=='1')
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed')
     check('NativePinnedRefusalFixture',s.ctl('dispatch',"hl.dsp.window.pin({window='"+selector+"'})").strip()=='ok')
     wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' and w['pinned'] for w in s.data('clients')))
     open_transfer();popup_capture('native-transfer-destinations');before=len(transfer_receipts());keyboard_button('Move selected window to workspace 2',28)
     refused=wait(lambda:len(transfer_receipts())==before+1 and transfer_receipts()[-1]);wait(lambda:(projection() or {}).get('phase')=='Coherent' and 'refused' in (bar_body() or {}).get('text','').lower())
     check('NativeRefusalRetainsWorkspaceOneWithVisibleFeedback',refused['status']=='Refused' and refused['reason']=='transfer-family-ineligible' and member()['workspace']=='1',receipt=refused,member=member(),bar=bar_body())
     def refusal_announcements():
      return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('announcement-delivery: ')]
     cue=wait(lambda:next((cue for cue in refusal_announcements() if json.loads(cue['message']['correlation']).get('outcome')=='transfer-refused'),None))
     correlation=json.loads(cue['message']['correlation'])
     check('RefusalAnnouncementMatchesExactNativeReceipt',correlation=={'outcome':'transfer-refused','binding':refused['binding'],'identity':{'effectProtocol':refused['effectProtocol'],'intent':refused['intent']}} and cue['deliver'] and cue['recipient']==cue['announcer'] and cue['recipient']['surface']=='bar',cue=cue,receipt=refused)
     announced_bar=wait(lambda:next((body for body in [bar_body()] if body and any(a.get('sequence')==cue['message']['sequence'] for a in body.get('announcements',[]))),None))
     live=announced_bar['announcements']
     check('OneNativeLiveRegionHasRefusalAndRecovery',len(live)==1 and live[0]['live']=='polite' and live[0]['sequence']==cue['message']['sequence'] and live[0]['correlation']==cue['message']['correlation'] and live[0]['text']==cue['message']['text'] and 'ELM-AUTHORITY-FIXTURE' in live[0]['text'] and 'Refresh window status, then choose again.' in live[0]['text'] and len(refusal_announcements())==1,bar=announced_bar)
     report['nativeRefusalAnnouncementObserved']=True
     report['refusalAnnouncementScope']='Exact native refusal/owner/serial and actual WebKit live-region DOM; native speech/braille and independent UI-010 acceptance remain unverified.'
     check('NativeUnpinForAcceptedTransfer',s.ctl('dispatch',"hl.dsp.window.pin({window='"+selector+"'})").strip()=='ok')
     wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' and not w['pinned'] for w in s.data('clients')))
     open_transfer();before=len(transfer_receipts());keyboard_button('Move selected window to workspace 2',28)
     committed=wait(lambda:len(transfer_receipts())==before+1 and transfer_receipts()[-1]);wait(lambda:member()['workspace']=='2' and (projection() or {}).get('phase')=='Coherent')
     check('MatchingCommittedTransferMovesOnlySelectedRoot',committed['status']=='Committed' and committed['intent']['incarnation']==root and committed['intent']['transfer']['source']=='1' and committed['intent']['transfer']['destination']=='2' and all(w['workspace']=='2' for w in facts()['facts']['windows']),receipt=committed,facts=facts())
     before=len(transfer_receipts());open_transfer('3');keyboard_button('Move selected window to workspace 3',28)
     empty=wait(lambda:len(transfer_receipts())==before+1 and transfer_receipts()[-1]);wait(lambda:member()['workspace']=='3' and (projection() or {}).get('phase')=='Coherent')
     check('TransferCreatesEmptyOrdinaryWorkspaceWithoutFollowing',empty['status']=='Committed' and empty['intent']['transfer']['source']=='2' and empty['intent']['transfer']['destination']=='3' and s.data('monitors')[0]['activeWorkspace']['id']==1,receipt=empty,member=member())
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open Task View' and not b['disabled']),None))
     click({'visible':True,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     body=wait(lambda:next((body for body in [popup_body()] if body and any(b['accessibleName']=='Activate ELM-AUTHORITY-FIXTURE on workspace 3' for b in body['buttons'])),None));popup_capture('native-transfer-workspace-three')
     check('TaskViewDisplaysAcceptedNativeMembership',any(b['accessibleName']=='Activate ELM-AUTHORITY-FIXTURE on workspace 3' for b in body['buttons']) and len(transfer_receipts())==before+1,body=body)
     key(1);wait(lambda:(projection() or {}).get('mode')=='closed');report['nativeTransferJourneyObserved']=True
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
    elif UNAVAILABLE:
     def center_body():
      body=popup_body();p=projection()
      return body if body and p and p.get('mode')=='notifications' and body['publication']==p['publication'] else None
     def incoming():return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('backend-frame: ')]
     def reads():return [row for row in incoming() if row.get('kind')=='notification-snapshot']
     def cues():return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('announcement-delivery: ') and json.loads(json.loads(line.split(': ',1)[1])['message']['correlation'])['outcome']=='adapter-unavailable']
     before_window=len(journal())
     opener=wait(lambda:next((b for b in (bar_body() or {}).get('buttons',[]) if b['accessibleName']=='Open notifications' and not b['disabled']),None))
     click({'visible':0<=opener['x'] and opener['x']+opener['width']<=800 and 0<=opener['y']<48,'point':[opener['x']+opener['width']/2,opener['y']+opener['height']/2]})
     wait(lambda:center_body() and reads() and cues())
     first=reads()[-1];cue=cues()[-1]
     check('ActualOccupiedServiceHasOnePoliteMatchedFailure',not first['snapshot']['available'] and len(cues())==1 and not cue['message']['interrupt'] and len(center_body()['announcements'])==1 and center_body()['announcements'][0]['live']=='polite',receipt=first,cue=cue,body=center_body())
     # Navigate to the real Refresh node, then use the physical key without a
     # helper Focus effect or a DOM script. Pending reads keep it focusable.
     button=wait(lambda:next((b for b in center_body()['buttons'] if b.get('identity')=='notifications:refresh' and not b['disabled']),None))
     for _ in range(len(center_body()['buttons'])+2):
      if center_body()['focusIdentity']=='notifications:refresh':break
      key(15)
     stable=center_body();check('PhysicalKeyboardReachesRefresh',stable['focusIdentity']=='notifications:refresh' and stable['documentFocused'])
     key(28);wait(lambda:len(cues())==2 and len(reads())>=4)
     failed=reads()[-1];cue=cues()[-1];correlation=json.loads(cue['message']['correlation']);body=center_body()
     check('ExactNativeFailureIdentityAndOneOwner',correlation['binding']==failed['binding'] and correlation['identity']=={'adapter':'notifications','request':failed['requestId'],'service':failed['snapshot']['service'],'revision':failed['snapshot']['revision']} and cue['recipient']==cue['announcer'] and cue['recipient']['surface']=='popup' and not cue['message']['interrupt'],receipt=failed,cue=cue)
     check('DuplicatedRealReceiptCannotReannounce',sum(row['requestId']==failed['requestId'] for row in reads())==2 and len(cues())==2 and sum(row['message']['sequence']==cue['message']['sequence'] for row in cues())==1,receipts=reads(),cues=cues())
     check('UnavailableFailureRetainsActualFocusedNode',body['focusNode']==stable['focusNode'] and body['focusIdentity']==stable['focusIdentity'] and body['documentFocused'] and len(body['announcements'])==1 and body['announcements'][0]['live']=='polite',before=stable,after=body)
     popup_capture('adapter-unavailable');capture=report['popupCaptures'][-1]
     check('UnavailableRecoveryHasActualNativeControlPixels',len(capture['controlRegions'])==1 and capture['controlRegions'][0]['accessibleName']=='Refresh notifications' and capture['controlRegions'][0]['brightPixels']>15,capture=capture)
     unavailable_stop.write_text('stop');unavailable_owner.wait(timeout=5)
     check('ExistingOwnerReleasesNormally',unavailable_owner.returncode==0)
     prior=len(cues());key(28)
     wait(lambda:reads() and reads()[-1]['snapshot']['available'] and center_body())
     recovered=reads()[-1];body=center_body()
     check('ExplicitKeyboardRefreshRecoversEmptyService',recovered['requestId']!=failed['requestId'] and recovered['snapshot']['service']==failed['snapshot']['service'] and int(recovered['snapshot']['revision'])>int(failed['snapshot']['revision']) and recovered['snapshot']['entries']==[],receipt=recovered)
     check('RecoveryDoesNotReplayAnnouncementOrMoveFocus',len(cues())==prior and body['focusNode']==stable['focusNode'] and body['focusIdentity']==stable['focusIdentity'] and body['documentFocused'],body=body,cues=cues())
     check('ReadOnlyRecoveryHasNoWindowLaunchOrNotificationEffects',len(journal())==before_window and not launches() and not requests('notification-effect'))
     popup_capture('adapter-recovered');report['nativeAdapterUnavailableObserved']=True;report['adapterReceipts']=reads();report['adapterAnnouncements']=cues()
    elif NOTIFICATIONS:
     notification_control=OUTPUT/'notification-control.json'
     producer=s.host.launch('notification-producers',['/usr/bin/python3','-B',str(ROOT/'qa/notification-producer.py'),str(notification_control)],env=env);apps.append(producer);notification_producer=producer
     notification_serial=0
     def producer_events():
      path=notification_control.with_suffix('.events.jsonl')
      raw=path.read_text() if path.exists() else ''
      return [json.loads(line) for line in raw[:raw.rfind('\n')+1].splitlines()]
     wait(lambda:any(row['kind']=='ready' for row in producer_events()))
     def notify(producer_index,summary,label,timeout=0,replaces=0,urgency=1):
      global notification_serial
      notification_serial+=1
      temp=notification_control.with_suffix('.tmp');temp.write_text(json.dumps({'serial':notification_serial,'op':'notify','producer':producer_index,'summary':summary,'label':label,'timeout':timeout,'replaces':replaces,'urgency':urgency}));os.replace(temp,notification_control)
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
     rejection_cue=wait(lambda:next((json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('announcement-delivery: ') and json.loads(json.loads(line.split(': ',1)[1])['message']['correlation'])['outcome']=='notification-expired-action-refused' and json.loads(json.loads(line.split(': ',1)[1])['message']['correlation'])['identity']['request']==queued['requestId']),None))
     rejection_identity=json.loads(rejection_cue['message']['correlation'])
     check('OriginalExpiredQueuedActionHasExactPoliteAnnouncement',refused['reason']=='expired' and rejection_identity['binding']==queued['binding'] and rejection_identity['identity']['target']==queued['intent'] and not rejection_cue['message']['interrupt'] and rejection_cue['recipient']==rejection_cue['announcer'],cue=rejection_cue,receipt=refused)

     keyboard_button('Open replacement notification',28)
     wait(lambda:any(row['signal']=='ActionInvoked' for row in signals(reuse)))
     check('OnlyNewIncarnationReceivesChosenAction',len([row for row in signals(reuse) if row['signal']=='ActionInvoked'])==1 and signals(other)==[],signals=signals(reuse))
     helper([str(POINTER),'800','600'],'move 400 280\nwheel 180 0\nsleep 100\n')
     popup_capture('notification-history')
     capture=report['popupCaptures'][-1]
     check('HistoryHasActualNativeTextPixels',any(region['accessibleName']=='Warlock fixture: Expiring notification' and region['brightPixels']>15 for region in capture['controlRegions']),capture=capture)
     # Extend the original journey using real producer messages and physical
     # policy controls. No fixture-injected permission or frontend outcome.
     def notification_cues():
      return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('announcement-delivery: ') and json.loads(json.loads(line.split(': ',1)[1])['message']['correlation'])['outcome']=='notification-arrival']
     def cue_for(identifier):
      row=notification_row(identifier)
      return next((cue for cue in notification_cues() if row and row['incarnation'] in json.loads(cue['message']['correlation'])['identity']['incarnations']),None)
     def assert_arrival(identifier,interrupt,stable_focus):
      cue=wait(lambda:cue_for(identifier));row=notification_row(identifier);correlation=json.loads(cue['message']['correlation'])
      body=wait(lambda:(body:=center_body()) and any(a.get('sequence')==cue['message']['sequence'] for a in body.get('announcements',[])) and body)
      observation=next(frame for frame in reversed(incoming()) if frame.get('kind')=='notification-update' and any(entry['incarnation']==row['incarnation'] for entry in frame['snapshot']['entries']))
      check('NativeNotificationAnnouncement'+row['summary'],cue['message']['interrupt']==interrupt and cue['recipient']==cue['announcer'] and cue['recipient']['surface']=='popup' and correlation['binding']==observation['binding'] and correlation['identity']['service']==observation['snapshot']['service'] and correlation['identity']['revision']==observation['snapshot']['revision'] and len(body['announcements'])==1 and body['announcements'][0]['live']==('assertive' if interrupt else 'polite') and body['focusNode']==stable_focus['node'] and body['focusIdentity']==stable_focus['identity'] and body['documentFocused'] and sum(c['message']['sequence']==cue['message']['sequence'] for c in notification_cues())==1,cue=cue,body=body,observation=observation)
     keyboard_button('Do not disturb for this session',28)
     wait(lambda:(body:=center_body()) and any(b['identity']=='notifications:dnd' and 'On' in b['label'] for b in body['buttons']))
     stable_focus={'node':center_body()['focusNode'],'identity':center_body()['focusIdentity']};prior_cues=len(notification_cues())
     silent=notify(0,'DND keeps native history','Open DND history')
     wait(lambda:(body:=center_body()) and 'DND keeps native history' in body['text'])
     check('NativeDndArrivalKeepsHistoryAndFocusWithoutAnnouncement',notification_row(silent)['state']=='live' and len(notification_cues())==prior_cues and center_body()['focusNode']==stable_focus['node'] and center_body()['focusIdentity']==stable_focus['identity'] and center_body()['documentFocused'] and cue_for(silent) is None,body=center_body(),row=notification_row(silent))
     keyboard_button('Do not disturb for this session',28)
     wait(lambda:(body:=center_body()) and any(b['identity']=='notifications:dnd' and 'Off' in b['label'] for b in body['buttons']))
     check('NativeDndOffDoesNotReplaySuppressedHistory',len(notification_cues())==prior_cues and cue_for(silent) is None)
     stable_focus={'node':center_body()['focusNode'],'identity':center_body()['focusIdentity']}
     unopted=notify(0,'Unopted critical stays polite','Open unopted critical',urgency=2)
     assert_arrival(unopted,False,stable_focus)
     keyboard_button('Allow critical notification interruptions for this session',28)
     wait(lambda:(body:=center_body()) and any(b['identity']=='notifications:critical-interrupt' and 'On' in b['label'] for b in body['buttons']))
     stable_focus={'node':center_body()['focusNode'],'identity':center_body()['focusIdentity']};prior_cues=len(notification_cues())
     opted=notify(0,'Opted critical interruption','Open opted critical',urgency=2)
     assert_arrival(opted,True,stable_focus)
     ordinary=notify(0,'Ordinary remains polite','Open ordinary notification',urgency=1)
     assert_arrival(ordinary,False,stable_focus)

     def expiry_cues():return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith('announcement-delivery: ') and json.loads(json.loads(line.split(': ',1)[1])['message']['correlation'])['outcome']=='notification-expiration']
     # Existing irrelevant 1200ms expiry above must remain silent. Its native
     # incarnation cannot be inferred from a count or reused numeric ID.
     check('OriginalUnfocusedUninvokedExpiryIsSilent',not any(old_expiring['incarnation'] in json.loads(cue['message']['correlation'])['identity']['incarnations'] for cue in expiry_cues()))
     focused_notification=notify(0,'Focused expiration','Open focused expiration',timeout=1800)
     wait(lambda:any(b['accessibleName']=='Open focused expiration' and not b['disabled'] for b in (center_body() or {}).get('buttons',[])))
     item=notification_row(focused_notification);focus_identity='notification:'+notification_snapshot()['service']+':'+item['incarnation']+':invoke:open'
     key(102)
     for _ in range(len(center_body()['buttons'])+2):
      if center_body()['focusIdentity']==focus_identity:break
      key(108)
     stable=wait(lambda:(body:=center_body()) and body['focusIdentity']==focus_identity and body['documentFocused'] and body)
     wait(lambda:notification_row(focused_notification)['state']=='expired' and any(item['incarnation'] in json.loads(cue['message']['correlation'])['identity']['incarnations'] for cue in expiry_cues()))
     cue=next(cue for cue in expiry_cues() if item['incarnation'] in json.loads(cue['message']['correlation'])['identity']['incarnations']);identity=json.loads(cue['message']['correlation'])
     body=wait(lambda:(body:=center_body()) and any(b.get('identity')==focus_identity and b.get('focusOnly') and b['disabled'] for b in body['buttons']) and body)
     observation=next(frame for frame in reversed(incoming()) if frame.get('kind')=='notification-update' and any(entry['incarnation']==item['incarnation'] and entry['state']=='expired' for entry in frame['snapshot']['entries']))
     check('FocusedExpiryHasExactPoliteIdentityAndRetainedActualNode',identity['binding']==observation['binding'] and identity['identity']['service']==observation['snapshot']['service'] and identity['identity']['revision']==observation['snapshot']['revision'] and identity['identity']['incarnations']==[item['incarnation']] and not cue['message']['interrupt'] and cue['recipient']==cue['announcer'] and body['focusNode']==stable['focusNode'] and body['focusIdentity']==focus_identity and body['documentFocused'] and len(body['announcements'])==1 and body['announcements'][0]['live']=='polite',cue=cue,observation=observation,before=stable,after=body)
     old_actions=len(requests('notification-effect'));key(28)
     check('RetainedExpiredControlCannotDispatchOrRelocate',len(requests('notification-effect'))==old_actions and center_body()['focusNode']==stable['focusNode'] and center_body()['focusIdentity']==focus_identity and not any(row['signal']=='ActionInvoked' for row in signals(focused_notification)))
     key(102);wait(lambda:(body:=center_body()) and body['focusIdentity']=='control:close' and not any(b.get('identity')==focus_identity for b in body['buttons']))
     check('UserKeyboardDepartureRetiresUnavailableControl',not any(b.get('identity')==focus_identity for b in center_body()['buttons']))
     keyboard_button('Do not disturb for this session',28)
     wait(lambda:any(b['identity']=='notifications:dnd' and 'On' in b['label'] for b in center_body()['buttons']))
     silent_expiry=notify(0,'DND focused expiration','Open DND focused expiration',timeout=1800)
     wait(lambda:any(b['accessibleName']=='Open DND focused expiration' and not b['disabled'] for b in center_body()['buttons']))
     silent_item=notification_row(silent_expiry);silent_focus='notification:'+notification_snapshot()['service']+':'+silent_item['incarnation']+':invoke:open';before_cues=len(expiry_cues())
     key(102)
     for _ in range(len(center_body()['buttons'])+2):
      if center_body()['focusIdentity']==silent_focus:break
      key(108)
     stable_silent=wait(lambda:(body:=center_body()) and body['focusIdentity']==silent_focus and body)
     wait(lambda:notification_row(silent_expiry)['state']=='expired' and any(b.get('identity')==silent_focus and b.get('focusOnly') for b in center_body()['buttons']))
     check('DndRelevantExpiryKeepsHistoryAndFocusWithoutAnnouncement',len(expiry_cues())==before_cues and center_body()['focusNode']==stable_silent['focusNode'] and center_body()['focusIdentity']==silent_focus and center_body()['documentFocused'],before=stable_silent,after=center_body())
     key(102);keyboard_button('Do not disturb for this session',28)
     wait(lambda:any(b['identity']=='notifications:dnd' and 'Off' in b['label'] for b in center_body()['buttons']))
     check('DndOffDoesNotReplayExpiration',len(expiry_cues())==before_cues)
     report['nativeNotificationRelevanceObserved']=True;report['notificationRelevanceCues']=expiry_cues()+[rejection_cue]
     report['nativeNotificationAnnouncementPolicyObserved']=True
     report['notificationAnnouncementScope']='Real native producer urgency, physical DND/consent controls, exact once-only announcement correlation, actual WebKit polite/assertive region and retained DOM focus; actual speech/braille and independent original acceptance remain open.'
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
     if LAYER:
      keyboard_button('Disable soft effects',28);keyboard_button('Reduce transparency',28)
      check('AppearanceDraftDoesNotApplyOrWrite',settings_body()['effects']=='on' and settings_body()['reducedTransparency']=='false' and not stored() and not requests('shell-settings-write'))
     check('SettingsDraftDoesNotChangeAppearanceOrWrite',settings_body()['theme']=='night' and settings_body()['textScale']=='100' and not requests('shell-settings-write') and not stored())
     keyboard_button('Save settings',28)
     saved=wait(lambda:stored() if stored() and stored()['values']=={'theme':desired_theme,'textScale':150,'effectsOff':LAYER,'reducedTransparency':LAYER} else None)
     body=wait(lambda:settings_body() if settings_body() and settings_body()['theme']==desired_theme and settings_body()['fontSize']=='24px' else None)
     if LAYER:check('BothCommittedAppearanceModesApply',body['effects']=='off' and body['reducedTransparency']=='true' and saved['schema']==2,body=body,storage=saved)
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
     original=state_file.read_bytes();invalid={**saved,'values':{**saved['values'],'theme':'night','textScale':77}}
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
     if LAYER:check('BothAppearanceModesSurviveWholeHostRestart',body['effects']=='off' and body['reducedTransparency']=='true' and bar_body()['effects']=='off' and bar_body()['reducedTransparency']=='true' and stored()==saved,body=body,bar=bar_body(),storage=stored())
     if LAYER:
      keyboard_button('Dismiss help',28)
      for _ in range(len(settings_body()['buttons'])+1):
       body=settings_body();focus=next((button for button in body['buttons'] if button['id']==body['focus']),None)
       if focus and focus['identity']=='settings:effects-off':break
       key(15)
      else:raise AssertionError('Original native appearance focus traversal')
      body=wait(lambda:settings_body() if settings_body() and settings_body()['focus']==focus['id'] and settings_body()['documentFocused'] else None)
      # Ordinary Tab reveals the second preference through the real popup scroll
      # route, rather than treating an offscreen successor as an unusable control.
      key(15)
      body=wait(lambda:settings_body() if settings_body() and any(button['identity']=='settings:reduced-transparency' and button['id']==settings_body()['focus'] for button in settings_body()['buttons']) else None)
      toggles=[button for button in body['buttons'] if button['identity'] in ['settings:effects-off','settings:reduced-transparency']]
      check('NativeAppearanceControlsRemainVisibleAndNamed',len(toggles)==2 and all(button['width']>0 and button['height']>0 and button['x']>=0 and button['y']>=0 and button['x']+button['width']<=body['viewportWidth'] and button['y']+button['height']<=body['viewportHeight'] for button in toggles),controls=toggles,body=body)
      check('NativeEffectsOffRetainsSolidKeyboardFocus',body['focusStyle']['outlineWidth']=='3px' and body['focusStyle']['outlineColor']=='rgb(23, 104, 176)',body=body)
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
     if LAYER:
      capture=report['popupCaptures'][-1]
      check('ActualNativeAppearanceControlsArePainted',bool(capture['controlRegions']) and all(c['area']>0 and c['paintedPixels']>.9*c['area'] for c in capture['controlRegions']),capture=capture)
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
    elif IME:
     click(wait(lambda:(projection() or {}).get('openApplications')))
     wait(lambda:field_value()=='' and (popup_body() or {}).get('focus')=='launcher-search')
     queries=lambda:(popup_body() or {}).get('queryObservations',[])
     before_effects=len(journal());before_launches=len(launches());before_queries=len(queries())
     def direct_preedit():
      helper([str(keyboard)],'key 29 1\nkey 42 1\nkey 22 1\nsleep 50\nkey 22 0\nkey 42 0\nkey 29 0\nsleep 100\nsync\n')
      for code in [3,7,4,30]:key(code)
      return wait(lambda:(body if body.get('composing') and any(e['type']=='compositionstart' and e['isTrusted'] for e in body.get('compositionEvents',[])) else None) if (body:=popup_body()) else None)
     def candidate_layers():
      return [row for output in s.data('layers').values() for rows in output.get('levels',{}).values() for row in rows if 'fcitx' in row.get('namespace','').lower()]
     def unicode_search():
      helper([str(keyboard)],'key 29 1\nkey 42 1\nkey 56 1\nkey 22 1\nsleep 50\nkey 22 0\nkey 56 0\nkey 42 0\nkey 29 0\nsleep 100\nsync\n')
      for code in [31,49,24,17,50,30,49]:key(code)
      return wait(candidate_layers)
     def settled(value):
      body=popup_body();return body if body and not body.get('composing') and 'No matching applications' in body.get('text','') and any(f['id']=='launcher-search' and f['value']==value and f.get('caretStart')==len(value) and f.get('caretEnd')==len(value) for f in body.get('fields',[])) else None
     preedit=direct_preedit();report['imePreedit']=preedit;popup_capture('ime-field-preedit')
     check('NativeFieldPreeditDoesNotDispatchCommittedQueryOrEffect',len(queries())==before_queries and len(journal())==before_effects and len(launches())==before_launches,preedit=preedit,queries=queries())
     key(57);committed=wait(lambda:settled('☺'));report['imeDirectCommitted']=committed;popup_capture('ime-field-committed')
     check('OneNativeFieldCommitHasCorrectCaretAndNoLaunch',len(queries())==before_queries+1 and len(journal())==before_effects and len(launches())==before_launches,queries=queries(),committed=committed)
     before_queries=len(queries());layers=unicode_search();report['imeCandidateLayers']=layers;popup_capture('ime-candidates')
     check('ActualExternalCandidatePreeditRetainsCommittedField',field_value()=='☺' and len(queries())==before_queries and len(journal())==before_effects and len(launches())==before_launches,layers=layers)
     key(108);key(28);committed=wait(lambda:settled('☺⛄'));report['imeCommitted']=committed;popup_capture('ime-candidate-committed')
     check('OneNativeCandidateCommitHasCorrectCaretAndNoLaunch',len(queries())==before_queries+1 and len(journal())==before_effects and len(launches())==before_launches,queries=queries(),committed=committed)
     before_queries=len(queries());cancelled_preedit=direct_preedit();report['imeCancelPreedit']=cancelled_preedit;key(1)
     cancelled=wait(lambda:settled('☺⛄'));report['imeCancelled']=cancelled;popup_capture('ime-field-cancelled')
     check('NativeFieldCancelClearsPreeditWithoutQueryOrUnintendedEffect',len(queries())==before_queries and len(journal())==before_effects and len(launches())==before_launches and (projection() or {}).get('mode')=='applications',queries=queries(),cancelled=cancelled)
     unicode_search();key(1);wait(lambda:not candidate_layers());cancelled=wait(lambda:settled('☺⛄'));report['imeCandidateCancelled']=cancelled
     check('NativeCandidateCancelHasNoQueryOrUnintendedEffect',len(queries())==before_queries and len(journal())==before_effects and len(launches())==before_launches,queries=queries(),cancelled=cancelled)
     check('NativeCompositionEventsAreTrustedGTKWebKitEvents',all(e['isTrusted'] for e in cancelled.get('compositionEvents',[])),events=cancelled.get('compositionEvents',[]))
     report['imeFixture']['nativeIMEObserved']=True
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
    elif TRANSFER:
     final_transfer_membership={w['incarnation']:(w['workspace'],w['monitor']) for w in facts()['facts']['windows']}
     expected_transfer_membership={**original_transfer_membership,root:('3',original_transfer_membership[root][1])}
     terminal_transfers=transfer_receipts()
     submitted_transfers=[r for r in journal() if r.get('intent',{}).get('operation')=='transfer-workspace']
     check('TransferReceiptsMatchExactSubmittedIdentities',len(submitted_transfers)==3 and len(terminal_transfers)==3 and all(len([r for r in terminal_transfers if all(r.get(k)==submitted.get(k) for k in ['binding','effectProtocol','intent'])])==1 for submitted in submitted_transfers),requests=submitted_transfers,receipts=terminal_transfers)
     check('OnlyMatchingCommittedTransferChangesWorkspace',final_transfer_membership==expected_transfer_membership and len(terminal_transfers)==3 and [r['status'] for r in terminal_transfers]==['Refused','Committed','Committed'] and [r['intent']['transfer']['destination'] for r in terminal_transfers]==['2','2','3'] and all(r['intent']['incarnation']==root for r in terminal_transfers),before=original_transfer_membership,after=final_transfer_membership,receipts=terminal_transfers)
    else:check('NoScratchpadOrWorkspaceTransfer',not facts()['facts']['windows'] and report['beforeControlledRetirements']['facts']['windows'] if CHORD else current_window()['workspace']==initial_workspace,nativeWorkspace='controlled original roots retired' if CHORD else current_window()['workspace'],originalWorkspace=initial_workspace)
   if LIVE:
    report.update(requirements=['ELM-UI-014','ELM-UI-018'],scenarios=['live-motion-minimize','live-motion-restore','live-motion-switcher','live-motion-Task View','motion-enable','motion-overlays','motion-disable'],scope='Actual GTK source changes, physical keyboard override/save/reset, durable restart and subsequent native normal-profile window operation. Original intermediate restore geometry/proxy and all separate live overlay intervals remain explicitly unverified.')
    keyboard=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
    def key(code):helper([str(keyboard)],f'key {code} 1\nsleep 50\nkey {code} 0\nsleep 100\nsync\n')
    def rows(prefix):return [json.loads(line.split(': ',1)[1]) for line in text().splitlines() if line.startswith(prefix+': ')]
    def requests(kind):return [row for row in rows('frontend-request') if row.get('kind')==kind]
    def motion_acks():return [row for row in rows('backend-frame') if row.get('kind')=='motion-profile']
    def current_body(origin):
     bodies=[json.loads(line.split(' ',2)[2])['body'] for line in text().splitlines() if line.startswith('surface-report: origin='+origin+' ')]
     p=projection()
     return bodies[-1] if bodies and p and bodies[-1]['publication']==p['publication'] else None
    def profile(value):
     ack=motion_acks();body=current_body('bar')
     return ack[-1] if ack and body and ack[-1]['profile']==value and body['motionProfile']==value else None
    def change_source(value,effective):
     before=len(rows('motion-preference'));motion_control.write_text(value+'\n')
     wait(lambda:len(rows('motion-preference'))>before and rows('motion-preference')[-1]['profile']==('full' if value=='F' else 'reduced'))
     wait(lambda:profile(effective));check('ActualGtkSource'+value+'Effective'+effective,True,observations=rows('motion-preference')[-2:],ack=motion_acks()[-1])
    def open_settings():
     def opener():
      body=current_body('bar')
      if not body:return None
      button=next((b for b in body['buttons'] if b['accessibleName']=='Open settings' and not b['disabled']),None)
      if not button:return None
      actions=body['actions']
      if button['x']<actions['x'] or button['x']+button['width']>actions['x']+actions['width']:
       helper([str(POINTER),'800','600'],f"move {round(actions['x']+actions['width']/2)} {round(actions['y']+actions['height']/2)}\nsleep 100\nwheel 4096\nsleep 100")
       return None
      return button
     button=wait(opener);click({'visible':0<=button['x']<800 and 0<=button['y']<48,'point':[button['x']+button['width']/2,button['y']+button['height']/2]})
     wait(lambda:current_body('popup') if (projection() or {}).get('mode')=='settings' else None)
    def keyboard_button(label):
     def target():return next((b for b in (current_body('popup') or {}).get('buttons',[]) if b['accessibleName']==label and not b['disabled']),None)
     button=wait(target)
     for _ in range(len(current_body('popup')['buttons'])+2):
      body=wait(lambda:current_body('popup'))
      current=target()
      if current and body['focus']==current['id']:break
      key(15)
     body=wait(lambda:current_body('popup'));button=target()
     check('MotionKeyboardReaches'+label,body['documentFocused'] and body['focus']==button['id'] and button['y']>=0 and button['y']+button['height']<=body['viewportHeight'],body=body,target=button)
     key(28)
    state_file=pathlib.Path(env['XDG_STATE_HOME'])/'warlock/motion.json'
    def stored():return json.loads(state_file.read_text()) if state_file.exists() else None
    def save_choice(label,value,effective):
     before=len(requests('motion-preferences-write'));revision=int(stored()['revision']) if stored() else 1
     keyboard_button(label);keyboard_button('Save motion preference')
     saved=wait(lambda:stored() if stored() and stored()['revision']==str(revision+1) and stored()['override']==value else None)
     wait(lambda:profile(effective));writes=requests('motion-preferences-write')
     check('MotionSaved'+label,len(writes)==before+1 and writes[-1]['proposal']=={'schema':1,'revision':str(revision),'override':value},storage=saved,request=writes[-1])
     report.setdefault('motionPreferenceSaves',[]).append({'label':label,'storage':saved,'request':writes[-1],'ack':motion_acks()[-1]})
    completed=len(journal());focus_before=facts()['facts']['focused']
    change_source('F','full');check('DisablingCompletedMotionDoesNotReplay',len(journal())==completed and facts()['facts']['focused']==focus_before)
    open_settings();save_choice('Reduced motion','reduced','reduced')
    before_config=len(requests('motion-profile-set'));change_source('R','reduced');change_source('F','reduced')
    check('SavedOverrideWinsWithoutExtraNativeConfigurations',len(requests('motion-profile-set'))==before_config)
    save_choice('Follow system',None,'full');save_choice('Full motion','full','full')
    change_source('R','full');saved=stored();key(1);wait(lambda:(projection() or {}).get('mode')=='closed')
    image=OUTPUT/'live-motion-before-restart.png';helper(['/usr/bin/grim',str(image)]);report['liveMotionBeforeRestart']={'path':str(image),'sha256':sha(image),'storage':saved}
    owned=next(row for proc,row in s.host.processes if proc is web);s.host.stop(owned,web);web.wait(timeout=5);check('MotionFirstHostNormalRestartExit',web.returncode==0)
    web=s.host.launch('warlock-motion-restarted',[str(binary),'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(ROOT/'adapter/daemon.py'),'--qa-exit-after-render','--qa-stay-open','--surface-experiment','--qa-motion-control',str(motion_control)],env=env);apps.append(web);log=OUTPUT/'warlock-motion-restarted.log';collector=Collector()
    wait(lambda:(projection() or {}).get('phase')=='Coherent' and profile('full'))
    check('RestartUsesSavedFullOverrideOverActualReducedGtk',stored()==saved and rows('motion-preference')[-1]['profile']=='reduced' and not requests('motion-preferences-write') and not journal(),storage=stored(),ack=motion_acks()[-1])
    open_settings();save_choice('Reduced motion','reduced','reduced');save_choice('Follow system',None,'reduced')
    image=OUTPUT/'live-motion-settings.png';helper(['/usr/bin/grim',str(image)]);report['liveMotionSettings']={'path':str(image),'sha256':sha(image),'body':current_body('popup'),'storage':stored()}
    key(1);wait(lambda:(projection() or {}).get('mode')=='closed');change_source('F','full')
    check('MotionControlsNeverMutateWindowsOrAppearance',not journal() and not requests('shell-settings-write') and not (state_file.parent/'settings.json').exists())
    button=wait(lambda:group('Minimize'));click(button);wait(lambda:transaction_state()=='Committed' and current_window()['minimized'])
    submitted=journal()[-1];observed=wait(lambda:next((row for row in motion_events() if row['binding']==submitted['binding'] and row['intent']==submitted['intent']),None))
    check('SubsequentWindowOperationUsesNormalProfileOnce',len(journal())==1 and submitted['intent']['operation']=='minimize' and observed['profile']=='full',request=submitted,motion=observed)
    check('MotionPreferenceFilePrivateAndVersioned',state_file.stat().st_mode&0o777==0o600 and stored()['schema']==1 and stored()['override'] is None)
    report['nativeLiveMotionPreferencesObserved']=True
    report['missingObservations']=['Actual intermediate restore geometry and exactly-once proxy retirement; live minimize/switcher/Task View transition toggles; separate switcher/Task View/snap reduced-motion fixtures; native AT and independent original acceptance.']
   report['nativeFeedbackObserved']=not FOCUS and not CATALOG and not TASKVIEW and not PRIMARY and not SWITCHER and not CHORD;report['nativeFocusJourneyObserved']=FOCUS;check('EveryRegisteredHelperExitedNormally',all(r['exitCode']==0 for r in report['helpers']));report['passed']=True
  finally:
   if MOTION and 'motion_socket' in globals():motion_socket.close()
   if paused:pause(False)
   if drag_writer is not None:
    os.close(drag_writer);drag_writer=None
   if drag_pointer is not None:
    drag_pointer.wait(timeout=5);check('PersistentPointerNormalExit',drag_pointer.returncode==0)
   if chord_writer is not None:
    os.close(chord_writer);chord_writer=None
   if chord_keyboard is not None:
    chord_keyboard.wait(timeout=5);check('PersistentKeyboardNormalExit',chord_keyboard.returncode==0)
   if unavailable_owner is not None and unavailable_owner.poll() is None:
    unavailable_stop.write_text('stop');unavailable_owner.wait(timeout=5)
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
