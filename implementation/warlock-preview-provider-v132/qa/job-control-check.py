"""Compare explicitly selected Quint job-control traces with actual native issuer."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('job-control-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+['spec/job_control.qnt','spec/job_control_tests.qnt',str(pathlib.Path(__file__).relative_to(root))]
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Native typed job-control proposal issuance compared after every explicitly selected and sampled Quint event against actual ImportedClients/owning Coordinator/Broker, authenticated synthetic source socket, C prefix and exact terminal ACK effects. Original immutable tickets, proof-only native slots, absent-record retries, unconfirmed resume barrier, bounded confirmed predecessor and no namespace reset. No capture, WebKit/renderer, actor/host close, hardware or full release acceptance.'}
def run(name,args,stdin=None,cwd=None):
 p=subprocess.run(args,input=stdin,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
def decode(v):
 if isinstance(v,list):return [decode(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
 return v
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/job-control-replay.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',args)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'job_control_tests.qnt').read_text());assert len(selected)==15
 run('typecheck',[tool,'typecheck','job_control_tests.qnt'],cwd=folder)
 run('selected',[tool,'test','job_control_tests.qnt','--main=job_control_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1010031','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==15
 run('samples',[tool,'run','job_control.qnt','--main=job_control','--backend=typescript','--invariant=safety','--seed=1010032','--max-samples=100','--max-steps=30','--n-traces=8','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];witnesses={}
 for path in sorted(out.glob('*.itf.json')):
  states=[v['s'] for v in decode(json.loads(path.read_text()))['states']];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({k:v for k,v in state.items() if k!='history'})
  stdin='\n'.join(states[-1]['history'])+'\n'
  actual=[json.loads(v) for v in run('replay-'+path.stem,[str(out/'checks')],stdin).splitlines()]
  assert actual==wanted,(path.name,actual,wanted)
  traces.append({'trace':path.name,'statesCompared':len(actual)});witnesses[path.name]=(stdin,wanted)
 mutants=[]
 for name,header,old,new,witness in [
  ('forget-exact-live-retry','native/imported_control_admission.hpp','if(auto retry=controls_.retry(grant_,active->second.reservation,body))','if(auto retry=std::optional<ControlReservations::Ticket>{})','postEffectAckRetryRetainsOriginal'),
  ('discard-confirmed-predecessor','native/imported_control_admission.hpp','confirmed_.insert_or_assign(entry,std::move(previous));','(void)previous;','exactConfirmedPredecessorIsDelivered'),
  ('claim-unconfirmed-predecessor','native/control_reservations.hpp','(void)slot;if(ordinal>channel_.confirmed)return {};','(void)slot;','unconfirmedAckCannotReleaseCredits'),
  ('reuse-confirmed-old-invocation','native/imported_control_admission.hpp','if(controls_.exactBody(grant_,ticket,body))return Proposal{ticket,true};','if(controls_.exactBody(grant_,ticket,body))return Proposal{ticket,false};','exactConfirmedPredecessorIsDelivered')]:
  changed=out/name;shutil.copytree(out/'inputs',changed);p=changed/header;s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  mutant=[*args];mutant[mutant.index('-o')+1]=str(changed/'checks');run(name+'-compile',mutant,cwd=changed)
  path=next(v for v in witnesses if witness in v);stdin,wanted=witnesses[path]
  actual=[json.loads(v) for v in run(name+'-replay',[str(changed/'checks')],stdin).splitlines()]
  assert actual!=wanted;mutants.append({'name':name,'compiled':True,'witness':path,'differentObservableState':True})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,selectedNames=selected,namedScenarios=15,invariantSamples=100,coupledTraces=traces,statesCompared=sum(v['statesCompared'] for v in traces),unsafeMutantsDetected=4,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:900]}),flush=True);sys.exit(not report['passed'])
