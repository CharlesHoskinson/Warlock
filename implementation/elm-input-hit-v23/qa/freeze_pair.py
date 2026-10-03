"""Freeze fresh input-hit core with unchanged, revalidated owning plugin ABI."""
import hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'elm-surface-facts-v20'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((OLD/'qa/slice-manifest.json').read_text());assert prior['passed']
for rel,digest in prior['files'].items():assert sha(OLD/rel)==digest,rel
pair=json.loads((OLD/'qa/build-pair-manifest.json').read_text())
plugin=json.loads((OLD/pair['buildReport']).read_text());assert plugin['passed']
for path,digest in plugin['dependencies'].items():assert sha(path)==digest,path
for name in ['SceneTrace.hpp','WindowPolicy.hpp','SceneModal.hpp']:assert sha(ROOT/'candidate'/name)==sha(OLD/'candidate'/name),name
build_path=sorted(ROOT.glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
for rel,digest in build['sources'].items():assert sha(ROOT/'candidate'/rel)==digest,rel
for path,digest in build['dependencies'].items():assert sha(path)==digest,path
assert sha(build['binary'])==build['binarySHA256']
assert sha(pair['nativePair']['plugin']['path'])==pair['nativePair']['plugin']['sha256']
assert build['owningVersionHeaderSHA256']==pair['nativePair']['core']['versionHeaderSHA256']
core={'path':build['binary'],'sha256':build['binarySHA256'],'versionHeaderSHA256':build['owningVersionHeaderSHA256']}
(ROOT/'native-build-report.json').write_text(json.dumps({'result':'pass','binary':build['binary'],'sha256':build['binarySHA256'],'buildReport':str(build_path),'buildReportSHA256':sha(build_path)},indent=2)+'\n')
manifest={'passed':True,'scope':'Fresh input-hit core; unchanged plugin/header ABI revalidated against owning V20 compile dependencies; native acceptance pending','nativePair':{'core':core,'plugin':pair['nativePair']['plugin']},'ancestorSliceManifestSHA256':sha(OLD/'qa/slice-manifest.json'),'buildReport':str(build_path.relative_to(ROOT)),'buildReportSHA256':sha(build_path),'files':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/build-pair-manifest.json'}}
(ROOT/'qa/build-pair-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Fresh input-hit core/unchanged owning ABI pair frozen')
