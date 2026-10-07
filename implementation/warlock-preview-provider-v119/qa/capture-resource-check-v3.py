"""Actual controlled C/socket capture reconciliation and strict decoder witnesses."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];plugin=root.parent/'warlock-family-style-crop-capture-v19'
out=root/'qa'/('capture-resource-check-v3-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(root)):sha(p) for p in (root/'native').glob('*') if p.is_file()}
inputs[str(pathlib.Path(__file__).relative_to(root))]=sha(pathlib.Path(__file__))
external={'capture-resources.hpp':sha(plugin/'native/capture-resources.hpp')}
report={'passed':False,'inputs':inputs,'pluginInputs':external,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual native controlled C admission/ticket/dispatcher/receipt/journal and GUI105 ImportedClients on authenticated synthetic socket using actual plugin19 resource engine/wire and owned export descriptors. Original pre-FD capture Unknown, malformed/lost release/retire ACK, locks and fair neighbor cleanup, no capture replay, permanent incarnation/proof/control barriers; strict lossless resource decoder. No compositor pixels, real capture FD import, WebKit or GUI release acceptance.'}
def run(name,args,cwd=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel in inputs:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 for name in external:shutil.copy2(plugin/'native'/name,out/'inputs/native'/name)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 common=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative']
 cargs=[*common,'native/capture-resource-c-test-v2.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'c-checks'),*flags]
 dargs=[*common,'native/capture-resource-decoder-test.cpp','-o',str(out/'decoder-checks'),*flags]
 run('c-compile',cargs);cevidence=json.loads(run('c-witnesses',[str(out/'c-checks')]).stdout)
 assert cevidence['passed'] and cevidence['normalOwnedExit'] and cevidence['resourceCases']==6
 run('decoder-compile',dargs);devidence=json.loads(run('decoder-witnesses',[str(out/'decoder-checks')]).stdout)
 assert devidence['passed'] and devidence['normalOwnedExit']
 mutants=[]
 for name,header,old,new,args,witness in [
  ('poll-before-receipt-capability-check','native/imported-clients.cpp','o.value.actorCounts(o.popup,*static_cast<ReceiptDelivery*>(delivery),o.subjects);\n        if(o.controlled)o.value.pollReconciliation(o.controlGrant(popup));','if(o.controlled)o.value.pollReconciliation(o.controlGrant(popup));',cargs,'Foreign receipt capability refuses before original native resource cleanup'),
  ('accept-foreign-resource-target','native/client_resources.hpp','reply.counter("subjectIncarnation")==scope.context.incarnation.value','reply.counter("subjectIncarnation")>0',dargs,'Malformed original native resource reply cannot partially advance cursor'),
  ('retire-unresolved-capture-without-backend-zero','native/imported_clients.hpp','if(!f.resources->backendEmpty())return false;','if(!f.resources->backendEmpty() && false)return false;',cargs,'Locked or malformed native evidence retains original charge without final proof'),
  ('replay-old-acquisition-during-resource-poll','native/imported_clients.hpp','observe(ClientResourceOperation::Observe,0);','try{captureClient(authority_->native,*f.captureIntent);}catch(...){}\n        observe(ClientResourceOperation::Observe,0);',cargs,'Unknown original acquisition remains unreplayed after backend settlement')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/header;s=p.read_text();assert s.count(old)==1,(name,s.count(old));p.write_text(s.replace(old,new))
  changed=[*args];changed[changed.index('-o')+1]=str(target/'checks');run(name+'-compile',changed,target)
  result=run(name+'-witness',[str(target/'checks')],target,False)
  assert result.returncode!=0 and witness in result.stderr.splitlines(),(name,result.stderr)
  mutants.append({'name':name,'compiled':True,'failedOriginalAssertion':witness})
 assert all(sha(root/rel)==wanted for rel,wanted in inputs.items())
 assert all(sha(plugin/'native'/name)==wanted for name,wanted in external.items())
 report.update(passed=True,cEvidence=cevidence,decoderEvidence=devidence,unsafeCompiledVariantsDetected=len(mutants),mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1400]}),flush=True);sys.exit(not report['passed'])
