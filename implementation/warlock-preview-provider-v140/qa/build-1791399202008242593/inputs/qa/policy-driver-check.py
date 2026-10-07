"""Actual native issuer/receipt/physical owner and native-owned JSC policy/outbox."""
import hashlib,json,os,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('policy-driver-check-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for base in ['src','native'] for p in (root/base).glob('*') if p.is_file()]+['elm.json','assets/native-preview-control-outbox.js','qa/policy-driver-roundtrip.js','qa/policy-driver-check.py','qa/toolchain.py','qa/toolchain.json'];plugin=root.parent/'warlock-family-style-crop-capture-v19/native/capture-resources.hpp';external=sha(plugin)
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'pluginResourceHeaderSHA256':external,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual creator-owned native driver integrates original single optimized Elm policy and unchanged native-issued outbox in private JSC contexts. Original Native/C Bootstrap/authenticated synthetic peer/Broker/receipt journal/purpose allocator/strict close. Input custody atomic and native epoch stamped before JS; original ticket retained before issued fact and native dispatch; JS callbacks defer effects/independent confirmation; Unknown capture remains until actual terminal/detachment processing.1065 ordinary inputs retained while urgent quarantine stays admissible. No actual WebKit/captured FD/window/physical concealment/process-loss recovery or measured resource/full release acceptance. Private diagnostic output remains native/QA only.'}
def run(name,args,env=None,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',env=env,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 shutil.copy2(plugin,out/'inputs/native/capture-resources.hpp');sys.path.insert(0,str(root/'qa'));from toolchain import verify
 held=verify();shutil.copytree(root/held['elmHome'],out/'mutable-elm-home');policy=out/'policy.js'
 run('optimized-policy',[str(root/held['compiler']),'make','src/NativePreviewPolicy.elm','--optimize','--output='+str(policy)],dict(os.environ,ELM_HOME=str(out/'mutable-elm-home')))
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0','javascriptcoregtk-4.1']));binary=out/'driver'
 run('compile-owner',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/policy-driver-fixture.cpp','native/preview-policy-driver.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','native/elm-preview-policy.cpp','-o',str(binary),*flags])
 run('driver-syntax',['node','--check','qa/policy-driver-roundtrip.js'])
 evidence=json.loads(run('native-policy-driver-roundtrip',['node',str(out/'inputs/qa/policy-driver-roundtrip.js'),str(binary),str(policy),str(out/'inputs/assets/native-preview-control-outbox.js')],cwd=out));assert evidence['passed'] and evidence['nativePolicyInstances']==1 and evidence['nativeTransportInstances']==1 and evidence['rendererWindowPolicies']==0 and evidence['normalOwnedExit'] and evidence['nativeGrantResets']==0
 report['evidence']=evidence;verify();assert sha(plugin)==external and all(sha(root/n)==v for n,v in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
