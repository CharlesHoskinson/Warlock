import datetime,hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports={}
for pattern in ['checks-*','model-*']:
 p=sorted((ROOT/'qa').glob(pattern+'/report.json'))[-1];v=json.loads(p.read_text());assert v['passed']
 if 'inputs' in v:assert all(sha(ROOT/name)==digest for name,digest in v['inputs'].items())
 else:assert sha(ROOT/'spec/surfaces.qnt')==v['sourceSHA256']
 reports[str(p.relative_to(ROOT))]={'passed':True,'sha256':sha(p),'typedChecks':v.get('typedChecks'),'presentationChecks':v.get('presentationChecks'),'namedScenarios':v.get('namedScenarios'),'invariantSamples':v.get('invariantSamples')}
manifest={'passed':True,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Shared pure interaction controller/presentation renderer component; native barrier/order is planned contract, C/dual-view GUI not implemented','wholeFeatureAccepted':False,'completedRequirementIds':[],'reports':reports,'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(ROOT/'qa/slice-manifest.json')
