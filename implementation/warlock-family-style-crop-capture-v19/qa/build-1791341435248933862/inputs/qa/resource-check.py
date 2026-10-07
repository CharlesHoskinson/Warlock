"""Compile and exercise the actual original native capture resource engine."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('resource-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()};inputs[str(pathlib.Path(__file__).relative_to(root))]=sha(pathlib.Path(__file__))
report={'passed':False,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual native resource engine operating on owned producer/export records and real sealed export descriptors; independent export/producer state, idempotent lost-ack cleanup, lock barriers, different current capture preservation, exact target/plane/binding/transfer, allocation-before-mutation and sequence exhaustion. No real compositor capture pixels/FD import, authenticated protocol/native GUI or full release acceptance.'}
def run(name,args,cwd=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in inputs:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0']).stdout)
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/capture-resources-test.cpp','-o',str(out/'checks'),*flags]
 run('compile',args);proof=json.loads(run('resource-witnesses',[str(out/'checks')]).stdout);assert proof['passed'] and proof['actualExportDescriptorsClosed']==2
 mutants=[]
 for name,old,new,witness in [
  ('retire-original-producer-under-lock','else if(locked)result.status=Status::PendingLock;','else if(locked && false)result.status=Status::PendingLock;','Original producer remains owned under lock'),
  ('retire-different-current-capture','if(probe.request==target.capture) {','if(probe.request) {','Original absent target cannot erase another current capture'),
  ('release-before-native-response-construction','auto output=std::forward<Prepare>(prepare)(result);','if(release)found->second.exported.reset();\n    auto output=std::forward<Prepare>(prepare)(result);','Failed native response construction precedes resource mutation')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/'native/capture-resources.hpp';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  changed=[*args];changed[changed.index('-o')+1]=str(target/'checks');run(name+'-compile',changed,target)
  result=run(name+'-witness',[str(target/'checks')],target,False);assert result.returncode!=0 and witness in result.stderr.splitlines(),(name,result.stderr)
  mutants.append({'name':name,'compiled':True,'failedOriginalAssertion':witness})
 assert all(sha(root/rel)==value for rel,value in inputs.items());report.update(passed=True,evidence=proof,unsafeCompiledVariantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1400]}),flush=True);sys.exit(not report['passed'])
