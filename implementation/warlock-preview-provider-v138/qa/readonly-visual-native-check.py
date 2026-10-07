"""Couple current single optimized Elm policy to actual C/native socket/outbox."""
import hashlib,json,os,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('readonly-visual-native-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for base in ['src','native'] for p in (root/base).glob('*') if p.is_file()]+['elm.json','assets/recovered-native-preview-control-outbox.js','assets/native-preview-proposals.js','qa/readonly-visual-native-roundtrip.js','qa/readonly-visual-native-check.py','qa/toolchain.py','qa/toolchain.json']
plugin=root.parent/'warlock-family-style-crop-capture-v19/native/capture-resources.hpp'
external=sha(plugin)
report={'pluginResourceHeaderSHA256':external,'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Readonly native projection getter invokes no Elm, emits no commands/diagnostic model and allocates no native ordinal. Original207 controls remain unchanged with additive actual optimized worker visual projection roundtripped through a separately compiled pure DTO decoder, never another window policy. No real renderer/DOM/WebKit projection delivery or ordering proof. Actual one native-owned JavaScriptCore context runs compiled retained Elm policy in the actual C fixture creator process, with actual Bootstrap/Native authenticated synthetic peer/broker/receipt journal/native purpose tickets and two recreated JS transport contexts. Two Active-subject epochs on one unchanged grant. No actual WebKit/window/captured FD or full release acceptance.'}
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
 run('compile-c-owner',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/persistent-policy-native-fixture-v4.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','native/elm-preview-policy.cpp','-o',str(out/'checks'),*flags])
 e=json.loads(run('actual-native-elm-outbox',['node','qa/readonly-visual-native-roundtrip.js',str(binary),str(out/'checks'),'assets/recovered-native-preview-control-outbox.js',str(out/'inputs/assets/native-preview-proposals.js'),str(decoder)]))
 assert e['passed'] and e['checks']==207 and e['visualProjectionChecks']==90 and e['readonlyProjectionChecks']>0 and e['rendererWindowPolicyInstances']==0 and e['pureRendererDecoderInstances']==1 and e['nativeOwnedJavaScriptCore'] and e['persistentPolicyContexts']==1 and e['rendererElmInstances']==0 and e['singlePreviewPolicy'] and e['actualControlledC'] and e['normalOwnedExit'] and e['realmEpochs']==2 and e['nativeGrantResets']==0;verify()
 assert sha(plugin)==external and all(sha(root/n)==v for n,v in report['inputs'].items());report.update(passed=True,evidence=e)
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2500]}),flush=True);sys.exit(not report['passed'])
