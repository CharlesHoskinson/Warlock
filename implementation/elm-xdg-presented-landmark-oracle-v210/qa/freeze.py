import hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];parent=s.parent/'elm-xdg-presented-landmark-oracle-v208'
origin=json.loads((s/'origin.json').read_text());assert hashlib.sha256((parent/'component-manifest.json').read_bytes()).hexdigest()==origin['parentManifestSHA256']
packet=json.loads((parent/'component-manifest.json').read_text())
for name,row in packet['files'].items():assert hashlib.sha256((parent/name).read_bytes()).hexdigest()==row['sha256'],name
assert (s/'qa/original-test.py').read_bytes()==(parent/'qa/test.py').read_bytes()
original=s/'qa/test-1791132578072609671/report.json';accepted=s/'qa/test-1791132578058133747/report.json';mutants=s/'qa/mutations-1791132524188492751/report.json'
for p in [original,accepted,mutants]:assert json.loads(p.read_text())['passed']
a=json.loads(accepted.read_text());m=json.loads(mutants.read_text());assert len(a['checks'])==64 and len(json.loads(original.read_text())['checks'])==24
assert len(m['controls'])==4 and all(row['rejected'] for row in m['controls'])
for p,row,key in [(s/'oracle.py',a,'sourceSHA256'),(s/'qa/test.py',a,'testSourceSHA256'),(s/'oracle.py',m,'sourceSHA256'),(s/'qa/test.py',m,'testSourceSHA256')]:assert hashlib.sha256(p.read_bytes()).hexdigest()==row[key]
files={str(p.relative_to(s)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size,'mode':p.stat().st_mode&0o7777} for p in sorted(s.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
manifest={'sourceHeld':True,'nativeAcceptance':False,'releaseAcceptance':False,'scope':'Strict metadata correction and synthetic CPU only; independent final review pending','originalChecks':24,'newChecks':64,'rejectedSourceControls':4,'acceptedReport':str(accepted.resolve()),'mutationsReport':str(mutants.resolve()),'files':files}
(s/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'sourceHeld':True,'manifestSHA256':hashlib.sha256((s/'component-manifest.json').read_bytes()).hexdigest(),'sourceSHA256':hashlib.sha256((s/'oracle.py').read_bytes()).hexdigest(),'files':len(files)}))
