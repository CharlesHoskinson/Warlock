import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path(__file__).resolve().parents[3];ROOT=REPO/'implementation/warlock-preview-provider-v55';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=ROOT/'qa/build-1791297945383010245/report.json';b=json.loads(report.read_text());assert not b['passed'] and b['commands'][-1]['name']=='receiver-extension-physical-tests'
assert 'second physical destroy precedes exact final ACK' in (report.parent/'receiver-extension-physical-tests.stderr').read_text()
for rel,h in b['inputs'].items():assert sha(ROOT/rel)==h,rel
files={}
for p in sorted(ROOT.rglob('*')):
 rel=p.relative_to(ROOT)
 if any(part in {'__pycache__','elm-stuff','mutable-elm-home'} for part in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'passed':False,'scope':scope,'buildReport':str(report),'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'failure':'Receiver growth test omitted explicit native consumer completion after second GIO reader close. Broker correctly refuses physical destruction without consumer fence. Fresh56 adds actual explicit consumer completion and a prior refusal assertion; original epoch/authorization/budgets/fence semantics remain unchanged.'},indent=2)+'\n')
print(json.dumps({'sourceHeld':True,'files':len(files),'failedReportRetained':True}))
