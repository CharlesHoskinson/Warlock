"""Actual native issuer/receipt/physical owner and native-owned JSC policy/outbox."""
import hashlib,json,os,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('policy-driver-realm-reuse-check-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for base in ['src','native'] for p in (root/base).glob('*') if p.is_file()]+['elm.json','assets/native-preview-control-outbox.js','qa/policy-driver-realm-reuse-roundtrip.js','qa/policy-driver-realm-reuse-check.py','qa/toolchain.py','qa/toolchain.json'];plugin=root.parent/'warlock-family-style-crop-capture-v19/native/capture-resources.hpp';external=sha(plugin)
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'pluginResourceHeaderSHA256':external,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual C/Bootstrap/Native authenticated synthetic peer and sealed-FD two-realm lifecycle through one persistent optimized Elm policy. Exact policy pointer and original Native binding preserved; permanent native Retired21 cannot resurrect in later epoch2, while actual Active22 captures and drains independently. Stale epoch/foreign binding/pre-transfer outbox failure/open-realm replacement/early retirement refused with original custody retained. Two grant-bound native outboxes, sole persistent policy, no grant reset. This CPU/C/JSC evidence does not qualify actual GTK/WebKit close/reopen, real Core image/frame/reveal, process-loss recovery or full release acceptance.'}
def run(name,args,env=None,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',env=env,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 shutil.copy2(plugin,out/'inputs/native/capture-resources.hpp');sys.path.insert(0,str(root/'qa'));from toolchain import verify
 held=verify();shutil.copytree(root/held['elmHome'],out/'mutable-elm-home');policy=out/'policy.js'
 run('optimized-policy',[str(root/held['compiler']),'make','src/NativePreviewPolicy.elm','--optimize','--output='+str(policy)],dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')))
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0','javascriptcoregtk-4.1']));binary=out/'driver'
 run('compile-owner',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/policy-driver-realm-reuse-fixture.cpp','native/preview-policy-driver.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','native/elm-preview-policy.cpp','-o',str(binary),*flags])
 run('driver-syntax',['node','--check','qa/policy-driver-realm-reuse-roundtrip.js'])
 evidence=json.loads(run('native-policy-driver-roundtrip',['node',str(out/'inputs/qa/policy-driver-realm-reuse-roundtrip.js'),str(binary),str(policy),str(out/'inputs/assets/native-preview-control-outbox.js')],cwd=out));assert evidence['passed'] and evidence['nativePolicyInstances']==1 and evidence['nativeTransportInstances']==2 and evidence['rendererWindowPolicies']==0 and evidence['normalOwnedExit'] and evidence['nativeGrantResets']==0
 report['evidence']=evidence;verify();assert sha(plugin)==external and all(sha(root/n)==v for n,v in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])

