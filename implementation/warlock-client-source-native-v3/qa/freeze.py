import json,hashlib,pathlib,resource,sys
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1];repo=r.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=r/"qa/native-1791237700328665016/report.json";d=json.loads(native.read_text());assert d["passed"] and d["cleanupPassed"] and len(d["checks"])==73 and len(d["ownedExitCodes"])==7 and all(x["exitCode"]==0 for x in d["ownedExitCodes"])
pre=json.loads((r/"qa/preflight.json").read_text())
for path,h in pre["inputs"].items():assert sha(pathlib.Path(path))==h,path
old=json.loads((repo/"implementation/warlock-client-source-native-v2/qa/native-1791236297652478028/report.json").read_text());assert [x["name"] for x in old["checks"]]==[x["name"] for x in d["checks"]]
assert not (r/"component-manifest.json").exists()
files={str(p.relative_to(r)):{"sha256":sha(p),"size":p.stat().st_size} for p in sorted(r.rglob("*")) if p.is_file() and not p.is_symlink()}
(r/"component-manifest.json").write_text(json.dumps({"sourceHeld":True,"evidenceIntegrityPassed":True,"nativeAcceptance":False,"fullReleaseAccepted":False,"boundedRootRegression":True,"files":files},indent=2)+"\n")
print("Original root73 identities held;7 normal exits and clean teardown")
