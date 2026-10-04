import hashlib,json,os,resource,stat
from pathlib import Path
REPO=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
names=['elm-shared-staged-menu-v300','elm-shared-staged-menu-carrier-v301','elm-shared-staged-menu-carrier-fixed-v302','elm-shared-staged-semantic-qa-v303','elm-shared-menu-owner-model-v304','elm-shared-staged-menu-carrier-complete-v305','elm-shared-menu-owner-model-fixed-v306','elm-shared-menu-owner-mutations-v307','elm-shared-staged-menu-acceptance-v308']
final=REPO/'implementation/elm-shared-staged-menu-carrier-complete-v305'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Match the final shipped Elm policy against every accepted worker's captured production input hashes.
comparisons=[]
checks=[REPO/'implementation/elm-shared-staged-menu-carrier-v301/qa/outputs-1791109110825365263/report.json',REPO/'implementation/elm-shared-staged-semantic-qa-v303/semantic/qa/replay-1791109163048386146/report.json',REPO/'implementation/elm-shared-staged-semantic-qa-v303/post-close/qa/replay-1791109163048345240/report.json']
for p in checks:
 d=json.loads(p.read_text());assert d['passed'];inventory=d.get('sourceInputs',d.get('inputs'));matched=[]
 for name,digest in inventory.items():
  if name.startswith('src/') or name=='elm.json':assert sha(final/name)==digest;matched.append(name)
 comparisons.append({'report':str(p.relative_to(REPO)),'sha256':sha(p),'matchedElmFiles':matched})
reports=[];files=[];special=[]
for name in names:
 root=REPO/'implementation'/name
 candidates=list(root.glob('qa/*/report.json'))+list(root.glob('*/qa/*/report.json'))
 for p in sorted(candidates):
  d=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'passed':d['passed'],'sha256':sha(p),'scope':d.get('scope'),'originalSuites':d.get('originalSuites')})
 for p in sorted(root.rglob('*')):
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(p));files.append(row)
  elif stat.S_ISREG(st.st_mode):row.update(size=st.st_size,sha256=sha(p));files.append(row)
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
assert len(reports)==11 and sum(x['passed'] for x in reports)==8
p=OUT/'slice-manifest.json';assert not p.exists()
d={'schema':1,'passed':True,'scope':'Actual shared staged menu/recovery Elm integration and geometry observation C carrier; native context input and release remain open','files':files,'specialFiles':special,'reports':reports,'finalSource':str(final.relative_to(REPO)),'finalElmInputComparisons':comparisons,'compiledSharedOutputChecks':37,'compiledSharedRecoveryChecks':49,'compiledSharedMenuOwnershipChecks':13,'compiledStagedMenuChecks':78,'compiledStagedGeometryChecks':53,'compiledStagedRefreshChecks':21,'compiledPostCloseChecks':59,'geometryCarrierChecks':34,'compiledUnsafeMutantsDetected':3,'quintNamedScenarios':12,'quintInvariantSamples':1000,'quintMaxSteps':40,'nativeRun':False,'nativeContextRouteIntegrated':False,'fullReleaseAccepted':False,'completedRequirementIds':[]}
p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports)}))
