"""Freeze owned source, failures and bounded evidence without release claims."""
import hashlib,json,resource,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
PREFIXES=[REPO/'implementation/elm-window-geometry-v16',ROOT]
MANIFEST=ROOT/'component-manifest.json';assert not MANIFEST.exists()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
accepted=['core/build-1791098117250155855/report.json','core/qa/closure-1791098168146518088/report.json','core/qa/link-closure-1791098175984269698/report.json','core/qa/callbacks-1791098413770820585/report.json','core/qa/map-state-1791098278016540852/report.json','core/qa/native-1791098384319585553/report.json']
for name in accepted:
 p=ROOT/name;r=json.loads(p.read_text());assert r['passed'],name
 for rel,value in r.get('artifacts',{}).items():assert sha(p.parent/rel)==value,(name,rel)
native=json.loads((ROOT/accepted[-1]).read_text());assert native['cleanupPassed'] and len(native['checks'])==35 and all(c['passed'] for c in native['checks'])
entries=[]
for prefix in PREFIXES:
 for path in sorted(prefix.rglob('*')):
  if '__pycache__' in path.parts:continue
  if path.is_symlink():entries.append({'path':str(path.relative_to(REPO)),'symlink':str(path.readlink())})
  elif path.is_file():entries.append({'path':str(path.relative_to(REPO)),'size':path.stat().st_size,'sha256':sha(path)})
packet={'passed':True,'frozenUTCUnixNs':time.time_ns(),'nativeScope':'Direct xdg ordinary/maximize/duplicate-set/restore/duplicate-unset with border-aware workarea, exact placement, request-correlated server barrier, client configure/ACK/queued buffer and three presented interior pixels','nativeChecks':35,'fullRoadmapAccepted':False,'menuAuthorityIntegrated':False,'pluginABIQualified':False,'deployed':False,'quintModelLogicApproved':False,'acceptedReports':[{ 'path':str((ROOT/name).relative_to(REPO)),'sha256':sha(ROOT/name)} for name in accepted],'files':entries,'excluded':'Python bytecode caches; immutable predecessor/runtime tuples retain their original manifests'}
MANIFEST.write_text(json.dumps(packet,indent=2)+'\n')
for entry in entries:
 path=REPO/entry['path']
 if 'sha256' in entry:assert path.stat().st_size==entry['size'] and sha(path)==entry['sha256']
 else:assert path.is_symlink() and str(path.readlink())==entry['symlink']
print(json.dumps({'passed':True,'manifest':str(MANIFEST),'sha256':sha(MANIFEST),'entries':len(entries)}),flush=True)
