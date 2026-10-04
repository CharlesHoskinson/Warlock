import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];parent=s.parent/'elm-xdg-presented-landmark-native-v212';manifest=parent/'component-manifest.json';expected='73293f58e1799bd5a6f474075d2df17278b0a391da5551c5eb384cf76e4fa362';assert hashlib.sha256(manifest.read_bytes()).hexdigest()==expected
files={}
def verify(path,digest):
 path=Path(path);assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,str(path);files[str(path)]=digest
packet=json.loads(manifest.read_text());assert packet['sourceHeld'] and packet['nativeAcceptance'] is False
for name,row in packet['files'].items():verify(parent/name,row['sha256'])
for reportname in ['qa/test-1791132955386570598/report.json','qa/preflight-1791132853806964315/report.json']:
 path=parent/reportname;report=json.loads(path.read_text());assert report['passed']
 for name,digest in report['inputs'].items():verify(name,digest)
verify(manifest,expected)
source=parent/'qa/native.py';helper=parent/'qa/pixels.py';snapshot={'scope':'Read-only final held212 source and existing report-input integrity; no GUI/native rerun','nativeAcceptance':False,'sourceReadyForRootNativeReview':True,'files':files,'nativeSourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'captureHelperSHA256':hashlib.sha256(helper.read_bytes()).hexdigest(),'owningManifestSHA256':expected};(s/'reviewed-inputs.json').write_text(json.dumps(snapshot,indent=2)+'\n')
out=s/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps({'passed':True,'verifiedFiles':len(files),'owningManifestSHA256':expected,'scope':snapshot['scope'],'nativeAcceptance':False},indent=2)+'\n')
rows={str(p.relative_to(s)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size,'mode':p.stat().st_mode&0o7777} for p in sorted(s.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
(s/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'nativeAcceptance':False,'scope':snapshot['scope'],'files':rows},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(out/'report.json'),'nativeSHA256':snapshot['nativeSourceSHA256'],'helperSHA256':snapshot['captureHelperSHA256'],'reviewManifestSHA256':hashlib.sha256((s/'component-manifest.json').read_bytes()).hexdigest(),'verifiedFiles':len(files)}))
