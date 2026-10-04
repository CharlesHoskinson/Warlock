import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent=REPO/'implementation/elm-native-retirement-graphics-reviewed-v598/qa/slice-manifest.json'
assert sha(parent)=='cb1bb3dc2b35e6278d83a64137342ca78f8655eed917537804dbf7c9b67ec36f'
components=[];files=[];links=[]
for number in [599,600,601,602,603,604,605,606,608,610]:
 directory=next((REPO/'implementation').glob('*v'+str(number)))
 manifest=directory/'component-manifest.json'
 if manifest.exists():
  data=json.loads(manifest.read_text());assert data['sourceHeld']
  inventory=data['files'];rows=list(inventory.items()) if isinstance(inventory,dict) else [(r['path'],r) for r in inventory]
  for name,row in rows:
   digest=row['sha256'] if isinstance(row,dict) else row
   assert sha(directory/name)==digest,(number,name)
   if isinstance(row,dict):assert (directory/name).stat().st_size==row['size']
  components.append({'path':str(manifest.relative_to(REPO)),'sha256':sha(manifest)})
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if p.is_file():files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
source=REPO/'implementation/elm-durable-reservation-release-v608'
reports=list((source/'qa').glob('tests-*/report.json'));assert len(reports)==1
report=json.loads(reports[0].read_text());assert report['passed'] and report['assertions']==248 and all(c['passed'] for c in report['checks'])
for name,digest in report['sourceSHA256'].items():assert sha(source/name)==digest,name
baseline=REPO/'implementation/elm-stable-surface-publication-v521'
for p in (source/'adapter').glob('*.py'):
 if p.name=='retirement_ledger.py':continue
 original=REPO/'implementation/elm-retirement-proof-endpoint-v599/adapter/grant_endpoint.py' if p.name=='grant_endpoint.py' else baseline/'adapter'/p.name
 assert sha(p)==sha(original),p.name
for p in (source/'native').glob('*'):assert sha(p)==sha(baseline/'native'/p.name),p.name
control=next((REPO/'implementation/elm-durable-release-mutations-v610/qa').glob('controls-*/report.json'))
mutants=json.loads(control.read_text());assert mutants['passed'] and len(mutants['mutations'])==6
assert mutants['sourceSHA256']==sha(source/'adapter/retirement_ledger.py')
assert all(m['syntaxValid'] and m['detected'] and m['behavioralCounterexample'] for m in mutants['mutations'])
assert len(components)==4
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':str(source.relative_to(REPO)),
 'durableReservationLedgerImplemented':True,'durableReservationCPUChecks':248,'actualPythonMutationsDetected':6,
 'reconciliationElmCompiledChecks':162,'reconciliationElmMutationsDetected':5,'retirementProofCPUChecks':625,
 'productionWired':False,'durableReconciliationNativeAccepted':False,'powerLossDurabilityAccepted':False,
 'nativeAcceptance':False,'fullReleaseAccepted':False,'completedRequirementIds':[],
 'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),
 'adoptedComponents':components,'storageReport':str(reports[0].relative_to(REPO)),'mutationReport':str(control.relative_to(REPO)),
 'files':files,'symlinks':links}
dest=ROOT/'qa/slice-manifest.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'symlinks':len(links),'manifestSHA256':sha(dest)}))
