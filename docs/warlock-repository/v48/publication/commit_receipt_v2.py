"""Record verified publication; an unchanged source checkpoint is not staged anew."""
import json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).resolve().parent
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
r=json.loads((base/'delivery.json').read_text());assert r['pushCompleted'] and r['remoteObserved']==r['publishedCommit']
assert git(['rev-parse','HEAD'],text=True).strip()==r['sourceCommit']
assert git(['ls-remote','github','refs/heads/feature/elm'],text=True).split()[0]==r['publishedCommit']
assert json.loads((base/'visibility.json').read_text())['visibility']=='PUBLIC'
paths=[str((base/name).relative_to(ROOT)) for name in ['prepared.json','delivery.json','visibility.json','push.stdout','push.stderr','commit_receipt_v2.py']]
checkpoint=sorted((ROOT/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'))[-1]
assert json.loads(checkpoint.read_text())['currentSlice']=='implementation/warlock-client-provider-native-v93';paths.append(str(checkpoint.relative_to(ROOT)))
existing=set(git(['diff','--cached','--name-only'],text=True).splitlines());assert existing<=set(paths)
git(['-c','core.autocrlf=false','add','--',*paths]);staged=set(git(['diff','--cached','--name-only'],text=True).splitlines());assert staged and staged<=set(paths)
for path in paths:assert git(['show',':'+path])==(ROOT/path).read_bytes(),path
for path in set(paths)-staged:assert git(['show','HEAD:'+path])==(ROOT/path).read_bytes(),path
git(['commit','-m','Record public Elm fallback metadata qualification'])
print(json.dumps({'receiptCommit':git(['rev-parse','HEAD'],text=True).strip(),'ownedFiles':len(staged),'rawBytesVerified':True}))
