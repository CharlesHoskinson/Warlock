"""Couple current single optimized Elm policy to actual C/native socket/outbox."""
import hashlib,json,os,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retained-ingress-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for p in (root/'src').glob('*') if p.is_file()]+['elm.json','qa/retained-ingress-checks.js','qa/retained-ingress-check.py','qa/native-source-fixture.json','qa/toolchain.py','qa/toolchain.json']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Current compiled retained Presenter wrapper delegates all window/lifecycle policy to the original PreviewPresenter. Native-issued facts are synthetic decoder stimuli; actual C coupling is qualified separately. No actual WebKit/window or full release acceptance.'}
def run(name,args,env=None):
 p=subprocess.run(args,cwd=out/'inputs',env=env,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 sys.path.insert(0,str(root/'qa'));from toolchain import verify
 held=verify();shutil.copytree(root/held['elmHome'],out/'mutable-elm-home')
 binary=out/'realm.js';run('optimized-elm',[str(root/held['compiler']),'make','src/RetainedPreviewPresenterReplay.elm','--optimize','--output='+str(binary)],dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')))
 e=json.loads(run('retained-boundaries',['node','qa/retained-ingress-checks.js',str(binary),'qa/native-source-fixture.json']))
 assert e['passed'] and e['singlePreviewPolicy'];verify()
 assert all(sha(root/n)==v for n,v in report['inputs'].items());report.update(passed=True,evidence=e)
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2500]}),flush=True);sys.exit(not report['passed'])
