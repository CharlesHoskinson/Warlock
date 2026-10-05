import json,hashlib,pathlib,resource,sys
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1];repo=r.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pre=json.loads((r/"qa/preflight.json").read_text())
for name,h in pre["inputs"].items():assert sha(pathlib.Path(name))==h,name
for root in [r,repo/"implementation/warlock-client-child-fixture-v3"]:
 assert not (root/"component-manifest.json").exists()
 files={str(p.relative_to(root)):{"sha256":sha(p),"size":p.stat().st_size} for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink()}
 (root/"component-manifest.json").write_text(json.dumps({"sourceHeld":True,"evidenceIntegrityPassed":True,"nativeAcceptance":False,"fullReleaseAccepted":False,"failedNativeEvidencePreserved":True,"files":files},indent=2)+"\n")
print("Preserved failed campaign and fixture source identity")
