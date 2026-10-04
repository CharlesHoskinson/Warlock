"""Hold additive profile expectations and exact CPU source/closure."""
import ast,hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=ROOT/'qa/check-1791130624586223434/report.json';r=json.loads(report.read_text());assert r['passed'] and r['projection']=={'checks':73,'failures':0} and r['profileCount']==22 and r['retainedBaselineCount']==8
for rel,d in r['artifacts'].items():assert sha(report.parent/rel)==d,rel
external={}
for section in ['dependencies','linkedLibraries','tools','externalPins']:
 for p,d in r[section].items():
  path=Path(p);assert sha(path)==d,p
  if not path.is_relative_to(ROOT):external[p]={'sha256':d,'size':path.stat().st_size,'resolved':str(path.resolve())}
profiles=json.loads((ROOT/'profiles.json').read_text())['profiles'];assert len(profiles)==22
assert len(r['cli'])==22 and {p['id'] for p in profiles}=={p['id'] for p in r['cli']}
source=REPO/'implementation/elm-geometry-xdg-origin-native-v196/qa/native.py';tree=ast.parse(source.read_text())
node=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROFILES' for t in n.targets));assert isinstance(node,ast.ListComp)
scales=ast.literal_eval(node.generators[0].iter);cases=ast.literal_eval(node.generators[1].iter)
expected=[(f'{kind}-scale{scale}',[x,y,px,py,scale],list(maximum)) for scale in scales for kind,x,y,px,py,maximum in cases]
actual=[(p['id'],[*p['origin'],*p['pads'],p['bufferScale']],p['maximum']) for p in profiles if p['retainedBaseline']];assert expected==actual and len(actual)==8
client=REPO/'implementation/elm-geometry-xdg-hint-choice-fixture-v197';m=json.loads((client/'component-manifest.json').read_text())
for rel,row in m['files'].items():assert sha(client/rel)==row['sha256'],rel
sourceHeader=report.parent/'inputs/ProspectiveGeometry.hpp';production=REPO/'implementation/elm-geometry-coordinate-authority-v409/qa/build-1791125683067025764/inputs/candidate/ProspectiveGeometry.hpp';assert sourceHeader.read_bytes()==production.read_bytes()
assert (report.parent/'inputs/projection.cpp').read_bytes()==(ROOT/'qa/projection.cpp').read_bytes()
target=ROOT/'component-manifest.json';assert not target.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':p.stat().st_mode&0o7777} for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=target}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Feasible/infeasible profile specification, actual client CLI and exact owning helper CPU; no native/menu/GTK/model/policy acceptance','nativeAcceptance':False,'modelAcceptance':False,'policyAcceptance':False,'files':files,'externalClosure':external,'selectedReport':str(report),'selectedReportSHA256':sha(report),'projectionChecks':73,'clientProfiles':22,'retainedBaselineProfiles':8,'baselineOrderVerified':True,'originalSource196SHA256':sha(source),'projectionHeaderSHA256':sha(production)}
target.write_text(json.dumps(packet,indent=2)+'\n')
for rel,row in files.items():assert sha(ROOT/rel)==row['sha256'],rel
print(json.dumps({'passed':True,'files':len(files),'external':len(external),'manifest':str(target),'manifestSHA256':sha(target)}))
