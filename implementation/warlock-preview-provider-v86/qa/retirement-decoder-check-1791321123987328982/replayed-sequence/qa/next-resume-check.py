"""Selected resume succession traces coupled to actual helper/Broker and C/Elm."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('next-resume-check-'+str(time.time_ns()));OUT.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
inputs={str(p.relative_to(ROOT)):sha(p) for folder in ['native','spec','qa','src'] for p in (ROOT/folder).glob('*') if p.is_file() and p.name!='current-build.json'}
report={'passed':False,'scope':scope,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'toolSHA256':sha(TOOL.resolve()),'projection':'Actual reserveImportedResumeAttempt helper, original receiver mutex epoch, bounded predecessor/current intent and physical Broker reservation/proof/floor. Fixed synthetic native identity/clock/observations, no whole ImportedClients refinement or native compositor/capture acceptance. Actual socket/C/bootstrap/delivery and optimized Elm checks are separate.'}
def run(name,argv,input=None,cwd=None):
 p=subprocess.run(argv,cwd=cwd or OUT/'inputs',capture_output=True,text=True,timeout=180,input=input)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
def decode(v):
 if isinstance(v,list):return [decode(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
 return v
try:
 bp=next(ROOT.glob('qa/build-*/report.json'));b=json.loads(bp.read_text());assert b['passed']
 for name,value in b['inputs'].items():assert sha(ROOT/name)==value,name
 report['fullBuild']={'path':str(bp),'sha256':sha(bp)}
 for name in inputs:
  target=OUT/'inputs'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 flags=shlex.split(run('gio-flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']));binary=OUT/'checks';source=OUT/'inputs/qa/next-resume-checks.cpp'
 run('compile-model',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative',str(source),'native/preview_uri.cpp','-o',str(binary),*flags])
 cbinary=OUT/'next-resume-tests';run('compile-c',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/next-resume-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(cbinary),*flags])
 guards=[]
 for mode in ['guard-retirement','guard-receiver']:
  d=json.loads(run('c-'+mode,[str(cbinary),mode]));assert d['passed'];guards.append(d)
 report['nativeGuardControls']=guards
 elm=bp.parent/'inputs/assets/feedback-replay.js';assert sha(elm)==b['artifacts']['inputs/assets/feedback-replay.js']
 wire=json.loads(run('actual-c-elm',['node','qa/next-resume-wire.js',str(cbinary),str(elm)]));assert wire['passed'];report['wireControls']=wire
 folder=OUT/'inputs/spec';names=re.findall(r'run (\w+)\s*=',(folder/'next_resume_tests.qnt').read_text());assert len(names)==len(set(names))==13
 run('typecheck',[str(TOOL),'typecheck','next_resume_tests.qnt'],cwd=folder)
 run('selected',[str(TOOL),'test','next_resume_tests.qnt','--main=next_resume_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=810001','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(OUT.glob('named-*.itf.json')))==13
 run('samples',[str(TOOL),'run','next_resume.qnt','--main=next_resume','--backend=typescript','--invariant=safety','--seed=810002','--max-samples=150','--max-steps=35','--n-traces=16','--out-itf='+str(OUT/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];traceInputs={}
 for path in sorted(OUT.glob('*.itf.json')):
  states=[row['s'] for row in decode(json.loads(path.read_text()))['states']];events=states[-1]['history'];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({k:v for k,v in state.items() if k!='history'})
  stdin='\n'.join(events)+'\n';actual=[json.loads(line) for line in run('replay-'+path.stem,[str(binary)],input=stdin).splitlines()]
  assert actual==wanted,(path.name,actual,wanted);traces.append({'trace':path.name,'statesCompared':len(actual)});traceInputs[path.name]=(stdin,wanted)
 assert len(traces)==29
 mutants=[('native/imported_lifecycle.hpp','pending-replaced','intent->deadline>s.now ||','false ||','pendingCannotSucceed'),('native/imported_lifecycle.hpp','lease-replayed','lease<=intent->lease)','false)','partialPublicationRefused'),('native/imported_enrollment.hpp','receiver-replayed','return view && epoch && view->epoch==epoch && view->binding==owner;','return view && epoch && view->binding==owner;','receiverReplacementPreventsQuery')];caught=[]
 for filename,name,old,new,witness in mutants:
  original=(OUT/'inputs'/filename).read_text();assert original.count(old)==1;folder=OUT/name;shutil.copytree(OUT/'inputs',folder);(folder/filename).write_text(original.replace(old,new,1))
  run(name+'-compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-I'+str(folder/'native'),str(folder/'qa/next-resume-checks.cpp'),str(folder/'native/preview_uri.cpp'),'-o',str(folder/'checks'),*flags])
  matches=[key for key in traceInputs if witness in key];assert len(matches)==1;stdin,wanted=traceInputs[matches[0]]
  p=subprocess.run([str(folder/'checks')],capture_output=True,text=True,input=stdin,timeout=30);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
  actual=[json.loads(line) for line in p.stdout.splitlines()];assert p.returncode!=0 or actual!=wanted,'Unsafe native mutation escaped';caught.append({'name':name,'trace':matches[0],'differentObservableState':True,'exitCode':p.returncode})
 report.update(passed=True,selectedNames=names,namedScenarios=13,invariantSamples=150,coupledTraces=traces,statesCompared=sum(row['statesCompared'] for row in traces),mutants=caught,unsafeMutantsDetected=3)
 assert all(sha(ROOT/name)==value for name,value in inputs.items()),'Source changed during checks'
except Exception as error:report['passed']=False;report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
