import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-seat-focus-bounds-qualified-v460/qa/slice-manifest.json';assert sha(parent)=='de87949b83f13b6ea51b159342a8e90288cfc0880aea60ac4af77bbd90c2acb6'
for e in json.loads(parent.read_text())['files']:assert sha(REPO/e['path'])==e['sha256']
source=REPO/'implementation/elm-seat-focus-presented-landmarks-v461';files=[];links=[];reports=[];native=[]
for p in sorted(source.rglob('*')):
 if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
 if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
 if not p.is_file():continue
 files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
 if p.name!='report.json' or 'native-evidence' in p.relative_to(source).parts or 'original' in p.relative_to(source).parts:continue
 j=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
 for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
 for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel))==digest
 if p.parent.name.startswith('native-'):
  assert not j['passed'] and j['cleanupPassed'] and len(j['checks'])==60 and j['error']=="AssertionError('origin-scale1:actualPresentedLandmarks')"
  assert len(j['pixelCaptures'])==4 and all(c['passed'] and c['postCapturePassed'] for c in j['pixelCaptures'][:3])
  c=j['pixelCaptures'][3];assert not c['passed'] and c['error']=="Refused('presented landmark mismatch')" and c['oracleArguments']['geometry']==[16,24,800,600] and c['oracleArguments']['real']==[-1,-1,800,600]
  assert c['oracleArguments']['diagnostic_nonzero'] is True
  assert all(c['samples'][i]['measured'][4]['rgb']==[32,32,32] for i in range(3))
  native.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'cleanupPassed':True,'checksReached':60,'zeroOriginFrameChecks':3,'error':j['error']})
 else:assert j['passed']
assert len(native)==1
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Actual nonzero-origin presentation discrepancy preserved; diagnostic transform unqualified','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'symlinks':links,'reports':reports,'failedNativeEvidence':native,'nativeAcceptance':False,'nativePixelsAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(output)}))
