import hashlib,json,pathlib,resource,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
PARENT=ROOT.parent/'elm-reconciliation-integrated-gui-v616'
def row(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
build_path=pathlib.Path(json.loads((ROOT/'qa/current-build.json').read_text())['report'])
build=json.loads(build_path.read_text());assert build['passed'] and 'qa/current-build.json' not in build['inputs']
for name,digest in build['inputs'].items():assert row(ROOT/name)['sha256']==digest,name
assert row(build_path.parent/'elm-host')['sha256']==build['binarySHA256']
for name,digest in build['artifacts'].items():assert row(build_path.parent/name)['sha256']==digest,name
pins={}
for directory in ['src','native','adapter','assets']:
    for p in (PARENT/directory).rglob('*'):
        if not p.is_file():continue
        name=str(p.relative_to(PARENT))
        if name=='adapter/daemon.py':continue
        pins[name]=row(p);assert row(ROOT/name)==pins[name],name
startup=ROOT/'qa/startup-1791152207897182745/report.json';r=json.loads(startup.read_text());assert r['passed']
for name,digest in r['sourceSHA256'].items():assert row(ROOT/name)['sha256']==digest,name
public=ROOT/'qa/tests-1791152233703381205/report.json';p=json.loads(public.read_text());assert p['passed']
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
files={str(p.relative_to(ROOT)):row(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=manifest}
value={'schema':1,'component':'elm-reconciliation-startup-order-v626','parent':str(PARENT),'unchangedProductionFiles':pins,'changedProductionFiles':['adapter/daemon.py'],'buildReport':str(build_path),'startupReport':str(startup),'publicElmReport':str(public),'nativeAcceptance':False,'files':files}
manifest.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
for name,expected in files.items():assert row(ROOT/name)==expected,name
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'unchangedProductionFiles':len(pins),'startupChecks':r['assertions'],'publicElmChecks':len(p['checks'])}))
