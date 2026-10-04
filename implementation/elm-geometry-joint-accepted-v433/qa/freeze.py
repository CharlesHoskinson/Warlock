import hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-geometry-current-recovery-accepted-v430/qa/slice-manifest.json';assert sha(parent)=='db8dca6216c0c3dfadff0904911cf797f3598cfacd330a7dca730a41da421ad1';held=json.loads(parent.read_text());assert held['passed']
for entry in held['files']:assert sha(REPO/entry['path'])==entry['sha256']
files=[];reports=[]
for name in ['elm-geometry-joint-current-native-v431','elm-geometry-lifetime-retirement-native-v432']:
 source=REPO/'implementation'/name
 for path in sorted(source.rglob('*')):
  if not path.is_file() or '__pycache__' in path.parts:continue
  assert not path.is_symlink();files.append({'path':str(path.relative_to(REPO)),'sha256':sha(path),'size':path.stat().st_size})
  if path.name!='report.json':continue
  j=json.loads(path.read_text());reports.append({'path':str(path.relative_to(REPO)),'sha256':sha(path),'passed':j['passed']})
  for rel,digest in j.get('artifacts',{}).items():assert sha(path.parent/rel)==digest
  for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel) if Path(rel).is_absolute() else source/rel)==digest
  if name.endswith('v431') and path.parent.name.startswith('native-'):
   assert not j['passed'] and j['cleanupPassed'] and j['scenarios']==['GEOMETRY-MENU-'+str(i).zfill(2) for i in range(1,10)] and j['error']=="AssertionError('retirementNeverTargetsSameTitleReplacement')"
  else:assert j['passed']
native=REPO/'implementation/elm-geometry-lifetime-retirement-native-v432/qa/native-1791129443414985239/report.json';j=json.loads(native.read_text());assert len(j['checks'])==161 and all(c['passed'] for c in j['checks']) and j['cleanupPassed'];assert j['scenarios']==['GEOMETRY-MENU-'+str(i).zfill(2) for i in range(1,11)]
assert j['receiptHold09']['finishedBeforeDeadline'] and all(t['finishedBeforeDeadline'] for t in j['transitions']);assert len(j['pixelAttempts'])>=6
pair=json.loads((REPO/'implementation/elm-geometry-bounds-runtime-v420/qa/build-pair-manifest.json').read_text());assert j['pair']==pair['nativePair']
for e in pair['nativePair'].values():assert sha(Path(e['path']))==e['sha256']
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Joint physical geometry menu01-10 with explicit lifetime oracle amendment; full size-profile/canonical layering/UIUX/release gates open','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'reports':reports,'nativeAcceptance':True,'jointGeometryMenuQualified':True,'retirementOracleAmended':True,'fullGeometryCampaignAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(output)}))
