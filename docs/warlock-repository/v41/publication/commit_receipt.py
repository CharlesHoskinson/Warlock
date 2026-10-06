import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).resolve().parent

def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
receipt=json.loads((base/'delivery.json').read_text());assert receipt['pushCompleted'] and receipt['remoteObserved']==receipt['publishedCommit']
assert git(['rev-parse','HEAD'],text=True).strip()==receipt['sourceCommit']
assert git(['ls-remote','github','refs/heads/feature/elm'],text=True).split()[0]==receipt['publishedCommit']
assert json.loads((base/'visibility.json').read_text())['visibility']=='PUBLIC'
assert not git(['diff','--cached','--name-only'])
paths=[str((base/name).relative_to(ROOT)) for name in ['prepared.json','delivery.json','visibility.json','push.stdout','push.stderr']]
checkpoint=sorted((ROOT/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'))[-1]
assert json.loads(checkpoint.read_text())['currentSlice']=='implementation/warlock-client-provider-native-v78';paths.append(str(checkpoint.relative_to(ROOT)))
git(['-c','core.autocrlf=false','add','--',*paths]);assert set(git(['diff','--cached','--name-only'],text=True).splitlines())==set(paths)
for path in paths:assert git(['show',':'+path])==(ROOT/path).read_bytes(),path
git(['commit','-m','Record public native coordinate rendering and bounded storage qualification'])
print(json.dumps({'receiptCommit':git(['rev-parse','HEAD'],text=True).strip(),'ownedFiles':len(paths),'rawBytesVerified':True}))
