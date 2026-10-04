"""Original135 behavioral oracles/deadlines; new coherent GUI/native tuple pins."""
import ast,hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
GUI=REPO/'implementation/elm-focus-recovery-integrated-gui-v333';CORE=REPO/'implementation/elm-grant-retirement-runtime-v595'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pointer=GUI/'qa/current-build.json';BUILD=Path(json.loads(pointer.read_text())['report'])
build=json.loads(BUILD.read_text());assert build['passed']
for name,digest in build['inputs'].items():assert sha(GUI/name)==digest,name
assert sha(BUILD.parent/'elm-host')==build['binarySHA256']
for name,digest in build['artifacts'].items():assert sha(BUILD.parent/name)==digest,name
for name,digest in build['inputs'].items():assert sha(BUILD.parent/'inputs'/name)==digest if name!='assets/elm.js' and name!='assets/bar.js' and name!='assets/popup.js' else True
pair_path=CORE/'qa/build-pair-manifest.json';pair=json.loads(pair_path.read_text());assert pair['passed']
for name,digest in pair['files'].items():assert sha(CORE/name)==digest,name
for r in pair['nativePair'].values():assert sha(r['path'])==r['sha256']
assert sha(pair['owningAcceptance'])==pair['owningAcceptanceSHA256']
assert sha(pair['owningCoreComponent'])==pair['owningCoreComponentSHA256']
descriptor=json.loads((CORE/'native-build-report.json').read_text());assert sha(descriptor['pluginBuildReport'])==descriptor['pluginBuildReportSHA256']
native_build=json.loads(Path(descriptor['pluginBuildReport']).read_text());assert native_build['passed'] and native_build['core']['sha256']==pair['nativePair']['core']['sha256']
for k in ['dependencies','linkedLibraries']:
 for p,digest in native_build[k].items():assert sha(p)==digest,p
grant_report=REPO/'implementation/elm-grant-retirement-native-v596/qa/native-1791146569027803533/report.json'
grant=json.loads(grant_report.read_text());assert grant['passed'] and grant['cleanupPassed'] and len(grant['checks'])==42 and grant['pair']==pair['nativePair']
for p,digest in grant['artifacts'].items():assert sha(grant_report.parent/p)==digest,p
code=(ROOT/'qa/native.py').read_text();ast.parse(code)
original=ast.parse((REPO/'implementation/elm-responsive-full-menu-v281/qa/native.py').read_text());actual=ast.parse(code)
def calls(tree,name):
 return [ast.dump(n,include_attributes=False) for n in sorted(ast.walk(tree),key=lambda n:(getattr(n,'lineno',0),getattr(n,'col_offset',0))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
for name in ['check','wait']:assert calls(original,name)==calls(actual,name),name
for name in ['wait','click','check']:
 old=next(n for n in ast.walk(original) if isinstance(n,ast.FunctionDef) and n.name==name);new=next(n for n in ast.walk(actual) if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),name
assert 'xwayland={enabled=false}' in code and 'Unchanged observation deadline' in code
assert "if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok'" in code
assert "str(build_path.parent/'inputs/adapter/daemon.py')" in code and "str(build_path.parent/'inputs/assets')" in code
observer_path=ROOT/'observer-build.json';observer=json.loads(observer_path.read_text());assert sha(observer['buildReport'])==observer['buildReportSHA256']
ob=json.loads(Path(observer['buildReport']).read_text());assert ob['passed'] and ob['core']['sha256']==pair['nativePair']['core']['sha256'] and not ob['missingSymbols'];assert sha(ob['binary'])==ob['binarySHA256']
for k in ['dependencies','linkedLibraries']:
 for x,d in ob[k].items():assert sha(x)==d
paths=[observer_path,Path(observer['buildReport']),Path(ob['binary']),*sorted((ROOT/'qa').glob('*.py')),ROOT/'fixture.py',pointer,BUILD,BUILD.parent/'elm-host',*[BUILD.parent/'inputs'/n for n in build['inputs']],*sorted(CORE.glob('*.*')),pair_path,grant_report,*[Path(r['path']) for r in pair['nativePair'].values()],
 Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer'),Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard'),Path('/usr/bin/grim'),Path('/usr/bin/magick')]
pins={str(p.resolve()):sha(p) for p in paths if p.is_file()}
out=ROOT/'qa/preflight.json';assert not out.exists()
out.write_text(json.dumps({'passed':True,'source':str(GUI),'runtime':str(CORE),'buildReport':str(BUILD),'nativeGrantQualifiedReport':str(grant_report),'inputs':pins,'claim':'Source/oracle/ABI closure only; native GUI acceptance separate','mainDesktopActions':False},indent=2)+'\n')
print(out)
