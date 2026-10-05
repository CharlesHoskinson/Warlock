import json,hashlib,pathlib,resource,sys
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1];repo=r.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=r/"qa/check-1791237663327899214/report.json";c=json.loads(report.read_text());assert c["passed"] and c["nativeStatesCompared"]==14 and len(c["traces"])==2
for path,h in c["inputs"].items():assert sha(pathlib.Path(path))==h,path
n=repo/"implementation/warlock-client-child-native-v6";receipt=json.loads((n/"qa/native-result.json").read_text());native=pathlib.Path(receipt["path"]);assert sha(native)==receipt["sha256"];d=json.loads(native.read_text());assert d["passed"] and d["cleanupPassed"] and len(d["checks"])==764 and len(d["ownedExitCodes"])==69 and all(x["exitCode"]==0 for x in d["ownedExitCodes"])
pre=json.loads((n/"qa/preflight.json").read_text())
for path,h in pre["inputs"].items():assert sha(pathlib.Path(path))==h,path
old=json.loads((repo/"implementation/warlock-client-child-native-v3/qa/native-1791237123393481021/report.json").read_text());assert {x["name"] for x in old["checks"]}<={x["name"] for x in d["checks"]}
for root in [r,n]:
 assert not (root/"component-manifest.json").exists()
 files={str(p.relative_to(root)):{"sha256":sha(p),"size":p.stat().st_size} for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink()}
 (root/"component-manifest.json").write_text(json.dumps({"sourceHeld":True,"evidenceIntegrityPassed":True,"boundedNativeLayoutCacheQualification":True,"nativeAcceptance":False,"fullReleaseAccepted":False,"files":files},indent=2)+"\n")
print("Held764 native checks,46 cache plus14 layout states and69 normal exits")
