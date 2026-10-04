import datetime,hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];GUI=ROOT.parent/'elm-native-popover-v61';assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=sorted((GUI/'qa').glob('build-*/report.json'))[-1];v=json.loads(build.read_text());assert v['passed']
assert all(sha(GUI/name)==digest for name,digest in v['inputs'].items())
reports={str(build):{'passed':True,'sha256':sha(build),'scope':'Build/effect20/shell27 only'}}
for p in sorted((ROOT/'qa').glob('native-*/report.json')):
 v=json.loads(p.read_text());assert not v['passed'] and v['cleanupPassed']
 assert sha(v['buildReport'])==v['buildReportSHA256']
 for name,digest in v['inputs'].items():
  source=p.parent/'inputs/native.py' if name==str(ROOT/'qa/native.py') else Path(name)
  assert sha(source)==digest,name
 for artifact in v['pair'].values():assert sha(artifact['path'])==artifact['sha256']
 reports[str(p)]={'passed':False,'sha256':sha(p),'checksReached':len(v['checks']),'error':v['error'],'cleanupPassed':True}
for directory in [GUI,ROOT]:
 manifest={'passed':False,'inventoryVerified':True,'disposition':'no-go for GTK3 GtkPopover as specified xdg_popup container; continue alternative native popup route','observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wholeFeatureAccepted':False,'completedRequirementIds':[],'reports':reports,'files':{str(p.relative_to(directory)):sha(p) for p in sorted(directory.rglob('*')) if p.is_file() and p.name!='slice-manifest.json'}}
 (directory/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(directory/'qa/slice-manifest.json')
