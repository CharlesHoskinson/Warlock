import hashlib,json,os,resource,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
final=REPO/'implementation/elm-shared-keyboard-menu-proof-v353'
build=final/'qa/build-1791118602700539676/report.json';d=json.loads(build.read_text());assert d['passed']
for rel,digest in d['inputs'].items():assert sha(final/rel)==digest,rel
comparisons=[]
for name in ['elm-shared-keyboard-menu-proof-v353/qa/outputs-1791118996230018059/report.json','elm-shared-close-navigation-semantic-v356/semantic/qa/replay-1791118873592071967/report.json']:
 p=REPO/'implementation'/name;d=json.loads(p.read_text());assert d['passed'];matched=[]
 for rel,digest in d.get('sourceInputs',d.get('inputs')).items():
  if rel.startswith('src/') or rel=='elm.json':assert sha(final/rel)==digest,rel;matched.append(rel)
 comparisons.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'matchedElmFiles':matched})
model=next((REPO/'implementation/elm-shared-keyboard-click-model-v357/qa').glob('model-*/report.json'));d=json.loads(model.read_text());assert d['passed'] and d['unsafeBrowserFallback']['detected']
assert 'QNT508' in (model.parent/'unsafe.stdout').read_text() and 'implicitClickCannotBypassTest failed' in (model.parent/'unsafe.stdout').read_text()
names=json.loads((ROOT/'qa/roots.json').read_text())+[ROOT.name];files=[];special=[];reports=[]
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(p));files.append(row)
  elif stat.S_ISREG(st.st_mode):
   row.update(size=st.st_size,sha256=sha(p));files.append(row)
   if p.name=='report.json':
    d=json.loads(p.read_text())
    if 'passed' in d:reports.append({'path':row['path'],'sha256':row['sha256'],'passed':d['passed'],'scope':d.get('scope'),'cleanupPassed':d.get('cleanupPassed'),'checks':len(d['checks']) if isinstance(d.get('checks'),list) else d.get('checks')})
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
native=[r for r in reports if '/qa/native-' in r['path']]
assert len(native)==6 and sum(r['passed'] for r in native)==4 and all(r['cleanupPassed'] for r in native)
latest=REPO/'implementation/elm-shared-menu-keyboard-fast-proof-v355/qa/native-1791118872482223100/report.json';d=json.loads(latest.read_text());assert d['passed'] and len(d['checks'])==48 and d['cleanupPassed']
p=ROOT/'qa/slice-manifest.json';assert not p.exists()
p.write_text(json.dumps({'schema':1,'passed':True,'scope':'Bounded native keyboard menu proof, Close and implicit-click suppression; full desktop/AT/release pending','files':files,'specialFiles':special,'reports':reports,'finalSource':str(final.relative_to(REPO)),'finalElmComparisons':comparisons,'nativeCampaigns':6,'nativeCampaignsPassed':4,'latestNativeReport':str(latest.relative_to(REPO)),'latestNativeReportSHA256':sha(latest),'tightenedNormalNativeChecks':48,'tightenedFastNativeChecks':48,'sharedOutputChecks':37,'sharedRecoveryChecks':49,'sharedMenuChecks':23,'adaptedStableMenuChecks':79,'geometryChecks':53,'refreshChecks':21,'contextGuardChecks':76,'keyChecks':20,'geometryCarrierChecks':34,'quintNamed':15,'invariantSamples':1000,'maxSteps':40,'unsafeBrowserFallbackModelDetected':True,'atActivationQualified':False,'completedRequirementIds':[],'fullReleaseAccepted':False},indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports)}))
