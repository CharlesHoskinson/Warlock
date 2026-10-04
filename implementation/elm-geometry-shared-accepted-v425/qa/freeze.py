import hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def item(path):return {'path':str(path.relative_to(REPO)),'sha256':sha(path),'size':path.stat().st_size}
names=['elm-shared-geometry-bounds-fixtures-v416','elm-output-publication-diagnostic-v417','elm-shared-application-publication-v418','elm-shared-application-reflow-fixture-v419','elm-geometry-bounds-runtime-v420','elm-geometry-bounds-shared-native-v421','elm-shared-geometry-carrier-v422','elm-geometry-carrier-shared-native-v424','elm-geometry-client-ack-proof-v426']
files=[];links=[];reports=[]
for name in names:
 source=REPO/'implementation'/name
 for path in sorted(source.rglob('*')):
  if 'elm-stuff' in path.parts or '__pycache__' in path.parts:continue
  if path.is_symlink():links.append({'path':str(path.relative_to(REPO)),'target':os.readlink(path)})
  elif path.is_file():files.append(item(path))
  if path.name!='report.json' or not path.is_file():continue
  report=json.loads(path.read_text());reports.append({**item(path),'passed':report['passed']})
  for rel,digest in report.get('artifacts',{}).items():assert sha(path.parent/rel)==digest
  for rel,digest in report.get('inputs',{}).items():
   if isinstance(digest,str):assert sha(Path(rel) if Path(rel).is_absolute() else source/rel)==digest
native=REPO/'implementation/elm-geometry-carrier-shared-native-v424/qa/native-1791127869741674715/report.json';report=json.loads(native.read_text())
assert report['passed'] and report['cleanupPassed'] and len(report['checks'])==69 and all(check['passed'] for check in report['checks'])
ack=REPO/'implementation/elm-geometry-client-ack-proof-v426/proof-1791128226455942940/report.json';a=json.loads(ack.read_text());assert a['passed'] and a['boundedNativeClientACKQualified'] and all(control['detected'] for control in a['controls'])
pair=json.loads((REPO/'implementation/elm-geometry-bounds-runtime-v420/qa/build-pair-manifest.json').read_text());assert pair['nativePair']==report['pair']
for entry in pair['nativePair'].values():assert sha(Path(entry['path']))==entry['sha256']
assert sha(Path(pair['producerEvidence']))==pair['producerEvidenceSHA256']
for entry in json.loads(Path(pair['producerEvidence']).read_text())['files']:assert sha(REPO/entry['path'])==entry['sha256']
source=REPO/'implementation/elm-shared-geometry-carrier-v422';build=source/'qa/build-1791127807406303648/report.json';b=json.loads(build.read_text());assert b['passed'] and sha(build.parent/'elm-host')==b['binarySHA256']
for rel,digest in b['inputs'].items():assert sha(source/rel)==digest
ancestor=REPO/'implementation/elm-shared-application-reflow-fixture-v419'
for directory in ['src','adapter','assets']:
 for path in (source/directory).glob('*'):
  if path.is_file():assert sha(path)==sha(ancestor/path.relative_to(source))
files.extend([item(ROOT/'HANDOFF.md'),item(Path(__file__).resolve())])
manifest={'schema':1,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Bounded coherent observation2 GTK/menu integration and client ACK evidence; full geometry/release acceptance open','source':str(source),'runtime':str(REPO/'implementation/elm-geometry-bounds-runtime-v420'),'nativeReport':item(native),'clientACKReport':item(ack),'fullGeometryCampaignAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[],'reports':reports,'files':files,'symlinks':links}
for entry in files:assert sha(REPO/entry['path'])==entry['sha256']
for entry in links:assert os.readlink(REPO/entry['path'])==entry['target']
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifest':str(output),'sha256':sha(output)}))
