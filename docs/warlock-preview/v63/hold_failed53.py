import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path(__file__).resolve().parents[3];ROOT=REPO/'implementation/warlock-preview-provider-v53';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=ROOT/'qa/build-1791296360836340389/report.json';b=json.loads(report.read_text());assert not b['passed'] and b['commands'][-1]['name']=='catalog-enrollment-replay'
assert 'Removal retains original exact frame Release' in (report.parent/'catalog-enrollment-replay.stderr').read_text()
for rel,h in b['inputs'].items():assert sha(ROOT/rel)==h,rel
files={}
for p in sorted(ROOT.rglob('*')):
 rel=p.relative_to(ROOT)
 if any(part in {'__pycache__','elm-stuff','mutable-elm-home'} for part in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'passed':False,'scope':scope,'buildReport':str(report),'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'failure':'Catalog replay incorrectly expected accepted cached frame release on metadata removal alone. Original Close retains accepted historical resource until own native source denial or expiry. Fresh54 corrects controlled stimulus to exact original source denial before Release; candidate cancellation, original scope/job/deadline and accepted-cache ownership remain intact.'},indent=2)+'\n')
print(json.dumps({'sourceHeld':True,'files':len(files),'failedReportRetained':True}))
