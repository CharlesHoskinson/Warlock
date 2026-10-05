"""Explicit finite layout scenarios coupled to real native pixel samples."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('check-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
TOOL='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
pointer=REPO/'implementation/warlock-client-child-native-v6/qa/native-result.json'
paths=[pathlib.Path(__file__),ROOT/'SPEC.md',ROOT/'spec/layout.qnt',pointer]
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'qaScope':scope,'commands':[], 'scope':'One fixed child pending/applied position and parent stacking; actual native sample coupling, not general layout/fence/presentation/fullrelease.'}
try:
 receipt=json.loads(pointer.read_text());native=pathlib.Path(receipt['path']);assert sha(native)==receipt['sha256']
 failed=REPO/'implementation/warlock-client-child-native-v5/qa/native-1791237339537618288/report.json'
 paths.extend([native,failed]);inputs={str(p):sha(p) for p in paths};r['inputs']=inputs
 report=json.loads(native.read_text());assert report['passed'] and report['cleanupPassed']
 assert all(c['passed'] for c in report['checks']) and all(e['exitCode']==0 for e in report['ownedExitCodes'])
 samples={row['name']:row for row in report['samples']}
 negative=json.loads(failed.read_text());assert not negative['passed'] and negative['cleanupPassed']
 negativeSamples={row['name']:row for row in negative['samples']}
 negativeBase=negativeSamples['layout-baseline'];negativePending=negativeSamples['layout-position-pending']
 assert negativeBase['pixels']['points']['old']==[0,0,255,255]
 assert negativePending['pixels']['points']['old']!=negativeBase['pixels']['points']['old']
 assert negativePending['scope']['context']!=negativeBase['scope']['context']
 r['actualPrematureLayoutNegativeDetected']={'report':str(failed),'sha256':sha(failed),'pixelsAndContextViolation':True}
 shutil.copy2(ROOT/'spec/layout.qnt',OUT/'layout.qnt')
 names=['positionParentTest','stackingParentTest'];r['selectedNames']=names
 for name,args in [('typecheck',[TOOL,'typecheck',str(OUT/'layout.qnt')]),('selected',[TOOL,'test',str(OUT/'layout.qnt'),'--main=layout','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=730021','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr
 traces=sorted(OUT.glob('named-*.itf.json'));assert len(traces)==2;compared=[]
 for path in traces:
  states=json.loads(path.read_text())['states'];prior=None;rows=[]
  for state in states:
   sample=samples[state['sample']];pixels=sample['pixels'];x=int(state['x']['#bigint']);above=state['above']
   assert pixels['blue']==(64*48 if above else 0) and pixels['red']==320*240-pixels['blue'] and pixels['green']==pixels['yellow']==pixels['cyan']==0,(path,state,sample)
   assert pixels['points']['old']==([0,0,255,255] if above and x==20 else [255,0,0,255])
   assert pixels['points']['moved']==([0,0,255,255] if above and x==100 else [255,0,0,255])
   if prior:
    same=prior[0]['x']==state['x'] and prior[0]['above']==state['above']
    oldContext=prior[1]['scope']['context'];newContext=sample['scope']['context']
    assert newContext==oldContext if same else int(newContext['content'])>int(oldContext['content'])
   rows.append({'state':state,'nativeSample':state['sample'],'context':sample['scope']['context'],'pixels':pixels});prior=(state,sample)
  compared.append({'path':str(path),'sha256':sha(path),'statesCompared':len(rows),'rows':rows})
 assert all(sha(p)==h for p,h in inputs.items());r.update(passed=True,traces=compared,nativeStatesCompared=sum(t['statesCompared'] for t in compared))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};reportPath=OUT/'report.json';reportPath.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(reportPath),'error':r.get('error')}),flush=True)
raise SystemExit(not r['passed'])
