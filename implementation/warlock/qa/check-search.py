"""Focused compiled launcher/search integration, protected CPU scope only."""
import pathlib,hashlib,json,os,sys,time,shutil,subprocess,shlex,importlib.util,concurrent.futures
PRIMARY=sys.argv[1:]==['--taskbar-primary']
SWITCHER=sys.argv[1:]==['--switcher']
NAV=sys.argv[1:]==['--workspace-navigation'];PINS=sys.argv[1:]==['--pins'];POPUP=sys.argv[1:]==['--native-popup'];TASKVIEW=sys.argv[1:]==['--task-view'] or NAV;assert not sys.argv[1:] or PINS or POPUP or TASKVIEW or PRIMARY or SWITCHER
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];HELD=REPO/'implementation/warlock-preview-provider-v143'
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
OUT=ROOT/'qa/runs'/(('switcher-' if SWITCHER else 'taskbar-primary-' if PRIMARY else 'workspace-navigation-' if NAV else 'task-view-' if TASKVIEW else 'popup-' if POPUP else 'pins-' if PINS else 'search-')+str(time.time_ns()));OUT.mkdir(parents=True);INPUT=OUT/'inputs';INPUT.mkdir();inputs={}
for folder in ['src','native','adapter','assets','qa']:
 (INPUT/folder).mkdir()
 for p in (ROOT/folder).iterdir():
  if p.is_file():shutil.copyfile(p,INPUT/folder/p.name);inputs[str(p.relative_to(ROOT))]=sha(p)
