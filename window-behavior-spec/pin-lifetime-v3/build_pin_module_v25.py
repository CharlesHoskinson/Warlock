import hashlib,json,subprocess,time
from pathlib import Path
p=Path(__file__).resolve().parent;n=p/'native-candidate'
sources=[*n.glob('*.cpp'),*n.glob('*.hpp'),n/'Makefile'];hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in sources}
c=['/usr/bin/make','-B','-j1','CXX=/usr/bin/clang++'];r=subprocess.run(c,cwd=n,text=True,capture_output=True,timeout=300)
record=dict(command=c,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,sourceSHA256=hashes,sourceUnchangedDuringBuild=all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in hashes.items()),nativeExecuted=False,mainWrites=False)
b=n/'hyprbars-v25-pin-stacking-candidate.so'
if r.returncode==0:record['binarySHA256']=hashlib.sha256(b.read_bytes()).hexdigest()
f=p/('pin-v25-module-build-report.json'if r.returncode==0 else f'pin-v25-module-build-failure-{time.time_ns()}.json');f.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(artifact=str(f),returncode=r.returncode,sourceUnchanged=record['sourceUnchangedDuringBuild'],binarySHA256=record.get('binarySHA256'),stderr=r.stderr[-7000:])));raise SystemExit(r.returncode)
