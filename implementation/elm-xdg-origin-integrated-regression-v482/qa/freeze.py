import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-xdg-origin-render-qualified-v474/qa/slice-manifest.json';assert sha(parent)=='5153ea2a98eb9896a695202f8979a2a6eaa61686b5b33438d0dc00d0402ac69a'
held=json.loads(parent.read_text())
for e in held['files']:assert sha(REPO/e['path'])==e['sha256']
for e in held['symlinks']:assert str((REPO/e['path']).readlink())==e['target']
files=[];links=[];reports=[];native=[];failure=[]
for number in range(475,483):
 source=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(source.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts or p==ROOT/'qa/slice-manifest.json':continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or any(x in p.relative_to(source).parts for x in ['inputs','native-evidence','original']):continue
  j=json.loads(p.read_text());row={'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']};reports.append(row)
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel) if Path(rel).is_absolute() else source/rel)==digest
  if number==475 and not j['passed']:
   assert j['error']=="KeyError('parent')" and not j['checks'] and 'cleanup' not in j;row['classification']='Metadata preflight refusal before GUI'
  elif number==478:
   assert not j['passed'] and j['cleanupPassed'] and len(j['checks'])==86 and j['error']=="RuntimeError('Unchanged observation deadline')";failure.append(row)
   d=[e['state'] for e in j['focusDiagnostics'] if e['kind']=='capability'];assert len(d)==3 and len({e['focus']['surfaceId'] for e in d})==1 and [e['focus']['liveKeyboardResources'] for e in d]==[1,0,1]
  else:assert j['passed']
  if p.parent.name.startswith('native-') and j['passed']:
   assert j['cleanupPassed'] and all(c['passed'] for c in j['checks']) and not j['mainDesktopActions'];native.append((number,p,j))
assert len(native)==6 and len(failure)==1
pair=held['nativePair'];counts=[]
for number,p,j in native:
 host=j.get('cleanup',j.get('privateHost'))
 assert host['hyprlandMaps']['files'][str(Path(pair['core']['path']).resolve())]==pair['core']['sha256']
 assert host['privateAquamarine']['mappedVerified'] and host['privateAquamarine']['mappedFiles']=={pair['aquamarine']['path']:pair['aquamarine']['sha256']}
 if 'pair' in j:assert j['pair']==pair
 counts.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':len(j['checks'])})
 if number==476:
  assert len(j['checks'])==285 and len(j['pointerStages'])==8 and sum(len(s['gestures']) for s in j['pointerStages'])==40 and len(j['pixelCaptures'])==16
  assert all(c['passed'] and c.get('postCapturePassed') for c in j['pixelCaptures'])
  for stage in j['pointerStages']:
   assert len(stage['gestures'])==5 and stage['physicalHardwareAccepted'] is False
   for gesture in stage['gestures']:assert len(gesture['validatedPair']['events'])==2 and gesture['validatedPair']['physicalHardwareAccepted'] is False
 elif number==479:assert len(j['checks'])==161 and j['scenarios']==['GEOMETRY-MENU-%02d'%x for x in range(1,11)]
 elif number==480:assert len(j['checks'])==57
 elif number==481:assert len(j['checks']) in [372,186,46] and not j['profileCleanupErrors'] and not j['finalCleanupErrors']
assert sum(e['checks'] for e in counts)==1107
assert sha(REPO/'implementation/elm-xdg-origin-owning-observer-v477/native/observer.cpp')==sha(REPO/'implementation/elm-seat-focus-owning-observer-v452/native/observer.cpp')
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Actual corrected-core root pointer/geometry/reconnect/bounds qualification with full menu same-title publication regression failure retained','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'symlinks':links,'reports':reports,'nativePair':pair,'boundedNativeAcceptance':True,'acceptedNativeCheckCount':1107,'acceptedNativeReports':counts,'failedMenuEvidence':failure,'pointerGestures':40,'pointerPixelFrames':16,'syntheticParentPointerAccepted':True,'physicalHardwareAccepted':False,'fullSharedMenuRegressionAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'acceptedNativeChecks':1107,'menuRegressionFailed':True,'manifestSHA256':sha(output)}))
