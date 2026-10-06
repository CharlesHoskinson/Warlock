"""Hold actual changed GUI source/build/model bytes before native enrollment."""
import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path(__file__).resolve().parents[3];ROOT=REPO/'implementation/warlock-preview-provider-v56'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
 xs=list(ROOT.glob(pattern));assert len(xs)==1,xs;return xs[0]
bp=only('qa/build-*/report.json');mp=only('qa/check-*/report.json');b=json.loads(bp.read_text());m=json.loads(mp.read_text())
assert b['passed'] and len(b['commands'])==88 and all(x['exitCode']==0 for x in b['commands'])
for rel,h in b['inputs'].items():assert sha(ROOT/rel)==h,rel
for rel,h in b['artifacts'].items():assert sha(bp.parent/rel)==h,rel
for key in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[key].items():assert sha(Path(p))==row['sha256'],p
assert sha(bp.parent/'elm-host')==b['binarySHA256']
assert m['passed'] and m['compiledChecks']==36 and m['namedScenarios']==10 and len(m['coupledTraces'])==22 and sum(x['statesCompared'] for x in m['coupledTraces'])==564 and m['unsafeMutantsDetected']==3
for rel,h in m['inputs'].items():assert sha(ROOT/rel)==h,rel
for rel,h in m['artifacts'].items():assert sha(mp.parent/rel)==h,rel
names=['receiver-extension-physical-tests','catalog-enrollment-replay','window-catalog-admission-tests','metadata-privacy-replay','metadata-icon-physical-tests','backdrop-frame-tests','backdrop-fd-physical-tests','backdrop-source-coupled-decoder','backdrop-source-general-decoder','typed-backdrop-presenter-replay','backdrop-denial-tests','typed-backdrop-denial-replay','qa-reader-control-tests']
evidence={name:json.loads((bp.parent/(name+'.stdout')).read_text()) for name in names}
assert evidence['window-catalog-admission-tests']=={'passed':True,'checks':26,'nativeAcceptance':False,'fullReleaseAccepted':False}
assert evidence['qa-reader-control-tests']=={'passed':True,'checks':15}
metadataPath=REPO/'implementation/warlock-preview-provider-v56/qa/metadata-check-1791298415751045948/report.json'
metadataProof=json.loads(metadataPath.read_text());assert metadataProof['passed'] and metadataProof['namedScenarios']==8 and metadataProof['invariantSamples']==100 and len(metadataProof['coupledTraces'])==16
assert metadataProof['compiledBuild']=={'path':str(bp),'sha256':sha(bp)}
for rel,h in metadataProof['inputs'].items():assert sha(metadataPath.parents[2]/rel)==h,rel
for rel,h in metadataProof['artifacts'].items():assert sha(metadataPath.parent/rel)==h,rel
assert evidence['metadata-privacy-replay']['checks']==82 and evidence['metadata-icon-physical-tests']['checks']==74
catalogPath=ROOT/'qa/catalog-check-1791298415753594560/report.json';catalogProof=json.loads(catalogPath.read_text());assert catalogProof['passed'] and catalogProof['namedScenarios']==8 and catalogProof['invariantSamples']==100 and len(catalogProof['coupledTraces'])==16
assert catalogProof['compiledBuild']=={'path':str(bp),'sha256':sha(bp)}
for rel,h in catalogProof['inputs'].items():assert sha(ROOT/rel)==h,rel
for rel,h in catalogProof['artifacts'].items():assert sha(catalogPath.parent/rel)==h,rel
assert evidence['catalog-enrollment-replay']['passed'] and evidence['catalog-enrollment-replay']['checks']==60
assert evidence['receiver-extension-physical-tests']=={'passed':True,'checks':40,'nativeAcceptance':False,'fullReleaseAccepted':False}
failedMetadata=[REPO/'implementation/warlock-preview-provider-v43/qa/metadata-check-1791290742610835828/report.json'];failure=json.loads(failedMetadata[0].read_text());assert not failure['passed'] and failure['commands'][-1]['name']=='typecheck'
files={}
for p in sorted(ROOT.rglob('*')):
 rel=p.relative_to(ROOT)
 if any(part in {'__pycache__','elm-stuff','mutable-elm-home'} for part in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':True,'buildReport':str(bp),'modelReport':str(mp),'evidence':evidence,'metadataModelReport':str(metadataPath),'metadataModelReportSHA256':sha(metadataPath),'catalogModelReport':str(catalogPath),'catalogModelReportSHA256':sha(catalogPath),'retainedFailedMetadataModelReport':str(failedMetadata[0]),'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual full optimized GUI56 native Endpoint atomically extends same own receiver membership against already enrolled native scopes, preserving original epoch/old GIO readers. Imported subject actors at most256, original two actor default preserved; same shared2items128MiB8records4readers2views unchanged. Actual ASAN/UBSAN GIO40 checks prove own/foreign atomic membership, held original read continuation, native revoke denial, third capture capacity without fabricated job/refusal, retained byte charge/actor floors/original deadlines, actual consumer fence and physical destroy before exact ACK. Full88build/catalog60/decoder26/metadata82/GIO74 and selected coupled catalogue8/metadata8/demand10 retained. Failed55 missing consumer-completion test stimulus is preserved. No actual changedGUI56 native campaign, ordinary eligible capture/resource grant, hardware or full release acceptance; prior native101 qualifies GUI54 only.'},indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(manifest),'files':len(files),'commands':len(b['commands']),'modelScenarios':10,'privateControlChecks':15}))
