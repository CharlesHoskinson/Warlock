import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-publication-input-reviewed-v541/qa/slice-manifest.json';assert sha(parent)=='a35f8f66de616393de697429237d01ff699877fc3ae6461d991791a8dfc7a4d9'
for row in json.loads(parent.read_text())['files']:assert sha(REPO/row['path'])==row['sha256']
files=[];links=[];reports=[];native=[]
for number in [542,543,544,545,546,547,548,550,551,552,553,554,555,556,557,558,559]:
 directory=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json':continue
  j=json.loads(p.read_text());inherited=p.parent.name=='mutations-1791137655753912153';assert j['passed']==(number not in [543,548,553,554,557] or inherited)
  reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed'],'inheritedArchive':inherited})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  if p.parent.name.startswith('native-'):
   assert j['cleanupPassed'] and not j['mainDesktopActions'] and all(c['passed'] for c in j['checks']);native.append({'path':str(p.relative_to(REPO)),'passed':j['passed'],'checks':len(j['checks']),'pair':j['pair']})
assert len(native)==4 and len(reports)==18
analysis=REPO/'implementation/elm-native-owner-interleave-analysis-v559/qa/report.json';a=json.loads(analysis.read_text());assert a['controlledMechanismConfirmed'] and not a['historical504CauseConfirmed'];assert [c['proofAgeMicroseconds'] for c in a['checks']]==[2433,2106]
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':'implementation/elm-stable-surface-publication-v521','diagnosticSources':['implementation/elm-native-owner-turn-interleave-before-v555','implementation/elm-native-owner-turn-interleave-current-v556'],'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'nativeAcceptance':True,'controlledCurrentNativeChecks':89,'controlledMechanismConfirmed':True,'historical504CauseConfirmed':False,'pointerRaceCausallyResolved':False,'fullReleaseAccepted':False,'completedRequirementIds':[],'nativeReports':native,'analysis':str(analysis.relative_to(REPO)),'files':files,'symlinks':links,'reports':reports}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(p)}))
