import hashlib,json,pathlib,sys,time,os
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];BASE=ROOT.parent
checks=[];held={}
def check(name,condition):
 checks.append({"name":name,"passed":bool(condition)})
 assert condition,name
def pin(p,sha=None,size=None):
 b=p.read_bytes();actual=hashlib.sha256(b).hexdigest()
 check("held:"+str(p), (sha is None or actual==sha) and (size is None or len(b)==size))
 held[str(p.relative_to(BASE.parent))]={"sha256":actual,"size":len(b)}
 return b
for name,expected in {"elm-atomic-admission-authority-v665":"a90d9a97e8ed72224b0b0d5841f0fb365edc5e18e9a16d06ae93b100790ce7b2","elm-uncertainty-layout-png-repair-v667":"7ff3469682f7e659359b809c3ccf675b5691b00a6c04202ccdacdf86461e873b"}.items():
 p=BASE/name/"component-manifest.json";m=json.loads(pin(p,expected))
 for rel,v in m["files"].items():pin(p.parent/rel,v["sha256"],v["size"])
a=BASE/"elm-atomic-admission-authority-v665"
m=json.loads((a/"component-manifest.json").read_bytes())
t=json.loads((a/m["testsReport"]).read_bytes());check("462FS58faults5children",t["passed"] and t["assertions"]==462 and t["failureBoundaries"]==58 and t["actualAbruptProcessExits"]==5)
check("boundedNotIntegrated",not any(t[k] for k in ["CIntegrated","S15Accepted","completionImplemented","nativeAcceptance","powerLossQualified"]))
check("byteExact647base",(a/"adapter/archive_base.py").read_bytes()==(BASE/"elm-paged-history-storage-v647/adapter/archive.py").read_bytes())
model=json.loads((a/m["modelReport"]).read_bytes());check("threeTypedModelCounterexamples",model["passed"] and len(model["mutations"])==3 and all(v["typecheckExit"]==0 and v["counterexampleExit"]==1 for v in model["mutations"]))
for name in ["elm-uncertainty-layout-native-v664","elm-uncertainty-layout-native-v668"]:
 for p in sorted((BASE/name).rglob("*")):
  if p.is_file() and not p.is_symlink():pin(p)
d=json.loads((BASE/"elm-uncertainty-layout-native-v668/qa/native-evidence/report.json").read_bytes());h=d["privateHost"]
check("668failurePreservedNoLayout",not d["passed"] and not d["layoutAcceptance"] and not d["layoutFindings"] and "setfloating" in d["failure"])
check("668noRemainingDescendants",h["remainingDescendants"]==[] and h["runtimeGone"] and not h["cleanupErrors"])
check("668normalCleanupNotAccepted",not d["cleanupPassed"] and bool(h["unexpectedInnerDescendants"]))
o=ROOT/"qa"/("review-"+str(time.time_ns()));o.mkdir();r={"passed":True,"checks":checks,"held":held,"fullReleaseAccepted":False,"completedRequirementIds":[],"nativeRerun":False,"historicalEvidenceOnly":True}
(o/"report.json").write_text(json.dumps(r,indent=2)+"\n")
(ROOT/"qa/current-review.json").write_text(json.dumps({"report":str(o/"report.json"),"sha256":hashlib.sha256((o/"report.json").read_bytes()).hexdigest()},indent=2)+"\n")
print(o/"report.json")
