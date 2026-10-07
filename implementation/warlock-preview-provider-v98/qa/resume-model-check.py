"""Explicitly selected native intent/deadline traces against actual ledger/allocator."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('resume-model-check-'+str(time.time_ns()));OUT.mkdir()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'native').glob('*') if p.is_file()}
for rel in ['spec/resume.qnt','spec/resume_tests.qnt','qa/resume-model-check.py','qa/resume-checks.cpp']:inputs[rel]=sha(ROOT/rel)
for rel in inputs:
 target=OUT/'inputs'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
report={'passed':False,'scope':scope,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'projection':'Actual retained resume helper, original receiver mutex guard, native Broker reservation/proof/floor and intent cutoff; synthetic native clock/scope, no real capture or whole ImportedClients refinement','fixedFixture':{'binding':[1,2,3],'incarnations':[11,12,13],'clock':10,'nativeNow':4,'resumeCutoff':2000000004,'oldJobDeadline':100,'items':2,'bytes':64},'toolSHA256':sha(TOOL.resolve())}
def run(name,argv,cwd=None,input=None):
 p=subprocess.run(argv,cwd=cwd or OUT,capture_output=True,text=True,timeout=180,input=input)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout
 return p
def decode(v):
 if isinstance(v,list):return [decode(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
 return v
try:
 flags=shlex.split(run('gio-flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 binary=OUT/'checks';folder=OUT/'inputs/spec';source=OUT/'inputs/qa/resume-checks.cpp'
 run('compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(OUT/'inputs/native'),str(source),str(OUT/'inputs/native/preview_uri.cpp'),'-o',str(binary),*flags])
 run('quint-typecheck',[str(TOOL),'typecheck','resume_tests.qnt'],cwd=folder)
 names=re.findall(r'run (\w+)\s*=',(folder/'resume_tests.qnt').read_text());assert len(names)==len(set(names))==8;report['selectedNames']=names
 run('quint-named',[str(TOOL),'test','resume_tests.qnt','--main=resume_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=621001','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(OUT.glob('named-*.itf.json')))==8
 run('quint-sampling',[str(TOOL),'run','resume.qnt','--main=resume','--backend=typescript','--invariant=safety','--seed=621002','--max-samples=150','--max-steps=35','--n-traces=16','--out-itf='+str(OUT/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];traceInputs={}
 for trace in sorted(OUT.glob('*.itf.json')):
  states=[row['s'] for row in decode(json.loads(trace.read_text()))['states']];events=states[-1]['history'];wanted=[];length=0
  for state in states:
   if len(state['history'])==length:continue
   length=len(state['history']);wanted.append({k:v for k,v in state.items() if k!='history'})
  stdin='\n'.join(events)+'\n';p=run('replay-'+trace.stem,[str(binary)],input=stdin);assert not p.stderr;actual=[json.loads(line) for line in p.stdout.splitlines()];assert actual==wanted,(trace.name,actual,wanted)
  traces.append({'trace':trace.name,'statesCompared':len(actual)});traceInputs[trace.name]=(stdin,wanted)
 assert len(traces)==24;report['coupledTraces']=traces
 mutants=[('native/imported_lifecycle.hpp','expired-resume','if(intent->deadline<=s.now)return {ImportedIntentLedger::Admission::Expired,{},"[]"};','if(false)return {ImportedIntentLedger::Admission::Expired,{},"[]"};','expiryAfterCapacityReturn'),('native/imported_enrollment.hpp','reused-receiver','return view && epoch && view->epoch==epoch && view->binding==owner;','return view && epoch && view->binding==owner;','replacedReceiverBeforeQuery'),('qa/resume-checks.cpp','unknown-rejection','known=result.native.job.has_value();','known=result.native.status==demand::Attempt::Status::Started;','actualIssuedRejectionKnown')];caught=[]
 for filename,name,old,new,witness in mutants:
  original=(OUT/'inputs'/filename).read_text();assert original.count(old)==1
  mutant=OUT/name;shutil.copytree(OUT/'inputs',mutant);(mutant/filename).write_text(original.replace(old,new,1))
  run(name+'-compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-I'+str(mutant/'native'),str(mutant/'qa/resume-checks.cpp'),str(mutant/'native/preview_uri.cpp'),'-o',str(mutant/'checks'),*flags])
  matches=[key for key in traceInputs if witness in key];assert len(matches)==1;stdin,wanted=traceInputs[matches[0]]
  p=subprocess.run([str(mutant/'checks')],capture_output=True,text=True,input=stdin,timeout=30)
  (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
  actual=[json.loads(line) for line in p.stdout.splitlines()];assert p.returncode!=0 or actual!=wanted,(name,'unsafe mutant escaped actual trace oracle');caught.append({'name':name,'trace':matches[0],'differentObservableState':True,'exitCode':p.returncode})
 report['mutants']=caught;assert all(sha(ROOT/rel)==h for rel,h in inputs.items());report.update(passed=True,namedScenarios=8,invariantSamples=150,statesCompared=sum(x['statesCompared'] for x in traces),unsafeMutantsDetected=3)
except Exception as exc:report['error']=repr(exc)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
