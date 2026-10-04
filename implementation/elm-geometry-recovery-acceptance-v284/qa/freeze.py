"""Freeze this cycle including compiler failure and unresolved cold-restart repro."""
import hashlib,json,resource
from pathlib import Path
REPO=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
roots=[REPO/'implementation'/n for n in ['elm-geometry-recovery-broker-v280','elm-geometry-recovery-ui-v281','elm-geometry-recovery-ui-fixed-v282','elm-unresolved-recovery-repro-v283','elm-geometry-recovery-acceptance-v284']]
reports=[]
for root in roots:
 for p in root.glob('qa/*/report.json'):
  d=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'passed':d['passed'],'checks':len(d.get('checks',[])),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert len(reports)==5 and sum(r['passed'] for r in reports)==3
files=[]
for root in roots:
 for p in sorted(root.rglob('*')):
  if p.is_file():files.append({'path':str(p.relative_to(REPO)),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
p=OUT/'slice-manifest.json';assert not p.exists()
d={'schema':1,'scope':'Broker journal and compiled shared Elm recovery progress; cold multi-Unknown preservation failed, integrated native release open','componentChecksPassed':True,'files':files,'reports':reports,'brokerRecoveryChecks':193,'framingChecks':1011,'inheritedCompiledElmChecks':[78,53,21],'compiledElmRecoveryChecks':34,'geometryBrokerJournalIntegrated':True,'compiledElmGeometryRecovery':True,'multiUnknownColdRecoveryAccepted':False,'integratedNativeHostAccepted':False,'nativeRun':False,'completedRequirementIds':[]}
p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'manifest':str(p),'files':len(files),'reports':len(reports),'multiUnknownAccepted':False}))
