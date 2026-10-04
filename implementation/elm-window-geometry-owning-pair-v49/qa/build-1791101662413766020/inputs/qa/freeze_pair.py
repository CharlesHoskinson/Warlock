"""Freeze the exact V48 source/V40 owning core plugin compile pair."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert len(sys.argv)==2,'Pass the exact accepted report path'
p=Path(sys.argv[1]).resolve();assert p.parent.parent==ROOT/'qa' and p.parent.name.startswith('build-')
b=json.loads(p.read_text());assert b['passed'] and b['nativeAcceptance'] is False and not b['missingSymbols']
for rel,value in b['inputs'].items():assert sha(ROOT/rel)==sha(p.parent/'inputs'/rel)==value,rel
core=b['core'];assert sha(core['path'])==core['sha256'] and sha(core['buildReport'])==core['buildReportSHA256']
assert sha(b['coreDescriptor'])==b['coreDescriptorSHA256']
for rel,value in b['owningHeaders'].items():assert sha(Path(core['buildReport']).parent/'owning-headers'/rel)==sha(p.parent/'owning-headers'/rel)==value,rel
assert len(b['owningHeaders'])==691
for section in ['dependencies','coreDependencies','coreLinkDependencies','tools','linkedLibraries']:
 for path,value in b[section].items():assert sha(path)==value,path
for rel,value in b['artifacts'].items():assert sha(p.parent/rel)==value,rel
for name in ['coreClosureReport','coreConsumerAudit','coreLimitsReport','linkClosureReport','parentBuildReport']:
 assert sha(b[name])==b[name+'SHA256'],name
assert sha(b['parentManifest'])==b['parentManifestSHA256']
assert sha(core['componentManifest'])==core['componentManifestSHA256']
m=json.loads(Path(core['componentManifest']).read_text());assert m['passed'] and len(m['files'])==1553
for entry in m['files']:
 path=Path(core['inventoryBase'])/entry['path']
 if 'symlink' in entry:assert path.is_symlink() and str(path.readlink())==entry['symlink'],str(path)
 else:assert path.is_file() and not path.is_symlink() and path.stat().st_size==entry['size'] and sha(path)==entry['sha256'],str(path)
upstream=b['sourceLineage']
for rel,value in upstream['sourceFiles'].items():assert sha(Path(upstream['source'])/rel)==sha(ROOT/rel)==value,rel
assert sha(b['binary'])==b['binarySHA256']
descriptor=dict(json.loads(Path(b['coreDescriptor']).read_text()))
descriptor.update(scope='Exact held V48 geometry source compiled against frozen V40 owning core and 691 captured headers; no loading, native operation, model or menu acceptance',installed=False,nativeAcceptance=False,plugin={'path':b['binary'],'sha256':b['binarySHA256']},pluginBuildReport=str(p),pluginBuildReportSHA256=sha(p),linkClosureReport=b['linkClosureReport'],linkClosureReportSHA256=b['linkClosureReportSHA256'],coreComponentManifest=core['componentManifest'],coreComponentManifestSHA256=core['componentManifestSHA256'])
d=ROOT/'native-build-report.json';assert not d.exists();d.write_text(json.dumps(descriptor,indent=2)+'\n')
files={}
for path in sorted(ROOT.rglob('*')):
 if path.is_file() and not path.is_symlink():
  path.chmod(stat.S_IMODE(path.stat().st_mode)&~0o222);files[str(path.relative_to(ROOT))]=sha(path)
manifest={'schema':1,'passed':True,'scope':descriptor['scope'],'nativeAcceptance':False,'parentPresentationQualified':False,'releaseAcceptance':False,'nativePair':{'core':core,'plugin':descriptor['plugin']},'buildReport':str(p.relative_to(ROOT)),'buildReportSHA256':sha(p),'sourceLineage':upstream,'upstreamSHA256':sha(ROOT/'upstream.json'),'files':files}
target=ROOT/'qa/build-pair-manifest.json';assert not target.exists();target.write_text(json.dumps(manifest,indent=2)+'\n');target.chmod(0o444)
print(json.dumps({'passed':True,'manifest':str(target),'manifestSHA256':sha(target),'descriptor':str(d),'pluginSHA256':b['binarySHA256'],'coreSHA256':core['sha256'],'files':len(files)}),flush=True)
