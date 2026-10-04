"""Freeze V5 exact CPU/native tuples, retaining every failed attempt.
Native lanes are explicitly selected; no feature/roadmap acceptance is promoted.
"""
import argparse,ast,hashlib,json,resource
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def link(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def passed(path):
 assert path.is_file() and not path.is_symlink(),str(path)
 data=json.loads(path.read_text());assert data.get('passed') is True and not data.get('error'),str(path)
 return data
def closure(path,data,current=True):
 assert data.get('inputs'),str(path)
 for relative,digest in data['inputs'].items():
  if current:assert sha(ROOT/relative)==digest,relative
  assert sha(path.parent/'inputs'/relative)==digest,relative
 for relative,digest in data.get('artifacts',{}).items():assert sha(path.parent/relative)==digest,relative
def calls(text,name):
 return [ast.dump(n,include_attributes=False) for n in sorted(ast.walk(ast.parse(text)),key=lambda n:(getattr(n,'lineno',0),getattr(n,'col_offset',0))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
def audit_wrapper(oracle,script,gui,metadata):
 source=REPO/oracle['originalSource']['path'];text=source.read_text();expected=text
 for old,new in [("GUI=REPO/'"+gui+"'","GUI=ROOT"),("FIXTURE=ROOT/'fixture.py'","FIXTURE=ROOT/'qa/fixture.py'"),("str(GUI/'adapter/daemon.py')","str(build_path.parent/'inputs/adapter/daemon.py')"),('report.update(buildReport=',metadata+'\n report.update(buildReport=')]:
  assert expected.count(old)==(4 if script=='output-regression.py' and old=="str(GUI/'adapter/daemon.py')" else 2 if old=="str(GUI/'adapter/daemon.py')" else 1),old
  expected=expected.replace(old,new)
 actual=(ROOT/'qa'/script).read_text()
 assert ast.dump(ast.parse(actual),include_attributes=False)==ast.dump(ast.parse(expected),include_attributes=False),script
 for name in ('check','wait'):assert calls(text,name)==calls(actual,name),name
parser=argparse.ArgumentParser()
for lane in ('native','regression','output-regression'):parser.add_argument('--'+lane+'-report',type=Path)
args=parser.parse_args();target=ROOT/'qa/implementation-manifest.json'
assert not target.exists(),'Frozen manifest is immutable'
paths={name:sorted((ROOT/'qa').glob(name+'-*/report.json'))[-1] for name in ('build','replay')}
reports={name:passed(path) for name,path in paths.items()}
for name,path in paths.items():closure(path,reports[name]);assert all(row['exitCode']==0 for row in reports[name]['commands'])
build=reports['build'];replay=reports['replay']
assert build['inputs'].get('qa/freeze.py')==sha(Path(__file__)) and replay['inputs'].get('qa/freeze.py')==sha(Path(__file__))
assert replay['checks']>=64
assert sha(paths['build'].parent/'elm-host')==build['binarySHA256']
compiled={}
for name,count in [('replay',20),('shell',27),('surface',55),('output-surface',67),('presentation',12)]:
 path=paths['build'].parent/(name+'-report.json');data=passed(path);assert data['checks']==count,name
 compiled[name]={'report':link(path),'checks':count}
# Exact immutable parent proofs and all original inventory members.
upstream=json.loads((ROOT/'upstream.json').read_text());parents={}
for key in ('baseProof','menuProof'):
 item=upstream[key];path=REPO/item['path'];assert sha(path)==item['sha256'],key
 data=passed(path);base=path.parents[1]
 for relative,value in data['files'].items():
  original=REPO/relative if key=='baseProof' else base/relative
  assert sha(original)==(value['sha256'] if isinstance(value,dict) else value),relative
 parents[key]=item
for relative,digest in upstream['productionInputs'].items():assert sha(REPO/relative)==digest,relative
# Independently accepted native oracles, source identities and exact check names.
oracles={}
for lane,filename in [('native','menu-native-oracle.json'),('regression','scenario-oracle.json'),('output-regression','output-scenario-oracle.json')]:
 path=ROOT/'qa'/filename;assert build['inputs'].get('qa/'+filename)==sha(path),filename
 oracle=json.loads(path.read_text());oracles[lane]=oracle
 for key in ('originalSource','originalReport','originalFixture'):
  if key in oracle:assert sha(REPO/oracle[key]['path'])==oracle[key]['sha256'],key
 original=passed(REPO/oracle['originalReport']['path'])
 assert original['cleanupPassed'] and all(c['passed'] for c in original['checks'])
 assert Counter(c['name'] for c in original['checks'])==Counter(oracle['originalCheckNames'])
 if 'originalFixture' in oracle:
  assert sha(ROOT/'fixture.py')==oracle['originalFixture']['sha256'] and sha(ROOT/'qa/fixture.py')==oracle['originalFixture']['sha256']
assert sha(ROOT/'qa/native.py')==oracles['native']['originalSource']['sha256'],'V4 native scenario changed'
audit_wrapper(oracles['regression'],'regression.py','implementation/elm-popup-choice-barrier-v87',"report['originalScenario']={'path':'implementation/elm-surface-regression-qa-v93/qa/regression.py','sha256':host.digest(REPO/'implementation/elm-surface-regression-qa-v93/qa/regression.py'),'changes':'candidate path and frozen backend/fixture location only; scenarios and deadlines retained'}")
audit_wrapper(oracles['output-regression'],'output-regression.py','implementation/elm-output-padding-v118',"report['originalScenario']={'path':'implementation/elm-output-padding-qa-v119/qa/regression.py','sha256':host.digest(REPO/'implementation/elm-output-padding-qa-v119/qa/regression.py'),'changes':'candidate and frozen backend/fixture paths only; original scenarios and deadlines retained'}")
# Original component oracles differ only in the worker module name.
assert (ROOT/'qa/output-surface.cjs').read_text()==(REPO/'implementation/elm-output-focus-checks-v107/qa/surface.cjs').read_text().replace('Elm.SurfaceReplay.init','Elm.OutputSurfaceReplay.init')
assert sha(ROOT/'qa/presentation.cjs')==sha(REPO/'implementation/elm-output-focus-checks-v107/qa/presentation.cjs')
native={}
for lane in ('native','regression','output-regression'):
 selected=getattr(args,lane.replace('-','_')+'_report')
 if selected is None:continue
 path=selected.resolve();assert path.is_relative_to(ROOT/'qa') and path.name=='report.json' and path.parent.name.startswith('native-'),str(path)
 data=passed(path);script=ROOT/'qa'/(lane+'.py')
 assert data.get('cleanupPassed') is True and data.get('mainDesktopActions') is False
 assert data['inputs'].get(str(script))==sha(script),'Wrong native lane identity'
 assert all(str(ROOT/'qa'/(other+'.py')) not in data['inputs'] for other in ('native','regression','output-regression') if other!=lane)
 assert all(c['passed'] for c in data['checks']) and Counter(c['name'] for c in data['checks'])==Counter(oracles[lane]['originalCheckNames']),lane
 if lane!='native':assert data['originalScenario']['sha256']==oracles[lane]['originalSource']['sha256']
 for source,digest in data['inputs'].items():assert sha(Path(source))==digest,source
 linked=Path(data['buildReport']);assert linked.is_relative_to(ROOT/'qa') and sha(linked)==data['buildReportSHA256']
 # Historical native builds retain their exact captured QA. The current native
 # runner inputs are checked above, and production equivalence is checked below.
 native_build=passed(linked);closure(linked,native_build,current=False)
 for relative,digest in native_build['inputs'].items():
  if relative.startswith(('src/','native/','adapter/','assets/')) or relative in ('elm.json','fixture.py'):assert build['inputs'].get(relative)==digest,relative
 for relative,digest in data.get('artifacts',{}).items():assert sha(path.parent/relative)==digest,relative
 native[lane]={'report':link(path),'buildReport':link(linked),'checks':len(data['checks']),'scope':data['scope']}
files={};symlinks={}
for path in sorted(ROOT.rglob('*')):
 relative=str(path.relative_to(ROOT))
 if path.is_symlink():symlinks[relative]=str(path.readlink())
 elif path.is_file():files[relative]={'sha256':sha(path),'size':path.stat().st_size}
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'V5 output/menu integration: exact selected component/native tuples; no whole feature or release acceptance',
 'wholeFeatureAccepted':False,'newNativeGuiAccepted':False,'roadmapCompleted':False,'completedRequirementIds':[],
 'buildReport':link(paths['build']),'replayReport':link(paths['replay']),'menuChecks':replay['checks'],'compiledChecks':compiled,
 'nativeScenarioReports':native,'parentProofs':parents,'originalRegressionCheckWaitASTPreserved':True,'normalizedNativeScenarioSourcesPreserved':True,
 'scenarioOracles':{lane:link(ROOT/'qa'/filename) for lane,filename in [('native','menu-native-oracle.json'),('regression','scenario-oracle.json'),('output-regression','output-scenario-oracle.json')]},
 'remainingGates':['single global controller and global output registry','complete gesture interleavings','bar keyboard and AT/IME/opener usability','application/Files/background providers','all-origin uncertainty and lost-broker recovery','mixed scale/transforms and hardware/GPU budgets','complete native roadmap and release journeys'],
 'files':files,'symlinks':symlinks}
with target.open('x') as stream:stream.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(target),'nativeLanes':list(native)}))
