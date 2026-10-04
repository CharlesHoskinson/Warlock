import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-xdg-coordinate-design-held-v465/qa/slice-manifest.json';assert sha(parent)=='f72ae292632c0e1903a0eb3e0741adb266a546b5cae3835847c2ff5d462d3943'
for e in json.loads(parent.read_text())['files']:assert sha(REPO/e['path'])==e['sha256']
files=[];links=[];reports=[];native=[];core=None
for number in range(466,474):
 source=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(source.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or any(x in p.relative_to(source).parts for x in ['inputs','native-evidence','original']):continue
  j=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel) if Path(rel).is_absolute() else source/rel)==digest
  if number==467:assert not j['passed'] and j['error']=="AssertionError('SurfacePassElement.cpp')"
  else:assert j['passed']
  if number==469:assert len(j['translationUnits'])==3 and all(row['exitCode']==0 and sha(Path(row['object']))==row['objectSHA256'] and sha(Path(row['source']))==row['sourceSHA256'] for row in j['translationUnits']) and len(j['owningHeaders'])==694
  if number==470:
   core=j;assert len(j['rebuiltArchiveMembers'])==3 and j['unchangedArchiveMembers']==430 and len(j['owningHeaders'])==694
   assert j['exportClosure']=={'ancestorCount':13412,'candidateCount':13412,'missingSymbols':[]}
  if number==471:assert not j['missingSymbols'] and len(j['owningHeaders'])==694
  if p.parent.name.startswith('native-'):
   assert j['passed'] and j['cleanupPassed'] and len(j['checks'])==124 and all(c['passed'] for c in j['checks']) and not j['mainDesktopActions']
   assert {c['name'] for c in j['profiles']}=={'zero-scale1','origin-scale1','zero-scale2','origin-scale2'}
   captures=j['pixelCaptures'];assert len(captures)==8 and all(c['passed'] and c['postCapturePassed'] and len(c['oracleResult']['samples'])==5 for c in captures)
   native.append((p,j))
assert core is not None and len(native)==1
pair=json.loads((REPO/'implementation/elm-xdg-origin-runtime-v472/qa/build-pair-manifest.json').read_text())['nativePair'];j=native[0][1];host=j['cleanup']
assert pair['core']=={'path':core['binary'],'sha256':core['binarySHA256']}
assert host['hyprlandMaps']['files'][str(Path(pair['core']['path']).resolve())]==pair['core']['sha256']
assert j['pluginMaps']['files'][str(Path(pair['plugin']['path']).resolve())]==pair['plugin']['sha256']
assert host['privateAquamarine']['mappedVerified'] and host['privateAquamarine']['mappedFiles']=={pair['aquamarine']['path']:pair['aquamarine']['sha256']}
assert sha(REPO/'implementation/elm-xdg-origin-runtime-v472/candidate_host.py')==sha(REPO/'implementation/elm-seat-focus-restored-runtime-v453/candidate_host.py')
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Bounded actual root geometry-origin full-surface rendering with bufferScale1/2 PNG/RGB and postcapture target/ACK/output identity','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'symlinks':links,'reports':reports,'nativePair':pair,'nativeAcceptance':True,'nativeCheckCount':124,'actualPixelFrames':8,'profileCount':4,'nativePixelsAccepted':True,'physicalPointerAccepted':False,'nonzeroGeometryOperationsAccepted':False,'sharedRegressionOnNewCoreAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'nativeChecks':124,'pixelFrames':8,'manifestSHA256':sha(output)}))
