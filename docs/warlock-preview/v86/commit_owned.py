"""Commit exact held GUI81/failed117/passed118 and owned publication preparation."""
import hashlib,json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=r,**kw)
assert git(['rev-parse','HEAD'],text=True).strip()=='70c6f9db74e9a70647ee94b5b32f5950f2adde58'
assert not git(['diff','--cached','--name-only'],text=True).strip();assert git(['rev-parse','--show-object-format'],text=True).strip()=='sha1'
foreign=git(['diff','--name-only'],text=True).splitlines();before={p:sha(r/p) for p in foreign};paths=set()
for name,passed in [('warlock-preview-provider-v85',True),('warlock-client-provider-native-v123',False),('warlock-client-provider-native-v124',True)]:
 root=r/'implementation'/name;m=root/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed']==passed;paths.add(str(m.relative_to(r)))
 for rel,row in d['files'].items():
  p=root/rel;assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];paths.add(str(p.relative_to(r)))
for base in [r/'docs/warlock-preview/v85',r/'docs/warlock-preview/v86',r/'docs/warlock-repository/v61/publication']:
 for p in base.rglob('*'):
  assert not p.is_symlink(),p
  if p.is_file():paths.add(str(p.relative_to(r)))
tracked=set(git(['ls-files','docs/elm-roadmap/delivery/build-loop-events'],text=True).splitlines())
for p in (r/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'):
 if str(p.relative_to(r)) not in tracked:paths.add(str(p.relative_to(r)))
assert not paths.intersection(foreign)
git(['-c','core.autocrlf=false','add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in sorted(paths)))
assert set(git(['diff','--cached','--name-only'],text=True).splitlines())==paths
rows={};ordered=sorted(paths)
for offset in range(0,len(ordered),400):
 for line in git(['ls-files','--stage','-z','--',*ordered[offset:offset+400]]).split(b'\0'):
  if not line:continue
  fields,name=line.split(b'\t',1);mode,oid,stage=fields.decode().split();assert stage=='0';rows[name.decode()]=(mode,oid)
assert set(rows)==paths
for name,(mode,oid) in rows.items():
 data=(r/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,name
assert all(sha(r/p)==h for p,h in before.items())
git(['commit','-m','Qualify bounded native window registry and strict lock control publication'])
print(json.dumps({'commit':git(['rev-parse','HEAD'],text=True).strip(),'ownedFiles':len(paths),'foreignPathsPreserved':foreign}))
