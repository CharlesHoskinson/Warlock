"""Actual Native/C/Endpoint realm replacement, failed construction and stale ticket gates."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('preview-realm-c-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()};inputs[str(pathlib.Path(__file__).relative_to(root))]=sha(pathlib.Path(__file__))
report={'passed':False,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual controlled C factory/original Native socket/Endpoint/Broker/retirement/control close. Same Native binding survives two successive controlled owners on reused receiver pointer with distinct native realm epochs; source-refused constructor consumes intermediate epoch, old exact same-binding ticket refuses before new handler, every original physical/proof/actor/processing/control close barrier remains. Closed controlled mode cannot become legacy. Fresh controlled near-exhaustion derivative tests lossless uint64 final epoch and refusal before later admission. No live-window detachment or WebKit/native GUI acceptance.'}
def run(name,args,cwd=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in inputs:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/preview-realm-c-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',args);normal=json.loads(run('actual-realm-replacement',[str(out/'checks')]).stdout)
 assert normal['passed'] and normal['failedConstructionEpochConsumed'] and normal['nativeRealmEpochThrough']=='3' and normal['normalOwnedExit']
 exhausted=out/'exhaustion';shutil.copytree(out/'inputs',exhausted);p=exhausted/'native/preview_client.hpp';s=p.read_text();old='std::atomic_uint64_t previewRealmThrough_{0};';assert s.count(old)==1;p.write_text(s.replace(old,'std::atomic_uint64_t previewRealmThrough_{UINT64_MAX-1};'))
 changed=[*args];changed[changed.index('-o')+1]=str(exhausted/'checks');run('exhaustion-compile',changed,exhausted);last=json.loads(run('actual-realm-exhaustion',[str(exhausted/'checks'),'exhaustion'],exhausted).stdout)
 assert last['passed'] and last['exhaustion'] and last['nativeRealmEpochThrough']==str(2**64-1) and last['normalOwnedExit']
 mutants=[]
 for name,header,old,new,witness in [
  ('reset-receiver-epoch-at-endpoint-replacement','native/imported-clients.cpp','endpoint.registerControlView(popup,binding,controlClaim->epoch())','endpoint.registerControlView(popup,binding)','Native realm epoch survives endpoint replacement and failed construction'),
  ('allow-controlled-to-legacy-downgrade','native/preview_client.hpp','!owner.previewRealmThrough_.load(std::memory_order_acquire) && ','','Closed controlled realm cannot downgrade to legacy ownership'),
  ('release-published-claim-on-refused-close','native/imported-clients.cpp','try {require(warlock_imported_clients_empty(owner),','try {if(owner->controlled)owner->controlClaim->complete();require(warlock_imported_clients_empty(owner),','Published realm claim survives refused original close')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/header;s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new));changed=[*args];changed[changed.index('-o')+1]=str(target/'checks');run(name+'-compile',changed,target)
  failed=run(name+'-witness',[str(target/'checks')],target,False);assert failed.returncode!=0 and witness in failed.stderr.splitlines(),(name,failed.stderr)
  mutants.append({'name':name,'compiled':True,'failedOriginalAssertion':witness})
 assert all(sha(root/rel)==v for rel,v in inputs.items())
 report.update(passed=True,evidence=normal,exhaustionEvidence=last,unsafeCompiledVariantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1800]}),flush=True);sys.exit(not report['passed'])
