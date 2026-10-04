import hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=sorted(ROOT.glob('build-*/report.json'))[-1];r=json.loads(p.read_text());assert r['passed'] and r['unchangedArchiveMembers']==432 and len(r['rebuiltArchiveMembers'])==1 and r['existingPublicHeadersUnchanged'] and r['geometryAndReloadArchivePayloadsPreserved']
for rel,h in r['inputs'].items():assert sha(ROOT/rel)==sha(p.parent/'inputs'/rel)==h
for rel,h in r['owningHeaders'].items():assert sha(p.parent/'owning-headers'/rel)==h
for name in ['dependencies','tools','linkDependencies','linkedLibraries']:
 for path,h in r[name].items():assert sha(path)==h,path
assert sha(r['binary'])==r['binarySHA256']
files={}
for f in sorted(ROOT.rglob('*')):
 if f.name=='component-manifest.json':continue
 assert not f.is_symlink(),str(f)
 if f.is_file():files[str(f.relative_to(ROOT))]={'sha256':sha(f),'size':f.stat().st_size}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'releaseAcceptance':False,'scope':'New first live parent device/output anchor hit-test compile with full merged geometry73 headers; 432 payloads/694public-private captured headers retained; native qualification separate','buildReport':str(p),'buildReportSHA256':sha(p),'files':files}
out=ROOT/'component-manifest.json';assert not out.exists();out.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'manifest':str(out),'sha256':sha(out),'files':len(files)}))
