import hashlib,json,resource,sys,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1]
report_path=Path(sys.argv[1]);report=json.loads(report_path.read_text());assert report['passed'] and report['nativeAcceptance'] is False
for name,digest in report['inputs'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
files={str(p.relative_to(s)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size,'mode':p.stat().st_mode&0o7777} for p in sorted(s.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
manifest={'sourceHeld':True,'nativeAcceptance':False,'scope':'Prepared source and protected CPU preflight only; independent source review/root native launch not executed','acceptedPreflight':str(report_path),'acceptedPreflightSHA256':hashlib.sha256(report_path.read_bytes()).hexdigest(),'files':files}
(s/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'sourceHeld':True,'manifest':str(s/'component-manifest.json'),'sha256':hashlib.sha256((s/'component-manifest.json').read_bytes()).hexdigest(),'nativeSourceSHA256':hashlib.sha256((s/'qa/native.py').read_bytes()).hexdigest()}))
