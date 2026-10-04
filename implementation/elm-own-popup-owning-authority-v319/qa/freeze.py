import hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
bp=ROOT/'qa/build-1791154808333780178/report.json';b=json.loads(bp.read_text());assert b['passed'] and not b['nativeAcceptance'] and not b['missingSymbols'] and len(b['owningHeaders'])==694
assert sha(b['binary'])==b['binarySHA256']
for rel,digest in b['inputs'].items():assert sha(ROOT/rel)==digest
for rel,digest in b['artifacts'].items():assert sha(bp.parent/rel)==digest
external={}
for key in ['dependencies','linkedLibraries','tools']:
 for path,digest in b[key].items():
  assert sha(path)==digest
  if not Path(path).is_relative_to(ROOT):external[path]=digest
core=b['core'];assert sha(core['path'])==core['sha256'] and sha(core['buildReport'])==core['buildReportSHA256']
external[core['path']]=core['sha256'];external[core['buildReport']]=core['buildReportSHA256']
mp=ROOT.parent/'elm-own-popup-xdg-grab-provenance-v307/component-manifest.json';assert sha(mp)=='335b15fb98e6276d55d011ceecf6450c9a81e19df2ef72db97377698b8029a13'
external[str(mp)]=sha(mp)
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
p=ROOT/'component-manifest.json';assert not p.exists()
p.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'installed':False,'scope':b['scope'],'buildReport':str(bp),'buildReportSHA256':sha(bp),'files':files,'external':external},indent=2)+'\n')
print(json.dumps({'held':True,'sha256':sha(p),'files':len(files),'external':len(external)}))
