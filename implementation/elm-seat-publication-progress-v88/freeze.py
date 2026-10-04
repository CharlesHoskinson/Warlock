import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;IMPL=ROOT.parent;REPO=IMPL.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def packet(p,passed):
 d=json.loads(p.read_text());assert d['passed'] is passed,p
 for rel,value in d.get('artifacts',{}).items():assert sha(p.parent/rel)==value,rel
 for path,value in d.get('inputs',{}).items():
  if Path(path).is_absolute():assert sha(path)==value,path
 return d
cpu=IMPL/'elm-seat-publication-v79/qa/replay-1791106071051756999/report.json';model=IMPL/'elm-seat-publication-v79/qa/model-1791106030241466522/report.json';native=IMPL/'elm-seat-original-input-v85/qa/native-1791106661802588805/report.json'
c=packet(cpu,True);m=packet(model,True);n=packet(native,True)
assert c['candidateChecks']==28 and c['mutantsRejected']==5 and len(m['namedScenarios'])==10 and m['mutantsRejected']==7 and m['invariantSamples']==1000 and m['maxSteps']==40
assert len(n['checks'])==159 and all(v['passed'] for v in n['checks']) and n['cleanupPassed']
old=json.loads((IMPL/'elm-parent-focus-hit-test-v76/qa/native-1791104913986704180/report.json').read_text());assert [v['name'] for v in old['checks']]==[v['name'] for v in n['checks']]
failed=[IMPL/'elm-seat-burst-native-v81/qa/native-1791106249964842316/report.json',IMPL/'elm-seat-burst-baseline-v83/qa/native-1791106369555028272/report.json',IMPL/'elm-seat-burst-observed-v86/qa/native-1791106441250677616/report.json',IMPL/'elm-seat-burst-qualified-v87/qa/native-1791106488291216547/report.json']
for p in failed:assert packet(p,False)['cleanupPassed']
unsafe=json.loads(failed[2].read_text());assert unsafe['checks'][-1]['announcements']==3 and unsafe['checks'][-1]['expected']==0
stationary=json.loads(failed[3].read_text());assert 'six-second observation deadline' in stationary['error'] and [(b['cycles'],b['final'],b['publications']) for b in stationary['capabilityBursts']]==[(3,0,0),(4,1,1)]
manifest=IMPL/'elm-seat-publication-v79/component-manifest.json';component=packet(manifest,True)
for v in component['files']:
 p=manifest.parent/v['path']
 if 'symlink' in v:assert p.is_symlink() and os.readlink(p)==v['symlink']
 else:assert sha(p)==v['sha256']
roots=['elm-seat-publication-v79','elm-seat-burst-fixture-v80','elm-seat-burst-native-v81','elm-seat-burst-fixture-fixed-v82','elm-seat-burst-baseline-v83','elm-seat-burst-fixed-v84','elm-seat-original-input-v85','elm-seat-burst-observed-v86','elm-seat-burst-qualified-v87','elm-seat-publication-progress-v88']
files=[]
for name in roots:
 for p in sorted((IMPL/name).rglob('*')):
  if p==ROOT/'progress-manifest.json':continue
  if p.is_symlink():files.append({'path':str(p.relative_to(REPO)),'symlink':os.readlink(p)})
  elif p.is_file():files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
r={'schema':1,'passed':True,'releaseAcceptance':False,'nativeBurstAcceptance':False,'classification':'Progress: guarded AQ compiles and original input159 passes; actual original native stale publication reproduced; corrected burst retains newly exposed stationary focus failure','scope':'One AQ implementation source; CPU/model/build evidence and original bounded input campaign, not integrated geometry/core/plugin release','cpuChecks':28,'cpuMutantsRejected':5,'namedModelScenarios':10,'modelSamples':1000,'modelMaxSteps':40,'modelMutantsRejected':7,'nativeOriginalCheckExecutions':159,'retainedFailedReports':[{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for p in failed],'acceptedReports':[{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for p in [cpu,model,native]],'ownedRoots':['implementation/'+v for v in roots],'files':files}
p=ROOT/'progress-manifest.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(p),'sha256':sha(p),'files':len(files)}))
