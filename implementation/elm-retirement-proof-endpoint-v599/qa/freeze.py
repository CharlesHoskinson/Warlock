import pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
origin=json.loads((ROOT/'origin.json').read_text())
for source,row in origin['sources'].items():
 assert sha(ROOT/row['copiedTo'])==row['sha256']
 assert sha(ROOT.parents[1]/source)==row['sha256']
test=sorted((ROOT/'qa').glob('test-*/report.json'))[-1];mutations=sorted((ROOT/'qa').glob('mutations-*/report.json'))[-1]
t=json.loads(test.read_text());m=json.loads(mutations.read_text());assert t['passed'] and m['passed']
assert t['endpointSHA256']==m['endpointSHA256']==sha(ROOT/'adapter/grant_endpoint.py')
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
d={'sourceHeld':True,'cpuAccepted':True,'nativeAcceptance':False,'syntheticTransportQualified':False,'durableReservationReleaseAccepted':False,'fullRoadmapAccepted':False,'scope':'Strict actual Python decoder replay; immutable native596 wires and synthetic transport controls only','testReport':str(test.relative_to(ROOT)),'mutationReport':str(mutations.relative_to(ROOT)),'checks':len(t['checks']),'nativeWireFixtures':t['nativeWireFixtureCount'],'syntaxValidMutationControls':m['mutantsRejected'],'files':files}
(ROOT/'component-manifest.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'manifest':str(ROOT/'component-manifest.json'),'sha256':sha(ROOT/'component-manifest.json')}))
