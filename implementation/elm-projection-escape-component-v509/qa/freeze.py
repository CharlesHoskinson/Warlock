import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-projection-native-escape-combined-v507'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=REPO/'implementation/elm-projection-retry-exhaustion-v498';escape=REPO/'implementation/elm-native-escape-competing-key-v190'
for directory in ['src','native','adapter','assets']:
 for p in (SOURCE/directory).glob('*'):
  if not p.is_file():continue
  rel=p.relative_to(SOURCE);ancestor=escape if str(rel) in ['native/shared-context.h','native/shared-context-test.c'] else old
  assert sha(p)==sha(ancestor/rel),str(rel)
model=escape/'component-manifest.json';assert sha(model)=='b47f28d956318dce0bb3d630debadf3c3fd86f6f2faf60b65213ed58c253f58c'
parent=REPO/'implementation/elm-projection-retry-boundary-qualified-v502/qa/slice-manifest.json';assert sha(parent)=='0b0f01cb2d60c228a8f51997279b56852df4ccb93e861ac5c64c18c787a053fc'
for manifest,base in [(model,escape),(parent,REPO)]:
 for row in json.loads(manifest.read_text())['files']:
  if 'sha256' in row:assert sha(base/row['path'])==row['sha256']
build=next((SOURCE/'qa').glob('build-*/report.json'));b=json.loads(build.read_text());assert b['passed'];assert sha(build.parent/'elm-host')==b['binarySHA256']
for rel,digest in b['inputs'].items():assert sha(SOURCE/rel)==digest and sha(build.parent/'inputs'/rel)==digest
for section in ['compilerDependencies','tools','linkedLibraries']:
 for path,row in b[section].items():assert sha(Path(path))==row['sha256']
assert 'shared-context-checks: 168' in (build.parent/'context-guard-tests.stdout').read_text()
controls=next((SOURCE/'qa').glob('mutations-*/report.json'));c=json.loads(controls.read_text());assert c['passed'] and len(c['controls'])==11 and all(row['accepted'] for row in c['controls'])
for row in c['controls']:assert sha(controls.parent/row['name']/'checks')==row['binarySHA256']
typed=next((REPO/'implementation/elm-projection-escape-typed-qa-v508/qa').glob('checks-*/report.json'));t=json.loads(typed.read_text());assert t['passed'] and len(t['checks'])==14
files=[];links=[]
for directory in [SOURCE,REPO/'implementation/elm-projection-escape-typed-qa-v508',REPO/'implementation/elm-projection-escape-integration-review-v506']:
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())})
  elif p.is_file():files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
files.append({'path':str(Path(__file__).resolve().relative_to(REPO)),'sha256':sha(Path(__file__)),'size':Path(__file__).stat().st_size})
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':str(SOURCE.relative_to(REPO)),'buildReport':str(build),'buildReportSHA256':sha(build),'mutationReport':str(controls),'mutationReportSHA256':sha(controls),'typedReport':str(typed),'typedReportSHA256':sha(typed),'helperChecks':168,'mutantsRejected':10,'typedCompiledCases':14,'nativeAcceptance':False,'fullReleaseAccepted':False,'completedRequirementIds':[],'files':files,'symlinks':links,'parentManifest':str(parent),'parentManifestSHA256':sha(parent),'escapeManifest':str(model),'escapeManifestSHA256':sha(model)}
p=ROOT/'component-manifest.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(p)}))
