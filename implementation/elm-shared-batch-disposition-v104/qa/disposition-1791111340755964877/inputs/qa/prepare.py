import hashlib,json,resource,shutil,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
manifest=REPO/'implementation/elm-shared-staged-menu-acceptance-v308/qa/slice-manifest.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
packet=json.loads(manifest.read_text());assert packet['passed'] and not packet['nativeRun']
for row in packet['files']:
 p=REPO/row['path']
 if 'sha256' in row:assert sha(p)==row['sha256'],str(p)
 if row.get('type')=='symlink':assert p.readlink().as_posix()==row['target']
source=REPO/packet['finalSource'];origins={}
for directory in ['src','native','assets','adapter','candidate']:
 for p in sorted((source/directory).rglob('*')):
  if p.is_file():
   relative=p.relative_to(source);dest=ROOT/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);origins[str(relative)]={'path':str(p),'sha256':sha(p)}
shutil.copy2(source/'elm.json',ROOT/'elm.json');origins['elm.json']={'path':str(source/'elm.json'),'sha256':sha(source/'elm.json')}
(ROOT/'qa/source-origins.json').write_text(json.dumps({'manifest':str(manifest),'manifestSHA256':sha(manifest),'files':origins},indent=2)+'\n')
print(json.dumps({'passed':True,'copied':len(origins),'verifiedClosureFiles':len(packet['files'])}))
