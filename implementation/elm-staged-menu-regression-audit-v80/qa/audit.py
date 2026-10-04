"""Retain exact old failed identities as open obligations; no semantic-equivalence inference."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
PARENT=REPO/"implementation/elm-menu-post-close-tests-v71/qa/replay-1791106215786245435"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(d):return next(v for v in d.values() if isinstance(v,list) and v and isinstance(v[0],dict) and "name" in v[0])
inputs={};obligations=[];counts={}
for name,total,failed in [("menu-original-checks.json",78,14),("refresh-original-checks.json",21,3)]:
 p=PARENT/name;inputs[str(p)]=sha(p);d=json.loads(p.read_text());cases=rows(d)
 assert len(cases)==total and len({r["name"] for r in cases})==total
 rejected=[r for r in cases if r["passed"] is False];assert len(rejected)==failed
 counts[name]={"total":total,"originalPassed":total-failed,"originalFailed":failed}
 for r in rejected:obligations.append({"suite":name,"originalIdentity":r["name"],"originalResult":"failed","originalDiagnostic":r.get("error"),"stagedEquivalentQualified":False,"requiredEvidence":"Fresh staged two-observation trace retaining the original final action, receipt/ledger/ownership assertion and identity; original fixture remains frozen."})
p=PARENT/"post-close-checks.json";inputs[str(p)]=sha(p);new=rows(json.loads(p.read_text()));assert len(new)==59 and all(r["passed"] for r in new)
report_path=PARENT/"report.json";inputs[str(report_path)]=sha(report_path)
original_report=json.loads(report_path.read_text());assert original_report["passed"]
OUT=ROOT/"qa"/("audit-"+str(time.time_ns()));OUT.mkdir(mode=0o700)
report={"passed":True,"scope":"Read-only exact failed-identity audit; preservation and coverage-gap evidence only","nativeAcceptance":False,"releaseAcceptance":False,"fullOriginalRegressionQualified":False,"inputs":inputs,"counts":counts,"newPostClosePassed":59,"newCasesAreNotAutomaticSubstitutes":True,"openObligations":obligations,"geometryOriginal":"Setup aborts at immediate-dispatch assumption; all original geometry identities still require a staged equivalent or original-compatible proof."}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"passed":True,"report":str(OUT/"report.json"),"openOriginalIdentities":len(obligations),"fullOriginalRegressionQualified":False}))
