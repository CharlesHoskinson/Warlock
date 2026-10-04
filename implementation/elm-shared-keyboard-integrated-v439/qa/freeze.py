import hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-geometry-joint-held-v434/qa/slice-manifest.json';assert sha(parent)=='a74eba5b7f831b662aee51677243cac86c551b7d0af5b6e35c1527e7ac211da9'
for e in json.loads(parent.read_text())['files']:assert sha(REPO/e['path'])==e['sha256']
runtime=REPO/'implementation/elm-shared-keyboard-runtime-v435';pair=json.loads((runtime/'qa/build-pair-manifest.json').read_text());assert sha(Path(pair['keyboardAcceptance']))==pair['keyboardAcceptanceSHA256']
for e in pair['nativePair'].values():assert sha(Path(e['path']))==e['sha256']
for rel,digest in pair['files'].items():assert sha(runtime/rel)==digest
files=[];reports=[];nativeChecks=0
for name in ['elm-shared-keyboard-runtime-v435','elm-shared-keyboard-menu-native-v436','elm-shared-keyboard-geometry-native-v437','elm-shared-keyboard-reconnect-native-v438']:
 source=REPO/'implementation'/name
 for p in sorted(source.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  assert not p.is_symlink();files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or 'inputs' in p.relative_to(source).parts or 'native-evidence' in p.relative_to(source).parts:continue
  j=json.loads(p.read_text());assert j['passed']
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel) if Path(rel).is_absolute() else source/rel)==digest
  if p.parent.name.startswith('native-'):
   assert j['cleanupPassed'] and all(c['passed'] for c in j['checks']) and j['pair']==pair['nativePair'];count=len(j['checks']);assert count==({'436':69,'437':161,'438':57}[name[-3:]]);nativeChecks+=count
   aq=j['privateHost']['privateAquamarine'];assert aq['mappedVerified'] and aq['sha256']==pair['nativePair']['aquamarine']['sha256'] and aq['mappedFiles'][pair['nativePair']['aquamarine']['path']]==aq['sha256']
   if name.endswith('437'):assert j['scenarios']==['GEOMETRY-MENU-'+str(i).zfill(2) for i in range(1,11)] and j['receiptHold09']['finishedBeforeDeadline']
  reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p)})
assert nativeChecks==287
for old,new in [('elm-geometry-carrier-shared-native-v424','elm-shared-keyboard-menu-native-v436'),('elm-geometry-lifetime-retirement-native-v432','elm-shared-keyboard-geometry-native-v437'),('elm-geometry-current-reconnect-native-v429','elm-shared-keyboard-reconnect-native-v438')]:
 a=(REPO/'implementation'/old/'qa/native.py').read_text();b=(REPO/'implementation'/new/'qa/native.py').read_text();assert a.replace('elm-geometry-bounds-runtime-v420','elm-shared-keyboard-runtime-v435')==b
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Coherent422/core89/plugin409/AQ155 shared menu69/geometry161/reconnect57; broad UIUX/input/hardware/release open','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'reports':reports,'nativeChecks':nativeChecks,'nativeAcceptance':True,'jointGeometryMenuQualified':True,'fullGeometryCampaignAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'nativeChecks':nativeChecks,'manifestSHA256':sha(output)}))
