import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];PARENT=ROOT.parent/'elm-uncertainty-layout-review-v662'
def row(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
parent_manifest=PARENT/'component-manifest.json';assert row(parent_manifest)['sha256']=='d0ed87ec3df20fe40a265942595b97db5408309ebbee4931acefce6b8925eea3'
pm=json.loads(parent_manifest.read_bytes())
for name,expected in pm['files'].items():assert row(PARENT/name)==expected,name
for name in ['webkit_fixture.py','current-preparation.json']:assert row(ROOT/'qa'/name)==row(PARENT/'qa'/name),name
pointer=json.loads((ROOT/'qa/current-dependencies.json').read_bytes());report=pathlib.Path(pointer['report']);assert row(report)['sha256']==pointer['sha256'];r=json.loads(report.read_bytes());assert r['passed'] and r['assertions']==34 and not r['nativeExecuted']
for name,digest in r['sourceSHA256'].items():assert row(ROOT/name)['sha256']==digest,name
for name,digest in r['dependencyPins'].items():assert row(pathlib.Path(name))['sha256']==digest,name
manifest=ROOT/'component-manifest.json';assert not manifest.exists();assert not any(p.is_symlink() for p in ROOT.rglob('*'))
files={str(p.relative_to(ROOT)):row(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=manifest}
manifest.write_text(json.dumps({'schema':1,'component':ROOT.name,'parentManifest':str(parent_manifest),'parentManifestSHA256':row(parent_manifest)['sha256'],'unchangedParentFiles':['qa/webkit_fixture.py','qa/current-preparation.json'],'dependencyReport':str(report.relative_to(ROOT)),'dependencyChecks':34,'nativeExecuted':False,'layoutAcceptance':False,'ATCompliance':False,'files':files},indent=2,sort_keys=True)+'\n')
for name,expected in files.items():assert row(ROOT/name)==expected,name
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'dependencyChecks':34,'nativeExecuted':False}))
