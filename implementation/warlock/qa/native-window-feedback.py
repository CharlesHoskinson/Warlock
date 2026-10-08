"""ELM-UI-007 restore feedback on the real private Wayland/Elm/native path.

Reuse immutable ABI/runtime by reference; no preview, supervisor or new source
lineage. Native/AT acceptance remain separate, with AT explicitly outstanding.
"""
import hashlib,importlib.util,json,os,pathlib,signal,subprocess,sys,time,traceback
PRIMARY=sys.argv[1:]==['--taskbar-primary']
CHORD=sys.argv[1:]==['--switcher-chord']
SWITCHER=sys.argv[1:]==['--switcher']
NAV=sys.argv[1:]==['--workspace-navigation'];FOCUS=sys.argv[1:]==['--taskbar-focus'];PRESENTATION=sys.argv[1:]==['--launcher-presentation'];SEARCH=sys.argv[1:]==['--launcher-search'] or PRESENTATION;PINS=sys.argv[1:]==['--taskbar-pins'];CATALOG=SEARCH or PINS;RETIRE_OPENER=sys.argv[1:]==['--task-view-retired-opener'];TASKVIEW=sys.argv[1:]==['--task-view'] or NAV or RETIRE_OPENER;assert not sys.argv[1:] or FOCUS or CATALOG or TASKVIEW or PRIMARY or SWITCHER or CHORD
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];HELD=REPO/'implementation/warlock-preview-provider-v143';RUNTIME=REPO/'implementation/warlock-client-provider-native-v204'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('feedback_private_host',RUNTIME/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
host.original.qa.require_qa_scope();sys.path.insert(0,str(RUNTIME/'qa'))
from session_bus import isolate_session_host
from system_isolation import supply,validate
from inspection import Collector
isolate_session_host(host)
sys.path.insert(0,str(ROOT/'adapter'));from effect_endpoint import Endpoint;from endpoint import start_time
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
OUT=ROOT/'qa/runs'/(('native-switcher-chord-' if CHORD else 'native-switcher-' if SWITCHER else 'native-primary-' if PRIMARY else 'native-workspace-navigation-' if NAV else 'native-task-view-' if TASKVIEW else 'native-pins-' if PINS else 'native-search-' if SEARCH else 'native-taskbar-focus-' if FOCUS else 'native-feedback-')+str(time.time_ns()));OUT.mkdir(parents=True)
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
 original_fixture=FIXTURE;FIXTURE=fixture_inputs/'primary-action-fixture.py';FIXTURE.write_text(adapted)
 primary_fixture={'originalSHA256':sha(original_fixture),'path':str(FIXTURE),'sha256':sha(FIXTURE),'change':'One original colored GTK root per process; distinct program identities create two single-family taskbar entries.'}
if CHORD:
 fixture_inputs=OUTPUT.with_name(OUTPUT.name+'-inputs');fixture_inputs.mkdir(mode=0o700,exist_ok=True)
 fixture_source=FIXTURE.read_text();initial="create('ELM-AUTHORITY-FIXTURE', 'red')\ncreate('ELM-ACTIVATION-PEER', 'green')"
 assert fixture_source.count(initial)==1
 adapted=fixture_source.replace(initial,initial+"\ncreate('ELM-CHORD-THIRD', 'blue')")
 needle="        elif request['op'] == 'retire-peer':"
 assert adapted.count(needle)==1
 adapted=adapted.replace(needle,"        elif request['op'] == 'arrive-chord':\n            create('ELM-CHORD-ARRIVAL', 'blue')\n        elif request['op'] == 'retire-third':\n            windows.pop('ELM-CHORD-THIRD').destroy()\n        elif request['op'] == 'retire-arrival':\n            windows.pop('ELM-CHORD-ARRIVAL').destroy()\n        elif request['op'] == 'retire-primary':\n            windows.pop('ELM-AUTHORITY-FIXTURE').destroy()\n"+needle)
 original_fixture=FIXTURE;FIXTURE=fixture_inputs/'chord-fixture.py';FIXTURE.write_text(adapted)
 chord_fixture={'originalSHA256':sha(original_fixture),'path':str(FIXTURE),'sha256':sha(FIXTURE),'change':'Third independent GTK root plus controlled retire/arrival operations; original client input/controllers unchanged.'}
report={'schema':1,'requirements':['ELM-UI-007'],'scenarios':['restore-pending','restore-refused','restore-unknown'],'scope':'Actual pointer/Elm/native effect feedback and private compositor pixels; no AT/IME/full release acceptance','nativeFeedbackObserved':False,'nativeAcceptance':False,'assistiveTechnologyAccepted':False,'fullReleaseAccepted':False,'mainDesktopActions':False,'passed':False,'checks':[],'sourceInputs':{str(p.relative_to(ROOT)):sha(p) for folder in ['src','native','adapter','assets'] for p in (ROOT/folder).iterdir() if p.is_file()},'pair':pair,'nativeHost':{'path':str(binary),'sha256':sha(binary),'heldBuild':str(build_path),'heldBuildSHA256':sha(build_path)},'runtimeByReference':{'root':str(RUNTIME),'hostSHA256':sha(RUNTIME/'candidate_host.py')},'helpers':[],'nativeFixtures':[]};s=None;loaded=False;apps=[];broker=None;paused=False;sequence=0;chord_keyboard=None;chord_writer=None
if focus_host:report['focusHostAdaptation']=focus_host
if retirement_fixture:report['retirementFixture']=retirement_fixture
if primary_fixture:report['primaryFixture']=primary_fixture
if SEARCH:report.update(requirements=['ELM-UI-005','ELM-UX-029'],scenarios=['search-no-match','search-race','search-refused','launcher-refused'],scope='Actual current query and private catalog, native typing/Enter refusal and no duplicate launch; AT/IME and popup physical presentation acceptance remain pending',popupPresentationAccepted=False)
if PINS:report.update(requirements=['ELM-UI-004','ELM-UX-004'],scenarios=['taskbar-zero','ux-004'],scope='Actual native keyboard pin/reorder, shell restart, identity order and one current zero-window launch; popup physical presentation and AT acceptance remain separate',popupPresentationAccepted=False,nativePinJourneyObserved=False)
if TASKVIEW:report.update(requirements=['ELM-UX-017','ELM-UI-006'],scenarios=['ux-017','overview-cancel'],scope='Actual two populated native workspaces, exact window membership and active marker, keyboard/pointer local browsing and Escape recipient; independent and applicable AT acceptance remain pending',nativeTaskViewJourneyObserved=False)
if RETIRE_OPENER:report['scope']='Actual native Task View browse then primary opener retirement; Escape must not revive its incarnation or dispatch a window effect. Independent/AT acceptance remains pending.'
if NAV:report.update(requirements=['ELM-UI-002','ELM-UI-006','ELM-UX-008'],scenarios=['activate-other-workspace','overview-select','ux-008','activation-refused'],scope='Actual minimized workspace-2 family selected through Task View and taskbar; native receipts, focus/keyboard, pixels and unchanged membership; stale-context refusal; other-output, partial-refusal and AT acceptance remain separate',nativeNavigationJourneyObserved=False,authorityBuild={'path':str(authority_path),'sha256':sha(authority_path)})
if FOCUS:report.update(requirements=['ELM-UI-004','ELM-UX-024'],scenarios=['taskbar-group','ux-024'],scope='Actual native picker traversal and Escape/focus recipient diagnosis; menu/AT original acceptance remains pending')
if CHORD:report.update(requirements=['ELM-UI-003','ELM-UX-012','ELM-UX-013'],scenarios=['switcher-order','switcher-cancel','switcher-zero-one','switcher-retire-arrive','ux-012','ux-013'],scope='Actual global native Alt-Tab three-root order, startup release, native cancellation fence, membership freeze and zero/one; modal/protected/AT/independent acceptance remain open',nativeChordJourneyObserved=False,chordFixture=chord_fixture)
if SWITCHER:report.update(requirements=['ELM-UI-003'],scenarios=['switcher-order','switcher-cancel'],scope='Actual native MRU observation, integrated switcher control pixels, local keyboard cycling/cancel and identity-bound chosen activation; global Alt-Tab journal, modal representation and AT/independent acceptance remain pending',nativeSwitcherJourneyObserved=False)
if PRIMARY:report.update(requirements=['ELM-UI-004'],scenarios=['taskbar-inactive','taskbar-active','taskbar-minimized'],scope='Actual pointer single-family activation/minimize/restore, exact native receipt and GTK keyboard recipient, MRU/desktop succession and pixels; primary keyboard and AT acceptance remain pending',nativePrimaryJourneyObserved=False)
LUA=b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''
if CHORD:LUA+=(ROOT/'native/switcher-bindings.lua').read_bytes()
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
   native=next(row for _,row in s.host.processes if row['name']=='hyprland')
   config={'runtime':str(s.host.runtime),'instance':s.env['HYPRLAND_INSTANCE_SIGNATURE'],'pid':native['pid'],'expected_start':int(start_time(native['pid'])),'binary_sha256':pair['core']['sha256']}
   config_path=OUTPUT/'authority-config.json';config_path.write_text(json.dumps(config));config_path.chmod(0o600)
   client=Endpoint(**config);client.hello();env=supply(s.env,s.host.runtime);validate(env,s.host.runtime);env['XDG_STATE_HOME']=str(s.host.runtime/'private-warlock-state');report['privateStateRoot']=env['XDG_STATE_HOME'];env.update(GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')
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
   control=OUTPUT/'fixture-control.json';fixture=s.host.launch('fixture',['/usr/bin/python3','-B',str(FIXTURE),str(control),*(['primary'] if PRIMARY else [])],env=env);apps.append(fixture)
   if PRIMARY:
    peer_control=OUTPUT/'peer-control.json';peer_fixture=s.host.launch('peer-fixture',['/usr/bin/python3','-B',str(FIXTURE),str(peer_control),'peer'],env=env);apps.append(peer_fixture)
   wait(lambda:any(w['title']=='ELM-AUTHORITY-FIXTURE' for w in s.data('clients')));wait(lambda:any(w['title']=='ELM-ACTIVATION-PEER' for w in s.data('clients')));
   if not (FOCUS or TASKVIEW or PRIMARY or SWITCHER or CHORD):fixture_control('hide-peer');wait(lambda:len(s.data('clients'))==1)
   if PRIMARY:
    peer=next(w for w in s.data('clients') if w['title']=='ELM-ACTIVATION-PEER');peer_selector='address:'+peer['address']
    if not peer['floating']:check('PeerFixtureFloats',s.ctl('dispatch',"hl.dsp.window.float({action='set',window='"+peer_selector+"'})").strip()=='ok')
    check('PeerFixtureSize',s.ctl('dispatch',"hl.dsp.window.resize({x=320,y=240,window='"+peer_selector+"'})").strip()=='ok')
    check('PeerFixturePosition',s.ctl('dispatch',"hl.dsp.window.move({x=400,y=150,window='"+peer_selector+"'})").strip()=='ok')
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
     row=client.scene_facts('430');n=str(8000+len(report['nativeFixtures']));intent={'request':n,'generation':n,'incarnation':identity,'operation':'activate','context':client.context(row)};result=client.effect(intent);report['nativeFixtures'].append({'intent':intent,'result':result});check('CommittedHistoryFixture',result['status']=='Committed',result=result)
    for identity in [a,b,c]:native_focus(identity)
    check('NativeHistoryABCBeforeFrontend',client.activation_history('430')['roots']==[c,b,a])
    physical('key 56 1\nkey 15 1\nsleep 50\nkey 15 0\nkey 56 0\nsleep 100')
    startup=client.switcher_journal('430',observe=True);report['startupJournalBeforeHost']=startup
    check('NativeReleaseRecordedBeforeFrontendExists',startup['chord']['released'] and startup['chord']['steps']==[1] and startup['chord']['history']==[c,b,a] and not startup['chord']['consumed'])
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
   web=s.host.launch('warlock',['%s'%binary,'--assets',str(assets),'--authority-config',str(config_path),'--backend',str(backend_fixture if CATALOG or CHORD else ROOT/'adapter/daemon.py'),'--qa-exit-after-render','--qa-stay-open','--surface-experiment'],env=env);apps.append(web);log=OUTPUT/'warlock.log';collector=Collector()
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
   initial=None if TASKVIEW or SWITCHER or CHORD else wait(lambda:group('Activate' if PRIMARY else 'Choose a window from' if FOCUS else 'Minimize'))
   target=next(w['incarnation'] for w in client.snapshot('442')['windows'] if w['label']==('ELM-ACTIVATION-PEER' if PRIMARY else 'ELM-AUTHORITY-FIXTURE'))
   initial_workspace=next(w['workspace'] for w in facts()['facts']['windows'] if w['incarnation']==target)
   def current_window():return next(w for w in facts()['facts']['windows'] if w['incarnation']==target)
   def transaction_state():return (projection() or {}).get('transaction')
   def private_effect(operation,identity=None):
    before=facts();n=str(9000+len(report['nativeFixtures']));intent={'request':n,'generation':n,'incarnation':identity or target,'operation':operation,'context':client.context(before)};result=client.effect(intent);report['nativeFixtures'].append({'intent':intent,'result':result});check('ControlledNativeFixture'+operation,result['status']=='Committed',result=result)
   def screenshot(state):
    body=wait(lambda:feedback(state));o=body['feedback'];check(state+'VisibleCorrelatedMessage',o and o['width']>=180 and o['height']==48 and o['clip']=='none' and o['display']!='none' and o['accessibleName']==o['text'] and o['atomic']=='true' and o['live']=='polite',feedback=o)
    image=OUTPUT/(state+'.png');helper(['/usr/bin/grim',str(image)])
    import gi;gi.require_version('GdkPixbuf','2.0');from gi.repository import GdkPixbuf
    pix=GdkPixbuf.Pixbuf.new_from_file(str(image));data=pix.get_pixels();stride=pix.get_rowstride();channels=pix.get_n_channels();left,top=int(o['x'])+5,int(o['y'])+3;right,bottom=min(800,int(o['x']+o['width'])-3),min(48,int(o['y']+o['height'])-3)
    bright=sum(1 for y in range(top,bottom) for x in range(left,right) if all(data[y*stride+x*channels+i]>170 for i in range(3)))
    check(state+'NativeTaskbarHasTextPixels',pix.get_width()==800 and pix.get_height()==600 and bright>30,image=str(image),sha256=sha(image),brightPixels=bright,region=[left,top,right,bottom]);report.setdefault('feedback',{})[state]=body
   if PRIMARY:
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
     button=next((b for b in body['buttons'] if b['accessibleName']==operation+' ELM-ACTIVATION-PEER' and not b['disabled']),None)
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
   elif CATALOG or TASKVIEW or SWITCHER or CHORD:
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
     for button in body['buttons']:
      selected=button['accessibleName'].startswith(('Activate ELM-','Restore ELM-')) if SWITCHER or CHORD else (button['accessibleName'].startswith('Browse workspace ') or (NAV and button['accessibleName'].startswith('Restore ELM-ACTIVATION-PEER'))) if TASKVIEW else button['accessibleName'] in ['Refresh applications','Open Files']
      if not selected or button['disabled'] or button['y']<0 or button['y']+button['height']>box[3]:continue
      left,top=max(0,int(box[0]+button['x'])+12),max(100,int(box[1]+button['y'])+6)
      right,bottom=min(800,int(box[0]+button['x']+min(220,button['width']))-12),min(600,box[1]+box[3],int(box[1]+button['y']+button['height'])-6)
      bright=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>170 for c in range(3)))
      painted=sum(1 for y in range(top,bottom) for x in range(left,right) if all(pixels[y*stride+x*channels+c]>15 for c in range(3)))
      regions.append({'accessibleName':button['accessibleName'],'brightPixels':bright,'paintedPixels':painted,'area':max(0,right-left)*max(0,bottom-top),'region':[left,top,right,bottom]})
     report.setdefault('popupCaptures',[]).append({'stage':stage,'path':str(image),'sha256':sha(image),'controlRegions':regions,'body':body,'drawObservations':[l for l in text().splitlines() if l.startswith('popup-draw-observation:')][-3:]})

    def bar_body():
     rows=[json.loads(l.split(' ',2)[2])['body'] for l in text().splitlines() if l.startswith('surface-report: origin=bar ')]
     return rows[-1] if rows else None
    def requests(kind):return [json.loads(l.split(': ',1)[1]) for l in text().splitlines() if l.startswith('frontend-request: ') and json.loads(l.split(': ',1)[1])['kind']==kind]
    def query(codes,expected):
     wait(lambda:(popup_body() or {}).get('focus')=='launcher-search')
     helper([str(keyboard)],'key 29 1\nkey 30 1\nsleep 50\nkey 30 0\nkey 29 0\nkey 14 1\nkey 14 0\nsleep 100\nsync\n')
     for code in codes:key(code)
     wait(lambda:field_value()==expected)
    def keyboard_button(label):
     button=wait(lambda:next((b for b in (popup_body() or {}).get('buttons',[]) if b['accessibleName']==label and not b['disabled']),None))
     for _ in range(len(popup_body()['buttons'])+2):
      if popup_body()['focus']==button['id']:break
      key(15)
     check('KeyboardReaches'+label,popup_body()['focus']==button['id'],body=popup_body())
     key(57)
    if CHORD:
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
     open_switcher();body=wait(lambda:selected_window('ELM-ACTIVATION-PEER'))
     visible_order=[button['accessibleName'].split(';',1)[0] for button in body['buttons'] if button['accessibleName'].startswith(('Activate ELM-','Restore ELM-'))]
     check('SwitcherFrozenOrderMatchesNativeHistory',visible_order==['Activate '+labels[root] for root in native_history['roots']],body=body)
     popup_capture('mru-initial');key(15);wait(lambda:selected_window('ELM-AUTHORITY-FIXTURE'))
     key(105);wait(lambda:selected_window('ELM-ACTIVATION-PEER'))
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
     before_refusal=facts();n=str(9000+len(report['nativeFixtures']));intent={'request':n,'generation':n,'incarnation':peer_identity,'operation':'activate','context':client.context(old)};receipt=client.effect(intent);report['nativeFixtures'].append({'intent':intent,'result':receipt})
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
    check('NoScratchpadOrWorkspaceTransfer',not facts()['facts']['windows'] and report['beforeControlledRetirements']['facts']['windows'] if CHORD else current_window()['workspace']==initial_workspace,nativeWorkspace='controlled original roots retired' if CHORD else current_window()['workspace'],originalWorkspace=initial_workspace)
   report['nativeFeedbackObserved']=not FOCUS and not CATALOG and not TASKVIEW and not PRIMARY and not SWITCHER and not CHORD;report['nativeFocusJourneyObserved']=FOCUS;check('EveryRegisteredHelperExitedNormally',all(r['exitCode']==0 for r in report['helpers']));report['passed']=True
  finally:
   if paused:pause(False)
   if chord_writer is not None:
    os.close(chord_writer);chord_writer=None
   if chord_keyboard is not None:
    chord_keyboard.wait(timeout=5);check('PersistentKeyboardNormalExit',chord_keyboard.returncode==0)
   for proc in reversed(apps):
    if proc.poll() is None:
     if proc is fixture:fixture_control('quit');proc.wait(timeout=5)
     else:owned=next(row for p,row in s.host.processes if p is proc);s.host.stop(owned,proc);proc.wait(timeout=5)
    check('OwnedClientNormalExit',proc.returncode==0,pid=proc.pid,exitCode=proc.returncode)
   if loaded:s.guard();check('OwningPluginUnloads',s.ctl('plugin','unload',pair['plugin']['path']).strip()=='ok');loaded=False
   registered={row['pid'] for _,row in s.host.processes}
   for row in reversed([r for r in s.host.descendants() if r['pid'] not in registered]):s.host.stop(row)
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost']=s.evidence if s else None
report['cleanupPassed']=bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed']=report['passed'] and report['cleanupPassed']
report['runtimeEvidenceDirectory']=str(OUTPUT);report['runnerSHA256']=sha(__file__)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
