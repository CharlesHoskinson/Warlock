import hashlib,json,pathlib,resource,sys,time
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"qa"/("freeze-"+str(time.time_ns()));OUT.mkdir()
reports=["qa/local-unsent-1791117490426147303/report.json","qa/regression-control-1791117555098109691/report.json","regression/semantic/qa/replay-1791117617654214232/report.json","regression/post-close/qa/replay-1791117617653951252/report.json"]
for n in reports:assert json.loads((ROOT/n).read_text())["passed"],n
rows=[]
for p in sorted(ROOT.rglob("*")):
 rel=p.relative_to(ROOT)
 if p==OUT or OUT in p.parents or p.name=="held-source-manifest.json" or "elm-stuff" in rel.parts or "node_modules" in rel.parts:continue
 assert not p.is_symlink(),str(p)
 if not p.is_file():continue
 data=p.read_bytes();rows.append({"path":str(rel),"size":len(data),"sha256":hashlib.sha256(data).hexdigest()})
for item in rows:
 data=(ROOT/item["path"]).read_bytes();assert len(data)==item["size"] and hashlib.sha256(data).hexdigest()==item["sha256"],item["path"]
manifest={"scope":"Own regular source/build/evidence packet for bounded CPU candidate; compiler dependencies remain separately recorded in tested reports; no native or ABI acceptance","nativeAcceptance":False,"releaseAcceptance":False,"operationChecks":62,"deferredChecks":3,"staleChecks":2,"semanticChecks":211,"oldCombinedDeferredFailureDemonstrated":True,"reports":reports,"files":rows}
path=ROOT/"qa/held-source-manifest.json";path.write_text(json.dumps(manifest,indent=2)+"\n")
report={"passed":True,"regularFiles":len(rows),"manifestSHA256":hashlib.sha256(path.read_bytes()).hexdigest(),"nativeAcceptance":False}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
