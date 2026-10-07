"""Hold the actual failed Elm mount-node integration before a fresh derivative."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=repo/'implementation/warlock-preview-provider-v123';native=repo/'implementation/warlock-client-provider-native-v133';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
report=native/'qa/native-controlled-1791381735280537776/report.json';d=json.loads(report.read_text());assert not d['passed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and d['cleanupPassed'] and any(row['name']=='controlled-host' and row['exitCode']==1 for row in d['ownedExitCodes'])
pre=json.loads((native/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in d['artifacts'].items():assert sha(report.parent/rel)==h,rel
build=pathlib.Path(pre['controlledHostBuild']);b=json.loads(build.read_text());assert b['passed'] and len(b['commands'])==118 and all(x['exitCode']==0 for x in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
scope='Actual GTK admission, factory and single native driver reached. Actual pure renderer initialization failed because the page requested native-preview-renderer.js while the compiler produces native-visual-renderer.js. Original six-second observation deadline and strict closure unchanged; controlled host exited1 with live uncertainty retained, private session cleanup passed. Full118-command CPU build passed. Earlier compiled host pressure2264 and synthetic adapter checks remain scoped source snapshots, not acceptance of this failed integration. No actual pure renderer, physical reveal/concealment, scoped URI execution, normal controlled closure, workload or release acceptance. Next fresh GUI124 corrects HTML/allowlist to the original compiled native-visual-renderer.js filename and checks packaged HTML assets; no grant reset/second policy/deadline change. Original Native131 legacy2518/278 remains baseline.'
for root in [gui,native]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 out=root/'component-manifest.json';assert not out.exists();out.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'cpuBuildPassed':True,'fullBuildCommands':118,'failedNativeReport':str(report),'failedNativeReportSHA256':sha(report),'privateSessionCleanupPassed':True,'actualNativeGTKAdmissionObserved':True,'actualPureRendererInitializationQualified':False,'normalControlledHostClosureQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'files':files},indent=2)+'\n');print(root.name,len(files))
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(gui.relative_to(repo)),['PROGRESS held failedGUI123/Native133 actual controlled host integration. GTK admission and controlled factory/single native driver reached; pure receiver initializer failed because Elm replaced its mount node/app id. Original deadline6 and strict native/uncertain closure unchanged; host exited1, private runtime cleanup passed. Current CPU full118 passed; earlier CPU compiled host pressure2264/normal synthetic peer and synthetic adapter checks preserved as their own snapshots. No actual renderer/physical reveal/normal controlled closure acceptance. Next ownGUI124 correct original compiled renderer asset filename and add packaged HTML asset closure checks, then current CPU/full build and serial actual scenario unchanged. Native1312518/278 actual legacy baseline and all full release gates remain; no installed/draft/foreign changes.'],'progress',[str((gui/'component-manifest.json').relative_to(repo)),str((native/'component-manifest.json').relative_to(repo)),str(report.relative_to(repo))]))
