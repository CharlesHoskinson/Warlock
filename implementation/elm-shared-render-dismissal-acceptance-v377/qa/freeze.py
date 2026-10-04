import hashlib,json,os,resource,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
final=REPO/'implementation/elm-shared-pending-render-dismissal-v371'
build=final/'qa/build-1791120875110960581/report.json';b=json.loads(build.read_text());assert b['passed']
for rel,digest in b['inputs'].items():assert sha(final/rel)==digest,rel
fixture=REPO/'implementation/elm-shared-pending-render-dismissal-fixture-v372';recovery=REPO/'implementation/elm-shared-render-dismissal-recovery-qa-v378';changed=[]
for folder in ['src','native','assets','adapter']:
 for p in sorted((final/folder).rglob('*')):
  if p.is_file():
   rel=p.relative_to(final);assert sha(p)==sha(recovery/rel),str(rel)
   if sha(p)!=sha(fixture/rel):changed.append(str(rel))
assert changed==['assets/popup-adapter.js'],changed
for p in (REPO/'implementation/elm-shared-keyboard-recovery-merge-v359/src').glob('*.elm'):assert sha(p)==sha(final/'src'/p.name)
local=next((recovery/'qa').glob('local-unsent-*/report.json'));ld=json.loads(local.read_text());assert ld['passed']
model=next((REPO/'implementation/elm-shared-render-dismissal-model-v373/qa').glob('model-*/report.json'));md=json.loads(model.read_text());assert md['passed'] and md['namedScenarios']==21 and md['unsafeRenderReadiness']['detected'] and md['unsafeBrowserFallback']['detected']
assert 'QNT508' in (model.parent/'unsafe-render.stdout').read_text()
names=['elm-shared-menu-render-delay-fixture-v369','elm-shared-menu-render-delay-native-v370','elm-shared-pending-render-dismissal-v371','elm-shared-pending-render-dismissal-fixture-v372','elm-shared-render-dismissal-model-v373','elm-shared-pending-render-dismissal-native-v374','elm-shared-pending-render-production-native-v375','elm-shared-pending-render-enter-refusal-native-v376','elm-shared-render-dismissal-recovery-qa-v378',ROOT.name]
files=[];reports=[];special=[]
for name in names:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(p));files.append(row)
  elif stat.S_ISREG(st.st_mode):
   row.update(size=st.st_size,sha256=sha(p));files.append(row)
   if p.name=='report.json':
    d=json.loads(p.read_text())
    if 'passed' in d:reports.append({'path':row['path'],'sha256':row['sha256'],'passed':d['passed'],'scope':d.get('scope'),'cleanupPassed':d.get('cleanupPassed'),'checks':len(d['checks']) if isinstance(d.get('checks'),list) else d.get('checks')})
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
native=[r for r in reports if '/qa/native-' in r['path']];assert len(native)==4 and sum(r['passed'] for r in native)==3 and all(r['cleanupPassed'] for r in native)
assert sorted(r['checks'] for r in native if r['passed'])==[48,49,50]
prior=REPO/'implementation/elm-shared-navigation-diagnostic-evidence-v368/qa/slice-manifest.json'
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps({'schema':1,'passed':True,'scope':'Bounded native pending-render Escape cancellation and strict Enter refusal; full release pending','files':files,'specialFiles':special,'reports':reports,'finalSource':str(final.relative_to(REPO)),'priorPacket':str(prior.relative_to(REPO)),'priorPacketSHA256':sha(prior),'nativeCampaigns':4,'nativeCampaignsPassed':3,'productionNativeChecks':48,'controlledNativeChecks':49,'controlledEnterRefusalChecks':50,'contextGuardChecks':90,'keyChecks':20,'geometryCarrierChecks':34,'quintNamed':21,'invariantSamples':1000,'maxSteps':40,'unsafeControlsDetected':True,'finalRecoveryReport':str(local.relative_to(REPO)),'finalRecoveryReportSHA256':sha(local),'fixtureChangedFiles':changed,'unchangedElmSource':'implementation/elm-shared-keyboard-recovery-merge-v359','atActivationQualified':False,'completedRequirementIds':[],'fullReleaseAccepted':False},indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports)}))
