import hashlib,json,os,pathlib,resource,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
PARENT=ROOT.parent/'elm-durable-reservation-release-v608'
def row(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
pins={}
for directory in ['adapter','native']:
    source={str(p.relative_to(PARENT)):p for p in (PARENT/directory).rglob('*') if p.is_file()}
    target={str(p.relative_to(ROOT)):p for p in (ROOT/directory).rglob('*') if p.is_file()}
    assert set(target)==set(source)|({'adapter/delivery_ledger.py'} if directory=='adapter' else set())
    for name,path in source.items():
        pins[name]=row(path);assert pins[name]==row(target[name]),name
REPORT=ROOT/'qa/tests-1791151811583372012/report.json';r=json.loads(REPORT.read_text())
assert r['passed'] and r['nativeAcceptance'] is False and r['productionWired'] is False
for name,digest in r['sourceSHA256'].items():assert row(ROOT/name)['sha256']==digest,name
assert row(ROOT/'qa/inherited608.py')==row(PARENT/'qa/test.py')
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
files={str(p.relative_to(ROOT)):row(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p!=manifest}
links={str(p.relative_to(ROOT)):{'kind':'symlink','target':os.readlink(p)} for p in sorted(ROOT.rglob('*')) if p.is_symlink()}
value={'schema':1,'component':'elm-release-delivery-attestation-v624','parent':str(PARENT),'unchangedParentProductionFiles':pins,'report':str(REPORT.relative_to(ROOT)),'assertions':r['assertions'],'inherited608Assertions':r['inherited608Assertions'],'nativeAcceptance':False,'productionWired':False,'files':files,'intentionalUnsafeFixtureSymlinks':links}
manifest.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
for name,expected in files.items():assert row(ROOT/name)==expected,name
for name,expected in links.items():assert (ROOT/name).is_symlink() and os.readlink(ROOT/name)==expected['target'],name
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'unchangedProductionFiles':len(pins),'assertions':r['assertions'],'inherited608Assertions':r['inherited608Assertions']}))
