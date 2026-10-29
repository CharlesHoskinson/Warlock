"""Protected current Elm roots build; no native execution or acceptance."""
import hashlib,json,os,resource,shutil,subprocess,sys,traceback
from pathlib import Path
R=Path('/home/charles/Warlock');P=R/'implementation/warlock';H=R/'implementation/warlock-preview-provider-v143';B=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild');D=Path(__file__).resolve().parent;O=D/'output'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(m):
 for p,h in m.items():
  if sha(p)!=h:raise RuntimeError('Input changed '+str(p))
def main():
 sys.path.insert(0,str(R/'window-integration-qa'));from qa_launch import require_qa_scope
 scope=require_qa_scope()
 if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):raise RuntimeError('Core limit changed')
 O.mkdir(exist_ok=False);report={'passed':False,'nativeAcceptance':False,'requirementAccepted':False,'scope':scope,'commands':[],'driverSHA256':sha(__file__)}
 try:
  pins={H/'qa/toolchain.json':'fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa',B/'arc004-build-terra2-v1/output/report.json':'1c35c3c24cbc2011176affe84191f111bbc96caa4ea32a17ff737dd32f658ef6'};check(pins)
  check({D/'source-pins.json':'0021ebf6911170ccf3e49c510aa6dc09b729b076a96e3184d1a39fbb5b2e27b5'})
  sources=json.loads((D/'source-pins.json').read_text());before=sha(D/'source-pins.json');check(sources)
  if {str(p) for p in (P/'src').rglob('*.elm')}!={p for p in sources if p.startswith(str(P/'src')+'/') and p.endswith('.elm')}:raise RuntimeError('Elm source inventory differs')
  old=json.loads((B/'arc004-build-terra2-v1/output/report.json').read_text());m=json.loads((H/'qa/toolchain.json').read_text());held={str(H/name):v['sha256'] for name,v in m['heldFiles'].items()};check(held)
  compiler=H/m['compiler']
  if sha(compiler)!='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948':raise RuntimeError('Compiler differs')
  static={str(p.relative_to(P/'assets')):sha(p) for p in (P/'assets').rglob('*') if p.is_file() and p.name not in {'elm.js','bar.js','popup.js'}}
  if static!=old['static']:raise RuntimeError('Static asset drift')
  w=O/'workspace';w.mkdir();(w/'src').symlink_to(P/'src',target_is_directory=True);shutil.copyfile(P/'elm.json',w/'elm.json');assets=O/'assets';assets.mkdir()
  for name in static:
   target=assets/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'assets'/name,target)
  home=O/'elm-home';shutil.copytree(H/m['elmHome'],home)
  env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','SOURCE_DATE_EPOCH':'0','PYTHONDONTWRITEBYTECODE':'1','ELM_HOME':str(home)}
  for module,target in [('Main','elm.js'),('Bar','bar.js'),('Popup','popup.js')]:
   argv=[str(compiler),'make','src/'+module+'.elm','--optimize','--output='+str(assets/target)];p=subprocess.run(argv,cwd=w,env=env,capture_output=True,timeout=240)
   out=O/(module+'.stdout');err=O/(module+'.stderr');out.write_bytes(p.stdout);err.write_bytes(p.stderr);report['commands'].append({'module':module,'argv':argv,'cwd':str(w),'environment':env,'exit':p.returncode,'stdoutSHA256':sha(out),'stderrSHA256':sha(err)})
   if p.returncode:raise RuntimeError(module+' compilation failed')
  check(pins);check(sources);check(held)
  if sha(D/'source-pins.json')!=before:raise RuntimeError('Reviewed source pins changed')
  report.update(passed=True,sources=sources,sourcePinsSHA256=before,static=static,compiler={'path':str(compiler),'sha256':sha(compiler)},heldFiles=held,receiptPins={str(p):h for p,h in pins.items()},outputs={str(p):sha(p) for p in assets.rglob('*') if p.is_file()})
 except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
 (O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(O/'report.json'),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
