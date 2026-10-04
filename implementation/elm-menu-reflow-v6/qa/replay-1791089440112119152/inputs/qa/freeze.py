"""Freeze V6 exact CPU/native tuples, retaining every failed attempt.
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
for lane in ('native','regression','output-regression','menu-reflow'):parser.add_argument('--'+lane+'-report',type=Path)
args=parser.parse_args();target=ROOT/'qa/implementation-manifest.json'
assert not target.exists(),'Frozen manifest is immutable'
paths={name:sorted((ROOT/'qa').glob(name+'-*/report.json'))[-1] for name in ('build','replay')}
reports={name:passed(path) for name,path in paths.items()}
for name,path in paths.items():closure(path,reports[name]);assert all(row['exitCode']==0 for row in reports[name]['commands'])
build=reports['build'];replay=reports['replay']
assert build['inputs'].get('qa/freeze.py')==sha(Path(__file__)) and replay['inputs'].get('qa/freeze.py')==sha(Path(__file__))
assert replay['checks']>=78
assert sha(paths['build'].parent/'elm-host')==build['binarySHA256']
compiled={}
for name,count in [('replay',20),('shell',27),('surface',55),('output-surface',70),('presentation',12)]:
 path=paths['build'].parent/(name+'-report.json');data=passed(path);assert data['checks']==count,name
 compiled[name]={'report':link(path),'checks':count}
# Exact immutable V5 proof, V132 build and the failed rotation parent.
upstream=json.loads((ROOT/'upstream.json').read_text());parents={}
item=upstream['baseProof'];path=REPO/item['path'];assert sha(path)==item['sha256']
data=passed(path);original_root=path.parents[1]
for relative,value in data['files'].items():assert sha(original_root/relative)==value['sha256'],relative
parents['baseProof']=item
item=upstream['reflowBuild'];path=REPO/item['path'];assert sha(path)==item['sha256']
data=passed(path)
for relative,digest in data['inputs'].items():
 assert sha(REPO/upstream['reflow']/relative)==digest,relative
 assert sha(path.parent/'inputs'/relative)==digest,relative
parents['reflowBuild']=item
item=upstream['reflowNativeFailure'];path=REPO/item['path'];assert sha(path)==item['sha256']
failed_rotation=json.loads(path.read_text());assert failed_rotation['passed'] is False and failed_rotation['cleanupPassed'] is True
parents['failedRotation']=item
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
assert (ROOT/'qa/output-surface.cjs').read_text()==(REPO/'implementation/elm-output-reflow-checks-v127/qa/surface.cjs').read_text().replace('Elm.SurfaceReplay.init','Elm.OutputSurfaceReplay.init')
assert sha(ROOT/'qa/presentation.cjs')==sha(REPO/'implementation/elm-output-reflow-checks-v127/qa/presentation.cjs')
# Targeted extension is additional evidence, never a replacement rotation campaign.
reflow_oracle_path=ROOT/'qa/menu-reflow-oracle.json';assert build['inputs'].get('qa/menu-reflow-oracle.json')==sha(reflow_oracle_path)
reflow_oracle=json.loads(reflow_oracle_path.read_text())
original=REPO/reflow_oracle['originalSource']['path'];assert sha(original)==reflow_oracle['originalSource']['sha256']
extension=ROOT/'qa/menu-reflow-extension.txt';assert sha(extension)==reflow_oracle['extensionSHA256']
original_text=original.read_text();actual=(ROOT/'qa/menu-reflow.py').read_text()
expected=original_text.replace("            screenshot = OUTPUT/'elm-context-menu-restored.png'",extension.read_text()+"            screenshot = OUTPUT/'elm-context-menu-restored.png'")
expected=expected.replace("'scope': 'Private real pointer and popup Menu/ShiftF10 through dual WebKit surfaces, disabled menu rows and authenticated minimize/restore; no bar keyboard, exhaustive gesture interleavings, multioutput, AT or release acceptance'","'scope': 'Original menu scenario plus targeted menu resize/integer-scale/Escape; parent rotation campaign remains failed/open; no exhaustive cancellation/geometry, bar keyboard, AT or release acceptance'")
assert ast.dump(ast.parse(actual),include_attributes=False)==ast.dump(ast.parse(expected),include_attributes=False)
for name in ('check','wait'):
 cursor=iter(calls(actual,name));assert all(any(row==old for row in cursor) for old in calls(original_text,name)),name
for name in reflow_oracle['originalHelpers']:
 helper=lambda text:next(node for node in ast.walk(ast.parse(text)) if isinstance(node,ast.FunctionDef) and node.name==name)
 assert ast.dump(helper(actual),include_attributes=False)==ast.dump(helper(original_text),include_attributes=False),name
native={}
for lane in ('native','regression','output-regression','menu-reflow'):
 selected=getattr(args,lane.replace('-','_')+'_report')
 if selected is None:continue
 path=selected.resolve();assert path.is_relative_to(ROOT/'qa') and path.name=='report.json' and path.parent.name.startswith('native-'),str(path)
 data=passed(path);script=ROOT/'qa'/(lane+'.py')
 assert data.get('cleanupPassed') is True and data.get('mainDesktopActions') is False
 assert data['inputs'].get(str(script))==sha(script),'Wrong native lane identity'
 assert all(str(ROOT/'qa'/(other+'.py')) not in data['inputs'] for other in ('native','regression','output-regression','menu-reflow') if other!=lane)
 assert all(c['passed'] for c in data['checks'])
 names=Counter(c['name'] for c in data['checks'])
 if lane=='menu-reflow':
  assert all(names[name]>=count for name,count in oracles['native']['originalCheckNames'].items()), 'Original menu observation missing'
  assert all(names[name]==1 for name in reflow_oracle['addedChecks']), 'Incomplete targeted reflow scenario'
 else:assert names==Counter(oracles[lane]['originalCheckNames']),lane
 if lane in ('regression','output-regression'):assert data['originalScenario']['sha256']==oracles[lane]['originalSource']['sha256']
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
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'V6 menu reflow integration: exact selected tuples; original rotation campaign remains failed/open; no whole feature or release acceptance',
 'rotationParentPassed':False,'nativeWrapperSafetyQualified':False,'targetedMenuReflowOracle':link(reflow_oracle_path),
 'wholeFeatureAccepted':False,'newNativeGuiAccepted':False,'roadmapCompleted':False,'completedRequirementIds':[],
 'buildReport':link(paths['build']),'replayReport':link(paths['replay']),'menuChecks':replay['checks'],'compiledChecks':compiled,
 'nativeScenarioReports':native,'parentProofs':parents,'originalRegressionCheckWaitASTPreserved':True,'normalizedNativeScenarioSourcesPreserved':True,
 'scenarioOracles':{lane:link(ROOT/'qa'/filename) for lane,filename in [('native','menu-native-oracle.json'),('regression','scenario-oracle.json'),('output-regression','output-scenario-oracle.json')]},
 'remainingGates':['parent full rotation/removal campaign remains open','complete native asynchronous proof cancellation','single global controller and global output registry','complete gesture interleavings','bar keyboard and AT/IME/opener usability','application/Files/background providers','all-origin uncertainty and lost-broker recovery','mixed scale/transforms and hardware/GPU budgets','complete native roadmap and release journeys'],
 'files':files,'symlinks':symlinks}
with target.open('x') as stream:stream.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(target),'nativeLanes':list(native)}))
