"""Freeze exact V14 tuple and bounded lifecycle evidence, not desktop acceptance."""
import hashlib,json,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
desc=read(ROOT/'parent-probe-build.json');bp=Path(desc['buildReport']);assert sha(bp)==desc['buildReportSHA256'];b=read(bp);assert b['passed']
for rel,digest in b['inputs'].items():assert sha(ROOT/rel)==digest and sha(bp.parent/'inputs'/rel)==digest,rel
for key in ['owningFiles','dependencies']:
 for path,digest in b[key].items():assert sha(path)==digest,path
for key in ['module','client']:assert sha(b[key])==b[key+'SHA256']
cpu=[]
for pattern,count in [('inspection-*',60),('event-kind-*',14),('seat-retirement-*',2),('helper-test-*',16)]:
 path=sorted((ROOT/'qa').glob(pattern+'/report.json'))[-1];r=read(path)
 assert r['passed'] and len(r['checks'])==count and all(c['passed'] for c in r['checks']),path
 for name,digest in r['inputs'].items():assert sha(ROOT/name if not Path(name).is_absolute() else name)==digest,name
 cpu.append({'path':str(path),'sha256':sha(path),'checks':count,'scope':r.get('scope')})
np=sorted((ROOT/'qa').glob('native-*/report.json'))[-1];n=read(np)
assert n['passed'] and n['cleanupPassed'] and len(n['checks'])==105 and all(c['passed'] for c in n['checks'])
assert n['buildReport']==str(bp) and n['buildReportSHA256']==sha(bp)
for path,digest in n['inputs'].items():assert sha(path)==digest,path
for rel,digest in n['artifacts'].items():assert sha(np.parent/rel)==digest,rel
baseline=[c for c in n['checks'] if c['name']=='actualGTKRecipientAndCoordinates'];assert len(baseline)==12
assert [c['mode'] for c in baseline]==[[w,h,s] for w,h,s in [(800,600,1),(640,480,1),(960,640,2),(800,600,1)] for _ in range(3)]
pairs=[c for c in n['checks'] if c['name'].endswith(':exactPhysicalPair')];assert len(pairs)==17
required=['held-shrink','held-scale','held-restore','held-controller-quit','held-controller-eof','duplicate-parent-press','three-held-buttons-eof:1','three-held-buttons-eof:3','three-held-buttons-eof:2']
assert all(any(c['name']==name+':exactPhysicalPair' for c in pairs) for name in required)
for c in pairs:
 assert len(c['press'])==len(c['release'])==1 and c['press'][0]['sequence']<c['release'][0]['sequence']
 for e,eventType in [(c['press'][0],4),(c['release'][0],7)]:
  assert e['eventType']==eventType and e['signalWidgetIsRecipient'] and e['eventWidgetIsRecipient'] and e['eventWindowIsOwned']
clients=n['interactiveClients'];assert len(clients)==16 and sum(c['exitCode']==6 for c in clients)==2
for c in clients:
 assert c['exitCode'] in (0,6) and c['clientSHA256']==b['clientSHA256'] and c['buildReportSHA256']==sha(bp) and c['wrapperSHA256']==sha(ROOT/'qa/interactive-client.py')
 assert c['process']['pgid']==c['process']['pid']
h=n['privateHost'];assert h['runtimeGone'] and not h['remainingDescendants'] and not h['cleanupErrors'] and not h['unexpectedInnerDescendants']
assert h['width']==800 and h['height']==600 and h['privateAquamarine']['mappedVerified']
assert 'until=time.monotonic()+6' in (ROOT/'qa/native.py').read_text() and sha(ROOT/'qa/native.py')==sha(np.parent/'native.py')
parent=ROOT.parent/'elm-parent-input-probe-v12/qa/implementation-manifest.json';parentPacket=read(parent)
for entry in parentPacket['files']:
 path=parent.parents[1]/entry['path']
 if 'sha256' in entry:assert sha(path)==entry['sha256']
 else:assert str(path.readlink())==entry['symlink']
manifest=ROOT/'qa/implementation-manifest.json';assert not manifest.exists()
files=[]
for path in sorted(ROOT.rglob('*')):
 if path.is_symlink():files.append({'path':str(path.relative_to(ROOT)),'symlink':str(path.readlink())})
 elif path.is_file():files.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'size':path.stat().st_size,'mode':stat.S_IMODE(path.stat().st_mode)})
manifest.write_text(json.dumps({'schema':1,'passed':True,'scope':'Original parent coordinate baseline plus held physical pair continuity across child modes, controller quit/EOF/refusal, three held buttons and fresh recovery clicks; callback retirement has CPU-only proof','fullRoadmapAcceptance':False,'releaseAcceptance':False,'parentConfigureFenceAcceptance':False,'focusLeaveAcceptance':False,'multiOutputAcceptance':False,'cursorAcceptance':False,'pixelPresentationAcceptance':False,'nativeSeatHotUnplugAcceptance':False,'buildReport':str(bp),'buildReportSHA256':sha(bp),'nativeReport':str(np),'nativeReportSHA256':sha(np),'nativeChecks':105,'baselineCoordinateGates':12,'lifecyclePhysicalPairs':17,'cpuReports':cpu,'parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files},indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(manifest),'files':len(files)}))
