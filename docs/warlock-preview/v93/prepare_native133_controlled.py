"""Fresh actual controlled-host probe on the unchanged reviewed native tuple."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v132';root=repo/'implementation/warlock-client-provider-native-v133';provider=repo/'implementation/warlock-preview-provider-v123';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert not d['passed'] and d['sourceHeld'] and d['cpuBuildPassed'] and d['privateSessionCleanupPassed'] and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
pre=json.loads((parent/'qa/preflight.json').read_text());assert pre['passed'] and not pre['nativeLaunched']
for p,h in pre['inputs'].items():assert sha(p)==h,p
reports=[]
for p in provider.glob('qa/build-*/report.json'):
 b=json.loads(p.read_text())
 if b['passed'] and len(b['commands'])==118 and all(sha(provider/n)==h for n,h in b['inputs'].items()):reports.append((p,b))
assert len(reports)==1;build,b=reports[0]
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
assert sha(build.parent/'elm-host')==b['binarySHA256']
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() or n=='preflight.json']
 return [n for n in names if n=='__pycache__']
shutil.copytree(parent,root,ignore=ignore)
runner=pathlib.Path(__file__).with_name('native132_controlled_runner.py');assert runner.is_file();shutil.copy2(runner,root/'qa/native-controlled-host.py')
inputs=dict(pre['inputs']);inputs[str(m)]=sha(m);inputs[str(parent/'qa/preflight.json')]=sha(parent/'qa/preflight.json');inputs[str(build)]=sha(build);inputs[str(build.parent/'elm-host')]=b['binarySHA256']
for base in ['src','native','assets','adapter','qa']:
 for p in (provider/base).glob('*'):
  if p.is_file():inputs[str(p)]=sha(p)
for n,h in b['artifacts'].items():inputs[str(build.parent/n)]=h
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():inputs[p]=row['sha256']
for base in [root,root/'qa']:
 for p in base.iterdir():
  if p.is_file():inputs[str(p)]=sha(p)
pre.update(inputs=inputs,controlledHostBinary=str(build.parent/'elm-host'),controlledHostAssets=str(build.parent/'inputs/assets'),controlledHostBackend=str(build.parent/'inputs/adapter/daemon.py'),controlledHostBuild=str(build),controlledHostBuildSHA256=sha(build),controlledSourceRoot=str(provider),retainedNative132FailureManifest=str(m),retainedNative132FailureManifestSHA256=sha(m),scope='QA-only actual controlled GTK/native persistent policy/pure WebKit renderer admission and closure probe on original core16/plugin19/AQ155. Physical curtain remains closed. This separate probe does not rerun or replace the original legacy2518/278 baseline, full S09 preview13, physical reveal, workload/RSS, reload recovery or full release acceptance.')
assert all(sha(p)==h for p,h in inputs.items());(root/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'currentProviderBuild':str(build),'currentProviderBuildSHA256':sha(build),'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS ownNative133 corrected actual controlled-host GTK/WebKit admission/closure probe. GUI122 current118-command build, original Native1312518/278 manifest and all preflight/source/build/tools/ABI inputs verified; exact core16/plugin19/AQ155 unchanged. New probe never replaces original legacy controls or claims full preview/frame/physical reveal acceptance. Native opacity curtain stays closed; one immutable native policy, pure renderer and original native physical/journal/independent-confirmation custody. Shared native lock and unchanged protected launcher required. Installed/drafts/foreign preserved.'],'progress',[str((root/'qa/preflight.json').relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
