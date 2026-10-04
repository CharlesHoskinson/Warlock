import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('review-snapshot-'+str(time.time_ns()));OUT.mkdir();(OUT/'inputs').mkdir()
paths=[ROOT/n for n in ['REQUIREMENTS.md','HANDOFF.md','pins.json','adoption.json','qt-domains-build-report.json']]+[ROOT/'qa'/n for n in ['driver.py','native.py','shell.py','popup.py','keyboard.py','capture_scope.py','preflight.py']]+list((ROOT/'qa/helpers').glob('*.py'))+[ROOT/'native/qt-domains.cpp']+list((ROOT/'qa/owning-qt-source').glob('*'))
files={}
for p in paths:
 rel=p.relative_to(ROOT);dest=OUT/'inputs'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes());files[str(rel)]={'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'size':dest.stat().st_size,'path':str(dest)}
packet={'schema':1,'snapshotImmutable':True,'sourceHeld':False,'nativeAcceptance':False,'knownBorrowedShellFailure':'GTK297 six-second menu wait timeout, retained and not yet qualified by303','files':files}
path=OUT/'snapshot.json';path.write_text(json.dumps(packet,indent=2)+'\n');print(path);print(hashlib.sha256(path.read_bytes()).hexdigest())
