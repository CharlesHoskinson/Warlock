import hashlib,json,os,resource,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
final=REPO/'implementation/elm-shared-registration-shutdown-merge-v380';prior=REPO/'implementation/elm-shared-render-dismissal-accepted-v379/qa/slice-manifest.json'
build=final/'qa/build-1791121552616106038/report.json';b=json.loads(build.read_text());assert b['passed']
for rel,digest in b['inputs'].items():assert sha(final/rel)==digest,rel
for rel in ['native/shared-context.h','native/shared-context-test.c','native/shared-host.c','assets/context.js','src/Surface.elm']:
 assert sha(final/rel)==sha(REPO/'implementation/elm-shared-pending-render-dismissal-v371'/rel),rel
comparisons=[]
for name in ['elm-shared-registration-output-qa-v382/qa/outputs-1791121715787434221/report.json','elm-shared-registration-semantic-qa-v383/semantic/qa/replay-1791121715803307333/report.json']:
 p=REPO/'implementation'/name;d=json.loads(p.read_text());assert d['passed'];matched=[]
 for rel,digest in d.get('sourceInputs',d.get('inputs')).items():
  if rel.startswith('src/') or rel=='elm.json':assert sha(final/rel)==digest,rel;matched.append(rel)
 comparisons.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'matchedElmFiles':matched})
model=next((REPO/'implementation/elm-shared-registration-recovery-model-v386/qa').glob('model-*/report.json'));md=json.loads(model.read_text());assert md['passed'] and md['namedScenarios']==8 and md['unsafeCertificate']['detected']
assert 'QNT508' in (model.parent/'unsafe.stdout').read_text() and 'wrongCertificateTest failed' in (model.parent/'unsafe.stdout').read_text()
files=[];reports=[];special=[]
for name in ['elm-shared-registration-shutdown-merge-v380','elm-shared-registration-shutdown-native-v381','elm-shared-registration-output-qa-v382','elm-shared-registration-semantic-qa-v383','elm-shared-registration-target-retirement-v384','elm-shared-registration-recovery-model-v385','elm-shared-registration-recovery-model-v386',ROOT.name]:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(p));files.append(row)
  elif stat.S_ISREG(st.st_mode):
   row.update(size=st.st_size,sha256=sha(p));files.append(row)
   if p.name=='report.json':
    d=json.loads(p.read_text())
    if 'passed' in d:reports.append({'path':row['path'],'sha256':row['sha256'],'passed':d['passed'],'scope':d.get('scope'),'cleanupPassed':d.get('cleanupPassed'),'checks':len(d['checks']) if isinstance(d.get('checks'),list) else d.get('checks')})
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
native=[r for r in reports if '/qa/native-' in r['path']];assert len(native)==2 and all(r['passed'] and r['cleanupPassed'] for r in native) and sorted(r['checks'] for r in native)==[48,49]
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps({'schema':1,'passed':True,'scope':'Bounded combined registration/shutdown/menu target retirement; original native faults/full release pending','files':files,'specialFiles':special,'reports':reports,'finalSource':str(final.relative_to(REPO)),'priorPacket':str(prior.relative_to(REPO)),'priorPacketSHA256':sha(prior),'finalElmComparisons':comparisons,'nativeCampaigns':2,'nativeCampaignsPassed':2,'productionNativeChecks':49,'targetRetirementChecks':48,'registrationChecks':25,'operationDeferredChecks':65,'brokerChecks':43,'shutdownChecks':10,'sharedOutputChecks':37,'sharedRecoveryChecks':49,'sharedMenuChecks':23,'adaptedMenuChecks':79,'geometryChecks':53,'refreshChecks':21,'contextGuardChecks':90,'keyChecks':20,'geometryCarrierChecks':34,'quintNamed':8,'invariantSamples':1000,'maxSteps':40,'unsafeCertificateDetected':True,'originalNativeFaultAccepted':False,'completedRequirementIds':[],'fullReleaseAccepted':False},indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports)}))
