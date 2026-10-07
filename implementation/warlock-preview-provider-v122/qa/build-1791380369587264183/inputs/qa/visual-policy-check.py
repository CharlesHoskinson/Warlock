"""Couple current single optimized Elm policy to actual C/native socket/outbox."""
import hashlib,json,os,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('visual-policy-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for base in ['src','native'] for p in (root/base).glob('*') if p.is_file()]+['elm.json','assets/recovered-native-preview-control-outbox.js','assets/native-preview-proposals.js','qa/visual-policy-checks.js','qa/visual-policy-check.py','qa/toolchain.py','qa/toolchain.json','qa/native-source-fixture.json']
plugin=root.parent/'warlock-family-style-crop-capture-v19/native/capture-resources.hpp'
external=sha(plugin)
report={'pluginResourceHeaderSHA256':external,'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual native-owned optimized C/JSC Elm worker with client/family live, historical, locked-unavailable and quarantined/detached hidden visual projections roundtripped through a pure compiled DTO decoder. Native ticket, offer, scope, terminal and close facts are explicitly synthetic. Preview concealment retains original Unknown/retiring resources; no actual DOM/captured FD or native/full release acceptance.'}
def run(name,args,env=None):
 p=subprocess.run(args,cwd=out/'inputs',env=env,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 shutil.copy2(plugin,out/'inputs/native/capture-resources.hpp')
 sys.path.insert(0,str(root/'qa'));from toolchain import verify
 held=verify();shutil.copytree(root/held['elmHome'],out/'mutable-elm-home')
 binary=out/'realm.js';run('optimized-elm',[str(root/held['compiler']),'make','src/NativePreviewPolicy.elm','--optimize','--output='+str(binary)],dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')))
 decoder=out/'visual-decoder.js';run('optimized-visual-decoder',[str(root/held['compiler']),'make','src/NativePreviewVisualReplay.elm','--optimize','--output='+str(decoder)],dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')))
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0','javascriptcoregtk-4.1']))
 run('compile-c-owner',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/persistent-policy-lifetime-fixture.cpp','native/elm-preview-policy.cpp','-o',str(out/'checks'),*flags])
 e=json.loads(run('actual-jsc-visual-policy',['node','qa/visual-policy-checks.js',str(binary),str(out/'checks'),str(decoder),'qa/native-source-fixture.json']))
 assert e['passed'] and e['actualNativeOwnedJSC'] and e['singleWindowPolicyPerFixture'] and e['syntheticNativeFacts'] and e['normalOwnedExits']==2 and not e['actualDOM'] and not e['actualCapturedFD'];verify()
 assert sha(plugin)==external and all(sha(root/n)==v for n,v in report['inputs'].items());report.update(passed=True,evidence=e)
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2500]}),flush=True);sys.exit(not report['passed'])
