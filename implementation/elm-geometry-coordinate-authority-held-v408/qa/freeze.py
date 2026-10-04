import hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def item(path):return {'path':str(path.relative_to(REPO)),'sha256':sha(path),'size':path.stat().st_size}
files=[];links=[];reports=[]
for version in [404,405,406,407]:
 source=REPO/'implementation'/('elm-geometry-coordinate-authority-v'+str(version))
 for path in sorted(source.rglob('*')):
  if path.is_symlink():links.append({'path':str(path.relative_to(REPO)),'target':os.readlink(path)})
  elif path.is_file():files.append(item(path))
 for path in source.glob('qa/*/report.json'):
  report=json.loads(path.read_text());reports.append({**item(path),'passed':report['passed'],'nativeAcceptance':report.get('nativeAcceptance',False)})
  for rel,digest in report['artifacts'].items():assert sha(path.parent/rel)==digest
  if not report['passed']:continue
  for rel,digest in report['inputs'].items():assert sha(source/rel)==digest
  if 'core' in report:
   assert sha(Path(report['binary']))==report['binarySHA256']
   assert sha(Path(report['core']['path']))==report['core']['sha256']
   for field in ['dependencies','linkedLibraries']:
    for entry,digest in report[field].items():assert sha(Path(entry))==digest
   lineage=report['sourceLineage'];parent=Path(lineage['parent'])
   assert sha(parent/'native-build-report.json')==lineage['parentDescriptorSHA256']
   for rel,digest in lineage['parentSourceFiles'].items():assert sha(parent/rel)==digest
source=REPO/'implementation/elm-geometry-coordinate-authority-v407'
descriptor=json.loads((source/'native-build-report.json').read_text())
assert descriptor['result']=='pass' and not descriptor['nativeAcceptance']
build=Path(descriptor['pluginBuildReport']);assert sha(build)==descriptor['pluginBuildReportSHA256']
policy=source/'qa/projection-1791125233666945444/report.json'
report=json.loads(policy.read_text());assert report['passed'] and report['checks']==1710
assert len(report['controls'])==5 and all(control['detected'] for control in report['controls'])
assert sha(source/'candidate/ProspectiveGeometry.hpp')==sha(REPO/'implementation/elm-geometry-coordinate-policy-v402/candidate/ProspectiveGeometry.hpp')
files.extend([item(ROOT/'HANDOFF.md'),item(Path(__file__).resolve())])
manifest={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,
          'scope':'Compiled geometryProtocol2 native producer and owning ABI closure; no loading or shared host integration',
          'source':str(source),'buildReport':item(build),'policyReport':item(policy),
          'completedRequirementIds':[],'reports':reports,'files':files,'symlinks':links}
for entry in files:assert sha(REPO/entry['path'])==entry['sha256']
for entry in links:assert os.readlink(REPO/entry['path'])==entry['target']
output=ROOT/'qa/slice-manifest.json';assert not output.exists()
output.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'symlinks':len(links),'reports':len(reports),'manifest':str(output),'sha256':sha(output)}))
