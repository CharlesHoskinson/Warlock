"""Freeze owned source/evidence, failed attempts and bounded acceptance claims."""
import hashlib,json,resource,stat,os
from pathlib import Path
REPO=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
names=['elm-multi-recovery-broker-v285','elm-multi-recovery-broker-fixed-v286','elm-multi-recovery-ui-v287','elm-multi-recovery-cold-v288','elm-multi-recovery-model-v289','elm-ledger-key-order-repro-v290','elm-multi-recovery-canonical-v291','elm-multi-recovery-acceptance-v292']
roots=[REPO/'implementation'/n for n in names]
reports=[]
for root in roots:
 for p in sorted(root.glob('qa/*/report.json')):
  d=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'passed':d['passed'],'checks':len(d.get('checks',[])),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'qualifiedInputClosure':not(root.name=='elm-multi-recovery-broker-v285' and p.parent.name.startswith('repro-'))})
assert len(reports)==16 and sum(r['passed'] for r in reports)==14
files=[];special=[]
for root in roots:
 for p in sorted(root.rglob('*')):
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid}
  if stat.S_ISLNK(st.st_mode):row.update(type='symlink',target=os.readlink(p));files.append(row)
  elif stat.S_ISREG(st.st_mode):row.update(size=st.st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());files.append(row)
  elif not stat.S_ISDIR(st.st_mode):special.append(row)
p=OUT/'slice-manifest.json';assert not p.exists()
d={'schema':1,'scope':'Bounded durable multi-intent broker and compiled Elm allocation recovery; live native admission handoff and release open','passed':True,'files':files,'specialFiles':special,'reports':reports,'finalSource':'implementation/elm-multi-recovery-canonical-v291','finalElm':'implementation/elm-multi-recovery-ui-v287','ledgerChecks':64,'brokerRecoveryChecks':219,'framingChecks':1011,'coldBrokerMigrationChecks':23,'originalColdReproductionChecks':4,'receiptOrderChecks':3,'compiledInheritedElmChecks':[78,53,21],'compiledElmRecoveryChecks':45,'quintNamedScenarios':9,'quintInvariantSamples':1000,'quintMaxSteps':40,'multiUnknownColdBrokerRecoveryAccepted':True,'nativeHostAdmissionIntegrated':False,'nativeRun':False,'fullReleaseAccepted':False,'completedRequirementIds':[]}
p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports),'nativeHostIntegrated':False}))
