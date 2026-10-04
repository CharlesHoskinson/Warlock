import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'build-1791090562611157328'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((OUT/'report.json').read_text());review=json.loads((ROOT/'independent-review.json').read_text())
assert r['passed'] and r['checks']==12 and r['unsafeSizeGuardMutationRejected']
assert review['passed'] and review['buildReportSHA256']==digest(OUT/'report.json')
assert digest(r['binary'])==r['binarySHA256']
assert digest(OUT/'libhyprland_lib.a')==r['archiveSHA256']
for relative,value in r['inputs'].items():
 assert digest(ROOT/relative)==value,relative
 assert digest(OUT/'inputs'/relative)==value,relative
for path,value in r['dependencies'].items():assert digest(path)==value,path
for name in ('ancestorCore','ancestorArchive'):
 assert digest(r[name]['path'])==r[name]['sha256'],name
entries=[]
for p in sorted(ROOT.rglob('*')):
 if p.name=='component-manifest.json':continue
 if p.is_symlink():entries.append({'path':str(p.relative_to(ROOT)),'symlink':os.readlink(p)})
 elif p.is_file():entries.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p),'size':p.stat().st_size})
manifest={'schema':1,'passed':True,'scope':'Core buffer-selection CPU/build component','nativeAcceptance':False,'releaseAcceptance':False,'pluginPairQualified':False,'parentPresentationQualified':False,'buildReportSHA256':digest(OUT/'report.json'),'files':entries}
p=ROOT/'component-manifest.json';assert not p.exists();p.write_text(json.dumps(manifest,indent=2)+'\n');print(p,flush=True)
