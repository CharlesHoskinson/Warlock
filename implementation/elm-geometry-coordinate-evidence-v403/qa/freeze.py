import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def item(path):return {'path':str(path.relative_to(REPO)),'sha256':sha(path),'size':path.stat().st_size}
paths=[]
for version in [399,400,401,402]:
 source=REPO/'implementation'/('elm-geometry-coordinate-policy-v'+str(version))
 for path in sorted(source.rglob('*')):
  assert not path.is_symlink(),str(path)
  if path.is_file():paths.append(path)
reportPaths=[path for path in paths if path.name=='report.json']
reports=[]
for path in reportPaths:
 report=json.loads(path.read_text());reports.append({**item(path),'passed':report['passed'],'checks':report.get('checks')})
 for rel,digest in report['artifacts'].items():assert sha(path.parent/rel)==digest
accepted=REPO/'implementation/elm-geometry-coordinate-policy-v402/qa/projection-1791124436709484431/report.json'
report=json.loads(accepted.read_text());assert report['passed'] and report['checks']==1710
assert len(report['controls'])==5 and all(control['detected'] for control in report['controls'])
for rel,digest in report['inputs'].items():assert sha(accepted.parents[2]/rel)==digest
for field in ['owningBuildReport','owningLibrary']:
 ref=report[field];assert sha(Path(ref['path']))==ref['sha256']
for path,digest in report['owningMathHeaders'].items():assert sha(Path(path))==digest
audit=REPO/'implementation/elm-geometry-constraint-coordinate-review-v155/reviewed-inputs.json'
for path,entry in json.loads(audit.read_text())['files'].items():assert sha(Path(path))==entry['sha256']
paths.extend([ROOT/'HANDOFF.md',Path(__file__).resolve()])
files=[item(path) for path in paths]
manifest={'schema':1,'scope':'Bounded zero-origin prospective geometry prototype; no native or wire acceptance','nativeAcceptance':False,'completedRequirementIds':[],
          'acceptedReport':item(accepted),'reports':reports,'sourceAudit':item(audit),'files':files}
for path,entry in zip(paths,files):assert sha(path)==entry['sha256']
output=ROOT/'qa/slice-manifest.json';assert not output.exists()
output.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifest':str(output),'sha256':sha(output)}))
