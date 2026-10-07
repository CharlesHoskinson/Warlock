"""Explicit control-prefix Quint traces coupled to actual native C header."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('control-prefix-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
names=['native/preview-control.h','qa/control-prefix-replay.c','qa/control-prefix-check.py','spec/control_prefix.qnt','spec/control_prefix_tests.qnt']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual C control-prefix begin/complete/exhaustion functions against explicit selected and sampled Quint traces. GUI router own-popup/thread/strict JSON tested separately in actual full host; this prefix is delivery continuity, never native effect success, physical cleanup or full retirement acceptance.'}
def run(name,args,stdin=None,cwd=None):
 p=subprocess.run(args,input=stdin,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
def decode(value):
 if isinstance(value,list):return [decode(v) for v in value]
 if isinstance(value,dict):return int(value['#bigint']) if '#bigint' in value else {k:decode(v) for k,v in value.items()}
 return value
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','glib-2.0']))
 compileArgs=['cc','-std=c11','-O1','-Wall','-Wextra','-Werror','-Inative','qa/control-prefix-replay.c','-o',str(out/'checks'),*flags]
 run('compile',compileArgs)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'control_prefix_tests.qnt').read_text());assert len(selected)==7
 run('typecheck',[str(tool),'typecheck','control_prefix_tests.qnt'],cwd=folder)
 run('selected',[str(tool),'test','control_prefix_tests.qnt','--main=control_prefix_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=880031','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==7
 run('samples',[str(tool),'run','control_prefix.qnt','--main=control_prefix','--backend=typescript','--invariant=safety','--seed=880032','--max-samples=100','--max-steps=20','--n-traces=8','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];witnesses={}
 for path in sorted(out.glob('*.itf.json')):
  states=[v['s'] for v in decode(json.loads(path.read_text()))['states']];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({k:str(v) if k in {'delivered','offered'} else v for k,v in state.items() if k!='history'})
  stdin='\n'.join(states[-1]['history'])+'\n'
  actual=[json.loads(v) for v in run('replay-'+path.stem,[str(out/'checks')],stdin).splitlines()]
  assert actual==wanted,(path.name,actual,wanted)
  traces.append({'trace':path.name,'statesCompared':len(actual)});witnesses[path.name]=(stdin,wanted)
 mutants=[]
 for name,old,new,witness in [
  ('missing-flight-guard','!state->inFlight && ','','reentrantSamePacketCannotReenter'),
  ('skip-missing-control','ordinal==state->delivered+1','ordinal>state->delivered','gapCannotDeliverReady'),
  ('reset-exhausted-prefix','state->delivered=ordinal;','state->delivered=ordinal==G_MAXUINT64?0:ordinal;','finalOrdinalThenNoWrap')]:
  changed=out/name;shutil.copytree(out/'inputs',changed)
  header=changed/'native/preview-control.h';s=header.read_text();assert s.count(old)==1;header.write_text(s.replace(old,new))
  run(name+'-compile',['cc','-std=c11','-O1','-Wall','-Wextra','-Werror','-I'+str(changed/'native'),str(changed/'qa/control-prefix-replay.c'),'-o',str(changed/'checks'),*flags])
  path=next(v for v in witnesses if witness in v);stdin,wanted=witnesses[path]
  actual=[json.loads(v) for v in run(name+'-replay',[str(changed/'checks')],stdin).splitlines()]
  assert actual!=wanted;mutants.append({'name':name,'witness':path,'differentObservableState':True})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,selectedNames=selected,namedScenarios=7,invariantSamples=100,coupledTraces=traces,statesCompared=sum(v['statesCompared'] for v in traces),unsafeMutantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:700]}),flush=True);sys.exit(not report['passed'])
