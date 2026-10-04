import ast,hashlib,json,os,resource,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=REPO/'implementation/elm-shared-registration-shutdown-accepted-v387/qa/slice-manifest.json';pd=json.loads(prior.read_text());assert pd['passed']
for row in pd['files']:
 p=REPO/row['path']
 if row.get('type')=='symlink':assert os.readlink(p)==row['target']
 else:assert sha(p)==row['sha256'],row['path']
fixture=REPO/'implementation/elm-shared-receipt-eof-fixture-v391'
assert json.loads((fixture/'algorithm-review.json').read_text())['passed']
old=REPO/'implementation/elm-shared-receipt-eof-fixture-v390'
assert sha(old/'receipt/qa/wrapper.py')==sha(fixture/'receipt/qa/wrapper.py')
def nodes(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(p.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
a=nodes(old/'relay/qa/relay.py');b=nodes(fixture/'relay/qa/relay.py');assert a['pump']==b['pump']
for rel,expected in [('receipt/qa/hold-1791122377802384658/report.json',45),('receipt/qa/selector-1791122377831233779/report.json',52),('relay/qa/test-1791122377803023729/report.json',19),('relay/qa/edges-1791122377799503999/report.json',7),('relay/qa/deadline-1791122377797560941/report.json',7)]:
 d=json.loads((old/rel).read_text());assert d['passed'] and len(d['checks'])==expected
profile=fixture/'profile-1791122564738394175/report.json';d=json.loads(profile.read_text());assert d['passed'] and len(d['checks'])==9
names=['elm-shared-receipt-eof-fixture-v388','elm-shared-receipt-eof-fixture-v389','elm-shared-receipt-eof-fixture-v390','elm-shared-receipt-eof-fixture-v391','elm-shared-relay-baseline-native-v392','elm-shared-relay-reconnect-native-v393',ROOT.name];files=[];reports=[];special=[]
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
native=[r for r in reports if '/qa/native-' in r['path']];assert len(native)==2 and all(r['passed'] and r['cleanupPassed'] for r in native) and sorted(r['checks'] for r in native)==[50,57]
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps({'schema':1,'passed':True,'scope':'Current schema5 QA selector/relay closure and bounded native normal EOF/reconnect; full original08/09/10 pending','files':files,'specialFiles':special,'reports':reports,'finalProductionSource':'implementation/elm-shared-registration-shutdown-merge-v380','finalFixture':str(fixture.relative_to(REPO)),'priorPacket':str(prior.relative_to(REPO)),'priorPacketSHA256':sha(prior),'nativeCampaigns':2,'nativeCampaignsPassed':2,'relayBaselineChecks':50,'reconnectSubsetChecks':57,'holdChecks':45,'selectorChecks':52,'relayChecks':19,'edgeChecks':7,'deadlineChecks':7,'profileChecks':9,'holdPumpAlgorithmsUnchanged':True,'originalGeometry08Accepted':False,'originalGeometry09Accepted':False,'originalGeometry10Accepted':False,'completedRequirementIds':[],'fullReleaseAccepted':False},indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports)}))
