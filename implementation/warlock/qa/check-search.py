"""Focused compiled launcher/search integration, protected CPU scope only."""
import pathlib,hashlib,json,os,sys,time,shutil,subprocess,shlex,importlib.util,concurrent.futures,http.server,threading
RELEVANCE=sys.argv[1:]==['--notification-relevance']
ADAPTER_ANNOUNCEMENTS=sys.argv[1:]==['--adapter-announcements']
NOTIFICATION_ANNOUNCEMENTS=sys.argv[1:]==['--notification-announcements']
ANNOUNCEMENTS=RELEVANCE or ADAPTER_ANNOUNCEMENTS or NOTIFICATION_ANNOUNCEMENTS or sys.argv[1:]==['--announcements']
DESCRIPTION=sys.argv[1:]==['--preview-description']
LAYER=sys.argv[1:]==['--layer-appearance']
SHUTDOWN=sys.argv[1:]==['--preview-shutdown']
BARRETURN=sys.argv[1:]==['--bar-keyboard-return']
SHORTCUTS=sys.argv[1:]==['--shortcut-choices']
PINMAX=sys.argv[1:]==['--pin-max']
QUIESCENT=sys.argv[1:]==['--preview-quiescence']
PREVIEW=DESCRIPTION or sys.argv[1:]==['--preview-states']
LIVE=sys.argv[1:]==['--live-motion']
MOTION=sys.argv[1:]==['--reduced-motion'] or LIVE
TRANSFER=sys.argv[1:]==['--transfer-workspace']
LAUNCHER=sys.argv[1:]==['--launcher-dismissal']
IME=sys.argv[1:]==['--ime'] or LAUNCHER
ACCESSIBILITY=sys.argv[1:]==['--accessibility']
CONTRAST=sys.argv[1:]==['--high-contrast']
DRAG=sys.argv[1:]==['--drag-ownership']
KEYBOARD=sys.argv[1:]==['--keyboard-shell']
ATTENTION=sys.argv[1:]==['--attention']
JUMP=sys.argv[1:]==['--jump-lists']
FILES=sys.argv[1:]==['--files']
SYSTEM=sys.argv[1:]==['--system-menu']
NOTIFICATIONS=RELEVANCE or ADAPTER_ANNOUNCEMENTS or NOTIFICATION_ANNOUNCEMENTS or sys.argv[1:]==['--notifications']
SETTINGS=LAYER or sys.argv[1:]==['--settings'] or CONTRAST or SHORTCUTS
SNAP=sys.argv[1:]==['--snap-chooser']
REFLOW=sys.argv[1:]==['--popup-reflow']
MENU=sys.argv[1:]==['--dense-menu'] or REFLOW
PICKER=sys.argv[1:]==['--dense-picker'] or MENU
DENSE=sys.argv[1:]==['--dense-taskbar'] or PICKER
PINMENUS=sys.argv[1:]==['--pinned-menus'] or (DENSE and not PICKER)
PRIMARY=DESCRIPTION or sys.argv[1:]==['--taskbar-primary'] or PINMENUS or PICKER
SWITCHER=sys.argv[1:]==['--switcher'] or ACCESSIBILITY
NAV=sys.argv[1:]==['--workspace-navigation'];PINS=sys.argv[1:]==['--pins'];POPUP=sys.argv[1:]==['--native-popup'] or QUIESCENT or SHUTDOWN or BARRETURN;TASKVIEW=sys.argv[1:]==['--task-view'] or NAV or SNAP or SETTINGS or NOTIFICATIONS or SYSTEM or FILES or JUMP or ATTENTION or KEYBOARD or DRAG or IME or TRANSFER or MOTION or PINMAX or ANNOUNCEMENTS;assert not sys.argv[1:] or PINS or POPUP or TASKVIEW or PRIMARY or SWITCHER or PREVIEW
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];HELD=REPO/'implementation/warlock-preview-provider-v143'
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
OUT=ROOT/'qa/runs'/(('announcements-' if ANNOUNCEMENTS else 'preview-description-' if DESCRIPTION else 'layer-appearance-' if LAYER else 'bar-keyboard-return-' if BARRETURN else 'preview-shutdown-' if SHUTDOWN else 'pin-max-' if PINMAX else 'preview-quiescence-' if QUIESCENT else 'preview-states-' if PREVIEW else 'live-motion-' if LIVE else 'reduced-motion-' if MOTION else 'transfer-workspace-' if TRANSFER else 'ime-' if IME else 'accessibility-' if ACCESSIBILITY else 'high-contrast-' if CONTRAST else 'drag-ownership-' if DRAG else 'keyboard-shell-' if KEYBOARD else 'attention-' if ATTENTION else 'jump-lists-' if JUMP else 'files-' if FILES else 'system-menu-' if SYSTEM else 'notifications-' if NOTIFICATIONS else 'settings-' if SETTINGS else 'snap-chooser-' if SNAP else 'switcher-' if SWITCHER else 'taskbar-primary-' if PRIMARY else 'workspace-navigation-' if NAV else 'task-view-' if TASKVIEW else 'popup-' if POPUP else 'pins-' if PINS else 'search-')+str(time.time_ns()));OUT.mkdir(parents=True);INPUT=OUT/'inputs';INPUT.mkdir();inputs={}
for folder in ['src','native','adapter','assets','qa']:
 (INPUT/folder).mkdir()
 for p in (ROOT/folder).iterdir():
  if p.is_file():shutil.copyfile(p,INPUT/folder/p.name);inputs[str(p.relative_to(ROOT))]=sha(p)
