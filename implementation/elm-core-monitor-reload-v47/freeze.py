import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=sorted(ROOT.glob('build-*/report.json'))[-1];r=json.loads(p.read_text());assert r['passed'] and r['unchangedArchiveMembers']==432
assert sha(r['binary'])==r['binarySHA256'] and sha(p.parent/'libhyprland_lib.a')==r['archiveSHA256']
for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==sha(p.parent/'inputs'/rel)==digest
for path,digest in r['dependencies'].items():assert sha(path)==digest,path
for entry in r['proofReports']:assert sha(entry['path'])==entry['sha256']
files=[]
out=ROOT/'component-manifest.json';assert not out.exists()
for f in sorted(ROOT.rglob('*')):
 if f==out:continue
 if f.is_symlink():files.append({'path':str(f.relative_to(ROOT)),'symlink':os.readlink(f)})
 elif f.is_file():files.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f),'size':f.stat().st_size})
out.write_text(json.dumps({'schema':1,'passed':True,'nativeAcceptance':False,'releaseAcceptance':False,'scope':'Owning core compile and bounded model/fragment dispatch proof only','buildReport':str(p),'buildReportSHA256':sha(p),'files':files},indent=2)+'\n');print(out)
