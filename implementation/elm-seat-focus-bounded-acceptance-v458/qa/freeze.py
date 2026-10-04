import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-keyboard-seat-focus-source-held-v449/qa/slice-manifest.json'
assert sha(parent)=='68e5c454daac62850674e00a695fd28ac3cc3e625ebe95d64a40fe641d7df875'
j=json.loads(parent.read_text())
for e in j['files']:assert sha(REPO/e['path'])==e['sha256'],e['path']
for e in j.get('symlinks',[]):assert str((REPO/e['path']).readlink())==e['target']
files=[];links=[];reports=[];native=[]
for number in range(450,458):
 source=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(source.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or 'inputs' in p.relative_to(source).parts or 'native-evidence' in p.relative_to(source).parts:continue
  j=json.loads(p.read_text());assert j['passed'],str(p)
  reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':True})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest,(p,rel)
  for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel) if Path(rel).is_absolute() else source/rel)==digest,(p,rel)
  if p.parent.name.startswith('native-'):
   assert j['cleanupPassed'] and all(c['passed'] for c in j['checks'])
   assert not j['mainDesktopActions']
   native.append((number,j))
  if number==450:
   assert len(j['rebuiltArchiveMembers'])==1 and 'InputManager.cpp.o' in j['rebuiltArchiveMembers']
   assert j['unchangedArchiveMembers']==432 and j['existingPublicHeadersUnchanged'] and j['geometryAndReloadArchivePayloadsPreserved']
   assert len(j['owningHeaders'])==694
   assert j['exportClosure']=={'ancestorCount':13412,'candidateCount':13412,'missingSymbols':[]}
assert [n for n,j in native]==[454,455,456]
assert [len(j['checks']) for n,j in native]==[89,161,57]
pair=native[0][1]['pair'];assert all(j['pair']==pair for n,j in native)
assert pair['core']['sha256']=='59200d452966c2d8cf35073b8eff54cf1a2f1cbc1f40ecfc0ff5626c54ba0746'
assert pair['aquamarine']['sha256']=='bfb0383901822a92f2fe945b4b80048f89cc4ffeeb6e9bb8ab748d57317928cb'
for e in pair.values():assert sha(Path(e['path']))==e['sha256']
menu=native[0][1]
for kind in ['focus','capability']:
 d=[e['state'] for e in menu['focusDiagnostics'] if e['kind']==kind];assert len(d)==3
 assert len({e['focus']['surfaceId'] for e in d})==1
 assert all(e['focus']['surfacePresent'] and e['seatGrab'] and e['focus']['surfaceClientPID']==menu['privateHost']['elm-webview']['pid'] for e in d)
 assert [e['focus']['liveKeyboardResources'] for e in d]==([1,0,1] if kind=='capability' else [1,1,1])
 assert d[1]['keys']==d[2]['keys']==[] and d[1]['bindKeys']==d[2]['bindKeys']==[] and d[1]['mods']==d[2]['mods']==0
geometry=native[1][1];assert geometry['scenarios']==['GEOMETRY-MENU-%02d'%n for n in range(1,11)] and geometry['passed']
assert not geometry['allContractScenariosPassed'] and not geometry['geometryMenuCompleteAccepted'] and not geometry['fullRoadmapAccepted']
old=REPO/'implementation/elm-keyboard-focus-resource-observer-v444/native/observer.cpp'
new=REPO/'implementation/elm-seat-focus-owning-observer-v452/native/observer.cpp';assert sha(old)==sha(new)
a=REPO/'implementation/elm-shared-keyboard-loss-parent-runtime-v440/candidate_host.py'
if not a.exists():a=next((REPO/'implementation').glob('*v440'))/'candidate_host.py'
b=REPO/'implementation/elm-seat-focus-restored-runtime-v453/candidate_host.py';assert sha(a)==sha(b)
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists()
output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Bounded live-popup seat-focus correction with unchanged shared menu/geometry/reconnect regression oracles','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'symlinks':links,'reports':reports,'nativePair':pair,'nativeAcceptance':True,'nativeCheckCount':307,'nativeReports':3,'source':'implementation/elm-shared-geometry-carrier-v422','runtime':'implementation/elm-seat-focus-restored-runtime-v453','fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'nativeChecks':307,'manifestSHA256':sha(output)}))
