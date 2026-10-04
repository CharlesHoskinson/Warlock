import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1]
o=r.parent/'elm-qt6-role-journal-fixture-v250'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(o/'component-manifest.json')=='c65966d9a136418a4b371278a554d3d830890f0d74b76950984857c0e4097983'
m=json.loads((o/'component-manifest.json').read_text())
for name,row in m['files'].items():
 p=o/name
 assert p.is_file() and not p.is_symlink()
 assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
 assert oct(p.stat().st_mode&0o777)==row['mode']
assert sha(o/'native/qt-role-client.cpp')=='83e8a3f065262e3a05deed454619733dcac81b23384e0533ccae330524d29418'
assert sha(Path(m['build']['path']))==m['build']['sha256']
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
report={'passed':True,'rows':len(m['files']),'ownerManifestSHA256':sha(o/'component-manifest.json'),'sourceReviewPassed':True,'nativeAcceptance':False,'scope':'Local Qt source/lifetime review only; native role/input/pixel/bus cleanup gates open'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
(r/'component-manifest.json').write_text(json.dumps({'schema':1,'sourceHeld':True,'sourceReviewPassed':True,'nativeAcceptance':False,'ownerManifestSHA256':report['ownerManifestSHA256'],'files':files,'verificationReport':str((out/'report.json').relative_to(r))},indent=2)+'\n')
print(json.dumps({'rows':report['rows'],'manifestSHA256':sha(r/'component-manifest.json')}))
