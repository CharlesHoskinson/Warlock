"""Freeze bounded draw-dispatch evidence, preserving separate claim scopes."""
import hashlib,json,resource
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pair_path=ROOT/'qa/build-pair-manifest.json';pair=json.loads(pair_path.read_text());assert pair['passed']
for rel,digest in pair['files'].items():assert sha(ROOT/rel)==digest,rel
for role in ('core','plugin'):assert sha(pair['nativePair'][role]['path'])==pair['nativePair'][role]['sha256']
natives=sorted((ROOT/'qa').glob('native-*/report.json'));assert len(natives)==2
native_reports=[]
for p in natives:
 v=json.loads(p.read_text());assert v['passed'] and not v.get('error') and v['cleanupPassed']
 for source,digest in v['inputs'].items():assert sha(source)==digest,source
 native_reports.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':len(v['checks']),'configuration':v.get('configurationVariant','Original private fixture')})
elm_path=sorted((ROOT/'qa').glob('elm-*/report.json'))[-1];elm=json.loads(elm_path.read_text());assert elm['passed'] and elm['checks']==22 and elm['nativeReportSHA256']==sha(natives[-1])
for rel,digest in elm['inputs'].items():assert sha(ROOT/rel)==digest,rel
model_path=sorted((ROOT/'qa').glob('model-*/report.json'))[-1];model=json.loads(model_path.read_text());assert model['passed'] and model['sourceSHA256']==sha(ROOT/'spec/trace.qnt')
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'Surface draw dispatch and quiescent opaque overlap evidence; not canonical scene/presentation or release acceptance','wholeFeatureAccepted':False,'canonicalSceneCapability':False,'completedRequirementIds':[],'pairManifestSHA256':sha(pair_path),'nativePair':pair['nativePair'],'nativeReports':native_reports,'elmReport':{'path':str(elm_path.relative_to(ROOT)),'sha256':sha(elm_path),'checks':elm['checks']},'modelReport':{'path':str(model_path.relative_to(ROOT)),'sha256':sha(model_path),'namedCases':model['namedScenarios'],'samples':model['invariantSamples']},'files':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Frozen original63/full-redraw78/Elm22/model8 evidence; canonical scene remains unqualified')
