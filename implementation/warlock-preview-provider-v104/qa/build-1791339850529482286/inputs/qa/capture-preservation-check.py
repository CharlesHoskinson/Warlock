"""Actual retained capture intent and sealed mapping adoption exception witnesses."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('capture-preservation-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()};inputs[str(pathlib.Path(__file__).relative_to(root))]=sha(pathlib.Path(__file__))
report={'passed':False,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual ImportedClients/native controlled tickets on authenticated synthetic socket retain immutable capture request/context/deadline across native refusal, malformed completion and unavailable FD transport, forbid acquisition replay and preserve unresolved Broker charge without invented final proofs. Actual sealed local mappings and Broker adoption test refusal, success, pre-transfer allocator exception and post-transfer receipt allocation exception with original local FD/proof drain. No real core pixels/capture FD, backend reconciliation, live-binding detachment/WebKit or full release acceptance.'}
def run(name,args,cwd=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in inputs:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 common=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative']
 native=[*common,'native/capture-intent-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'capture-checks'),*flags]
 allocation=[*common,'native/imported-allocation-test.cpp','-o',str(out/'allocation-checks'),*flags]
 run('capture-compile',native);capture=json.loads(run('capture-witnesses',[str(out/'capture-checks')]).stdout);assert capture['passed'] and capture['normalOwnedExit'] and capture['retainedUnknownCases']==3
 run('allocation-compile',allocation);adoption=json.loads(run('allocation-witnesses',[str(out/'allocation-checks')]).stdout);assert adoption['passed'] and adoption['allocationCases']==4
 mutants=[]
 for name,header,old,new,args,witness in [
  ('forget-original-intent-on-capture-error','native/imported_clients.hpp','f.attempted=true;f.capture=captureClient(authority_->native,*f.captureIntent);','f.attempted=true;try{f.capture=captureClient(authority_->native,*f.captureIntent);}catch(...){f.captureIntent.reset();throw;}',native,'Original request and deadline retained across capture exception'),
  ('publish-caller-mapping-before-adoption','native/client_import.hpp','try {\n        auto result=broker.allocate(entry,job,payload,expires);','retained=candidate;\n    try {\n        auto result=broker.allocate(entry,job,payload,expires);',allocation,'Pre-transfer allocation exception cannot retain caller mapping'),
  ('forget-mapping-after-committed-adoption-error','native/client_import.hpp','}catch(...) {\n        if(!payload)retained=candidate;\n        throw;','}catch(...) {\n        throw;',allocation,'Post-transfer receipt allocation exception retains actual Broker mapping')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/header;s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  changed=[*args];changed[changed.index('-o')+1]=str(target/'checks');run(name+'-compile',changed,target)
  result=run(name+'-witness',[str(target/'checks')],target,False);assert result.returncode!=0 and witness in result.stderr.splitlines(),(name,result.stderr)
  mutants.append({'name':name,'compiled':True,'failedOriginalAssertion':witness})
 assert all(sha(root/rel)==value for rel,value in inputs.items())
 report.update(passed=True,captureEvidence=capture,allocationEvidence=adoption,unsafeCompiledVariantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1400]}),flush=True);sys.exit(not report['passed'])
