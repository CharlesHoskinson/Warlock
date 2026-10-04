"""Hold only exact CPU-qualified sources; retain usability failure ancestry."""
import hashlib,json,os,re,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'releaseAcceptance':False,'checks':[]}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
selected=[('qa/local-unsent-1791120515099922497/report.json','proof'),('qa/review-1791120515102404593/report.json','registration'),('regression/current-semantic/qa/replay-1791120515113903395/report.json','semantic'),('regression/post-close/qa/replay-1791120515117303804/report.json','post-close')]
try:
 evidence=[]
 for relative,kind in selected:
  path=ROOT/relative;j=json.loads(path.read_text());check('protected PASS '+kind,j['passed'] is True)
  if kind=='proof':
   check('certificate62 and deferred3',len(j['checks'])==62 and len(j['deferredChecks'])==3)
   check('optimized three actual programs',all(any(c['name']==name and c['exitCode']==0 for c in j['commands']) for name in ['actual-main-compile','actual-bar-compile','actual-popup-compile']))
   for rel,digest in j['inputs'].items():check('tested proof source '+rel,sha(ROOT/rel)==digest and sha(path.parent/'inputs'/rel)==digest)
   for name,digest in j['compilerDependencies'].items():check('actual C dependency '+name,sha(name)==digest)
  elif kind=='registration':
   check('compiled registration25',len(j['checks'])==25)
   for rel,digest in j['sources'].items():check('tested registration source '+rel,sha(ROOT/rel)==digest and sha(path.parent/'inputs'/rel)==digest)
  else:
   if kind=='semantic':check('current semantic152',sum(x['checks'] for x in j['stagedSuites'].values())==152 and all(x['passed'] for x in j['stagedSuites'].values()))
   else:check('post-close59',j['postCloseChecks']['passed'] and j['postCloseChecks']['checks']==59)
   for rel,digest in j['sourceInputs'].items():check('tested regression production '+kind+' '+rel,sha(ROOT/rel)==digest)
   for rel,digest in j['qaInputs'].items():check('tested regression oracle '+kind+' '+rel,sha(path.parents[2]/rel)==digest)
  for rel,digest in j['artifacts'].items():check('retained artifact '+kind+' '+rel,sha(path.parent/rel)==digest)
  evidence.append({'path':relative,'sha256':sha(path),'scope':kind})
 up=json.loads((ROOT/'upstream.json').read_text());parent=Path(up['parent']);manifest=parent/'component-manifest.json';check('frozen132 exact manifest',sha(manifest)==up['componentManifestSHA256'])
 pm=json.loads(manifest.read_text())
 for row in pm['ownProduction']:check('frozen132 source '+row['path'],sha(parent/row['path'])==row['sha256'])
 for row in pm['evidence']:check('frozen132 evidence '+row['path'],sha(row['path'])==row['sha256'])
 for directory in ['native','assets','adapter']:
  for path in (parent/directory).rglob('*'):
   if path.is_file():check('unchanged candidate owning '+str(path.relative_to(parent)),sha(ROOT/path.relative_to(parent))==sha(path))
 for p in (parent/'src').glob('*.elm'):
  if p.name not in ['Shell.elm','TaskbarShell.elm','OutputController.elm','BatchReplay.elm']:check('unchanged actual module '+p.name,sha(ROOT/'src'/p.name)==sha(p))
 ancestor=REPO/'implementation/elm-shared-registration-refusal-review-v135';held=ancestor/'qa/held-source-manifest.json';check('held failure review exact',sha(held)=='9efef5ac62c295e6c74c55e17e45993bbc7b1289d1af21c9f39a2a70ae1480b1')
 for rel,row in json.loads(held.read_text())['files'].items():check('held failure source/evidence '+rel,sha(ancestor/rel)==row['sha256'])
 failed=ancestor/'qa/usability-1791119273559384011/report.json';check('original three failures retained',json.loads(failed.read_text())['passed'] is False)
 probe=ROOT/'qa/local-unsent-1791120515099922497/probe';linked=subprocess.run(['ldd',str(probe)],capture_output=True,text=True,check=True);(OUT/'probe.ldd').write_text(linked.stdout);check('CPU helper owning link closure resolves','not found' not in linked.stdout)
 libraries={}
 for line in linked.stdout.splitlines():
  match=re.search(r'(?:=>\s+)?(/[^\s]+)\s+\(',line)
  if match:
   lib=Path(match.group(1)).resolve(strict=True);libraries[str(lib)]=sha(lib)
 report.update(passed=True,evidence=evidence,linkedLibraries=libraries,freezeSourceSHA256=sha(Path(__file__)))
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if report['passed']:
 files={};links={}
 for p in sorted(ROOT.rglob('*')):
  if 'elm-stuff' in p.parts or p.name=='held-source-manifest.json':continue
  if p.is_symlink():links[str(p.relative_to(ROOT))]=os.readlink(p)
  elif p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':p.stat().st_mode&0o777}
 held={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'releaseAcceptance':False,'files':files,'symlinks':links,'evidence':evidence,'counts':{'certificate':62,'deferredAttach':3,'registration':25,'currentSemantic':211},'sourceParent':up,'failedRequirements':{'path':str(failed),'sha256':sha(failed)},'freezeReport':{'path':str((OUT/'report.json').relative_to(ROOT)),'sha256':sha(OUT/'report.json')},'scope':'Dedicated internal local non-submission disposition and bounded authenticated recovery; CPU actual controller/C helper only. No native certificate/outcome fabricated, unrelated actual Pending/Unknown preserved.'}
 with (ROOT/'qa/held-source-manifest.json').open('x') as stream:stream.write(json.dumps(held,indent=2)+'\n')
print(OUT/'report.json');raise SystemExit(not report['passed'])
