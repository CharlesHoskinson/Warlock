"""Verify positive/negative evidence closure; full minimize acceptance stays false."""
import datetime,hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parent
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Protected launcher required'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pair_path=ROOT/'qa/build-pair-manifest.json';pair=json.loads(pair_path.read_text());assert pair['passed']
for relative,digest in pair['files'].items():assert sha(ROOT/relative)==digest,relative
paths=['qa/native-1791058639153902245/report.json','qa/native-1791058947594074854/report.json','qa/native-1791059374174458273/report.json'];rows=[]
for relative in paths:
 p=ROOT/relative;r=json.loads(p.read_text());assert r['cleanupPassed'] and not r['mainDesktopActions']
 assert r['sourceManifestSHA256']==sha(pair_path) and r['pair']['core']==pair['nativePair']['core']
 for path,digest in r['inputs'].items():assert sha(path)==digest,path
 for path,digest in r['artifacts'].items():assert sha(p.parent/path)==digest,path
 if relative==paths[-1]:assert not r['passed'] and 'newChildOfMinimizedOwnerExcluded' in r['error'] and r['checks'][-1]['passed'] is False and all(c['passed'] for c in r['checks'][:-1])
 else:assert r['passed'] and all(c['passed'] for c in r['checks'])
 rows.append({'path':relative,'sha256':sha(p),'passed':r['passed'],'checksReached':len(r['checks'])})
model_path=ROOT/'qa/model-1791059205434786756/report.json';model=json.loads(model_path.read_text());assert model['passed'] and model['namedScenarios']==9
for relative,digest in model['inputs'].items():assert sha(ROOT/relative)==digest,relative
for relative,digest in model['artifacts'].items():assert sha(model_path.parent/relative)==digest,relative
manifest={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'scope':'Exact source/build and positive/negative proof closure only; complete native minimize/scene acceptance blocked by NMIN-001','featureAccepted':False,'completedRequirementIds':[],'nativePair':pair['nativePair'],'nativeReports':rows,'positiveNativeCases':54,'blockingFailures':['NMIN-001'],'quintNamedScenarios':9,'quintInvariantSamples':1000,'quintMaxSteps':40,'quintReportSHA256':sha(model_path),'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))
