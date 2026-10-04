import hashlib,json,os,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent=REPO/'implementation/elm-gui-bounds-held-v280/acceptance-manifest.json';assert sha(parent)=='803d21b080df49b90e6f4272975d2c32456006ec5cbb22682a4d2332c967954b';held=json.loads(parent.read_text());assert held['passed']
for entry in held['files']:
 p=REPO/entry['path']
 if 'symlink' in entry:assert p.is_symlink() and os.readlink(p)==entry['symlink']
 else:assert sha(p)==entry['sha256'],str(p)
r={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'compiled':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'source':'implementation/elm-responsive-surfaces-gui-v278','parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'files':held['files'],'scope':'CPU exact-source binding derivative of held280 current278 optimized build and captured adapter; parent893 native evidence retained separately, no additional native acceptance'}
with (ROOT/'source-manifest.json').open('x') as f:f.write(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(r['files']),'manifestSHA256':sha(ROOT/'source-manifest.json')}))
