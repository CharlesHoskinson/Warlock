import hashlib,json,os,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'usabilityAcceptance':False,'checks':[]}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
try:
 selected=ROOT/'qa/review-1791119327744462474/report.json';actual=json.loads(selected.read_text());check('compiled reproduction PASS',actual['passed'] is True)
 for relative,digest in actual['sources'].items():check('tested source '+relative,sha(ROOT/relative)==digest and sha(selected.parent/'inputs'/relative)==digest)
 for relative,digest in actual['artifacts'].items():check('captured artifact '+relative,sha(selected.parent/relative)==digest)
 failed=ROOT/'qa/usability-1791119273559384011/report.json';requirements=json.loads(failed.read_text());check('three actual required failures preserved',requirements['passed'] is False and len(requirements['checks'])==3 and all(c['passed'] is False for c in requirements['checks']))
 check('failed usability exact compiled input',sha(ROOT/requirements['input'])==requirements['inputSHA256'])
 check('failed usability exact test source',sha(ROOT/'qa/usability.py')==requirements['sourceSHA256'])
 up=json.loads((ROOT/'upstream.json').read_text());source=Path(up['sourceRoot']);check('source132 component unchanged',sha(source/'component-manifest.json')==up['componentManifestSHA256'])
 for relative,digest in up['sources'].items():check('unchanged upstream '+relative,sha(source/relative)==digest)
 for relative,digest in up['sources'].items():
  if relative!='src/BatchReplay.elm':check('actual production byte-exact '+relative,sha(ROOT/relative)==digest)
 report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if report['passed']:
 files={};links={}
 for p in sorted(ROOT.rglob('*')):
  if 'elm-stuff' in p.parts or p.name=='held-source-manifest.json':continue
  if p.is_symlink():links[str(p.relative_to(ROOT))]=os.readlink(p)
  elif p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':p.stat().st_mode&0o777}
 manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'usabilityAcceptance':False,'files':files,'symlinks':links,'compiledReview':{'path':str(selected.relative_to(ROOT)),'sha256':sha(selected),'checks':len(actual['checks'])},'failedRequirements':{'path':str(failed.relative_to(ROOT)),'sha256':sha(failed),'failed':3},'freezeReport':{'path':str((OUT/'report.json').relative_to(ROOT)),'sha256':sha(OUT/'report.json')},'scope':'Unchanged V132 compiled failure reproduction; no corrective source changes, native launch, receipts or replay'}
 with (ROOT/'qa/held-source-manifest.json').open('x') as f:f.write(json.dumps(manifest,indent=2)+'\n')
print(OUT/'report.json');raise SystemExit(not report['passed'])
