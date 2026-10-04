import hashlib,json,resource,time,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];o=r.parent/'elm-xdg-pointer-owned-runner-v224';m=o/'component-manifest.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(m)=='4b4c2e27c36f99ba930c81c5c45d631064efdc1673e21a394ec8e9a6ebb4f241'
d=json.loads(m.read_text());assert d['sourceHeld'] and not d['nativeAcceptance']
rows={}
for p,row in [(o/name,row) for name,row in d['files'].items()]+[(Path(name),row) for name,row in d['externalFiles'].items()]:
 assert p.is_file() and sha(p)==row['sha256'] and p.stat().st_size==row['size'],str(p)
 rows[str(p)]=row
for name,row in d['selectedReports'].items():assert sha(Path(row['path']))==row['sha256'];assert json.loads(Path(row['path']).read_text())['passed'],name
for p in r.rglob('*'):
 if p.is_file():rows[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
rows[str(m)]={'sha256':sha(m),'size':m.stat().st_size}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
report={'passed':True,'nativeAcceptance':False,'scope':'Held224 source integrity and read-only semantic review only','checks':len(rows),'files':rows}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in r.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'reviewDisposition':'No blocking source finding; root-controlled exact-tuple attempt only','files':files}
p=r/'component-manifest.json';p.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(rows),'report':str(out/'report.json'),'manifestSHA256':sha(p)}))
