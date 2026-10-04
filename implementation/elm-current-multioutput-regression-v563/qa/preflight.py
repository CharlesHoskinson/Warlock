"""Read-only source/runtime closure before serial protected native input QA."""
import ast,hashlib,json,resource,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
SOURCE=REPO/'implementation/elm-stable-surface-publication-v521';CORE=REPO/'implementation/elm-keyboardless-current-runtime-v216'
BUILD=SOURCE/'qa/build-1791138800386580258';d=json.loads((BUILD/'report.json').read_text());assert d['passed']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in d['inputs'].items():assert sha(SOURCE/name)==digest
assert sha(BUILD/'elm-host')==d['binarySHA256']
code=(ROOT/'qa/regression.py').read_text();ast.parse(code)
assert 'xwayland={enabled=false}' in code
assert "CORE=REPO/'implementation/elm-keyboardless-current-runtime-v216';GUI=REPO/'implementation/elm-stable-surface-publication-v521'" in code
assert "str(build_path.parent/'inputs/adapter/daemon.py')" in code
assert 'Unchanged observation deadline' in code and "if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok'" in code
pair=json.loads((CORE/'qa/build-pair-manifest.json').read_text());assert pair['passed']
assert sha(Path(pair['owningAcceptance']))==pair['owningAcceptanceSHA256']
for row in pair['nativePair'].values():assert sha(Path(row['path']))==row['sha256']
assert sha(Path(pair['producerEvidence']))==pair['producerEvidenceSHA256']
producer=json.loads(Path(pair['producerEvidence']).read_text());assert producer['sourceHeld'] and producer['evidenceIntegrityPassed'] and producer['nativeAcceptance'] and not producer['fullReleaseAccepted']
for entry in producer['files']:assert sha(REPO/entry['path'])==entry['sha256']
for entry in producer.get('symlinks',[]):assert str((REPO/entry['path']).readlink())==entry['target']
descriptor=json.loads((CORE/'native-build-report.json').read_text());assert sha(Path(descriptor['pluginBuildReport']))==descriptor['pluginBuildReportSHA256']
pluginBuild=json.loads(Path(descriptor['pluginBuildReport']).read_text());assert pluginBuild['passed'] and pluginBuild['core']['sha256']==pair['nativePair']['core']['sha256']
for path,digest in pluginBuild['dependencies'].items():assert sha(Path(path))==digest
for path,digest in pluginBuild['linkedLibraries'].items():assert sha(Path(path))==digest

original=ast.parse((REPO/'implementation/elm-output-shared-qa-v151/qa/regression.py').read_text());actual=ast.parse(code)
def calls(tree,name):
 return [ast.dump(n,include_attributes=False) for n in sorted(ast.walk(tree),key=lambda n:(getattr(n,'lineno',0),getattr(n,'col_offset',0))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
for name in ['check','wait']:assert calls(original,name)==calls(actual,name),name
for name in ['wait','click','check','choose','press_key']:
 old=next(n for n in ast.walk(original) if isinstance(n,ast.FunctionDef) and n.name==name);new=next(n for n in ast.walk(actual) if isinstance(n,ast.FunctionDef) and n.name==name);assert ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),name
current=REPO/'implementation/elm-keyboardless-current-acceptance-v222/acceptance-manifest.json';assert sha(current)=='bbb42789486071600535cf66d4ba869722530c6fe590cc7f1af72a203fc80fe4';accepted=json.loads(current.read_text());assert accepted['nativePair']==pair['nativePair'] and accepted['gui']==str(SOURCE.relative_to(REPO)) and accepted['acceptedGuiNativeCheckCount']==473
paths=[*sorted((ROOT/'qa').glob('*.py')),ROOT/'fixture.py',current,*sorted(CORE.glob('*.*')),CORE/'qa/build-pair-manifest.json',BUILD/'report.json',BUILD/'elm-host',*[BUILD/'inputs'/p for p in d['inputs']],*sorted((BUILD/'inputs/assets').glob('*')),*sorted((BUILD/'inputs/adapter').glob('*.py')),Path(pair['owningAcceptance']),*[Path(row['path']) for row in pair['nativePair'].values()],Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer'),Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard'),Path('/usr/bin/grim'),Path('/usr/bin/magick')]
inputs={str(p.resolve()):sha(p) for p in paths if p.is_file()}
p=ROOT/'qa/preflight.json';assert not p.exists()
p.write_text(json.dumps({'passed':True,'scope':'Source/runtime closure only; actual native input results separate','inputs':inputs,'source':str(SOURCE),'runtime':str(CORE),'mainDesktopActions':False},indent=2)+'\n');print(str(p))
