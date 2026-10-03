"""Freeze diagnostic validation only; preserve exact historical native lineage."""
import hashlib,json,resource
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=sorted((ROOT/'qa').glob('elm-*/report.json'))[-1];report=json.loads(p.read_text())
assert report['passed'] and not report.get('error')
assert report['checks']==121 and report['nativeCaptures']==18
for rel,digest in report['inputs'].items():assert sha(ROOT/rel)==digest,rel
assert sha(p.parent/'checks.json')==report['checksSHA256']
assert sha(p.parent/'replay.js')==report['replaySHA256']
assert sha(report['nativeReportSource'])==report['nativeReportSHA256']
parent=ROOT.parent/'elm-surface-facts-v20/qa/slice-manifest.json'
previous=json.loads(parent.read_text());assert previous['passed']
for rel,digest in previous['files'].items():assert sha(parent.parents[1]/rel)==digest,rel
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'Compiled bounded diagnostic validation only; V20 native evidence replayed, no new native campaign','wholeFeatureAccepted':False,'canonicalSceneCapability':False,'completedRequirementIds':[],'checks':121,'historicalNativePackets':18,'report':str(p.relative_to(ROOT)),'reportSHA256':sha(p),'ancestorManifestSHA256':sha(parent),'files':{str(f.relative_to(ROOT)):sha(f) for f in ROOT.rglob('*') if f.is_file() and not f.is_symlink() and f!=ROOT/'qa/slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Frozen compiled trace validation: 121 checks, no scene admission')
