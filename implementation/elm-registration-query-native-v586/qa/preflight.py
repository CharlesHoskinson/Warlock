import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
held_path=REPO/'implementation/elm-unknown-reconciliation-reviewed-v582/qa/slice-manifest.json';assert sha(held_path)=='c990deed11a69a543a7a1e6cd7807842bd0f9e037b6c09856e6ec06828c96ef3';held=json.loads(held_path.read_text())
for row in held['files']:assert Path(REPO/row['path']).stat().st_size==row['size'] and sha(REPO/row['path'])==row['sha256']
for row in held['symlinks']:assert str((REPO/row['path']).readlink())==row['target']
core=REPO/'implementation/elm-registration-query-runtime-v585';base=REPO/'implementation/elm-keyboardless-current-runtime-v216'
for name in ['candidate_host.py','aq-tuple.json','parent-probe-build.json']:assert sha(core/name)==sha(base/name)
j=json.loads((core/'qa/build-pair-manifest.json').read_text());descriptor=json.loads((core/'native-build-report.json').read_text());assert j['nativePair']['plugin']==descriptor['plugin']
report_path=Path(descriptor['pluginBuildReport']);assert sha(report_path)==descriptor['pluginBuildReportSHA256'];report=json.loads(report_path.read_text());assert report['passed'] and not report['missingSymbols'] and len(report['owningHeaders'])==694
for group in ['dependencies','linkedLibraries','tools']:
 for path,digest in report[group].items():assert sha(path)==digest
for row in j['nativePair'].values():assert sha(row['path'])==row['sha256']
inputs={str(p):sha(p) for directory in [ROOT,core] for p in directory.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.md'] and p.name!='preflight.json'}
for p in (REPO/'implementation/elm-stable-surface-publication-v521/adapter').glob('*.py'):inputs[str(p)]=sha(p)
inputs[str(held_path)]=sha(held_path)
r={'passed':True,'nativeAcceptance':False,'scope':'Prospective source/pair/dependency review only; native query not yet executed','inputs':inputs,'nativePair':j['nativePair'],'reviewedProducer':str(held_path)};(ROOT/'qa/preflight.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'inputs':len(inputs)}))
