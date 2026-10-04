import copy,hashlib,json,resource,shutil,subprocess,sys,time,traceback
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-picker-ready-gui-v231';OUT=ROOT/'qa'/('refine-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Actual compiled candidate231 controller/native225 frame order, synthetic public confirmed actions and typed counterfactuals; native qualification separate','checks':[],'controls':[]}
try:
 w=json.loads((REPO/'implementation/elm-picker-joint-observation-v226/witness.json').read_text());log=Path(w['nativeLog']);assert sha(log)==w['nativeLogSHA256']
 frames=[json.loads(l.removeprefix('backend-frame: ')) for l in log.read_text().splitlines() if l.startswith('backend-frame: ')]
 base=[{'kind':'native','frame':f} for f in frames[:6]]+[{'kind':'primary'},{'kind':'choose','root':'2'}]+[{'kind':'native','frame':f} for f in frames[6:]]
 def effects(rows):return [w for row in rows for w in row['requests'] if w['kind']=='window-effect']
 def good(rows):return len(effects(rows))==1 and effects(rows)[0]['intent']['operation']=='activate' and effects(rows)[0]['intent']['incarnation']=='2' and not rows[-1]['pendingChoice']
 def inert(rows):return not effects(rows) and not rows[-1]['pendingChoice']
 def mutate_reply(events,kind,request,mutate):
  result=copy.deepcopy(events);found=False
  for e in result:
   if e['kind']=='native' and e['frame']['kind']==kind and e['frame'].get('requestId')==request:mutate(e['frame']);found=True
  assert found;return result
 cases={}
 def add(name,events,oracle):cases[name]=(events,oracle)
 add('capturedGeometryLast',base,good)
 reordered=copy.deepcopy(base)
 for request,next_request in [('4','5'),('6','7')]:
  indexes=[i for i,e in enumerate(reordered) if e['kind']=='native' and e['frame'].get('requestId') in [request,next_request]];assert len(indexes)==2;reordered[indexes[0]],reordered[indexes[1]]=reordered[indexes[1]],reordered[indexes[0]]
 add('projectionLast',reordered,good)
 add('duplicateCompletion',base+[copy.deepcopy(base[-1])],good)
 partial=base[:next(i for i,e in enumerate(base) if e['kind']=='native' and e['frame'].get('requestId')=='5')]
 add('projectionPendingGeometry',partial,lambda rows:not effects(rows) and rows[-1]['pendingChoice'] and not rows[-1]['available'])
 invalids=[('zeroGeometrySequence',lambda f:f.update(sequence='0')),('retrogradeGeometrySequence',lambda f:f.update(sequence='1')),('foreignGeometryBinding',lambda f:f['binding'].update(session='1')),('wrongGeometryRequest',lambda f:f.update(requestId='999')),('overflowGeometryRequest',lambda f:f.update(requestId='18446744073709551616')),('wrongGeometryProtocol',lambda f:f.update(geometryProtocol=3)),('malformedGeometryFacts',lambda f:f.pop('facts'))]
 for name,change in invalids:
  bad=mutate_reply(base,'geometry-facts','7',change);add(name,bad+[copy.deepcopy(base[-1])],lambda rows:not effects(rows[:-1]) and rows[-2]['pendingChoice'] and good(rows))
 for name,change in [('foreignProjectionBinding',lambda f:f['binding'].update(session='1')),('wrongProjectionRequest',lambda f:f.update(requestId='999')),('wrongProjectionProtocol',lambda f:f.update(protocolVersion=4))]:
  bad=mutate_reply(base,'action-projection','6',change);proper=next(e for e in base if e['kind']=='native' and e['frame'].get('requestId')=='6');add(name,bad+[copy.deepcopy(proper)],lambda rows:not effects(rows[:-1]) and rows[-2]['pendingChoice'] and good(rows))
 wrongoutput=mutate_reply(base,'action-projection','6',lambda f:f['context'].update(output='2'));wrongoutput=mutate_reply(wrongoutput,'geometry-facts','7',lambda f:f.update(outputGeneration='2'));add('changedOutputRetiresChoice',wrongoutput,inert)
 add('geometryOutputMismatchRetiresChoice',mutate_reply(base,'geometry-facts','7',lambda f:f.update(outputGeneration='2')),inert)
 retired=mutate_reply(base,'action-projection','6',lambda f:f['scene'].update(windows=[w for w in f['scene']['windows'] if w['incarnation']!='2']));retired=mutate_reply(retired,'geometry-facts','7',lambda f:f['facts'].update(windows=[w for w in f['facts']['windows'] if w['incarnation']!='2']));add('retiredNativeRoot',retired,inert)
 def differentapp(f):
  for w in f['scene']['windows']:
   if w['incarnation']=='2':w['application']='Other Application'
 add('changedNativeApplication',mutate_reply(base,'action-projection','6',differentapp),inert)
 add('originalChoiceTimer',base[:-1]+[{'kind':'deadline'},copy.deepcopy(base[-1])],inert)
 add('disconnectedChoice',base[:8]+[{'kind':'native','frame':{'protocolVersion':3,'kind':'disconnected'}}]+base[8:],inert)
 optional=[{'kind':'native','frame':copy.deepcopy(f)} for f in frames[:4]]
 optional.append({'kind':'native','frame':{'protocolVersion':3,'kind':'geometry-unavailable','binding':copy.deepcopy(frames[0]['binding']),'requestId':'2','reason':'unsupported'}})
 projection=copy.deepcopy(next(f for f in frames if f.get('requestId')=='4'));projection['requestId']='3'
 add('unsupportedGeometryPreservesLegacyChoice',optional+[{'kind':'primary'},{'kind':'choose','root':'2'},{'kind':'native','frame':projection}],good)
 close=copy.deepcopy(base);close[7]={'kind':'close'}
 def returned(rows):return not effects(rows) and len([f for row in rows[7:] for f in row['focus'] if f.startswith('group:')])==1 and not rows[-1]['returnFocus']
 add('geometryLastReturnsFocus',close,returned)
 close_first=copy.deepcopy(reordered);close_first[7]={'kind':'close'};add('projectionLastReturnsFocus',close_first,returned)
 add('geometryOutputMismatchRetiresReturnFocus',mutate_reply(close,'geometry-facts','7',lambda f:f.update(outputGeneration='2')),lambda rows:not effects(rows) and not any(row['focus'] for row in rows[7:]) and not rows[-1]['returnFocus'])
 add('openApplicationsPreventsReturnFocus',close[:-1]+[{'kind':'open'},copy.deepcopy(close[-1])],lambda rows:not effects(rows) and not any(row['focus'] for row in rows[7:]))
 runner=OUT/'probe.cjs';runner.write_text("const app=require(process.argv[2]).Elm.Probe.init({flags:null});app.ports.outgoing.subscribe(x=>{console.log(JSON.stringify(x));process.exit(0)});app.ports.incoming.send(JSON.parse(require('fs').readFileSync(process.argv[3],'utf8')));setTimeout(()=>process.exit(2),3000);")
 def compile(name,change=None):
  inputs=OUT/name/'inputs';shutil.copytree(SOURCE/'src',inputs/'src');shutil.copy2(SOURCE/'elm.json',inputs/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',inputs/'src/Probe.elm')
  if change:
   p=inputs/'src/Desktop.elm';s=p.read_text();before,after=change;assert before in s;s=s.replace(before,after);p.write_text(s)
  worker=inputs.parent/'worker.js';p=subprocess.run(['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Probe.elm','--output='+str(worker)],cwd=inputs,capture_output=True,timeout=180);(inputs.parent/'compile.stdout').write_bytes(p.stdout);(inputs.parent/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr.decode()[-2500:];return worker
 def invoke(worker,name,events):
  path=worker.parent/(name+'.json');path.write_text(json.dumps(events,indent=2)+'\n');p=subprocess.run(['node',str(runner),str(worker),str(path)],capture_output=True,text=True,timeout=10);(worker.parent/(name+'.stdout')).write_text(p.stdout);(worker.parent/(name+'.stderr')).write_text(p.stderr);assert p.returncode==0,p.stderr;rows=json.loads(p.stdout);assert len(rows)==len(events);return rows
 worker=compile('baseline')
 for name,(events,oracle) in cases.items():
  rows=invoke(worker,name,events);ok=oracle(rows);r['checks'].append({'name':name,'passed':ok,'effects':effects(rows),'pendingChoice':rows[-1]['pendingChoice'],'returnFocus':rows[-1]['returnFocus']});assert ok,(name,rows[-1])
 controls=[('projection-only',('matchingObservation = matchingProjection || matchingGeometry','matchingObservation = matchingProjection'),'capturedGeometryLast'),('consume-before-ready',('not matchingObservation || not (Shell.available next.windows.shell)','not matchingObservation'),'projectionPendingGeometry'),('geometry-output-ignored',(' || geometryOutput/=Just pending.output',''),'geometryOutputMismatchRetiresChoice'),('output-scope-ignored',('output/=Just pending.output || geometryOutput/=Just pending.output','False'),'changedOutputRetiresChoice'),('retired-root-ignored',('item.root==pending.root && ',''),'retiredNativeRoot'),('changed-application-ignored',('item.application==pending.application && ',''),'changedNativeApplication'),('choice-retained',('choice=Nothing,choiceNotice="The window changed. Choose again."','choice=next.choice,choiceNotice="The window changed. Choose again."'),'capturedGeometryLast'),('return-output-ignored',(' || geometryOutput/=target.output',''),'geometryOutputMismatchRetiresReturnFocus')]
 for name,change,case in controls:
  worker=compile(name,change);events,oracle=cases[case];rows=invoke(worker,case,events);rejected=not oracle(rows);r['controls'].append({'name':name,'case':case,'compiled':True,'normalExitCode':0,'rejected':rejected});assert rejected,name
 r.update(passed=True,capturedLog=str(log),capturedLogSHA256=sha(log),cases=len(cases),compiledControlsRejected=len(controls),inputs={str(p):sha(p) for p in [Path(__file__),ROOT/'qa/Probe.elm',SOURCE/'elm.json',*sorted((SOURCE/'src').glob('*.elm'))]})
except Exception as e:r['error']=repr(e);r['traceback']=traceback.format_exc()
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
