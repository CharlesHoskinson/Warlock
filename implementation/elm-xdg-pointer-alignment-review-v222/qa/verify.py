import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parents[1]; base=root.parent
owner=base/'elm-xdg-pointer-alignment-native-v219'; manifest=owner/'component-manifest.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest()=='bec46ee86dd120a919197148436d6c7ab2f517d0c7dff5494e6214d737aada3f'
rows={}
def add(p,sha=None,size=None):
 assert p.is_file() and not p.is_symlink(),str(p)
 data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
 if sha is not None: assert digest==sha,str(p)
 if size is not None: assert len(data)==size,str(p)
 rows[str(p)]={'sha256':digest,'size':len(data)}
add(manifest)
for rel,row in json.loads(manifest.read_text())['files'].items():add(owner/rel,row['sha256'],row['size'])
for path,sha in json.loads((owner/'pointer-pin.json').read_text())['files'].items():add(Path(path),sha)
for path,sha in json.loads((owner/'pointer-pin.json').read_text())['manifests'].items():
 m=Path(path)/'component-manifest.json';add(m,sha)
 for rel,row in json.loads(m.read_text())['files'].items():add(Path(path)/rel,row['sha256'],row['size'])
b82=base/'elm-seat-burst-fixture-fixed-v82/build-1791106310522558513'
for rel in ['inputs/native/parent-input-module.c','inputs/native/parent-input.xml']:add(b82/rel)
for p in root.rglob('*'):
 if p.is_file() and p.name!='component-manifest.json':add(p)
witness=json.loads((root/'qa/witness-1791134690967051395/report.json').read_text())
assert witness['diagnosisConfirmed'] and len(witness['records'])==7
assert witness['sourceSHA256']==rows[str(owner/'qa/pointer.py')]['sha256']
out=root/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
report={'passed':True,'nativeAcceptance':False,'scope':'Protected source integrity and actual-parser diagnosis only','checks':len(rows),'files':rows}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(root/'reviewed-inputs.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(rows),'report':str(out/'report.json')}))
