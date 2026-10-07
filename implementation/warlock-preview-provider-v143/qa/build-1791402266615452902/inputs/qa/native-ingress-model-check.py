"""Explicitly selected ingress traces against the actual compiled C/native owner."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('native-ingress-model-check-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+['qa/native-ingress-model-check.py','qa/native-ingress-refinement.js','spec/native_realm_ingress.qnt','spec/native_realm_ingress_tests.qnt']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Exact realm/proposal ingress admission and native issued frontier compared to actual sanitizer-backed C/Bootstrap/Native authenticated synthetic peer/Broker/purpose reservations. Original actual job/physical status must remain identical before final owned cleanup. No actual WebKit/window or full release acceptance.'}
def run(name,args,cwd=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 prior=next(root.glob('qa/realm-ingress-native-check-*/report.json'));d=json.loads(prior.read_text());assert d['passed'] and d['evidence']['checks']==192
 for rel,v in d['inputs'].items():assert sha(root/rel)==v,rel
 checks=out/'checks';shutil.copy2(prior.parent/'checks',checks);report['compiledControls']={'path':str(prior),'sha256':sha(prior),'binarySHA256':sha(checks)}
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 shutil.copy2(prior.parent/'inputs/native/capture-resources.hpp',out/'inputs/native/capture-resources.hpp')
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'native_realm_ingress_tests.qnt').read_text());assert len(selected)==12
 run('typecheck',[tool,'typecheck','native_realm_ingress_tests.qnt'],folder)
 run('selected',[tool,'test','native_realm_ingress_tests.qnt','--main=native_realm_ingress_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1140011','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
 assert len(list(out.glob('named-*.itf.json')))==12
 run('samples',[tool,'run','native_realm_ingress.qnt','--main=native_realm_ingress','--backend=typescript','--invariant=safety','--seed=1140012','--max-samples=200','--max-steps=25','--n-traces=10','--out-itf='+str(out/'sample-{seq}.itf.json')],folder)
 traces=sorted(out.glob('*.itf.json'));e=json.loads(run('actual-c-refinement',['node','qa/native-ingress-refinement.js',str(checks),*[str(p) for p in traces]]).stdout);assert e['passed'] and all(t['normalOwnedExit'] for t in e['coupledTraces'])
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/realm-ingress-native-fixture.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 variants=[]
 for name,old,new,witness in [
  ('foreign-epoch','message.counter("receiverEpoch")==grant.epoch','message.counter("receiverEpoch")>0','foreignEpochConsumesNoOrdinal'),
  ('foreign-binding','decodeBinding(Json::child(root,"binding"))==owner->native.binding()','decodeBinding(Json::child(root,"binding")).lifetime.value>0','foreignBindingConsumesNoOrdinal'),
  ('extra-header','Json::fields(root,{"previewProtocol","kind","binding","receiverEpoch","entries"});',';','extraHeaderConsumesNoOrdinal'),
  ('aggregate-partial-issue','json_array_get_length(entries)==1','json_array_get_length(entries)>=1','aggregateCannotPartiallyIssue'),
  ('oversized-ingress','strlen(envelope)<=4096','strlen(envelope)<=65536','oversizedIngressConsumesNoOrdinal')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/'native/imported-clients.cpp';s=p.read_text();assert s.count(old)==1,(name,s.count(old));p.write_text(s.replace(old,new));changed=[*args];changed[changed.index('-o')+1]=str(target/'checks');run(name+'-compile',changed,target)
  trace=next(out.glob('named-'+witness+'-*.itf.json'));r=run(name+'-witness',['node','qa/native-ingress-refinement.js',str(target/'checks'),str(trace)],target,False)
  assert r.returncode==1 and 'AssertionError' in r.stderr and witness in r.stderr,(name,r.stderr);variants.append({'name':name,'compiled':True,'witness':witness,'originalAdmissionMismatch':True})
 assert all(sha(root/n)==v for n,v in report['inputs'].items());report.update(passed=True,namedScenarios=12,selectedNames=selected,invariantSamples=200,evidence=e,unsafeCompiledNativeVariantsDetected=5,variants=variants)
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
