"""Freeze exact source, bounded evidence and live owning host compilation closure."""
import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
origin=json.loads((ROOT/'origin.json').read_text());OLD=Path(origin['source'])
assert sha(OLD/'component-manifest.json')==origin['manifestSHA256']
deltas=[]
for row in origin['production']:
 assert sha(OLD/row['path'])==row['sha256'],row['path']
 if sha(ROOT/row['path'])!=row['sha256']:deltas.append(row['path'])
assert sorted(deltas)==['adapter/daemon.py','native/host.c'],deltas
selected={
 'broker':'qa/review-1791120525848117563/report.json',
 'shutdown':'qa/shutdown-1791120457849241370/report.json',
 'build':'qa/build-1791120424654802946/report.json',
 'semantic':'current-semantic/qa/replay-1791120310793928909/report.json',
 'postClose':'post-close/qa/replay-1791120090708932449/report.json'}
reports={};external={}
for name,rel in selected.items():
 p=ROOT/rel;r=json.loads(p.read_text());assert r['passed'],name
 reports[name]={'path':str(p),'sha256':sha(p)}
 if name in ['broker','shutdown']:
  assert len(r['checks'])==({'broker':43,'shutdown':10}[name])
  for artifact,w in r['artifacts'].items():assert sha(p.parent/artifact)==w,artifact
 if name=='broker':
  for source,w in r['sourceInputs'].items():assert sha(ROOT/source)==w,source
 if name in ['semantic','postClose']:
  for source,w in r['sourceInputs'].items():assert sha(ROOT/source)==w,source
buildpath=ROOT/selected['build'];build=json.loads(buildpath.read_text());buildroot=buildpath.parent
for rel,w in build['inputs'].items():
 assert sha(buildroot/'inputs'/rel)==w,rel
 if rel.startswith(('src/','native/','adapter/','assets/')) or rel=='elm.json':assert sha(ROOT/rel)==w,rel
for section in ['compilerDependencies','tools','linkedLibraries']:
 for path,row in build[section].items():
  assert sha(Path(path))==row['sha256'],path
  external[path]=row
for rel,w in build['artifacts'].items():assert sha(buildroot/rel)==w,rel
assert sha(buildroot/'elm-host')==build['binarySHA256']
target=ROOT/'component-manifest.json';assert not target.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size}
 for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p!=target}
gui={}
for name in ['elm.js','bar.js','popup.js']:
 p=buildroot/'inputs/assets'/name;gui['assets/'+name]={'path':str(p),'sha256':sha(p),'compiled':True}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Bounded broker/stdout and orderly EOF process drain CPU qualification; no GUI/native operation or combined recovery acceptance',
 'nativeAcceptance':False,'fullRecoveryAcceptance':False,'releaseAcceptance':False,
 'productionDeltas':deltas,'reports':reports,'checks':{'broker':43,'shutdown':10,'semantic':152,'postClose':59},
 'buildReport':str(buildpath),'buildReportSHA256':sha(buildpath),'buildRoot':str(buildroot),'binary':str(buildroot/'elm-host'),'binarySHA256':build['binarySHA256'],'guiAssets':gui,
 'originManifest':str(OLD/'component-manifest.json'),'originManifestSHA256':origin['manifestSHA256'],
 'files':files,'externalClosure':external}
target.write_text(json.dumps(manifest,indent=2)+'\n')
for rel,row in files.items():assert sha(ROOT/rel)==row['sha256'],rel
print(json.dumps({'passed':True,'files':len(files),'external':len(external),'manifest':str(target),'manifestSHA256':sha(target)}))
