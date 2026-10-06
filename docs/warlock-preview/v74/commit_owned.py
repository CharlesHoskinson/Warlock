import hashlib,json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=r,**kw)
assert git(['rev-parse','HEAD'],text=True).strip()=='1893577f218f932a24a44eba2924dc8c043477b7'
manifest=r/'implementation/warlock-preview-provider-v66/component-manifest.json';d=json.loads(manifest.read_text());assert d['passed'] and not d['nativeAcceptance'];paths={str(manifest.relative_to(r))}
for name,row in d['files'].items():
 p=manifest.parent/name;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size'];paths.add(str(p.relative_to(r)))
for p in (r/'docs/warlock-preview/v74').rglob('*'):
 assert not p.is_symlink(),p
 if p.is_file():paths.add(str(p.relative_to(r)))
for p in (r/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'):
 if not git(['ls-files','--',str(p.relative_to(r))],text=True).strip():paths.add(str(p.relative_to(r)))
assert set(git(['diff','--cached','--name-only'],text=True).splitlines())<=paths
git(['-c','core.autocrlf=false','add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in sorted(paths)))
assert set(git(['diff','--cached','--name-only'],text=True).splitlines())<=paths
for p in paths:assert git(['show',':'+p])==(r/p).read_bytes(),p
git(['commit','-m','Verify rejected native preview jobs settle through Elm without capture replay']);print(git(['rev-parse','HEAD'],text=True).strip())
