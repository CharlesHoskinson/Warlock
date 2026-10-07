"""Compile native recovery guard variants against the original C/JS witnesses."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('recovery-native-variants-v2-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+['assets/recovered-native-preview-control-outbox.js','qa/native-outbox-recovery-roundtrip-v3.js','qa/recovery-native-variants-v2.py']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'variants':[],'nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,args,cwd,required=True):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0'],out/'inputs').stdout)
 for name,old,new,witness in [
  ('ignore-captured-confirmation','confirmed==o.controlDelivery.confirmed','confirmed<=o.controlDelivery.confirmed','Actual changed confirmed frontier invalidates old page'),
  ('ignore-recovery-epoch','sender_epoch && sender_epoch==o.epoch,"Original renderer realm before recovery inventory"','sender_epoch>0,"Original renderer realm before recovery inventory"','Foreign recovery epoch refuses'),
  ('change-recovered-native-bytes','.text("wire",state.next->wire)','.text("wire",state.next->wire+" ")','Actual native recovery original bytes')]:
  folder=out/name;shutil.copytree(out/'inputs',folder);p=folder/'native/imported-clients.cpp';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  binary=folder/'checks';run(name+'-compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/native-outbox-recovery-fixture.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(binary),*flags],folder)
  p=run(name+'-witness',['node','qa/native-outbox-recovery-roundtrip-v3.js','assets/recovered-native-preview-control-outbox.js',str(binary)],folder,False)
  assert p.returncode==1 and 'AssertionError' in p.stderr and witness in p.stderr,(name,p.stderr)
  report['variants'].append({'name':name,'compiled':True,'namedObservableMismatch':True,'witness':witness})
 assert all(sha(root/rel)==v for rel,v in report['inputs'].items());report.update(passed=True,unsafeCompiledNativeVariantsDetected=3)
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1600]}));sys.exit(not report['passed'])
