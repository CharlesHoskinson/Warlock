"""Freeze bounded accepted evidence; failures remain immutable history."""
import hashlib,json,resource
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ('elm-seat-effects-v15','elm-gui-effects-v16'):
 root=REPO/'implementation'/name
 build_path=sorted((root/'qa').glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
 for rel,digest in build['inputs'].items():assert sha(root/rel)==digest,rel
 native_path=sorted((root/'qa').glob('native-*/report.json'))[-1];native=json.loads(native_path.read_text());assert native['passed'] and not native.get('error') and native['cleanupPassed']
 for p,digest in native['inputs'].items():assert sha(Path(p))==digest,p
 if name.endswith('v16'):assert native['buildReportSHA256']==sha(build_path)
 manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':native['scope'],'wholeFeatureAccepted':False,'completedRequirementIds':[],'buildReport':str(build_path.relative_to(root)),'buildReportSHA256':sha(build_path),'nativeReport':str(native_path.relative_to(root)),'nativeReportSHA256':sha(native_path),'nativeChecks':len(native['checks']),'files':{str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink() and p!=root/'qa/slice-manifest.json'}}
 (root/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(name,manifest['nativeChecks'])
