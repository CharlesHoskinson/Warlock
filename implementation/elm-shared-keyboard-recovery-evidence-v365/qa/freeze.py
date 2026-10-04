import hashlib,json,os,resource,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=REPO/'implementation/elm-shared-keyboard-proof-acceptance-v358/qa/slice-manifest.json'
pd=json.loads(prior.read_text());assert pd['passed']
for row in pd['files']:
 p=REPO/row['path']
 if row.get('type')=='symlink':assert p.is_symlink() and os.readlink(p)==row['target']
 else:assert sha(p)==row['sha256'],str(p)
source=REPO/'implementation/elm-shared-keyboard-recovery-merge-v359'
build=source/'qa/build-1791119492743283927/report.json';b=json.loads(build.read_text());assert b['passed']
for rel,digest in b['inputs'].items():assert sha(source/rel)==digest,rel
comparisons=[]
for name in ['elm-shared-recovery-output-supersession-qa-v361/qa/outputs-1791119842526605333/report.json','elm-shared-keyboard-recovery-semantic-v363/semantic/qa/replay-1791120130989157956/report.json','elm-shared-keyboard-recovery-merge-v359/qa/local-unsent-1791119574468988321/report.json']:
 p=REPO/'implementation'/name;d=json.loads(p.read_text());assert d['passed'];matched=[]
 for rel,digest in d.get('sourceInputs',d.get('inputs')).items():
  if rel.startswith('src/') or rel=='elm.json':assert sha(source/rel)==digest,rel;matched.append(rel)
 comparisons.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'matchedElmFiles':matched})
files=[];special=[];reports=[]
for name in json.loads((ROOT/'qa/roots.json').read_text())+[ROOT.name]:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(p));files.append(row)
  elif stat.S_ISREG(st.st_mode):
   row.update(size=st.st_size,sha256=sha(p));files.append(row)
   if p.name=='report.json':
    d=json.loads(p.read_text())
    if 'passed' in d:reports.append({'path':row['path'],'sha256':row['sha256'],'passed':d['passed'],'cleanupPassed':d.get('cleanupPassed'),'scope':d.get('scope')})
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
native=[r for r in reports if '/qa/native-' in r['path']];assert len(native)==3 and sum(r['passed'] for r in native)==1 and all(r['cleanupPassed'] for r in native)
p=ROOT/'qa/slice-manifest.json';assert not p.exists()
p.write_text(json.dumps({'schema':1,'passed':True,'scope':'Frozen combined-source CPU qualification and held native attempts; strict native acceptance remains failed','files':files,'specialFiles':special,'reports':reports,'finalSource':str(source.relative_to(REPO)),'priorPacket':str(prior.relative_to(REPO)),'priorPacketSHA256':sha(prior),'finalElmComparisons':comparisons,'nativeCampaigns':3,'nativeCampaignsPassed':1,'strictNativeAccepted':False,'sharedOutputChecks':37,'sharedRecoveryChecks':49,'sharedMenuChecks':23,'adaptedStableMenuChecks':79,'geometryChecks':53,'refreshChecks':21,'localUnsentChecks':65,'browserWireChecks':2,'contextGuardChecks':76,'keyChecks':20,'geometryCarrierChecks':34,'deadlineControlChecks':4,'atActivationQualified':False,'completedRequirementIds':[],'fullReleaseAccepted':False},indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports)}))