info=json.loads((ROOT/'elm.json').read_text());info['source-directories']=['src','qa'];(INPUT/'elm.json').write_text(json.dumps(info))
spec=importlib.util.spec_from_file_location('search_toolchain',HELD/'qa/toolchain.py');toolchain=importlib.util.module_from_spec(spec);spec.loader.exec_module(toolchain);pinned=toolchain.verify();shutil.copytree(HELD/pinned['elmHome'],OUT/'elm-home');env={**os.environ,'ELM_HOME':str(OUT/'elm-home')}
report={'passed':False,'scope':'Compiled Elm query/ranking, native scoped field admission and current integrated host; native keyboard/AT release acceptance pending','requirements':['ELM-UI-005','ELM-UX-029'],'inputs':inputs,'commands':[],'protectedScope':scope,'nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,args):
 p=subprocess.run(args,cwd=INPUT,env=env,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p.stdout
try:
 if SWITCHER:report.update(requirements=['ELM-UI-003','ELM-UX-012','ELM-UX-013'],scope='Compiled real switcher/root/view, bounded release/Ready/ordinal reducer and current native-history admission; global chord, native focus/AT and atomic cancellation remain separately unverified')
 if PRIMARY:report.update(requirements=['ELM-UI-004'],scope='Compile current taskbar state labels and integrated Elm roots; unchanged native host reused by exact source/binary hashes; actual pointer/keyboard/AT acceptance separate')
 if PINS:report.update(requirements=['ELM-UI-004','ELM-UX-004'],scope='Compiled identity pins/reorder, private atomic native persistence, current integrated host; native restart/pixels acceptance pending')
 if POPUP:report.update(requirements=['ELM-UI-005','ELM-UX-029','ELM-UX-004'],scope='Changed native popup presentation units compiled/relinked; previously verified compiled Elm assets reused unchanged; actual native pixels acceptance pending')
 if TASKVIEW:report.update(requirements=['ELM-UX-017','ELM-UI-006'],scope='Compiled integrated Task View, workspace membership/active marker and guarded native selection; native pixels/input and original acceptance remain separate')
 if NAV:report.update(requirements=['ELM-UI-002','ELM-UI-006','ELM-UX-008'],scope='Compiled exact current off-workspace choice/restore replay and coherent scene admission; bounded navigation/refusal/no-replay model; separately compiled authority and actual native journeys required')
 if not POPUP:
  for name,target in [('Main','elm'),('Bar','bar'),('Popup','popup')]:run('compile-'+name,[str(HELD/pinned['compiler']),'make','src/'+name+'.elm','--optimize','--output=assets/'+target+'.js'])
  run('compile-search',[str(HELD/pinned['compiler']),'make','qa/SearchReplay.elm','--optimize','--output=assets/search.js'])
  replay=(INPUT/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.SearchReplay');(INPUT/'qa/search-replay.js').write_text(replay)
  run('typed-search',['node','qa/search-replay.js','assets/search.js',str(OUT/'search.json')]);r=json.loads((OUT/'search.json').read_text());assert r['rank']==['z-exact','a-prefix','b-token'] and r['keyword']==['z-exact'] and r['generic']==['b-token','z-exact'] and r['unicode']==['c-unicode'];assert r['refreshClearsSettledRefusal'] and r['refreshPreservesUnknown'];assert r['queryEditHasNoEffects'] and r['staleQueryRejected'] and 'No matching' in r['noMatchStatus'] and r['queryRetained']=='nonexistent';report['typedSearch']=r
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
console.log('Actual shipped routing: terminal release once, stale scope cancels, repeat ignored, cycle observation forwarded');
'''])
  run('compile-switcher',[str(HELD/pinned['compiler']),'make','qa/SwitcherReplay.elm','--optimize','--output=assets/switcher.js'])
  (INPUT/'qa/switcher-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.SwitcherReplay'));run('typed-switcher',['node','qa/switcher-replay.js','assets/switcher.js',str(OUT/'switcher.json')]);report['typedSwitcher']=json.loads((OUT/'switcher.json').read_text());assert all(report['typedSwitcher']['checks'].values())
  run('switcher-model-typecheck',['quint','typecheck','qa/switcher.qnt']);run('switcher-model-named',['quint','test','qa/switcher.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79111']);run('switcher-model-invariants',['quint','run','qa/switcher.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79112'])
 if TASKVIEW:
  run('compile-task-view',[str(HELD/pinned['compiler']),'make','qa/TaskViewReplay.elm','--optimize','--output=assets/task-view.js'])
  (INPUT/'qa/task-view-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.TaskViewReplay'));run('typed-task-view',['node','qa/task-view-replay.js','assets/task-view.js',str(OUT/'task-view.json')]);report['typedTaskView']=json.loads((OUT/'task-view.json').read_text());assert all(report['typedTaskView']['checks'].values())
  run('task-view-model-typecheck',['quint','typecheck','qa/task-view.qnt']);run('task-view-model-named',['quint','test','qa/task-view.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79101']);run('task-view-model-invariants',['quint','run','qa/task-view.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79102'])
 if NAV:
  run('navigation-projection',['/usr/bin/python3','-B','qa/check-navigation-projection.py'])
  run('navigation-model-typecheck',['quint','typecheck','qa/workspace-navigation.qnt']);run('navigation-model-named',['quint','test','qa/workspace-navigation.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79103']);run('navigation-model-invariants',['quint','run','qa/workspace-navigation.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79104'])
 if PINS:
  run('compile-pins',[str(HELD/pinned['compiler']),'make','qa/PinsReplay.elm','--optimize','--output=assets/pins.js'])
  (INPUT/'qa/pins-replay.js').write_text(replay.replace('Elm.SearchReplay','Elm.PinsReplay'));run('typed-pins',['node','qa/pins-replay.js','assets/pins.js',str(OUT/'pins.json')]);report['typedPins']=json.loads((OUT/'pins.json').read_text());assert all(report['typedPins']['checks'].values());run('pin-storage',['/usr/bin/python3','-B','qa/check-pin-storage.py'])
  run('pin-model-typecheck',['quint','typecheck','qa/pins.qnt']);run('pin-model-named',['quint','test','qa/pins.qnt','--backend=typescript','--match=Test$','--max-samples=1','--seed=79019']);run('pin-model-invariants',['quint','run','qa/pins.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79020'])
 if PRIMARY:
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
   run('surface-admission-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/surface-test.c','-o',str(OUT/'surface-tests'),*flags]);run('surface-admission',[str(OUT/'surface-tests')])
  run('host-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/'host.d'),'-c','native/shared-host.c','-o',str(OUT/'host.o'),*flags])
  units=['preview_uri.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp','preview-uri-router.cpp','elm-preview-policy.cpp','preview-visual-channel.cpp','preview-policy-driver.cpp']
  if PINS or POPUP or TASKVIEW or SWITCHER:
   previous=json.loads((ROOT/'qa/current-search-build.json').read_text());prior_path=REPO/previous['report'];assert sha(prior_path)==previous['reportSHA256'];prior=json.loads(prior_path.read_text());assert prior['passed'] and sha(prior_path.parent/'elm-host')==prior['binarySHA256'];report['reusedNativeObjects']={}
   if SWITCHER:
    # The readonly compositor TU is compiled separately. Reused host objects
    # must retain every dependency except the changed owning host/surface files.
    assert all(sha(INPUT/p)==h for p,h in prior['inputs'].items() if p.startswith('native/') and p not in ['native/host.c','native/shared-host.c','native/surface.h','native/authority.cpp'])
    assert all('surface.h' not in (INPUT/'native'/name).read_text() for name in units)
   if POPUP:
    assert all(sha(INPUT/p)==h for p,h in prior['inputs'].items() if p.startswith('native/') and p not in ['native/host.c','native/shared-host.c'])
    assert all(sha(INPUT/'assets'/n)==h for n,h in previous['compiledAssets'].items())
   if TASKVIEW:
    # The authority TU is independently compiled against its owning core; none
    # of these reused GTK host objects link it or include its modal preflight.
    excluded=['native/surface.h']+(['native/authority.cpp','native/navigation-modal.hpp'] if NAV else [])
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
 run('host-self-tests',[str(OUT/'elm-host'),'--self-test']);assert all(sha(ROOT/p)==h for p,h in inputs.items());toolchain.verify();report['compiledAssets']={n:sha(INPUT/'assets'/n) for n in ['elm.js','bar.js','popup.js']};report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
