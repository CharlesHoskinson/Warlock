import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_files(rows):
 for row in rows:
  p=REPO/row['path']
  if 'symlink' in row:assert p.is_symlink() and os.readlink(p)==row['symlink']
  else:assert sha(p)==row['sha256'],str(p)
parent=REPO/'implementation/elm-picker-current-recovery-held-v267/acceptance-manifest.json';assert sha(parent)=='b970f76dcf13307aacf740ac418dbee3f0f852455f1b94a6cc7031941f35492d';ancestor=json.loads(parent.read_text());assert ancestor['passed'];verify_files(ancestor['files']);pair=ancestor['nativePair']
failures=REPO/'implementation/elm-gui-bounds-failure-v273/failure-manifest.json';assert sha(failures)=='d72a3fe4afa983ab8aa6cccdeb079b149f884d8ba35d23bd041c984fbb4bfa2e';verify_files(json.loads(failures.read_text())['files'])
profile_root=REPO/'implementation/elm-gui-bounds-native-v275';plan=json.loads((profile_root/'profiles.json').read_text())['profiles'];assert len(plan)==22
reports=[];policies=[];checks=0;pixels=0
paths=sorted((profile_root/'qa').glob('native-*/report.json'));assert len(paths)==3
for p in paths:
 r=json.loads(p.read_text());assert r['passed'] and r['cleanupPassed'] and not r.get('profileCleanupErrors') and not r.get('finalCleanupErrors')
 assert all(c['passed'] for c in r['checks'])
 cleanup=r['cleanup'];assert cleanup['runtimeGone'] and not any(cleanup.get(k) for k in ('cleanupErrors','unexpectedInnerDescendants','remainingDescendants'))
 assert r['pluginMaps']['files'][pair['plugin']['path']]==pair['plugin']['sha256']
 for name,digest in r['inputs'].items():assert sha(name)==digest,name
 for name,digest in r['artifacts'].items():assert sha(p.parent/name)==digest,name
 counts=len(r['checks']);checks+=counts
 actualpixels=sum(c['name'].endswith(':GUIactualSerialRGBPixels') for c in r['checks']);pixels+=actualpixels
 policies+=r['guiProfilePolicies'];reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':True,'checks':counts,'profiles':len(r['guiProfilePolicies']),'actualSerialRGBPixelChecks':actualpixels,'cleanupPassed':True})
assert sorted(p['id'] for p in policies)==sorted(p['id'] for p in plan)
assert [r['profiles'] for r in reports]==[14,6,2]
assert pixels==2*sum(p['expectedGUIMAX'] for p in policies)
files=[]
for name in ['elm-gui-bounds-contract-v268',*[f'elm-gui-bounds-native-v{v}' for v in range(269,273)],'elm-gui-bounds-failure-v273','elm-responsive-bar-gui-v274','elm-gui-bounds-native-v275',ROOT.name]:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  if p==ROOT/'acceptance-manifest.json':continue
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if p.is_symlink():row['symlink']=os.readlink(p)
  elif p.is_file():row.update(sha256=sha(p),size=st.st_size)
  elif p.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(p))
  files.append(row)
build=next((REPO/'implementation/elm-responsive-bar-gui-v274/qa').glob('build-*/report.json'));built=json.loads(build.read_text());assert built['passed']
r={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':True,'acceptedGuiBoundsProfileCount':22,'acceptedGuiBoundsNativeCheckCount':checks,'acceptedSerialRGBPixelCheckCount':pixels,'currentGuiGeneralRegressionAccepted':False,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'standardPortalAccessibilityBusAccepted':False,'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'parentNativeGuiCheckCount':473,'parentScopedRecoveryCheckCount':40,'parentCountsAreAncestryOnly':True,'failureManifest':str(failures.relative_to(REPO)),'failureManifestSHA256':sha(failures),'nativePair':pair,'guiBuild':{'path':str(build.relative_to(REPO)),'sha256':sha(build),'binarySHA256':built['binarySHA256']},'reports':reports,'guiProfilePolicies':policies,'files':files,'scope':'Actual274 Elm GUI physical-input/Max/Restore or disabled/noeffect/native configureACK+serialRGB all22 unchanged bounds profiles on205206AQ155. Controlled no-service-activation bus only; current fullmenu/focus/recovery/general GUI regression, real toolkits/portal/ATIME/hardware/fullroadmap release remain separate.'}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':True,'profiles':22,'checks':checks,'pixels':pixels,'files':len(files),'manifestSHA256':sha(ROOT/'acceptance-manifest.json')}))
