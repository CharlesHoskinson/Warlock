import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];PARENT=ROOT.parent/'elm-reconciliation-accepted-read-v619'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
primary=max((ROOT/'qa').glob('tests-*/report.json'));mutants=max((ROOT/'qa').glob('mutations-*/report.json'));drain=max((ROOT/'qa').glob('drain-*/report.json'));controls=max((ROOT/'qa').glob('controls-*/report.json'))
a=json.loads(primary.read_text());b=json.loads(mutants.read_text());c=json.loads(drain.read_text());d=json.loads(controls.read_text())
assert a['passed'] and len(a['checks'])==51 and b['passed'] and len(b['controls'])==13 and c['passed'] and c['assertions']==21 and d['passed'] and d['assertions']==20 and len(d['compiledControls'])==6
for r in [a,b,c,d]:
 assert all(v.get('passed',v.get('detected',False)) for v in r.get('checks',r.get('controls',r.get('compiledControls',[]))))
 for command in r.get('commands',[]):assert command.get('exitCode',command.get('exit',0))==0
for name,h in a['sourceSHA256'].items():assert sha(ROOT/'src'/name)==h and sha(primary.parent/'inputs/src'/name)==h
for name,h in c['frontendSourceHashes'].items():assert sha(ROOT/'src'/name)==h
for p,h in c['sourceHashes'].items():assert sha(pathlib.Path(p))==h
changed=[];pins={}
for p in sorted((PARENT/'src').glob('*.elm')):
 q=ROOT/'src'/p.name
 if sha(q)!=sha(p):changed.append(p.name)
 else:pins[p.name]=sha(p)
assert changed==['ReconciliationTracking.elm','SurfaceController.elm']
assert sha(ROOT/'src/ReconciliationFrame.elm')==sha(PARENT/'src/ReconciliationFrame.elm')
rows=[]
for f in sorted(ROOT.rglob('*')):
 if f.is_file() and f not in [ROOT/'component-manifest.json',ROOT/'qa/freeze-receipt.json',ROOT/'qa/protected-freeze.log']:
  assert not f.is_symlink();rows.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f),'size':f.stat().st_size})
m=ROOT/'component-manifest.json';m.write_text(json.dumps({'sourceHeld':True,'passed':True,'parent619ManifestSHA256':sha(PARENT/'component-manifest.json'),'changedProductionFiles':changed,'unchangedProductionPins':pins,'public619Assertions':51,'inheritedCompiledMutants':13,'actual630CoordinatorFilesystem642Assertions':21,'targetedInformationalAssertions':20,'targetedCompiledMutants':6,'nativeAcceptance':False,'completeGUIBuild':False,'reports':[str(p.relative_to(ROOT)) for p in [primary,mutants,drain,controls]],'files':rows},indent=2)+'\n');out={'passed':True,'files':len(rows),'manifestSHA256':sha(m),'nativeAcceptance':False};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
