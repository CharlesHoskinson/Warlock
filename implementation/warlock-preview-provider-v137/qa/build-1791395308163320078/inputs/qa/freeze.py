"""Hold the full shared provider's source/build/model evidence; no native claim."""
import hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
builds=list(ROOT.glob('qa/build-*/report.json'))
models=list(ROOT.glob('qa/check-*/report.json'))
assert len(builds)==len(models)==1
build=json.loads(builds[0].read_text());model=json.loads(models[0].read_text())
assert build['passed'] and all(row['exitCode']==0 for row in build['commands'])
assert model['passed'] and model['namedScenarios']==10 and len(model['coupledTraces'])==22 and model['unsafeMutantsDetected']==3
for name,digest in build['inputs'].items():assert sha(ROOT/name)==digest,name
for group in ['compilerDependencies','linkedLibraries','tools']:
    for name,row in build[group].items():assert sha(pathlib.Path(name))==row['sha256'],name
assert sha(builds[0].parent/'elm-host')==build['binarySHA256']
for name,digest in build['artifacts'].items():assert sha(builds[0].parent/name)==digest,name
for name,digest in model['inputs'].items():assert sha(ROOT/name)==digest,name
evidence={}
for name in ['backdrop-frame-tests','backdrop-fd-physical-tests','backdrop-source-coupled-decoder','backdrop-source-general-decoder','typed-backdrop-presenter-replay','backdrop-denial-tests','typed-backdrop-denial-replay']:
    value=json.loads((builds[0].parent/(name+'.stdout')).read_text());assert value['passed'];evidence[name]=value
files={}
for p in sorted(ROOT.rglob('*')):
    relative=p.relative_to(ROOT)
    if any(part in {'mutable-elm-home','elm-stuff','__pycache__'} for part in relative.parts):continue
    if p==ROOT/'component-manifest.json' or not p.is_file():continue
    assert not p.is_symlink(),str(p)
    files[str(relative)]={'sha256':sha(p),'size':p.stat().st_size}
manifest={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':True,
    'buildReport':str(builds[0]),'modelReport':str(models[0]),'evidence':evidence,'files':files,
    'nativeAcceptance':False,'fullReleaseAccepted':False,
    'scope':'Full GUI519-derived explicit generated native source/FD4 mapping and immutable Elm presenter; original source/family ownership retained. Requires actual owning native campaign.'}
(ROOT/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'manifest':str(ROOT/'component-manifest.json')}))
