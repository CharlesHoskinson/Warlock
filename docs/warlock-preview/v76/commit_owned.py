"""Commit held native result with batched exact raw index verification."""
import hashlib,json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=r,**kw)
assert git(['log','-1','--format=%s'],text=True).strip()=='Retain native resume deadlines and correlate Elm terminal acknowledgments'
assert not git(['diff','--cached','--name-only'],text=True).strip();assert git(['rev-parse','--show-object-format'],text=True).strip()=='sha1'
root=r/'implementation/warlock-client-provider-native-v109';m=root/'component-manifest.json';d=json.loads(m.read_text());assert d['passed'] and d['nativeChecks']==2419;paths={str(m.relative_to(r))}
for name,row in d['files'].items():
 p=root/name;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size'];paths.add(str(p.relative_to(r)))
for base in [r/'docs/warlock-preview/v76',r/'docs/warlock-repository/v55/publication']:
 for p in base.rglob('*'):
  assert not p.is_symlink(),p
  if p.is_file():paths.add(str(p.relative_to(r)))
tracked=set(git(['ls-files','docs/elm-roadmap/delivery/build-loop-events'],text=True).splitlines())
for p in (r/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'):
 if str(p.relative_to(r)) not in tracked:paths.add(str(p.relative_to(r)))
git(['-c','core.autocrlf=false','add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in sorted(paths)))
assert set(git(['diff','--cached','--name-only'],text=True).splitlines())<=paths
rows={}
for line in git(['ls-files','--stage','-z','--',*sorted(paths)]).split(b'\0'):
 if not line:continue
 fields,name=line.split(b'\t',1);mode,oid,stage=fields.decode().split();assert stage=='0';rows[name.decode()]=(mode,oid)
assert set(rows)==paths
for name,(mode,oid) in rows.items():
 data=(r/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,name
git(['commit','-m','Qualify native resume capacity and receiver ownership on the owning GUI tuple']);print(git(['rev-parse','HEAD'],text=True).strip())
