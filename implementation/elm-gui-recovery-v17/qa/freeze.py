"""Freeze bounded evidence with current source, native pair and replay hashes."""
import hashlib,json,resource
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CORE=ROOT.parent/'elm-seat-effects-v15'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
paths={key:sorted((ROOT/'qa').glob(key+'-*/report.json'))[-1] for key in ['build','native','model','conformance']}
reports={key:json.loads(p.read_text()) for key,p in paths.items()}
for key,v in reports.items():assert v['passed'] and not v.get('error'),key
for rel,digest in reports['build']['inputs'].items():assert sha(ROOT/rel)==digest,rel
for path,digest in reports['native']['inputs'].items():assert sha(path)==digest,path
assert reports['native']['cleanupPassed'] and reports['native']['buildReportSHA256']==sha(paths['build'])
assert reports['model']['sourceSHA256']==sha(ROOT/'spec/recovery.qnt')
assert reports['conformance']['buildReportSHA256']==sha(paths['build']) and reports['conformance']['modelReportSHA256']==sha(paths['model'])
assert reports['conformance']['compiledShellSHA256']==sha(paths['build'].parent/'shell.js')
core=json.loads((CORE/'qa/slice-manifest.json').read_text());assert core['passed']
for rel,digest in core['files'].items():assert sha(CORE/rel)==digest,rel
pair=json.loads((CORE/'qa/build-pair-manifest.json').read_text())['nativePair']
assert reports['native']['pair']==pair
for role in ('core','plugin'):assert sha(pair[role]['path'])==pair[role]['sha256']
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':reports['native']['scope'],'wholeFeatureAccepted':False,'completedRequirementIds':[],'nativePair':pair,'reports':{key:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for key,p in paths.items()},'effectReplayChecks':20,'shellReplayChecks':27,'modelNamedRuns':8,'modelInvariantSamples':1000,'modelReplayTraces':reports['conformance']['traces'],'modelReplayTransitions':reports['conformance']['transitions'],'nativeChecks':len(reports['native']['checks']),'files':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Frozen broker recovery evidence; renderer/authority/release gates remain open')
