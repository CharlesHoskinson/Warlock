"""Freeze exact tested V4 tuples; no mandatory requirement acceptance.
Run only with the protected launcher. Optional native reports must be explicitly
selected, passed, normally cleaned up, and use the current production closure.
Failed attempts remain in the immutable file inventory.
"""
import argparse
import ast
from collections import Counter
import hashlib
import json
import resource
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def record(path): return {'path':str(path.relative_to(ROOT)), 'sha256':sha(path)}
def load_passed(path):
    assert path.is_file() and not path.is_symlink(), str(path)
    data=json.loads(path.read_text())
    assert data.get('passed') is True and not data.get('error'), str(path)
    return data

def closure(path, data, source=ROOT):
    assert data.get('inputs'), str(path)
    for relative,digest in data['inputs'].items():
        entry=source/relative
        assert entry.is_file() and not entry.is_symlink() and sha(entry)==digest, relative
        snapshot=path.parent/'inputs'/relative
        assert snapshot.is_file() and sha(snapshot)==digest, relative
    for relative,digest in data.get('artifacts',{}).items():
        assert sha(path.parent/relative)==digest,relative

parser=argparse.ArgumentParser()
parser.add_argument('--native-report',type=Path)
parser.add_argument('--regression-report',type=Path)
args=parser.parse_args()
target=ROOT/'qa/implementation-manifest.json'
assert not target.exists(), 'Frozen manifests are immutable'
build_path=sorted((ROOT/'qa').glob('build-*/report.json'))[-1]
replay_path=sorted((ROOT/'qa').glob('replay-*/report.json'))[-1]
build=load_passed(build_path);replay=load_passed(replay_path)
closure(build_path,build);closure(replay_path,replay)
assert build['inputs'].get('qa/freeze.py')==sha(Path(__file__)), 'Rebuild after adding or changing freezer'
assert replay['inputs'].get('qa/freeze.py')==sha(Path(__file__)), 'Rerun compiled menu checks with current freezer'
assert all(row['exitCode']==0 for row in build['commands'])
assert all(row['exitCode']==0 for row in replay['commands'])
assert replay['checks']>=48
assert sha(build_path.parent/'elm-host')==build['binarySHA256']
preserved={}
for name,count in [('replay',20),('shell',27),('surface',55)]:
    path=build_path.parent/(name+'-report.json');data=load_passed(path)
    assert data['checks']==count,name
    preserved[name]={'report':record(path),'checks':count}
# Verify original candidates against their pre-existing accepted captures.
upstream=json.loads((ROOT/'upstream.json').read_text())
original_build=REPO/upstream['baseBuildReport'];base=load_passed(original_build)
closure(original_build,base,REPO/upstream['base'])
menu_original=REPO/upstream['menuAdapter'];menu_manifest=menu_original/'qa/implementation-manifest.json'
menu_capture=load_passed(menu_manifest)
for path in (menu_original/'src').glob('*.elm'):
    relative=str(path.relative_to(menu_original))
    assert sha(path)==menu_capture['files'][relative]['sha256'],relative
oracle_path=ROOT/'qa/scenario-oracle.json'
assert build['inputs'].get('qa/scenario-oracle.json')==sha(oracle_path), 'Rebuild with reviewed scenario oracle'
oracle=json.loads(oracle_path.read_text())
for key in ('originalReport','originalSource','originalFixture'):
    assert sha(REPO/oracle[key]['path'])==oracle[key]['sha256'],key
original_regression=REPO/oracle['originalSource']['path']
original_native=load_passed(REPO/oracle['originalReport']['path'])
assert original_native['cleanupPassed'] and len(original_native['checks'])==92
assert Counter(check['name'] for check in original_native['checks'])==Counter(oracle['originalCheckNames'])
assert sha(ROOT/'fixture.py')==oracle['originalFixture']['sha256']
assert sha(ROOT/'qa/fixture.py')==oracle['originalFixture']['sha256']
def calls(text,name):
    tree=ast.parse(text)
    return [ast.dump(node,include_attributes=False) for node in sorted(ast.walk(tree),key=lambda node:(getattr(node,'lineno',0),getattr(node,'col_offset',0)))
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id==name]
# Approved wrapper edits change locations and add provenance metadata only.
expected=original_regression.read_text()
patches=[("GUI=REPO/'implementation/elm-popup-choice-barrier-v87'","GUI=ROOT"),
    ("FIXTURE=ROOT/'fixture.py'","FIXTURE=ROOT/'qa/fixture.py'"),
    ("str(GUI/'adapter/daemon.py')","str(build_path.parent/'inputs/adapter/daemon.py')"),
    ("report.update(buildReport=", "report['originalScenario']={'path':'implementation/elm-surface-regression-qa-v93/qa/regression.py','sha256':host.digest(REPO/'implementation/elm-surface-regression-qa-v93/qa/regression.py'),'changes':'candidate path and frozen backend/fixture location only; scenarios and deadlines retained'}\n report.update(buildReport=")]
