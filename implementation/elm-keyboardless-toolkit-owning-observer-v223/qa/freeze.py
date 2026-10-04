"""Preserve exact canonical toolkit observer recompiled against corrected Core205."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=next((ROOT/'qa').glob('build-*/report.json'));r=json.loads(p.read_text());assert r['passed'] and not r['missingSymbols'] and len(r['owningHeaders'])==694
for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest
for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest
external={}
for section in ['dependencies','linkedLibraries','tools']:
 for path,digest in r[section].items():assert sha(path)==digest;external[path]={'sha256':digest,'size':Path(path).stat().st_size}
for key in ['path','buildReport','componentManifest']:
 path=r['core'][key];digest=r['core'][{'path':'sha256','buildReport':'buildReportSHA256','componentManifest':'componentManifestSHA256'}[key]];assert sha(path)==digest;external[path]={'sha256':digest,'size':Path(path).stat().st_size}
a=json.loads((ROOT/'origin.json').read_text());assert sha(a['source'])==a['sourceSHA256']==sha(ROOT/'native/observer.cpp') and sha(a['component'])==a['componentSHA256']
files={};links={}
for path in sorted(ROOT.rglob('*')):
 if path==ROOT/'component-manifest.json':continue
 if path.is_symlink():links[str(path.relative_to(ROOT))]=os.readlink(path)
 elif path.is_file():files[str(path.relative_to(ROOT))]={'sha256':sha(path),'size':path.stat().st_size,'mode':stat.S_IMODE(path.stat().st_mode)}
result={'sourceHeld':True,'evidenceIntegrityPassed':True,'compiled':True,'nativeAcceptance':False,'fullRoadmapAccepted':False,'scope':'Byte-exact canonical toolkit observer246 recompiled against exact Core205; owning ABI/symbol/source gate only, no GTK01-08 or hardware GUI acceptance','buildReport':str(p),'buildReportSHA256':sha(p),'files':files,'symlinks':links,'externalFiles':external}
with (ROOT/'component-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'external':len(external),'manifestSHA256':sha(ROOT/'component-manifest.json')}))
