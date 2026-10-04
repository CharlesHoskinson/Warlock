"""Freeze bounded calibration and explicitly preserve failed attempts."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report_path=next((ROOT/'qa').glob('native-*/report.json'));report=json.loads(report_path.read_text())
assert report['passed'] and report['cleanupPassed'] and report['performanceAcceptance'] is False
assert len(report['checks'])==26 and all(row['passed'] for row in report['checks'])
assert report['helperToDOMReceiptMs']['count']==20 and len(report['resourceSamples'])==31
assert all(s['pssComplete'] for s in report['resourceSamples'])
for path,digest in report['inputs'].items():assert sha(Path(path))==digest,path
build_path=Path(report['buildReport']);assert sha(build_path)==report['buildReportSHA256']
build=json.loads(build_path.read_text());gui=REPO/'implementation/elm-output-shared-host-v150'
for path,digest in build['inputs'].items():assert sha(gui/path)==digest,path
assert sha(build_path.parent/'elm-host')==build['binarySHA256']
for participant in ['core','plugin']:
 item=report['pair'][participant];assert sha(Path(item['path']))==item['sha256']
original=REPO/'implementation/elm-output-shared-qa-v151/qa/regression.py'
for name in ['check','wait','click']:
 def fn(path):return next(n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(fn(original),include_attributes=False)==ast.dump(fn(ROOT/'qa/native.py'),include_attributes=False),name
references={'functional':REPO/'implementation/elm-output-shared-qa-v151/qa/slice-manifest.json','graphics':REPO/'implementation/elm-shared-gpu-qa-v157/qa/slice-manifest.json'}
for path in references.values():assert json.loads(path.read_text())['passed']
# Exact reported resource metrics remain in the raw packet; no threshold inferred.
a,b=report['resourceSamples'][0],report['resourceSamples'][-1]
metrics={'idleCpuPercentOneCore':report['idle']['survivingIdentityCpuPercentOneCore'],'processCount':report['idle']['processCount'],'helperToDOMReceiptMs':report['helperToDOMReceiptMs'],'initialPssKiB':a['knownPssKiB'],'finalPssKiB':b['knownPssKiB'],'initialPrivateKiB':a['knownPrivateKiB'],'finalPrivateKiB':b['knownPrivateKiB'],'allSamples':report['allSamples']}
files={str(p.relative_to(REPO)):sha(p) for name in ['elm-shared-measure-v158','elm-shared-measure-v159','elm-shared-measure-v160'] for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and p!=ROOT/'qa/slice-manifest.json'}
result={'passed':True,'scope':report['scope'],'nativeChecks':26,'popupCycles':20,'resourceSampleCount':31,'metrics':metrics,'limitations':report['measurementLimitations'],'performanceBudgetsAccepted':False,'completedRequirementIds':[],'cleanupPassed':True,'evidence':{'native':{'path':str(report_path.relative_to(REPO)),'sha256':sha(report_path)},**{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':True} for k,p in references.items()}},'files':files}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'nativeChecks':26,'popupCycles':20,'performanceBudgetsAccepted':False}))
