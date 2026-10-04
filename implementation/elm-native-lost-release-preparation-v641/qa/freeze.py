import hashlib,json,os,pathlib,resource,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def row(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
report=ROOT/'qa/controls-1791153465947021714/report.json';r=json.loads(report.read_text());assert r['passed'] and not r['nativeLaunched']
for name,digest in r['sources'].items():assert row(ROOT/name)['sha256']==digest,name
parent=REPO/'implementation/elm-release-delivery-attestation-v624';pins={}
for source,target in [('adapter','fixture-adapter'),('native','fixture-native')]:
 for p in (parent/source).glob('*'):
  if not p.is_file():continue
  name=target+'/'+p.name;pins[name]=row(p);assert row(ROOT/name)==pins[name],name
for source,target in [('fixture.py','fixture.py'),('qa/inspection.py','qa/inspection.py')]:
 p=REPO/'implementation/elm-reconciliation-native-journey-v627'/source;pins[target]=row(p);assert row(ROOT/target)==pins[target],target
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
files={str(p.relative_to(ROOT)):row(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p!=manifest}
links={str(p.relative_to(ROOT)):os.readlink(p) for p in ROOT.rglob('*') if p.is_symlink()}
value={'schema':1,'component':'elm-native-lost-release-preparation-v641','report':str(report),'checks':r['assertions'],'copiedFixtureInputs':pins,'nativeLaunched':False,'targetPreflightPending':True,'files':files,'intentionalUnsafeFixtureSymlinks':links}
manifest.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
for name,expected in files.items():assert row(ROOT/name)==expected,name
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'checks':r['assertions']}))
