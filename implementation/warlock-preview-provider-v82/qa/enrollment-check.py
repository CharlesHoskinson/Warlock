"""Explicitly selected native intent/deadline traces against actual ledger/allocator."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('enrollment-check-'+str(time.time_ns()));OUT.mkdir()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'native').glob('*') if p.is_file()}
for rel in ['spec/enrollment.qnt','spec/enrollment_tests.qnt','qa/enrollment-check.py','qa/enrollment-checks.cpp']:inputs[rel]=sha(ROOT/rel)
for rel in inputs:
 target=OUT/'inputs'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
report={'passed':False,'scope':scope,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'projection':'Actual atomic Endpoint.nativeDemandView receiver epoch and membership plus reserveImportedIntent/Ledger original identity/deadline and native demand/Broker reservation state for three fixed own actors sharing two items. Native producer/clock fixture is synthetic; this is not real capture, Native transport, new ImportedClients concrete-field refinement, GIO or whole product evidence. Actual mapped-resource paths are qualified separately.','fixedFixture':{'binding':[1,2,3],'incarnations':[11,12,13],'clock':10,'initialNativeNow':3,'originalDeadline':20,'firstTwoDeadlines':100,'items':2,'bytes':64},'toolSHA256':sha(TOOL.resolve())}
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
 binary=OUT/'checks';folder=OUT/'inputs/spec';source=OUT/'inputs/qa/enrollment-checks.cpp'
 run('compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(OUT/'inputs/native'),str(source),str(OUT/'inputs/native/preview_uri.cpp'),'-o',str(binary),*flags])
 run('quint-typecheck',[str(TOOL),'typecheck','enrollment_tests.qnt'],cwd=folder)
 names=re.findall(r'run (\w+)\s*=',(folder/'enrollment_tests.qnt').read_text());assert len(names)==len(set(names))==8;report['selectedNames']=names
 run('quint-named',[str(TOOL),'test','enrollment_tests.qnt','--main=enrollment_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=621001','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(OUT.glob('named-*.itf.json')))==8
 run('quint-sampling',[str(TOOL),'run','enrollment.qnt','--main=enrollment','--backend=typescript','--invariant=safety','--seed=621002','--max-samples=150','--max-steps=35','--n-traces=16','--out-itf='+str(OUT/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];traceInputs={}
 for trace in sorted(OUT.glob('*.itf.json')):
  states=[row['s'] for row in decode(json.loads(trace.read_text()))['states']];events=states[-1]['history'];wanted=[];length=0
  for state in states:
   if len(state['history'])==length:continue
   length=len(state['history']);wanted.append({k:v for k,v in state.items() if k!='history'})
  stdin='\n'.join(events)+'\n';p=run('replay-'+trace.stem,[str(binary)],input=stdin);assert not p.stderr;actual=[json.loads(line) for line in p.stdout.splitlines()];assert actual==wanted,(trace.name,actual,wanted)
  traces.append({'trace':trace.name,'statesCompared':len(actual)});traceInputs[trace.name]=(stdin,wanted)
 assert len(traces)==24;report['coupledTraces']=traces
 original={name:(OUT/'inputs/native'/name).read_text() for name in ['imported_admission.hpp','imported_enrollment.hpp']};mutants=[('imported_admission.hpp','changed-intent','if(prior!=intents_.end() && prior->second!=intent)return Admission::Conflict;','if(prior!=intents_.end() && false)return Admission::Conflict;','changedDeadlineRefused'),('imported_admission.hpp','expired-intent','if(intent.deadline<=nativeNow)return Admission::Expired;','if(false)return Admission::Expired;','expiredIntentNotRevived'),('imported_enrollment.hpp','reused-receiver','return view && epoch && view->epoch==epoch && view->binding==owner;','return view && epoch && view->binding==owner;','reusedReceiverCannotIssue')];caught=[]
 for filename,name,old,new,witness in mutants:
  assert original[filename].count(old)==1;mutant=OUT/name;shutil.copytree(OUT/'inputs/native',mutant);(mutant/filename).write_text(original[filename].replace(old,new,1))
  run(name+'-compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-I'+str(mutant),str(source),str(mutant/'preview_uri.cpp'),'-o',str(mutant/'checks'),*flags])
  matches=[key for key in traceInputs if witness in key];assert len(matches)==1;stdin,wanted=traceInputs[matches[0]];p=run(name+'-replay',[str(mutant/'checks')],input=stdin);actual=[json.loads(line) for line in p.stdout.splitlines()];assert actual!=wanted,(name,'unsafe mutant escaped actual trace oracle');caught.append({'name':name,'trace':matches[0],'differentObservableState':True})
 report['mutants']=caught;assert all(sha(ROOT/rel)==h for rel,h in inputs.items());report.update(passed=True,namedScenarios=8,invariantSamples=150,statesCompared=sum(x['statesCompared'] for x in traces),unsafeMutantsDetected=3)
except Exception as exc:report['error']=repr(exc)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
