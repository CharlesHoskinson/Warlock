"""Independent read-only build/closure verification and immutable inventory publication."""
import ast,hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
builds=[]
for p in ROOT.glob("core/build-*/report.json"):
 d=json.loads(p.read_text())
 if d["passed"]:builds.append((p,d))
assert len(builds)==1
report,r=builds[0];out=report.parent
assert not r["installed"] and not r["nativeAcceptance"]
assert len(r["affectedTranslationUnits"])==17 and len(r["rebuiltArchiveMembers"])==17 and r["unchangedArchiveMembers"]==416
assert all(c["exitCode"]==0 for c in r["commands"])
assert sum(c["name"].endswith("-compile") for c in r["commands"])==17
assert r["exportClosure"]=={"ancestorCount":13412,"candidateCount":13412,"missingSymbols":[]}
for rel,wanted in r["artifacts"].items():assert sha(out/rel)==wanted,rel
for group in ["dependencies","tools","linkDependencies","ancestorLinkDependencies","linkedLibraries","consumerDependencyInventories","retainedPolicyHeaders"]:
 for path,wanted in r[group].items():assert sha(path)==wanted,path
for rel,wanted in r["owningHeaders"].items():assert sha(out/"owning-headers"/rel)==wanted,rel
for rel,wanted in r["inputs"].items():assert sha(ROOT/"core"/rel)==sha(out/"inputs"/rel)==wanted,rel
assert sha(r["binary"])==r["binarySHA256"]==sha(out/"Hyprland-relink")
assert sha(out/"libhyprland_lib.a")==r["archiveSHA256"]
a=json.loads((out/"ancestor-archive-payloads.json").read_text());b=json.loads((out/"new-archive-payloads.json").read_text())
# Reparse archive payloads using the frozen reviewed parser, never execute builder.
module=ast.parse((out/"initial-build.py").read_text());fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=="payloads")
ns={"Path":Path,"hashlib":hashlib};exec(compile(ast.Module(body=[fn],type_ignores=[]),"archive-parser","exec"),ns)
assert ns["payloads"](r["ancestor"]["archive"])==a
assert ns["payloads"](out/"libhyprland_lib.a")==b
assert len(a)==len(b)==433
for old,new in zip(a,b):
 assert old["name"]==new["name"]
 member=new["name"]
 if member in r["rebuiltArchiveMembers"]:assert new["sha256"]==r["rebuiltArchiveMembers"][member]==sha(out/member)
 else:assert new==old
for rel,entry in r["sourceOrigins"].items():
 assert sha(entry["geometrySource"])==entry["geometrySourceSHA256"]
 assert sha(entry["selectedSource"])==entry["selectedSourceSHA256"]==sha(out/"owning-headers"/rel)
 assert entry["ancestorArchiveMember"]==next(row for row in a if row["name"]==Path(rel).name+".o")
lineage=json.loads((ROOT/"LINEAGE.json").read_text());assert sha(lineage["failedReport"])==lineage["failedReportSHA256"]
failed=json.loads(Path(lineage["failedReport"]).read_text());assert failed["passed"] is False and failed["error"]=="KeyError('source')"
limits=list(ROOT.glob("core/qa/limits-*/report.json"));assert len(limits)==1 and json.loads(limits[0].read_text())["passed"]
files={str(p.relative_to(ROOT)):{"sha256":sha(p),"size":p.stat().st_size} for p in sorted(ROOT.rglob("*")) if p.is_file() and not p.is_symlink() and p.name!="component-manifest.json"}
manifest={"sourceHeld":True,"evidenceIntegrityPassed":True,"nativeAcceptance":False,"releaseAcceptance":False,"scope":"Full merged core actual compile/archive/link closure and limits component only; no plugin/GUI acceptance","buildReport":str(report),"files":files}
target=ROOT/"component-manifest.json"
with target.open("x") as f:f.write(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"passed":True,"manifest":str(target),"sha256":sha(target),"files":len(files)}))
