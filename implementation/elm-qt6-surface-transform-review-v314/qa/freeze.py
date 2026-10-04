import hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rp=ROOT/'qa/verify-1791153959763343843/report.json';r=json.loads(rp.read_text());assert r['passed'] and not r['nativeAcceptance']
pins=json.loads((rp.parent/'pins.json').read_text());assert sha(rp.parent/'pins.json')==r['pinsSHA256']
for p,digest in pins.items():assert sha(p)==digest
for p,digest in r['sourceInputs'].items():assert sha(p)==digest and sha(rp.parent/'inputs'/Path(p).name)==digest
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
p=ROOT/'component-manifest.json';assert not p.exists()
p.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':r['scope'],'report':str(rp),'reportSHA256':sha(rp),'files':files,'external':pins},indent=2)+'\n')
print(json.dumps({'held':True,'sha256':sha(p),'files':len(files),'external':len(pins)}))
