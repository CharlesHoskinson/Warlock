"""Freeze compile-only core/plugin tuple for subsequent serial native execution."""
import hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Protected launcher required'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
build_path=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
for relative,digest in build['inputs'].items():assert sha(ROOT/relative)==digest,relative
for path,digest in build['dependencies'].items():assert sha(path)==digest,path
core=json.loads((ROOT/'native-build-report.json').read_text());assert sha(core['buildReport'])==core['buildReportSHA256'];receipt=json.loads(Path(core['buildReport']).read_text());assert receipt['passed']
core_root=Path(core['buildReport']).parents[1]
for relative,digest in receipt['sources'].items():assert sha(core_root/'candidate'/relative)==digest,relative
for name in ('SceneModal.hpp','WindowPolicy.hpp'):
 assert sha(ROOT/'candidate'/name)==sha(core_root/'candidate'/name),name
for path,digest in receipt['dependencies'].items():assert sha(path)==digest,path
assert sha(build['binary'])==build['binarySHA256'] and sha(build['core']['path'])==build['core']['sha256']
manifest={'passed':True,'scope':'Exact owning core/plugin compile and source closure only; native acceptance pending','nativePair':{'core':build['core'],'plugin':{'path':build['binary'],'sha256':build['binarySHA256']}},'buildReport':str(build_path.relative_to(ROOT)),'buildReportSHA256':sha(build_path),'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='build-pair-manifest.json'}}
assert not (ROOT/'qa/build-pair-manifest.json').exists(),'Preserve prior frozen packet'
(ROOT/'qa/build-pair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Exact compile tuple frozen; no native acceptance claimed')
