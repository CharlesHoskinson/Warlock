"""Commit only held preview-lane source/evidence, preserving each raw blob."""
import hashlib,json,pathlib,subprocess,sys,resource
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
assert git(['rev-parse','HEAD'],text=True).strip()=='915ea9ecb97196477a6deae90d8cf87b520bd0d1'
existingStage=set(git(['diff','--cached','--name-only'],text=True).splitlines())
paths=set()
p=REPO/'implementation/warlock-preview-provider-v51/component-manifest.json'
held=json.loads(p.read_text());assert held['passed'] and not held['nativeAcceptance'] and len(held['files'])==918
paths.add(str(p.relative_to(REPO)))
for rel,row in held['files'].items():
    q=p.parent/rel;assert q.is_file() and not q.is_symlink() and sha(q)==row['sha256'] and q.stat().st_size==row['size'],q
    paths.add(str(q.relative_to(REPO)))
validator=REPO/'openspec/changes/warlock-preview-product-enrollment/qa/validate-1791295182643554599/report.json'
v=json.loads(validator.read_text());assert v['passed'] and v['frozenBaseline']==[242,417] and not v['nativeAcceptance']
for path,h in v['inputs'].items():assert sha(pathlib.Path(path))==h,path
for root in ['docs/warlock-preview/v61','openspec/changes/warlock-preview-product-enrollment','docs/warlock-repository/v50/publication']:
    for p in (REPO/root).rglob('*'):
        if '__pycache__' in p.parts:continue
        assert not p.is_symlink(),p
        if p.is_file():paths.add(str(p.relative_to(REPO)))
lane=sorted(str(p.relative_to(REPO)) for p in (REPO/'docs/elm-roadmap/delivery/build-loop-events').glob('*--f6779148-8f5d-4bdf-8a0f-044184e486f2--*.json'))
tracked=set(git(['ls-tree','-r','--name-only','HEAD','--',*lane],text=True).splitlines());paths.update(set(lane)-tracked)
assert existingStage<=paths
assert all((REPO/p).stat().st_size<100*1024*1024 for p in paths)
git(['-c','core.autocrlf=false','add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in sorted(paths)))
staged=set(git(['diff','--cached','--name-only','-z']).decode().rstrip('\0').split('\0'));assert staged<=paths and staged,(len(staged),len(paths))
for unchanged in paths-staged:assert git(['show','HEAD:'+unchanged])==(REPO/unchanged).read_bytes(),unchanged
batch=subprocess.Popen(['git','cat-file','--batch'],cwd=REPO,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
try:
    for line in git(['ls-files','--stage','-z','--',*sorted(paths)]).split(b'\0'):
        if not line:continue
        metadata,name=line.split(b'\t',1);mode,oid,stage=metadata.decode().split();assert stage=='0' and mode in ['100644','100755']
        batch.stdin.write((oid+'\n').encode());batch.stdin.flush();header=batch.stdout.readline().decode().split();assert header[:2]==[oid,'blob'];raw=batch.stdout.read(int(header[2]));assert batch.stdout.read(1)==b'\n';assert raw==(REPO/name.decode()).read_bytes(),name
finally:
    batch.stdin.close();assert batch.wait()==0
git(['commit','-m','Add strict native window catalog for ordinary preview enrollment'])
print(json.dumps({'sourceCommit':git(['rev-parse','HEAD'],text=True).strip(),'ownedPaths':len(staged),'verifiedHeldPaths':len(paths),'rawBytesVerified':True}))
