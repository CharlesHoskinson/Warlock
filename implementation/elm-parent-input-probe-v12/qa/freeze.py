"""Freeze bounded parent-pointer evidence after checking actual reports and inputs."""
import hashlib,json,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
build=read(ROOT/'parent-probe-build.json');bp=Path(build['buildReport']);assert sha(bp)==build['buildReportSHA256'];b=read(bp);assert b['passed']
for rel,digest in b['inputs'].items():assert sha(ROOT/rel)==digest and sha(bp.parent/'inputs'/rel)==digest,rel
for key in ('owningFiles','dependencies'):
 for path,digest in b[key].items():assert sha(path)==digest,path
for pathkey,hashkey in [('module','moduleSHA256'),('client','clientSHA256')]:assert sha(b[pathkey])==b[hashkey]
cp=sorted((ROOT/'qa').glob('inspection-*/report.json'))[-1];c=read(cp)
assert c['passed'] and all(x['passed'] for x in c['checks'])
for rel,digest in c['inputs'].items():assert sha(ROOT/rel)==digest,rel
np=sorted((ROOT/'qa').glob('native-*/report.json'))[-1];n=read(np)
assert n['passed'] and n['cleanupPassed'] and all(x['passed'] for x in n['checks'])
assert n['buildReport']==str(bp) and n['buildReportSHA256']==sha(bp)
for path,digest in n['inputs'].items():assert sha(path)==digest,path
for rel,digest in n['artifacts'].items():assert sha(np.parent/rel)==digest,rel
points=[x for x in n['checks'] if x['name']=='actualGTKRecipientAndCoordinates'];assert len(points)==12
assert [x['mode'] for x in points]==[[w,h,s] for w,h,s in [(800,600,1),(640,480,1),(960,640,2),(800,600,1)] for _ in range(3)]
for point in points:
 assert len(point['press'])==len(point['release'])==1
 for event in point['press']+point['release']:
  assert event['signalWidgetIsRecipient'] and event['eventWidgetIsRecipient'] and event['eventWindowIsOwned']
 assert point['press'][0]['sequence']<point['release'][0]['sequence']
h=n['privateHost'];assert h['runtimeGone'] and not h['remainingDescendants'] and not h['cleanupErrors'] and not h['unexpectedInnerDescendants']
assert h['width']==800 and h['height']==600 and h['privateAquamarine']['mappedVerified']
assert 'until=time.monotonic()+6' in (ROOT/'qa/native.py').read_text()
assert sha(ROOT/'qa/native.py')==sha(np.parent/'native.py')
retained=[]
for relative in ['implementation/elm-menu-reflow-v6/qa/native-1791089500194235014/report.json','implementation/elm-parent-input-probe-v11/qa/inspection-1791094226825165411/report.json','implementation/elm-parent-input-probe-v11/qa/native-1791094184233174808/report.json']:
 path=REPO/relative;data=read(path);retained.append({'path':relative,'sha256':sha(path),'passed':data['passed']})
assert retained[0]['passed'] is False and retained[1]['passed'] is False and retained[2]['passed'] is True
manifest=ROOT/'qa/implementation-manifest.json';assert not manifest.exists()
files=[]
for path in sorted(ROOT.rglob('*')):
 if path.is_symlink():files.append({'path':str(path.relative_to(ROOT)),'symlink':str(path.readlink())})
 elif path.is_file():files.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'size':path.stat().st_size,'mode':stat.S_IMODE(path.stat().st_mode)})
manifest.write_text(json.dumps({'schema':1,'passed':True,'scope':'Single unrotated parent800x600; three GTK points each across child800x600@1,640x480@1,960x640@2,800x600@1, exact paired clicks and malformed-coordinate CPU checks only','fullRoadmapAcceptance':False,'releaseAcceptance':False,'pixelPresentationAcceptance':False,'cursorAcceptance':False,'multiOutputAcceptance':False,'rotationAcceptance':False,'staleCallbackAcceptance':False,'buildReport':str(bp),'buildReportSHA256':sha(bp),'nativeReport':str(np),'nativeReportSHA256':sha(np),'nativeChecks':len(n['checks']),'coordinateGates':len(points),'cpuReport':str(cp),'cpuReportSHA256':sha(cp),'cpuChecks':len(c['checks']),'retainedEvidence':retained,'files':files},indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(manifest),'files':len(files)}))
