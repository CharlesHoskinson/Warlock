"""CPU/source closure only. No Wayland clients or graphics workload launched."""
import ast,hashlib,json,os,pathlib,resource,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
binding=json.loads((ROOT/'qa/runner-binding.json').read_text());bp=pathlib.Path(binding['buildReport']);check('fixed-instrumented-build-hash',sha(bp)==binding['buildReportSHA256']);b=json.loads(bp.read_text());check('actual-Elm-C-build-passed',b['passed']);check('actual-instrumented-host-binary',sha(bp.parent/'elm-host')==b['binarySHA256'])
inputs={str(bp):sha(bp),str(bp.parent/'elm-host'):sha(bp.parent/'elm-host')}
for name,h in b['inputs'].items():check('built-source-'+name,sha(ROOT/name)==h);inputs[str((ROOT/name).resolve())]=h
for category in ['compilerDependencies','linkedLibraries','tools']:
 for name,row in b[category].items():check('compiled-closure-'+name,sha(name)==row['sha256']);inputs[name]=row['sha256']
base=REPO/'implementation/elm-stable-surface-publication-v521'; baseline=base/'qa/build-1791138800386580258/report.json';d=json.loads(baseline.read_text());check('baseline521-build-passed',d['passed']);inputs[str(baseline)]=sha(baseline)
for name,h in d['inputs'].items():check('baseline521-source-'+name,sha(base/name)==h);inputs[str(base/name)]=h
allowed={'native/shared-host.c','assets/bar-adapter.js'}
for folder in ['src','native','adapter','assets']:
 for f in (ROOT/folder).iterdir():
  if f.is_file() and str(f.relative_to(ROOT)) not in allowed:check('baseline-byte-equal-'+str(f.relative_to(ROOT)),f.read_bytes()==(base/f.relative_to(ROOT)).read_bytes())
core=REPO/'implementation/elm-keyboardless-current-runtime-v216';pairpath=core/'qa/build-pair-manifest.json';pair=json.loads(pairpath.read_text());check('owning-runtime-manifest',pair['passed']);inputs[str(pairpath)]=sha(pairpath)
for name,h in pair['files'].items():check('owning-runtime-'+name,sha(core/name)==h);inputs[str(core/name)]=h
for name,row in pair['nativePair'].items():check('exact-owning-pair-'+name,sha(row['path'])==row['sha256']);inputs[row['path']]=row['sha256']
check('Core205-plugin206-AQ155-pair', 'elm-core-keyboardless-focus-v205/' in pair['nativePair']['core']['path'] and 'elm-keyboardless-focus-owning-pair-v206/' in pair['nativePair']['plugin']['path'] and 'elm-keyboard-focus-cancellation-v155/' in pair['nativePair']['aquamarine']['path'])
for k in ['owningAcceptance','producerEvidence']:
 check('owning-ancestry-'+k,sha(pair[k])==pair[k+'SHA256']);inputs[pair[k]]=pair[k+'SHA256']
producer=json.loads(pathlib.Path(pair['producerEvidence']).read_text());check('ancestry-bounded-not-release',producer['sourceHeld'] and producer['evidenceIntegrityPassed'] and producer['nativeAcceptance'] and not producer['fullReleaseAccepted'])
for row in producer['files']:check('ancestry-source-'+row['path'],sha(REPO/row['path'])==row['sha256']);inputs[str(REPO/row['path'])]=row['sha256']
for row in producer.get('symlinks',[]):check('ancestry-symlink-'+row['path'],str((REPO/row['path']).readlink())==row['target'])
code=(ROOT/'qa/native.py').read_text();tree=ast.parse(code);old=ast.parse((REPO/'implementation/elm-related-gpu-qa-v166/qa/regression.py').read_text())
names=['sharedBarExecutesWebGLShaderReadback','sharedBarReportsRendererIdentity','nativeEngineReportsHardwareRenderer','probeRetiresShaderObjects','shaderPixelsActuallyDisplayedByNativeBar','webgpuCapabilityHasExplicitResult','secondSharedBarExecutesShader']
def named(tree,name):return [ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value==name]
for name in names:check('original-graphics-assertion-'+name,len(named(tree,name))==1 and named(tree,name)==named(old,name))
for name in ['wait','check']:
 f=lambda t:next(n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name==name)
 check('original-deadline-helper-'+name,ast.dump(f(tree),include_attributes=False)==ast.dump(f(old),include_attributes=False))
check('compiled-assets-backend-one-build',"str(build_path.parent/'inputs/assets')" in code and "str(build_path.parent/'inputs/adapter/daemon.py')" in code)
check('original-private-runtime-and-ordered-teardown',"CORE=REPO/'implementation/elm-keyboardless-current-runtime-v216'" in code and 'host.PrivateHyprSession' in code and 'xwayland={enabled=false}' in code and "if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok'" in code and 'process.wait(timeout=5)' in code)
c=(ROOT/'native/shared-host.c').read_text();js=(ROOT/'assets/bar-adapter.js').read_text();check('QA-only-bounded-probe', 'qa_exit && origin && kind && g_str_equal(kind,"gpu-probe") && strlen(text)<=16384' in c and 'if (window.elmHostQA)' in js)
check('sandboxed-secure-origin', 'webkit_web_context_set_sandbox_enabled(shared_context,TRUE)' in c and 'register_uri_scheme_as_secure' in c)
check('unprivileged-restricted-diagnostic', '"webkit://gpu"' in c and '"user-content-manager"' not in c[c.index('gpu_diagnostic='):c.index('gpu_diagnostic=')+190] and 'g_object_unref(gpu_diagnostic)' in c)
for f in [*ROOT.glob('*.py'),*ROOT.joinpath('qa').glob('*.py'),ROOT/'qa/runner-binding.json',pathlib.Path('/usr/bin/grim'),pathlib.Path('/usr/bin/magick')]:inputs[str(f.resolve())]=sha(f)
report={'passed':True,'scope':'Protected CPU build/source/preflight closure only; no new native/GPU/calibration acceptance','checks':checks,'inputs':inputs,'nativePair':pair['nativePair'],'baselineGui':str(base),'instrumentedGui':str(ROOT),'runtime':str(core),'mainDesktopActions':False,'budgetsAccepted':False,'parentSocketQualification':'Native runtime216 PrivateHyprSession retains live parent verification, private runtime, nested-only and ordered teardown; CPU preflight does not launch or qualify a parent/client.'};(ROOT/'qa/preflight.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(checks),'sourceInputs':len(inputs)}))
