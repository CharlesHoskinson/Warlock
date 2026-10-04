import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];r=json.loads(p.read_text());assert r['passed'] and not r['missingSymbols'] and len(r['owningHeaders'])==694
assert sha(r['binary'])==r['binarySHA256'] and sha(r['core']['path'])==r['core']['sha256']
for section in ['dependencies','linkedLibraries','tools']:
 for path,wanted in r[section].items():assert sha(path)==wanted,path
for rel,wanted in r['inputs'].items():assert sha(ROOT/rel)==sha(p.parent/'inputs'/rel)==wanted,rel
for rel,wanted in r['owningHeaders'].items():assert sha(p.parent/'owning-headers'/rel)==wanted,rel
files={};symlinks={}
for f in sorted(ROOT.rglob('*')):
 if f.name=='build-pair-manifest.json':continue
 if f.is_symlink():symlinks[str(f.relative_to(ROOT))]=os.readlink(f)
 elif f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
m={'schema':1,'passed':True,'nativeAcceptance':False,'releaseAcceptance':False,'nativePair':{'core':r['core'],'plugin':{'path':r['binary'],'sha256':r['binarySHA256']}},'buildReport':str(p.relative_to(ROOT)),'buildReportSHA256':sha(p),'scope':'Fresh unchanged negotiated geometry authority against exact first-anchor core/694 captured owning headers; strong-symbol closure and QA legacy endpoints only; native acceptance separate','files':files,'symlinks':symlinks}
out=ROOT/'qa/build-pair-manifest.json';assert not out.exists();out.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'manifest':str(out),'sha256':sha(out),'files':len(files),'strongImports':r['strongUndefinedCount']}))
