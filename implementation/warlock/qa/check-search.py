"""Focused compiled launcher/search integration, protected CPU scope only."""
import pathlib,hashlib,json,os,sys,time,shutil,subprocess,shlex,importlib.util,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];HELD=REPO/'implementation/warlock-preview-provider-v143'
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
OUT=ROOT/'qa/runs'/('search-'+str(time.time_ns()));OUT.mkdir(parents=True);INPUT=OUT/'inputs';INPUT.mkdir();inputs={}
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
 for name,target in [('Main','elm'),('Bar','bar'),('Popup','popup')]:run('compile-'+name,[str(HELD/pinned['compiler']),'make','src/'+name+'.elm','--optimize','--output=assets/'+target+'.js'])
 run('compile-search',[str(HELD/pinned['compiler']),'make','qa/SearchReplay.elm','--optimize','--output=assets/search.js'])
 replay=(INPUT/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.SearchReplay');(INPUT/'qa/search-replay.js').write_text(replay)
 run('typed-search',['node','qa/search-replay.js','assets/search.js',str(OUT/'search.json')]);r=json.loads((OUT/'search.json').read_text());assert r['rank']==['z-exact','a-prefix','b-token'] and r['keyword']==['z-exact'] and r['generic']==['b-token','z-exact'] and r['unicode']==['c-unicode'];assert r['refreshClearsSettledRefusal'] and r['refreshPreservesUnknown'];assert r['queryEditHasNoEffects'] and r['staleQueryRejected'] and 'No matching' in r['noMatchStatus'] and r['queryRetained']=='nonexistent';report['typedSearch']=r
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],text=True))
 run('focus-model-typecheck',['quint','typecheck','qa/focus-publication.qnt'])
 run('focus-model-named',['quint','test','qa/focus-publication.qnt','--backend=typescript','--match=^(pendingSurvivesPublicationTest|issuedNeverReplayedTest|replacementCannotReceiveOldFocusTest|closeCannotReviveFocusTest|staleAckCannotIssueFocusTest)$','--max-samples=1','--seed=79017'])
 run('focus-model-invariants',['quint','run','qa/focus-publication.qnt','--backend=typescript','--invariants=safety','--max-samples=100','--max-steps=20','--seed=79018'])
 run('surface-admission-build',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','native/surface-test.c','-o',str(OUT/'surface-tests'),*flags]);run('surface-admission',[str(OUT/'surface-tests')])
 run('host-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-MD','-MF',str(OUT/'host.d'),'-c','native/shared-host.c','-o',str(OUT/'host.o'),*flags])
 units=['preview_uri.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp','preview-uri-router.cpp','elm-preview-policy.cpp','preview-visual-channel.cpp','preview-policy-driver.cpp']
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  futures=[pool.submit(run,name+'-compile',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-c','native/'+name,'-o',str(OUT/(name+'.o')),*flags]) for name in units]
  for future in futures:future.result()
 run('host-link',['g++',str(OUT/'host.o'),*[str(OUT/(name+'.o')) for name in units],'-o',str(OUT/'elm-host'),*flags]);report['binarySHA256']=sha(OUT/'elm-host')
 run('host-self-tests',[str(OUT/'elm-host'),'--self-test']);assert all(sha(ROOT/p)==h for p,h in inputs.items());toolchain.verify();report['compiledAssets']={n:sha(INPUT/'assets'/n) for n in ['elm.js','bar.js','popup.js']};report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
