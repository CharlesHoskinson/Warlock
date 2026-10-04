import ast,hashlib,json,resource,stat,sys,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];o=r.parent/'elm-xdg-pointer-current-tuple-v229';parent=r.parent/'elm-xdg-pointer-owned-runner-v224';m=o/'component-manifest.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(m)==sys.argv[1];d=json.loads(m.read_text());assert d['sourceHeld'] and not d['nativeAcceptance'];rows={}
for p,row in [(o/name,row) for name,row in d['files'].items()]+[(Path(name),row) for name,row in d['externalFiles'].items()]:
 assert p.is_file() and sha(p)==row['sha256'] and p.stat().st_size==row['size'],str(p);rows[str(p)]=row
for name in ('pointer.py','pixels.py','parent_observation.py'):assert (o/'qa'/name).read_bytes()==(parent/'qa'/name).read_bytes(),name
old=[ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse((parent/'qa/native.py').read_text())) if isinstance(n,ast.Assert)]
new=[ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse((o/'qa/native.py').read_text())) if isinstance(n,ast.Assert)]
assert all(n in new for n in old)
meta=json.loads((o/'runtime/native-build-report.json').read_text());assert '/elm-core-xdg-origin-projection-v470/' in meta['binary'];assert '/elm-xdg-origin-owning-pair-v471/' in meta['plugin']['path']
for p in r.rglob('*'):
 if p.is_file():rows[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
rows[str(m)]={'sha256':sha(m),'size':m.stat().st_size}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();report={'passed':True,'nativeAcceptance':False,'checks':len(rows),'scope':'Exact held229 source/tuple integrity only','files':rows}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in r.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
p=r/'component-manifest.json';p.write_text(json.dumps({'sourceHeld':True,'nativeAcceptance':False,'evidenceIntegrityPassed':True,'reviewDisposition':'No source blocker for root-controlled bounded exact tuple attempt','files':files},indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(rows),'report':str(out/'report.json'),'manifestSHA256':sha(p)}))
