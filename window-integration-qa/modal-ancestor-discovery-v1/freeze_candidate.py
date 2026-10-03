from pathlib import Path
import hashlib,json,os
B=Path(__file__).resolve().parent;Q=B.parent;files={};links={};sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(path,expected=None):
 value=sha(path)
 if expected is not None:assert value==expected,str(path)
 files[str(path)]=value
old=Q/'qt-modal-private-v8/frozen-inputs.json';add(old);packet=json.loads(old.read_text())
for row in packet['files']:add(row['path'],row['sha256'])
for row in packet['symlinks']:links[row['path']]=row['target']
for name,key in [('build-report.json','sourceDependencies'),('helper-report.json','dependencies')]:
 for path,value in json.loads((B/name).read_text())[key].items():add(path,value)
for name in ('report.json','qt/report.json'):add(Q/'qt-modal-private-v8/attempt-1'/name)
for p in B.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts and p.name!='frozen-inputs.json':add(p)
for path,target in links.items():assert Path(path).is_symlink() and os.readlink(path)==target
out=B/'frozen-inputs.json';assert not out.exists();out.write_text(json.dumps({'scope':'Press-only modal ancestor discovery candidate; no main install/load','inputs':dict(sorted(files.items())),'symlinks':links,'candidateBinarySHA256':sha(B/'native-candidate/hyprbars-v19-modal-candidate.so'),'quintNamed':23,'quintModels':3,'samplesPerModel':2000,'stepsPerSample':100,'seedArgument':'20260930','cppCoordinates':72,'cppCache':38,'pythonSourceChecks':7,'nativeExecuted':False,'mainLoaded':False},indent=2)+'\n');print(json.dumps({'inputs':len(files),'links':len(links),'manifestSHA256':sha(out)}))
