"""CPU-only source/ABI closure preparation; never launches GUI or native clients."""
import argparse,ast,hashlib,json,pathlib,resource,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
p=argparse.ArgumentParser();p.add_argument('--gui',required=True,type=pathlib.Path);p.add_argument('--output',required=True,type=pathlib.Path);p.add_argument('--native-output-directory',required=True,type=pathlib.Path);args=p.parse_args()
GUI=args.gui;CORE=REPO/'implementation/elm-grant-retirement-runtime-v595'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
assert GUI.is_absolute() and GUI.resolve()==GUI
pointer=GUI/'qa/current-build.json';build_path=pathlib.Path(json.loads(pointer.read_text())['report']);build=json.loads(build_path.read_text());assert build['passed']
for name,digest in build['inputs'].items():assert sha(GUI/name)==digest,name
assert sha(build_path.parent/'elm-host')==build['binarySHA256']
for name,digest in build['artifacts'].items():assert sha(build_path.parent/name)==digest,name
for name in ['delivery_ledger.py','reconciliation.py','recovery_store.py','daemon.py']:assert 'adapter/'+name in build['inputs']
pair_path=CORE/'qa/build-pair-manifest.json';pair=json.loads(pair_path.read_text());assert pair['passed']
for name,digest in pair['files'].items():assert sha(CORE/name)==digest,name
for row in pair['nativePair'].values():assert sha(row['path'])==row['sha256']
assert sha(pair['owningAcceptance'])==pair['owningAcceptanceSHA256']
descriptor=json.loads((CORE/'native-build-report.json').read_text());assert sha(descriptor['pluginBuildReport'])==descriptor['pluginBuildReportSHA256']
native_build=json.loads(pathlib.Path(descriptor['pluginBuildReport']).read_text());assert native_build['passed'] and native_build['core']['sha256']==pair['nativePair']['core']['sha256']
for group in ['dependencies','linkedLibraries']:
 for name,digest in native_build[group].items():assert sha(name)==digest,name
baseline=ast.parse((REPO/'implementation/elm-reconciliation-native-journey-v627/qa/regression.py').read_text());runner=ast.parse((ROOT/'qa/runner.py').read_text())
for name in ['wait','click']:
 old=next(n for n in ast.walk(baseline) if isinstance(n,ast.FunctionDef) and n.name==name);new=next(n for n in ast.walk(runner) if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False),name
assert 'xwayland={enabled=false}' in (ROOT/'qa/runner.py').read_text()
assert 'g_subprocess_send_signal' in (build_path.parent/'inputs/native/host.c').read_text()
paths=[*sorted((ROOT/'qa').glob('*.py')),ROOT/'fixture.py',pointer,build_path,build_path.parent/'elm-host',*[build_path.parent/'inputs'/n for n in build['inputs']],pair_path,*[pathlib.Path(r['path']) for r in pair['nativePair'].values()],CORE/'candidate_host.py',pathlib.Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')]
pins={str(path.resolve()):sha(path) for path in paths if path.is_file()}
assert GUI==REPO/'implementation/elm-focus-recovery-integrated-gui-v333'
sys.path.insert(0,str(ROOT/'qa'));from closure import verify_current
pins.update(verify_current(ROOT))
assert args.output.is_absolute() and not args.output.exists() and args.native_output_directory.is_absolute() and not args.native_output_directory.exists()
value={'passed':True,'gui':str(GUI),'buildReport':str(build_path),'inputs':pins,'outputDirectory':str(args.native_output_directory),'claim':'Source/ABI closure only, target must be separately reviewed for repeated reconnect liveness; native campaign unrun','mainDesktopActions':False}
args.output.write_text(json.dumps(value,indent=2));args.output.chmod(0o600);print(args.output)
