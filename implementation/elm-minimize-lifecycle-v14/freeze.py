"""Freeze actual lifecycle repair evidence, with bounded claim scope."""
import datetime,hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Protected launcher required'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pair_path=ROOT/'qa/build-pair-manifest.json';pair=json.loads(pair_path.read_text());assert pair['passed']
for relative,digest in pair['files'].items():assert sha(ROOT/relative)==digest,relative
rows=[]
for relative in ['qa/native-1791060204902211100/report.json','qa/native-1791060628116278551/report.json']:
 p=ROOT/relative;r=json.loads(p.read_text());assert r['passed'] and r['cleanupPassed'] and not r['mainDesktopActions'] and all(c['passed'] for c in r['checks'])
 assert r['sourceManifestSHA256']==sha(pair_path) and r['pair']['core']==pair['nativePair']['core']
 for path,digest in r['inputs'].items():assert sha(path)==digest,path
 for path,digest in r['artifacts'].items():assert sha(p.parent/path)==digest,path
 rows.append({'path':relative,'sha256':sha(p),'cases':len(r['checks'])})
legacy=json.loads((REPO/'implementation/elm-native-minimize-v13/qa/native-1791058947594074854/report.json').read_text())
assert {c['name'] for c in legacy['checks']} <= {c['name'] for c in r['checks']}
assert {'newChildOfMinimizedOwnerExcluded','semanticMinimizeRetryDeduplicated','ambiguousRestoreRefusedBeforeMutation','newChildMinimizedPixelsExcluded','newChildMinimizedActualKeyboardExcluded','newChildMinimizedPointerExcluded'} <= {c['name'] for c in r['checks']}
model_path=ROOT/'qa/model-1791060322338767941/report.json';model=json.loads(model_path.read_text());assert model['passed'] and model['namedScenarios']==13
for relative,digest in model['inputs'].items():assert sha(ROOT/relative)==digest,relative
for relative,digest in model['artifacts'].items():assert sha(model_path.parent/relative)==digest,relative
manifest={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'scope':'60 private quiescent native minimize/modal/lifecycle cases and separate abstract policy model; no complete scene/presentation, hardware/AT or release acceptance','nativePair':pair['nativePair'],'nativeReports':rows,'nativeCases':60,'resolvedBoundedFindings':['NMIN-001','NMIN-002','NMIN-003'],'completeFeatureAccepted':False,'completedRequirementIds':[],'quintNamedScenarios':13,'quintInvariantSamples':1000,'quintMaxSteps':40,'quintReportSHA256':sha(model_path),'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))
