import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/"qa"/("combined-review-"+str(time.time_ns()));OUT.mkdir()
WORK=ROOT/"qa/local-unsent-1791117219012158141"
PARENT=REPO/"implementation/elm-shared-observation-recovery-v121/qa/disposition-1791112312091107116"
report={"passed":False,"nativeAcceptance":False,"releaseAcceptance":False,"inputs":{},"commands":[]}
def capture(path,label):
 dest=OUT/"inputs"/label;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
 report["inputs"][str(path)]={"snapshot":str(dest),"sha256":hashlib.sha256(dest.read_bytes()).hexdigest()};return dest
def run(name,args,cwd):
 result=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180)
 (OUT/(name+".stdout")).write_text(result.stdout);(OUT/(name+".stderr")).write_text(result.stderr)
 report["commands"].append({"name":name,"argv":args,"exitCode":result.returncode})
 assert result.returncode==0,result.stderr[-6000:]
try:
 test=capture(PARENT/"inputs/qa/stale.cjs","stale.cjs")
 worker=capture(WORK/"worker.js","worker.js");ancestor=capture(PARENT/"ancestor.js","ancestor.js")
 evidence=capture(WORK/"inputs/qa/native-evidence.json","native-evidence.json");probe=capture(WORK/"probe","probe")
 prior=json.loads((WORK/"report.json").read_text());assert prior["passed"]
 for relative,wanted in prior["inputs"].items():
  assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==wanted,relative
  capture(ROOT/relative,pathlib.Path("source")/relative)
 run("candidate-stale",["node",str(test),str(worker),str(evidence),str(probe),str(OUT/"candidate.json"),"candidate"],ROOT)
 run("unsafe-control",["node",str(test),str(ancestor),str(evidence),str(probe),str(OUT/"ancestor.json"),"ancestor"],ROOT)
 source=OUT/"inputs/source"
 for module in ["Bar","Popup"]:
  run(module+"-compile",["npm","exec","--yes","--package=elm@0.19.2-0","--","elm","make","src/"+module+".elm","--optimize","--output="+str(OUT/(module+".js"))],source)
 report["checks"]=json.loads((OUT/"candidate.json").read_text())["checks"]
 report["unsafeAncestorFailureDemonstrated"]=json.loads((OUT/"ancestor.json").read_text())["unsafeAncestorFailureDemonstrated"]
 report["passed"]=True
except Exception as e:report["error"]=repr(e)
report["scope"]="Combined captured V121/V122 prototype: operation62 already passed; independently exercised stale UI guard and unsafe ancestor controls; optimized Bar/Popup compile. Deferred attach final fix and current shared-context/native integration remain open."
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"passed":report["passed"],"report":str(OUT/"report.json"),"error":report.get("error")}));sys.exit(not report["passed"])
