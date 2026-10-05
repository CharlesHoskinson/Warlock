"""Freeze exact owned implementation and bounded evidence; no release promotion."""
import hashlib,json,pathlib
ROOT=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
OUT=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
components=['warlock-client-source-revisions-v1','warlock-client-tree-checks-v1','warlock-client-source-native-v1']
for name in components:
 base=ROOT/'implementation'/name;files={}
 for p in sorted(base.rglob('*')):
  if not p.is_file() or p.is_symlink() or p.name=='component-manifest.json':continue
  if '__pycache__' in p.parts:continue
  files[str(p.relative_to(base))]={'sha256':sha(p),'size':p.stat().st_size}
 manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'boundedRootNativeChecksPassed':name=='warlock-client-source-native-v1','files':files}
 target=base/'component-manifest.json';assert not target.exists();target.write_text(json.dumps(manifest,indent=2)+'\n')
paths=[ROOT/'implementation/warlock-core-surface-revision-v2/build-1791234190898766722/report.json',ROOT/'implementation/warlock-client-source-revisions-v1/qa/build-1791234326683052589/report.json',ROOT/'implementation/warlock-client-tree-checks-v1/qa/check-1791234574812309058/report.json',ROOT/'implementation/warlock-client-source-native-v1/qa/native-1791234649244421021/report.json']
for p in paths:assert json.loads(p.read_text())['passed']
native=json.loads(paths[-1].read_text());assert len(native['checks'])==73 and all(row['passed'] for row in native['checks']) and native['cleanupPassed'];assert len(native['ownedExitCodes'])==7 and all(row['exitCode']==0 for row in native['ownedExitCodes'])
report={'schema':1,'nativeAcceptance':False,'fullReleaseAccepted':False,'boundedRootRegressionPassed':True,'nativeChildTreeQualified':False,'mainDesktopActivated':False,'evidence':{str(p.relative_to(ROOT)):sha(p) for p in paths},'components':{name:sha(ROOT/'implementation'/name/'component-manifest.json') for name in ['warlock-core-surface-revision-v1','warlock-core-surface-revision-v2',*components]},'remainingWorkplanSHA256':sha(OUT/'WORKPLAN.md'),'scope':'Applied-state native API and bounded tree revision snapshot compiled; 65 CPU controls/9 named Quint/300 samples/21 traces508 states; retained native73 root pixel/context/FD regression on exact new tuple. Real child-only qualification and production integration remain open.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
