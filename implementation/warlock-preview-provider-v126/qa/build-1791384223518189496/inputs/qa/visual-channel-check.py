"""Actual sanitizer native visual custody, persistent JSC and pure Elm receiver."""
import hashlib,json,os,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('visual-channel-check-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for p in (root/'src').glob('*') if p.is_file()]+['elm.json','native/elm-preview-policy.h','native/elm-preview-policy.cpp','native/preview-visual-channel.h','native/preview-visual-channel.cpp','native/visual-channel-fixture.cpp','qa/visual-channel-check.py','qa/visual-channel-roundtrip.js','qa/native-source-fixture.json','qa/toolchain.py','qa/toolchain.json']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Creator/thread and actual GObject-context visual custody with native-issued leases/separate visual sequence, exact pending retries and latest committed cache comparison before acceptance. Actual sanitizer C and one persistent JSC worker coupled to two compiled pure Elm renderer receivers. Native policy grant/close and maximum sequence DTO boundary are explicitly synthetic. GObject contexts are not actual WebKit callback authentication; receipts prove receiver acceptance, not DOM/frame/pixels/physical concealment/freshness between checks. Actual host route and all original native/full release gates remain open.'}
def run(name,args,env=None,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',env=env,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 sys.path.insert(0,str(root/'qa'));from toolchain import verify
 held=verify();shutil.copytree(root/held['elmHome'],out/'mutable-elm-home');env=dict(os.environ,ELM_HOME=str(out/'mutable-elm-home'));compiler=str(root/held['compiler'])
 policy=out/'policy.js';receiver=out/'receiver.js';renderer=out/'renderer.js'
 run('optimized-policy',[compiler,'make','src/NativePreviewPolicy.elm','--optimize','--output='+str(policy)],env)
 run('optimized-receiver',[compiler,'make','src/NativePreviewReceiverReplay.elm','--optimize','--output='+str(receiver)],env)
 run('optimized-renderer',[compiler,'make','src/NativePreviewRenderer.elm','--optimize','--output='+str(renderer)],env)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-2.0','json-glib-1.0','javascriptcoregtk-4.1']));binary=out/'channel'
 run('compile-owner',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/visual-channel-fixture.cpp','native/elm-preview-policy.cpp','native/preview-visual-channel.cpp','-o',str(binary),*flags])
 run('driver-syntax',['node','--check','qa/visual-channel-roundtrip.js'])
 evidence=json.loads(run('native-receiver-roundtrip',['node',str(out/'inputs/qa/visual-channel-roundtrip.js'),str(binary),str(policy),str(receiver),str(out/'inputs/qa/native-source-fixture.json')],cwd=out).splitlines()[-1]);assert evidence['passed'] and evidence['normalOwnedExit'] and evidence['pureRendererInstances']==2 and evidence['rendererWindowPolicies']==0
 report['evidence']=evidence;verify();assert all(sha(root/n)==value for n,value in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and 'mutable-elm-home' not in p.parts and 'elm-stuff' not in p.parts}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
