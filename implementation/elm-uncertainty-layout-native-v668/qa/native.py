"""Reviewed root-only source closure then unchanged V667 diagnostic runner."""
import hashlib,json,os,pathlib,runpy,sys
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT.parent
pins={"elm-uncertainty-layout-review-v662":"d0ed87ec3df20fe40a265942595b97db5408309ebbee4931acefce6b8925eea3","elm-uncertainty-layout-png-repair-v667":"7ff3469682f7e659359b809c3ccf675b5691b00a6c04202ccdacdf86461e873b"}
held={}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name,sha in pins.items():
 p=BASE/name/"component-manifest.json"
 assert digest(p)==sha,"changed parent manifest"
 m=json.loads(p.read_bytes())
 for rel,v in m["files"].items():
  q=p.parent/rel
  assert q.is_file() and not q.is_symlink() and q.stat().st_size==v["size"] and digest(q)==v["sha256"],str(q)
  held[str(q)]=v["sha256"]
repair=BASE/"elm-uncertainty-layout-png-repair-v667"
m=json.loads((repair/"component-manifest.json").read_bytes())
d=json.loads((repair/m["dependencyReport"]).read_bytes())
assert d["passed"]
for p,sha in d["dependencyPins"].items():
 assert digest(pathlib.Path(p))==sha,"changed dependency "+p
 held[p]=sha
out=ROOT/"qa/native-evidence"
assert not out.exists(),"fresh output required"
os.environ["ELM_LAYOUT_NATIVE_OUTPUT"]=str(out)
(ROOT/"qa/preflight.json").write_text(json.dumps({"passed":True,"held":held,"parentManifestPins":pins,"nativeExecuted":False,"fullReleaseAccepted":False},indent=2)+"\n")
sys.path.insert(0,str(repair/"qa"))
runpy.run_path(str(repair/"qa/native.py"),run_name="__main__")
