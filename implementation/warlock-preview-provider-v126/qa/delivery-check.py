"""Selected Quint receipt-growth traces against actual physical GIO and journal."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('delivery-check-'+str(time.time_ns()));OUT.mkdir()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'native').glob('*') if p.is_file()}
for rel in ['spec/delivery.qnt','spec/delivery_tests.qnt','qa/delivery-check.py','qa/delivery-checks.cpp']:inputs[rel]=sha(ROOT/rel)
for rel in inputs:
 target=OUT/'inputs'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
report={'passed':False,'scope':scope,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'projection':'Two fixed own actors/jobs/deadlines, one receiver retaining epoch across explicit subject extension; actual GIO reader count, actual Broker charge/record count, old/new exact terminal delivery. Binding/incarnation mixed refusal is separately tested by full compiled physical test; not a whole product/hardware refinement.','fixedFixture':{'binding':[1,2,3],'incarnations':[11,12],'clock':10,'now':1,'jobs':[1,1],'origin':1,'originalDeadline':100,'expires':120,'items':2,'bytes':64},'toolSHA256':sha(TOOL.resolve())}
def run(name,argv,cwd=None,input=None):
 p=subprocess.run(argv,cwd=cwd or OUT,capture_output=True,text=True,timeout=180,input=input)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout
 return p
def decode(v):
 if isinstance(v,list):return [decode(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
 return v
def expected(state):
 old,new=state['old'],state['new'];receiver=state['receiver']
 return {'receiver':receiver,'readers':int(old<2)+int(new<2),'charge':32*(int(old<4)+int(new<4)),'records':int(old<5)+int(new<5),'oldReceipts':2 if receiver and old==4 else 0,'newReceipts':2 if receiver and state['admitted'] and new==4 else 0}
try:
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','json-glib-1.0','gio-unix-2.0']).stdout)
 binary=OUT/'checks';folder=OUT/'inputs/spec'
 command=['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(OUT/'inputs/native'),str(OUT/'inputs/qa/delivery-checks.cpp'),str(OUT/'inputs/native/preview_uri.cpp'),'-o',str(binary),*flags]
 run('compile',command);run('quint-typecheck',[str(TOOL),'typecheck','delivery_tests.qnt'],cwd=folder)
 names=re.findall(r'run (\w+)\s*=',(folder/'delivery_tests.qnt').read_text());assert len(names)==len(set(names))==6;report['selectedNames']=names
 run('quint-named',[str(TOOL),'test','delivery_tests.qnt','--main=delivery_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=571001','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(OUT.glob('named-*.itf.json')))==6
 run('quint-sampling',[str(TOOL),'run','delivery.qnt','--main=delivery','--backend=typescript','--invariant=safety','--seed=571002','--max-samples=150','--max-steps=35','--n-traces=10','--out-itf='+str(OUT/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];traceInputs={}
 for trace in sorted(OUT.glob('*.itf.json')):
  states=[row['s'] for row in decode(json.loads(trace.read_text()))['states']];events=states[-1]['history'];wanted=[];length=0
  for state in states:
   if len(state['history'])==length:continue
   length=len(state['history']);wanted.append(expected(state))
  stdin='\n'.join(events)+'\n';p=run('replay-'+trace.stem,[str(binary)],input=stdin);assert not p.stderr;actual=[json.loads(line) for line in p.stdout.splitlines()];assert actual==wanted,(trace.name,actual,wanted)
  traces.append({'trace':trace.name,'statesCompared':len(actual)});traceInputs[trace.name]=(stdin,wanted)
 assert len(traces)==16;report['coupledTraces']=traces
 original=(OUT/'inputs/native/preview_delivery.hpp').read_text();mutants=[('missing-admission','view(popup,registered);admit(broker,*registered);return true;','(void)broker;view(popup,registered);return true;'),('reused-epoch','registered->epoch==epoch_','true')]
 caught=[]
 for name,old,new in mutants:
  assert original.count(old)==1;mutant=OUT/name;shutil.copytree(OUT/'inputs/native',mutant);(mutant/'preview_delivery.hpp').write_text(original.replace(old,new,1))
  argv=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-I'+str(mutant),str(OUT/'inputs/qa/delivery-checks.cpp'),str(mutant/'preview_uri.cpp'),'-o',str(mutant/'checks'),*flags];run(name+'-compile',argv)
  witness='named-'+('explicitJournalGrowth' if name=='missing-admission' else 'replacedReceiverRetainsJournal')+'-0.itf.json'
  matches=[key for key in traceInputs if ('explicitJournalGrowth' if name=='missing-admission' else 'replacedReceiverRetainsJournal') in key];assert len(matches)==1
  stdin,wanted=traceInputs[matches[0]];p=run(name+'-replay',[str(mutant/'checks')],input=stdin);actual=[json.loads(line) for line in p.stdout.splitlines()];assert actual!=wanted,(name,'unsafe mutant escaped actual trace oracle');caught.append({'name':name,'trace':matches[0],'differentObservableState':True})
 report['mutants']=caught;assert all(sha(ROOT/rel)==h for rel,h in inputs.items());report.update(passed=True,namedScenarios=6,invariantSamples=150,statesCompared=sum(x['statesCompared'] for x in traces),unsafeMutantsDetected=2)
except Exception as exc:report['error']=repr(exc)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
