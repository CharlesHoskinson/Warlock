import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/"qa"/("regression-control-"+str(time.time_ns()));OUT.mkdir()
OLD=REPO/"implementation/elm-combined-disposition-prototype-v127/qa/local-unsent-1791117219012158141"
NEW=ROOT/"qa/local-unsent-1791117490426147303"
report={"passed":False,"nativeAcceptance":False,"releaseAcceptance":False,"inputs":{},"commands":[]}
def capture(p,n):
 q=OUT/"inputs"/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 report["inputs"][str(p)]={"snapshot":str(q),"sha256":hashlib.sha256(q.read_bytes()).hexdigest()};return q
def run(n,args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=45)
 (OUT/(n+".stdout")).write_text(p.stdout);(OUT/(n+".stderr")).write_text(p.stderr)
 report["commands"].append({"name":n,"argv":args,"exitCode":p.returncode});return p
try:
 old=capture(OLD/"worker.js","old-worker.js");new=capture(NEW/"worker.js","new-worker.js")
 evidence=capture(NEW/"inputs/qa/native-evidence.json","evidence.json");probe=capture(NEW/"probe","probe")
 script=capture(NEW/"inputs/qa/deferred-attach.cjs","deferred.cjs")
 result=run("old-deferred",["node",str(script),str(old),str(evidence),str(probe),str(OUT/"old-deferred.json")])
 failed=json.loads((OUT/"old-deferred.json").read_text())
 assert result.returncode==1 and not failed["passed"]
 assert len(failed["checks"])==1 and "while Pending" in failed["checks"][0]
 assert "geometry-facts-request" in result.stderr and "geometry-attach" in result.stderr
 report["oldDeferredAttachFailureDemonstrated"]=True
 result=run("new-deferred",["node",str(script),str(new),str(evidence),str(probe),str(OUT/"new-deferred.json")]);assert result.returncode==0
 report["deferredChecks"]=json.loads((OUT/"new-deferred.json").read_text())["checks"]
 stale=capture(REPO/"implementation/elm-shared-observation-recovery-v121/qa/disposition-1791112312091107116/inputs/qa/stale.cjs","stale.cjs")
 result=run("new-stale",["node",str(stale),str(new),str(evidence),str(probe),str(OUT/"new-stale.json"),"candidate"]);assert result.returncode==0
 report["staleChecks"]=json.loads((OUT/"new-stale.json").read_text())["checks"]
 report["passed"]=True
except Exception as e:report["error"]=repr(e)
report["scope"]="Same actual compiled regression oracle fails the prior combined worker and passes new captured combined worker; stale UI guards remain intact. CPU only."
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"passed":report["passed"],"report":str(OUT/"report.json"),"error":report.get("error")}));sys.exit(not report["passed"])
