import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
r=pathlib.Path(__file__).resolve().parents[1]
def row(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
report=json.loads((r/'qa/report.json').read_bytes());assert report['passed'] and report['assertions']==62
parent=r.parent/'elm-paged-history-storage-v647/component-manifest.json'
assert row(parent)['sha256']==report['parentManifestSHA256']
inputs={}
for path in ['elm-durable-reservation-release-v608/adapter/retirement_ledger.py','elm-release-delivery-attestation-v624/adapter/delivery_ledger.py','elm-recovery-delivery-integration-v630/adapter/reconciliation.py','elm-recovery-delivery-integration-v630/adapter/durable_ledger.py','elm-informational-history-drain-v642/src/ReconciliationTracking.elm','elm-paged-history-archive-v629/requirements.json','elm-paged-history-storage-v647/adapter/archive.py','elm-paged-history-storage-v647/spec/storage.qnt','elm-paged-history-storage-v647/spec/REFINEMENT.md','elm-paged-history-storage-v647/qa/tests-1791154696119822432/report.json','elm-paged-history-storage-v647/qa/model-1791154554659366036/report.json']:
 inputs[path]=row(r.parent/path)
manifest=r/'component-manifest.json';assert not manifest.exists()
files={str(p.relative_to(r)):row(p) for p in sorted(r.rglob('*')) if p.is_file()}
m={'schema':1,'component':r.name,'scope':'independent storage-only review and proposed V7 architecture, no semantic integration','verdict':'confirmed bounded647 storage scope; V7 changes required','parentManifestSHA256':row(parent)['sha256'],'reviewedInputs':inputs,'newAssertions':62,'historical362NotRerun':True,'nativeAcceptance':False,'ledgerIntegrated':False,'S15Accepted':False,'powerLossQualified':False,'files':files}
manifest.write_text(json.dumps(m,sort_keys=True,indent=2)+'\n')
for path,v in files.items():assert row(r/path)==v
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'newAssertions':62}))
