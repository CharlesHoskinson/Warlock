"""Fresh actual controlled-host probe on the unchanged reviewed native tuple."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v138';root=repo/'implementation/warlock-client-provider-native-v167';provider=repo/'implementation/warlock-preview-provider-v138';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['passed'] and d['normalControlledHostClosureQualified'] and d['sourceHeld'] and d['cpuBuildPassed'] and d['privateSessionCleanupPassed'] and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
pre=json.loads((parent/'qa/preflight.json').read_text());assert pre['passed'] and not pre['nativeLaunched']
for p,h in pre['inputs'].items():assert sha(p)==h,p
reports=[]
for p in provider.glob('qa/build-*/report.json'):
 b=json.loads(p.read_text())
 if b['passed'] and len(b['commands'])==119 and all(sha(provider/n)==h for n,h in b['inputs'].items()):reports.append((p,b))
assert len(reports)==1;build,b=reports[0]
assert '/usr/bin/grim' in pre['inputs'] and sha('/usr/bin/grim')==pre['inputs']['/usr/bin/grim']
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
assert sha(build.parent/'elm-host')==b['binarySHA256']
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() or n=='preflight.json']
 return [n for n in names if n=='__pycache__']
shutil.copytree(parent,root,ignore=ignore)
runner=pathlib.Path(__file__).with_name('native159_cancelled_reopened_snapshot_runner.py');assert runner.is_file();shutil.copy2(runner,root/'qa/native-controlled-host.py')
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
pre.update(inputs=inputs,controlledHostBinary=str(build.parent/'elm-host'),controlledHostAssets=str(build.parent/'inputs/assets'),controlledHostBackend=str(build.parent/'inputs/adapter/daemon.py'),controlledHostBuild=str(build),controlledHostBuildSHA256=sha(build),controlledSourceRoot=str(provider),retainedNative138PositiveManifest=str(m),retainedNative138PositiveManifestSHA256=sha(m),scope='QA-only actual controlled GTK/native persistent policy/pure WebKit renderer private Wayland output observation probe retaining original image pixels and admission/closure checks on original core16/plugin19/AQ155. Physical curtain remains closed. This separate probe does not rerun or replace the original legacy2518/278 baseline, full S09 preview13, physical reveal, workload/RSS, reload recovery or full release acceptance.')
oracleReport=repo/'docs/warlock-preview/v93/curtain-oracle-build-1791385499631701448/report.json';o=json.loads(oracleReport.read_text());assert o['passed']
for p,h in o['inputs'].items():assert sha(p)==h,p;inputs[p]=h
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,h in o[category].items():assert sha(p)==h,p;inputs[p]=h
for p,h in o['artifacts'].items():assert sha(oracleReport.parent/p)==h,p;inputs[str(oracleReport.parent/p)]=h
inputs[str(oracleReport)]=sha(oracleReport);pre.update(popupCurtainOracle=str(oracleReport.parent/'popup-curtain-oracle'),popupCurtainOracleBuild=str(oracleReport),scope='QA-only original real WebKit snapshot result through strict old C realm close/view replacement/later same-policy native epoch/current projection acknowledgement, original16 GTK/native admission and strict drain/teardown controls and original grim private output region observation, with actual pure renderer source pixels and all original26 admission/image/output/drain checks. Original scenario deadline6/core16/plugin19/AQ155/physical/journal/confirmation and strict close unchanged. Distinct bounded stale-result probe: original16 admission/drain controls retained; one actual originally canceled GCancellable/WebKit result held across strict old close and actual new native epoch; actual original finish must report image0/G_IO_ERROR_CANCELLED once, current view epoch navigation projection guard must reject old request1 error/artifact without current GUI failure, current new request2 original source pixels/opacity0 output and strict final cleanup qualify separately. Does not replace normal Native14029-control regression or qualify reload/process/uncertain recovery. GTK after-paint is not Wayland or hardware presentation; physical reveal/recovery/full release remain open.')
assert all(sha(p)==h for p,h in inputs.items());(root/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'currentProviderBuild':str(build),'currentProviderBuildSHA256':sha(build),'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS ownNative167 packaged actual controlled-host GTK/WebKit admission/closure probe. GUI138 current119-command build with current projection/native snapshot context guards and private loaded-image observer, actual original grim output capture/independent decoder to prepare physical frame/concealment qualification; exact packaged HTML/script/style closure, original Native1312518/278 manifest and all preflight/source/build/tools/ABI inputs verified; exact core16/plugin19/AQ155 unchanged. Host strict realm retirement/context replacement is active, but this unchanged delayed-result regression does not qualify a later GUI reopen or unknown/process recovery. New probe never replaces original legacy controls or claims full preview/frame/physical reveal acceptance. Native opacity curtain stays closed; one immutable native policy, pure renderer and original native physical/journal/independent-confirmation custody. Shared native lock and unchanged protected launcher required. Installed/drafts/foreign preserved.'],'progress',[str((root/'qa/preflight.json').relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))

