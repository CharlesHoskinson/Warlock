"""Commit verified public retirement observation delivery and owned checkpoints."""
import hashlib,json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');base=pathlib.Path(__file__).parent
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=r,**kw)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((base/'delivery.json').read_text())
assert git(['rev-parse','HEAD'],text=True).strip()==d['sourceCommit']
assert not git(['diff','--cached','--name-only'],text=True).strip()
assert d['pushCompleted'] and d['ownedFiles']>=2213 and len(d['inventory'])==d['ownedFiles'] and d['priorPublication']=='48451e88124dd0ae9aa8e69f25e25c7ba8e82e05'
assert d['remoteObserved']==d['publishedCommit'] and json.loads((base/'branch.json').read_text())=={'commit':d['publishedCommit'],'verified':True}
assert git(['ls-remote','github','refs/heads/feature/elm'],text=True).split()[0]==d['publishedCommit']
assert json.loads((base/'visibility.json').read_text())['visibility']=='PUBLIC'
foreign=git(['diff','--name-only'],text=True).splitlines();before={p:sha(r/p) for p in foreign}
paths={str(p.relative_to(r)) for p in base.glob('*') if p.is_file()}
tracked=set(git(['ls-files','docs/elm-roadmap/delivery/build-loop-events'],text=True).splitlines())
for p in (r/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'):
 if str(p.relative_to(r)) not in tracked:paths.add(str(p.relative_to(r)))
assert not paths.intersection(foreign)
git(['-c','core.autocrlf=false','add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in sorted(paths)))
assert set(git(['diff','--cached','--name-only'],text=True).splitlines())<=paths
assert git(['rev-parse','--show-object-format'],text=True).strip()=='sha1';seen=set();ordered=sorted(paths)
for offset in range(0,len(ordered),400):
 for line in git(['ls-files','--stage','-z','--',*ordered[offset:offset+400]]).split(b'\0'):
  if not line:continue
  fields,name=line.split(b'\t',1);mode,oid,stage=fields.decode().split();assert stage=='0';p=name.decode();data=(r/p).read_bytes()
  assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,p;seen.add(p)
assert seen==paths and all(sha(r/p)==h for p,h in before.items())
git(['commit','-m','Record public native-issued renderer transport qualification'])
print(git(['rev-parse','HEAD'],text=True).strip())
