"""Root-reviewed CPU freezer; no native acceptance or deadline changes."""
import hashlib,json,os,pathlib,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir()
r={'passed':False,'nativeAcceptance':False};external={}
def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def add(path,digest=None):
 p=pathlib.Path(path);assert p.is_absolute(),p
 if digest is not None:assert sha(p)==digest,('hash',str(p))
 if p.is_symlink():
  external[str(p)]={'symlink':os.readlink(p)};p=p.resolve(strict=True)
 assert p.is_file(),p
 external[str(p)]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)}
def row(path,value):
 p=pathlib.Path(path)
 if type(value) is str:value={'sha256':value}
 assert type(value) is dict and set(value)<= {'sha256','size','mode','symlink'},('row schema',str(p))
 if 'symlink' in value:assert p.is_symlink() and os.readlink(p)==value['symlink'];external[str(p)]={'symlink':value['symlink']};return
 add(p,value['sha256'])
 if 'size' in value:assert p.stat().st_size==value['size']
 if 'mode' in value:
  mode=int(value['mode'],8) if type(value['mode']) is str else value['mode'];assert p.stat().st_mode&0o777==mode

def held(path,digest):
 p=pathlib.Path(path);add(p,digest);m=json.loads(p.read_bytes());assert m['sourceHeld'] and m['evidenceIntegrityPassed']
 for rel,v in m['files'].items():row(p.parent/rel,v)
 for rel,v in m.get('symlinks',{}).items():assert os.readlink(p.parent/rel)==v;external[str(p.parent/rel)]={'symlink':v}
 for section in ('externalFiles','external'):
  assert type(m.get(section,{})) is dict
  for absolute,v in m.get(section,{}).items():assert pathlib.Path(absolute).is_absolute();row(absolute,v)
 for absolute,target in m.get('externalSymlinks',{}).items():
  assert pathlib.Path(absolute).is_absolute()
  if type(target) is dict:assert set(target)=={'symlink'};target=target['symlink']
  assert type(target) is str and os.readlink(absolute)==target;external[absolute]={'symlink':target}
 return m

def evidence(d,report):
 for section in ('inputs','sourceInputs','sourceFiles','qualifiedFiles','externalFiles','guardFiles'):
  for key,value in d.get(section,{}).items():row(pathlib.Path(key) if pathlib.Path(key).is_absolute() else ROOT/key,value)
 for key,value in d.get('proof',{}).get('files',{}).items():row(key,value)
 for key,value in d.get('artifacts',{}).items():
  p=(report.parent/key).resolve();assert p.is_relative_to(report.parent.resolve());row(p,value)

def reports_current(paths):
 selected={}
 for path,count in paths:
  p=ROOT/'qa'/path;d=json.loads(p.read_bytes());assert d['passed'] and d['nativeAcceptance'] is False and len(d['checks'])==count
  evidence(d,p)
  selected[path]={'sha256':sha(p),'checks':count}
 return selected
