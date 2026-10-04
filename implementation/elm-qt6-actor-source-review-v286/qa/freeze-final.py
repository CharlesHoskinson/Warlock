import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OWNER=ROOT.parent/'elm-qt6-owned-actor-v285'
def item(p):
 s=p.stat();return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':s.st_size,'mode':oct(s.st_mode&0o777)}
old=ROOT/'qa/deadline-1791149388419479975/report.json';new=ROOT/'qa/deadline-1791149457090482189/report.json'
a=json.loads(old.read_text());b=json.loads(new.read_text());assert a['passed'] and not a['correctionAccepted'] and b['passed'] and b['correctionAccepted']
assert b['sourceSHA256']==item(OWNER/'qa/actor.py')['sha256']
for name in ['actor.py','journal.py']:
 dest=ROOT/'qa'/('corrected-'+name);assert dest.read_bytes()==(OWNER/'qa'/name).read_bytes() if dest.exists() else True
 if not dest.exists():dest.write_bytes((OWNER/'qa'/name).read_bytes())
external={str(p):item(p) for p in [OWNER/'qa/actor.py',OWNER/'qa/journal.py',OWNER/'REQUIREMENTS.md',OWNER/'qa/actor-1791149432244905391/report.json',OWNER/'qa/commands-1791149432655542921/report.json']}
for p in list(external)[-2:]:assert json.loads(Path(p).read_text())['passed']
files={str(p.relative_to(ROOT)):item(p) for p in sorted(ROOT.rglob('*')) if p.is_file()}
packet={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Independent actual Qt actor boundary/deadline review only','files':files,'externalFiles':external,'oldDeadlineWitness':str(old.relative_to(ROOT)),'correctedDeadlineEvidence':str(new.relative_to(ROOT))}
path=ROOT/'component-manifest.json';assert not path.exists();path.write_text(json.dumps(packet,indent=2)+'\n')
for name,row in files.items():assert item(ROOT/name)==row
for name,row in external.items():assert item(Path(name))==row
print(path);print(item(path)['sha256'])
