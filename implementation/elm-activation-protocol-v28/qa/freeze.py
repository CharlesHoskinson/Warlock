"""Freeze journaled activation with distinct compiled/model/native evidence."""
import hashlib,json,resource
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'elm-window-activation-v27'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pair_path=ROOT/'qa/build-pair-manifest.json';pair=json.loads(pair_path.read_text());assert pair['passed']
for rel,digest in pair['files'].items():assert sha(ROOT/rel)==digest,rel
for a in pair['nativePair'].values():assert sha(a['path'])==a['sha256']
accepted=[]
for p in sorted((ROOT/'qa').glob('native-*/report.json')):
 v=json.loads(p.read_text());assert v['passed'] and v['cleanupPassed'] and not v.get('error') and all(c['passed'] for c in v['checks'])
 for source,digest in v['inputs'].items():assert sha(source)==digest,source
 assert v['pair']['core']==pair['nativePair']['core'] and v['pair']['authority']['sha256']==pair['nativePair']['plugin']['sha256']
 accepted.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':len(v['checks'])})
assert sorted(r['checks'] for r in accepted)==[80,111]
elm_path=sorted((OLD/'qa').glob('elm-*/report.json'))[-1];elm=json.loads(elm_path.read_text());assert elm['passed'] and elm['checks']=={'original-effects':20,'original-shell':27,'activation':17}
for rel,digest in elm['inputs'].items():assert sha(ROOT/rel)==digest,rel
model_path=sorted((OLD/'qa').glob('model-*/report.json'))[-1];model=json.loads(model_path.read_text());assert model['passed'] and model['namedScenarios']==10 and model['invariantSamples']==1000 and model['sourceSHA256']==sha(ROOT/'spec/activation.qnt')
mutant_path=sorted((ROOT/'qa').glob('mutant-*/report.json'))[-1];mutant=json.loads(mutant_path.read_text());assert mutant['passed'] and mutant['originalSHA256']==sha(ROOT/'spec/activation.qnt')
failed_path=next((OLD/'qa').glob('native-*/report.json'));failed=json.loads(failed_path.read_text());assert not failed['passed'] and failed['cleanupPassed'] and failed['error']=="Refused('Unsupported effect')"
for source,digest in failed['inputs'].items():assert sha(source)==digest,source
manifest={'passed':True,'observedUTC':datetime.now(timezone.utc).isoformat(),'scope':'Typed and native Activate with capability agreement, journal/preflight/modal/seat checks; not complete canonical scene, taskbar, output/device or release acceptance','wholeFeatureAccepted':False,'canonicalSceneCapability':False,'completedRequirementIds':[],'nativePair':pair['nativePair'],'pairManifestSHA256':sha(pair_path),'nativeReports':accepted,'compiledChecks':64,'elmReport':str(elm_path),'elmReportSHA256':sha(elm_path),'modelReport':str(model_path),'modelReportSHA256':sha(model_path),'quintNamedRuns':10,'quintInvariantSamples':1000,'mutantReport':str(mutant_path.relative_to(ROOT)),'mutantReportSHA256':sha(mutant_path),'abstractUnsafeSeatVariantDetected':True,'failedNativeReport':str(failed_path),'failedNativeReportSHA256':sha(failed_path),'ancestorFiles':{str(p.relative_to(OLD)):sha(p) for p in OLD.rglob('*') if p.is_file() and not p.is_symlink()},'files':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Frozen typed/native activation80/111 checks and compiled64/model10/1000 evidence')
