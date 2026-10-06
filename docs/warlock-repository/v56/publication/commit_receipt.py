"""Commit exact public-delivery receipts and this owner's fresh checkpoints."""
import hashlib,json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=r,**kw)
assert git(['rev-parse','HEAD'],text=True).strip()=='d62345012d19181d05b2c1c97eabd5461413c807'
assert not git(['diff','--cached','--name-only'],text=True).strip()
d=json.loads((base/'delivery.json').read_text())
assert d['pushCompleted'] and d['ownedFiles']==8731 and d['publishedCommit']=='498df7d93c334137711c87de7915a7e936ba2074'
assert json.loads((base/'visibility.json').read_text())['visibility']=='PUBLIC'
paths={str(p.relative_to(r)) for p in base.glob('*') if p.is_file()}
tracked=set(git(['ls-files','docs/elm-roadmap/delivery/build-loop-events'],text=True).splitlines())
for p in (r/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'):
 if str(p.relative_to(r)) not in tracked:paths.add(str(p.relative_to(r)))
git(['-c','core.autocrlf=false','add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in sorted(paths)))
assert set(git(['diff','--cached','--name-only'],text=True).splitlines())<=paths
assert git(['rev-parse','--show-object-format'],text=True).strip()=='sha1';seen=set();ordered=sorted(paths)
for offset in range(0,len(ordered),400):
 for line in git(['ls-files','--stage','-z','--',*ordered[offset:offset+400]]).split(b'\0'):
  if not line:continue
  fields,name=line.split(b'\t',1);mode,oid,stage=fields.decode().split();assert stage=='0';p=name.decode();data=(r/p).read_bytes()
  assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,p;seen.add(p)
assert seen==paths
git(['commit','-m','Record public native capacity and expiry GUI qualification'])
print(git(['rev-parse','HEAD'],text=True).strip())
