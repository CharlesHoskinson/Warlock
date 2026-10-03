"""Freeze bounded native scene proof without promoting it to product acceptance."""
import datetime
import hashlib
import json
from pathlib import Path
import resource

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
core_path=ROOT/'qa/core-source-manifest-v10.json'
core=json.loads(core_path.read_text())
assert core['passed'] and not core['productSceneAcceptance']
for relative,digest in core['files'].items():
    assert sha(REPO/'implementation/elm-modal-focus-v10'/relative)==digest,relative
packet=ROOT/'qa/native-1791056554713775783/report.json'
proof=json.loads(packet.read_text())
assert proof['passed'] and proof['cleanupPassed'] and not proof['mainDesktopActions']
assert proof['sourceManifestSHA256']==sha(core_path)
assert len(proof['checks'])==23 and all(row['passed'] for row in proof['checks'])
assert proof['pair']['core']==core['nativePair']['core']
for path,digest in proof['inputs'].items(): assert sha(Path(path))==digest,path
for relative,digest in proof['artifacts'].items(): assert sha(packet.parent/relative)==digest,relative
manifest={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,
'scope':'23 private single-output quiescent MAX/pin/exclusion/modal pixel-pointer-keyboard and modal-retirement held-release checks; not canonical atomic scene, full minimize, security, hardware or product release acceptance',
'acceptedReport':str(packet.relative_to(ROOT)),'acceptedReportSHA256':sha(packet),
'coreManifestSHA256':sha(core_path),'checks':23,'completedRequirementIds':[],
'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))
