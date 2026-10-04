import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent=REPO/'implementation/elm-unknown-reconciliation-reviewed-v582/qa/slice-manifest.json';assert sha(parent)=='c990deed11a69a543a7a1e6cd7807842bd0f9e037b6c09856e6ec06828c96ef3'
files=[];links=[];components=[];native=None
for number in range(583,587):
 directory=next((REPO/'implementation').glob('*v'+str(number)))
 manifest=directory/'component-manifest.json'
 if manifest.exists():
  j=json.loads(manifest.read_text());assert j['sourceHeld']
  rows=j['files'];rows=rows.items() if isinstance(rows,dict) else [(row['path'],row['sha256']) for row in rows]
  for rel,digest in rows:assert sha(directory/rel)==digest,(number,rel)
  components.append({'path':str(manifest.relative_to(REPO)),'sha256':sha(manifest)})
  if number==583:
   assert sha(manifest)=='2b59e922edad80af9eb7c0ea6c026e3dd40f7421e158ad7230627c14350e6398'
   report=json.loads((directory/'qa/report.json').read_text());assert report['passed'] and len(report['checks'])==44 and all(c['passed'] for c in report['checks'])
   assert sha(REPO/'docs/elm-roadmap/delivery/budgets.json')==report['currentBudgetsSHA256']
  if number==584:
   report=json.loads(Path(j['report']).read_text());assert report['passed'] and len(report['checks'])==11 and all(c['passed'] for c in report['checks']) and sha(j['report'])==j['reportSHA256']
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if number==586 and p.name=='report.json' and p.parent.name.startswith('native-'):
   j=json.loads(p.read_text());assert j['passed'] and len(j['checks'])==25 and all(c['passed'] for c in j['checks']) and j['cleanupPassed'] and not j['mainDesktopActions'] and not j['nativeAcceptance']
   for rel,digest in j['artifacts'].items():assert sha(p.parent/rel)==digest
   native={'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':25,'cleanupPassed':True,'pair':j['pair']}
assert native is not None and len(components)==2
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
r={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':'implementation/elm-binding-registration-query-v579','nativeRegistrationQueryAccepted':True,'nativeRegistrationChecks':25,'nativeCampaign':native,'nativeAcceptance':False,'durableReconciliationImplemented':False,'guiCandidateQualificationComplete':False,'budgetStructuralChecks':44,'performanceAccepted':False,'recoveryPresentationCompiledChecks':11,'recoveryPresentationImplemented':False,'fullReleaseAccepted':False,'completedRequirementIds':[],'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'adoptedComponents':components,'files':files,'symlinks':links}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(p)}))