info=json.loads((ROOT/'elm.json').read_text());info['source-directories']=['src','qa'];(INPUT/'elm.json').write_text(json.dumps(info))
spec=importlib.util.spec_from_file_location('search_toolchain',HELD/'qa/toolchain.py');toolchain=importlib.util.module_from_spec(spec);spec.loader.exec_module(toolchain);pinned=toolchain.verify();shutil.copytree(HELD/pinned['elmHome'],OUT/'elm-home');env={**os.environ,'ELM_HOME':str(OUT/'elm-home')}
report={'passed':False,'scope':'Compiled Elm query/ranking, native scoped field admission and current integrated host; native keyboard/AT release acceptance pending','requirements':['ELM-UI-005','ELM-UX-029'],'inputs':inputs,'commands':[],'protectedScope':scope,'nativeAcceptance':False,'fullReleaseAccepted':False};server=None
def run(name,args):
 p=subprocess.run(args,cwd=INPUT,env=env,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p.stdout
try:
 if RELEVANCE:
  model=json.loads(run('notification-relevance-model',['/usr/bin/python3','-B','qa/check-notification-relevance.py']));assert model['passed'];report['notificationRelevanceModel']=model
  run('compile-notification-relevance',[str(HELD/pinned['compiler']),'make','qa/NotificationRelevanceReplay.elm','--optimize','--output=assets/notification-relevance.js'])
  replay=(INPUT/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.NotificationRelevanceReplay');(INPUT/'qa/notification-relevance-replay.js').write_text(replay)
  run('typed-notification-relevance',['node','qa/notification-relevance-replay.js','assets/notification-relevance.js',str(OUT/'notification-relevance.json')]);report['notificationRelevance']=json.loads((OUT/'notification-relevance.json').read_text());assert all(report['notificationRelevance']['checks'].values())
 if ADAPTER_ANNOUNCEMENTS:
  model=json.loads(run('adapter-announcements-model',['/usr/bin/python3','-B','qa/check-adapter-announcements.py']));assert model['passed'];report['adapterAnnouncementsModel']=model
  run('compile-adapter-announcements',[str(HELD/pinned['compiler']),'make','qa/AdapterAnnouncementReplay.elm','--optimize','--output=assets/adapter-announcements.js'])
  replay=(INPUT/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.AdapterAnnouncementReplay');(INPUT/'qa/adapter-announcement-replay.js').write_text(replay)
  run('typed-adapter-announcements',['node','qa/adapter-announcement-replay.js','assets/adapter-announcements.js',str(OUT/'adapter-announcements.json')]);report['adapterAnnouncements']=json.loads((OUT/'adapter-announcements.json').read_text());assert all(report['adapterAnnouncements']['checks'].values())
 if NOTIFICATION_ANNOUNCEMENTS:
  model=json.loads(run('notification-announcements-model',['/usr/bin/python3','-B','qa/check-notification-announcements.py']));assert model['passed'];report['notificationAnnouncementsModel']=model
  run('compile-notification-announcements',[str(HELD/pinned['compiler']),'make','qa/NotificationAnnouncementReplay.elm','--optimize','--output=assets/notification-announcements.js'])
  replay=(INPUT/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.NotificationAnnouncementReplay');(INPUT/'qa/notification-announcement-replay.js').write_text(replay)
  run('typed-notification-announcements',['node','qa/notification-announcement-replay.js','assets/notification-announcements.js',str(OUT/'notification-announcements.json')]);report['notificationAnnouncements']=json.loads((OUT/'notification-announcements.json').read_text());assert all(report['notificationAnnouncements']['checks'].values())
 if ANNOUNCEMENTS:
  model=json.loads(run('announcement-owner-model',['/usr/bin/python3','-B','qa/check-announcement-owner.py']));assert model['passed'];report['announcementOwnerModel']=model
  run('compile-announcements',[str(HELD/pinned['compiler']),'make','qa/AnnouncementReplay.elm','--optimize','--output=assets/announcements.js'])
  replay=(INPUT/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.AnnouncementReplay');(INPUT/'qa/announcement-replay.js').write_text(replay)
  run('typed-announcements',['node','qa/announcement-replay.js','assets/announcements.js',str(OUT/'announcements.json')]);report['announcements']=json.loads((OUT/'announcements.json').read_text());assert all(report['announcements']['checks'].values())
 if LAYER:
  layerPacket=json.loads(run('layer-appearance-model',['/usr/bin/python3','-B','qa/check-layer-appearance.py']));assert layerPacket['passed'];report['layerAppearanceModel']=layerPacket
 if BARRETURN:
  modelPacket=json.loads(run('bar-keyboard-return-model',['/usr/bin/python3','-B','qa/check-bar-keyboard-return.py']))
  assert modelPacket['passed'];report['barKeyboardReturnModel']=modelPacket
 if SHUTDOWN:
  modelPacket=json.loads(run('shutdown-preview-model',['/usr/bin/python3','-B','qa/check-shutdown-preview.py']))
  assert modelPacket['passed'];report['shutdownPreviewModel']=modelPacket
 if PINMAX:
  modelPacket=json.loads(run('menu-read-order-model',['/usr/bin/python3','-B','qa/check-menu-read-order.py']))
  assert modelPacket['passed'];report['menuReadOrderModel']=modelPacket
  run('compile-pin-max',[str(HELD/pinned['compiler']),'make','qa/PinMaxReplay.elm','--optimize','--output=assets/pin-max.js'])
  replay=(INPUT/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.PinMaxReplay');(INPUT/'qa/pin-max-replay.js').write_text(replay)
  run('typed-pin-max',['node','qa/pin-max-replay.js','assets/pin-max.js',str(OUT/'pin-max.json')])
  report['pinMax']=json.loads((OUT/'pin-max.json').read_text());assert all(report['pinMax']['checks'].values())
 if PREVIEW:
  report.update(requirements=['ELM-UI-016'],scenarios=['preview-states'],scope='Actual compiled picker source/presenter states, strict legacy isolation, publication revalidation and owning native producer pool/host; physical/native/AT acceptance separate')
  run('compile-preview-states',[str(HELD/pinned['compiler']),'make','qa/PreviewStateReplay.elm','--optimize','--output=assets/preview-states.js'])
  replay=(INPUT/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.PreviewStateReplay');(INPUT/'qa/preview-states-replay.js').write_text(replay)
  run('typed-preview-states',['node','qa/preview-states-replay.js','assets/preview-states.js',str(OUT/'preview-states.json')])
  report['previewStates']=json.loads((OUT/'preview-states.json').read_text());assert all(report['previewStates']['checks'].values())
  run('preview-owning-table',['/usr/bin/python3','-B','qa/check-preview-states.py'])
  if DESCRIPTION:run('compile-preview-renderer',[str(HELD/pinned['compiler']),'make','src/NativePreviewRenderer.elm','--optimize','--output=assets/preview-renderer.js'])
 if SWITCHER:report.update(requirements=['ELM-UI-003','ELM-UX-012','ELM-UX-013'],scope='Compiled real switcher/root/view, bounded release/Ready/ordinal reducer and typed native journal/selection-fence admission; actual physical chord, native focus/AT and original acceptance remain separate')
 if PRIMARY:report.update(requirements=['ELM-UI-004'],scope='Compile current taskbar state labels and integrated Elm roots; unchanged native host reused by exact source/binary hashes; actual pointer/keyboard/AT acceptance separate')
 if PINS:report.update(requirements=['ELM-UI-004','ELM-UX-004'],scope='Compiled identity pins/reorder, private atomic native persistence, current integrated host; native restart/pixels acceptance pending')
 if POPUP:report.update(requirements=['ELM-UI-005','ELM-UX-029','ELM-UX-004'],scope='Changed native popup presentation units compiled/relinked; previously verified compiled Elm assets reused unchanged; actual native pixels acceptance pending')
 if QUIESCENT:report.update(requirements=['ELM-UI-017'],scenarios=['quiesce','reopen'],scope='Changed native preview scheduler compiled/relinked with exact unchanged Elm/C++ assets; actual GLib idle source retirement self-test; native counters and original soak acceptance separate')
 if BARRETURN:report.update(requirements=['ELM-UX-023'],scenarios=['ux-023','keyboard-taskbar-groups'],scope='Owning exact once-only GTK replay routing back to the original live bar engine; native proof/held-key preservation and exact C++/Elm hashes; actual native key delivery and original nine-surface journey remain separate')
 if SHUTDOWN:report.update(requirements=['ELM-DEL-021'],scenarios=['delivery-021'],scope='Changed owning host retirement-only shutdown routing, ordered negative controls and strict source/ABI reuse; native exit/custody/module/session observations remain separate')
 if TASKVIEW:report.update(requirements=['ELM-UX-017','ELM-UI-006'],scope='Compiled integrated Task View, workspace membership/active marker and guarded native selection; native pixels/input and original acceptance remain separate')
 if PINMAX:report.update(requirements=['ELM-UX-016'],scenarios=['ux-016'],scope='Compiled typed pin/MAX observation, pending/Unknown and exact existing custody path; owning native tuple and physical acceptance separate')
 if NAV:report.update(requirements=['ELM-UI-002','ELM-UI-006','ELM-UX-008'],scope='Compiled exact current off-workspace choice/restore replay and coherent scene admission; bounded navigation/refusal/no-replay model; separately compiled authority and actual native journeys required')
 if not POPUP:
  for name,target in [('Main','elm'),('Bar','bar'),('Popup','popup')]:run('compile-'+name,[str(HELD/pinned['compiler']),'make','src/'+name+'.elm','--optimize','--output=assets/'+target+'.js'])
  run('compile-search',[str(HELD/pinned['compiler']),'make','qa/SearchReplay.elm','--optimize','--output=assets/search.js'])
  replay=(INPUT/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.SearchReplay');(INPUT/'qa/search-replay.js').write_text(replay)
  run('typed-search',['node','qa/search-replay.js','assets/search.js',str(OUT/'search.json')]);r=json.loads((OUT/'search.json').read_text());assert r['rank']==['z-exact','a-prefix','b-token'] and r['keyword']==['z-exact'] and r['generic']==['b-token','z-exact'] and r['unicode']==['c-unicode'];assert r['refreshClearsSettledRefusal'] and r['refreshPreservesUnknown'];assert r['queryEditHasNoEffects'] and r['staleQueryRejected'] and 'No matching' in r['noMatchStatus'] and r['queryRetained']=='nonexistent';report['typedSearch']=r
 if REFLOW:
  run('compile-popup-reflow',[str(HELD/pinned['compiler']),'make','qa/PopupReflowReplay.elm','--optimize','--output=assets/popup-reflow.js'])
  (INPUT/'qa/popup-reflow-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.PopupReflowReplay'));run('typed-popup-reflow',['node','qa/popup-reflow-replay.js','assets/popup-reflow.js',str(OUT/'popup-reflow.json')]);report['typedPopupReflow']=json.loads((OUT/'popup-reflow.json').read_text());assert all(report['typedPopupReflow']['checks'].values())
  run('focus-model-typecheck',['quint','typecheck','qa/focus-publication.qnt'])
  run('focus-model-named',['quint','test','qa/focus-publication.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79113'])
  run('focus-model-invariants',['quint','run','qa/focus-publication.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79114'])
 if PINMENUS:
  run('activation-release-routing',['node','qa/activation-release.js'])
  report.update(requirements=['ELM-UI-008','ELM-UX-023'],scope='Compiled running-pin context guards and changed native keyboard-parent host; unchanged C++ objects reused by exact hashes; native menu/AT acceptance separate')
  run('compile-pinned-menu',[str(HELD/pinned['compiler']),'make','qa/PinnedMenuReplay.elm','--optimize','--output=assets/pinned-menu.js'])
  (INPUT/'qa/pinned-menu-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.PinnedMenuReplay'));run('typed-pinned-menu',['node','qa/pinned-menu-replay.js','assets/pinned-menu.js',str(OUT/'pinned-menu.json')]);report['typedPinnedMenus']=json.loads((OUT/'pinned-menu.json').read_text());assert all(report['typedPinnedMenus']['checks'].values())
 if SWITCHER:
  run('switcher-key-routing',['node','-e',r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert');const handlers={},sent=[];
const node={dataset:{mode:'switcher',publication:'7',lease:'2'},isConnected:true,contains:()=>true,querySelectorAll:()=>['control:commit','control:close','control:forward','control:reverse'].map(id=>({dataset:{surfaceControl:id},disabled:false}))};
const target={closest:()=>node};const document={getElementById:()=>null,addEventListener:(name,fn)=>{handlers[name]=fn;}};
const ports=new Proxy({},{get:()=>({send:packet=>sent.push(packet),subscribe:()=>{}})});
const window={addEventListener:()=>{},webkit:{messageHandlers:{native:{postMessage:()=>{}}}}};
vm.runInNewContext(fs.readFileSync('assets/popup-adapter.js','utf8'),{Elm:{Popup:{init:()=>({ports})}},window,document,requestAnimationFrame:()=>{},Object});
const event=key=>({key,target,preventDefault(){},stopImmediatePropagation(){}});
handlers.keydown(event('Enter'));assert.equal(sent.length,0);handlers.keyup(event('Enter'));assert.equal(sent.length,1);handlers.keyup(event('Enter'));assert.equal(sent.length,1);
handlers.keydown(event('Escape'));node.dataset.publication='8';handlers.keyup(event('Escape'));assert.equal(sent.length,1);
handlers.keydown({...event('Enter'),repeat:true});handlers.keyup(event('Enter'));assert.equal(sent.length,1);
handlers.keydown(event('Tab'));assert.equal(sent.at(-1).id,'control:forward');
node.dataset.mode='overview';const before=sent.length;handlers.keydown(event('Escape'));assert.equal(sent.length,before);handlers.keyup(event('Escape'));assert.equal(sent.length,before+1);assert.equal(sent.at(-1).id,'control:close');handlers.keyup(event('Escape'));assert.equal(sent.length,before+1);
node.dataset.mode='applications';handlers.keydown(event('Escape'));assert.equal(sent.length,before+1);handlers.keyup(event('Escape'));assert.equal(sent.length,before+2);
console.log('Actual shipped routing: terminal release once, stale scope cancels, repeat ignored, cycle observation forwarded');
'''])
  run('compile-switcher',[str(HELD/pinned['compiler']),'make','qa/SwitcherReplay.elm','--optimize','--output=assets/switcher.js'])
  (INPUT/'qa/switcher-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.SwitcherReplay'));run('typed-switcher',['node','qa/switcher-replay.js','assets/switcher.js',str(OUT/'switcher.json')]);report['typedSwitcher']=json.loads((OUT/'switcher.json').read_text());assert all(report['typedSwitcher']['checks'].values())
  run('switcher-model-typecheck',['quint','typecheck','qa/switcher.qnt']);run('switcher-model-named',['quint','test','qa/switcher.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79111']);run('switcher-model-invariants',['quint','run','qa/switcher.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79112'])
 if ACCESSIBILITY:report.update(requirements=['ELM-UX-025'],scenarios=['actual-surface-at'],scope='Actual compiled taskbar button pressed state and switcher listbox selection, names and focus. Native inspector/Orca evidence remains separate.')
 if MOTION:
  report.update(requirements=['ELM-UX-022'],scenarios=['ux-022'],scope='Actual immutable-root motion observation/configuration/ack/retirement replay, native read-only preference observer and changed host compile; native transition recording remains separate.')
  run('compile-motion',[str(HELD/pinned['compiler']),'make','qa/MotionReplay.elm','--optimize','--output=assets/motion.js'])
  (INPUT/'qa/motion-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.MotionReplay'));run('typed-motion',['node','qa/motion-replay.js','assets/motion.js',str(OUT/'motion.json')]);report['typedMotion']=json.loads((OUT/'motion.json').read_text());assert all(report['typedMotion']['checks'].values())
  report['nativePreferenceObserver']=json.loads(run('native-motion-preference',['/usr/bin/python3','-B','qa/check-motion.py']))
  run('motion-model-typecheck',['quint','typecheck','qa/motion-profile.qnt'])
  run('motion-model-named',['quint','test','qa/motion-profile.qnt','--main=motionProfile','--backend=typescript','--match=Test$','--max-samples=1','--seed=79151'])
  run('motion-model-invariants',['quint','run','qa/motion-profile.qnt','--main=motionProfile','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79152'])
 if LIVE:
  report.update(requirements=['ELM-UI-014','ELM-UI-018'],scenarios=['live-motion-minimize','live-motion-restore','live-motion-switcher','live-motion-Task View','motion-enable','motion-overlays','motion-disable'],scope='Actual root persisted override/source precedence and window transaction preservation; private durable storage and strict host admission. Original mid-transition native presentation, overlay fixtures and restart remain separate.')
  run('compile-live-motion',[str(HELD/pinned['compiler']),'make','qa/LiveMotionReplay.elm','--optimize','--output=assets/live-motion.js'])
  (INPUT/'qa/live-motion-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.LiveMotionReplay'));run('typed-live-motion',['node','qa/live-motion-replay.js','assets/live-motion.js',str(OUT/'live-motion.json')]);report['typedLiveMotion']=json.loads((OUT/'live-motion.json').read_text());assert all(report['typedLiveMotion']['checks'].values())
  report['motionStorage']=json.loads(run('motion-store',['/usr/bin/python3','-B','qa/check-live-motion.py']))
  run('live-motion-model-named',['quint','test','qa/motion-profile.qnt','--main=liveMotion','--backend=typescript','--match=Test$','--max-samples=1','--seed=79161'])
  run('live-motion-model-invariants',['quint','run','qa/motion-profile.qnt','--main=liveMotion','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79162'])
 if IME:
  report.update(requirements=['ELM-UX-028'],scenarios=['ime-spike-commit','ime-spike-cancel'],scope='Actual compiled popup composition lifecycle, commit coalescing and field/custody retirement; original native IME candidate and caret evidence remains separate.')
  run('compile-ime',[str(HELD/pinned['compiler']),'make','qa/ImeReplay.elm','--optimize','--output=assets/ime.js'])
  (INPUT/'qa/ime-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.ImeReplay'));run('typed-ime',['node','qa/ime-replay.js','assets/ime.js',str(OUT/'ime.json')]);report['typedIme']=json.loads((OUT/'ime.json').read_text());assert all(report['typedIme']['checks'].values())
  if LAUNCHER:
   report.update(requirements=['ELM-UX-023'],scenarios=['keyboard-launcher'],scope='Shipped Apps terminal-release adapters and actual compiled composition/stale behavior; native keyboard/focus and independent acceptance remain separate.')
   run('launcher-dismissal-routing',['node','qa/launcher-dismissal.js'])
 if TRANSFER:
  report.update(requirements=['ELM-UX-018'],scenarios=['ux-018','transfer-refused','transfer-accepted'],scope='Actual Task View transfer controls and immutable shared transaction/receipt/membership gates; production custody/schema/key checks. Original native transfer/refusal evidence separate.')
  run('compile-transfer',[str(HELD/pinned['compiler']),'make','qa/TransferReplay.elm','--optimize','--output=assets/transfer.js'])
  (INPUT/'qa/transfer-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.TransferReplay'));run('typed-transfer',['node','qa/transfer-replay.js','assets/transfer.js',str(OUT/'transfer.json')]);report['typedTransfer']=json.loads((OUT/'transfer.json').read_text());assert all(report['typedTransfer']['checks'].values())
  report['transferCustody']=json.loads(run('transfer-custody',['/usr/bin/python3','-B','qa/check-transfer-workspace.py']))
  run('transfer-model-typecheck',['quint','typecheck','qa/transfer-workspace.qnt'])
  run('transfer-model-named',['quint','test','qa/transfer-workspace.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79141'])
  run('transfer-model-invariants',['quint','run','qa/transfer-workspace.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79142'])
 if TASKVIEW and not IME:
  run('compile-task-view',[str(HELD/pinned['compiler']),'make','qa/TaskViewReplay.elm','--optimize','--output=assets/task-view.js'])
  (INPUT/'qa/task-view-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.TaskViewReplay'));run('typed-task-view',['node','qa/task-view-replay.js','assets/task-view.js',str(OUT/'task-view.json')]);report['typedTaskView']=json.loads((OUT/'task-view.json').read_text());assert all(report['typedTaskView']['checks'].values())
  run('task-view-model-typecheck',['quint','typecheck','qa/task-view.qnt']);run('task-view-model-named',['quint','test','qa/task-view.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79101']);run('task-view-model-invariants',['quint','run','qa/task-view.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79102'])
 if DRAG:
  report.update(requirements=['ELM-UX-021'],scenarios=['ux-021'],scope='Compiled immutable native pointer ownership/root suppression and strict production decoder; original frozen native_drag invariant model. Actual crossing/native gesture end acceptance separate.')
  run('compile-pointer-ownership',[str(HELD/pinned['compiler']),'make','qa/PointerOwnershipReplay.elm','--optimize','--output=assets/pointer-ownership.js'])
  (INPUT/'qa/pointer-ownership-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.PointerOwnershipReplay'));run('typed-pointer-ownership',['node','qa/pointer-ownership-replay.js','assets/pointer-ownership.js',str(OUT/'pointer-ownership.json')]);report['typedPointerOwnership']=json.loads((OUT/'pointer-ownership.json').read_text());assert all(report['typedPointerOwnership']['checks'].values())
  report['pointerDecoder']=json.loads(run('pointer-decoder',['/usr/bin/python3','-B','qa/check-pointer-ownership.py']))
  drag_model=REPO/'window-behavior-spec/native_drag.qnt';report['frozenDragModel']={'path':str(drag_model),'sha256':sha(drag_model)}
  run('drag-model-typecheck',['quint','typecheck',str(drag_model)])
  run('drag-model-invariants',['quint','run',str(drag_model),'--backend=typescript','--invariants=allProps','--max-samples=100','--max-steps=30','--seed=79135'])
 if KEYBOARD:
  report.update(requirements=['ELM-UX-023'],scenarios=['ux-023','keyboard-launcher','keyboard-taskbar-groups','keyboard-switcher','keyboard-task-view','keyboard-snap-chooser','keyboard-menus','keyboard-settings','keyboard-notifications','keyboard-jump-lists'],scope='Compiled integrated native shortcut reducers and strict admission; epoch/serial/gap/no-replay model. Original physical keyboard-only surface journeys and independent acceptance remain separate.')
  run('shortcut-popup-release',['node','-e',r"""
const fs=require('fs'),vm=require('vm'),assert=require('assert');const handlers={},sent=[];
const node={dataset:{mode:'settings',publication:'7',lease:'2'},isConnected:true,contains:()=>true,querySelectorAll:()=>[{dataset:{surfaceControl:'control:close'},disabled:false}]};
const body={closest:()=>null},document={body,documentElement:{},getElementById:()=>null,querySelector:()=>node,addEventListener:(name,fn)=>{handlers[name]=fn;}};
const ports=new Proxy({},{get:()=>({send:packet=>sent.push(packet),subscribe:()=>{}})}),window={addEventListener:()=>{},webkit:{messageHandlers:{native:{postMessage:()=>{}}}}};
vm.runInNewContext(fs.readFileSync('assets/popup-adapter.js','utf8'),{Elm:{Popup:{init:()=>({ports})}},window,document,requestAnimationFrame:()=>{},Object});
const event=extra=>({key:'Escape',target:body,preventDefault(){},stopImmediatePropagation(){},...extra});
handlers.keydown(event());assert.equal(sent.length,0);handlers.keyup(event());assert.equal(sent.length,1);assert.equal(sent[0].id,'control:close');handlers.keyup(event());assert.equal(sent.length,1);
handlers.keydown(event());node.dataset.publication='8';handlers.keyup(event());assert.equal(sent.length,1);
handlers.keydown(event({isComposing:true}));handlers.keyup(event());assert.equal(sent.length,1);
handlers.keydown(event({repeat:true}));handlers.keyup(event());assert.equal(sent.length,1);
handlers.keydown(event({target:{closest:()=>null}}));handlers.keyup(event());assert.equal(sent.length,1);
console.log('Current body-target Escape releases once; stale scope, preedit, repeat and foreign target refuse');
"""])
  report['shortcutAdmission']=json.loads(run('shortcut-admission',['/usr/bin/python3','-B','qa/check-keyboard-shortcuts.py']))
  run('compile-shortcuts',[str(HELD/pinned['compiler']),'make','qa/KeyboardShortcutsReplay.elm','--optimize','--output=assets/shortcuts.js'])
  (INPUT/'qa/shortcuts-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.KeyboardShortcutsReplay'));run('typed-shortcuts',['node','qa/shortcuts-replay.js','assets/shortcuts.js',str(OUT/'shortcuts.json')]);report['typedShortcuts']=json.loads((OUT/'shortcuts.json').read_text());assert all(report['typedShortcuts']['checks'].values())
  run('shortcut-model-typecheck',['quint','typecheck','qa/keyboard-shortcuts.qnt']);run('shortcut-model-named',['quint','test','qa/keyboard-shortcuts.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79133']);run('shortcut-model-invariants',['quint','run','qa/keyboard-shortcuts.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79134'])
 if ATTENTION:
  report.update(requirements=['ELM-UX-009'],scenarios=['ux-009'],scope='Compiled immutable native attention projection, exact observed family states, actual renderer/browser color/accessible labels. Native urgency and original AT acceptance separate.')
  report['attentionProjection']=json.loads(run('attention-projection',['/usr/bin/python3','-B','qa/check-attention.py']))
  run('compile-attention',[str(HELD/pinned['compiler']),'make','qa/AttentionReplay.elm','--optimize','--output=assets/attention.js'])
  (INPUT/'qa/attention-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.AttentionReplay'));run('typed-attention',['node','qa/attention-replay.js','assets/attention.js',str(OUT/'attention.json')]);report['typedAttention']=json.loads((OUT/'attention.json').read_text());assert all(report['typedAttention']['checks'].values())
 if JUMP:
  report.update(requirements=['ELM-UX-010'],scenarios=['ux-010','jump-list-recent-identity'],scope='Integrated immutable jump lists, exact catalog-declared GIO actions and identity-bound local XBEL recent files; compiled reducer/native adapter/browser evidence, actual native GUI and independent acceptance separate')
  report['jumpListGio']=json.loads(run('jump-list-native-gio',['/usr/bin/python3','-B','qa/check-jump-lists.py']))
  run('compile-jump-lists',[str(HELD/pinned['compiler']),'make','qa/JumpListReplay.elm','--optimize','--output=assets/jump-lists.js'])
  (INPUT/'qa/jump-lists-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.JumpListReplay'));run('typed-jump-lists',['node','qa/jump-lists-replay.js','assets/jump-lists.js',str(OUT/'jump-lists.json')]);report['typedJumpLists']=json.loads((OUT/'jump-lists.json').read_text());assert all(report['typedJumpLists']['checks'].values())
  run('jump-list-model-typecheck',['quint','typecheck','qa/jump-lists.qnt']);run('jump-list-model-named',['quint','test','qa/jump-lists.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79131']);run('jump-list-model-invariants',['quint','run','qa/jump-lists.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79132'])
 if FILES:
  report.update(requirements=['ELM-UX-033'],scenarios=['ux-033'],scope='Integrated Files reducers, folder field/preedit, strict native admission and actual Quickshell protocol fixture. Installed explorer/native GUI acceptance is separate.')
  report['filesProtocol']=json.loads(run('files-protocol',['/usr/bin/python3','-B','qa/check-files.py']))
  run('compile-files',[str(HELD/pinned['compiler']),'make','qa/FilesReplay.elm','--optimize','--output=assets/files.js'])
  (INPUT/'qa/files-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.FilesReplay'));run('typed-files',['node','qa/files-replay.js','assets/files.js',str(OUT/'files.json')]);report['typedFiles']=json.loads((OUT/'files.json').read_text());assert all(report['typedFiles']['checks'].values())
  run('files-model-typecheck',['quint','typecheck','qa/files.qnt']);run('files-model-named',['quint','test','qa/files.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79129']);run('files-model-invariants',['quint','run','qa/files.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79130'])
 if SYSTEM:
  report.update(requirements=['ELM-UX-032'],scenarios=['ux-032'],scope='Current immutable Elm system menu, native capability/outcome admission, actual private audio and D-Bus protocols; physical GUI, hardware and independent acceptance separate')
  run('system-model-typecheck',['quint','typecheck','qa/system-menu.qnt']);run('system-model-named',['quint','test','qa/system-menu.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79127']);run('system-model-invariants',['quint','run','qa/system-menu.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79128'])
  report['systemLifecycle']=json.loads(run('system-providers',['/usr/bin/python3','-B','qa/check-system-menu.py']))
  run('compile-system-menu',[str(HELD/pinned['compiler']),'make','qa/SystemMenuReplay.elm','--optimize','--output=assets/system-menu.js'])
  (INPUT/'qa/system-menu-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.SystemMenuReplay'));run('typed-system-menu',['node','qa/system-menu-replay.js','assets/system-menu.js',str(OUT/'system-menu.json')]);report['typedSystemMenu']=json.loads((OUT/'system-menu.json').read_text());assert all(report['typedSystemMenu']['checks'].values())
 if NOTIFICATIONS:
  report.update(requirements=['ELM-UX-031'],scenarios=['ux-031','notification-valid','notification-reused'],scope='Integrated typed notification center and actual private-D-Bus lifecycle/producer actions; native GUI acceptance remains separate')
  report['notificationLifecycle']=json.loads(run('notification-producers',['/usr/bin/python3','-B','qa/check-notifications.py']))
  run('notification-model-typecheck',['quint','typecheck','qa/notifications.qnt']);run('notification-model-named',['quint','test','qa/notifications.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79125']);run('notification-model-invariants',['quint','run','qa/notifications.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79126'])
  run('compile-notifications',[str(HELD/pinned['compiler']),'make','qa/NotificationsReplay.elm','--optimize','--output=assets/notifications.js'])
  (INPUT/'qa/notifications-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.NotificationsReplay'));run('typed-notifications',['node','qa/notifications-replay.js','assets/notifications.js',str(OUT/'notifications.json')]);report['typedNotifications']=json.loads((OUT/'notifications.json').read_text());assert all(report['typedNotifications']['checks'].values())
 if CONTRAST:report.update(requirements=['ELM-UX-027'],scenarios=['ux-027'],scope='Integrated high contrast theme; actual compiled committed-theme projection, CAS/restart/invalid-theme handling and measured browser content/focus at all supported theme/text-scale fixtures. Native all-surface original qualification remains separate.')
 if SETTINGS:
  report.update(requirements=['ELM-UX-027'] if CONTRAST else ['ELM-UX-030'],scenarios=['ux-027'] if CONTRAST else ['ux-030'],scope='Integrated committed appearance and validated revision-CAS storage; actual native restart and invalid-scale observations remain separate')
  run('settings-store',['/usr/bin/python3','-B','qa/check-settings.py'])
  run('settings-model-typecheck',['quint','typecheck','qa/settings.qnt']);run('settings-model-named',['quint','test','qa/settings.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79123']);run('settings-model-invariants',['quint','run','qa/settings.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79124'])
  run('compile-settings',[str(HELD/pinned['compiler']),'make','qa/SettingsReplay.elm','--optimize','--output=assets/settings.js'])
  (INPUT/'qa/settings-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.SettingsReplay'));run('typed-settings',['node','qa/settings-replay.js','assets/settings.js',str(OUT/'settings.json')]);report['typedSettings']=json.loads((OUT/'settings.json').read_text());assert all(report['typedSettings']['checks'].values())
 if SNAP:
  report.update(requirements=['ELM-UX-019','ELM-UX-020'],scenarios=['ux-019','ux-020'],scope='Compiled integrated snap chooser with generation-bound half/quarter previews and stale action/output invalidation; native placement authority and original isolated recordings remain required')
  run('snap-wire-custody',['/usr/bin/python3','-B','qa/check-snap.py'])
  run('compile-snap',[str(HELD/pinned['compiler']),'make','qa/SnapReplay.elm','--optimize','--output=assets/snap.js'])
  (INPUT/'qa/snap-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.SnapReplay'));run('typed-snap',['node','qa/snap-replay.js','assets/snap.js',str(OUT/'snap.json')]);report['typedSnap']=json.loads((OUT/'snap.json').read_text());assert all(report['typedSnap']['checks'].values())
  run('snap-model-typecheck',['quint','typecheck','qa/snap-chooser.qnt']);run('snap-model-named',['quint','test','qa/snap-chooser.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79121']);run('snap-model-invariants',['quint','run','qa/snap-chooser.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79122'])
 if LAYER:
  run('compile-layer-appearance',[str(HELD/pinned['compiler']),'make','qa/LayerAppearanceReplay.elm','--optimize','--output=assets/layer-appearance.js'])
  (INPUT/'qa/layer-appearance-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.LayerAppearanceReplay'))
  run('typed-layer-appearance',['node','qa/layer-appearance-replay.js','assets/layer-appearance.js',str(OUT/'layer-appearance.json')])
  report['typedLayerAppearance']=json.loads((OUT/'layer-appearance.json').read_text());assert all(report['typedLayerAppearance']['checks'].values())
 if SHORTCUTS:
  registration=json.loads(run('shortcut-registration-model',['/usr/bin/python3','-B','qa/check-shortcut-registration.py']))
  registration_path=pathlib.Path(registration['report']);registration_report=json.loads(registration_path.read_text());assert registration['passed'] and registration_report['passed'];report['shortcutRegistrationModel']={'path':str(registration_path),'sha256':sha(registration_path),'witnessCounts':registration_report['witnessCounts']}
  run('shortcut-preference-store',['/usr/bin/python3','-B','qa/check-shortcut-preferences.py'])
  run('compile-shortcut-preferences',[str(HELD/pinned['compiler']),'make','qa/ShortcutPreferencesReplay.elm','--optimize','--output=assets/shortcut-preferences.js'])
  (INPUT/'qa/shortcut-preferences-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.ShortcutPreferencesReplay'))
  run('typed-shortcut-preferences',['node','qa/shortcut-preferences-replay.js','assets/shortcut-preferences.js',str(OUT/'shortcut-preferences.json')]);report['shortcutPreferences']=json.loads((OUT/'shortcut-preferences.json').read_text());assert all(report['shortcutPreferences']['checks'].values())
  run('shortcut-choice-model-typecheck',['quint','typecheck','qa/shortcut-choices.qnt']);run('shortcut-choice-model-named',['quint','test','qa/shortcut-choices.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79201']);run('shortcut-choice-model-invariants',['quint','run','qa/shortcut-choices.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79202'])
  report.update(requirements=['ELM-UI-020','ELM-UX-023'],scenarios=['first-use','keyboard-settings'],scope='Compiled actual Settings shortcut choices, live conflict/readback admission, private CAS storage and pending/Unknown no-replay; native original keyboard/conflict/restoration, AT and independent acceptance separate.')
 if NAV:
  run('navigation-projection',['/usr/bin/python3','-B','qa/check-navigation-projection.py'])
  run('navigation-model-typecheck',['quint','typecheck','qa/workspace-navigation.qnt']);run('navigation-model-named',['quint','test','qa/workspace-navigation.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79103']);run('navigation-model-invariants',['quint','run','qa/workspace-navigation.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79104'])
 if PINS:
  run('compile-pins',[str(HELD/pinned['compiler']),'make','qa/PinsReplay.elm','--optimize','--output=assets/pins.js'])
  (INPUT/'qa/pins-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.PinsReplay'));run('typed-pins',['node','qa/pins-replay.js','assets/pins.js',str(OUT/'pins.json')]);report['typedPins']=json.loads((OUT/'pins.json').read_text());assert all(report['typedPins']['checks'].values());run('pin-storage',['/usr/bin/python3','-B','qa/check-pin-storage.py'])
  run('pin-model-typecheck',['quint','typecheck','qa/pins.qnt']);run('pin-model-named',['quint','test','qa/pins.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79019']);run('pin-model-invariants',['quint','run','qa/pins.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79020'])
 if PRIMARY and not PINMENUS and not REFLOW:
  previous=json.loads((ROOT/'qa/current-search-build.json').read_text());prior_path=REPO/previous['report'];assert sha(prior_path)==previous['reportSHA256'];prior=json.loads(prior_path.read_text());assert prior['passed']
  old_binary=prior_path.parent/'elm-host';assert sha(old_binary)==prior['binarySHA256']
  assert all(sha(INPUT/p)==h for p,h in prior['inputs'].items() if p.startswith('native/'))
  shutil.copyfile(old_binary,OUT/'elm-host');(OUT/'elm-host').chmod(0o700)
  report['reusedNativeHost']={'report':str(prior_path),'reportSHA256':sha(prior_path),'binarySHA256':sha(old_binary),'reason':'Only Elm presentation changes; every captured native source remains identical.'};report['binarySHA256']=sha(OUT/'elm-host')
 else:
  flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],text=True))
  # Popup-only lifecycle changes still exercise current/closed focus leases.
  run('focus-model-typecheck',['quint','typecheck','qa/focus-publication.qnt'])
  run('focus-model-named',['quint','test','qa/focus-publication.qnt','--backend=typescript','--match=^(pendingSurvivesPublicationTest|issuedNeverReplayedTest|replacementCannotReceiveOldFocusTest|closeCannotReviveFocusTest|staleAckCannotIssueFocusTest)$','--max-samples=1','--seed=79017'])
  run('focus-model-invariants',['quint','run','qa/focus-publication.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79018'])
  if not POPUP:
   run('surface-admission-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','qa/surface-admission.c' if RELEVANCE else 'native/surface-test.c','-o',str(OUT/'surface-tests'),*flags]);run('surface-admission',[str(OUT/'surface-tests')])
  run('host-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/'host.d'),'-c','native/shared-host.c','-o',str(OUT/'host.o'),*flags])
  units=['preview_uri.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp','preview-uri-router.cpp','elm-preview-policy.cpp','preview-visual-channel.cpp','preview-policy-driver.cpp']
  if PINS or POPUP or TASKVIEW or SWITCHER or PINMENUS or REFLOW:
   previous=json.loads((ROOT/'qa/current-search-build.json').read_text());prior_path=REPO/previous['report'];assert sha(prior_path)==previous['reportSHA256'];prior=json.loads(prior_path.read_text());assert prior['passed'] and sha(prior_path.parent/'elm-host')==prior['binarySHA256'];report['reusedNativeObjects']={}
   if SWITCHER:
    # The readonly compositor TU is compiled separately. Reused host objects
    # must retain every dependency except the changed owning host/surface files.
    assert all(sha(INPUT/p)==h for p,h in prior['inputs'].items() if p.startswith('native/') and p not in ['native/host.c','native/shared-host.c','native/surface.h','native/authority.cpp','native/shared-context.h','native/shared-context-test.c'])
    assert all('surface.h' not in (INPUT/'native'/name).read_text() for name in units)
   if POPUP:
    assert all(sha(INPUT/p)==h for p,h in prior['inputs'].items() if p.startswith('native/') and p not in ['native/host.c','native/shared-host.c']+(['native/shared-context.h','native/shared-context-test.c'] if BARRETURN else []))
    assert all(sha(INPUT/'assets'/n)==h for n,h in previous['compiledAssets'].items())
   if PINMENUS or REFLOW:
    # Only the owning GTK host changes; every reused C++ dependency is exact.
    assert all(sha(INPUT/p)==h for p,h in prior['inputs'].items() if p.startswith('native/') and p not in ['native/host.c','native/shared-host.c'])
   if TASKVIEW:
    # The authority TU is independently compiled against its owning core; none
    # of these reused GTK host objects link it or include its modal preflight.
    excluded=['native/surface-test.c','native/surface.h','native/host.c','native/shared-host.c','native/shell-bindings.lua','native/shared-context.h','native/shared-context-test.c']+(['native/authority.cpp','native/navigation-modal.hpp'] if NAV or DRAG else [])+(['native/authority.cpp','native/host-journal.h','native/geometry-effects.inc','native/snap-placement.inc','native/motion-profile.inc','native/geometry.inc'] if SNAP or SETTINGS or NOTIFICATIONS or SYSTEM or FILES or JUMP or ATTENTION or KEYBOARD or TRANSFER or MOTION or PINMAX else [])
    if ANNOUNCEMENTS:
     # This header belongs exclusively to the C host compiled immediately above;
     # every reused C++ source/dependency retains its original exact hash.
     excluded+=['native/announcement-transport.h']
     assert 'native/announcement-transport.h' in (OUT/'host.d').read_text()
     assert all('announcement-transport.h' not in (INPUT/'native'/name).read_text() for name in units)
    if SHORTCUTS:
     excluded+=['native/shortcut-bindings.inc']
     assert all('shortcut-bindings.inc' not in (INPUT/'native'/name).read_text() for name in units)
    assert all(sha(INPUT/p)==h for p,h in prior['inputs'].items() if p.startswith('native/') and p not in excluded)
    assert all('surface.h' not in (INPUT/'native'/name).read_text() for name in units)
   object_path=prior_path;object_report=prior;seen=set()
   while 'reusedNativeHost' in object_report:
    assert object_path not in seen;seen.add(object_path)
    inherited=object_report['reusedNativeHost'];object_path=pathlib.Path(inherited['report']);assert sha(object_path)==inherited['reportSHA256']
    object_report=json.loads(object_path.read_text());assert object_report['passed'] and object_report['binarySHA256']==prior['binarySHA256']
   for name in units:
    assert sha(INPUT/'native'/name)==prior['inputs']['native/'+name]==object_report['inputs']['native/'+name];obj=object_path.parent/(name+'.o');report['reusedNativeObjects'][name]={'sha256':sha(obj),'sourceSHA256':sha(INPUT/'native'/name),'build':str(object_path)};shutil.copyfile(obj,OUT/(name+'.o'))
  else:
   with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    futures=[pool.submit(run,name+'-compile',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-c','native/'+name,'-o',str(OUT/(name+'.o')),*flags]) for name in units]
    for future in futures:future.result()
  run('host-link',['g++',str(OUT/'host.o'),*[str(OUT/(name+'.o')) for name in units],'-o',str(OUT/'elm-host'),*flags]);report['binarySHA256']=sha(OUT/'elm-host')
  if SWITCHER or KEYBOARD or BARRETURN:
   run('popup-context-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-c','native/shared-context-test.c','-o',str(OUT/'popup-context.o'),*flags])
   run('popup-context-link',['g++',str(OUT/'popup-context.o'),*[str(OUT/(name+'.o')) for name in units],'-o',str(OUT/'popup-context-tests'),*flags])
   run('popup-context-tests',[str(OUT/'popup-context-tests')])
 run('host-self-tests',[str(OUT/'elm-host'),'--self-test'])
 if ANNOUNCEMENTS or DESCRIPTION or IME or ACCESSIBILITY or DENSE or SNAP or SETTINGS or NOTIFICATIONS or SYSTEM or FILES or JUMP or ATTENTION:
  if DENSE:report.update(requirements=['ELM-UI-008'],scenarios=['overflow-first-last','overflow-resize','menu-invocation'],scope='Current compiled renderer/adapter dense enlarged-text browser journeys and rebuilt scalable native host; native output/menu/AT observations separate')
  (INPUT/'qa/dense.html').write_text('<!doctype html><html style="font-size:24px"><head><link rel="stylesheet" href="../assets/shell.css"></head><body class="bar"><div id="app"></div><script>window.nativePackets=[];window.webkit={messageHandlers:{native:{postMessage:s=>nativePackets.push(JSON.parse(s))}}};</script><script src="../assets/bar.js"></script><script src="../assets/bar-adapter.js"></script><script src="../assets/context.js"></script><script src="../assets/activation.js"></script></body></html>')
  (INPUT/'qa/dense-picker.html').write_text('<!doctype html><html style="font-size:24px"><head><link rel="stylesheet" href="../assets/shell.css"></head><body class="popup"><div id="app"></div><script>window.nativePackets=[];window.webkit={messageHandlers:{native:{postMessage:s=>nativePackets.push(JSON.parse(s))}}};</script><script src="../assets/popup.js"></script><script src="../assets/popup-adapter.js"></script><script src="../assets/context.js"></script><script src="../assets/activation.js"></script></body></html>')
  if PICKER:report.update(requirements=['ELM-UI-008','ELM-UI-004'],scenarios=['overflow-first-last','overflow-resize','menu-invocation','taskbar-group'],scope='Actual compiled dense picker and bar enlarged-text component navigation, identity, lease, disabled and resize checks; exact unchanged native host reused; native activation/menu/input and AT obligations separate')
  if MENU:report.update(requirements=['ELM-UI-008'],scenarios=['overflow-first-last','menu-invocation'],scope='Actual compiled menu selection/navigation, enlarged text, content growth, disabled rows and bounded viewport reveal; exact unchanged native host reused; original native/AT observations separate')
  if REFLOW:report.update(requirements=['ELM-UI-008'],scenarios=['overflow-resize'],scope='Compiled actual popup reflow policy/retired-lease rejection and dense picker/menu presentation continuity; exact unchanged native host reused; physical output resizing and AT/independent acceptance remain separate')
  class Handler(http.server.SimpleHTTPRequestHandler):
   def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(INPUT),**kwargs)
   def log_message(self,*args):pass
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
  browser=pathlib.Path('/home/hoskinson/.cache/puppeteer/chrome-headless-shell/linux-154.0.8037.57/chrome-headless-shell-linux64/chrome-headless-shell');report['browserSHA256']=sha(browser)
  if DESCRIPTION:
   (INPUT/'qa/preview-description.html').write_text('''<!doctype html><html><head><link rel="stylesheet" href="../assets/shell.css"></head><body class="popup"><div id="app"></div><script src="../assets/preview-renderer.js"></script><script>window.nativePackets=[];window.previewReceipts=[];window.app=Elm.NativePreviewRenderer.init({node:document.getElementById("app"),flags:{channelProtocol:1,kind:"native-preview-renderer-grant",binding:{lifetime:"1",session:"1",frontend:"1"},receiverEpoch:"1",rendererLease:"1",sequenceFloor:"0"}});app.ports.acceptedSnapshots.subscribe(v=>previewReceipts.push(v));app.ports.surfaceActions.subscribe(v=>nativePackets.push(v));window.receiveVisual=v=>app.ports.visualSnapshots.send(v);</script></body></html>''')
   report.update(requirements=['ELM-UI-016'],scenarios=['preview-states'],scope='Compiled ordinary Popup and actual native preview receiver/renderer; passive control descriptions and keyed focus/geometry in Chromium AX component; unchanged producer/ownership model and typed source isolation. Native AT/speech/braille and independent original acceptance remain separate.')
  if ANNOUNCEMENTS:
   (INPUT/'qa/announcement-host.html').write_text('<!doctype html><html><body><iframe id="bar1" src="dense.html"></iframe><iframe id="bar2" src="dense.html"></iframe><iframe id="popup" src="dense-picker.html" style="width:640px;height:620px"></iframe></body></html>')
  if ANNOUNCEMENTS:report.update(requirements=['ELM-UI-010'],scenarios=['announce-launch refusal','announce-transfer refusal','announce-settings validation failure'],scope='Integrated typed refusal identity, Elm-selected announcement ownership, native once-only transport and actual multi-view browser focus/live-region projection; native speech/braille/independent acceptance and permitted notification policy remain separate.')
  if NOTIFICATION_ANNOUNCEMENTS:report.update(requirements=['ELM-UI-010'],scenarios=['announce-notification arrival','announcement-dnd','announcement-urgency-opt-in'],scope='Integrated native urgency facts and Elm session permission, typed/batch/suppression/no-focus and multi-view live-region behavior; actual native GUI/AT and independent acceptance separate.')
  if ADAPTER_ANNOUNCEMENTS:report.update(requirements=['ELM-UI-010'],scenarios=['announce-adapter unavailable'],scope='Matched typed adapter failures, explicit read-only empty notification-service retry, shared polite owner and retained keyed focus; native speech/braille and independent acceptance remain separate.')
  if RELEVANCE:report.update(requirements=['ELM-UI-010'],scenarios=['announce-notification expiration','announce-expired action rejection','announcement-expiration-irrelevant'],scope='Scoped passive focus observation, exact relevant expiry/refusal policy, readonly retained unavailable action and DND/irrelevant/repeat suppression; native speech/braille and independent acceptance remain separate.')
  browser_name='announcement-browser' if ANNOUNCEMENTS else 'preview-description-browser' if DESCRIPTION else 'ime-browser' if IME else 'accessibility-browser' if ACCESSIBILITY else 'attention-browser' if ATTENTION else 'jump-lists-browser' if JUMP else 'files-browser' if FILES else 'system-menu-browser' if SYSTEM else 'notifications-browser' if NOTIFICATIONS else 'settings-browser' if SETTINGS else 'snap-browser' if SNAP else 'dense-browser';browser_runner='announcement-browser.mjs' if ANNOUNCEMENTS else 'preview-description-browser.mjs' if DESCRIPTION else 'ime-browser.mjs' if IME else 'accessibility-browser.mjs' if ACCESSIBILITY else 'attention-browser.mjs' if ATTENTION else 'jump-lists-browser.mjs' if JUMP else 'files-browser.mjs' if FILES else 'system-menu-browser.mjs' if SYSTEM else 'notifications-browser.mjs' if NOTIFICATIONS else 'settings-browser.mjs' if SETTINGS else 'snap-browser.mjs' if SNAP else 'dense-taskbar-browser.mjs'
  run(browser_name,['node','qa/'+browser_runner,'http://127.0.0.1:'+str(server.server_port),str(OUT),str(browser)])
  child_path=OUT/(browser_name+'.json');child=json.loads(child_path.read_text());assert child['passed'] and child['browserExitCode']==0;report['announcementBrowser' if ANNOUNCEMENTS else 'previewDescriptionBrowser' if DESCRIPTION else 'imeBrowser' if IME else 'accessibilityBrowser' if ACCESSIBILITY else 'attentionBrowser' if ATTENTION else 'jumpListsBrowser' if JUMP else 'filesBrowser' if FILES else 'systemMenuBrowser' if SYSTEM else 'notificationsBrowser' if NOTIFICATIONS else 'settingsBrowser' if SETTINGS else 'snapBrowser' if SNAP else 'denseBrowser']={'path':str(child_path),'sha256':sha(child_path),'checks':child['checks']}
  if SNAP:
   run('menu-navigation-regression',['node','qa/dense-taskbar-browser.mjs','http://127.0.0.1:'+str(server.server_port),str(OUT),str(browser)])
   regression=json.loads((OUT/'dense-browser.json').read_text());assert regression['passed'] and regression['browserExitCode']==0;report['menuNavigationRegression']={'path':str(OUT/'dense-browser.json'),'sha256':sha(OUT/'dense-browser.json'),'checks':regression['checks']}
  if LAYER:
   (OUT/'layer-browser').mkdir()
   run('layer-appearance-browser',['node','qa/layer-appearance-browser.mjs','http://127.0.0.1:'+str(server.server_address[1]),str(OUT),str(browser)])
   child_path=OUT/'layer-browser/report.json';child=json.loads(child_path.read_text());assert child['passed'] and child['browserExitCode']==0;report['layerAppearanceBrowser']={'path':str(child_path),'sha256':sha(child_path),'checks':child['checks']}
 assert all(sha(ROOT/p)==h for p,h in inputs.items());toolchain.verify();report['compiledAssets']={n:sha(INPUT/'assets'/n) for n in ['elm.js','bar.js','popup.js']};report['passed']=True
except Exception as error:report['error']=repr(error)
finally:
 if server:server.shutdown();server.server_close()
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
