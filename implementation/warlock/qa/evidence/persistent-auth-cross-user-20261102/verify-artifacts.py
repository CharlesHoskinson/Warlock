import hashlib,json,re,subprocess,os
from pathlib import Path
base=Path(__file__).resolve().parent
stage=Path('/home/charl/warlock-mvp-20261101T1058Z')
def fact(path):
 p=Path(path);st=p.stat()
 with p.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
 return dict(path=str(p),resolvedPath=str(p.resolve()),device=str(st.st_dev),inode=str(st.st_ino),size=str(st.st_size),sha256=digest)
m=json.loads((base/'source-manifest.json').read_text())
for name,expected in m['completeHaskellSources'].items():assert fact(stage/'source'/name)['sha256']==expected,name
result=dict(scope='Compiled and linked guest artifacts; not a GUI or native acceptance observation',originalBuildExitStatus=int((base/'build.exit').read_text().strip()),artifacts={},documents={},sourceInputCount=len(m['completeHaskellSources']),sourceInputsStable=True,nativeAccepted=False,releaseAccepted=False)
for name in ['credential-peer-child','persistent-bootstrap-controls']:
 p=base/'assets'/name;assert p.is_file() and os.access(p,os.X_OK)
 dynamic=subprocess.run(['readelf','-d',str(p)],capture_output=True,text=True,check=True)
 linked=subprocess.run(['ldd',str(p)],capture_output=True,text=True,check=True)
 assert 'not found' not in linked.stdout
 paths=set(re.findall(r'=> (/[^\s]+)',linked.stdout))
 paths.update(re.findall(r'^\s*(/[^\s]+)\s+\(',linked.stdout,re.M))
 assert paths
 result['artifacts'][name]=dict(image=fact(p),dynamicSection=dynamic.stdout,ldd=linked.stdout,readelfExit=dynamic.returncode,lddExit=linked.returncode,dependencies=[fact(v) for v in sorted(paths)])
(base/'guest-artifacts.json').write_text(json.dumps(result,indent=2))
print(json.dumps(dict(sourceInputCount=result['sourceInputCount'],artifacts={name:dict(sha256=value['image']['sha256'],dependencies=len(value['dependencies'])) for name,value in result['artifacts'].items()},documents={name:value['sha256'] for name,value in result['documents'].items()},verificationExit=0,nativeAccepted=False)))
