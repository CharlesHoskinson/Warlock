"""Actual compiled host input custody against original Native/C/JSC driver."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('controlled-host-custody-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=root/'qa/build-1791379533615874579';prior=json.loads((base/'report.json').read_text());assert prior['passed'] and len(prior['commands'])==118
names=[str(p.relative_to(root)) for directory in ['src','native'] for p in (root/directory).glob('*') if p.is_file()]+['elm.json','assets/native-preview-control-outbox.js','qa/controlled-host-custody.py','qa/controlled-host-custody-fixture.c','qa/policy-driver-host-custody-fixture.cpp','qa/policy-driver-host-custody-roundtrip.js']
objects=['preview_uri.cpp','preview-uri-router.cpp','preview_icons.cpp','preview-uri-webkit.cpp','preview-provider-bootstrap.cpp','client-producer.cpp','imported-clients.cpp','elm-preview-policy.cpp','preview-visual-channel.cpp','preview-policy-driver.cpp']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'priorBuild':{'path':str(base/'report.json'),'sha256':sha(base/'report.json')},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual shared-host.c queue/flush compiled as C, linked to the current real native policy driver and original Native/C issuer/physical/journal/closure with synthetic sealed-FD peer. Exact original full1065 input queue forces host WOULD_BLOCK, preserves identical producer bytes, then actual driver progress permits that same host input. Original positive driver oracle and strict owned close remain. Added C/C++ fixtures are sanitized; inherited full program native object code retains original build flags. No GTK/WebKit function is exercised by this CPU fixture; no actual GUI, workload/RSS or physical reveal acceptance.'}
def run(name,args,cwd):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 for n,h in prior['inputs'].items():assert sha(root/n)==h,n
 for n,h in prior['artifacts'].items():assert sha(base/n)==h,n
 for category in ['compilerDependencies','linkedLibraries','tools']:
  for n,row in prior[category].items():assert sha(pathlib.Path(n))==row['sha256'],n
 for n in names:
  p=out/'inputs'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/n,p)
 shutil.copy2(root.parent/'warlock-family-style-crop-capture-v19/native/capture-resources.hpp',out/'inputs/native/capture-resources.hpp')
 compiled={}
 for n in objects:
  original=base/(n+'.o');target=out/(n+'.o');compiled[n]=sha(original);shutil.copy2(original,target);assert sha(target)==compiled[n]
 report['originalCompiledObjects']=compiled
 shutil.copy2(base/'inputs/assets/native-preview-policy.js',out/'policy.js')
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0'],out))
 cwd=out/'inputs';shared_flags=['-O1','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative']
 run('compile-actual-host-custody',['cc','-std=c11',*shared_flags,'-c','qa/controlled-host-custody-fixture.c','-o',str(out/'host-custody.o'),*flags],cwd)
 binary=out/'driver';run('link-actual-host-native-driver',['g++','-std=c++20',*shared_flags,'qa/policy-driver-host-custody-fixture.cpp',str(out/'host-custody.o'),*[str(out/(n+'.o')) for n in objects],'-o',str(binary),*flags],cwd)
 evidence=json.loads(run('original-positive-and-host-pressure',['node',str(cwd/'qa/policy-driver-host-custody-roundtrip.js'),str(binary),str(out/'policy.js'),str(cwd/'assets/native-preview-control-outbox.js')],out));assert evidence['passed'] and evidence['checks']==2263 and evidence['preGrantFaultChecks']==9 and evidence['normalOwnedExit'] and evidence['normalOwnedPeerExit'] and evidence['nativeGrantResets']==0
 report['evidence']=evidence;report['actualCompiledHostInputPressureQualified']=True
 assert all(sha(root/n)==h for n,h in report['inputs'].items());assert all(sha(base/(n+'.o'))==h for n,h in compiled.items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
