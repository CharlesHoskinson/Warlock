import hashlib,json,resource,stat,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];o=r.parent/'elm-toolkit-role-observer-v235';m=o/'component-manifest.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(m)=='150a1c75db7f6cb5ccf4e0562fdd0152df525fced500a81ee7928557872819cd';d=json.loads(m.read_text());assert d['sourceHeld'] and not d['nativeAcceptance'];rows={}
for p,row in [(o/name,row) for name,row in d['files'].items()]+[(Path(name),row) for name,row in d['externalFiles'].items()]:
 assert p.is_file() and sha(p)==row['sha256'] and p.stat().st_size==row['size'],str(p);rows[str(p)]=row
build=json.loads(Path(d['buildReport']).read_text());assert build['passed'] and not build['missingSymbols'] and len(build['owningHeaders'])==694
origin=json.loads((o/'origin.json').read_text());old=Path(origin['parent'])/'native/observer.cpp';assert sha(old)==origin['files']['native/observer.cpp']
a=old.read_text().split('std::string observe(',1)[1].split('\n}\n}\nAPICALL',1)[0];b=(o/'native/observer.cpp').read_text().split('std::string observe(',1)[1].split('\n}\n}\nAPICALL',1)[0];assert a==b
for p in r.rglob('*'):
 if p.is_file():rows[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
rows[str(m)]={'sha256':sha(m),'size':m.stat().st_size}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps({'passed':True,'nativeAcceptance':False,'checks':len(rows),'files':rows},indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in r.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
p=r/'component-manifest.json';p.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'reviewDisposition':'No read-only observer source blocker; toolkit/modal behavior unqualified','files':files},indent=2)+'\n');print(json.dumps({'passed':True,'checks':len(rows),'report':str(out/'report.json'),'manifestSHA256':sha(p)}))
