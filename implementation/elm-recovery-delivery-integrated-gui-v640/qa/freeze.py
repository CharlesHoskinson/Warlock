import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bp=Path(json.loads((ROOT/'qa/current-build.json').read_text())['report']);b=json.loads(bp.read_text());assert b['passed']
for n,d in b['inputs'].items():assert sha(ROOT/n)==d
for n,d in b['artifacts'].items():assert sha(bp.parent/n)==d
assert sha(bp.parent/'elm-host')==b['binarySHA256']
for pattern in ['tests-*/report.json','drain-*/report.json','controls-*/report.json']:
 ps=list((ROOT/'qa').glob(pattern));assert len(ps)==1 and json.loads(ps[0].read_text())['passed']
files={}
for p in sorted(ROOT.rglob('*')):
 if 'elm-stuff' in p.parts or '__pycache__' in p.parts or p==ROOT/'component-manifest.json':continue
 assert not p.is_symlink(),str(p)
 if p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size}
out=ROOT/'component-manifest.json';assert not out.exists();out.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'component':'elm-recovery-delivery-integrated-gui-v640','completeGUIBuild':True,'buildReport':str(bp),'buildReportSHA256':sha(bp),'nativeAcceptance':False,'fullReleaseAccepted':False,'separateNativeReceipt':'implementation/elm-recovery-delivery-reviewed-v650/component-manifest.json','files':files},indent=2)+'\n');print(out)
