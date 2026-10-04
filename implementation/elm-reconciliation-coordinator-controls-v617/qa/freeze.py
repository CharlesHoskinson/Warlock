import hashlib,json,pathlib,resource,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
PARENT=ROOT.parent/'elm-retirement-recovery-coordinator-v615'
REPORT='qa/tests-1791150400922859665/report.json'
def row(path):
    return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':path.stat().st_size}
pins={}
for directory in ['adapter','native']:
    source={str(p.relative_to(PARENT)):p for p in (PARENT/directory).rglob('*') if p.is_file()}
    target={str(p.relative_to(ROOT)):p for p in (ROOT/directory).rglob('*') if p.is_file()}
    assert set(source)==set(target)
    for name,p in source.items():
        assert not p.is_symlink() and not target[name].is_symlink()
        pins[name]=row(p)
        assert pins[name]==row(target[name]),name
report=json.loads((ROOT/REPORT).read_text())
assert report['passed'] and report['nativeAcceptance'] is False and report['frontendIntegrated'] is False
for name,digest in report['sourceSHA256'].items():
    assert row(ROOT/name)['sha256']==digest,name
manifest=ROOT/'component-manifest.json'
assert not manifest.exists()
files={str(p.relative_to(ROOT)):row(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=manifest}
assert all(not (ROOT/name).is_symlink() for name in files)
value={'schema':1,'component':'elm-reconciliation-coordinator-controls-v617','parent':str(PARENT),'parentProductionFiles':pins,'report':REPORT,'reportAssertions':report['assertions'],'nativeAcceptance':False,'frontendIntegrated':False,'files':files}
manifest.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
for name,expected in files.items():assert row(ROOT/name)==expected,name
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'productionFiles':len(pins),'assertions':report['assertions']}))
