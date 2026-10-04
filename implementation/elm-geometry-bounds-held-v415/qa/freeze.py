import ast,hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def item(path):return {'path':str(path.relative_to(REPO)),'sha256':sha(path),'size':path.stat().st_size}
names=['elm-geometry-coordinate-authority-v409','elm-shared-geometry-bounds-v410','elm-geometry-bounds-consumer-qa-v411','elm-geometry-bounds-consumer-qa-v412','elm-geometry-bounds-negotiation-qa-v413','elm-geometry-size-model-v414']
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
  if not report['passed']:continue
  for rel,digest in report.get('inputs',{}).items():
   p=Path(rel) if Path(rel).is_absolute() else source/rel
   assert sha(p)==digest
  if 'sourceSHA256' in report:assert sha(source/'spec/recovery.qnt')==report['sourceSHA256']
source=REPO/'implementation/elm-geometry-coordinate-authority-v409'
native=source/'qa/build-1791125683067025764/report.json';report=json.loads(native.read_text());assert report['passed']
assert sha(Path(report['binary']))==report['binarySHA256']
for field in ['dependencies','linkedLibraries']:
 for path,digest in report[field].items():assert sha(Path(path))==digest
policy=source/'qa/projection-1791125593548153454/report.json';report=json.loads(policy.read_text());assert report['passed'] and report['checks']==1715 and len(report['controls'])==6 and all(control['detected'] for control in report['controls'])
consumer=REPO/'implementation/elm-geometry-bounds-consumer-qa-v412/checks-1791126321935256810/report.json';report=json.loads(consumer.read_text());assert report['passed'] and report['checks']==68 and report['owningCppProjections']==36
model=REPO/'implementation/elm-geometry-size-model-v414/qa/model-1791126384856853307/report.json';report=json.loads(model.read_text());assert report['passed'] and report['namedScenarios']==12 and report['unsafeCombinedFixed']['detected']
for path in (REPO/'implementation/elm-shared-geometry-bounds-v410/adapter').glob('*.py'):ast.parse(path.read_text())
files.extend([item(ROOT/'HANDOFF.md'),item(Path(__file__).resolve())])
manifest={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Matching observation2 native/Python/Elm implementation; bounded compile/decoder/model proof, shared replay/native integration pending','completedRequirementIds':[],'reports':reports,'files':files,'symlinks':links}
for entry in files:assert sha(REPO/entry['path'])==entry['sha256']
for entry in links:assert os.readlink(REPO/entry['path'])==entry['target']
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifest':str(output),'sha256':sha(output)}))
