"""Detect compiled C boundary regressions with original actual socket witnesses."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('imported-controlled-c-mutations-v2-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=root/'qa/imported-controlled-c-check-v3-1791338427936183521/report.json'
report={'passed':False,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Five compiled unsafe native C variants must fail actual original socket fixture assertions. Raw command bypass, unowned valid command ticket, receipt access after core exit, actor/control close barrier and readiness JSON reconstruction. Compiler errors and sanitizer failures alone never count as detection. Same original260 metadata actors/1041 native issued tickets, no real capture/FD/WebKit/live-binding detachment or native release acceptance.'}
def run(name,args,cwd,required=True):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 proof=json.loads(baseline.read_text());assert proof['passed'] and proof['controls'][0]['actorsTurnedOver']==260 and proof['controls'][0]['nativeIssuedPrefix']==1041
 for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
 for rel,value in proof['artifacts'].items():assert sha(baseline.parent/rel)==value,rel
 report['baseline']={'path':str(baseline),'sha256':sha(baseline)}
 report['inputs']={**proof['inputs'],str(pathlib.Path(__file__).relative_to(root)):sha(pathlib.Path(__file__))}
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0'],root).stdout)
 reconstruct='auto wire=Wire().text("kind","retire-ready").begin("binding").binding(owner_).end().counter("subject",original.subject.value).counter("observationRequest",original.request).counter("observationSequence",original.sequence).finish();'
 mutations=[
  ('raw-command-bypass','native/imported-clients.cpp','command && !o.controlled','command',['Actual C refusal reported']),
  ('accept-unowned-valid-ticket','native/imported-clients.cpp','owner->native.binding()==binding && owner->controlBank->ownsTicket(grant,ordinal,ticket)','owner->native.binding()==binding',['Actual C refusal reported','Changed valid command cannot invoke native-owned ordinal']),
  ('require-live-core-for-original-receipt','native/imported-clients.cpp','(!liveCore || native.binding()==binding)','((void)liveCore,native.binding()==binding)',['Actual native C dispatcher return and independent receipt']),
  ('close-before-actor-control-confirmation','native/imported-clients.cpp','(!owner->controlled || owner->value.canCloseControlBinding(owner->controlDelivery.grant))','true',['Broker proof drain alone cannot close native actor/control ownership']),
  ('reconstruct-original-ready-bytes','native/retirement_journal.hpp','auto wire=row->second.acceptedReady;',reconstruct,['Actual C polling resumes exact accepted readiness'])]
 rows=[]
 for name,header,old,new,witnesses in mutations:
  target=out/name;shutil.copytree(baseline.parent/'inputs',target)
  p=target/header;s=p.read_text();assert s.count(old)==1,(name,s.count(old));p.write_text(s.replace(old,new))
  args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/imported-controlled-c-test-v3.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(target/'checks'),*flags]
  run(name+'-compile',args,target)
  result=run(name+'-witness',[str(target/'checks')],target,False)
  detected=[v for v in witnesses if v in result.stderr.splitlines()]
  assert result.returncode!=0 and detected,(name,result.stdout,result.stderr)
  rows.append({'name':name,'compiled':True,'failedOriginalAssertion':detected,'compilerOrSanitizerFailureAloneAccepted':False})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,unsafeCompiledVariantsDetected=5,mutants=rows)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1400]}),flush=True);sys.exit(not report['passed'])
