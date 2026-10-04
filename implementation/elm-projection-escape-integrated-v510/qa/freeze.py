import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-projection-retry-boundary-qualified-v502/qa/slice-manifest.json';assert sha(parent)=='0b0f01cb2d60c228a8f51997279b56852df4ccb93e861ac5c64c18c787a053fc';held=json.loads(parent.read_text())
for e in held['files']:assert sha(REPO/e['path'])==e['sha256']
component=REPO/'implementation/elm-projection-escape-component-v509/component-manifest.json';assert sha(component)=='e2bfabe380a089059e3330c93e3b4af310563fa69ca2e727a781c369d6cf1cfa'
c=json.loads(component.read_text());assert c['passed'] and c['helperChecks']==168 and c['mutantsRejected']==10 and c['typedCompiledCases']==14
for e in c['files']:assert sha(REPO/e['path'])==e['sha256']
files=[];links=[];reports=[];native=[]
for number in list(range(503,510))+list(range(511,516)):
 directory=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or any(x in p.relative_to(directory).parts for x in ['inputs','native-evidence']):continue
  j=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  if number==504 and p.parent.name.startswith('native-'):
   assert not j['passed'] and len(j['checks'])==138 and j['cleanupPassed'] and 'six-second deadline' in j['error'];continue
  assert j['passed']
  if number in [512,513,514] and p.parent.name.startswith('native-'):
   expected={512:161,513:57,514:89}[number];assert len(j['checks'])==expected and all(e['passed'] for e in j['checks']) and j['cleanupPassed'] and not j['mainDesktopActions'];assert j['pair']==held['nativePair'];assert '/elm-projection-native-escape-combined-v507/' in j['buildReport'];native.append({'path':str(p.relative_to(REPO)),'checks':expected,'nativeEscapeIntents':(p.parent/'native-evidence/elm-webview.log').read_text(errors='replace').count('surface-native-escape-stored:')})
assert len(native)==3 and sum(e['checks'] for e in native)==307 and sum(e['nativeEscapeIntents'] for e in native)==8
witness=REPO/'implementation/elm-pointer-publication-race-diagnostic-v515/witness.json';w=json.loads(witness.read_text());assert w['passed'] and not w['causeConfirmed']
assert sha(Path(w['report']))==w['reportSHA256'] and sha(Path(w['log']))==w['logSHA256']
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':'implementation/elm-projection-native-escape-combined-v507','componentManifest':str(component),'componentManifestSHA256':sha(component),'parentManifest':str(parent),'parentManifestSHA256':sha(parent),'nativeAcceptance':True,'nativeCheckCount':307,'nativeReports':native,'nativePair':held['nativePair'],'helperChecks':168,'mutantsRejected':10,'typedCompiledCases':14,'files':files,'symlinks':links,'reports':reports,'unresolvedPointerPublicationRace':str(witness.relative_to(REPO)),'fullReleaseAccepted':False,'completedRequirementIds':[]}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'nativeChecks':307,'manifestSHA256':sha(p)}))
