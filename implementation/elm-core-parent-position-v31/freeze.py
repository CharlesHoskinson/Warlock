"""Freeze the reviewed single-object build and byte-preserved ancestor archive."""
import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent
OUT=sorted(ROOT.glob('build-*/report.json'))[-1].parent
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((OUT/'report.json').read_text())
assert r['passed'] and r['unsafeRawSizeMutationRejected'] and r['unsafeParentRemapMutationRejected'] and r['checks']>50000 and r['parentPositionChecks']>60000
assert digest(r['binary'])==r['binarySHA256'] and digest(OUT/'libhyprland_lib.a')==r['archiveSHA256']
for rel,sha in r['inputs'].items():assert digest(ROOT/rel)==digest(OUT/'inputs'/rel)==sha,rel
for p,sha in r['dependencies'].items():assert digest(p)==sha,p
for name in ['ancestorCore','ancestorArchive']:assert digest(r[name]['path'])==r[name]['sha256']
entries=[]
for p in sorted(ROOT.rglob('*')):
 if p.name=='component-manifest.json':continue
 if p.is_symlink():entries.append({'path':str(p.relative_to(ROOT)),'symlink':os.readlink(p)})
 elif p.is_file():entries.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p),'size':p.stat().st_size})
p=ROOT/'component-manifest.json';assert not p.exists()
p.write_text(json.dumps({'schema':1,'passed':True,'scope':'Parent output/normalized-position routing and replay CPU/incremental owning core build only',
 'nativeAcceptance':False,'releaseAcceptance':False,'pluginPairQualified':False,'buildReport':str(OUT/'report.json'),
 'buildReportSHA256':digest(OUT/'report.json'),'files':entries},indent=2)+'\n')
print(p)
