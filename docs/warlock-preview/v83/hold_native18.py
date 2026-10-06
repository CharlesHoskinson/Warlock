"""Freeze exact native18 build/classifier evidence; socket qualification open."""
import hashlib, json, pathlib, resource, stat, sys
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root=repo/'implementation/warlock-family-style-crop-capture-v18'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
build=next(root.glob('qa/build-*/report.json'));proof=json.loads(build.read_text())
assert proof['passed'] and not proof['missingSymbols']
assert all(row['exitCode']==0 for row in proof['commands'])
for name,value in proof['inputs'].items():assert sha(root/name)==value,name
for section in ['dependencies','linkedLibraries']:
 for name,value in proof[section].items():assert sha(pathlib.Path(name))==value,name
assert sha(pathlib.Path(proof['binary']))==proof['binarySHA256']
model=next((repo/'docs/warlock-preview/v83').glob('retirement-check-*/report.json'));checks=json.loads(model.read_text())
assert checks['passed'] and checks['namedScenarios']==8 and len(checks['coupledTraces'])==20 and checks['statesCompared']==438 and checks['unsafeMutantsDetected']==2
for name,value in checks['inputs'].items():assert sha(pathlib.Path(name))==value,name
for name,value in checks['artifacts'].items():assert sha(model.parent/name)==value,name
assert checks['fullBuild']=={'path':str(build),'sha256':sha(build)}
files={};links={}
for path in sorted(root.rglob('*')):
 rel=path.relative_to(root)
 if '__pycache__' in rel.parts:continue
 if path.is_symlink():links[str(rel)]=str(path.readlink());continue
 if path.is_file():files[str(rel)]={'kind':'file','sha256':sha(path),'size':path.stat().st_size,'mode':oct(stat.S_IMODE(path.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'passed':True,
 'files':files,'localBuildLinks':links,'buildReport':str(build),'modelReport':str(model),
 'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,
 'scope':'Current native18 module compiled against unchanged owning core16 with strong symbol closure. Eight selected classifier cases/20 synthetic membership traces/438 states/two unsafe native mutants pass. Authenticated socket, actual native membership and actor removal qualification remain open.'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),
 ['PROGRESS public58 verified027373f sourcebc11/receipt23c4; fullGUI81/native1182467/284normal all2429stable retained. Native18 retirement observation held actual module compile/core16 strong closure; classifier8/20/438states/2mutants. Next full native119 authenticated live/minimized/future/foreign/closed incarnation controls without altering original118 paths/deadlines; actor erasure/ordinary capture/fullrelease stillopen.'],
 'progress',[str(manifest.relative_to(repo))]))
