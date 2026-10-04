import datetime,hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports={}
for kind in ["checks","model"]:
 p=sorted((ROOT/"qa").glob(kind+"-*/report.json"))[-1];v=json.loads(p.read_text());assert v["passed"]
 if kind == "checks":
  assert all(sha(ROOT/rel)==digest for rel,digest in v["inputs"].items())
 else:assert sha(ROOT/"spec/launch.qnt")==v["sourceSHA256"]
 reports[str(p.relative_to(ROOT))]={"sha256":sha(p),"passed":True,"checks":len(v.get("checks",[])),"typedChecks":v.get("typedChecks"),"legacyParserTests":v.get("legacyParserTests"),"namedScenarios":v.get("namedScenarios"),"invariantSamples":v.get("invariantSamples")}
assert sha(ROOT/"src/UInt64.elm")==sha(ROOT.parent/"elm-catalog-launch-v55/src/UInt64.elm")
files={str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob("*")) if p.is_file() and p.name!="slice-manifest.json"}
manifest={"passed":True,"observedUTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"Pure typed launch controller with actual native receipt replay; no GUI/broker integration or application readiness","wholeFeatureAccepted":False,"completedRequirementIds":[],"reports":reports,"files":files}
(ROOT/"qa/slice-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(ROOT/"qa/slice-manifest.json")
