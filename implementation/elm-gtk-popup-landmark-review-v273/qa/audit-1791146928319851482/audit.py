import hashlib,json,resource,sys,time,importlib.util
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
SOURCE=REPO/"implementation/elm-gtk-popup-landmark-fixture-v272"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=SOURCE/"component-manifest.json"
assert sha(manifest)=="07889645e6dc7eaef6aefe96df6a5c575680895364f28de2d612c6fdd8deb0c7"
m=json.loads(manifest.read_text());verified={}
for name,row in m["files"].items():
 p=SOURCE/name;assert sha(p)==row["sha256"];assert p.stat().st_size==row["size"];assert p.stat().st_mode&0o777==row["mode"];verified[str(p)]=row["sha256"]
for name,digest in m["externalFiles"].items():assert sha(name)==digest;verified[name]=digest
assert len(m["files"])==121 and len(m["externalFiles"])==1043
assert m["nativeAcceptance"] is False and m["gtk06Accepted"] is False
spec=importlib.util.spec_from_file_location("callbacks",SOURCE/"qa/callback-test.py");mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
old=REPO/"implementation/elm-gtk-sibling-role-fixture-v253/native/gtk-role-client.c"
a=old.read_text();b=(SOURCE/"native/gtk-role-client.c").read_text()
assert len(m["unchangedFunctions"])==24
for fn in m["unchangedFunctions"]:assert mod.extract(a,fn)==mod.extract(b,fn),fn
for name in m["selectedReports"]:
 report=json.loads((SOURCE/"qa"/name/"report.json").read_text());assert report["passed"] is True and report["nativeAcceptance"] is False
 if "sourceSHA256" in report:assert report["sourceSHA256"]==sha(SOURCE/"native/gtk-role-client.c")
popup=json.loads((SOURCE/"qa/popup-1791146503047786823/report.json").read_text());assert popup["checks"]==9 and len(popup["controls"])==3 and all(x["rejected"] is True and x["exitCode"]!=0 for x in popup["controls"])
assert mod.extract(b,"close_role").index("r->button=NULL")<mod.extract(b,"close_role").index("gtk_widget_unparent")
verified[str(manifest)]=sha(manifest)
out=ROOT/"qa"/("audit-"+str(time.time_ns()));out.mkdir()
report={"passed":True,"nativeAcceptance":False,"gtk06Accepted":False,"verifiedFiles":len(verified),"sourceManifestSHA256":sha(manifest),"unchangedFunctions":24,"popupWitnesses":9,"popupUnsafeControls":3,"inputs":verified}
(out/"report.json").write_text(json.dumps(report,indent=2)+"\n");(out/"audit.py").write_bytes(Path(__file__).read_bytes());print(out/"report.json")
