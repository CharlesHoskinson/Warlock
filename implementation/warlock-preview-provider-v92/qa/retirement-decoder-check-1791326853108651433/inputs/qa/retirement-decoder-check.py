"""Selected retirement decoder traces against current compiled native JSON boundary."""
import hashlib, json, pathlib, re, resource, shlex, shutil, subprocess, sys, time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'qa'/('retirement-decoder-check-'+str(time.time_ns()));out.mkdir()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
inputs={str(path.relative_to(root)):sha(path) for folder in ['native','spec','qa','src'] for path in (root/folder).glob('*') if path.is_file() and path.name!='current-build.json'}
report={'passed':False,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,
 'scope':'Actual strict native retirement JSON decoder/query code coupled to synthetic binding/request/subject/clock/sequence/frontier traces. Native socket/whole ImportedClients refinement, physical retirement, actor turnover and full release are separate.'}
def run(name,args,stdin=None,cwd=None):
 result=subprocess.run(args,input=stdin,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':result.returncode});print(name,result.returncode,flush=True)
 assert result.returncode==0,result.stderr or result.stdout
 return result.stdout
def decode(value):
 if isinstance(value,list):return [decode(row) for row in value]
 if isinstance(value,dict):return int(value['#bigint']) if '#bigint' in value else {key:decode(row) for key,row in value.items()}
 return value
try:
 build=next(root.glob('qa/build-*/report.json'));proof=json.loads(build.read_text());assert proof['passed'] and len(proof['commands'])==95
 for name,value in proof['inputs'].items():assert sha(root/name)==value,name
 report['fullBuild']={'path':str(build),'sha256':sha(build)}
 for name in inputs:
  target=out/'inputs'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
 flags=shlex.split(run('gio-flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
 run('compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','qa/retirement-decoder-checks.cpp','-o',str(out/'checks'),*flags])
 folder=out/'inputs/spec';names=re.findall(r'run (\w+)\s*=',(folder/'retirement_decoder_tests.qnt').read_text());assert len(names)==13
 run('typecheck',[str(tool),'typecheck','retirement_decoder_tests.qnt'],cwd=folder)
 run('selected',[str(tool),'test','retirement_decoder_tests.qnt','--main=retirement_decoder_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=820001','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==13
 run('samples',[str(tool),'run','retirement_decoder.qnt','--main=retirement_decoder','--backend=typescript','--invariant=safety','--seed=820002','--max-samples=150','--max-steps=35','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];witnesses={}
 for path in sorted(out.glob('*.itf.json')):
  states=[row['s'] for row in decode(json.loads(path.read_text()))['states']];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({key:value for key,value in state.items() if key!='history'})
  stdin='\n'.join(states[-1]['history'])+'\n'
  actual=[json.loads(line) for line in run('replay-'+path.stem,[str(out/'checks')],stdin).splitlines()]
  assert actual==wanted,(path.name,actual,wanted)
  traces.append({'trace':path.name,'statesCompared':len(actual)});witnesses[path.name]=(stdin,wanted)
 mutants=[]
 for name,old,new,witness in [('foreign-owner','binding==owner && reply.counter','true && reply.counter','foreignBindingRefused'),('foreign-clock','clock.value==owner.lifetime.value','true','foreignClockRefused'),('replayed-sequence','sequence>cursor.sequence &&','true &&','replayCannotAdvanceCursor')]:
  changed=out/name;shutil.copytree(out/'inputs',changed);header=changed/'native/preview_retirement.hpp';text=header.read_text();assert text.count(old)==1;header.write_text(text.replace(old,new))
  run(name+'-compile',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-I'+str(changed/'native'),str(changed/'qa/retirement-decoder-checks.cpp'),'-o',str(changed/'checks'),*flags])
  trace=next(key for key in witnesses if witness in key);stdin,wanted=witnesses[trace]
  actual=[json.loads(line) for line in run(name+'-replay',[str(changed/'checks')],stdin).splitlines()];assert actual!=wanted
  mutants.append({'name':name,'trace':trace,'differentObservableState':True})
 assert len(traces)==25 and len(mutants)==3
 assert all(sha(root/name)==value for name,value in inputs.items())
 report.update(passed=True,selectedNames=names,namedScenarios=13,invariantSamples=150,coupledTraces=traces,statesCompared=sum(row['statesCompared'] for row in traces),mutants=mutants,unsafeMutantsDetected=3)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(path.relative_to(out)):sha(path) for path in out.rglob('*') if path.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
