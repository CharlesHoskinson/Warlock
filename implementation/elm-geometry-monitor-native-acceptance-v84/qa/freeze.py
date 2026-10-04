"""Freeze bounded actual native geometry acceptance and preserved menu failure."""
import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
lanes=[("elm-geometry-staged-menu-native-v77","d5a9c11862d587175890cc814e852f1f73cb3481fa497883e7e4941236da6559","native-1791107389900372198",False),("elm-geometry-monitor-native-regression-v79","e5e3a3180de9e8c3a67a2e262ccd4e5d830bef81608edf767754cf61a6c0c6d2","native-1791107523831396904",True)]
files={};reports=[]
for name,digest,native,accepted in lanes:
 base=REPO/"implementation"/name;held=base/"qa/held-source-manifest.json";assert sha(held)==digest
 packet=json.loads(held.read_text());assert packet["sourceHeld"] and packet["evidenceIntegrityPassed"]
 for rel,row in packet["files"].items():
  p=base/rel;assert p.is_file() and not p.is_symlink() and sha(p)==row["sha256"],rel
 report_path=base/"qa"/native/"report.json";report=json.loads(report_path.read_text());assert report["passed"] is accepted and report["cleanupPassed"]
 assert not report["mainDesktopActions"] and report["privateHost"]["mainDisplayUsed"] is False
 assert all(c["passed"] for c in report["checks"])
 maps=report["privateHost"]["privateAquamarine"];assert maps["mappedVerified"] and maps["mappedFiles"]=={maps["path"]:maps["sha256"]}
 assert sha(maps["path"])==maps["sha256"]
 if accepted:
  assert len(report["checks"])==96 and len(report["pixelAttempts"])==7 and not report["menuTransportIntegrated"]
 else:
  assert len(report["checks"])==110 and report["scenarios"]==["GEOMETRY-MENU-"+str(i).zfill(2) for i in range(1,8)]
  assert report["error"]=="RuntimeError('Whole-transition absolute six-second deadline')" and "coherent()['reconnect']" in report["traceback"]
 for rel,digest in report["artifacts"].items():assert sha(report_path.parent/rel)==digest,rel
 for path,digest in report["inputs"].items():assert sha(path)==digest,path
 for p in sorted(base.rglob("*")):
  if p.is_file():
   assert not p.is_symlink();files[str(p.relative_to(REPO))]={"sha256":sha(p),"size":p.stat().st_size}
 reports.append({"path":str(report_path),"sha256":sha(report_path),"passed":accepted,"cleanupPassed":True})
for p in ROOT.rglob("*"):
 if p.is_file():files[str(p.relative_to(REPO))]={"sha256":sha(p),"size":p.stat().st_size}
manifest={"sourceHeld":True,"evidenceIntegrityPassed":True,"scope":"Actual native single floating Wayland window geometry96/7 on V73/V75/V30; original menu campaign failure110 preserved. No full menu/shared-host/hardware/release acceptance.","boundedGeometryNativeAccepted":True,"fullMenuNativeAccepted":False,"fullRoadmapAccepted":False,"releaseAccepted":False,"inventoryBase":str(REPO),"files":files,"reports":reports,"remaining":["Correct menu08 disconnect precondition without increasing absolute6s deadline","Full09 actual matching receipt held while facts and notifications progress","Menu10 exact target retirement/replacement","Fresh semantic traces for original14menu+3refresh and geometry setup failures","Shared-output durable admission/recovery and remaining S01–S16 mandatory release/deployment gates"]}
p=ROOT/"component-manifest.json"
with p.open("x") as f:f.write(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"passed":True,"manifest":str(p),"sha256":sha(p),"files":len(files)}))
