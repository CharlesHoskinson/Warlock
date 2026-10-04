"""Freeze unqualified effect source/build, strict adapter CPU and barrier replay."""
import hashlib,json,os,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
NAMES=['elm-window-geometry-effects-v42','elm-window-geometry-effect-adapter-v43','elm-geometry-effect-guards-v44','elm-geometry-effect-guards-v45','elm-window-geometry-effects-build-v47']
TARGET=ROOT/'component-manifest.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def check_file(p,h):assert sha(p)==h,str(p)
def verify(d):
 assert d['nativeAcceptance'] is False and d['completedRequirements']==[]
 for rel,e in d['files'].items():
  p=REPO/rel
  if 'symlink' in e:assert p.is_symlink() and os.readlink(p)==e['symlink'],rel
  else:assert p.is_file() and not p.is_symlink() and p.stat().st_size==e['size'] and stat.S_IMODE(p.stat().st_mode)==e['mode'] and sha(p)==e['sha256'],rel
 for path,digest in d['externalInputs'].items():check_file(path,digest)
if '--verify' in sys.argv:
 d=load(TARGET);verify(d);print(json.dumps({'passed':True,'manifest':str(TARGET),'files':len(d['files']),'nativeAcceptance':False}));raise SystemExit(0)
assert not TARGET.exists(),'Do not overwrite frozen proof'
external={}
build_path=ROOT/'qa/geometry-build-1791101058015687320/report.json';b=load(build_path)
assert b['passed'] and not b['nativeAcceptance'] and not b['missingSymbols']
check_file(b['binary'],b['binarySHA256'])
for rel,digest in b['inputs'].items():check_file(ROOT/rel,digest);check_file(build_path.parent/'inputs'/rel,digest)
for path,digest in b['sourceLineage'].items():check_file(path,digest)
for rel,digest in b['owningHeaders'].items():check_file(build_path.parent/'owning-headers'/rel,digest)
for section in ['dependencies','tools','linkedLibraries']:
 for path,digest in b[section].items():check_file(path,digest);external[path]=digest
for rel,digest in b['artifacts'].items():check_file(build_path.parent/rel,digest)
for field in ['parentManifest','parentBuildReport']:
 p=b[field];h=b[field+'SHA256'];check_file(p,h);external[p]=h
core=b['core'];check_file(core['path'],core['sha256']);external[core['path']]=core['sha256']
for field in ['buildReport','componentManifest']:
 p=core[field];h=core[field+'SHA256'];check_file(p,h);external[p]=h
# Bound complete upstream component, rather than only its pointer.
for e in load(core['componentManifest'])['files']:
 p=Path(core['inventoryBase'])/e['path']
 if 'symlink' in e:assert p.is_symlink() and os.readlink(p)==e['symlink']
 else:check_file(p,e['sha256']);external[str(p)]=e['sha256']
a_root=REPO/'implementation/elm-window-geometry-effect-adapter-v43';a_path=a_root/'qa/geometry-endpoint-1791100881855459295/report.json';a=load(a_path)
assert a['passed'] and a['checkCount']==176 and not a['nativeAcceptance'] and all(c['passed'] for c in a['checks'])
for rel,digest in a['inputs'].items():check_file(a_root/rel,digest);check_file(a_path.parent/'inputs'/rel,digest)
g_path=REPO/'implementation/elm-geometry-effect-guards-v45/qa/guards-1791100932615016400/report.json';g=load(g_path)
assert g['passed'] and not g['nativeAcceptance'] and len(g['checks'])==6 and all(c['passed'] for c in g['checks'])
check_file(g['source'],g['sourceSHA256'])
for rel,digest in g['artifacts'].items():check_file(g_path.parent/rel,digest)
f_path=REPO/'implementation/elm-geometry-effect-guards-v44/qa/guards-1791100888498206577/report.json';f=load(f_path)
assert not f['passed'] and 'unused parameter' in f['error']
files={}
for name in NAMES:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  if p==TARGET or '__pycache__' in p.parts:continue
  rel=str(p.relative_to(REPO))
  if p.is_symlink():files[rel]={'symlink':os.readlink(p)}
  elif p.is_file():files[rel]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
d={'schema':1,'passed':True,'nativeAcceptance':False,'completedRequirements':[],'scope':'Unaccepted V42 experimental effect source, V47 owning V28 compile/ABI closure, V43 strict adapter176CPU and V45 actual barrier50000operations/5 compiled mutants; V44 harness compile failure retained. V42 accepts experimental effects despite unavailable capabilities; this defect requires fresh V48 negotiated derivative before native use. No GUI or release qualification.','reports':{str(p.relative_to(REPO)):sha(p) for p in [build_path,a_path,g_path,f_path]},'files':files,'externalInputs':external}
verify(d);TARGET.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(TARGET),'files':len(files),'nativeAcceptance':False}))
