import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent=REPO/'implementation/elm-responsive-focus-held-v285/acceptance-manifest.json';assert sha(parent)=='e97d5682b47b02ee0bbf7a4b0fe437f14639e63e01741a3311c6387fbe999e6e';pair=json.loads(parent.read_text())['nativePair']
reports=[]
for name,passed in [('elm-responsive-reconnect-v293',True),('elm-responsive-geometry-v288',True)]:
 p=next((REPO/'implementation'/name/'qa').glob('native-*/report.json'));m=json.loads(p.read_text());assert m['passed']==passed and m['cleanupPassed'] and not m.get('inputChanges',[]) and m['pair']==pair
 for path,digest in m['inputs'].items():assert sha(path)==digest
 for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
 reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':passed,'checks':len(m['checks']),'cleanupPassed':True})
 if passed:
  assert all(c['passed'] for c in m['checks']) and len(m['checks'])==(57 if name.endswith('v293') else 161) and m.get('privateHost',m.get('cleanup',{}))['runtimeGone'] and not m.get('privateHost',m.get('cleanup',{})).get('unexpectedInnerDescendants')
  accepted=sum(r['checks'] for r in reports)
failure=REPO/'implementation/elm-responsive-regression-failure-v295/failure-manifest.json';assert sha(failure)=='1245ffd90baa6b97dcb4be0bfb9a2d682850159a48e609e01377cbc7c818d039'
for entry in json.loads(failure.read_text())['files']:
 p=REPO/entry['path']
 if 'symlink' in entry:assert p.is_symlink() and os.readlink(p)==entry['symlink']
 else:assert sha(p)==entry['sha256']
files=[]
for name in ['elm-responsive-capability-v283','elm-responsive-focus-v284','elm-responsive-focus-held-v285','elm-responsive-geometry-v286','elm-responsive-reconnect-v287','elm-responsive-geometry-v288','elm-responsive-regression-held-v289','elm-responsive-regression-failure-v290','elm-responsive-source-held-v291','elm-responsive-broker-fixture-v292','elm-responsive-reconnect-v293','elm-responsive-regression-failure-v295',ROOT.name]:
 for path in sorted((REPO/'implementation'/name).rglob('*')):
  if path==ROOT/'acceptance-manifest.json':continue
  st=path.lstat();row={'path':str(path.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if path.is_symlink():row['symlink']=os.readlink(path)
  elif path.is_file():row.update(sha256=sha(path),size=st.st_size)
  elif path.is_dir():continue
  else:raise RuntimeError('Unexpected special file '+str(path))
  files.append(row)
assert accepted==218
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':True,'acceptedGuiBoundsProfileCount':22,'parentGuiBoundsNativeCheckCount':893,'acceptedCurrentGuiGeneralNativeCheckCount':473,'acceptedCurrentGuiGeometryReconnectNativeCheckCount':accepted,'currentGuiGeneralRegressionAccepted':True,'currentRendererRecoveryAccepted':False,'pendingUnknownReconciliationAccepted':False,'serverOldGrantRetirementAccepted':False,'fullRoadmapAccepted':False,'fullReleaseAccepted':False,'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'nativePair':pair,'reports':reports,'files':files,'fixtureVariants':['unchanged adapter255 archived231 capture for capability/focus/geometry','291/292 actual278 capture for reconnect; adapter source bytes identical'], 'scope':'Actual CSS-corrected278 Core205/plugin206/AQ155 source tuple: original fullmenu89/heldcapability83/heldfocus83/nativegeometry161/reconnect57=473 all PASS and normalcleanup; actual22 bounds893 parent accepted separately. Source-bound fixture variants above retain identical production adapter bytes; this reproduces original scoped261 coverage, not original137 fulljourney, broad Unknown/server retirement/currentrenderer40/real toolkits/hardwareATIME/budgets/user/fullroadmap/release acceptance.'}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'acceptedCurrentGuiGeneralNativeCheckCount':473,'manifestSHA256':sha(ROOT/'acceptance-manifest.json')}))
