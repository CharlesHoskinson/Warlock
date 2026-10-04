"""Read-only protected integrity/source review of held diagnostic runner204."""
import ast,hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];TARGET=REPO/'implementation/elm-geometry-feasible-bounds-native-v204';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=TARGET/'component-manifest.json';assert sha(manifest)=='909dbbf0c2b0b12c80829e205942fa5412063fbd7802ff857d49735f36299cd3'
m=json.loads(manifest.read_text());assert m['sourceHeld'] and not m['nativeAcceptance']
verified={}
def check(p,d):
 p=Path(p);assert sha(p)==d,str(p);verified[str(p)]={'sha256':d,'size':p.stat().st_size}
for rel,row in m['files'].items():check(TARGET/rel,row['sha256'])
check(manifest,sha(manifest));native=TARGET/'qa/native.py';check(native,'ca4b37efeaba17152b834c3faa8913c6cfaba1f5775fe9dfdf55adb4c06d8c2a');assert (ROOT/'qa/reviewed-native.py').read_bytes()==native.read_bytes();ast.parse(native.read_text())
preflight=Path(m['acceptedPreflight']);check(preflight,m['acceptedPreflightSHA256']);p=json.loads(preflight.read_text());assert p['passed'] and not p['nativeAcceptance']
for path,d in p['inputs'].items():check(path,d)
for rel,d in p['artifacts'].items():check(preflight.parent/rel,d)
for rel in ['qa/snapshot-test-1791131747539256302/report.json','qa/plan-test-1791131747537878181/report.json']:
 report=TARGET/rel;j=json.loads(report.read_text());assert j['passed'];assert j['inputs'][str(native)]==sha(native)
 for path,d in j['inputs'].items():check(path,d)
profiles=json.loads((TARGET/'profiles.json').read_text())['profiles'];assert len(profiles)==22 and len([x for x in profiles if x['retainedBaseline']])==8
assert len([x for x in profiles if x['expectedMAX']])==10
out=ROOT/'verification.json';assert not out.exists();out.write_text(json.dumps({'passed':True,'scope':'Read-only held source/report/artifact integrity and review; no GUI/native acceptance','reviewStatus':'scoped clear for diagnostic launch','verified':verified,'nativeAcceptance':False},indent=2)+'\n')
packet=ROOT/'component-manifest.json';assert not packet.exists()
files={str(f.relative_to(ROOT)):{'sha256':sha(f),'size':f.stat().st_size} for f in ROOT.rglob('*') if f.is_file() and f!=packet}
packet.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Independent source review; no native acceptance','nativeAcceptance':False,'reviewStatus':'scoped clear for diagnostic launch','files':files,'reviewedManifest':str(manifest),'reviewedManifestSHA256':sha(manifest),'verifiedEntries':len(verified)},indent=2)+'\n')
print(json.dumps({'passed':True,'verifiedEntries':len(verified),'manifestSHA256':sha(packet),'manifest':str(packet)}))
