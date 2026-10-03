"""Freeze actual Elm activation/recovery without broader GUI/release claims."""
import hashlib,json,resource
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];CORE=ROOT.parent/'elm-activation-protocol-v28'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
cp=CORE/'qa/slice-manifest.json';core=json.loads(cp.read_text());assert core['passed']
for rel,digest in core['files'].items():assert sha(CORE/rel)==digest,rel
for rel,digest in core['ancestorFiles'].items():assert sha(ROOT.parent/'elm-window-activation-v27'/rel)==digest,rel
bp=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];build=json.loads(bp.read_text());assert build['passed']
for rel,digest in build['inputs'].items():assert sha(ROOT/rel)==digest,rel
assert sha(bp.parent/'elm-host')==build['binarySHA256']
np=next((ROOT/'qa').glob('native-*/report.json'));native=json.loads(np.read_text());assert native['passed'] and native['cleanupPassed'] and not native.get('error') and len(native['checks'])==27 and all(c['passed'] for c in native['checks'])
for source,digest in native['inputs'].items():assert sha(source)==digest,source
assert native['pair']==core['nativePair']
failed=[];ancestor_files={}
for name in ['elm-gui-activation-v29','elm-gui-activation-recovery-v30','elm-gui-activation-events-v31']:
 base=ROOT.parent/name;p=next((base/'qa').glob('native-*/report.json'));v=json.loads(p.read_text());assert not v['passed'] and v['cleanupPassed']
 for source,digest in v['inputs'].items():assert sha(source)==digest,source
 failed.append({'path':str(p),'sha256':sha(p),'error':v['error']})
 ancestor_files[name]={str(f.relative_to(base)):sha(f) for f in base.rglob('*') if f.is_file() and not f.is_symlink()}
for name in ['Effects.elm','Shell.elm','ActionProjection.elm','Binding.elm','UInt64.elm']:assert sha(ROOT/'src'/name)==sha(CORE/'src'/name),name
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'Real pointer/Elm/native activation and keyboard recipients, stable displayed order and exact-journal broker reconnect; not full taskbar, scene/presentation, renderer/authority restart or release acceptance','wholeFeatureAccepted':False,'canonicalSceneCapability':False,'completedRequirementIds':[],'nativePair':core['nativePair'],'coreManifestSHA256':sha(cp),'buildReport':str(bp.relative_to(ROOT)),'buildReportSHA256':sha(bp),'nativeReport':str(np.relative_to(ROOT)),'nativeReportSHA256':sha(np),'nativeChecks':27,'compiledOriginalChecks':47,'inheritedCompiledActivationChecks':17,'failedReports':failed,'ancestorFiles':ancestor_files,'files':{str(f.relative_to(ROOT)):sha(f) for f in ROOT.rglob('*') if f.is_file() and not f.is_symlink() and f!=ROOT/'qa/slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Frozen actual Elm/native activation and exact-journal recovery27 checks')
