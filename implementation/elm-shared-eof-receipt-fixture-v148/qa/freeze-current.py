"""Freeze source-only fixtures/evidence and owning pins without native claims."""
import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'qa'))
import backend,relay
backend.verify_backend();assert relay.verify_receipt(ROOT)==ROOT/'qa/broker-entrypoint.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected={
 'relay':('test-1791121752973483375',19),
 'deadline':('deadline-1791121769479030512',7),
 'edges':('edges-1791121769476991342',7),
 'profiles':('profile-current-1791122207631948940',24),
 'actualAdmissionHistoricalReceipt':('admission-current-1791122125585508486',18),
 'syntheticSelector':('selector-1791122207675783263',52),
 'syntheticSupervision':('hold-1791122290936490365',45)}
reports={}
for name,(directory,count) in selected.items():
 p=ROOT/'qa'/directory/'report.json';r=json.loads(p.read_text());assert r['passed'] and len(r['checks'])==count,name
 for rel,w in r['artifacts'].items():assert sha(p.parent/rel)==w,rel
 reports[name]={'path':str(p),'sha256':sha(p),'checks':count}
pin=json.loads((ROOT/'backend-pin.json').read_text());external={}
for path in [pin['componentManifest'],pin['buildReport'],*pin['tupleFiles']]:
 p=Path(path);external[path]={'sha256':sha(p),'size':p.stat().st_size}
for name,row in pin['adapterFiles'].items():
 for p in [Path(pin['adapterDirectory'])/name,Path(row['source'])]:
  assert sha(p)==row['sha256'];external[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
component=json.loads(Path(pin['componentManifest']).read_text())
for row in component['files']:
 p=Path(row['path']);assert sha(p)==row['sha256'],str(p)
for lane in ['elm-geometry-broker-eof-deadline-v92','elm-geometry-receipt-eof-relay-v90','elm-geometry-receipt-selector-v82']:
 p=REPO/'implementation'/lane/'qa/held-source-manifest.json';external[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
target=ROOT/'component-manifest.json';assert not target.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size}
 for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p!=target}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Current-schema5 source-only EOF/receipt fixtures; actual C admission/store CPU and recorded historical receipt replay, synthetic units separately named',
 'nativeAcceptance':False,'full08Accepted':False,'full09Accepted':False,'full10Accepted':False,'releaseAcceptance':False,
 'profileEntrypoint':str(ROOT/'qa/relay.py'),'receiptEntrypoint':str(ROOT/'qa/broker-entrypoint.py'),'backendPin':pin,'reports':reports,'files':files,'externalClosure':external}
target.write_text(json.dumps(manifest,indent=2)+'\n')
for rel,row in files.items():assert sha(ROOT/rel)==row['sha256']
print(json.dumps({'passed':True,'files':len(files),'manifest':str(target),'manifestSHA256':sha(target)}))
