"""Protected source/evidence hold, no native acceptance."""
import json,pathlib,sys,time,stat,resource
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
from preflight import verify,checked_guard,sha
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False}
try:
 test=pathlib.Path(sys.argv[1]).resolve();assert test.is_relative_to(ROOT/'qa');e=json.loads(test.read_text());assert e['passed'] is True and len(e['checks'])>=26
 selector=pathlib.Path(sys.argv[2]).resolve();assert selector.is_relative_to(ROOT/'qa');selected=json.loads(selector.read_text());assert selected['passed'] is True and len(selected['checks'])==27
 for source,digest in selected['inputs'].items():assert sha(source)==digest
 _,_,_,_,_,_,external=verify();_,guard=checked_guard();external.update(guard)
 origin=json.loads((ROOT/'target-helper-origin.json').read_text())
 for name,row in origin.items():
  assert sha(row['path'])==row['sha256'] and sha(ROOT/'qa/helpers'/name)==row['sha256'];external[row['path']]=row['sha256']
 for rel,digest in e['inputs'].items():assert sha(ROOT/rel)==digest
 rows={};links={}
 for p in sorted(ROOT.rglob('*')):
  if p==ROOT/'component-manifest.json' or p.is_relative_to(OUT) or '__pycache__' in p.parts:continue
  rel=str(p.relative_to(ROOT))
  if p.is_symlink():links[rel]=str(p.readlink());continue
  if p.is_file():rows[rel]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'nativeReadiness':False,'scope':'Exact current rendered DOM selector fix; inherited325 picker predicates/budgets/tuple unchanged; original325 failure retained; no new GUI run or eligibility grant','testReport':str(test),'testReportSHA256':sha(test),'selectorReport':str(selector),'selectorReportSHA256':sha(selector),'files':rows,'symlinks':links,'externalFiles':external,'runtimeGuardManifestSHA256':'66527cb94aa2fc22e7b2bfc29af1e868a90a42668a2008af33adcc204583960f'}
 (ROOT/'component-manifest.json').write_text(json.dumps(packet,indent=2)+'\n');r.update(passed=True,manifestSHA256=sha(ROOT/'component-manifest.json'),ownFiles=len(rows),externalFiles=len(external))
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
