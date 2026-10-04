import hashlib,json,pathlib,sys
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parent.parent
pointer=json.loads((ROOT/"qa/current-review.json").read_bytes());p=pathlib.Path(pointer["report"])
assert hashlib.sha256(p.read_bytes()).hexdigest()==pointer["sha256"]
d=json.loads(p.read_bytes());assert d["passed"]
files=dict(d["held"])
for p in ROOT.rglob("*"):
 if p.is_file() and not p.is_symlink() and p.name!="component-manifest.json":
  b=p.read_bytes();files[str(p.relative_to(REPO))]={"sha256":hashlib.sha256(b).hexdigest(),"size":len(b)}
for rel,v in files.items():
 p=REPO/rel;assert p.is_file() and not p.is_symlink();b=p.read_bytes();assert len(b)==v["size"] and hashlib.sha256(b).hexdigest()==v["sha256"],rel
m={"component":str(ROOT.relative_to(REPO)),"files":files,"passed":True,"evidenceIntegrityPassed":True,"sourceHeld":True,"665AdmissionPrototypeOnly":True,"668DiagnosticFailed":True,"668NormalCleanupAccepted":False,"fullReleaseAccepted":False,"completedRequirementIds":[],"mainDesktopActions":False,"selfExcluded":True}
(ROOT/"component-manifest.json").write_text(json.dumps(m,indent=2)+"\n")
print("Frozen",len(files),"regular files",hashlib.sha256((ROOT/"component-manifest.json").read_bytes()).hexdigest())
