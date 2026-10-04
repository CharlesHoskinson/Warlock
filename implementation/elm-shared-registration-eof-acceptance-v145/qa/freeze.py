import hashlib,json,pathlib,resource,sys,time
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/"implementation/elm-shared-registration-eof-integration-v144";OUT=ROOT/"qa"/("freeze-"+str(time.time_ns()));OUT.mkdir()
reports=["qa/build-1791121323616998481/report.json","qa/local-unsent-1791120852860062017/report.json","qa/review-1791120852863993164/report.json","qa/review-1791120852886116199/report.json","qa/shutdown-1791120852864561245/report.json","current-semantic/qa/replay-1791120962064122688/report.json","post-close/qa/replay-1791120962064030981/report.json"]
for name in reports:assert json.loads((SOURCE/name).read_text())["passed"],name
build=json.loads((SOURCE/reports[0]).read_text())
for rel,digest in build["inputs"].items():assert hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()==digest,rel
own=[]
for p in sorted(SOURCE.rglob("*")):
 if "elm-stuff" in p.parts or "node_modules" in p.parts:continue
 assert not p.is_symlink(),str(p)
 if p.is_file():own.append({"path":str(p.resolve()),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size":p.stat().st_size})
external=[]
for group in ["compilerDependencies","tools","linkedLibraries"]:
 for original,row in build[group].items():
  p=pathlib.Path(original);assert str(p.resolve())==row["resolved"],original
  assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==row["sha256"] and p.stat().st_size==row["size"],original
  external.append({"kind":group,"path":original,**row})
for row in own:assert hashlib.sha256(pathlib.Path(row["path"]).read_bytes()).hexdigest()==row["sha256"],row["path"]
manifest={"scope":"Bounded combined actual CPU/source/build evidence; no native/release acceptance","certificateChecks":62,"deferredAttachChecks":3,"registrationChecks":25,"brokerChecks":43,"teardownChecks":10,"semanticChecks":211,"nativeAcceptance":False,"releaseAcceptance":False,"reports":reports,"files":own,"externalClosure":external}
p=ROOT/"component-manifest.json";p.write_text(json.dumps(manifest,indent=2)+"\n")
report={"passed":True,"ownFiles":len(own),"externalEntries":len(external),"manifestSHA256":hashlib.sha256(p.read_bytes()).hexdigest()};(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
