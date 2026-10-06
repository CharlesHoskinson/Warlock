"""Hold GUI61 original-intent admission and actual allocator/model evidence."""
import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path('/home/hoskinson/omarchy-windows-parity');ROOT=REPO/'implementation/warlock-preview-provider-v61';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
 rows=list(ROOT.glob(pattern));assert len(rows)==1,rows;return rows[0]
def verify(path):
 data=json.loads(path.read_text());assert data['passed'],path
 for rel,h in data['inputs'].items():assert sha(ROOT/rel)==h,rel
 for rel,h in data.get('artifacts',{}).items():assert sha(path.parent/rel)==h,rel
 return data
bp=only('qa/build-*/report.json');b=verify(bp);assert len(b['commands'])==92 and all(row['exitCode']==0 for row in b['commands'])
for section in ['compilerDependencies','linkedLibraries','tools']:
 for name,row in b[section].items():assert sha(Path(name))==row['sha256'],name
assert sha(bp.parent/'elm-host')==b['binarySHA256']
reports={};proofs={}
for key,pattern,names,traces in [('modelReport','qa/check-*/report.json',10,22),('metadataModelReport','qa/metadata-check-*/report.json',8,16),('catalogModelReport','qa/catalog-check-*/report.json',8,16),('deliveryModelReport','qa/delivery-check-*/report.json',6,16),('intentModelReport','qa/intent-check-*/report.json',6,16)]:
 path=only(pattern);d=verify(path);assert d['namedScenarios']==names and len(d['coupledTraces'])==traces
 reports[key]=str(path);proofs[key]=d
assert proofs['modelReport']['compiledChecks']==36 and proofs['modelReport']['unsafeMutantsDetected']==3 and sum(x['statesCompared'] for x in proofs['modelReport']['coupledTraces'])==564
assert proofs['metadataModelReport']['compiledBuild']=={'path':str(bp),'sha256':sha(bp)} and sum(x['statesCompared'] for x in proofs['metadataModelReport']['coupledTraces'])==210
assert proofs['catalogModelReport']['compiledBuild']=={'path':str(bp),'sha256':sha(bp)} and sum(x['statesCompared'] for x in proofs['catalogModelReport']['coupledTraces'])==214
assert proofs['deliveryModelReport']['invariantSamples']==150 and proofs['deliveryModelReport']['unsafeMutantsDetected']==2
assert proofs['intentModelReport']['statesCompared']==363 and proofs['intentModelReport']['unsafeMutantsDetected']==2 and proofs['intentModelReport']['invariantSamples']==150
names=['imported-admission-tests','receiver-extension-physical-tests','delivery-extension-physical-tests','catalog-enrollment-replay','window-catalog-admission-tests','metadata-privacy-replay','metadata-icon-physical-tests','backdrop-frame-tests','backdrop-fd-physical-tests','backdrop-source-coupled-decoder','backdrop-source-general-decoder','typed-backdrop-presenter-replay','backdrop-denial-tests','typed-backdrop-denial-replay','qa-reader-control-tests']
evidence={name:json.loads((bp.parent/(name+'.stdout')).read_text()) for name in names}
assert evidence['imported-admission-tests']=={'passed':True,'checks':27,'nativeAcceptance':False,'fullReleaseAccepted':False}
assert evidence['receiver-extension-physical-tests']['checks']==40 and evidence['delivery-extension-physical-tests']['checks']==49 and evidence['catalog-enrollment-replay']['checks']==60 and evidence['metadata-privacy-replay']['checks']==82 and evidence['metadata-icon-physical-tests']['checks']==74 and evidence['qa-reader-control-tests']['checks']==15
for p in [REPO/'implementation/warlock-preview-provider-v57/component-manifest.json',REPO/'implementation/warlock-preview-provider-v58/component-manifest.json',REPO/'implementation/warlock-preview-provider-v59/component-manifest.json']:assert json.loads(p.read_text())['sourceHeld']
files={}
for p in sorted(ROOT.rglob('*')):
 rel=p.relative_to(ROOT)
 if any(part in {'__pycache__','elm-stuff','mutable-elm-home'} for part in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':True,'buildReport':str(bp),**reports,'evidence':evidence,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Full optimized GUI61 build92 and native ImportedIntentLedger/ImportedClients.tryStart preserving exact original native subject/binding/clock/publication/lease/deadline. Capacity and expiry carry no invented job or proof; actual rejected job/ownership retained pending C/frontend reconciliation. Actual allocator27 plus selected intent6/150samples/16traces363states/2unsafe mutants coupled to real Ledger and Coordinator/Broker with synthetic native scopes/clocks. All original demand/delivery/catalog/metadata checks retained. No GUI61 native campaign or ordinary eligible product capture/hardware/full release acceptance.'},indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(manifest),'files':len(files),'buildCommands':92,'intentControls':27,'intentStates':proofs['intentModelReport']['statesCompared']}))
