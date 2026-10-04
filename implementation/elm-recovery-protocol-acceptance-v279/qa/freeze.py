"""Freeze only this cycle's source, failed attempts and bounded evidence."""
import hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
roots=[ROOT/'implementation'/n for n in ['elm-recovery-protocols-v275','elm-admission-protocols-v276','elm-recovery-protocol-model-v277','elm-recovery-protocol-model-v278','elm-recovery-protocol-acceptance-v279']]
manifest=OUT/'slice-manifest.json';assert not manifest.exists()
reports=[]
for root in roots:
 for p in root.glob('qa/*/report.json'):reports.append({'path':str(p.relative_to(ROOT)),**json.loads(p.read_text())})
assert [r['passed'] for r in reports].count(True)==5
assert [r['passed'] for r in reports].count(False)==1
files=[]
for root in roots:
 for p in sorted(root.rglob('*')):
  if p.is_file():files.append({'path':str(p.relative_to(ROOT)),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
data={'schema':1,'scope':'Typed durable legacy/geometry journal and compiled C admission; no native/Elm integration acceptance','passed':True,'files':files,'reports':[{'path':r['path'],'passed':r['passed'],'checks':len(r.get('checks',[])),'namedScenarios':r.get('namedScenarios')} for r in reports],'journalChecks':60,'inheritedJournalChecks':19,'namespaceChecks':42,'compiledAdmissionChecks':47,'quintNamedScenarios':9,'quintInvariantSamples':1000,'quintMaxSteps':40,'nativeRun':False,'geometryBrokerIntegrated':False,'elmGeometryRecoveryIntegrated':False,'completedRequirementIds':[]}
manifest.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'manifest':str(manifest),'files':len(files),'reports':len(reports),'passed':True}))
