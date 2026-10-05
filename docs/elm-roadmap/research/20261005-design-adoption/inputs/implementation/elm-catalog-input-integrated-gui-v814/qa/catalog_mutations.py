import hashlib,json,os,pathlib,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
from toolchain import verify
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'qa'/('catalog-mutations-'+str(time.time_ns()));out.mkdir();checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,args,cwd,expected=True):
 p=subprocess.run(args,cwd=cwd,env=dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')),capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 checks.append({'name':name,'args':args,'exitCode':p.returncode});assert (p.returncode==0)==expected,p.stdout+p.stderr
 if not expected:assert 'AssertionError' in p.stdout+p.stderr or 'assertion failed' in (p.stdout+p.stderr).lower(),p.stdout+p.stderr
 return p.stdout
try:
 tc=verify();shutil.copytree(root/tc['elmHome'],out/'mutable-elm-home')
 controls=sorted(p.parent for p in (root/'qa').glob('catalog-controls-*/report.json') if json.loads(p.read_text()).get('passed'))[-1];assert json.loads((controls/'report.json').read_text())['passed']
 for p in [controls/'worker.js',controls/'baseline-worker.js',controls/'probe',controls/'effect-controls.json',controls/'ready-events.json',root/'qa/catalog-controls.cjs']:
  shutil.copy2(p,out/p.name)
 mutations=[
  ('ignore-current-request','Desktop.elm','model.expected==Just request','True'),
  ('remint-current-popup-lease','OutputController.elm','refuseCatalogs (Just batch.lease) batch.catalogs settled','refuseCatalogs (lease model.controller) batch.catalogs settled'),
  ('omit-local-catalog-proof','OutputController.elm','refuseCatalogs (lease model.controller) catalogs settled','(settled,[])'),
  ('ignore-exact-native-wire','OutputController.elm','&& batch.wire==certificate.wire','&& True')]
 for name,filename,old,new in mutations:
  directory=out/name;directory.mkdir();shutil.copytree(root/'src',directory/'src');shutil.copy2(root/'elm.json',directory/'elm.json')
  target=directory/'src'/filename;text=target.read_text();assert text.count(old)==1;target.write_text(text.replace(old,new))
  (directory/'mutation.json').write_text(json.dumps({'file':filename,'old':old,'new':new,'sha256':sha(target)},indent=2)+'\n')
  run(name+'-compile',[str(root/tc['compiler']),'make','src/BatchReplay.elm','--optimize','--output='+str(directory/'worker.js')],directory)
  run(name+'-counterexample',['node',str(out/'catalog-controls.cjs'),str(directory/'worker.js'),str(out/'ready-events.json'),str(out/'baseline-worker.js'),str(out/'probe'),str(out/'effect-controls.json'),str(directory/'packet.json'),str(directory/'controls.json')],directory,False)
  assert sha(target)==json.loads((directory/'mutation.json').read_text())['sha256']
 directory=out/'uncertain-popup-classification';directory.mkdir();shutil.copytree(controls/'inputs/native',directory/'native');(directory/'qa').mkdir();shutil.copy2(root/'qa/catalog-probe.c',directory/'qa/catalog-probe.c')
 target=directory/'native/host.c';text=target.read_text();old='if (open && !popup_open()) return SURFACE_PREFLIGHT_UNSENT;';assert text.count(old)==1;target.write_text(text.replace(old,'if (open && !popup_open()) return SURFACE_UNCERTAIN;'));(directory/'mutation.json').write_text(json.dumps({'sha256':sha(target),'old':old},indent=2)+'\n')
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],directory))
 run('uncertain-popup-classification-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','qa/catalog-probe.c','-o',str(directory/'probe'),*flags],directory)
 run('uncertain-popup-classification-counterexample',[str(directory/'probe'),str(controls/'packet.json'),'catalog'],directory,False)
 verify();report={'passed':True,'checks':checks,'nativeAcceptance':False,'scope':'Four actual compiled Elm guard/source mutants and one actual C classification mutant rejected by preserved original/candidate controls; source retained per mutation, no product or frozen-source mutation'}
except Exception as error:report={'passed':False,'checks':checks,'error':repr(error),'nativeAcceptance':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json');sys.exit(not report['passed'])
