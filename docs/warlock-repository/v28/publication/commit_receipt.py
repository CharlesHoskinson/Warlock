import hashlib,json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
assert git(['rev-parse','HEAD'],text=True).strip()=='19a4bbde009b3aaf39e48169c597f27ed78003dd'
assert not git(['diff','--cached','--name-only'])
base=ROOT/'docs/warlock-repository/v28/publication'
paths=[str((base/name).relative_to(ROOT)) for name in ['prepared.json','delivery.json','visibility.json','push.stdout','push.stderr','commit_receipt.py']]
lanes=sorted((ROOT/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'));checkpoint=lanes[-1];assert json.loads(checkpoint.read_text())['currentSlice']=='implementation/warlock-client-provider-native-v42';paths.append(str(checkpoint.relative_to(ROOT)))
receipt=json.loads((base/'delivery.json').read_text());assert receipt['pushCompleted'] and receipt['remoteObserved']=='af34cc4245a7d1063bf1e3ba7c88e14de8f87541'
assert json.loads((base/'visibility.json').read_text())['visibility']=='PUBLIC'
git(['-c','core.autocrlf=false','add','--',*paths]);assert set(git(['diff','--cached','--name-only'],text=True).splitlines())==set(paths)
for path in paths:assert git(['show',':'+path])==(ROOT/path).read_bytes(),path
git(['commit','-m','Record public native style publication and style crop checkpoint'])
print(json.dumps({'receiptCommit':git(['rev-parse','HEAD'],text=True).strip(),'ownedFiles':len(paths),'rawBytesVerified':True}))
