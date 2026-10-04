import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/"qa"/("projection-"+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={"passed":False,"nativeAcceptance":False,"scope":"Zero-origin pure prospective conversion with owning math library; no native or wire integration","inputs":{},"commands":[]}
try:
 owner=REPO/"implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json"
 closure=json.loads(owner.read_text());assert closure["passed"]
 report["owningBuildReport"]={"path":str(owner),"sha256":sha(owner)}
 library=Path("/usr/lib/libhyprutils.so.0.14.2")
 assert sha(library)==closure["linkedLibraries"][str(library)]
 report["owningLibrary"]={"path":str(library),"sha256":sha(library)}
 for rel in ["candidate/ProspectiveGeometry.hpp","qa/projection-test.cpp","qa/test.py","spec/REQUIREMENTS.md"]:
  p=ROOT/rel;report["inputs"][rel]=sha(p);q=OUT/"inputs"/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 args=["c++","-std=c++23","-O2","-Wall","-Wextra","-Werror","-MD","-MF",str(OUT/"dependencies.d"),str(OUT/"inputs/qa/projection-test.cpp"),str(library),"-o",str(OUT/"projection-test")]
 for name,command in [("compile",args),("checks",[str(OUT/"projection-test")])]:
  p=subprocess.run(command,capture_output=True,text=True,timeout=30)
  (OUT/(name+".stdout")).write_text(p.stdout);(OUT/(name+".stderr")).write_text(p.stderr)
  report["commands"].append({"name":name,"exitCode":p.returncode});assert p.returncode==0,p.stderr
 report["checks"]=int(p.stdout.split(": ")[1]);assert report["checks"]>=1000
 dependencies=(OUT/"dependencies.d").read_text().replace(chr(92)+chr(10)," ").split()[1:]
 report["owningMathHeaders"]={}
 for entry in dependencies:
  path=Path(entry)
  if str(path).startswith("/usr/include/hyprutils/"):
   digest=sha(path);assert digest==closure["dependencies"][str(path)]
   report["owningMathHeaders"][str(path)]=digest
   q=OUT/"owning-headers"/path.relative_to("/usr/include");q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,q)
 assert report["owningMathHeaders"]
 assert sha(library)==report["owningLibrary"]["sha256"]
 for rel,digest in report["inputs"].items():assert sha(ROOT/rel)==digest
 report["controls"]=[]
 controls=[
  ("double-max-reserves","selected.size()-(input.reserved.topLeft+input.reserved.bottomRight)","selected.size()-2*(input.reserved.topLeft+input.reserved.bottomRight)"),
  ("restore-subtracts-reserves","CBox real=input.logical;","CBox real{input.logical.pos(),input.logical.size()-(input.reserved.topLeft+input.reserved.bottomRight)};"),
  ("raw-checks-real-not-integer","axis(configure.x,input.raw.minimum.x","axis(real.w,input.raw.minimum.x"),
  ("configure-multiplies-scale","std::floor(real.w),std::floor(real.h)","std::floor(real.w*input.monitorScale),std::floor(real.h*input.monitorScale)"),
  ("nonzero-origin-guessed","input.xdgGeometryOrigin!=Vector2D{0,0}","false")]
 for name,before,after in controls:
  area=OUT/"controls"/name
  (area/"candidate").mkdir(parents=True);(area/"qa").mkdir()
  text=(OUT/"inputs/candidate/ProspectiveGeometry.hpp").read_text();assert text.count(before)==1
  (area/"candidate/ProspectiveGeometry.hpp").write_text(text.replace(before,after))
  shutil.copy2(OUT/"inputs/qa/projection-test.cpp",area/"qa/projection-test.cpp")
  command=["c++","-std=c++23","-O2","-Wall","-Wextra","-Werror",str(area/"qa/projection-test.cpp"),str(library),"-o",str(area/"projection-test")]
  result=subprocess.run(command,capture_output=True,text=True,timeout=30)
  (area/"compile.stdout").write_text(result.stdout);(area/"compile.stderr").write_text(result.stderr)
  assert result.returncode==0,result.stderr
  result=subprocess.run([str(area/"projection-test")],capture_output=True,text=True,timeout=30)
  (area/"checks.stdout").write_text(result.stdout);(area/"checks.stderr").write_text(result.stderr)
  detected=result.returncode==1 and result.stderr.startswith("failed check ")
  report["controls"].append({"name":name,"exitCode":result.returncode,"detected":detected});assert detected,name
 report["passed"]=True
except Exception as error:report["error"]=repr(error)
report["artifacts"]={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob("*") if p.is_file()}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"passed":report["passed"],"checks":report.get("checks"),"report":str(OUT/"report.json"),"error":report.get("error")}));raise SystemExit(not report["passed"])
