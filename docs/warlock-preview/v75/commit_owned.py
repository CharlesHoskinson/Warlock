"""Commit exact held GUI/source/spec/evidence and preserve concurrent changes."""
import hashlib,json,pathlib,resource,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=r,**kw)
assert git(['rev-parse','HEAD'],text=True).strip()=='03e865cdfdc02bc2b03033b4f3e37a413524c82e'
paths=set()
for n in range(67,72):
 root=r/('implementation/warlock-preview-provider-v'+str(n));m=root/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'];assert d['passed']==(n==71);paths.add(str(m.relative_to(r)))
 for name,row in d['files'].items():
  p=root/name;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size'];paths.add(str(p.relative_to(r)))
spec=r/'openspec/changes/warlock-preview-resume-intents';m=spec/'component-manifest.json';d=json.loads(m.read_text());assert d['requirements']==5 and d['scenarios']==11;paths.add(str(m.relative_to(r)))
for name,row in d['files'].items():
 p=spec/name;assert sha(p)==row['sha256'];paths.add(str(p.relative_to(r)))
for p in (r/'docs/warlock-preview/v75').rglob('*'):
 assert not p.is_symlink(),p
 if p.is_file():paths.add(str(p.relative_to(r)))
for p in (r/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'):
 if not git(['ls-files','--',str(p.relative_to(r))],text=True).strip():paths.add(str(p.relative_to(r)))
assert set(git(['diff','--cached','--name-only'],text=True).splitlines())<=paths
git(['-c','core.autocrlf=false','add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in sorted(paths)))
assert set(git(['diff','--cached','--name-only'],text=True).splitlines())<=paths
for p in paths:assert git(['show',':'+p])==(r/p).read_bytes(),p
git(['commit','-m','Retain native resume deadlines and correlate Elm terminal acknowledgments']);print(git(['rev-parse','HEAD'],text=True).strip())
