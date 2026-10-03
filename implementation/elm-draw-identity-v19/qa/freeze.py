"""Freeze current draw identity and historical retirement proof scopes."""
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
assert sorted(v['checks'] for v in native_reports)==[63,81]
reports={}
for key in ['elm','model','mutant']:
 p=sorted((ROOT/'qa').glob(key+'-*/report.json'))[-1];v=json.loads(p.read_text());assert v['passed'] and not v.get('error'),key
 if key=='elm':
  assert v['checks']==26 and v['nativeReportSHA256'] in accepted_hashes
  for rel,digest in v['inputs'].items():assert sha(ROOT/rel)==digest,rel
 elif key=='model':assert v['sourceSHA256']==sha(ROOT/'spec/identity.qnt') and v['namedScenarios']==6
 else:assert v['originalSHA256']==sha(ROOT/'spec/identity.qnt')
 reports[key]={'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'Draw-time window/lifetime tokens and actual retained-frame unmap/remap retirement; not complete scene/presentation or release acceptance','wholeFeatureAccepted':False,'canonicalSceneCapability':False,'completedRequirementIds':[],'nativePair':pair['nativePair'],'pairManifestSHA256':sha(pair_path),'nativeReports':native_reports,'reports':reports,'elmChecks':26,'quintNamedRuns':6,'quintInvariantSamples':1000,'modelUnsafeVariantDetected':True,'files':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Frozen draw identity evidence; complete scene remains open')
