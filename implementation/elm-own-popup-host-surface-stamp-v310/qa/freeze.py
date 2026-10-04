import hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
bp=ROOT/'qa/build-1791153652664233159/report.json';b=json.loads(bp.read_text())
assert b['passed'] and not b['nativeAcceptance'] and len(b['commands'])==14
assert all(c['exitCode']==0 for c in b['commands'])
assert sha(bp.parent/'host')==b['binarySHA256']
for rel,digest in b['inputs'].items():assert sha(ROOT/rel)==digest
for rel,digest in b['artifacts'].items():assert sha(bp.parent/rel)==digest
external={}
for key in ['dependencies','tools','linkedLibraries']:
 for path,digest in b[key].items():
  assert sha(path)==digest
  if not Path(path).is_relative_to(ROOT):external[path]=digest
origin=json.loads((ROOT/'origin.json').read_text());assert sha(origin['manifest'])==origin['manifestSHA256']
ancestor=Path(origin['ancestor'])
for p in (ROOT/'native').glob('*'):
 if not p.is_file() or p.name in ['host.c','shared-host.c'] or p.name.startswith('popup-native-'):continue
 assert p.read_bytes()==(ancestor/'native'/p.name).read_bytes()
external[origin['manifest']]=origin['manifestSHA256']
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
mp=ROOT/'component-manifest.json';assert not mp.exists()
mp.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'installed':False,
 'scope':'Trusted host read-only surface stamp diagnostic compile/kernel/identity/inherited C checks; no production grant/GUI retirement proof',
 'buildReport':str(bp),'buildReportSHA256':sha(bp),'files':files,'external':external},indent=2)+'\n')
print(json.dumps({'held':True,'manifest':str(mp),'sha256':sha(mp),'files':len(files),'external':len(external)}))