try:
 import parent_source
 parent_source.original((ROOT/'qa/native.py').read_text())
 origin=json.loads((ROOT/'adoption-origin.json').read_bytes())
 fixed={'baseManifest':('elm-own-popup-native-budget-timing-v373','296aef045de8e2926875c5da743ecb7a2c6a6e3594bed96817ef35d8dac5fbc8'),'collectorManifest':('elm-own-popup-parent-map-parallel-v382','76d9194b31524e658b164f4c70b9c39bc48c5a8146a8a1b88746642fa3f361e3'),'collectorReviewManifest':('elm-own-popup-parent-map-review-v386','e017693eb0bd4b7b5224fc79542dc5b387c447333be22c7bcc43e92455ba7206')}
 for key,(name,digest) in fixed.items():
  assert pathlib.Path(origin[key])==ROOT.parent/name/'component-manifest.json' and origin[key+'SHA256']==digest;held(origin[key],digest)
 runtime=json.loads((ROOT/'runtime-guard-pin.json').read_bytes());assert runtime['manifest']==str(ROOT.parent/'elm-own-popup-runtime-index-guard-v364/component-manifest.json') and runtime['sha256']=='4d940d15d8f1cfe24d60c927939fdf9b9f5d5c7b0a778211992f067c43d9e1b6';held(runtime['manifest'],runtime['sha256'])
 review_pin=json.loads((ROOT/'index-review-pin.json').read_bytes());assert review_pin['manifest']==str(ROOT.parent/'elm-own-popup-runtime-index-review-v366/component-manifest.json') and review_pin['sha256']=='bfb418b1d48e44bd4f6d2c6aa93938b56f1a453894907f05d20f9db06423842f';held(review_pin['manifest'],review_pin['sha256'])
 # Actual source/cache/executable/library/header/artifact closure comes from
 # held ancestors AND each source-current selected report, never inferred.
 assert len(sys.argv)==8
 report_paths=[]
 for argument,count in zip(sys.argv[1:],(15,14,9,35,31,32,14)):
  p=pathlib.Path(argument).resolve();assert p.is_relative_to(ROOT/'qa');report_paths.append((str(p.relative_to(ROOT/'qa')),count))
 selected=reports_current(report_paths)
 peer=ROOT.parent/'elm-own-popup-native-parent-review-v394';report=peer/'qa/verify-1791175386801903854/report.json';d=json.loads(report.read_bytes());assert d['passed'] and d['nativeAcceptance'] is False and len(d['suites'])==7
 add(report)
 expected=list(zip(('parent-test.py','loader-test.py','wrapper-test.py','test.py','origin-adopted-test.py','targeted-adopted-test.py','timing-adopted-test.py'),(15,14,9,35,31,32,14)))
 for suite,(script,count) in zip(d['suites'],expected):
  assert set(suite)=={'script','checks','report','sha256'} and suite['script']==script and type(suite['checks']) is int and suite['checks']==count
  child=pathlib.Path(suite['report']);assert child==report.parent/pathlib.Path(script).stem/'report.json' and child.resolve().is_relative_to(report.parent.resolve());add(child,suite['sha256'])
  child_data=json.loads(child.read_bytes());assert child_data['passed'] is True and child_data['nativeAcceptance'] is False and len(child_data['checks'])==count;evidence(child_data,child)
 for p,v in d['inputs'].items():row(p,v)
 for rel,v in d['artifacts'].items():row(report.parent/rel,v)
 # Retain all independently captured predecessors, unsafe cache/self-verifier
 # witnesses and exact source snapshots. This is a mutable-review snapshot,
 # not a fabricated held peer manifest or circular final review dependency.
 for p in sorted(peer.rglob('*')):
  if p.is_symlink():external[str(p)]={'symlink':os.readlink(p)}
  elif p.is_file():add(p)
 files={};links={}
 for p in sorted(ROOT.rglob('*')):
  if p.is_relative_to(OUT) or p.name=='component-manifest.json':continue
  if p.is_symlink():links[str(p.relative_to(ROOT))]=os.readlink(p)
  elif p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)}
 manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'nativePerformanceAccepted':False,'ownBlockerGrantQualified':False,'scope':'Source-executed external parent collect qualification, all-row full-hash adoption with original307/319/315/AQ155 tuple and6s/3s clocks; no GUI/performance/authority transfer. Direct internal wrapper methods are not adversarial boundary; uncertain native worker cleanup remains open.','files':files,'symlinks':links,'externalFiles':external,'selectedReports':selected,'independentReplayReport':str(report),'independentReplayReportSHA256':sha(report),'independentReplayHeld':False,'originalNativeBodyAfterClosedDelta':'373','collectorManifestSHA256':origin['collectorManifestSHA256'],'collectorReviewManifestSHA256':origin['collectorReviewManifestSHA256'],'runtimeGuardManifestSHA256':'4d940d15d8f1cfe24d60c927939fdf9b9f5d5c7b0a778211992f067c43d9e1b6'}
 temporary=ROOT/'component-manifest.json.pending';temporary.write_text(json.dumps(manifest,indent=2)+'\n');os.replace(temporary,ROOT/'component-manifest.json')
 r.update(passed=True,ownFiles=len(files),externalFiles=len(external),manifestSHA256=sha(ROOT/'component-manifest.json'))
except BaseException as e:
 import traceback;r['error']=repr(e);r['traceback']=traceback.format_exc()
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
