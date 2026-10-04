import hashlib,json,pathlib,resource,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
PARENT=ROOT.parent/'elm-reconciliation-startup-order-v626'
FRONTEND=ROOT.parent/'elm-reconciliation-accepted-read-v619'
DELIVERY=ROOT.parent/'elm-release-delivery-attestation-v624'
def row(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
changed=['adapter/reconciliation.py','adapter/recovery_store.py'];pins={}
for directory in ['src','native','adapter','assets']:
    for p in (PARENT/directory).rglob('*'):
        if not p.is_file():continue
        name=str(p.relative_to(PARENT))
        if name in changed:continue
        pins[name]=row(p);assert row(ROOT/name)==pins[name],name
assert row(ROOT/'adapter/delivery_ledger.py')==row(DELIVERY/'adapter/delivery_ledger.py')
report=ROOT/'qa/integration-1791152781571263529/report.json';r=json.loads(report.read_text());assert r['passed']
for name,digest in r['sourceSHA256'].items():assert row(ROOT/name)['sha256']==digest,name
for name,digest in r['compiled619SourceSHA256'].items():
    assert row(FRONTEND/'src'/name)['sha256']==digest,name
    assert row(report.parent/'inputs/src'/name)['sha256']==digest,name
public=ROOT/'qa/tests-1791152811827803535/report.json';p=json.loads(public.read_text());assert p['passed']
for name,digest in p['sourceSHA256'].items():assert row(public.parent/'inputs/src'/name)['sha256']==digest,name
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
files={str(p.relative_to(ROOT)):row(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=manifest}
value={'schema':1,'component':'elm-recovery-delivery-integration-v630','parent':str(PARENT),'unchangedProductionFiles':pins,'changedProductionFiles':changed,'addedDeliveryHelper':row(ROOT/'adapter/delivery_ledger.py'),'integrationReport':str(report),'integrationChecks':r['assertions'],'public619Report':str(public),'public619Checks':len(p['checks']),'nativeAcceptance':False,'completeGUIBuild':False,'files':files}
manifest.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
for name,expected in files.items():assert row(ROOT/name)==expected,name
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'unchangedProductionFiles':len(pins),'integrationChecks':r['assertions'],'public619Checks':len(p['checks'])}))
