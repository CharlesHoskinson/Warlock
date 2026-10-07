"""Focused ELM-UI-007 component build/browser check, protected launcher only."""
import hashlib,http.server,json,os,pathlib,resource,shutil,subprocess,sys,threading,time,importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];HELD=REPO/'implementation/warlock-preview-provider-v143'
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa/runs'/str(time.time_ns());OUT.mkdir(parents=True);INPUT=OUT/'inputs';INPUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'ANCESTRY.json').read_text());inputs={}
for folder in ['src','assets','qa']:
 (INPUT/folder).mkdir()
 for p in (ROOT/folder).iterdir():
  if p.is_file():shutil.copy2(p,INPUT/folder/p.name);inputs[str(p.relative_to(ROOT))]=sha(p)
info=json.loads((ROOT/'elm.json').read_text());info['source-directories']=['src','qa'];(INPUT/'elm.json').write_text(json.dumps(info))
spec=importlib.util.spec_from_file_location('held_toolchain',HELD/'qa/toolchain.py');toolchain=importlib.util.module_from_spec(spec);spec.loader.exec_module(toolchain);pinned=toolchain.verify()
shutil.copytree(HELD/pinned['elmHome'],OUT/'elm-home');env=dict(os.environ,ELM_HOME=str(OUT/'elm-home'))
report={'schema':1,'requirements':['ELM-UI-007'],'scenarios':['restore-pending','restore-refused','restore-unknown'],'scope':'Actual compiled Elm policy projection and browser rendering; no native/AT acceptance','nativeAcceptance':False,'fullReleaseAccepted':False,'passed':False,'commands':[],'inputs':inputs,'protectedScope':scope,'heldCompilerSHA256':pinned['compilerSHA256']};server=None

def run(name,command):
 toolchain.verify();p=subprocess.run(command,cwd=INPUT,env=env,capture_output=True,text=True,timeout=120);toolchain.verify();(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p
try:
 for name,target in [('Main','elm'),('Bar','bar'),('Popup','popup')]:run('compile-'+name,[str(HELD/pinned['compiler']),'make','src/'+name+'.elm','--optimize','--output=assets/'+target+'.js'])
 run('compile-feedback',[str(HELD/pinned['compiler']),'make','qa/FeedbackReplay.elm','--optimize','--output=assets/feedback.js'])
 run('typed-feedback',['node','qa/feedback-replay.js','assets/feedback.js',str(OUT/'feedback.json')])
 rows=json.loads((OUT/'feedback.json').read_text());states={r['status']:r for r in rows}
 assert 'applying' in states['Pending']['frame']['status']
 assert 'refused' in states['Refused']['frame']['status']
 assert 'not confirmed' in states['Unknown']['frame']['status']
 assert states['Unknown']['unresolved']==1 and states['Committed']['unresolved']==0
 assert len({states[s]['frame']['status'] for s in ['Pending','Refused','Unknown']})==3
 # No native/effect/dispatch implementation changed in this presentation repair.
 unchanged=[p for p in manifest['parentSources'] if p.startswith('native/') or p in ['src/Effects.elm','src/Shell.elm','src/TaskbarShell.elm','src/Launch.elm','src/SurfaceController.elm']]
 assert all(sha(ROOT/p)==manifest['parentSources'][p] for p in unchanged)
 report['inheritedAuthoritySourcesUnchanged']=unchanged
 (INPUT/'qa/feedback.json').write_text(json.dumps(rows))
 (INPUT/'qa/baseline.css').write_bytes((HELD/'assets/shell.css').read_bytes())
 (INPUT/'qa/feedback.html').write_text('<!doctype html><html><head><link rel="stylesheet" href="../assets/shell.css"></head><body class="bar"><div id="app"></div><script src="../assets/bar.js"></script><script>window.testApp=Elm.Bar.init({node:document.getElementById("app")});window.actions=[];testApp.ports.actions.subscribe(v=>actions.push(v));window.submitSurfaceAction=v=>testApp.ports.requestAction.send(v);</script><script src="../assets/activation.js"></script></body></html>')
 class Handler(http.server.SimpleHTTPRequestHandler):
  def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(INPUT),**kwargs)
  def log_message(self,*args):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 browser=pathlib.Path('/home/hoskinson/.cache/puppeteer/chrome-headless-shell/linux-154.0.8037.57/chrome-headless-shell-linux64/chrome-headless-shell');report['browserSHA256']=sha(browser)
 run('browser',['node','qa/feedback-browser.mjs','http://127.0.0.1:'+str(server.server_port),str(OUT),str(browser)])
 child=json.loads((OUT/'browser-report.json').read_text());assert child['passed'] and child['browserExitCode']==0;report['browserReport']={'path':str(OUT/'browser-report.json'),'sha256':sha(OUT/'browser-report.json'),'checks':child['checks']}
 assert all(sha(ROOT/p)==v for p,v in inputs.items())
 BUILD=ROOT/'.build';BUILD.mkdir(exist_ok=True);dest=BUILD/'assets';shutil.copytree(INPUT/'assets',dest,dirs_exist_ok=True)
 report['compiledAssets']={p.name:sha(p) for p in dest.iterdir() if p.is_file()}
 report['passed']=True
except Exception as e:report['error']=repr(e)
finally:
 if server:server.shutdown();server.server_close()
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
