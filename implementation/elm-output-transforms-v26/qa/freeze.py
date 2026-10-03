"""Freeze native output/mask fixtures; maintain explicit bounded acceptance."""
import hashlib,json,resource
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
CORE=ROOT.parent/'elm-input-hit-v23';parent_path=CORE/'qa/slice-manifest.json';parent=json.loads(parent_path.read_text());assert parent['passed']
for rel,digest in parent['files'].items():assert sha(CORE/rel)==digest,rel
for artifact in parent['nativePair'].values():assert sha(artifact['path'])==artifact['sha256']
accepted=[];failed=[];sibling_files={}
for name,count,passed in [('elm-output-facts-v24',105,False),('elm-output-mapping-v25',111,True),('elm-output-transforms-v26',168,True)]:
 base=ROOT.parent/name
 source=json.loads((base/'qa/source-manifest.json').read_text())
 for rel,digest in source['files'].items():assert sha(base/rel)==digest,rel
 paths=list((base/'qa').glob('native-*/report.json'));assert len(paths)==1
 p=paths[0];v=json.loads(p.read_text());assert v['passed']==passed and len(v['checks'])==count and v['cleanupPassed']
 assert v['pair']['core']==parent['nativePair']['core']
 for path,digest in v['inputs'].items():assert sha(path)==digest,path
 receipt={'path':str(p),'sha256':sha(p),'checks':count,'sourceManifestSHA256':sha(base/'qa/source-manifest.json')}
 if passed:
  assert all(c['passed'] for c in v['checks']) and not v.get('error')
  accepted.append(receipt)
 else:
  assert v['error']=="AssertionError('rotatedInputHoleStillPaintsPeer')" and not v['checks'][-1]['passed']
  receipt['error']=v['error'];failed.append(receipt)
 if base!=ROOT:sibling_files[name]={str(f.relative_to(base)):sha(f) for f in base.rglob('*') if f.is_file() and not f.is_symlink()}
tp=sorted((ROOT/'qa').glob('trace-*/report.json'))[-1];t=json.loads(tp.read_text());assert t['passed'] and t['checks']==109
for path,digest in t['inputs'].items():assert sha(path)==digest,path
assert sha(tp.parent/'checks.json')==t['checksSHA256']
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'Actual output movement, fractional scale and8 transforms with immutable retained configurations and logical pointer/keyboard mask routing; not raw scanout/presentation or full scene/output/device/release acceptance','wholeFeatureAccepted':False,'canonicalSceneCapability':False,'completedRequirementIds':[],'nativePair':parent['nativePair'],'ancestorManifestSHA256':sha(parent_path),'nativeReports':accepted,'failedReports':failed,'typedActualPacketChecks':109,'traceReport':str(tp.relative_to(ROOT)),'traceReportSHA256':sha(tp),'newQuintRun':False,'siblingFiles':sibling_files,'files':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Frozen bounded output movement/scale/transform receipts and109 actual Elm packet checks')
