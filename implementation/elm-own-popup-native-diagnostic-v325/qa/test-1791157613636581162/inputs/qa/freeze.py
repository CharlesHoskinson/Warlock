"""Protected source/evidence hold, no native acceptance."""
import json,pathlib,sys,time,stat,resource
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
from preflight import verify,checked_guard,sha
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False}
try:
 test=ROOT/'qa/test-1791157510866833972/report.json';e=json.loads(test.read_text());assert e['passed'] is True and len(e['checks'])==26
 _,_,_,_,_,_,external=verify();_,guard=checked_guard();external.update(guard)
 for rel,digest in e['inputs'].items():assert sha(ROOT/rel)==digest
 rows={};links={}
 for p in sorted(ROOT.rglob('*')):
  if p==ROOT/'component-manifest.json' or p.is_relative_to(OUT) or '__pycache__' in p.parts:continue
  rel=str(p.relative_to(ROOT))
  if p.is_symlink():links[rel]=str(p.readlink());continue
  if p.is_file():rows[rel]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'nativeReadiness':False,'scope':'Executable picker map/wholegrab/close/fresh-facts diagnostic; no GUI run or eligibility grant','testReport':str(test),'testReportSHA256':sha(test),'files':rows,'symlinks':links,'externalFiles':external,'runtimeGuardManifestSHA256':'e92e4a0ce189606b9455a4634d416d11a2e7342fa42c989a5911d788c6faf9ce'}
 (ROOT/'component-manifest.json').write_text(json.dumps(packet,indent=2)+'\n');r.update(passed=True,manifestSHA256=sha(ROOT/'component-manifest.json'),ownFiles=len(rows),externalFiles=len(external))
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