for old,new in patches:
    assert expected.count(old)==(2 if old=="str(GUI/'adapter/daemon.py')" else 1),old
    expected=expected.replace(old,new)
actual=(ROOT/'qa/regression.py').read_text()
assert ast.dump(ast.parse(actual),include_attributes=False)==ast.dump(ast.parse(expected),include_attributes=False), 'Unapproved regression scenario change'
assert calls(original_regression.read_text(),'check')==calls(actual,'check'), 'Original check arguments/order changed'
assert calls(original_regression.read_text(),'wait')==calls(actual,'wait'), 'Original wait arguments/order changed'
native_reports={}
for lane,selected in [('context-menu',args.native_report),('preserved-window-regression',args.regression_report)]:
    if selected is None: continue
    path=selected.resolve()
    assert path.is_relative_to(ROOT/'qa') and path.name=='report.json',str(path)
    assert path.parent.name.startswith('native-'),str(path)
    data=load_passed(path)
    lane_script=ROOT/'qa'/('native.py' if lane=='context-menu' else 'regression.py')
    other_script=ROOT/'qa'/('regression.py' if lane=='context-menu' else 'native.py')
    assert data.get('inputs',{}).get(str(lane_script))==sha(lane_script), 'Wrong native scenario identity'
    assert str(other_script) not in data['inputs'], 'Ambiguous native lane identity'
    names=Counter(check['name'] for check in data.get('checks',[]))
    if lane=='preserved-window-regression':
        assert names==Counter(oracle['originalCheckNames']), 'Original 91+1 native check multiset changed'
        assert data.get('originalScenario',{}).get('sha256')==oracle['originalSource']['sha256']
    else:
        assert all(names[name]==1 for name in oracle['menuRequiredChecks']), 'Incomplete native menu scenario'
    assert data.get('cleanupPassed') is True,str(path)
    assert data.get('mainDesktopActions') is False,str(path)
    assert data.get('checks') and all(check['passed'] for check in data['checks']),str(path)
    for source,digest in data['inputs'].items(): assert sha(Path(source))==digest,source
    linked=Path(data['buildReport']);linked_data=load_passed(linked)
    assert linked.is_relative_to(ROOT/'qa') and sha(linked)==data['buildReportSHA256']
    closure(linked,linked_data)
    # A later build may add this freezer; every tested production input remains exact.
    for relative,digest in linked_data['inputs'].items():
        if relative.startswith(('src/','native/','adapter/','assets/')) or relative in ('elm.json','fixture.py'):
            assert build['inputs'].get(relative)==digest,relative
    for relative,digest in data.get('artifacts',{}).items(): assert sha(path.parent/relative)==digest,relative
    native_reports[lane]={'report':record(path),'buildReport':record(linked),'scope':data['scope'],'checks':len(data['checks'])}
files={};links={}
for candidate in sorted(ROOT.rglob('*')):
    relative=str(candidate.relative_to(ROOT))
    if candidate.is_symlink():links[relative]=str(candidate.readlink())
    elif candidate.is_file():files[relative]={'sha256':sha(candidate),'size':candidate.stat().st_size}
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),
    'scope':'Visible production menu/controller compiled checks and explicitly selected private native scenarios; scoped evidence only',
    'wholeFeatureAccepted':False,'newNativeGuiAccepted':False,'roadmapCompleted':False,'completedRequirementIds':[],
    'buildReport':record(build_path),'replayReport':record(replay_path),'menuChecks':replay['checks'],
    'preservedChecks':preserved,'nativeScenarioReports':native_reports,
    'scenarioOracle':record(oracle_path),'originalCheckCallASTPreserved':True,'originalWaitCallASTPreserved':True,'normalizedRegressionASTPreserved':True,
    'originalReports':{'baseBuild':{'path':str(original_build.relative_to(REPO)),'sha256':sha(original_build)},
                       'menuManifest':{'path':str(menu_manifest.relative_to(REPO)),'sha256':sha(menu_manifest)}},
    'remainingGates':['complete manager-checked right-click gesture interleavings and policy',
        'bar keyboard context invocation, scoped opener focus restoration and accessibility',
        'multioutput identities, positioning, transforms and mixed scale',
        'application, Files and background provider actions',
        'all-origin uncertainty and lost-broker journal recovery',
        'GPU/hardware budgets, IME, complete native roadmap and release journeys'],
    'files':files,'symlinks':links}
with target.open('x') as stream:stream.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(target),'files':len(files),'nativeScenarios':list(native_reports)}))
