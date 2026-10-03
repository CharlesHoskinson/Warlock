"""Freeze repair and actual pointer/keyboard evidence without broad acceptance."""
import hashlib,json,resource
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pair_path=ROOT/'qa/build-pair-manifest.json';pair=json.loads(pair_path.read_text());assert pair['passed']
for rel,digest in pair['files'].items():assert sha(ROOT/rel)==digest,rel
for artifact in pair['nativePair'].values():assert sha(artifact['path'])==artifact['sha256']
accepted=[];failed=[]
for p in sorted((ROOT/'qa').glob('native-*/report.json')):
 v=json.loads(p.read_text())
 if not v['passed']:
  assert len(v['checks'])==0 and 'FileNotFoundError' in v.get('error','')
  failed.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'error':v['error']});continue
 assert v['cleanupPassed'] and not v.get('error') and all(c['passed'] for c in v['checks'])
 assert v['pair']['core']==pair['nativePair']['core']
 for path,digest in v['inputs'].items():assert sha(path)==digest,path
 accepted.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':len(v['checks']),'configuration':v.get('configurationVariant','Original private fixture')})
assert sorted(v['checks'] for v in accepted)==[63,94,97]
tp=sorted((ROOT/'qa').glob('trace-*/report.json'))[-1];t=json.loads(tp.read_text());assert t['passed'] and t['checks']==44
for path,digest in t['inputs'].items():assert sha(path)==digest,path
assert sha(tp.parent/'checks.json')==t['checksSHA256']
failures=[]
for name in ['elm-input-region-v22','elm-input-mask-v22']:
 parent=ROOT.parent/name
 p=next((parent/'qa').glob('native-*/report.json'));v=json.loads(p.read_text());assert not v['passed'] and v['cleanupPassed'] and any(not c['passed'] for c in v['checks'])
 for path,digest in v['inputs'].items():assert sha(path)==digest,path
 failures.append({'path':str(p),'sha256':sha(p),'error':v['error']})
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'Native content input-mask selection, actual hole/solid/restored pointer and keyboard recipients above lower owner and MAX; no full scene/presentation/release acceptance','wholeFeatureAccepted':False,'canonicalSceneCapability':False,'completedRequirementIds':[],'nativePair':pair['nativePair'],'pairManifestSHA256':sha(pair_path),'nativeReports':accepted,'failedPreflightReports':failed,'originalFailedReports':failures,'typedActualPacketChecks':44,'traceReport':str(tp.relative_to(ROOT)),'traceReportSHA256':sha(tp),'files':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Frozen bounded native input-mask selection repair; all full release gates remain open')
