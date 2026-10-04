import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1]
def row(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
prep=json.loads((ROOT/'qa/current-preparation.json').read_bytes());p=pathlib.Path(prep['report']);assert row(p)['sha256']==prep['sha256'];pr=json.loads(p.read_bytes());assert pr['passed'] and len(pr['checks'])==152
for path,digest in pr['sourcePins'].items():assert row(pathlib.Path(path))['sha256']==digest,path
review=ROOT/'qa/review-1791155917908466495/report.json';r=json.loads(review.read_bytes());assert r['passed'] and r['assertions']==129 and not r['nativeExecuted']
for name,digest in r['sourceSHA256'].items():assert row(ROOT/name)['sha256']==digest,name
manifest=ROOT/'component-manifest.json';assert not manifest.exists();assert not any(p.is_symlink() for p in ROOT.rglob('*'))
files={str(p.relative_to(ROOT)):row(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=manifest}
manifest.write_text(json.dumps({'schema':1,'component':ROOT.name,'selectedGUI':'elm-recovery-delivery-integrated-gui-v640','preparationReport':str(p.relative_to(ROOT)),'reviewReport':str(review.relative_to(ROOT)),'compiledPreparationChecks':152,'sourceReviewChecks':129,'nativeExecuted':False,'layoutAcceptance':False,'ATCompliance':False,'files':files},indent=2,sort_keys=True)+'\n')
for name,expected in files.items():assert row(ROOT/name)==expected,name
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'nativeExecuted':False}))
