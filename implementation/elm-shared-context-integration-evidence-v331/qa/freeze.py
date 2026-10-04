import hashlib,json,os,resource,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
final=REPO/'implementation/elm-shared-context-startup-order-v329'
build=final/'qa/build-1791111589989159244/report.json';d=json.loads(build.read_text());assert d['passed']
for name,digest in d['inputs'].items():assert sha(final/name)==digest
comparisons=[]
for name in ['elm-shared-menu-post-close-authority-v319/qa/outputs-1791111158633694731/report.json','elm-shared-context-semantic-v320/post-close/qa/replay-1791111187748274884/report.json','elm-shared-context-stable-popup-scope-v325/semantic/qa/replay-1791111367402468218/report.json']:
 p=REPO/'implementation'/name;d=json.loads(p.read_text());assert d['passed'];inventory=d.get('sourceInputs',d.get('inputs'));matched=[]
 for rel,digest in inventory.items():
  if rel.startswith('src/') or rel=='elm.json':assert sha(final/rel)==digest;matched.append(rel)
 comparisons.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'matchedElmFiles':matched})
names=json.loads((ROOT/'qa/roots.json').read_text())+[ROOT.name];files=[];special=[];reports=[]
for name in names:
 root=REPO/'implementation'/name
 for p in sorted(root.rglob('*')):
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(p));files.append(row)
  elif stat.S_ISREG(st.st_mode):
   row.update(size=st.st_size,sha256=sha(p));files.append(row)
   if p.name=='report.json':
    d=json.loads(p.read_text())
    if 'passed' in d:reports.append({'path':row['path'],'sha256':row['sha256'],'passed':d['passed'],'scope':d.get('scope'),'cleanupPassed':d.get('cleanupPassed')})
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
native=[r for r in reports if '/qa/native-' in r['path']]
assert len(native)==7 and all(not r['passed'] and r['cleanupPassed'] for r in native)
p=ROOT/'qa/slice-manifest.json';assert not p.exists()
p.write_text(json.dumps({'schema':1,'passed':True,'scope':'Frozen bounded shared-context implementation and failed native campaigns; no complete native-menu or release acceptance','files':files,'specialFiles':special,'reports':reports,'finalSource':str(final.relative_to(REPO)),'finalElmComparisons':comparisons,'sharedOutputChecks':37,'sharedRecoveryChecks':49,'sharedMenuChecks':23,'postCloseChecks':59,'adaptedStableMenuChecks':78,'geometryChecks':53,'refreshChecks':21,'nativeCampaigns':7,'nativeCampaignsPassed':0,'contextQuintNamed':12,'refreshQuintNamed':11,'samplesPerModel':1000,'maxSteps':40,'completedRequirementIds':[],'fullReleaseAccepted':False},indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports)}))
