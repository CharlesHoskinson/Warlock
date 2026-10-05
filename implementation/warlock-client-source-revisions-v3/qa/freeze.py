import json,hashlib,pathlib,resource,sys
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((r/"native-build-report.json").read_text());report=pathlib.Path(d["pluginBuildReport"]);assert sha(report)==d["pluginBuildReportSHA256"];b=json.loads(report.read_text());assert b["passed"]
for rel,h in b["inputs"].items():assert sha(r/rel)==h,rel
assert not (r/"component-manifest.json").exists()
files={str(p.relative_to(r)):{"sha256":sha(p),"size":p.stat().st_size} for p in sorted(r.rglob("*")) if p.is_file() and not p.is_symlink()}
(r/"component-manifest.json").write_text(json.dumps({"sourceHeld":True,"evidenceIntegrityPassed":True,"nativeAcceptance":False,"fullReleaseAccepted":False,"pluginSourcesUnchanged":True,"files":files},indent=2)+"\n")
print("Source held; exact696 owning headers and compiled plugin retained")
