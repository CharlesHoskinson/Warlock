import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/'elm-paged-history-archive-v629'
def row(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
pins={}
for p in sorted((ROOT/'ancestry').iterdir()):
 original=PARENT/p.name;assert row(p)==row(original),p.name;pins[p.name]=row(original)
report=ROOT/'qa/tests-1791154696119822432/report.json';r=json.loads(report.read_bytes());assert r['passed'] and r['assertions']==362
for name,digest in r['sourceSHA256'].items():assert row(ROOT/name)['sha256']==digest,name
model=ROOT/'qa/model-1791154554659366036/report.json';m=json.loads(model.read_bytes());assert m['passed'] and len(m['mutationControls'])==3
assert all(x['typecheckExit']==0 and x['counterexampleExit']!=0 for x in m['mutationControls'])
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
assert not any(p.is_symlink() for p in ROOT.rglob('*'))
files={str(p.relative_to(ROOT)):row(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=manifest}
value={'schema':1,'component':ROOT.name,'parent':str(PARENT),'unchangedFrozen629Inputs':pins,'report':str(report.relative_to(ROOT)),'modelReport':str(model.relative_to(ROOT)),'assertions':362,'retainedRecords':1026,'nativeAcceptance':False,'ledgerIntegrated':False,'S15Accepted':False,'powerLossQualified':False,'files':files}
manifest.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
for name,expected in files.items():assert row(ROOT/name)==expected,name
print(json.dumps({'manifest':str(manifest),'sha256':row(manifest)['sha256'],'files':len(files),'assertions':362,'retainedRecords':1026}))
