"""Protected current-source verification and immutable independent review inventory."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-geometry-family-menu-receipt-cleanup-native-v100'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=SOURCE/'qa/held-source-manifest.json';assert sha(p)=='7a7c0ed9c3559afea1140ffb51fdc6baafaa25a5b8334d42a3e84a9b7ef479f5';m=json.loads(p.read_text());assert m['sourceHeld'] and m['evidenceIntegrityPassed'] and not m['nativeAcceptance']
for rel,e in m['files'].items():
 f=SOURCE/rel;assert not f.is_symlink() and f.stat().st_size==e['size'] and sha(f)==e['sha256'] and stat.S_IMODE(f.stat().st_mode)==int(e['mode'],8),rel
report=ROOT/'qa/review-1791110160832839920/report.json';r=json.loads(report.read_text());assert r['passed'] and not r.get('error') and len(r['checks'])==19 and all(c['passed'] for c in r['checks'])
for path,e in r['inputs'].items():assert sha(Path(path))==e['sha256'] and Path(path).stat().st_size==e['size'],path
for rel,digest in r['artifacts'].items():assert sha(report.parent/rel)==digest,rel
failed=ROOT/'qa/review-1791110142404788992/report.json';assert not json.loads(failed.read_text())['passed']
files={}
for f in sorted(ROOT.rglob('*')):
 if f.is_file():assert not f.is_symlink();files[str(f.relative_to(ROOT))]={'sha256':sha(f),'size':f.stat().st_size,'mode':stat.S_IMODE(f.stat().st_mode)}
out={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'full09Accepted':False,'releaseAcceptance':False,'scope':'Independent V100 source review; AST/auth/deadline/census only, no GUI','reviewedSourceManifest':{'path':str(p),'sha256':sha(p),'verifiedFiles':len(m['files'])},'acceptedReport':{'path':str(report.relative_to(ROOT)),'sha256':sha(report),'checks':19},'failure':{'path':str(failed.relative_to(ROOT)),'sha256':sha(failed)},'files':files}
target=ROOT/'qa/held-source-manifest.json'
with target.open('x') as stream:stream.write(json.dumps(out,indent=2)+'\n')
target.chmod(0o444);print(json.dumps({'passed':True,'verifiedV100Files':len(m['files']),'manifest':str(target),'sha256':sha(target),'reviewFiles':len(files)}))
