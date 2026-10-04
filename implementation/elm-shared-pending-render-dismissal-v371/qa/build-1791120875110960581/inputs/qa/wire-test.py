import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/"qa"/("wire-"+str(time.time_ns()));OUT.mkdir();report={"passed":False,"nativeAcceptance":False,"inputs":{}}
try:
 paths=[ROOT.parent/"elm-shared-context-disposition-probe-v131/assets/adapter.js",ROOT/"assets/adapter.js",ROOT/"qa/wire-test.cjs",ROOT/"src/Main.elm"]
 copies=[]
 for i,p in enumerate(paths):
  q=OUT/(str(i)+"-"+p.name);shutil.copy2(p,q);copies.append(q);report["inputs"][str(p)]={"snapshot":str(q),"sha256":hashlib.sha256(q.read_bytes()).hexdigest()}
 assert "port nativeBatchDispositions" in copies[3].read_text()
 result=subprocess.run(["node",str(copies[2]),str(copies[0]),str(copies[1]),str(OUT/"checks.json")],capture_output=True,text=True,timeout=30)
 (OUT/"stdout").write_text(result.stdout);(OUT/"stderr").write_text(result.stderr);report["exitCode"]=result.returncode;assert result.returncode==0,result.stderr
 report["checks"]=json.loads((OUT/"checks.json").read_text())["checks"];report["passed"]=True
except Exception as e:report["error"]=repr(e)
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"passed":report["passed"],"report":str(OUT/"report.json"),"error":report.get("error")}));sys.exit(not report["passed"])
