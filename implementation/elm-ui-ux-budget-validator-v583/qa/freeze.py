import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]; REPO=ROOT.parents[1]
report=json.loads((ROOT/'qa/report.json').read_text());assert report['passed'] and len(report['checks'])==44 and all(c['passed'] for c in report['checks'])
for p,h in report['sourceHashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
assert hashlib.sha256((REPO/'docs/elm-roadmap/delivery/budgets.json').read_bytes()).hexdigest()==report['currentBudgetsSHA256']
legacy=json.loads((ROOT/'qa/current-budgets-verdict.json').read_text());assert legacy['verdict']=='calibration-only' and legacy['completeness']=='incomplete' and not legacy['performanceAccepted']
files=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p.name not in ('component-manifest.json','freeze-receipt.json'):
  assert not p.is_symlink(); files.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size})
manifest={'schema':1,'scope':'CPU budget-matrix structural preflight only; no performance/native/GPU/release acceptance','sourceHeld':True,'checks':44,'mainDesktopActions':False,'currentBudgetsUnchangedSHA256':report['currentBudgetsSHA256'],'files':files}
m=ROOT/'component-manifest.json';m.write_text(json.dumps(manifest,indent=2)+'\n')
r={'passed':True,'files':len(files),'manifestSHA256':hashlib.sha256(m.read_bytes()).hexdigest(),'command':['PYTHONDONTWRITEBYTECODE=1','/usr/bin/python3','-B','/home/hoskinson/window-integration-qa/qa_run.py','--','/usr/bin/python3','-B',str(pathlib.Path(__file__).resolve())],'scope':manifest['scope']};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
