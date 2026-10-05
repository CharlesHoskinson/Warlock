"""Freeze exact owned client prototype/evidence; keep release claims bounded."""
import hashlib,json,pathlib
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
for kind,versions in [('warlock-client-capture',range(1,5)),('warlock-client-capture-native',range(1,5))]:
 for v in versions:
  root=REPO/'implementation'/f'{kind}-v{v}';d=json.loads((root/'component-manifest.json').read_text())
  assert all((root/rel).stat().st_size==row['size'] and sha(root/rel)==row['sha256'] for rel,row in d['files'].items())
source=REPO/'implementation/warlock-client-capture-v5';native=REPO/'implementation/warlock-client-capture-native-v5';build=json.loads((source/'native-build-report.json').read_text());assert build['result']=='pass' and sha(build['plugin']['path'])==build['plugin']['sha256'] and sha(build['pluginBuildReport'])==build['pluginBuildReportSHA256']
reportPath=native/'qa/native-1791233397651613475/report.json';report=json.loads(reportPath.read_text());assert report['passed'] and report['cleanupPassed'] and len(report['checks'])==73 and all(x['passed'] for x in report['checks']) and all(x['exitCode']==0 for x in report['ownedExitCodes'])
controls=REPO/'implementation/warlock-client-capture-v3/qa/check-1791232839885645164/report.json';d=json.loads(controls.read_text());assert d['passed'] and d['compiledChecks']==2091 and d['namedScenarios']==5
for rel in ['native/client_plan.hpp','native/preview_png.hpp','native/preview_fd.hpp','native/preview_uri.hpp','native/preview_broker.hpp','qa/checks.cpp','spec/planes.qnt']:assert sha(source/rel)==d['inputs'][rel],rel
for p,h in json.loads((native/'qa/preflight.json').read_text())['inputs'].items():assert sha(p)==h,p
inventories={}
for root in [source,native,REPO/'implementation/warlock-client-projection-v1']:
 files={str(p.relative_to(root)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='component-manifest.json'}
 manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'componentCompilePassed':True,'boundedNativeChecksPassed':root==native,'nativeAcceptance':False,'fullReleaseAccepted':False,'files':files};path=root/'component-manifest.json';assert not path.exists();path.write_text(json.dumps(manifest,indent=2)+'\n');inventories[str(root.relative_to(REPO))]={'manifestSHA256':sha(path),'files':len(files)}
r={'passed':True,'scope':'Bounded isolated root-client source prototype, selected pure source-kind controls and native73; no eligible production capture, whole GUI or full release acceptance','components':inventories,'sourceBuildReport':build['pluginBuildReport'],'nativeReport':str(reportPath),'nativeChecks':73,'compiledControls':2091,'selectedQuintScenarios':5,'coupledStates':507,'previewEligible':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'nextWorkplan':str(OUT/'WORKPLAN.md')};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
