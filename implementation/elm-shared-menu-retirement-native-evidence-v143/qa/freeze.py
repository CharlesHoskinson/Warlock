import hashlib,json,pathlib,resource,sys,time
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/"qa"/("freeze-"+str(time.time_ns()));OUT.mkdir()
NATIVE=REPO/"implementation/elm-shared-menu-retirement-cleanup-native-v142"
p=NATIVE/"qa/native-1791120086344847435/report.json";d=json.loads(p.read_text());assert d["passed"] and d["cleanupPassed"] and not d["mainDesktopActions"]
assert len(d["checks"])==48 and all(row["passed"] for row in d["checks"])
ancestor=REPO/"implementation/elm-shared-menu-target-retirement-native-v139/qa/native-1791119969130228936/report.json"
a=json.loads(ancestor.read_text());assert [x["name"] for x in d["checks"] if x["name"]!="nativeClientsEmptyBeforePluginUnload"]==[x["name"] for x in a["checks"]]
assert next(x for x in d["checks"] if x["name"]=="nativeClientsEmptyBeforePluginUnload")["clients"]==[]
assert d["retirementExtension"]["remainingSeconds"]>0 and not d["retirementExtension"]["originalGeometryMenu10Accepted"]
pre=NATIVE/"qa/preflight.json";preflight=json.loads(pre.read_text());assert preflight["passed"]
expected=dict(preflight["inputs"])
for relative,digest in d["artifacts"].items():expected[str(p.parent/relative)]=digest
for extra in [p,pre,ancestor,ROOT/"HANDOFF.md",NATIVE/"qa/deadline-test.py",REPO/"implementation/elm-shared-context-disposition-deadline-native-v136/qa/deadline-1791119130710191445/report.json",NATIVE/"qa/deadline-origin.json"]:expected[str(extra)]=hashlib.sha256(extra.read_bytes()).hexdigest()
rows=[]
for path,digest in sorted(expected.items()):
 q=pathlib.Path(path);assert q.is_file() and not q.is_symlink(),path
 stat=q.stat();data=q.read_bytes();assert hashlib.sha256(data).hexdigest()==digest,path
 assert (stat.st_ino,stat.st_size,stat.st_mtime_ns)==(q.stat().st_ino,q.stat().st_size,q.stat().st_mtime_ns),path
 rows.append({"path":str(q.resolve()),"sha256":digest,"size":len(data)})
manifest={"scope":"Bounded current shared-menu native baseline only; original fault/full roadmap gates open","boundedSharedMenuNativeAccepted":True,"boundedTargetRetirementAccepted":True,"emptyClientCensusBeforePluginUnload":True,"originalGeometryMenu10Accepted":False,"nativeChecks":48,"pixelStages":3,"cleanupPassed":True,"deadlineSeconds":6,"deadlineControls":4,"fullFaultRecoveryAccepted":False,"fullReleaseAccepted":False,"pair":d["pair"],"files":rows}
target=ROOT/"component-manifest.json";target.write_text(json.dumps(manifest,indent=2)+"\n")
report={"passed":True,"verifiedFiles":len(rows),"manifestSHA256":hashlib.sha256(target.read_bytes()).hexdigest()};(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
