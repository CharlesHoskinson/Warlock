"""Hold actual changed GUI source/build/model bytes before native enrollment."""
import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path(__file__).resolve().parents[3];ROOT=REPO/'implementation/warlock-preview-provider-v38'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
 xs=list(ROOT.glob(pattern));assert len(xs)==1,xs;return xs[0]
bp=only('qa/build-*/report.json');mp=only('qa/check-*/report.json');b=json.loads(bp.read_text());m=json.loads(mp.read_text())
assert b['passed'] and len(b['commands'])==77 and all(x['exitCode']==0 for x in b['commands'])
for rel,h in b['inputs'].items():assert sha(ROOT/rel)==h,rel
for rel,h in b['artifacts'].items():assert sha(bp.parent/rel)==h,rel
for key in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[key].items():assert sha(Path(p))==row['sha256'],p
assert sha(bp.parent/'elm-host')==b['binarySHA256']
assert m['passed'] and m['compiledChecks']==36 and m['namedScenarios']==10 and len(m['coupledTraces'])==22 and sum(x['statesCompared'] for x in m['coupledTraces'])==564 and m['unsafeMutantsDetected']==3
for rel,h in m['inputs'].items():assert sha(ROOT/rel)==h,rel
for rel,h in m['artifacts'].items():assert sha(mp.parent/rel)==h,rel
names=['backdrop-frame-tests','backdrop-fd-physical-tests','backdrop-source-coupled-decoder','backdrop-source-general-decoder','typed-backdrop-presenter-replay','backdrop-denial-tests','typed-backdrop-denial-replay','qa-reader-control-tests']
evidence={name:json.loads((bp.parent/(name+'.stdout')).read_text()) for name in names}
assert evidence['qa-reader-control-tests']=={'passed':True,'checks':15}
files={}
for p in sorted(ROOT.rglob('*')):
 rel=p.relative_to(ROOT)
 if any(part in {'__pycache__','elm-stuff','mutable-elm-home'} for part in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':True,'buildReport':str(bp),'modelReport':str(mp),'evidence':evidence,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Full shared owning GUI/private same-endpoint held reader and bounded undispatched Elm effects; native actual address reuse qualification remains required.'},indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(manifest),'files':len(files),'commands':len(b['commands']),'modelScenarios':10,'privateControlChecks':15}))
