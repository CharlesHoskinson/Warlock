"""Freeze captured surface/output facts and bounded retained geometry evidence."""
import hashlib,json,resource
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pair_path=ROOT/'qa/build-pair-manifest.json';pair=json.loads(pair_path.read_text());assert pair['passed']
for rel,digest in pair['files'].items():assert sha(ROOT/rel)==digest,rel
for role in ('core','plugin'):assert sha(pair['nativePair'][role]['path'])==pair['nativePair'][role]['sha256']
native_reports=[];accepted_hashes=set()
for p in sorted((ROOT/'qa').glob('native-*/report.json')):
 v=json.loads(p.read_text())
 if not v['passed']:continue
 assert not v.get('error') and v['cleanupPassed']
 for source,digest in v['inputs'].items():assert sha(source)==digest,source
 accepted_hashes.add(sha(p));native_reports.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':len(v['checks']),'configuration':v.get('configurationVariant','Original private fixture')})
assert sorted(v['checks'] for v in native_reports)==[63,84]
reports={}
for key in ['elm','model','mutant']:
 p=sorted((ROOT/'qa').glob(key+'-*/report.json'))[-1];v=json.loads(p.read_text());assert v['passed'] and not v.get('error'),key
 if key=='elm':
  assert v['checks']==28 and v['nativeCaptures']==18 and v['nativeReportSHA256'] in accepted_hashes
  for rel,digest in v['inputs'].items():assert sha(ROOT/rel)==digest,rel
 elif key=='model':assert v['sourceSHA256']==sha(ROOT/'spec/facts.qnt') and v['namedScenarios']==6
 else:assert v['originalSHA256']==sha(ROOT/'spec/facts.qnt')
 reports[key]={'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'Captured surface/output facts and actual retained geometry across resize; not complete scene/input/presentation or release acceptance','wholeFeatureAccepted':False,'canonicalSceneCapability':False,'completedRequirementIds':[],'nativePair':pair['nativePair'],'pairManifestSHA256':sha(pair_path),'nativeReports':native_reports,'reports':reports,'elmChecks':28,'quintNamedRuns':6,'quintInvariantSamples':1000,'modelUnsafeVariantDetected':True,'files':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Frozen surface facts evidence; full input/scene/presentation gates remain open')
